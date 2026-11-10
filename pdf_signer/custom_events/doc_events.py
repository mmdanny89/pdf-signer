import frappe
from frappe import _

from pdf_signer.utils.api import is_pdf
from pdf_signer.utils.permission import get_allowed_settings

# Attach field -> extensions that the field accepts. All of them must be private files.
CERTIFICATE_FIELDS = {
	"cert_file": (".p12", ".pfx"),
	"ca_root": (".cer", ".crt"),
	"ca_interm": (".cer", ".crt"),
}


def remove_file_signed(doc, method):
	# TODO: remove file for app register.!!
	pass


def check_file_uploaded(doc, method):
	"""Ask the user to sign a new PDF, if the global settings say so and the user can sign."""
	if not frappe.db.get_single_value("Global Settings PDF Signer", "always_ask"):
		return
	if is_pdf(doc) and get_allowed_settings("sign"):
		frappe.publish_realtime(event="ask_to_sign", message={"docname": doc.name}, user=frappe.session.user)


def validate_extension(doc, method):
	"""Accept only private certificate files with the correct extension in a certificate container."""
	if doc.attached_to_doctype != "Certificate Container" or doc.attached_to_field not in CERTIFICATE_FIELDS:
		return
	if not doc.is_private:
		frappe.throw(_("Certificate files must be private files."), title=_("Public certificate"))
	extensions = CERTIFICATE_FIELDS[doc.attached_to_field]
	if not str(doc.file_name).lower().endswith(extensions):
		frappe.throw(
			_("The file {0} has a wrong extension. Allowed extensions: {1}").format(
				doc.file_name, ", ".join(extensions)
			),
			title=_("Wrong extension"),
		)
