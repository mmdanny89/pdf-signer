// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt

frappe.ui.form.on("Electronic Sign Setting", {
	setup(frm) {
		set_upload_restrictions(frm, "bg_image", [".png", ".jpg", ".jpeg"]);
		set_upload_restrictions(frm, "font_file", [".ttf", ".otf"]);
	},
	refresh(frm) {
		frm.add_custom_button(__("Preview Signature Box"), () => preview_box(frm)).each(
			function () {
				frappe.ui.button.dress(this, { label: __("Preview Signature Box"), icon: "eye" });
			}
		);
		if (frm.is_new()) return;
		const enabled = frm.doc.status === "Enable";
		frm.add_custom_button(
			enabled ? __("Disable Sign Setting") : __("Enable Sign Setting"),
			() => set_status(frm, enabled ? "Disabled" : "Enable")
		).each(function () {
			frappe.ui.button.dress(this, {
				label: enabled ? __("Disable Sign Setting") : __("Enable Sign Setting"),
				variant: enabled ? "subtle" : "solid",
				theme: enabled ? "red" : "gray",
				icon: enabled ? "circle-x" : "power",
			});
		});
	},
});

function set_status(frm, status) {
	frappe.db.set_value(frm.doctype, frm.docname, "status", status).then(() => {
		frm.reload_doc();
		frappe.show_alert(
			{
				message:
					status === "Enable"
						? __("The sign setting is enabled.")
						: __("The sign setting is disabled."),
				indicator: status === "Enable" ? "green" : "orange",
			},
			4
		);
	});
}

function set_upload_restrictions(frm, fieldname, extensions) {
	frm.set_df_property(fieldname, "options", {
		restrictions: { allowed_file_types: extensions, max_number_of_files: 1 },
	});
}

// Show the signature box of the values of the form on a blank A4 page. Nothing is saved.
function preview_box(frm) {
	frappe.call({
		method: "pdf_signer.pdf_signer.doctype.electronic_sign_setting.electronic_sign_setting.preview",
		args: { doc: frm.doc },
		freeze: true,
		freeze_message: __("Making the preview..."),
		callback(r) {
			const bytes = Uint8Array.from(atob(r.message), (c) => c.charCodeAt(0));
			const url = URL.createObjectURL(new Blob([bytes], { type: "application/pdf" }));
			const dialog = new frappe.ui.Dialog({
				title: __("Preview Signature Box"),
				size: "extra-large",
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "preview",
						options: `<p class="text-muted">${__(
							"A blank A4 page with the signature box. The preview shows your user name in place of the name of the certificate holder."
						)}</p><iframe src="${url}#view=FitH" style="width: 100%; height: 70vh; border: 0;"></iframe>`,
					},
				],
			});
			dialog.onhide = () => URL.revokeObjectURL(url);
			dialog.show();
		},
	});
}
