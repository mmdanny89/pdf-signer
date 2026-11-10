import frappe


def has_app_permission():
	"""Show PDF Signer on the apps screen only to desk users who can read the sign settings."""
	if frappe.session.user == "Administrator":
		return True
	if frappe.get_cached_value("User", frappe.session.user, "user_type") == "Website User":
		return False
	return bool(frappe.has_permission("Electronic Sign Setting", ptype="read"))
