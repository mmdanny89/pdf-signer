# Signing and verifying

## Sign a PDF

1. Open the PDF file in the **File** form. To find the PDF files, use **PDF Signer > Signing > PDF Files**.
2. Click **Sign PDF**.
3. Select a sign setting. The list shows only the enabled sign settings that you can sign with.
4. Click **Sign Document**.

The **Sign PDF** button shows only if you can change the file and you can sign with at least one sign setting. The app signs private and public PDF files.

The app signs the file in place. The file keeps its name and its URL, and the app updates its content hash. A message shows "The PDF is signed." when the signature is complete.

The signature is a PAdES signature (`ETSI.CAdES.detached`) that pyHanko makes. If the sign setting has a TSA, the signature also has a time stamp (PAdES B-T). With long-term validation, the PDF also gets the revocation data and a document time stamp (PAdES B-LTA).

### Signature field

The app selects the signature field in this order:

1. The first empty signature field of the PDF. For example, a contract that has a field for your signature.
2. A new field with the name `Signature-<random code>`, in the box of the sign setting.

After a certification signature of the type **Certification: Form Filling and Signing**, a new field is invisible. A new visible field changes the page, and that makes the certification not valid. The message of the app tells you when the signature is invisible. To have a visible signature after a certification, prepare the empty signature fields in the PDF before the certification.

### When the app does not sign

| Case | Message |
|---|---|
| The PDF has a certification signature of the type No Changes. | The PDF has a certification signature that does not allow changes. |
| The sign setting makes a certification signature and the PDF already has signatures. | A certification signature must be the first signature of the PDF. |
| You cannot sign with the sign setting. | You cannot sign with the sign setting. |
| You cannot change the file. | You do not have the permission to use the file. |

## Sign a PDF when you attach it

If **Always Ask to Sign when PDF is Uploaded in any Doctype** is on, the app opens the sign dialog after a user attaches a PDF file to a document.

The dialog opens only if the browser has loaded the File form one time in the session. Refer to [decisions.md](decisions.md#known-limits).

## Verify the signatures of a PDF

1. Open the PDF file in the **File** form.
2. Click **Verify Signed PDF**.
3. Select a sign setting. The list shows only the enabled sign settings that you can verify with. The app uses the CA root and the intermediate CAs of its certificate container.
4. Click **Verify Sign**.

The result shows one section for each signature, with these rows:

| Row | Content |
|---|---|
| Result | The final result. The signature is valid only if all the checks below pass. |
| Integrity | Intact, or changed after signing. |
| Cryptographic check | The check of the signature value. |
| Trust | Trusted, not trusted, or revoked certificate. |
| Type | Approval, or certification with its level. |
| Coverage | The part of the file that the signature covers. |
| Modifications | The changes to the file after the signature. |
| Signing time | The time that the signer reported. |
| Time stamp | The time of the time stamp, if the signature has one, and if the time stamp is trusted. |
| Signer, Issuer, Serial number, Valid until | The data of the certificate of the signer. |
| Trust anchor | The CA root that the chain of the certificate ends in. |
| SHA-256 fingerprint | The fingerprint of the certificate of the signer. |

A PDF with long-term validation also shows a section for the document time stamp. Its type is "Document time stamp (long-term validation)". The TSA signs it, so the verification uses the TSA Root Certificate of the sign setting.

A signature is trusted only if its chain ends in the CA root of the sign setting. The intermediate CAs help to build the chain, but they are not trust anchors.

The certificate container of the sign setting must have a CA root file. If it does not have one, the app shows an error.
