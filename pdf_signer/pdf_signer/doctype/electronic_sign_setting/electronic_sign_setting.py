# Copyright (c) 2022, Danny Molina Morales and contributors
# For license information, please see license.txt

import base64
import json
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document

from pdf_signer.utils.appearance import STAMP_TEXT_VARIABLES, hex_to_rgb, preview_pdf


class ElectronicSignSetting(Document):
	def before_save(self):
		if not frappe.db.exists("Electronic Sign Setting", {"name": ["!=", self.name]}):
			self.is_default = 1

	def validate(self):
		self.validate_timestamp()
		if not self.visible_signature:
			return
		self.validate_box()
		self.validate_text()
		self.validate_colors()
		self.validate_font()

	def validate_timestamp(self):
		if not self.tsa_url:
			self.long_term_validation = 0
			return
		if not self.tsa_url.lower().startswith(("http://", "https://")):
			frappe.throw(_("The Time Stamp Authority URL must start with http:// or https://."))
		if self.tsa_certificate and not self.tsa_certificate.lower().endswith((".cer", ".crt", ".pem")):
			frappe.throw(_("The TSA root certificate must be a .cer, .crt or .pem file."))

	def validate_box(self):
		if self.page == "Page Number" and (self.page_number or 0) < 1:
			frappe.throw(_("The page number must be 1 or more."))
		if (self.box_width or 0) <= 0 or (self.box_height or 0) <= 0:
			frappe.throw(_("The width and the height of the signature box must be more than 0."))
		if self.position == "Custom" and (self.custom_x is None or self.custom_y is None):
			frappe.throw(_("Give the distance from the left and from the bottom for a custom position."))

	def validate_text(self):
		if not (self.stamp_text or "").strip():
			if self.stamp_style == "Text":
				frappe.throw(_("The style Text needs a text. Write the Text, or select another style."))
			return
		try:
			self.stamp_text % {name: "" for name in (*STAMP_TEXT_VARIABLES, "ts")}
		except KeyError as e:
			frappe.throw(
				_("The text has an unknown variable: {0}. Use only {1}.").format(
					e.args[0], ", ".join(f"%({name})s" for name in (*STAMP_TEXT_VARIABLES, "ts"))
				)
			)
		except (TypeError, ValueError):
			frappe.throw(_("The text has a % sign that is not a variable. Write %% to show a % sign."))
		try:
			datetime.now().strftime(self.timestamp_format or "")
		except ValueError:
			frappe.throw(_("The date format {0} is not correct.").format(self.timestamp_format))

	def validate_colors(self):
		for fieldname in ("text_color", "border_color", "handwritten_color"):
			value = self.get(fieldname)
			if value and hex_to_rgb(value) is None:
				frappe.throw(_("{0} must be a color like #1F3A93.").format(_(self.meta.get_label(fieldname))))

	def validate_font(self):
		if self.font_file and not self.font_file.lower().endswith((".ttf", ".otf")):
			frappe.throw(_("The font file must be a TTF or OTF file."))


@frappe.whitelist()
def preview(doc):
	"""Return a PDF (base64) with the signature box of the values of the form. Nothing is saved."""
	setting = frappe.get_doc(json.loads(doc) if isinstance(doc, str) else doc)
	if not frappe.has_permission("Electronic Sign Setting", "write"):
		frappe.throw(_("You cannot change sign settings."), frappe.PermissionError)
	if not setting.visible_signature:
		frappe.throw(_("The signature is invisible. It does not have a box to show."), title=_("No preview"))
	setting.validate()
	pdf = preview_pdf(setting, frappe.utils.get_fullname(frappe.session.user))
	return base64.b64encode(pdf).decode()
