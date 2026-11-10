import base64
import io
import json
import os

import frappe
from frappe import _
from frappe.utils import format_datetime
from frappe.utils.data import convert_utc_to_system_timezone
from frappe.utils.password import get_decrypted_password
from PIL import Image
from pyhanko import stamp
from pyhanko.pdf_utils import images, text
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import fields, signers
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

CONTAINER = "Certificate Container"

# Signature Type of the sign setting -> DocMDP level of a certification signature (None: approval)
CERTIFICATION_LEVELS = {
	"Approval": None,
	"Certification: No Changes": fields.MDPPerm.NO_CHANGES,
	"Certification: Form Filling and Signing": fields.MDPPerm.FILL_FORMS,
}


def attachment_paths(doctype, name, fieldname):
	"""Return the paths on disk of the files attached to a field of a document."""
	files = frappe.get_all(
		"File",
		filters={"attached_to_doctype": doctype, "attached_to_name": name, "attached_to_field": fieldname},
		pluck="name",
		order_by="creation asc",
	)
	return [frappe.get_doc("File", file).get_full_path() for file in files]


def load_signer(setting):
	"""Load the certificate and the key of the certificate container of the sign setting."""
	container = setting.cert_container
	cert_files = attachment_paths(CONTAINER, container, "cert_file")
	if not cert_files:
		frappe.throw(
			_("The certificate container {0} does not have a certificate file.").format(container),
			title=_("Missing certificate"),
		)
	passphrase = get_decrypted_password(CONTAINER, container, "passphrase", raise_exception=False)
	ca_files = attachment_paths(CONTAINER, container, "ca_root") + attachment_paths(
		CONTAINER, container, "ca_interm"
	)
	signer = signers.SimpleSigner.load_pkcs12(
		pfx_file=cert_files[-1],
		ca_chain_files=ca_files or None,
		passphrase=passphrase.encode() if passphrase else None,
	)
	if not signer:
		frappe.throw(
			_(
				"The certificate of {0} cannot be opened. Check the certificate file and the passphrase."
			).format(container),
			title=_("Invalid certificate"),
		)
	return signer


def check_policy(setting, reader):
	"""Stop if the signatures of the PDF do not allow this signature."""
	if any(signature.docmdp_level == fields.MDPPerm.NO_CHANGES for signature in reader.embedded_signatures):
		frappe.throw(
			_("The PDF has a certification signature that does not allow changes. You cannot sign it again."),
			title=_("Signature not possible"),
		)
	if CERTIFICATION_LEVELS[setting.signature_type] and reader.embedded_signatures:
		frappe.throw(
			_(
				"The PDF already has signatures. A certification signature must be the first signature of the PDF. Use a sign setting with the Approval signature type."
			),
			title=_("Certification not possible"),
		)


def signature_metadata(setting, field_name):
	"""Return the metadata of the signature: certification level, reason, location and contact."""
	level = CERTIFICATION_LEVELS[setting.signature_type]
	return signers.PdfSignatureMetadata(
		field_name=field_name,
		certify=bool(level),
		docmdp_permissions=level or fields.MDPPerm.FILL_FORMS,
		reason=setting.reason or None,
		location=setting.location or None,
		contact_info=setting.contact_info or None,
	)


def prepare_field(writer, setting):
	"""Choose the signature field, and return its name and a note for the user.

	- The first empty signature field of the PDF, if there is one.
	- Else a new field. After a certification that allows form filling, the new field is
	  invisible: a new visible field changes the pages, and that breaks the certification.
	"""
	empty = next(fields.enumerate_sig_fields(writer, filled_status=False), None)
	if empty:
		return empty[0], _("The signature uses the empty signature field {0} of the PDF.").format(empty[0])
	field_name = f"Signature-{frappe.generate_hash(length=8)}"
	certified = any(
		signature.docmdp_level == fields.MDPPerm.FILL_FORMS for signature in writer.prev.embedded_signatures
	)
	box = None if certified else tuple(json.loads(setting.postition).values())
	fields.append_signature_field(
		writer, sig_field_spec=fields.SigFieldSpec(field_name, box=box, on_page=int(setting.on_page))
	)
	if certified:
		return field_name, _(
			"The PDF has a certification signature. The new signature is invisible, so that the certification stays valid."
		)
	return field_name, None


