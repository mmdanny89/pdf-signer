// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt


let customize_fileds = function(frm) {
	frm.$wrapper.find('div.ace-editor-target').css("height", "70px");
	frm.$wrapper.find('div[data-fieldname="postition"]').find('button').hide();
}


frappe.ui.form.on('Electronic Sign Setting', {
	onload_post_render: function(frm){
		customize_fileds(frm);
		if (frm.doc.use_own_sign_bg_image || frm.doc.use_bg_image) {
			frm.set_df_property('use_qr_style', 'read_only', 1);
			frm.refresh_field('use_qr_style')
		}
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
			frm.set_df_property('use_qr_style', 'read_only', 1);
		} else {
			if (frm.doc.use_own_sign_bg_image == 0) {
				frm.set_df_property('use_qr_style', 'read_only', 0);
			}
		}
	},
	use_own_sign_bg_image: function(frm) {
		if (frm.doc.use_own_sign_bg_image) {
			frm.set_value('use_bg_image', 0);
			frm.set_df_property('use_qr_style', 'read_only', 1);
		} else {
			if (frm.doc.use_bg_image == 0) {
				frm.set_df_property('use_qr_style', 'read_only', 0);
			}
		}
	},
	use_qr_style: function(frm) {
		if (frm.doc.use_qr_style) {
			frm.set_df_property('use_bg_image', 'read_only', 1);
			frm.set_df_property('use_own_sign_bg_image', 'read_only', 1);
		} else {
			frm.set_df_property('use_bg_image', 'read_only', 0);
			frm.set_df_property('use_own_sign_bg_image', 'read_only', 0);
		}
	}
});


function customize_image(frm) {
	frm.get_field('bg_image').df.options = {
		restrictions: {
			allowed_file_types: ['png'],
			max_number_of_files: 1,
			crop_image_aspect_ratio: 4/3,
		},
		
	};
}