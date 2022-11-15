// MIT 2022, Ing. Danny Molina Morales
// For license information, please see license.txt

frappe.ui.form.on('File', {
	refresh: function(frm) {
		console.log('desde el formulario');
	}
});

frappe.realtime.on('ask_to_sign', (message) => {
	console.log('************************');
});