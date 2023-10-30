// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt


let customize_fileds = function(frm) {
	frm.$wrapper.find('div.ace-editor-target').css("height", "70px");
	frm.$wrapper.find('div[data-fieldname="postition"]').find('button').hide();
}


frappe.ui.form.on('Electronic Sign Setting', {
	onload_post_render: function(frm){
		customize_fileds(frm);
	},
	refresh: function(frm) {
		customize_fileds(frm);
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
		customize_image(frm)
		

	},
	use_bg_image: function(frm) {
		if (frm.doc.use_bg_image) {
			frm.set_value('use_own_sign_bg_image', 0);
		}
	},
	use_own_sign_bg_image: function(frm) {
		if (frm.doc.use_own_sign_bg_image) {
			frm.set_value('use_bg_image', 0);
		}
	},
});


function customize_image(frm) {
	frm.get_field('bg_image').df.options = {
		restrictions: {
			allowed_file_types: ['png'],
			crop_image_aspect_ratio:NaN,
		},
		
	};
	console.log(frm.get_field('bg_image').df)
}