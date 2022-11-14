# Copyright (c) 2022, Danny Molina Morales and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ElectronicSignSetting(Document):
    def before_save(self):
        if len(frappe.db.get_list("Electronic Sign Setting")) == 0:
            self.is_default = 1
