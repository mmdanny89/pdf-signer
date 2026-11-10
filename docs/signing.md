# Signing and verifying

## Sign a PDF

1. Open the PDF file in the **File** form. To find the PDF files, use **PDF Signer > Signing > PDF Files**.
2. Click **Sign PDF**.
3. Select an enabled sign setting.
4. Click **Sign Document**.

The app signs the file in place. The file keeps its name and its URL, and the app updates its content hash. A message shows "Doc was signed.!" when the signature is complete.

The signature is a PAdES signature that pyHanko makes. Each signature adds a field with the name `Signature-<timestamp>` to the PDF.

If **Allow Add Others Signs** is on, you can sign the same file again with the same or another sign setting. If it is off, the first signature does not allow changes, and a new signature is a change.

## Sign a PDF when you attach it

If **Always Ask to Sign when PDF is Uploaded in any Doctype** is on, the app opens the sign dialog after a user attaches a PDF file to a document.

The dialog opens only if the browser has loaded the File form one time in the session. Refer to [decisions.md](decisions.md#known-limits).

## Verify the signatures of a PDF

1. Open the PDF file in the **File** form.
2. Click **Verify Signed PDF**.
3. Select an enabled sign setting. The app uses the CA root and the intermediate CAs of its certificate container.
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
| Time stamp | The time of the time stamp, if the signature has one. |
| Signer, Issuer, Serial number, Valid until | The data of the certificate of the signer. |
| Trust anchor | The CA root that the chain of the certificate ends in. |
| SHA-256 fingerprint | The fingerprint of the certificate of the signer. |

A signature is trusted only if its chain ends in the CA root of the sign setting. The intermediate CAs help to build the chain, but they are not trust anchors.

The certificate container of the sign setting must have a CA root file. If it does not have one, the app shows an error.
