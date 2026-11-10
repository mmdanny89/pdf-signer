import base64
import io
import json
import os
from datetime import datetime

import frappe
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

from pdf_signer.utils.openssl import get_realpath_by_name_file


def sign_pdf_s(file_name, settings):
	try:
		file_cl = frappe.get_doc("File", file_name)
	except frappe.DoesNotExistError:
		frappe.publish_realtime("unfreeze_signer", message="", user=frappe.session.user)
		frappe.throw(msg="File does not exists!", title="Error")
	real_path = get_realpath_by_name_file(file_cl.file_name)
	cert_name = frappe.db.get_value(
		"File",
		{
			"attached_to_name": settings.cert_container,
			"attached_to_doctype": "Certificate Container",
			"attached_to_field": "cert_file",
		},
		"file_name",
	)
	if cert_name:
		ccert_file = get_realpath_by_name_file(cert_name)
		password_ = get_decrypted_password(
			"Certificate Container", name=settings.cert_container, fieldname="passphrase"
		)
		if ccert_file and password_:
			try:
				signer = signers.SimpleSigner.load_pkcs12(
					pfx_file=ccert_file["full_path"], passphrase=password_.encode()
				)
				signer_id = "Signature-" + str(int(datetime.now().timestamp()))
				perms_ = fields.MDPPerm.NO_CHANGES
				if int(settings.allow_add_signs) == 1:
					perms_ = fields.MDPPerm.FILL_FORMS
				box_position = tuple(json.loads(settings.postition).values())
				with open(real_path["full_path"], "rb") as inf:
					w = IncrementalPdfFileWriter(inf)
					fields.append_signature_field(
						w,
						sig_field_spec=fields.SigFieldSpec(
							signer_id,
							box=box_position,
							# to allow other add your sign
							doc_mdp_update_value=perms_,
							on_page=int(settings.on_page),
						),
					)
					meta = signers.PdfSignatureMetadata(field_name=signer_id)
					name_info = signer.subject_name
					stamp_style_ = None
					if int(settings.use_bg_image) == 1 or int(settings.use_own_sign_bg_image) == 1:
						background_ = None
						if int(settings.use_bg_image) == 1:
							bg_image_name = frappe.db.get_value(
								"File",
								{
									"attached_to_name": settings.name,
									"attached_to_doctype": "Electronic Sign Setting",
									"attached_to_field": "bg_image",
								},
								"file_name",
							)
							bg_image = get_realpath_by_name_file(bg_image_name)
							background_ = bg_image["full_path"]
						elif int(settings.use_own_sign_bg_image) == 1:
							background_ = Image.open(
								io.BytesIO(
									base64.b64decode(
										str(settings.own_sign).replace("data:image/png;base64,", "")
									)
								)
							)
						stamp_style_ = stamp.TextStampStyle(
							# the 'signer' and 'ts' parameters will be interpolated by pyHanko, if present
							stamp_text="Signed by: %(name_info)s\nTime: %(ts)s\n%(url)s",
							text_box_style=text.TextBoxStyle(font_size=int(settings.text_size)),
							background=images.PdfImage(background_),
						)
					else:
						stamp_style_ = stamp.QRStampStyle(
							border_width=0,
							# Let's include the URL in the stamp text as well
							stamp_text="Signed by: %(name_info)s\nTime: %(ts)s\n%(url)s",
							text_box_style=text.TextBoxStyle(font_size=int(settings.text_size)),
						)
					pdf_signer = signers.PdfSigner(
						meta,
						signer=signer,
						stamp_style=stamp_style_,
					)
					result = real_path["full_path"] + ".tmp"
					additional = ""
					if settings.additional:
						additional = str(settings.additional)
					with open(result, "wb") as outf:
						# with QR stamps, the 'url' text parameter is special-cased and mandatory, even if it
						# doesn't occur in the stamp text: this is because the value of the 'url' parameter is
						# also used to render the QR code.
						pdf_signer.sign_pdf(
							w, output=outf, appearance_text_params={"url": additional, "name_info": name_info}
						)
				head, tail = os.path.split(real_path["full_path"])
				os.remove(real_path["full_path"])
				newname = head + "/" + tail
				os.rename(result, newname)
				# TODO: update file content hash in table tabFile
				file_cl.content_hash = None
				file_cl.generate_content_hash()
				frappe.db.set_value("File", file_cl.name, "content_hash", file_cl.content_hash)
				return {"success": True, "msg": "Doc was signed.!"}
			except Exception as e:
				frappe.publish_realtime("unfreeze_signer", message="", user=frappe.session.user)
				frappe.throw(msg=str(e), title="Error")
		else:
			frappe.publish_realtime("unfreeze_signer", message="", user=frappe.session.user)
			frappe.throw(
				msg="Check Certificate and password on Cert Container for this Sign Settings", title="Error"
			)
	else:
		frappe.publish_realtime("unfreeze_signer", message="", user=frappe.session.user)
		frappe.throw(
			msg="Certificate does not exists. Check Cert Container for this Sign Settings", title="Error"
		)


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
