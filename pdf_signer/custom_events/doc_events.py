# -*-coding:utf-8 -*-
"""
File    :   doc_events.py
Date    :   2022/11/14 14:30:58
Author  :   Ing. Danny Molina Morales
Version :   1.0
E-mail  :   mmdanny89@gmail.com
"""

import frappe
from frappe import _

from pdf_signer.utils import api


def remove_file_signed(doc, method):
    # TODO: remove file for app register.!!
    pass


def check_file_uploaded(doc, method):
    mime = api.check_pdf(doc.file_name, doc.is_private)
    if mime["success"]:
        ask = frappe.db.get_single_value("Global Settings PDF Signer", "always_ask")
        if int(ask) == 1:
            frappe.publish_realtime(event="ask_to_sign", message={"docname": doc.name}, user=frappe.session.user)
    pass


def validate_extension(doc, method):
    if doc.attached_to_field == "cert_file" or doc.attached_to_field == "key_file":
        if doc.is_private == 0:
            frappe.throw(_("Certificate and Key are private files."), title="Error")
        if doc.attached_to_field == "cert_file":
            if not str(doc.file_name).endswith((".cer", ".crt", ".p12", ".pfx")):
                frappe.throw(_("Invalid extension for certificate file. Allowed: (.cer, .crt, .p12, .pfx)"), "Error")
        if doc.attached_to_field == "key_file":
            if not str(doc.file_name).endswith((".pem", ".crt", ".key")):
                frappe.throw(_("Invalid extension for key file. Allowed: (.pem, .crt, .key)"), "Error")
