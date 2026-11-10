"""The certificate of a certificate container: its data and the state of its chain."""

import asyncio
from datetime import UTC, datetime

import frappe
from asn1crypto import x509 as asn1_x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from frappe import _
from frappe.utils.password import get_decrypted_password
from pyhanko.keys import load_cert_from_pemder
from pyhanko_certvalidator import CertificateValidator, ValidationContext
from pyhanko_certvalidator.errors import PathBuildingError, PathValidationError, ValidationError

from pdf_signer.utils.sign import CONTAINER, container_files

EXPIRING_DAYS = 30


def name_attributes(name):
	"""Return the attributes of an X.509 name that the form shows."""
	native = name.native
	return {
		"common_name": native.get("common_name"),
		"organization": native.get("organization_name"),
		"organizational_unit": native.get("organizational_unit_name"),
		"locality": native.get("locality_name"),
		"state": native.get("state_or_province_name"),
		"country": native.get("country_name"),
		"email": native.get("email_address"),
		"serial_number": native.get("serial_number"),
		"dn": name.human_friendly,
	}


def validity(cert):
	not_before = cert["tbs_certificate"]["validity"]["not_before"].native
	not_after = cert["tbs_certificate"]["validity"]["not_after"].native
	now = datetime.now(UTC)
	days_left = (not_after - now).days
	if now < not_before:
		state = "not_yet_valid"
	elif now > not_after:
		state = "expired"
	elif days_left <= EXPIRING_DAYS:
		state = "expiring"
	else:
		state = "valid"
	return {
		"state": state,
		"days_left": days_left,
		"not_before": not_before.strftime("%Y-%m-%d"),
		"not_after": not_after.strftime("%Y-%m-%d"),
	}


def load_certificate(container):
	"""Return the certificate of the container as an asn1crypto certificate.

	It stops with a clear message if the container has no certificate file, or if the file
	or the passphrase is not correct."""
	files = container_files(container)
	if not files.cert:
		raise frappe.ValidationError(_("Attach the certificate file in the tab Certificate Settings."))
	passphrase = get_decrypted_password(CONTAINER, container, "passphrase", raise_exception=False)
	try:
		with open(files.cert, "rb") as f:
			key, cert, _others = pkcs12.load_key_and_certificates(
				f.read(), passphrase.encode() if passphrase else None
			)
	except (ValueError, TypeError):
		raise frappe.ValidationError(
			_("The certificate cannot be read. Check the certificate file and the passphrase.")
		)
	# Without the private key, cryptography gives the certificate in the other certificates.
	if key is None:
		raise frappe.ValidationError(
			_("The certificate file does not contain the private key. The app needs it to sign.")
		)
	if cert is None:
		raise frappe.ValidationError(_("The certificate file does not contain a certificate."))
	return asn1_x509.Certificate.load(cert.public_bytes(serialization.Encoding.DER))


def chain_status(cert, container):
	"""Return the state of the chain from the certificate to the CA root of the container.

	valid: the chain ends in the CA root, and every certificate is valid now.
	no_ca: the container has no CA root, so the chain cannot be checked.
	invalid: the chain does not end in the CA root, or a certificate is not valid."""
	files = container_files(container)
	if not files.root:
		return {
			"state": "no_ca",
			"message": _("Attach the CA root in the tab Certificate Authority (CA) to check the chain."),
		}
	try:
		context = ValidationContext(
			trust_roots=[load_cert_from_pemder(files.root)],
			other_certs=[load_cert_from_pemder(path) for path in files.interms],
		)
		path = asyncio.run(
			CertificateValidator(cert, validation_context=context).async_validate_usage(key_usage=set())
		)
	except PathBuildingError:
		return {
			"state": "invalid",
			"message": _(
				"The chain is not valid: the certificate does not come from the CA root of the container, or an intermediate CA is missing."
			),
		}
	except (PathValidationError, ValidationError) as e:
		return {"state": "invalid", "message": _("The chain is not valid: {0}").format(e)}
	except Exception:
		return {
			"state": "invalid",
			"message": _("The CA files cannot be read. Use DER (.cer) or PEM (.crt) files."),
		}
	return {
		"state": "valid",
		"message": _("The certificate chain is valid."),
		"chain": [
			c.subject.native.get("common_name") or c.subject.human_friendly for c in reversed(list(path))
		],
	}


@frappe.whitelist()
def certificate_summary(name):
	"""Return the data of the certificate of the container and the state of its chain."""
	frappe.has_permission(CONTAINER, "read", doc=name, throw=True)
	try:
		cert = load_certificate(name)
	except frappe.ValidationError as e:
		frappe.clear_messages()
		return {"success": False, "error": str(e)}
	return {
		"success": True,
		"subject": name_attributes(cert.subject),
		"issuer": name_attributes(cert.issuer),
		"validity": validity(cert),
		"serial": format(cert.serial_number, "X"),
		"sha256": cert.sha256_fingerprint,
		"chain": chain_status(cert, name),
	}
