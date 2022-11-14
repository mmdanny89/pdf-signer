
frappe.listview_settings['Certificate Container'] = {
    hide_name_column: true,
    onload: function(listview) {
    },
    refresh: function(listview) {
		  $("div[data-fieldname = name]").hide();
    }
}