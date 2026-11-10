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
	refresh(frm) {
		if (frm.is_new()) {
			frappe.msgprint({
				title: __("Before you add a certificate"),
				indicator: "blue",
				message: __(
					"Save the container first. After the save, you can attach the certificate and the certificates of the CA."
				),
			});
			return;
		}
		if (!frm.doc.cert_file) return;
		frm.add_custom_button(__("View Certificate Info"), () => show_certificate_info(frm)).each(
			function () {
				frappe.ui.button.dress(this, { label: __("View Certificate Info"), icon: "info" });
			}
		);
		frm.add_custom_button(__("Verify Chain"), () => verify_chain(frm)).each(function () {
			frappe.ui.button.dress(this, { label: __("Verify Chain"), icon: "link" });
		});
	},
});

function show_certificate_info(frm) {
	frappe.call({
		method: "pdf_signer.pdf_signer.doctype.certificate_container.api.cert_details",
		args: { name: frm.docname },
		callback(r) {
			if (r.message.errno !== 0) return;
			const esc = (value) => frappe.utils.escape_html(value || "");
			const rows = [
				["user", __("Name"), r.message.name],
				["flag", __("Country"), r.message.country],
				["map-pin", __("City"), r.message.city],
				["calendar", __("Expiration Date"), r.message.expire],
			];
			frappe.msgprint(
				rows
					.map(
						([icon, label, value]) =>
							`${frappe.utils.icon(icon, "sm")} ${label}: <strong>${esc(
								value
							)}</strong>`
					)
					.join("<br>"),
				__("Certificate Info")
			);
		},
	});
}

function verify_chain(frm) {
	frappe.call({
		method: "pdf_signer.pdf_signer.doctype.certificate_container.api.verify_chain",
		args: { name_container: frm.docname },
		callback(r) {
			const results = {
				0: ["circle-check", __("The chain is correct."), __("Verification Success")],
				1: [
					"triangle-alert",
					__(
						"The CA root is correct, but the chain is not complete. Add the missing intermediate CAs."
					),
					__("Partial Chain"),
				],
			};
			const [icon, message, title] = results[r.message.code] || [
				"circle-x",
				__("The certificate does not come from this CA. Correct the chain."),
				__("Verification Error"),
			];
			frappe.msgprint(
				`<p class="text-center">${frappe.utils.icon(
					icon,
					"sm"
				)} <strong>${message}</strong></p>`,
				title
			);
		},
	});
}
