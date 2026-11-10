# Configuration

This guide uses example data. Replace the names and the files with your own data.

| Example item | Example value |
|---|---|
| Company | Example Company |
| Certificate container | Example Container |
| Sign setting | Example Signature |

## Requirements

- Frappe 16 and Python 3.14.
- The `libmagic1` system package. The app uses it to find the PDF files.
- A certificate in PKCS#12 format (.p12 or .pfx) that contains the certificate and its private key.
- The certificate of the certificate authority (CA) in DER format (.cer), if you want to verify signatures.

## Install the app

```bash
cd frappe-bench
bench get-app --branch version-16 https://github.com/mmdanny89/pdf-signer.git
bench --site example.local install-app pdf_signer
bench --site example.local migrate
```

Only the System Manager role can read and change the DocTypes of the app.

## Create a certificate container

A certificate container keeps the certificate, its passphrase and the certificates of the CA.

1. Open **PDF Signer > Certificates > Certificate Container**.
2. Click **Add Certificate Container**.
3. Type the name in **Certificate Container Name** and select the **Company**.
4. Save the container. The tabs **Certificate Settings** and **Certificate Authority (CA)** show after the first save.
5. In **Certificate Settings**, attach the .p12 or .pfx file in **Certificate File**.
6. Type the passphrase of the certificate in **Passphrase**.
7. In **Certificate Authority (CA)**, attach the CA root certificate (.cer) in **Certificate Authority File**.
8. If the chain has intermediate CAs, add one row for each intermediate CA in **Certificate Authority Intermediarie**.
9. Save the container.

Use these files:

| Field | Extensions | Format | Privacy |
|---|---|---|---|
| Certificate File | .p12, .pfx | PKCS#12 | Private file |
| Certificate Authority File | .cer | DER | Private file |
| Intermediate CA | .cer | DER | Private file |

The app checks only the Certificate File. It stops the save if the file is public or if the extension is not .p12 or .pfx. The app does not check the CA files, but it reads them from the private files folder.

### Check the certificate

After you save the container, the form shows two buttons:

- **View Certificate Info** shows the name, the country, the city and the expiration date of the certificate.
- **Verify Chain** checks the certificate against the CA root and the intermediate CAs.

**Verify Chain** gives one of these results:

| Result | Meaning |
|---|---|
| This chain match! | The full chain is correct. |
| This chain match partial! | The CA root is correct, but the chain is not complete. Add the missing intermediate CAs. |
| This chain not match! | The certificate does not come from this CA. |

## Create a sign setting

A sign setting tells the app which certificate to use and how the signature box looks. You can have more than one sign setting, for example one for each company.

1. Open **PDF Signer > Signing > Electronic Sign Setting**.
2. Click **Add Electronic Sign Setting**.
3. Type the name in **Sign Name**, and select the **Company** and the **Certificate Container**.
4. Set the fields of the signature box. Refer to [Signature box](#signature-box).
5. Save the sign setting.
6. Click **Enable Electronic Sign**.

A new sign setting has the status Disabled. The sign dialogs show only the sign settings with the status Enable. To stop a sign setting, click **Disabled Electronic Sign**.

The first sign setting that you save gets **Is Default**.

### Signature box

| Field | Default | Use |
|---|---|---|
| Allow Add Others Signs | On | On: other people can add signatures after this one. Off: the document does not accept changes after this signature. |
| Position | `{"x1":10, "y1":20, "x2":300, "y2":90}` | The corners of the signature box, in PDF points. The origin is the bottom-left corner of the page. |
| On Page | 0 | The page of the signature box. 0 is the first page and -1 is the last page. |
| Text Size | 11 | The size of the text in the signature box. |
| Additional Info | My Company, Ltd. | A text that the signature box shows. With the QR style, the QR code also contains this text. |
| Use backgroud image for Sign Box | Off | Shows the image of **Backgroud Image** behind the text. The image must be a private PNG file. |
| Use my own sign as backgroud of Sign Box | Off | Shows the hand signature that you draw in **Use my Own sign as backgroud of Sign Box** behind the text. |

The signature box shows the name of the signer, the time of the signature and the additional info. If the two background options are off, the box also shows a QR code.

## Global settings

**PDF Signer > Settings > Global Settings PDF Signer** has one option:

- **Always Ask to Sign when PDF is Uploaded in any Doctype**: after a user attaches a PDF file, the app opens the sign dialog. Refer to [signing.md](signing.md#sign-a-pdf-when-you-attach-it).
