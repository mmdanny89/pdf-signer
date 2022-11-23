// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt


let customize_fileds = function(frm) {
	let class_ = "ace-editor-target border rounded ace_editor ace_hidpi ace-tomorrow";
	let mutationObserver = new MutationObserver(function(mutations) {
		mutations.forEach(function(mutation) {
		  if (mutation.type === "attributes" && mutation.attributeName === "class") {
			if (mutation.target.classList.toString() === class_){
				if (String(mutation.target.style.height) === "300px") {
					mutation.target.style.height = "70px";
				}
			}
		  }	
		});
	  });
	mutationObserver.observe(document.body, {
		attributes: true,
		childList: true,
		subtree: true,
	});
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
