// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt

function info_card(title, text) {
	return `<div class="card mb-3">
		<div class="card-header"><strong>${__("Important")}</strong></div>
		<div class="card-body">
			<h5 class="card-title">${title}</h5>
			<p class="card-text">${text}</p>
		</div>
	</div>`;
}

frappe.ui.form.on("Certificate Container", {
	onload(frm) {
		frm.set_df_property(
			"html_info_certs",
			"options",
			info_card(
				__("P12 or PFX certificate file"),
				__(
					"Use a private file with the extension .p12 or .pfx. The file contains the certificate and its key. Type its passphrase below, if it has one."
				)
			)
		);
		frm.set_df_property(
			"html_info_ca",
			"options",
			info_card(
				__("Certificates of the certificate authority"),
				__(
					"Use private files with the extension .cer (DER format) or .crt (PEM format). The CA root is necessary to verify signatures."
				)
			)
		);
	},
	async refresh(frm) {
		frm.set_intro("");
		if (frm.is_new()) {
			frm.set_intro(
				__(
					"Save the container first. After the save, you can attach the certificate and the certificates of the CA."
				),
				"blue"
			);
			return;
		}
		const r = await frappe.call({
			method: "pdf_signer.utils.certificate.certificate_summary",
			args: { name: frm.docname },
		});
		const info = r.message || {};
		const chain = info.chain || {};
		const header = info.success
			? { valid: "green", no_ca: "orange", invalid: "red" }[chain.state]
			: "red";
		frm.set_intro("");
		frm.set_intro(frappe.utils.escape_html(info.success ? chain.message : info.error), header);
		frm.set_df_property("cert_info", "options", certificate_html(info));
	},
});

const CERT_VALIDITY = {
	valid: { label: __("Valid"), theme: "green", icon: "badge-check" },
	expiring: { label: __("Expires soon"), theme: "orange", icon: "clock-alert" },
	expired: { label: __("Expired"), theme: "red", icon: "badge-x" },
	not_yet_valid: { label: __("Not valid yet"), theme: "orange", icon: "clock" },
};

const CHAIN_STATES = {
	valid: { label: __("Valid chain"), theme: "green", icon: "circle-check" },
	no_ca: { label: __("Not checked"), theme: "orange", icon: "triangle-alert" },
	invalid: { label: __("Invalid chain"), theme: "red", icon: "circle-x" },
};

function cert_row(label, value, mono = false) {
	if (!value) return "";
	return `<div class="ps-cert-row">
		<div class="ps-cert-label">${frappe.utils.escape_html(label)}</div>
		<div class="ps-cert-value ${mono ? "ps-cert-mono" : ""}">${frappe.utils.escape_html(value)}</div>
	</div>`;
}

function cert_card(icon, title, body, wide = false) {
	return `<div class="ps-cert-card ${wide ? "ps-cert-wide" : ""}">
		<div class="ps-cert-card-title">${frappe.utils.icon(icon, "sm")} ${title}</div>
		${body}
	</div>`;
}

