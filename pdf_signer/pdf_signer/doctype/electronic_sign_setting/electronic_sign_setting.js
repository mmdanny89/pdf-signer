// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt

let customize_fileds = function(frm) {
	frappe.after_ajax(function () {
		frm.$wrapper.find('div[data-fieldname="postition"]').find('.ace-editor-target.border.rounded.ace_editor.ace_hidpi.ace-tomorrow').attr('style', 'height: 70px');
		frm.$wrapper.find('div[data-fieldname="postition"]').find('button').hide();
	});
		
}

frappe.ui.form.on('Electronic Sign Setting', {
	onload_post_render: function(frm){
		customize_fileds(frm);
	},
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			if (frm.doc.status === 'Enable') {
				frm.add_custom_button(__('Disabled Electronic Sign'), function(){
					frappe.db.set_value('Electronic Sign Setting', frm.docname, 'status', 'Disabled')
					.then(r => {
						frm.reload_doc();
						frappe.show_alert({
							message:__('Sign Setting is disabled'),
							indicator:'green'
						}, 4);
					});
				}).removeClass('btn-default').addClass("btn-danger");;

			} else if (frm.doc.status === 'Disabled') {
				frm.add_custom_button(__('Enable Electronic Sign'), function(){
					frappe.db.set_value('Electronic Sign Setting', frm.docname, 'status', 'Enable')
					.then(r => {
						frm.reload_doc();
						frappe.show_alert({
							message:__('Sign Setting is enable'),
							indicator:'green'
						}, 4);
					});

				}).removeClass('btn-default').addClass("btn-primary");
			}
		}
	}
});
