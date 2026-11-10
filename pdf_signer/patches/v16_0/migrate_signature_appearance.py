import json

import frappe

MM = 72 / 25.4
OLD_COLUMNS = ("postition", "on_page", "use_bg_image", "use_own_sign_bg_image")


def execute():
	"""Move the old appearance fields of the sign settings to the new fields.

	The values keep the look of the old signatures: the same box in points, the same page,
	the same style, the old text and date format of pyHanko, and the old borders.
	The old columns stay in the table after the fields leave the DocType.
	"""
	if not all(frappe.db.has_column("Electronic Sign Setting", column) for column in OLD_COLUMNS):
		return
	settings = frappe.db.sql(
		"""select name, postition, on_page, use_bg_image, use_own_sign_bg_image, additional
		from `tabElectronic Sign Setting`""",
		as_dict=True,
	)
	for setting in settings:
		frappe.db.set_value(
			"Electronic Sign Setting", setting.name, new_values(setting), update_modified=False
		)


def new_values(setting):
	if setting.use_bg_image:
		style = "Background Image"
	elif setting.use_own_sign_bg_image:
		style = "Handwritten Signature"
	else:
		style = "Text and QR Code"
	values = {
		"visible_signature": 1,
		"stamp_style": style,
		"qr_position": "Left of Text",
		"qr_content": setting.additional,
		"stamp_text": "Signed by: %(signer)s\nTime: %(ts)s\n%(additional)s",
		"timestamp_format": "%Y-%m-%d %H:%M:%S %Z",
		"border_width": 0 if style == "Text and QR Code" else 3,
		"border_color": "#000000",
		"text_color": "#000000",
		"handwritten_color": "#404040",
		"background_opacity": 60,
		**page_values(setting.on_page),
		**box_values(setting.postition),
	}
	return values


def page_values(on_page):
	on_page = int(on_page or 0)
	if on_page == 0:
		return {"page": "First Page", "page_number": 1}
	if on_page < 0:
		return {"page": "Last Page", "page_number": 1}
	return {"page": "Page Number", "page_number": on_page + 1}


def box_values(position):
	try:
		box = json.loads(position or "{}")
		x1, y1, x2, y2 = (float(box[key]) for key in ("x1", "y1", "x2", "y2"))
	except (ValueError, KeyError, TypeError):
		return {"position": "Bottom Right", "box_width": 70, "box_height": 25, "margin": 10}
	return {
		"position": "Custom",
		"custom_x": round(min(x1, x2) / MM, 1),
		"custom_y": round(min(y1, y2) / MM, 1),
		"box_width": round(abs(x2 - x1) / MM, 1),
		"box_height": round(abs(y2 - y1) / MM, 1),
		"margin": 10,
	}
