# PDF Signer
Simple application for signing PDF files with Electronic Certificates.

## Install on Frappe Cloud

1. Go to https://frappecloud.com/dashboard/#/sites and click the "New Site" button.
2. In Step 2 ("Select apps to install"), select "PDF Signer".
3. Complete the new site wizard.

## Install on Self-Hosted

```bash
cd frappe-bench
bench get-app https://github.com/mmdanny89/pdf-signer.git
bench --site sitename install-app pdf_signer
```
> Remeber to replace `sitename` with your site name.