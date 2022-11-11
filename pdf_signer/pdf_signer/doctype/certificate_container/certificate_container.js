// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt

frappe.ui.form.on('Certificate Container', {
	onload: function(frm) {
		
	},
	refresh: function(frm) {
		
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
			
	}
});
