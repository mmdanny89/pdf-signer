// MIT 2022, Ing. Danny Molina Morales
// For license information, please see license.txt


frappe.require([
    '/assets/pdf_signer/js/utils.js',
]);

let customize_pdf_signer = function(frm) {
	if (!frm.doc.__islocal) {
		frappe.call('pdf_signer.utils.api.check_pdf', {
			file_name: frm.doc.file_name,
			is_private: frm.doc.is_private
		}).then(r => {
			if (r.message.success) {
				frm.add_custom_button('<i class="fa fa-pencil-square"></i> Sign PDF' , function(){
					sign_pdf_dialog(frm.docname);
				}).removeClass('btn-default').addClass("btn-warning");

				frm.add_custom_button('<i class="fa fa-check-square"></i> Verify Sign PDF' , function(){

				}).removeClass('btn-default').addClass("btn-warning");
			}
		})
	}
}

frappe.ui.form.on('File', {
	refresh: function(frm) {
		customize_pdf_signer(frm);
	}
});
