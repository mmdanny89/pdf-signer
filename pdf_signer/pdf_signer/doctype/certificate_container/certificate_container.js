// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt
let template_ca = '<div class="card border-info mb-3">'+
'<div class="card-header"><strong>Important...</strong></div>'+
'<div class="card-body text-info">'+
  '<h5 class="card-title text-info">CA Root is Chain:</h5>'+
  '<p class="card-text">Some quick example text to build on the card title and make up the bulk of the card content.</p>'+
  '<h5 class="card-title text-info">Allowed extensions and formats:</h5>'+
  '<p class="card-text">Some quick example text to build on the card title and make up the bulk of the card content.</p>'+
'</div>'+
'</div>';

let template_cert = '<div class="card border-info mb-3">'+
'<div class="card-header"><strong>Important...</strong></div>'+
'<div class="card-body text-info">'+
  '<h5 class="card-title">P12/PFX Certificate Files</h5>'+
  '<p class="card-text">Allowed file with extensions: <strong>(.p12, .pfx)</strong>. File contain Certificate and Key. File will be protected with password.</p>'+
  '<h5 class="card-title">Ceritifcate File</h5>'+
  '<p class="card-text">Allowed certificate files with extensions and format: <strong>.cer with format DER</strong> and <strong>.crt with format PEM</strong>.</p>'+
  '<h5 class="card-title">Key File</h5>'+
  '<p class="card-text">Allowed key files with extensions: <strong>.pem, .crt, .key</strong>. Key file will be protected with password</p>'+
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
				frm.add_custom_button(__('View Certificate Info'), function(){

				}).removeClass('btn-default').addClass("btn-info");
			}
		}
	},
	is_pfx: function(frm) {
		if (frm.doc.is_pfx) {
			frm.set_value('is_pair', 0);
		} else {
			frm.set_value('is_pair', 1);
		}
	},
	is_pair: function(frm) {
		if (frm.doc.is_pair) {
			frm.set_value('is_pfx', 0);
		} else {
			frm.set_value('is_pfx', 1);
		}	
	},
	
});
