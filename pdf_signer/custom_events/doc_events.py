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
    # TODO: remove file for app register.!!
    pass


def check_file_uploaded(doc, method):
    frappe.publish_realtime(event="ask_to_sign", message='alert("{0}")'.format("JAHJAGSJH"), user=frappe.session.user)
    pass
