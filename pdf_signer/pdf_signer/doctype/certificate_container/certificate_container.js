// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt
let template_ca = '<div class="card border-info mb-3">'+
'<div class="card-header text-info"><strong>Important...</strong></div>'+
'<div class="card-body text-info">'+
  '<h5 class="card-title text-info">Allowed extensions and formats:</h5>'+
  '<p class="card-text">Only allowed .cer extensions with DER format.</p>'+
'</div>'+
'</div>';

let template_cert = '<div class="card border-info mb-3">'+
'<div class="card-header text-info"><strong>Important...</strong></div>'+
'<div class="card-body text-info">'+
  '<h5 class="card-title">P12/PFX Certificate Files</h5>'+
  '<p class="card-text">Allowed file with extensions: <strong>(.p12, .pfx)</strong>. File contain Certificate and Key. File will be protected with password.</p>'+
'</div>'+
'</div>';

const BEFORE_MESSAGE_TITLE = String(__('Before work with Certificate Containers:'));
const BEFORE_MESSAGE_FIRST = String(__('Before storing your certificate you must create a container to store it.'));

let welcome_certs = function(frm) {
	if (frm.doc.__islocal) {
		frappe.msgprint({
			title: BEFORE_MESSAGE_TITLE,
			indicator: 'blue',
			message: '<i class="text-primary fa fa-angle-double-right"></i> ' + BEFORE_MESSAGE_FIRST + '<br>',
		});
	}
}

frappe.ui.form.on('Certificate Container', {
	onload: function(frm) {
		frm.set_df_property('html_info_certs', 'options', template_cert);
		frm.set_df_property('html_info_ca', 'options', template_ca);
	},
	refresh: function(frm) {
		welcome_certs(frm);
		if (!frm.doc.__islocal) {
			if (frm.doc.cert_file) {
				frm.add_custom_button(__("View Certificate Info"), function(){
					frappe.call({
						method: "pdf_signer.pdf_signer.doctype.certificate_container.api.cert_details",
						args: {
							name: frm.docname,
						},
						callback: function(r) {
							if (r.message.errno === 0) {
								frappe.msgprint(
									'<i class="text-primary fa fa-user"></i> Name: <strong>'+r.message.name+'</strong><br>'+
									'<i class="text-primary fa fa-flag"></i> Country: <strong>'+r.message.country+'</strong><br>'+
									'<i class="text-primary fa fa-home"></i> City: <strong>'+r.message.city+'</strong><br>'+
									'<i class="text-primary fa fa-calendar"></i> Expiration Date: <strong>'+r.message.expire+'</strong>',
									__("Cerificate Info")
								);
							} 
						}
					});
				}).removeClass('btn-default').addClass("btn-info");
				frm.add_custom_button(__("Verify Chain"), function(){
					frappe.call({
						method: "pdf_signer.pdf_signer.doctype.certificate_container.api.verify_chain",
						args: {
							name_container: frm.docname,
						},
						callback: function(r) {
							if (r.message.code == 0) {
								frappe.msgprint(
									'<p class="text-center"><i class="text-success fa fa-check"></i> <strong>This chain match!</strong></p>',
									__("Verification Success")
								);

							} else if (r.message.code == 1) {
								frappe.msgprint(
									'<p class="text-center"><i class="text-warning fa fa-warning"></i> <strong>This chain match partial!. Verify chain.</strong></p>',
									__("Verification Success")
								);
							} else {
								frappe.msgprint(
									'<p class="text-center"><i class="text-danger fa fa-times"></i> <strong>This chain not match!. Fix chain.</strong></p>',
									__("Verification Error")
								);
							}
						}
					});
				}).removeClass('btn-default').addClass("btn-info");
			}
		}
	},
});
