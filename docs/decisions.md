# Decisions

These are the decisions of the version for Frappe 16, with their reasons.

## Base branch

The branch `version-16` starts from `version-15`, not from `main`. `version-15` has three fixes that `main` does not have: the label "Verify Signed PDF", the `.DS_Store` rule of `.gitignore`, and the chain check without `is_chain`.

## Package and dependencies

The app uses `pyproject.toml` with flit, like a new Frappe 16 app. The app does not have `setup.py`, `requirements.txt` or `MANIFEST.in`. The Python dependencies are in `[project] dependencies`. The apt package `libmagic1` is in `[deploy.dependencies.apt]` for Frappe Cloud.

pyHanko stays on version 0.20.1. This version works on Python 3.14 with cryptography 50 and pyOpenSSL 26.

## Icons and buttons

Frappe 16 does not load Font Awesome. The forms use the SVG icons of Frappe (`frappe.utils.icon`), and the buttons use `frappe.ui.button.dress`. The app icons come from the app icon of the README. Refer to [desk.md](desk.md#icons).

## File list

The app had a `file_list.js` that replaced the list settings of File with an empty object. This removed the list settings of Frappe for File. The version for Frappe 16 does not have this file.

## Known limits

- The sign dialog after an upload opens only if the browser has loaded `utils.js`. The File form loads it. The bundle `pdf_signer.bundle.js` is empty.
- The app reads the files of the certificates, the background image and the PDF from the private files folder. A public PDF cannot be signed.
- The sign setting needs a passphrase. A certificate without a passphrase cannot sign.
- The fields **Add QR to Sign**, **Text Font**, **Algorithm** and **Role** do not change the signature.
- The DocType **PDF Signer Documents Signed** does not get records.
- The app does not check the extension and the privacy of the CA files. Refer to [configuration.md](configuration.md#create-a-certificate-container).
