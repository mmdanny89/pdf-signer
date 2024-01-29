# -*- coding: utf-8 -*-
"""
File    :   api_certs.py
Date    :   2023/10/02 11:26:32
Author  :   Ing. Danny Molina Morales
Version :   1.0
E-mail  :   mmdanny89@gmail.com
"""

from __future__ import unicode_literals

import json

import frappe

from pdf_signer.utils.openssl_doctype_tools import _cert_details, _verify_chain


@frappe.whitelist(allow_guest=False)
def cert_details(name):
    return _cert_details(name)


@frappe.whitelist(allow_guest=False)
def clean_attached_file_ca(doctype, name, file_url):
    for file in json.loads(file_url):
        file_ = frappe.db.get_value("Certificate Authority Intermediarie", {"name": file}, ["ca_interm"])
        if frappe.db.exists({"doctype": "File", "file_url": file_, "attached_to_doctype": doctype, "attached_to_field": "ca", "attached_to_name": name}):
            dc_name = frappe.db.get_value("File", {"attached_to_doctype": doctype, "file_url": file_, "attached_to_field": "ca", "attached_to_name": name}, ["name"])
            frappe.delete_doc(doctype="File", name=dc_name)
    return {"success": True}


@frappe.whitelist(allow_guest=False)
def verify_chain(name_container):
   return _verify_chain(name_container)