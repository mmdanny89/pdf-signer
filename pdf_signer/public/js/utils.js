// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt

let flag_protect = false;

$(document).ready(function () {
	frappe.realtime.on("ask_to_sign", function (file_reference) {
		if (flag_protect == false) {
			sign_pdf_dialog(file_reference.docname);
		}
	});
});

// The Link field of the sign and verify dialogs: only the enabled settings that the user can use.
function sign_setting_field(purpose) {
	return {
		label: __("Sign Setting"),
		fieldname: "sign_setting",
		fieldtype: "Link",
		options: "Electronic Sign Setting",
		reqd: 1,
		get_query: () => ({
			query: "pdf_signer.utils.permission.sign_setting_query",
			filters: { purpose: purpose },
		}),
	};
}

function sign_pdf_dialog(file_reference, on_signed) {
	let d = new frappe.ui.Dialog({
		title: __("Sign PDF"),
		fields: [sign_setting_field("sign")],
		primary_action_label: __("Sign Document"),
		primary_action(values) {
			flag_protect = true;
			d.hide();
			frappe.dom.freeze(__("Signing the document..."));
			frappe.call({
				method: "pdf_signer.utils.api.sign_pdf",
				args: {
					file: file_reference,
					sign_setting: values.sign_setting,
				},
				always: () => {
					frappe.dom.unfreeze();
					flag_protect = false;
				},
				callback: function (r) {
					frappe.show_alert({ message: r.message.msg, indicator: "green" }, 5);
					on_signed && on_signed();
				},
			});
		},
	});
	d.show();
}
