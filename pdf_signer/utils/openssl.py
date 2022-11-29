# -*-coding:utf-8 -*-

"""
File    :   openssl.py
Date    :   2022/11/29 09:31:18
Author  :   Ing. Danny Molina Morales
Version :   1.0
E-mail  :   mmdanny89@gmail.com
"""


import os

import frappe
from cryptography import x509

# from cryptography.hazmat.bindings.openssl.binding import Binding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from frappe.utils import cstr
from OpenSSL import crypto
from OpenSSL.crypto import X509Store, X509StoreContext


def get_realpath_by_name_file(private_file):
    file_dir_site = frappe.get_site_path("private", "files", private_file)
    cert_file = os.path.abspath(file_dir_site)
    dir_name = os.path.dirname(cert_file)
    return {"full_path": cert_file, "file_path": dir_name}


def get_realpath_by_url_file(url_file):
    return os.getcwd() + "/" + cstr(frappe.local.site) + url_file


def parse_chain(cert_file_chain):
    """
    load certificates on file. The format of file is ONLY (PEM)
    return same dict of fucntion load_ca_root
    """
    data_ = {"ca": None, "errno": 0}
    start_line = b"-----BEGIN CERTIFICATE-----"
    result = []
    if str(cert_file_chain).endswith(".crt"):
        try:
            """Before parse. We needed validate that is .crt and PEM file format"""
            with open(cert_file_chain, "rb") as key_file:
                # cert_test = x509.load_pem_x509_certificate(key_file.read())
                key_file.close()
        except ValueError:
            data_["errno"] = 1
            return data_
        except FileNotFoundError:
            data_["errno"] = 2
            return data_
        except PermissionError:
            data_["errno"] = 3
            return data_
        """ Parse file and load all certs """
        with open(cert_file_chain, "rb") as key_file:
            pem_bytes = key_file.read()
            key_file.close()
        cert_slots = pem_bytes.split(start_line)
        for single_pem_cert in cert_slots[1:]:
            cert = x509.load_pem_x509_certificate(start_line + single_pem_cert)
            result.append(cert)
        data_["ca"] = result
    else:
        data_["errno"] = 1
    return data_


def load_certs(file_cert, passwd, file_ca_root=None, ca_interm=None, public_soap=None, is_chain=0):
    """
    Load certificates from Files.
        Parameters:
            :param file_cert is a private path for file
            :param file_ca_root is a private path for file
            :param ca_interm is a list of private files path
        Returns:
            { cert_user: {cert: Cert, priv_key: PKey, errno:0 },
                    ca_root: { errno:0, ca:[cas] }, cainterm: {interm:[cas_interm], errno:0},
                    public_soap: {cert:Cert, errno:0}
                    errno:0}
    """
    res_ = {"cert_user": None, "ca_root": None, "cainterm": None, "public_soap": None, "errno": 0}
    if file_ca_root:
        ca_root_ = load_ca_root(file_ca_root["file_name"], is_chain)
        if ca_root_["errno"] > 0:
            res_["errno"] = 2
            res_["ca_root"] = ca_root_
            return res_
        else:
            res_["ca_root"] = ca_root_
    if ca_interm:
        ca_interm_ = load_intermediaries(ca_interm)
        if ca_interm_["errno"] > 0:
            res_["errno"] = 3
            res_["cainterm"] = ca_interm_
            return res_
        else:
            res_["cainterm"] = ca_interm_
    certs_ = load_cert_user(file_cert, passwd)
    if certs_["errno"] > 0:
        res_["errno"] = 1
        res_["cert_user"] = certs_
        return res_
    res_["cert_user"] = certs_
    return res_


def load_ca_root(file_root, is_chain):
    """
    When CA ROOT is chain. Is very important that the file have this structure:
    CAROOT, INTERM_X, ITERM_Y. Frist Position of file is for ca root. Then the intermediaries
    """
    data_ = {"ca": None, "errno": 0}
    if file_root:
        real_path = get_realpath_by_name_file(file_root)
        if is_chain == 0:
            try:
                with open(real_path["full_path"], "rb") as key_file:
                    if str(real_path["full_path"]).endswith(".cer"):
                        certificate = x509.load_der_x509_certificate(key_file.read())
                        key_file.close()
                    elif str(real_path["full_path"]).endswith(".crt"):
                        certificate = x509.load_pem_x509_certificate(key_file.read())
                        key_file.close()
                    else:
                        data_["errno"] = 4
            except ValueError:
                data_["errno"] = 1
                return data_
            except FileNotFoundError:
                data_["errno"] = 2
                return data_
            except PermissionError:
                data_["errno"] = 3
                return data_
            data_["ca"] = [certificate]
        else:
            data_ = parse_chain(real_path["full_path"])
    return data_


