# Desk

## Where the app shows

| Place | What shows | Source |
|---|---|---|
| Apps screen | PDF Signer with the app logo | `add_to_apps_screen` and `app_logo_url` in `hooks.py` |
| Desktop | The PDF Signer tile | `pdf_signer/desktop_icon/pdf_signer.json` |
| Dock | The PDF Signer entry | `pdf_signer/dock/pdf_signer/pdf_signer.json` |
| Sidebar | The links of the app | `pdf_signer/pdf_signer/sidebar/pdf_signer/pdf_signer.json` |
| Workspace | The PDF Signer home page | `pdf_signer/pdf_signer/workspace/pdf_signer/pdf_signer.json` |

The apps screen shows PDF Signer only to desk users who can read Electronic Sign Setting. The check is `pdf_signer.utils.permission.has_app_permission`.

Frappe imports the desktop icon only on a site that uses the desktop grid. A site that uses the apps screen does not keep Desktop Icon records.

## Sidebar

| Section | Link | Opens |
|---|---|---|
| | Home | The PDF Signer workspace |
| Signing | PDF Files | The File list with the filter File Type = PDF |
| Signing | Electronic Sign Setting | The list of sign settings |
| Certificates | Certificate Container | The list of certificate containers |
| Settings | Global Settings PDF Signer | The global settings |

## Icons

All the icons come from the app icon of the README, `images/esign.png`.

| File | Size | Use |
|---|---|---|
| `public/images/pdf-signer-logo.svg` | 512 x 512 | App logo: apps screen and dock header |
| `public/icons/desktop_icons/subtle/pdf_signer.svg` | 54 x 54 | Desktop tile, light variant |
| `public/icons/desktop_icons/solid/pdf_signer.svg` | 54 x 54 | Desktop tile, solid variant |
| `public/icons/module-icons.svg` | 24 x 24 | Soft icon `pdf-signer-soft`: dock entry and sidebar header |

The logo and the desktop tiles are a trace of the PNG. They use the vertical gradient of the PNG, from `#00EAF0` to `#0071F0`.

The soft icon is a drawing on the 24 grid of the soft icons of Frappe. It uses the classes `soft-body`, `soft-layer` and `soft-accent-line`, so it takes the color of the desk theme. `app_include_icons` in `hooks.py` loads the sprite.

The links of the sidebar use Lucide icons of Frappe: `house`, `signature`, `file-text`, `file-pen-line`, `shield-check`, `file-key` and `settings`.

## Change the desk records

1. Make the change in the JSON file.
2. Set `modified` to a later date and time. Frappe imports the file again only if `modified` is later than the record on the site.
3. Run `bench --site example.local migrate`.
4. If you changed a file in `public/`, run `bench build --app pdf_signer`.
