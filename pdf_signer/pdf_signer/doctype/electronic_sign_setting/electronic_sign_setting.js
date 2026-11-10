// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt

frappe.ui.form.on("Electronic Sign Setting", {
	setup(frm) {
		set_upload_restrictions(frm, "bg_image", [".png", ".jpg", ".jpeg"]);
		set_upload_restrictions(frm, "font_file", [".ttf", ".otf"]);
	},
	refresh(frm) {
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