def load_cert_user(file, password):
    """
    only p21 files.
    Return dict
    { cert: certobject, priv_key: privkeyobject, errno: 0 }
    """
    data_ = {"cert": None, "priv_key": None, "errno": 0}
    real_path = get_realpath_by_name_file(file)
    try:
        with open(real_path["full_path"], "rb") as key_file:
            if password:
                certificate = pkcs12.load_key_and_certificates(data=key_file.read(), password=str(password).encode())
            else:
                certificate = pkcs12.load_key_and_certificates(data=key_file.read(), password=None)
    except ValueError:
        data_["errno"] = 1
        return data_
    except FileNotFoundError:
        data_["errno"] = 2
        return data_
    except PermissionError:
        data_["errno"] = 3
        return data_
    else:
        data_["cert"] = certificate[1]
        data_["priv_key"] = certificate[0]
        return data_


def load_intermediaries(chain_files):
    res_ = {"interm": None, "errno": 0}
    list_certs = []
    if chain_files:
        for file_private in chain_files:
            full_path = get_realpath_by_url_file(file_private[0])
            try:
                with open(full_path, "rb") as key_file:
                    if str(full_path).endswith(".cer"):
                        certificate = x509.load_der_x509_certificate(key_file.read())
                        key_file.close()
                    elif str(full_path).endswith(".crt"):
                        certificate = x509.load_pem_x509_certificate(key_file.read())
                        key_file.close()
                    else:
                        res_["errno"] = 4
                        return res_
            except ValueError:
                res_["errno"] = 1
                return res_
            except FileNotFoundError:
                res_["errno"] = 2
                return res_
            except PermissionError:
                res_["errno"] = 3
                return res_
            else:
                list_certs.append(certificate)
    res_["interm"] = list_certs
    return res_


def verify_chain(file_cert, passwd, file_ca_root, ca_interm, is_chain=0):
    chain = load_certs(file_cert, passwd, file_ca_root, ca_interm, is_chain)
    if chain["errno"] == 0:
        # binding = Binding()
        # lib = binding.lib
        store = X509Store()
        ca_root = None
        chain_cas = []
        if chain["ca_root"] and len(chain["ca_root"]["ca"]) >= 1:
            ca_root = chain["ca_root"]["ca"][0]
            chain_cas.extend(chain["ca_root"]["ca"][1:])
        if ca_root:
            ca_root = crypto.load_certificate(crypto.FILETYPE_PEM, ca_root.public_bytes(serialization.Encoding.PEM))
            store.add_cert(ca_root)
        if chain["cainterm"] and chain["cainterm"]["interm"]:
            chain_cas.extend(chain["cainterm"]["interm"])
        chain_cas = convert_X509_crypto(chain_cas)
        cert = chain["cert_user"]["cert"]
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert.public_bytes(serialization.Encoding.PEM))
        store_ctx = X509StoreContext(store, cert, chain_cas)
        try:
            store_ctx.verify_certificate()
            return {"errno": 0, "code": 0}
        except crypto.X509StoreContextError:
            store_partial = X509Store()
            # store_partial.set_flags(lib.X509_V_FLAG_PARTIAL_CHAIN)
            if ca_root:
                store_partial.add_cert(ca_root)
            try:
                store_ctx.set_store(store_partial)
                store_ctx.verify_certificate()
                return {"errno": 0, "code": 1}
            except crypto.X509StoreContextError:
                return {"errno": 0, "code": 2}
    if chain["errno"] == 1:
        return {"errno": 1, "cert": chain["cert_user"]["errno"]}
    if chain["errno"] == 2:
        return {"errno": 2, "ca_root": chain["ca_root"]["errno"]}
    if chain["errno"] == 3:
        return {"errno": 3, "cainterm": chain["cainterm"]["errno"]}


def cert_detail(file, password):
    real_path = get_realpath_by_name_file(file)
    try:
        with open(real_path["full_path"], "rb") as key_file:
            if password:
                certificate = pkcs12.load_key_and_certificates(data=key_file.read(), password=str(password).encode())
            else:
                certificate = pkcs12.load_key_and_certificates(data=key_file.read(), password=None)
    except ValueError:
        return {"errno": 1}
    except FileNotFoundError:
        return {"errno": 2}
    except PermissionError:
        return {"errno": 3}
    else:
        city = certificate[1].issuer.get_attributes_for_oid(x509.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
        country = certificate[1].issuer.get_attributes_for_oid(x509.NameOID.COUNTRY_NAME)[0].value
        common_name = certificate[1].subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        expire = certificate[1].not_valid_after.strftime("%d/%m/%Y")
        return {"city": city, "country": country, "name": common_name, "expire": expire, "errno": 0}


def convert_X509_crypto(list_certs_api_criptographic):
    result = []
    if list_certs_api_criptographic:
        for cert_ in list_certs_api_criptographic:
            result.append(crypto.load_certificate(crypto.FILETYPE_PEM, cert_.public_bytes(serialization.Encoding.PEM)))
    return result


def get_public_bytes_from_memory_cert(cert_object):
    cert_bytes = cert_object.public_bytes(serialization.Encoding.PEM)
    return cert_bytes


def get_private_bytes_from_memory_pkey(pkey_object):
    key_bytes = pkey_object.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())
    return key_bytes
