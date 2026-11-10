# Decisions

These are the decisions of the version for Frappe 16, with their reasons.

## Base branch

The branch `version-16` starts from `version-15`, not from `main`. `version-15` has three fixes that `main` does not have: the label "Verify Signed PDF", the `.DS_Store` rule of `.gitignore`, and the chain check without `is_chain`.

## Package and dependencies

The app uses `pyproject.toml` with flit, like a new Frappe 16 app. The app does not have `setup.py`, `requirements.txt` or `MANIFEST.in`. The Python dependencies are in `[project] dependencies`. The apt package `libmagic1` is in `[deploy.dependencies.apt]` for Frappe Cloud.

The app uses pyHanko 0.38 with the extras `opentype` and `qr`. pyHanko 0.20.1 was too old: it had no text color and no border color, and it did not get security fixes.

The app does not use the extra `image-support`. That extra needs `python-barcode==0.16.1`, and the xpos app needs `python-barcode` 0.15.1 in the same bench. The app uses Pillow from Frappe for the images.

The verification reads the status object of pyHanko. It does not parse the text of `pretty_print_details`, because that text changes between versions and cannot be translated.

## Icons and buttons

Frappe 16 does not load Font Awesome. The forms use the SVG icons of Frappe (`frappe.utils.icon`), and the buttons use `frappe.ui.button.dress`. The app icons come from the app icon of the README. Refer to [desk.md](desk.md#icons).

## File list

The app had a `file_list.js` that replaced the list settings of File with an empty object. This removed the list settings of Frappe for File. The version for Frappe 16 does not have this file.

## No company field

The certificate containers and the sign settings had a mandatory link to Company. Company is a DocType of ERPNext, so on a site without ERPNext the user could not save a container or a sign setting. The app does not use the company, so the version for Frappe 16 does not have this field. The column stays in the database tables.

## Roles and access

The app has two roles: PDF Signer Manager configures the app, and PDF Signer User signs and verifies. Each sign setting has its own users and roles. The users win over the roles, because a personal certificate is for its holder only. Without users and roles, only the managers can sign, as in the earlier versions, where only the System Manager could use the app.

The whitelisted methods check the permission on the file and the access of the sign setting. The dialogs show only the sign settings that the user can use.

## Signature policy

The old field **Allow Add Others Signs** did not change the signature. pyHanko ignores the `doc_mdp_update_value` of a new field without a field lock. The new field **Signature Type** makes an approval or a certification signature with `certify` and `docmdp_permissions` of pyHanko. A patch sets the type from the old field: on gives Approval, off gives Certification: No Changes.

After a certification that allows form filling, a new visible signature field breaks the certification, because it changes the annotations of the page. Tests with pyHanko 0.38 showed that an invisible new field and an empty field that the PDF already has keep the certification valid. For this reason the app uses an empty field first, and makes a new field invisible after this type of certification.

## Appearance

The box uses millimeters and positions that depend on the size of the page. The old JSON field with points needed the size of the page, and it did not work for every paper size. A patch moves the old values to the new fields and keeps the look of the old signatures: a Custom position with the same box, the same page, the same style, the old text and date format, and the old borders.

pyHanko 0.38 has `text_color` and `border_color`. The app uses them for the text and the border.

Frappe draws the signature in the Signature field with the color of the desk theme, and stores it as a PNG with a transparent background. The app uses the transparency of the PNG and paints the lines in **Handwritten Signature Color**, so that the color in the PDF does not depend on the theme of the user.

The standard PDF font of pyHanko uses the WinAnsi encoding. It shows the letters of Spanish, but not other characters. A TTF or OTF font is optional, so that the app does not include a font file.

## PAdES, time stamps and long-term validation

pyHanko uses the subfilter `adbe.pkcs7.detached` if the app does not give one. The earlier versions made these signatures, although the sign setting said PAdES. The app now gives the subfilter `ETSI.CAdES.detached`, which PAdES needs.

A time stamp comes from a TSA, not from the CA of the certificate. The verification validates the time stamps against the TSA Root Certificate of the sign setting. The app does not use the trust list of the operating system, because pyhanko-certvalidator marks it as deprecated, and because an explicit root shows which TSA the user trusts.

Long-term validation uses `embed_validation_info` and `use_pades_lta` of pyHanko, with a validation context that trusts the CA root of the container and the TSA root, and that can get OCSP and CRL data. The verification validates a document time stamp with `validate_pdf_timestamp`, because it is not a signature.

## Preview

The preview uses the same code as the signature to calculate the box and the style, and draws the box with the stamps of pyHanko on a blank A4 page. It does not need the certificate, and it does not save the form.

## JavaScript bundle

`pdf_signer.bundle.js` imports `utils.js`, and `app_include_js` loads the bundle in every page of the desk. The sign dialog after an upload works in every document for this reason. A bundle does not make global functions, so `utils.js` puts its functions in the `pdf_signer` namespace (`pdf_signer.sign_pdf_dialog` and `pdf_signer.sign_setting_field`). `file.js` uses them, and does not load `utils.js` a second time.

After a change in `utils.js`, run `bench build --app pdf_signer`. `bench migrate` does not build the bundle, and the browser keeps the old bundle until the build.

## Translations

All the texts of the app are in English, and `pdf_signer/locale/es.po` has their translation to Spanish of Spain (es-ES), with usted. The default text of the signature box is in English, because a field default cannot be translated. The user changes the text in the sign setting.

## Known limits

- The app does not use the rotation of a page (`/Rotate`) to calculate the position of the box.
- The DocType **PDF Signer Documents Signed** does not get records.
- The preview always uses an A4 page, and your user name in place of the name of the certificate holder.
