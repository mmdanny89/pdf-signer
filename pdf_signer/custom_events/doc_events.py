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


def validate_extension(doc, method):
    if doc.attached_to_field == "cert_file":
        if doc.is_private == 0:
            frappe.throw(_("Certificates are private files."), title="Error")
        if doc.attached_to_field == "cert_file":
            if not str(doc.file_name).endswith((".p12", ".pfx")):
                frappe.throw(_("Invalid extension for certificate file. Allowed: (.p12, .pfx)"), "Error")
        if doc.attached_to_field == "ca_root":
            if not str(doc.file_name).endswith((".cer")):
                frappe.throw(_("Invalid extension for CA Root file. Allowed: (.cer)"), "Error")
        if doc.attached_to_field == "ca_interm":
            if not str(doc.file_name).endswith((".cer")):
                frappe.throw(_("Invalid extension for CA Intermediaries files. Allowed: (.cer)"), "Error")
