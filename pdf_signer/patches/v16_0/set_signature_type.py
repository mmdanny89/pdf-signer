import frappe


def execute():
	"""Set the Signature Type of the sign settings from the old field "Allow Add Others Signs".

	The old field did not change the signature. It meant: on, other people can sign after you
	(an approval signature); off, the document does not accept changes (a certification signature
	without changes). The column stays in the table after the field leaves the DocType.
	"""
	if not frappe.db.has_column("Electronic Sign Setting", "allow_add_signs"):
		return
	settings = frappe.db.sql("select name, allow_add_signs from `tabElectronic Sign Setting`", as_dict=True)
	for setting in settings:
		signature_type = "Approval" if setting.allow_add_signs else "Certification: No Changes"
		frappe.db.set_value(
			"Electronic Sign Setting", setting.name, "signature_type", signature_type, update_modified=False
		)
