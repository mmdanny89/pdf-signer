frappe.listview_settings['Electronic Sign Setting'] = {
    hide_name_column: true,
    get_indicator: function (doc) {
      if (doc.status === "Enable") {
        return [__("Enable"), "blue", "status,=,Enable"]
      } else if (doc.status === "Disabled") {
        return [__("Disabled"), "red", "status,=,Disabled"]
      }
    },
    onload: function(listview) {
		
    },
    refresh: function(listview) {
		$("div[data-fieldname = name]").hide();
    }
}