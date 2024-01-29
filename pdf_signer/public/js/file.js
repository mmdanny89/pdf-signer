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
					frm.reload_doc();
				}).removeClass('btn-default').addClass("btn-dark");

				frm.add_custom_button('<i class="fa fa-check-square"></i> Verify Sign PDF' , function(){
					verify_sign_pdf_dialog(frm.doc.file_name)
				}).removeClass('btn-default').addClass("btn-dark");
			}
		})
	}
}

frappe.ui.form.on('File', {
	refresh: function(frm) {
		customize_pdf_signer(frm);
	}
});


function verify_sign_pdf_dialog(file_reference) {
	let d = new frappe.ui.Dialog({
		title: 'Select Electronic Sign Setting',
		fields: [
			{
				label: 'Setting',
				fieldname: 'sign_field',
				fieldtype: 'Link',
				options: 'Electronic Sign Setting',
				reqd: 1,
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
		primary_action_label: 'Verify Sign',
		primary_action(values) {
			frappe.call({
				method: 'pdf_signer.utils.api.verify_pdf',
				args: {
					file_name: file_reference,
					sign_name: values.sign_field,
				},
				callback: function(r) {
					let fields_ = build_fields(r.message)
					let dialog = new frappe.ui.Dialog({
						title: 'Verification Result',
						fields: fields_,
						primary_action_label: 'Exit',
						size: 'extra-large',
						primary_action(values) {
							dialog.hide();
						}
					});
					dialog.fields.forEach(f => {
						if (f.fieldtype == "HTML") {
							let field_html = dialog.get_field(f.fieldname)
						}
					})
					
					dialog.show();								
				}
			});
			d.hide();
		}
	});
	d.show();
}


function build_fields(response) {
	let fields = [];
	let counter = 0;
	response.forEach(signature => {
		const name_sig = String(signature.signature).split("-")
		fields.push(
			
			{
				label: String(signature.signature),
				fieldname: 'signature_tab'+String(counter),
				fieldtype: 'Section Break'
			},
			{
				label: 'Verification Result',
				fieldname: 'validation_r'+String(counter),
				fieldtype: 'HTML',
				options: build_template_data(name_sig[1], signature.status)
			},
		)
		counter++;
	});
	return fields;
}


function build_template_data(id, data) {
	let id_tab = "list-tab" + "-" + String(id)
	let template = $(`
		<div class="row">
			<div class="col-4">
				<div class="list-group" id="${id_tab}" role="tablist">
					<a class="list-group-item list-group-item-action active" id="list-validation-list" data-target=".validation-${String(id)}" data-toggle="list" href="#list-validation" role="tab" aria-controls="validation">Validation</a>
					<a class="list-group-item list-group-item-action" id="list-modification-list" data-target=".modification-${String(id)}" data-toggle="list" href="#list-modification" role="tab" aria-controls="modification">Modifications</a>
					<a class="list-group-item list-group-item-action" id="list-integrity-list" data-target=".integrity-${String(id)}" data-toggle="list" href="#list-integrity" role="tab" aria-controls="integrity">Integrity</a>
					<a class="list-group-item list-group-item-action" id="list-time-list" data-target=".time-${String(id)}" data-toggle="list" href="#list-time" role="tab" aria-controls="time">Signing Time</a>
					<a class="list-group-item list-group-item-action" id="list-signer-list" data-target=".signer-${String(id)}" data-toggle="list" href="#list-signer" role="tab" aria-controls="signer">Signer Info</a>
				</div>
			</div>
			<div class="col-8">
				<div class="tab-content" id="nav-tabContent">
					<div class="tab-pane fade show active validation-${String(id)}" id="list-validation" role="tabpanel" aria-labelledby="list-validation-list">${data.bottom}</div>
					<div class="tab-pane fade modification-${String(id)}" id="list-modification" role="tabpanel" aria-labelledby="list-modification-list">${data.modification}</div>
					<div class="tab-pane fade integrity-${String(id)}" id="list-integrity" role="tabpanel" aria-labelledby="list-integrity-list">${data.integrity}</div>
					<div class="tab-pane fade time-${String(id)}" id="list-time" role="tabpanel" aria-labelledby="list-time-list">${data.time}</div>
					<div class="tab-pane fade signer-${String(id)}" id="list-signer" role="tabpanel" aria-labelledby="list-signer-list">
					<strong>Certificate subject:</strong> ${data.info.subject}<br>
						<strong>${data.info.fingerprint[0].name}:</strong> ${data.info.fingerprint[0].value}<br>
						<strong>${data.info.fingerprint[1].name}:</strong> ${data.info.fingerprint[1].value}<br>
						<strong>Trust Anchor:</strong> ${data.info.trust_anchor}<br>
						<strong>${data.info.trust}</strong>
						
					</div>
				</div>
			</div>
	</div>`)
	template.find(`#${id_tab} a`).on('click', function (e) {
		e.preventDefault()
		e.stopPropagation();
		$(this).tab('show')
	  })
	return template;
}