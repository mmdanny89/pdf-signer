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

## Roles

| Role | What it can do |
|---|---|
| PDF Signer Manager | Configure the app: certificate containers, sign settings and global settings. Sign and verify with the settings that do not limit the users. |
| PDF Signer User | Select a sign setting in the sign and verify dialogs. The Access tab of each sign setting decides if the user can sign or verify with it. |
| System Manager | The same as PDF Signer Manager. |

To sign a PDF, a user also needs the permission to change the file. For an attached file, this is the permission to change the document that the file is attached to.

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
| Certificate Authority File | .cer, .crt | DER (.cer) or PEM (.crt) | Private file |
| Intermediate CA | .cer, .crt | DER (.cer) or PEM (.crt) | Private file |

The app stops the upload if a file is public or if its extension is not in the list.

The passphrase is optional. Leave it empty if the certificate file does not have one.

The signature includes the CA root and the intermediate CAs of the container. This helps other programs to validate the signature.

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

The first sign setting that you save gets **Is Default**. The dialogs show the default setting first.

### Signature policy

The tab **Signature Policy** sets the type of the signature and the data that PDF readers show in the signature panel.

| Signature Type | What it does | Use it for |
|---|---|---|
| Approval | A normal signature. Other people can sign the PDF after you. | Most documents. |
| Certification: No Changes | The first signature of the PDF. Any later change, also a new signature, makes it not valid. The app does not sign a PDF with this signature again. | A final document that nobody else signs. |
| Certification: Form Filling and Signing | The first signature of the PDF. Other people can fill the form fields and sign. | A document that you send to other people to sign. |

A PDF can have only one certification signature, and it must be the first signature. The app stops a certification if the PDF already has signatures.

**Reason**, **Location** and **Contact Information** are optional. PDF readers show them in the signature panel.

### Access

The tab **Access** decides who can use the sign setting.

| Field | Rule |
|---|---|
| Users That Can Sign | Only these users can sign. Use it for a personal certificate. If you add users, the app does not use the roles to sign. |
| Roles That Can Sign | Users with one of these roles can sign. If this field and the users are empty, only the PDF Signer Manager and the System Manager can sign. |
| Roles That Can Verify | Users with one of these roles can verify. If it is empty, all the users that can read the PDF can verify. |

If you add users, the Administrator can sign only if it is in the list.

### Signature box

| Field | Default | Use |
|---|---|---|
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
