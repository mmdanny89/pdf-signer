// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt


let flag_protect = false;



$(document).ready(function(){
	frappe.realtime.on("ask_to_sign",function (file_reference) {
		if (flag_protect == false) {
			sign_pdf_dialog(file_reference.docname);
		}
			
	});
	frappe.realtime.on("unfreeze_signer",function () {
		frappe.dom.unfreeze();
		flag_protect = false
	});
});


function sign_pdf_dialog(file_reference) {
	let d = new frappe.ui.Dialog({
		title: 'Select a Sign Profile',
		fields: [
			{
				label: 'Sign',
				fieldname: 'sign_field',
				fieldtype: 'Link',
				options: 'Electronic Sign Setting',
				get_query: function(){
					return {
						filters: {
							status: 'Enable',
						}
					}
				},
				req:1
			}
		],
		primary_action_label: 'Sign Document',
		primary_action(values) {
			flag_protect = true
			frappe.dom.freeze("Signing Document...");
			frappe.call({
				method: 'pdf_signer.utils.api.sign_pdf',
				args: {
					file_name: file_reference,
					sign_name: values.sign_field,
				},
				callback: function(r) {
					frappe.dom.unfreeze();
					if (r.message.success === true) {
						frappe.show_alert({
							message:__(r.message.msg),
							indicator:'green'
						}, 5);
						flag_protect = false;
					} else {
						frappe.show_alert({
							message:__(r.message.msg),
							indicator:'red'
						}, 5);
						flag_protect = false
					}										
				}
			});
			d.hide();
		}
	});
	d.show();
}