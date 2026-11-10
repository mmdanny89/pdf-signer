import os

import frappe
from frappe import _
from frappe.utils import format_datetime
from frappe.utils.data import convert_utc_to_system_timezone
from frappe.utils.password import get_decrypted_password
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import fields, signers
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko.sign.timestamps import HTTPTimeStamper
from pyhanko.sign.validation import validate_pdf_signature, validate_pdf_timestamp
from pyhanko_certvalidator import ValidationContext

from pdf_signer.utils.appearance import file_url_path, signature_box, signer_name, stamp_style

CONTAINER = "Certificate Container"

# Signature Type of the sign setting -> DocMDP level of a certification signature (None: approval)
CERTIFICATION_LEVELS = {
	"Approval": None,
	"Certification: No Changes": fields.MDPPerm.NO_CHANGES,
	"Certification: Form Filling and Signing": fields.MDPPerm.FILL_FORMS,
}


def container_files(container):
	"""Return the paths on disk of the files of a certificate container: cert, root and interms.

	The values of the fields decide, not the attachments: a file of a deleted row of the
	intermediate CAs stays attached to the container, but the app must not use it."""
	doc = frappe.get_doc(CONTAINER, container)
	return frappe._dict(
		cert=file_url_path(doc.cert_file) if doc.cert_file else None,
		root=file_url_path(doc.ca_root) if doc.ca_root else None,
		interms=[file_url_path(row.ca_interm) for row in doc.ca_interms if row.ca_interm],
	)


