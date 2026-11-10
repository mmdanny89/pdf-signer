# Development

## Structure

| Path | Content |
|---|---|
| `pyproject.toml` | Package data (flit), Python dependencies, apt dependencies and the settings of ruff |
| `pdf_signer/hooks.py` | Hooks of the app, made from the hooks template of Frappe 16 |
| `pdf_signer/custom_events/doc_events.py` | The hooks of File: file checks and the sign request |
| `pdf_signer/utils/api.py` | Whitelisted methods to check, sign and verify a PDF |
| `pdf_signer/utils/sign.py` | Signature and validation with pyHanko |
| `pdf_signer/utils/openssl.py` | Certificate load, chain check and certificate details |
| `pdf_signer/utils/openssl_doctype_tools.py` | Error messages of the chain check and of the certificate details |
| `pdf_signer/utils/permission.py` | Permission check of the apps screen |
| `pdf_signer/public/js/file.js` | Buttons and dialogs of the File form |
| `pdf_signer/public/js/utils.js` | Sign dialog and realtime events |

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

If a JavaScript file uses a function of another file of the app, declare the function in `globals` of `.eslintrc`. For example, `file.js` uses `sign_pdf_dialog` of `utils.js`.

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