function certificate_html(info) {
	if (!info.success) {
		return `<div class="text-muted text-center p-4">${frappe.utils.icon(
			"triangle-alert",
			"lg"
		)}
			<p class="mt-2 mb-0">${frappe.utils.escape_html(info.error || "")}</p></div>`;
	}
	const e = frappe.utils.escape_html;
	const subject = info.subject;
	const validity = CERT_VALIDITY[info.validity.state] || CERT_VALIDITY.valid;
	const chain = CHAIN_STATES[info.chain.state] || CHAIN_STATES.invalid;
	const days =
		info.validity.days_left >= 0
			? __("{0} days left", [info.validity.days_left])
			: __("Expired {0} days ago", [-info.validity.days_left]);
	const place = [subject.locality, subject.state, subject.country].filter(Boolean).join(", ");

	const holder_card = cert_card(
		"user-round",
		__("Holder"),
		cert_row(__("Name"), subject.common_name) +
			cert_row(__("Organization"), subject.organization) +
			cert_row(__("Unit"), subject.organizational_unit) +
			cert_row(__("Identifier"), subject.serial_number, true) +
			cert_row(__("Place"), place) +
			cert_row(__("Email"), subject.email)
	);
	const issuer_card = cert_card(
		"landmark",
		__("Issuer"),
		cert_row(__("Authority"), info.issuer.common_name) +
			cert_row(__("Organization"), info.issuer.organization) +
			cert_row(__("Valid from"), frappe.datetime.str_to_user(info.validity.not_before)) +
			cert_row(__("Valid until"), frappe.datetime.str_to_user(info.validity.not_after))
	);
	const chain_card = cert_card(
		"link",
		__("Chain of trust"),
		`<div class="mb-2">${frappe.ui.badge.html({
			label: chain.label,
			theme: chain.theme,
		})}</div>
		<div class="small ${info.chain.state === "invalid" ? "text-danger" : "text-muted"}">${e(
			info.chain.message
		)}</div>
		${(info.chain.chain || [])
			.map(
				(name, index) => `<div class="ps-cert-link">${frappe.utils.icon(
					"circle-check",
					"sm"
				)}
					<span>${e(name)}</span> ${frappe.ui.badge.html({
					label: index === 0 ? __("Certificate") : __("CA"),
				})}</div>`
			)
			.join("")}`,
		true
	);
	const id_card = cert_card(
		"fingerprint-pattern",
		__("Identification"),
		cert_row(__("Serial number"), info.serial, true) +
			cert_row(__("SHA-256 fingerprint"), info.sha256, true),
		true
	);

	return `<style>
		.ps-cert .icon { margin: 0; flex: none; }
		.ps-cert-header { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between;
			padding: var(--padding-md, 15px); border: 1px solid var(--border-color); border-radius: var(--border-radius-md, 8px);
			background: var(--card-bg); margin-bottom: 12px; }
		.ps-cert-holder { display: flex; gap: 10px; align-items: center; min-width: 0; }
		.ps-cert-name { font-size: var(--text-lg, 16px); font-weight: 600; overflow-wrap: anywhere; }
		.ps-cert-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
		.ps-cert-card { border: 1px solid var(--border-color); border-radius: var(--border-radius-md, 8px);
			background: var(--card-bg); padding: var(--padding-md, 15px); min-width: 0; }
		.ps-cert-card-title { display: flex; gap: 6px; align-items: center; font-weight: 600; margin-bottom: 10px; }
		.ps-cert-row { display: grid; grid-template-columns: minmax(100px, 150px) 1fr; gap: 8px; padding: 3px 0; }
		.ps-cert-label { color: var(--text-muted); }
		.ps-cert-value { min-width: 0; overflow-wrap: anywhere; }
		.ps-cert-mono { font-family: var(--font-family-monospace, monospace); font-size: var(--text-xs, 11px); }
		.ps-cert-link { display: flex; gap: 6px; align-items: center; padding: 3px 0; }
		.ps-cert-wide { grid-column: 1 / -1; }
	</style>
	<div class="ps-cert">
		<div class="ps-cert-header">
			<div class="ps-cert-holder">
				${frappe.utils.icon(validity.icon, "lg")}
				<div>
					<div class="ps-cert-name">${e(subject.common_name || subject.dn)}</div>
					<div class="text-muted small">${e(info.issuer.common_name || info.issuer.dn)}</div>
				</div>
			</div>
			<div class="text-right">
				${frappe.ui.badge.html({ label: validity.label, theme: validity.theme })}
				${frappe.ui.badge.html({ label: chain.label, theme: chain.theme })}
				<div class="text-muted small mt-1">${e(days)}</div>
			</div>
		</div>
		<div class="ps-cert-grid">${holder_card}${issuer_card}${chain_card}${id_card}</div>
	</div>`;
}
