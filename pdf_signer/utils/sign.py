
from pyhanko import stamp
from pyhanko.pdf_utils import text
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
from pyhanko.sign import fields
import os
from pyhanko.pdf_utils import text, images
from pyhanko_certvalidator import ValidationContext
from datetime import datetime

from pyhanko.sign.general import load_cert_from_pemder
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature

import re
from pdf_signer.utils.openssl import get_realpath_by_name_file
import json
import frappe
from frappe.utils.password import get_decrypted_password


def sign_pdf_s(file_name, settings):
	try: 
		file_cl = frappe.get_doc("File", file_name)
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
		ccert_file = get_realpath_by_name_file(cert_name)
		password_ = get_decrypted_password("Certificate Container", name=settings.cert_container, fieldname="passphrase")
		signer = signers.SimpleSigner.load_pkcs12(pfx_file=ccert_file["full_path"], passphrase=password_.encode())
		signer_id = "Signature-"+str(int(datetime.now().timestamp()))
		perms_ = fields.MDPPerm.NO_CHANGES
		if int(settings.allow_add_signs) == 1:
			perms_ = fields.MDPPerm.FILL_FORMS
		box_position = tuple(json.loads(settings.postition).values())
		with open(real_path["full_path"], 'rb') as inf:
			w = IncrementalPdfFileWriter(inf)
			fields.append_signature_field(
				w, sig_field_spec=fields.SigFieldSpec(
					signer_id, box=box_position,
					# to allow other add your sign
					doc_mdp_update_value=perms_,
					on_page=int(settings.on_page)
				)
			)
			meta = signers.PdfSignatureMetadata(field_name=signer_id)
			name_info = signer.subject_name
			stamp_style_ = None
			if int(settings.use_bg_image) == 1 or int(settings.use_own_sign_bg_image) == 1:
				if int(settings.use_bg_image) == 1:
					bg_image_name = frappe.db.get_value(
							"File",
							{
								"attached_to_name": settings.name,
								"attached_to_doctype": "Electronic Sign Setting ",
								"attached_to_field": "bg_image",
							},
							"file_name",
						)
					bg_image = get_realpath_by_name_file(bg_image_name)
					stamp_style_= stamp.TextStampStyle(
						# the 'signer' and 'ts' parameters will be interpolated by pyHanko, if present
						stamp_text='Signed by: %(name_info)s\nTime: %(ts)s\n%(url)s',
						text_box_style=text.TextBoxStyle(
							font_size=int(settings.text_size)
						),
						background=images.PdfImage(bg_image["full_path"])
					)
			else:
				stamp_style_ = stamp.QRStampStyle(
					border_width=0,
					# Let's include the URL in the stamp text as well
					stamp_text='Signed by: %(name_info)s\nTime: %(ts)s\n%(url)s',
					text_box_style=text.TextBoxStyle(
						font_size=int(settings.text_size)
					),
				)
			pdf_signer = signers.PdfSigner(
				meta, signer=signer, stamp_style=stamp_style_,
			)
			result = real_path["full_path"] + '.tmp'
			additional = ""
			if settings.additional:
				additional = str(settings.additional)
			with open(result, 'wb') as outf:
				# with QR stamps, the 'url' text parameter is special-cased and mandatory, even if it
				# doesn't occur in the stamp text: this is because the value of the 'url' parameter is
				# also used to render the QR code.
				pdf_signer.sign_pdf(
					w, output=outf,
					appearance_text_params={'url': additional, 'name_info': name_info}
				)
		head, tail = os.path.split(real_path["full_path"])
		os.remove(real_path["full_path"])
		newname= head + '/' + tail
		os.rename(result, newname)
		#TODO: update file content hash in table tabFile
		file_cl.content_hash = None
		file_cl.generate_content_hash()
		frappe.db.set_value("File", file_cl.name, "content_hash", file_cl.content_hash)
		return {"success": True, "msg": "Doc was signed.!"}
	except Exception as e:
		frappe.publish_realtime("unfreeze_signer", message="", user=frappe.session.user)
		frappe.throw(msg=str(e), exc=e.type, title="Error")
		

def validate_sign(pdf_file_verify, root, chain=[]):
	result = []
	root = load_cert_from_pemder(root)
	trust = [root]
	if chain:
		for ca in chain:
			root_cert = load_cert_from_pemder(ca)
			trust.append(root_cert)
	vc = ValidationContext(trust_roots=trust)
	with open(pdf_file_verify, 'rb') as doc:
		r = PdfFileReader(doc)
		for signature in r.embedded_signatures:
			status = validate_pdf_signature(signature, vc)
			data_r = prepare_output(status=status.pretty_print_details())
			result.append({"signature": signature.field_name, "status": data_r})
	return result


def prepare_output(status):
	result = {"integrity": None, "bottom": None, "modification": None, "time": None}
	info = re.search("Signer info\\n\-\-\-\-\-\-\-\-\-\-\-\\n(.*?)\\n\\n\\nIntegrity\\n\-\-\-\-\-\-\-\-\-\\n", status, flags=re.DOTALL)
	integrity = re.search("\\n\\n\\nIntegrity\\n\-\-\-\-\-\-\-\-\-\\n(.*?)\\n\\n\\nSigning time\\n\-\-\-\-\-\-\-\-\-\-\-\-\\n", status, flags=re.DOTALL)
	time_s = re.search('\\n\\n\\nSigning time\\n\-\-\-\-\-\-\-\-\-\-\-\-\\n(.*?)\\n\\n\\nModifications\\n\-\-\-\-\-\-\-\-\-\-\-\-\-\\n', status, flags=re.DOTALL)
	modification = re.search('\\n\\n\\nModifications\\n\-\-\-\-\-\-\-\-\-\-\-\-\-\\n(.*?)\\n\\n\\nBottom line\\n\-\-\-\-\-\-\-\-\-\-\-\\n', status, flags=re.DOTALL)
	bottom = re.search('\\n\\n\\nBottom line\\n\-\-\-\-\-\-\-\-\-\-\-\\n(.*?)\\n\\n', status, flags=re.DOTALL)
	if integrity:
		result["integrity"] = str(integrity.group(1)).replace("\n", "")
	if bottom:
		result["bottom"] = bottom.group(1)
	if modification:
		result["modification"] = str(modification.group(1)).replace("\n", "")
	if time_s:
		result["time"] = time_s.group(1)
	if info:
		result["info"] = parse_info(info.group(1))
	return result


def parse_info(info):
	info_r = {}
	if info:
		data_parse = info.split("\n")
		if data_parse:
			info_r["subject"] = data_parse[0].replace("Certificate subject: ", "")
			info_r["fingerprint"] = [
				{"name": data_parse[1].split(":")[0], "value": data_parse[1].split(":")[1]},
				{"name": data_parse[2].split(":")[0], "value": data_parse[2].split(":")[1]},
			]
			info_r["trust_anchor"] = data_parse[3].replace("Trust anchor: ", "")
			info_r["trust"] = data_parse[4].replace("\n", "")
	return info_r

