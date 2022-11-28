// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt


let visted = [];
let current_ = [];


$(document).ready(function(){
	frappe.db.get_single_value('Global Settings PDF Signer', 'always_ask')
	.then(r => {
		if (r === 1) {
			always_ask_when_pdf_uploaded();
		}
	});
});


const OBSERVER = new MutationObserver(function (mutations) {
	for (const mutation of mutations) {
		if (mutation.type === 'attributes') {
			if (mutation.attributeName === 'data-route') {
				current_ = mutation.target.dataset.route.split('/');
				break;
			}		
		  }
	}
	if (current_) {
		if (current_[0] === 'Form') {
			const isFound = visted.some(element => {
				if (String(element) === String(current_[1])) {
					return true;
				}
				return false;
			});
			if(isFound === false) {
				
				frappe.ui.form.on(current_[1], {
					onload: function(frm) {
						frappe.realtime.on("ask_to_sign",function (file_reference) {
							sign_pdf_dialog(file_reference.docname);	
						});
					},
				});
				visted.push(String(current_[1]));
			}
		}
	}
});
  

const CONFIG  = {
    childList: true, 
    subtree: true,
	attributes: true
};


function always_ask_when_pdf_uploaded() {
	OBSERVER.observe(document.body, CONFIG);
}


function disble_ask() {
	OBSERVER.disconnect();
}


function sign_pdf_dialog(file_reference) {
	let d = new frappe.ui.Dialog({
		title: 'Select a Sign Profile',
		fields: [
			{
				label: 'Sign',
				fieldname: 'sign_field',
				fieldtype: 'Link',
				options: 'Electronic Sign Setting',
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