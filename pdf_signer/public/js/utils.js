// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt


let visted = [];
let current_ = [];


$(document).ready(function(){
	frappe.realtime.on("ask_to_sign",function (file_reference) {
		sign_pdf_dialog(file_reference.docname);	
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
			frappe.call({
				method: 'pdf_signer.utils.api.sign_pdf',
				args: {
					file_name: file_reference,
					sign_name: values.sign_field,
				},
				callback: function(r) {
					if (r.message.success === true) {
						frappe.show_alert({
							message:__('Hi, you have a new message'),
							indicator:'green'
						}, 5);
					} else {
						frappe.show_alert({
							message:__('Hi, you have a new message'),
							indicator:'red'
						}, 5);
					}											
				}
			});
			d.hide();
		}
	});
	d.show();
}