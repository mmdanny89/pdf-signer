# -*-coding:utf-8 -*-
"""
File    :   doc_events.py
Date    :   2022/11/14 14:30:58
Author  :   Ing. Danny Molina Morales
Version :   1.0
E-mail  :   mmdanny89@gmail.com
"""

import frappe


def remove_file_signed(doc, method):
    print("hello world")


def check_file_uploaded(doc, method):
    ask_way = frappe.db.get_single_value("Global Settings PDF Signer", "always_ask")
    if ask_way == 1:
        signature_setting = frappe.db.get("Electronic Sign Setting", filters={"status": "Enable", "is_default": 1})
        if signature_setting:
            frappe.publish_realtime(event="ask_to_sign", message={"task_id": 10000001, "foo": "bar"}, user=frappe.session.user)
        else:
            signs_enable = frappe.db.get_list("Electronic Sign Setting", filters={"status": "Enable"}, pluck="name")
            frappe.publish_realtime("ask_to_sign", message={"name_sign": signs_enable, "file_name": doc.name}, user=frappe.session.user)