def sign_file(file_doc, setting):
	"""Sign the PDF of the File document in place with the sign setting."""
	pdf_path = file_doc.get_full_path()
	signer = load_signer(setting)
	temp_path = f"{pdf_path}.signing"
	try:
		with open(pdf_path, "rb") as inf:
			writer = IncrementalPdfFileWriter(inf)
			check_policy(setting, writer.prev)
			field_name, note = prepare_field(writer, setting)
			style, text_params = stamp_style(setting, signer)
			pdf_signer = signers.PdfSigner(
				signature_metadata(setting, field_name), signer=signer, stamp_style=style
			)
			with open(temp_path, "wb") as outf:
				pdf_signer.sign_pdf(writer, output=outf, appearance_text_params=text_params)
		os.replace(temp_path, pdf_path)
	except frappe.ValidationError:
		raise
	except Exception as e:
		frappe.log_error(title=_("PDF Signer: the PDF could not be signed"))
		frappe.throw(_("The PDF could not be signed: {0}").format(e), title=_("Signature error"))
	finally:
		if os.path.exists(temp_path):
			os.remove(temp_path)

	file_doc.content_hash = None
	file_doc.generate_content_hash()
	frappe.db.set_value("File", file_doc.name, "content_hash", file_doc.content_hash)
	return {"success": True, "msg": " ".join(filter(None, [_("The PDF is signed."), note]))}


def stamp_style(setting, signer):
	"""Return the stamp style of the signature box and its text parameters."""
	text_params = {"url": setting.additional or "", "name_info": signer.subject_name}
	stamp_text = "Signed by: %(name_info)s\nTime: %(ts)s\n%(url)s"
	text_box_style = text.TextBoxStyle(font_size=int(setting.text_size))
	if setting.use_bg_image or setting.use_own_sign_bg_image:
		if setting.use_bg_image:
			background = attachment_paths(setting.doctype, setting.name, "bg_image")[-1]
		else:
			background = Image.open(
				io.BytesIO(base64.b64decode(str(setting.own_sign).replace("data:image/png;base64,", "")))
			)
		style = stamp.TextStampStyle(
			stamp_text=stamp_text, text_box_style=text_box_style, background=images.PdfImage(background)
		)
	else:
		# With QR stamps, the 'url' text parameter is mandatory: it is the content of the QR code.
		style = stamp.QRStampStyle(border_width=0, stamp_text=stamp_text, text_box_style=text_box_style)
	return style, text_params


def validate_sign(pdf_file_verify, root, chain=None):
	"""Validate every signature of the PDF against the CA root and the intermediate CAs."""
	trust_roots = [load_cert_from_pemder(root)]
	other_certs = [load_cert_from_pemder(ca) for ca in chain or []]
	vc = ValidationContext(trust_roots=trust_roots, other_certs=other_certs)
	with open(pdf_file_verify, "rb") as doc:
		reader = PdfFileReader(doc)
		return [
			signature_result(signature, validate_pdf_signature(signature, vc))
			for signature in reader.embedded_signatures
		]


def signature_result(signature, status):
	"""Return the data of one signature that the verification dialog shows."""
	cert = status.signing_cert
	return {
		"field": signature.field_name,
		"valid": status.bottom_line,
		"intact": status.intact,
		"crypto_valid": status.valid,
		"trusted": status.trusted,
		"revoked": status.revoked,
		"signer": cert.subject.human_friendly,
		"issuer": cert.issuer.human_friendly,
		"serial_number": format(cert.serial_number, "X"),
		"valid_until": format_utc(cert.not_valid_after),
		"sha256": cert.sha256_fingerprint,
		"trust_anchor": status.validation_path[0].subject.human_friendly if status.validation_path else None,
		"signing_time": format_utc(status.signer_reported_dt),
		"timestamp": format_utc(status.timestamp_validity.timestamp) if status.timestamp_validity else None,
		"coverage": status.coverage.name if status.coverage else None,
		"modification_level": status.modification_level.name if status.modification_level else None,
		"docmdp_ok": status.docmdp_ok,
		"certification": signature.docmdp_level.name if signature.docmdp_level else None,
	}


def format_utc(value):
	"""Show a UTC datetime in the time zone of the system."""
	if not value:
		return None
	return format_datetime(convert_utc_to_system_timezone(value).replace(tzinfo=None))