def load_signer(setting):
	"""Load the certificate and the key of the certificate container of the sign setting."""
	container = setting.cert_container
	files = container_files(container)
	if not files.cert:
		frappe.throw(
			_("The certificate container {0} does not have a certificate file.").format(container),
			title=_("Missing certificate"),
		)
	passphrase = get_decrypted_password(CONTAINER, container, "passphrase", raise_exception=False)
	ca_files = ([files.root] if files.root else []) + files.interms
	signer = signers.SimpleSigner.load_pkcs12(
		pfx_file=files.cert,
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
	"""Return the metadata of the signature: PAdES, certification level, reason, location,
	contact, and the long-term validation data if the sign setting asks for it."""
	level = CERTIFICATION_LEVELS[setting.signature_type]
	long_term = bool(setting.tsa_url and setting.long_term_validation)
	return signers.PdfSignatureMetadata(
		field_name=field_name,
		subfilter=SigSeedSubFilter.PADES,
		certify=bool(level),
		docmdp_permissions=level or fields.MDPPerm.FILL_FORMS,
		reason=setting.reason or None,
		location=setting.location or None,
		contact_info=setting.contact_info or None,
		embed_validation_info=long_term,
		use_pades_lta=long_term,
		validation_context=signing_validation_context(setting) if long_term else None,
	)


def tsa_root(setting):
	"""Return the path of the root certificate of the TSA of the sign setting, or None."""
	return file_url_path(setting.tsa_certificate) if setting.tsa_url and setting.tsa_certificate else None


def signing_validation_context(setting):
	"""Validation context for the long-term validation data: it trusts the CA of the container
	and the TSA, and it can get the OCSP and CRL data from the addresses in the certificates."""
	container = setting.cert_container
	files = container_files(container)
	if not files.root:
		frappe.throw(
			_("Long-term validation needs the CA root file in the certificate container {0}.").format(
				container
			),
			title=_("Missing CA root"),
		)
	trust_roots = [load_cert_from_pemder(files.root)]
	if tsa_root(setting):
		trust_roots.append(load_cert_from_pemder(tsa_root(setting)))
	other_certs = [load_cert_from_pemder(path) for path in files.interms]
	return ValidationContext(trust_roots=trust_roots, other_certs=other_certs, allow_fetching=True)


def timestamper(setting):
	"""Return the client of the TSA of the sign setting, or None."""
	if not setting.tsa_url:
		return None
	password = setting.get_password("tsa_password", raise_exception=False) if setting.tsa_username else None
	return HTTPTimeStamper(
		setting.tsa_url,
		https=setting.tsa_url.lower().startswith("https://"),
		timeout=20,
		auth=(setting.tsa_username, password or "") if setting.tsa_username else None,
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
	page, box = 0, None
	if setting.visible_signature and not certified:
		page, box = signature_box(writer, setting)
	fields.append_signature_field(
		writer, sig_field_spec=fields.SigFieldSpec(field_name, box=box, on_page=page)
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
			style, text_params = stamp_style(setting, signer_name(signer))
			pdf_signer = signers.PdfSigner(
				signature_metadata(setting, field_name),
				signer=signer,
				stamp_style=style,
				timestamper=timestamper(setting),
			)
			with open(temp_path, "wb") as outf:
				pdf_signer.sign_pdf(writer, output=outf, appearance_text_params=text_params)
		os.replace(temp_path, pdf_path)
	except frappe.ValidationError:
		raise
	except Exception as e:
		frappe.log_error(title=_("PDF Signer: the PDF could not be signed"))
		frappe.throw(
			_("The PDF could not be signed: {0}").format(str(e) or type(e).__name__),
			title=_("Signature error"),
		)
	finally:
		if os.path.exists(temp_path):
			os.remove(temp_path)

	file_doc.content_hash = None
	file_doc.generate_content_hash()
	frappe.db.set_value("File", file_doc.name, "content_hash", file_doc.content_hash)
	return {"success": True, "msg": " ".join(filter(None, [_("The PDF is signed."), note]))}


def validate_sign(pdf_file_verify, root, chain=None, tsa_root_path=None):
	"""Validate every signature of the PDF against the CA root and the intermediate CAs.

	The time stamps come from a TSA, not from the CA. With the root certificate of the TSA,
	the time stamps are validated against it. Without it, they are not trusted."""
	trust_roots = [load_cert_from_pemder(root)]
	other_certs = [load_cert_from_pemder(ca) for ca in chain or []]
	vc = ValidationContext(trust_roots=trust_roots, other_certs=other_certs)
	ts_vc = ValidationContext(trust_roots=[load_cert_from_pemder(tsa_root_path)]) if tsa_root_path else vc
	with open(pdf_file_verify, "rb") as doc:
		reader = PdfFileReader(doc)
		results = []
		for signature in reader.embedded_signatures:
			if signature.sig_object_type == "/DocTimeStamp":
				# A document time stamp of the long-term validation: the TSA signs it, not the signer.
				results.append(document_timestamp_result(signature, validate_pdf_timestamp(signature, ts_vc)))
			else:
				status = validate_pdf_signature(signature, vc, ts_validation_context=ts_vc)
				results.append(signature_result(signature, status))
		return results


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
		"timestamp_trusted": bool(
			status.timestamp_validity
			and status.timestamp_validity.intact
			and status.timestamp_validity.valid
			and status.timestamp_validity.trusted
		),
		"coverage": status.coverage.name if status.coverage else None,
		"modification_level": status.modification_level.name if status.modification_level else None,
		"docmdp_ok": status.docmdp_ok,
		"certification": signature.docmdp_level.name if signature.docmdp_level else None,
	}


def document_timestamp_result(signature, status):
	"""Return the data of one document time stamp, with the keys of signature_result."""
	cert = status.signing_cert
	valid = bool(status.intact and status.valid and status.trusted)
	return {
		"field": signature.field_name,
		"document_timestamp": True,
		"valid": valid,
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
		"signing_time": format_utc(status.timestamp),
		"timestamp": format_utc(status.timestamp),
		"timestamp_trusted": valid,
		"coverage": status.coverage.name if status.coverage else None,
		"modification_level": status.modification_level.name if status.modification_level else None,
		"docmdp_ok": status.docmdp_ok,
		"certification": None,
	}


def format_utc(value):
	"""Show a UTC datetime in the time zone of the system."""
	if not value:
		return None
	return format_datetime(convert_utc_to_system_timezone(value).replace(tzinfo=None))
