import os

import frappe
from frappe import _

from pdf_signer.utils import utils
from pdf_signer.utils.permission import get_allowed_settings, get_setting
from pdf_signer.utils.sign import CONTAINER, attachment_paths, sign_file, tsa_root, validate_sign


def get_file(name, ptype):
	"""Return the File document, or stop if the user does not have the permission."""
	file_doc = frappe.get_doc("File", name)
	if not frappe.has_permission("File", ptype, doc=file_doc):
		frappe.throw(
			_("You do not have the permission to use the file {0}.").format(file_doc.file_name),
			frappe.PermissionError,
		)
	return file_doc


def is_pdf(file_doc):
	"""Return True if the File document is a PDF file on the disk of the site."""
	if file_doc.is_folder or not file_doc.file_url or file_doc.file_url.startswith(("http://", "https://")):
		return False
	path = file_doc.get_full_path()
	return os.path.isfile(path) and utils.get_mimetype_file(path) == "application/pdf"


@frappe.whitelist()
def check_pdf(file):
	"""Tell the File form if the file is a PDF, and if the user can sign or verify it."""
	file_doc = get_file(file, "read")
	if not is_pdf(file_doc):
		return {"success": False}
	return {
		"success": True,
		"can_sign": bool(
			frappe.has_permission("File", "write", doc=file_doc) and get_allowed_settings("sign")
		),
		"can_verify": bool(get_allowed_settings("verify")),
	}


@frappe.whitelist()
def sign_pdf(file, sign_setting):
	file_doc = get_file(file, "write")
	if not is_pdf(file_doc):
		frappe.throw(_("The file {0} is not a PDF.").format(file_doc.file_name))
	return sign_file(file_doc, get_setting(sign_setting, "sign"))


@frappe.whitelist()
def verify_pdf(file, sign_setting):
	file_doc = get_file(file, "read")
	if not is_pdf(file_doc):
		frappe.throw(_("The file {0} is not a PDF.").format(file_doc.file_name))
	setting = get_setting(sign_setting, "verify")
	container = setting.cert_container
	ca_roots = attachment_paths(CONTAINER, container, "ca_root")
	if not ca_roots:
		frappe.throw(
			_("The certificate container {0} does not have a CA root file.").format(container),
			title=_("Missing CA root"),
		)
	return validate_sign(
		file_doc.get_full_path(),
		ca_roots[-1],
		attachment_paths(CONTAINER, container, "ca_interm"),
		tsa_root(setting),
	)
