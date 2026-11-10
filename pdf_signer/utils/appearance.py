"""The signature box of a sign setting: its page, its place, its style and its text."""

import base64
import io
import re

import frappe
from frappe import _
from frappe.utils import get_url
from PIL import Image, ImageOps
from pyhanko import stamp
from pyhanko.pdf_utils import images, text
from pyhanko.pdf_utils.font.opentype import GlyphAccumulatorFactory

MM = 72 / 25.4  # PDF points in one millimeter

# Variables of the text of the box. pyHanko fills %(ts)s itself.
STAMP_TEXT_VARIABLES = ("signer", "reason", "location", "additional", "url")

# Position of the sign setting -> horizontal and vertical alignment on the page
POSITIONS = {
	"Bottom Left": ("left", "bottom"),
	"Bottom Center": ("center", "bottom"),
	"Bottom Right": ("right", "bottom"),
	"Top Left": ("left", "top"),
	"Top Center": ("center", "top"),
	"Top Right": ("right", "top"),
}

QR_POSITIONS = {
	"Left of Text": stamp.QRPosition.LEFT_OF_TEXT,
	"Right of Text": stamp.QRPosition.RIGHT_OF_TEXT,
	"Above Text": stamp.QRPosition.ABOVE_TEXT,
	"Below Text": stamp.QRPosition.BELOW_TEXT,
}


def hex_to_rgb(value):
	"""Return a color like #1F3A93 as an RGB tuple with values from 0 to 1, or None if it is not valid."""
	match = re.fullmatch(r"#?([0-9a-fA-F]{6})", (value or "").strip())
	if not match:
		return None
	digits = match.group(1)
	return tuple(int(digits[i : i + 2], 16) / 255 for i in (0, 2, 4))


def file_url_path(file_url):
	"""Return the path on disk of a file of the site from its URL."""
	name = frappe.db.get_value("File", {"file_url": file_url}, "name")
	if not name:
		frappe.throw(_("The file {0} does not exist.").format(file_url))
	return frappe.get_doc("File", name).get_full_path()


def page_index(writer, setting):
	"""Return the zero-based index of the page of the signature box."""
	count = int(writer.root["/Pages"]["/Count"])
	if setting.page == "Last Page":
		return count - 1
	if setting.page == "Page Number":
		if setting.page_number > count:
			frappe.throw(
				_("The sign setting puts the signature on page {0}, but the PDF has {1} pages.").format(
					setting.page_number, count
				),
				title=_("Page not found"),
			)
		return setting.page_number - 1
	return 0


def page_box(page):
	"""Return the visible area of a page as (left, bottom, right, top). The box can come from a parent node."""
	node = page
	while node is not None:
		for key in ("/CropBox", "/MediaBox"):
			if key in node:
				left, bottom, right, top = (float(v) for v in node[key])
				return min(left, right), min(bottom, top), max(left, right), max(bottom, top)
		node = node.get("/Parent")
	return 0.0, 0.0, 595.0, 842.0  # A4, if the PDF does not give a size


def signature_box(writer, setting):
	"""Return the page index and the box (x1, y1, x2, y2) in points of the signature."""
	index = page_index(writer, setting)
	page = writer.find_page_for_modification(index)[0].get_object()
	left, bottom, right, top = page_box(page)
	width, height = setting.box_width * MM, setting.box_height * MM
	if setting.position == "Custom":
		x, y = left + (setting.custom_x or 0) * MM, bottom + (setting.custom_y or 0) * MM
	else:
		margin = (setting.margin or 0) * MM
		horizontal, vertical = POSITIONS[setting.position]
		x = {
			"left": left + margin,
			"center": left + (right - left - width) / 2,
			"right": right - margin - width,
		}[horizontal]
		y = {"bottom": bottom + margin, "top": top - margin - height}[vertical]
	if x < left or y < bottom or x + width > right or y + height > top:
		frappe.throw(
			_("The signature box does not fit on the page. Make it smaller, or change its position."),
			title=_("Box outside the page"),
		)
	return index, (round(x, 2), round(y, 2), round(x + width, 2), round(y + height, 2))


def signer_name(signer):
	"""Return the common name of the certificate holder, or its full subject."""
	subject = signer.signing_cert.subject.native
	return subject.get("common_name") or signer.signing_cert.subject.human_friendly


def handwritten_image(setting):
	"""Return the drawn signature as an image in the color of the sign setting."""
	data = str(setting.own_sign).split(",", 1)[-1]
	drawing = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGBA")
	alpha = drawing.getchannel("A")
	if alpha.getextrema() == (255, 255):
		# An image without transparency: the dark lines are the signature.
		alpha = ImageOps.invert(drawing.convert("L"))
	red, green, blue = (round(v * 255) for v in hex_to_rgb(setting.handwritten_color) or (0, 0, 0))
	colored = Image.new("RGBA", drawing.size, (red, green, blue, 255))
	colored.putalpha(alpha)
	return colored


def text_box_style(setting):
	font = {"font": GlyphAccumulatorFactory(file_url_path(setting.font_file))} if setting.font_file else {}
	return text.TextBoxStyle(
		font_size=int(setting.text_size or 11), text_color=hex_to_rgb(setting.text_color), **font
	)


def stamp_style(setting, signer):
	"""Return the stamp style of the signature box and the values of its text variables."""
	text_params = {
		"signer": signer_name(signer),
		"reason": setting.reason or "",
		"location": setting.location or "",
		"additional": setting.additional or "",
		"url": setting.qr_content or setting.additional or get_url(),
	}
	common = {
		"stamp_text": setting.stamp_text,
		"timestamp_format": setting.timestamp_format or "%d/%m/%Y %H:%M:%S %Z",
		"text_box_style": text_box_style(setting),
		"border_width": int(setting.border_width or 0),
		"border_color": hex_to_rgb(setting.border_color),
	}
	if setting.stamp_style == "Text and QR Code":
		# pyHanko puts the "url" text parameter in the QR code.
		return stamp.QRStampStyle(qr_position=QR_POSITIONS[setting.qr_position], **common), text_params
	if setting.stamp_style == "Background Image":
		background = images.PdfImage(file_url_path(setting.bg_image))
	elif setting.stamp_style == "Handwritten Signature":
		background = images.PdfImage(handwritten_image(setting))
	else:
		return stamp.TextStampStyle(**common), text_params
	opacity = (setting.background_opacity if setting.background_opacity is not None else 60) / 100
	return stamp.TextStampStyle(background=background, background_opacity=opacity, **common), text_params
