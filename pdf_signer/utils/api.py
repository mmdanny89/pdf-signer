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
