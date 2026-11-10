# Copyright (c) 2022, Danny Molina Morales and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document

from pdf_signer.utils.appearance import STAMP_TEXT_VARIABLES, hex_to_rgb


class ElectronicSignSetting(Document):
	def before_save(self):
		if not frappe.db.exists("Electronic Sign Setting", {"name": ["!=", self.name]}):
			self.is_default = 1

	def validate(self):
		if not self.visible_signature:
			return
		self.validate_box()
		self.validate_text()
		self.validate_colors()
		self.validate_font()

	def validate_box(self):
		if self.page == "Page Number" and (self.page_number or 0) < 1:
			frappe.throw(_("The page number must be 1 or more."))
		if (self.box_width or 0) <= 0 or (self.box_height or 0) <= 0:
			frappe.throw(_("The width and the height of the signature box must be more than 0."))
		if self.position == "Custom" and (self.custom_x is None or self.custom_y is None):
			frappe.throw(_("Give the distance from the left and from the bottom for a custom position."))

	def validate_text(self):
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
