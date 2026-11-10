# Development

## Structure

| Path | Content |
|---|---|
| `pyproject.toml` | Package data (flit), Python dependencies, apt dependencies and the settings of ruff |
| `pdf_signer/hooks.py` | Hooks of the app, made from the hooks template of Frappe 16 |
| `pdf_signer/custom_events/doc_events.py` | The hooks of File: file checks and the sign request |
| `pdf_signer/utils/api.py` | Whitelisted methods to check, sign and verify a PDF |
| `pdf_signer/utils/sign.py` | Signature, signature policy and validation with pyHanko |
| `pdf_signer/utils/appearance.py` | Signature box: page, position, style, QR code, colors and font |
| `pdf_signer/utils/certificate.py` | Data of the certificate of a container and the state of its chain, for the form of the container |
| `pdf_signer/utils/permission.py` | Access of the sign settings, the query of the dialogs and the permission of the apps screen |
| `pdf_signer/patches/v16_0/` | Patches that move the old fields of the sign settings to the new fields |
| `pdf_signer/public/js/file.js` | Buttons and dialogs of the File form |
| `pdf_signer/public/js/pdf_signer.bundle.js` | Bundle of every desk page. It imports `utils.js`. |
| `pdf_signer/public/js/utils.js` | Sign dialog, the field of the sign settings and the realtime event, in the `pdf_signer` namespace |

## Pre-commit and linters

The app uses the pre-commit configuration of a new Frappe 16 app:

- pre-commit-hooks: trailing whitespace, merge conflicts, Python AST, JSON, TOML, YAML and debug statements.
- ruff: import sorter, linter and formatter. The settings are in `[tool.ruff]` of `pyproject.toml`: tabs, double quotes, line length 110 and Python 3.14.
- prettier and eslint for the JavaScript. eslint uses the `.eslintrc` of Frappe.

Enable the hooks one time:

```bash
cd apps/pdf_signer
pre-commit install
```

Check all the files:

```bash
pre-commit run --all-files
```

The ruff linter hook does not fix the code. To fix the findings that ruff can fix, run `ruff check --fix .` with the ruff version of the hook.

The shared JavaScript functions are in the `pdf_signer` namespace of `utils.js`. `.eslintrc` declares `pdf_signer` in `globals`. After a change in `utils.js`, run `bench build --app pdf_signer`.

## Translations

The texts of the app are in English. `pdf_signer/locale/es.po` has the translation to Spanish of Spain (es-ES).

After you add or change a text in `_()`, `__()` or a DocType:

```bash
bench generate-pot-file --app pdf_signer
bench update-po-files --app pdf_signer --locale es
```

Then translate the new entries in `es.po`. Keep the placeholders, for example `{0}` and `%(signer)s`, as they are. Compile the file to test it:

```bash
bench compile-po-to-mo --app pdf_signer --locale es
```

## Tests

```bash
bench --site example.local set-config allow_tests true
bench --site example.local run-tests --app pdf_signer
```

The test classes use `IntegrationTestCase`. They do not have tests yet.

## Versions

| Branch | Frappe | Python |
|---|---|---|
| `main` | 14 | 3.10 |
| `version-15` | 15 | 3.10 |
| `version-16` | 16 | 3.14 |
