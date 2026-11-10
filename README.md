
<a name="readme-top"></a>

<br />
<div align="center">
  <a href="https://github.com/mmdanny89/pdf-signer">
    <img src="images/esign.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">PDF Signer</h3>

  <p align="center">
    Sign PDF files with electronic certificates in Frappe, with or without ERPNext.
    <br />
    <a href="docs/configuration.md"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/mmdanny89/pdf-signer/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/mmdanny89/pdf-signer/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-pdf-signer">About PDF Signer</a></li>
    <li><a href="#requirements">Requirements</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#quick-start">Quick start</a></li>
    <li><a href="#documentation">Documentation</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About PDF Signer

[![Product Name Screen Shot][product-screenshot]](https://github.com/mmdanny89/pdf-signer)

PDF Signer applies electronic signatures to PDF files in the desk of Frappe. It uses [pyHanko](https://github.com/MatthiasValvekens/pyHanko).

- **PAdES signatures** with certificates in PKCS#12 format (.p12 or .pfx).
- **Approval or certification signatures**: an approval lets other people sign after you. A certification is the first signature, and it allows no changes, or only form filling and signing.
- **Time stamps and long-term validation** (PAdES B-T and B-LTA) with a time stamp authority (TSA).
- **Verification** of the signatures of a PDF against the certificate authority (CA) of a container. The result shows the integrity, the trust, the modifications, the time stamp and the data of the certificate.
- **Signature box**: visible or invisible, on the first page, the last page or a page number, in a position of the page or in a custom place. The box shows a text, a QR code, an image or a signature that you draw, with your colors and font. A preview shows the box before you save.
- **Ask to sign** when a user attaches a PDF file to any document.
- **Access by sign setting**: each sign setting has the users and the roles that can sign and verify with it. A personal certificate can be for its holder only.
- **Certificate containers**: the certificate, its passphrase and the chain of the CA. The form shows the data of the certificate and the state of its chain.
- **English and Spanish (Spain)**.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- REQUIREMENTS -->
## Requirements

| Item | Version or detail |
|---|---|
| Frappe | 16. ERPNext is not necessary. |
| Python | 3.14 |
| System package | `libmagic1`. The app uses it to find the PDF files. On Frappe Cloud, the app installs it. |
| Python packages | `pyHanko[opentype,qr]` 0.38 and `python-magic` 0.4. `bench get-app` installs them. |
| Certificate | A PKCS#12 file (.p12 or .pfx) with the certificate and its private key. |
| Certificate authority | The CA root, and the intermediate CAs if the chain has them, in DER or PEM format (.cer or .crt). They are necessary to verify signatures. |
| Time stamp (optional) | The URL of a TSA and its root certificate. |
| Long-term validation (optional) | The server must reach the TSA and the OCSP or CRL addresses of the certificates. |

For Frappe 14 and 15, use the branches `version-14` and `version-15`. Their requirements are different.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- INSTALLATION -->
## Installation

### Self-hosted

```bash
cd frappe-bench
bench get-app --branch version-16 https://github.com/mmdanny89/pdf-signer.git
bench --site sitename install-app pdf_signer
bench --site sitename migrate
bench build --app pdf_signer
```

Replace `sitename` with the name of your site.

### Frappe Cloud

1. Go to https://frappecloud.com/dashboard/#/sites and click **New Site**.
2. In the step "Select apps to install", select **PDF Signer**.
3. Complete the new site wizard.

### Branches

| Frappe | Branch |
|---|---|
| 16 | `version-16` (also `main`) |
| 15 | `version-15` |
| 14 | `version-14` |

Since version 16.0.0, `main` follows the latest version of Frappe. To install or update a site of Frappe 14 or 15, use `version-14` or `version-15`, not `main`.

### Update from an earlier version

`bench --site sitename migrate` moves the sign settings to the new fields. The look of the signatures stays the same. After the update, check these items:

- **Roles**: give the role **PDF Signer Manager** to the users that configure the app, and **PDF Signer User** to the users that sign. Then set the tab **Access** of each sign setting. Without users and roles in a sign setting, only the PDF Signer Manager and the System Manager can sign.
- **Signature Type**: the old option "Allow Add Others Signs" did not change the signature. The migration sets Approval if it was on, and Certification: No Changes if it was off.
- **Text of the box**: the migration keeps the old text "Signed by … / Time …". You can change it or leave it empty.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- QUICK START -->
## Quick start

1. Open **PDF Signer > Certificates > Certificate Container**, and make a container. Save it.
2. Attach the certificate file and type its passphrase. Attach the CA root, and add the intermediate CAs. The header of the form turns green when the chain is valid.
3. Open **PDF Signer > Signing > Electronic Sign Setting**, and make a sign setting for the container. Set the tabs **Signature Policy**, **Access** and **Appearance**. Click **Preview Signature Box** to see the box. Save, and click **Enable Sign Setting**.
4. Open a PDF file in the **File** form, and click **Sign PDF**. To check the signatures, click **Verify Signed PDF**.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- DOCUMENTATION -->
## Documentation

| Guide | Content |
|---|---|
| [Configuration](docs/configuration.md) | Install, roles, certificate containers, sign settings, signature box, time stamps, global settings |
| [Signing and verifying](docs/signing.md) | Sign a PDF, sign when you attach a PDF, verify the signatures |
| [Desk](docs/desk.md) | Apps screen, desktop, dock, sidebar, workspace and icons |
| [Development](docs/development.md) | Structure, pre-commit, linters, translations, tests and branches |
| [Decisions](docs/decisions.md) | The decisions of the version for Frappe 16, and the known limits |

For Frappe 14 and 15, refer to the [Wiki Usage](https://github.com/mmdanny89/pdf-signer/wiki/Usage).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

This app uses `pre-commit` for code formatting and linting. [Install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/pdf_signer
pre-commit install
```

Pre-commit uses these tools to check and format the code:

- ruff
- eslint
- prettier

The texts of the app are in English, and `pdf_signer/locale/es.po` has their translation to Spanish. Refer to [Development](docs/development.md#translations).

<p align="right">(<a href="#readme-top">back to top</a>)</p>





<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>





[product-screenshot]: images/pdf-signer-dashboard.png
