import frappe
from frappe import _

SETTING = "Electronic Sign Setting"
MANAGER_ROLES = {"System Manager", "PDF Signer Manager"}


def has_app_permission():
	"""Show PDF Signer on the apps screen only to desk users who can read the sign settings."""
	if frappe.session.user == "Administrator":
		return True
	if frappe.get_cached_value("User", frappe.session.user, "user_type") == "Website User":
		return False
	return bool(frappe.has_permission(SETTING, ptype="read"))


def can_sign(setting, user=None):
	"""Return True if the user can sign with the sign setting.

	The users of the setting win over its roles: a personal certificate is for its holder only.
	Without users and roles, only the managers of the app can sign.
	"""
	user = user or frappe.session.user
	users = {row.user for row in setting.sign_users}
	if users:
		return user in users
	roles = {row.role for row in setting.sign_roles} or MANAGER_ROLES
	return bool(roles & set(frappe.get_roles(user)))


def can_verify(setting, user=None):
	"""Return True if the user can verify signatures with the sign setting.

	Without roles, every user that can read the PDF can verify.
	"""
	roles = {row.role for row in setting.verify_roles}
	if not roles:
		return True
	return bool((roles | MANAGER_ROLES) & set(frappe.get_roles(user or frappe.session.user)))


CHECKS = {"sign": can_sign, "verify": can_verify}


def get_allowed_settings(purpose, txt=""):
	"""Return the names of the enabled sign settings that the user can use for the purpose."""
	check = CHECKS[purpose]
	names = frappe.get_all(
		SETTING,
		filters={"status": "Enable", "name": ["like", f"%{txt}%"]},
		order_by="is_default desc, name asc",
		pluck="name",
	)
	return [name for name in names if check(frappe.get_cached_doc(SETTING, name))]


def get_setting(name, purpose):
	"""Return the sign setting, or stop if it is disabled or the user cannot use it."""
	setting = frappe.get_cached_doc(SETTING, name)
	if setting.status != "Enable":
		frappe.throw(_("The sign setting {0} is disabled.").format(name), title=_("Disabled setting"))
	if not CHECKS[purpose](setting):
		message = {
			"sign": _("You cannot sign with the sign setting {0}."),
			"verify": _("You cannot verify with the sign setting {0}."),
		}[purpose]
		frappe.throw(message.format(name), frappe.PermissionError, title=_("Not permitted"))
	return setting


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def sign_setting_query(doctype, txt, searchfield, start, page_len, filters):
	"""Link query of the sign and verify dialogs: only the settings that the user can use."""
	purpose = (filters or {}).get("purpose")
	if purpose not in CHECKS:
		frappe.throw(_("Unknown purpose: {0}").format(purpose))
	names = get_allowed_settings(purpose, txt)[start : start + page_len]
	containers = dict(
		frappe.get_all(
			SETTING, filters={"name": ["in", names]}, fields=["name", "cert_container"], as_list=True
		)
	)
	return [(name, containers.get(name)) for name in names]
