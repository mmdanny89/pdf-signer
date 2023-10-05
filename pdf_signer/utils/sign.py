
from pyhanko import stamp
from pyhanko.pdf_utils import text
from pyhanko.pdf_utils.font import opentype
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
from pyhanko.sign import fields
import os
from pyhanko.sign import signers, timestamps
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko_certvalidator import ValidationContext
from datetime import datetime

from pyhanko.sign.general import load_cert_from_pemder
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature

from pyhanko.pdf_utils import  writer
import re


def sign_pdf(file_path, settings):
    pass


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

