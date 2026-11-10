// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt
let template_ca =
	'<div class="card mb-3">' +
	'<div class="card-header "><strong>Important...</strong></div>' +
	'<div class="card-body ">' +
	'<h5 class="card-title ">Allowed extensions and formats:</h5>' +
	'<p class="card-text">Only allowed .cer extensions with DER format.</p>' +
	"</div>" +
	"</div>";

let template_cert =
	'<div class="card mb-3">' +
	'<div class="card-header "><strong>Important...</strong></div>' +
	'<div class="card-body ">' +
	'<h5 class="card-title">P12/PFX Certificate Files</h5>' +
	'<p class="card-text">Allowed file with extensions: <strong>(.p12, .pfx)</strong>. File contain Certificate and Key. File will be protected with password.</p>' +
	"</div>" +
	"</div>";

const BEFORE_MESSAGE_TITLE = String(__("Before work with Certificate Containers:"));
const BEFORE_MESSAGE_FIRST = String(
	__("Before storing your certificate you must create a container to store it.")
);

let welcome_certs = function (frm) {
	if (frm.doc.__islocal) {
		frappe.msgprint({
			title: BEFORE_MESSAGE_TITLE,
			indicator: "blue",
			message:
				frappe.utils.icon("chevrons-right", "sm") + " " + BEFORE_MESSAGE_FIRST + "<br>",
		});
	}
};

frappe.ui.form.on("Certificate Container", {
	onload: function (frm) {
		frm.set_df_property("html_info_certs", "options", template_cert);
		frm.set_df_property("html_info_ca", "options", template_ca);
	},
	refresh: function (frm) {
		welcome_certs(frm);
		if (!frm.doc.__islocal) {
			if (frm.doc.cert_file) {
				frm.add_custom_button(__("View Certificate Info"), function () {
					frappe.call({
						method: "pdf_signer.pdf_signer.doctype.certificate_container.api.cert_details",
						args: {
							name: frm.docname,
						},
						callback: function (r) {
							if (r.message.errno === 0) {
								frappe.msgprint(
									frappe.utils.icon("user", "sm") +
										" Name: <strong>" +
										r.message.name +
										"</strong><br>" +
										frappe.utils.icon("flag", "sm") +
										" Country: <strong>" +
										r.message.country +
										"</strong><br>" +
										frappe.utils.icon("map-pin", "sm") +
										" City: <strong>" +
										r.message.city +
										"</strong><br>" +
										frappe.utils.icon("calendar", "sm") +
										" Expiration Date: <strong>" +
										r.message.expire +
										"</strong>",
									__("Cerificate Info")
								);
							}
						},
					});
				}).each(function () {
					frappe.ui.button.dress(this, {
						label: __("View Certificate Info"),
						icon: "info",
					});
				});
				frm.add_custom_button(__("Verify Chain"), function () {
					frappe.call({
						method: "pdf_signer.pdf_signer.doctype.certificate_container.api.verify_chain",
						args: {
							name_container: frm.docname,
						},
						callback: function (r) {
							if (r.message.code == 0) {
								frappe.msgprint(
									'<p class="text-center">' +
										frappe.utils.icon("circle-check", "sm") +
										" <strong>This chain match!</strong></p>",
									__("Verification Success")
								);
							} else if (r.message.code == 1) {
								frappe.msgprint(
									'<p class="text-center">' +
										frappe.utils.icon("triangle-alert", "sm") +
										" <strong>This chain match partial!. Verify chain.</strong></p>",
									__("Verification Success")
								);
							} else {
								frappe.msgprint(
									'<p class="text-center">' +
										frappe.utils.icon("circle-x", "sm") +
										" <strong>This chain not match!. Fix chain.</strong></p>",
									__("Verification Error")
								);
							}
						},
					});
				}).each(function () {
					frappe.ui.button.dress(this, { label: __("Verify Chain"), icon: "link" });
				});
			}
		}
	},
});
