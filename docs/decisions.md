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

## Roles and access

The app has two roles: PDF Signer Manager configures the app, and PDF Signer User signs and verifies. Each sign setting has its own users and roles. The users win over the roles, because a personal certificate is for its holder only. Without users and roles, only the managers can sign, as in the earlier versions, where only the System Manager could use the app.

The whitelisted methods check the permission on the file and the access of the sign setting. The dialogs show only the sign settings that the user can use.

## Signature policy

The old field **Allow Add Others Signs** did not change the signature. pyHanko ignores the `doc_mdp_update_value` of a new field without a field lock. The new field **Signature Type** makes an approval or a certification signature with `certify` and `docmdp_permissions` of pyHanko. A patch sets the type from the old field: on gives Approval, off gives Certification: No Changes.

After a certification that allows form filling, a new visible signature field breaks the certification, because it changes the annotations of the page. Tests with pyHanko 0.38 showed that an invisible new field and an empty field that the PDF already has keep the certification valid. For this reason the app uses an empty field first, and makes a new field invisible after this type of certification.

## Known limits

- The sign dialog after an upload opens only if the browser has loaded `utils.js`. The File form loads it. The bundle `pdf_signer.bundle.js` is empty.
- The fields **Add QR to Sign**, **Text Font**, **Algorithm** and **Role** do not change the signature.
- The DocType **PDF Signer Documents Signed** does not get records.
