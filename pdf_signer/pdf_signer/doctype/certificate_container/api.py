"""
File    :   api_certs.py
Date    :   2023/10/02 11:26:32
Author  :   Ing. Danny Molina Morales
Version :   1.0
E-mail  :   mmdanny89@gmail.com
"""

import frappe

from pdf_signer.utils.openssl_doctype_tools import _cert_details, _verify_chain


def check_container_permission(name):
	frappe.has_permission("Certificate Container", "read", doc=name, throw=True)


@frappe.whitelist()
def cert_details(name):
	check_container_permission(name)
	return _cert_details(name)


@frappe.whitelist()
def verify_chain(name_container):
	check_container_permission(name_container)
	return _verify_chain(name_container)
