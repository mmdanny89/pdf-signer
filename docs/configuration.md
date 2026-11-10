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
4. Set the tabs **Signature Policy**, **Access** and **Appearance**. Refer to the sections below.
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

### Appearance

The tab **Appearance** sets the signature box: its page, its place, its style and its text. Each field has a description in the form.

#### Signature box

| Field | Default | Use |
|---|---|---|
| Visible Signature | On | Off makes an invisible signature. PDF readers show it only in the signature panel. |
| Page | First Page | First Page, Last Page, or Page Number. With Page Number, give the number in **Page Number**. The first page is 1. |
| Position | Bottom Right | Bottom Left, Bottom Center, Bottom Right, Top Left, Top Center, Top Right, or Custom. |
| Width (mm), Height (mm) | 70, 25 | The size of the box. |
| Margin (mm) | 10 | The distance between the box and the edges of the page. Not for Custom. |
| Distance from the Left (mm), Distance from the Bottom (mm) | | Only for Custom. The distance from the bottom-left corner of the page to the bottom-left corner of the box. |

The app calculates the box from the size of the page, so the same setting works for A4, Letter and other sizes. The app does not sign in these cases:

- The PDF has fewer pages than **Page Number**.
- The box does not fit on the page.

#### Style

| Style | Content of the box |
|---|---|
| Text | Only the text. |
| Text and QR Code | The text and a QR code. **QR Code Position** puts the QR code on the left, on the right, above or below the text. **QR Code Content** is the text or the web address in the QR code. If it is empty, the QR code contains the Additional Text, or the address of the site. |
| Background Image | The text on a PNG or JPG image, for example the stamp of the company. |
| Handwritten Signature | The text on a signature that you draw in the form. |

For a drawn signature, **Handwritten Signature Color** sets its color in the PDF. The drawing pad of the form shows the signature in another color. This does not change the PDF.

**Background Opacity** sets the strength of the image or of the drawn signature. 100% gives the full color. A lower value makes it lighter, so that the text is easier to read.

#### Text

| Field | Default | Use |
|---|---|---|
| Text | `Signed by: %(signer)s` / `Date: %(ts)s` / `%(additional)s` | The text of the box, one line for each line of the field. |
| Additional Text | | The value of `%(additional)s`, for example the name of the company. |
| Date Format | `%d/%m/%Y %H:%M:%S %Z` | The format of `%(ts)s`. |
| Font File | | Optional. A TTF or OTF font. |
| Text Size | 11 | The size of the text in points. |
| Text Color | #000000 | The color of the text. |
| Border Width | 0 | The width of the line around the box, in points. 0 gives no border. |
| Border Color | #000000 | The color of the line around the box. |

These variables are available in **Text**:

| Variable | Value |
|---|---|
| `%(signer)s` | The common name of the certificate holder. |
| `%(ts)s` | The date and the time of the signature, in the format of **Date Format**. |
| `%(reason)s`, `%(location)s` | The Reason and the Location of the tab Signature Policy. |
| `%(additional)s` | The Additional Text. |
| `%(url)s` | The content of the QR code. |

The default text is in English. To have the text in Spanish, change it, for example to `Firmado por: %(signer)s`. To show a % sign, write `%%`. The form stops the save if the text has an unknown variable.

The standard PDF font shows letters with accents and the letter ñ. It does not show other special characters, for example the em dash. For these characters, attach a TTF or OTF font in **Font File**. With a QR code, the text is small, because it shares the box with the code. Use a larger box or fewer lines.

## Global settings

**PDF Signer > Settings > Global Settings PDF Signer** has one option:

- **Always Ask to Sign when PDF is Uploaded in any Doctype**: after a user attaches a PDF file, the app opens the sign dialog. Refer to [signing.md](signing.md#sign-a-pdf-when-you-attach-it).
