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

The result shows one section for each signature. Each section has these tabs:

| Tab | Content |
|---|---|
| Validation | The final result, for example "The signature is judged VALID." |
| Modifications | The changes to the document after the signature. |
| Integrity | The check of the signed content. |
| Signing Time | The time of the signature. |
| Signer Info | The subject of the certificate, its fingerprints and the trust anchor. |

A signature is valid only if the CA of the sign setting issued the certificate of the signer.

The certificate container of the sign setting must have a CA root file. If it does not have one, the verification does not show a result.
