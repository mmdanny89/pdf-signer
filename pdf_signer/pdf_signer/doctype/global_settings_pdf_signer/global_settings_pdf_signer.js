// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt

frappe.require([
    '/assets/pdf_signer/js/utils.js',
]);

frappe.ui.form.on('Global Settings PDF Signer', {
	refresh: function(frm) {

	},
	always_ask: function(frm) {
	}, 
	after_save: function(frm) {
		if (frm.doc.always_ask) {
			console.log('is called');
			always_ask_when_pdf_uploaded();
		} else {
			disble_ask();
		}
	}
});
