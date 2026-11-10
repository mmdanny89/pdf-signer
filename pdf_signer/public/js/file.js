// MIT 2022, Ing. Danny Molina Morales
// For license information, please see license.txt

frappe.require(["/assets/pdf_signer/js/utils.js"]);

let customize_pdf_signer = function (frm) {
	if (frm.doc.__islocal) return;
	frappe.call("pdf_signer.utils.api.check_pdf", { file: frm.docname }).then((r) => {
		if (!r.message.success) return;
		if (r.message.can_sign) {
			frm.add_custom_button(__("Sign PDF"), function () {
				sign_pdf_dialog(frm.docname, () => frm.reload_doc());
			}).each(function () {
				frappe.ui.button.dress(this, {
					label: __("Sign PDF"),
					variant: "solid",
					icon: "signature",
				});
			});
		}
		if (r.message.can_verify) {
			frm.add_custom_button(__("Verify Signed PDF"), function () {
				verify_sign_pdf_dialog(frm.docname);
			}).each(function () {
				frappe.ui.button.dress(this, {
					label: __("Verify Signed PDF"),
					icon: "badge-check",
				});
			});
		}
	});
};

frappe.ui.form.on("File", {
	refresh: function (frm) {
		customize_pdf_signer(frm);
	},
});

function verify_sign_pdf_dialog(file_reference) {
	let d = new frappe.ui.Dialog({
		title: __("Verify Signed PDF"),
		fields: [sign_setting_field("verify")],
		primary_action_label: __("Verify Signatures"),
		primary_action(values) {
			d.hide();
			frappe.call({
				method: "pdf_signer.utils.api.verify_pdf",
				args: {
					file: file_reference,
					sign_setting: values.sign_setting,
				},
				freeze: true,
				freeze_message: __("Verifying the signatures..."),
				callback: function (r) {
					let dialog = new frappe.ui.Dialog({
						title: __("Verification Result"),
						fields: build_fields(r.message),
						primary_action_label: __("Close"),
						size: "large",
						primary_action() {
							dialog.hide();
						},
					});
					dialog.show();
				},
			});
		},
	});
	d.show();
}

function build_fields(signatures) {
	if (!signatures || !signatures.length) {
		return [
			{
				fieldname: "no_signatures",
				fieldtype: "HTML",
				options: `<p class="text-muted">${__("This PDF does not have signatures.")}</p>`,
			},
		];
	}
	return signatures.flatMap((signature, index) => [
		{
			label: signature.field,
			fieldname: "signature_section_" + index,
			fieldtype: "Section Break",
		},
		{
			fieldname: "signature_result_" + index,
			fieldtype: "HTML",
			options: signature_result_html(signature),
		},
	]);
}

const COVERAGE_LABELS = {
	ENTIRE_FILE: __("The signature covers the entire file."),
	ENTIRE_REVISION: __("The signature covers its revision. The file has later revisions."),
	CONTIGUOUS_BLOCK_FROM_START: __("The signature covers only a part of the file."),
	UNCLEAR: __("The coverage of the signature is not clear."),
};

const MODIFICATION_LABELS = {
	NONE: __("No changes after the signature."),
	LTA_UPDATES: __("Only validation data and time stamps were added after the signature."),
	FORM_FILLING: __("Only form filling and new signatures after the signature."),
	ANNOTATIONS: __("Form filling, new signatures and comments after the signature."),
	OTHER: __("Other changes after the signature."),
};

const CERTIFICATION_LABELS = {
	NO_CHANGES: __("Certification: no changes allowed"),
	FILL_FORMS: __("Certification: form filling and signing allowed"),
	ANNOTATE: __("Certification: form filling, signing and comments allowed"),
};

function signature_result_html(signature) {
	const yes_no = (value, yes, no) =>
		value
			? `<span class="indicator-pill green">${yes}</span>`
			: `<span class="indicator-pill red">${no}</span>`;
	const esc = (value) => frappe.utils.escape_html(value || "");
	const rows = [
		[
			__("Result"),
			yes_no(
				signature.valid,
				__("The signature is valid"),
				__("The signature is not valid")
			),
		],
		[__("Integrity"), yes_no(signature.intact, __("Intact"), __("Changed after signing"))],
		[
			__("Cryptographic check"),
			yes_no(signature.crypto_valid, __("Correct"), __("Not correct")),
		],
		[
			__("Trust"),
			signature.revoked
				? yes_no(false, "", __("Revoked certificate"))
				: yes_no(signature.trusted, __("Trusted"), __("Not trusted")),
		],
		[__("Type"), esc(CERTIFICATION_LABELS[signature.certification] || __("Approval"))],
		[__("Coverage"), esc(COVERAGE_LABELS[signature.coverage])],
		[__("Modifications"), esc(MODIFICATION_LABELS[signature.modification_level])],
		[__("Signing time"), esc(signature.signing_time)],
		[__("Time stamp"), esc(signature.timestamp || __("None"))],
		[__("Signer"), esc(signature.signer)],
		[__("Issuer"), esc(signature.issuer)],
		[__("Serial number"), esc(signature.serial_number)],
		[__("Valid until"), esc(signature.valid_until)],
		[__("Trust anchor"), esc(signature.trust_anchor || __("None"))],
		[__("SHA-256 fingerprint"), `<code>${esc(signature.sha256)}</code>`],
	];
	return `<table class="table table-sm">
		${rows
			.map(
				([label, value]) =>
					`<tr><th style="width: 30%">${label}</th><td>${value}</td></tr>`
			)
			.join("")}
	</table>`;
}
