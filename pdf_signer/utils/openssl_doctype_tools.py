import frappe

from pdf_signer.utils.openssl import cert_detail, verify_chain
from frappe import _
from frappe.utils.password import get_decrypted_password


def _verify_chain(name_container):
    cert_container = frappe.db.get("Certificate Container", filters={"container_name": name_container})
    if cert_container:
        _name_cert = name_container
        doctype_ = "Certificate Container"
        attached_to_field = "cert_file"
        field_password = "passphrase"
        file_ca_root_attached = "ca_root"
        pass_ = cert_container["passphrase"]
        is_chain = cert_container["caroot_is_chain"]
        interm_ca = frappe.get_all(
            "Certificate Authority Intermediarie",
            {"parent": _name_cert, "parenttype": doctype_},
            ["ca_interm"],
            as_list=1,
        )
        file = frappe.db.get_value(
            "File",
            {
                "attached_to_name": _name_cert,
                "attached_to_doctype": doctype_,
                "attached_to_field": attached_to_field,
            },
            ["file_name"],
            as_dict=1,
        )
        file_ca = frappe.db.get_value(
            "File",
            {
                "attached_to_name": _name_cert,
                "attached_to_doctype": doctype_,
                "attached_to_field": file_ca_root_attached,
            },
            ["file_name"],
            as_dict=1,
        )
        if file and str(file["file_name"]).endswith((".p12", ".pfx")):
            passwd = None
            if pass_:
                passwd = get_decrypted_password(doctype_, _name_cert, field_password)
            if not file_ca and not interm_ca:
                msg = "Certificate Authority must exist to verify the certificate chain."
                frappe.throw(msg, "Error")
            chain_ = verify_chain(
                file["file_name"],
                passwd,
                file_ca_root=file_ca,
                ca_interm=interm_ca,
                is_chain=is_chain,
            )
            if chain_["errno"] == 1:
                if chain_["cert"] == 1:
                    frappe.throw("An error occurred while interpreting the Certificate. Check the Certificate and your Password.", "Error")
                elif chain_["cert"] == 2:
                    frappe.throw("Certificate File not found. Contact the Administrator.", "Error")
                elif chain_["cert"] == 3:
                    frappe.throw("The Certificate could not be accessed. Permission issues. Contact the Administrator.", "Error")
            elif chain_["errno"] == 2:
                if chain_["ca_root"] == 1:
                    frappe.throw("An error occurred while interpreting the Root CA. Format: PEM -> .crt or DER -> .cer. If your Root CA is a string: (PEM -> .crt). Structure: (CA_ROOT, INTERM_X, INTERM_Y...)", "Error")
                elif chain_["ca_root"] == 2 or chain_["ca_root"] == 4:
                    frappe.throw("CA-ROOT file not found. Contact the Administrator.", "Error")
                elif chain_["ca_root"] == 3:
                    frappe.throw("The CA-ROOT could not be accessed. Permission issues. Contact the Administrator.", "Error")
            elif chain_["errno"] == 3:
                if chain_["cainterm"] == 1:
                    frappe.throw("An error occurred while interpreting the Intermediary CA. Format: PEM -> .crt or DER -> .cer.", "Error")
                elif chain_["cainterm"] == 2 or chain_["cainterm"] == 4:
                    frappe.throw("The Intermediate CA was not found. Contact the Administrator.", "Error")
                elif chain_["cainterm"] == 3:
                    frappe.throw("The Intermediary CA could not be accessed. Permission issues. Contact the Administrator.", "Error")
            else:
                return chain_
        else:
            frappe.throw("This Container is empty.", "Error")
    else:
        frappe.throw("This Container does not exist.", "Error")


def _cert_details(name_container):
    cert_container = frappe.db.get("Certificate Container", filters={"name": name_container})
    if cert_container:
        _name_cert = name_container
        doctype_ = "Certificate Container"
        attached_to_field = "cert_file"
        field_password = "passphrase"
        pass_ = cert_container["passphrase"]
        file = frappe.db.get_value(
            "File",
            {
                "attached_to_name": _name_cert,
                "attached_to_doctype": doctype_,
                "attached_to_field": attached_to_field,
            },
            ["file_name"],
            as_dict=1,
        )
    if file and str(file["file_name"]).endswith((".p12", ".pfx")):
        passwd = None
        if pass_:
            passwd = get_decrypted_password(doctype_, _name_cert, field_password)
        result = cert_detail(file["file_name"], passwd)
        if result["errno"] == 1:
            frappe.throw("An error occurred while interpreting the Certificate File. Check the Certificate and your Password.", "Error")
        elif result["errno"] == 2:
            frappe.throw("Certificate File not found. Contact the Administrator.", "Error")
        elif result["errno"] == 3:
            frappe.throw("The Certificate File could not be accessed. Permission issues. Contact the Administrator.", "Error")
        else:
            return result
