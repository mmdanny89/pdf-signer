# -*-coding:utf-8 -*-
"""
File    :   api.py
Date    :   2022/11/16 09:06:15
Author  :   Ing. Danny Molina Morales
Version :   1.0
E-mail  :   mmdanny89@gmail.com
"""
import os

import frappe

from pdf_signer.utils import utils
from pdf_signer.utils.openssl import get_realpath_by_name_file
from pdf_signer.utils.sign import validate_sign


@frappe.whitelist(allow_guest=False)
def check_pdf(file_name, is_private):
    file_dir_site = None
    if int(is_private) == 1:
        file_dir_site = frappe.get_site_path("private", "files", file_name)
    else:
        file_dir_site = frappe.get_site_path("public", "files", file_name)
    cert_file = os.path.abspath(file_dir_site)
    if utils.get_mimetype_file(cert_file) == "application/pdf":
        return {"success": True}
    return {"success": False}


@frappe.whitelist(allow_guest=False)
def sign_pdf(file_name, sign_name):
    real_path = get_realpath_by_name_file(file_name)
    return {"success": False}


@frappe.whitelist(allow_guest=False)
def verify_pdf(file_name, sign_name):
    result = None
    file_real_path = get_realpath_by_name_file(file_name)["full_path"]
    cert_container = frappe.db.get_value("Electronic Sign Setting", {"name": sign_name, "status": "Enable"}, "cert_container")
    if cert_container:
        ca_root_file_name = frappe.db.get_value("File", {"attached_to_name": cert_container, "attached_to_doctype": "Certificate Container", "attached_to_field": "ca_root"}, "file_name")
        interms = frappe.db.get_list("File", {"attached_to_name": cert_container, "attached_to_doctype": "Certificate Container", "attached_to_field": "ca_interm"}, "file_name")
        if ca_root_file_name:
            ca_root_file_name = get_realpath_by_name_file(ca_root_file_name)["full_path"]
            if interms:
                interms = [get_realpath_by_name_file(interm["file_name"])["full_path"] for interm in interms]
            result = validate_sign(file_real_path, ca_root_file_name, interms)
    return result
