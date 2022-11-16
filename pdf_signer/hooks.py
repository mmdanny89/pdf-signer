from . import __version__ as app_version

app_name = "pdf_signer"
app_title = "Pdf Signer"
app_publisher = "Danny Molina Morales"
app_description = "Application for signing PDF files"
app_email = "mmdanny89@gmail.com"
app_license = "MIT"
app_version = app_version

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pdf_signer/css/pdf_signer.css"

# include js, css files in header of web template
# web_include_css = "/assets/pdf_signer/css/pdf_signer.css"
# web_include_js = "/assets/pdf_signer/js/pdf_signer.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pdf_signer/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"File": "public/js/file.js"}
doctype_list_js = {"File": "public/js/file_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "pdf_signer.utils.jinja_methods",
# 	"filters": "pdf_signer.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "pdf_signer.install.before_install"
# after_install = "pdf_signer.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "pdf_signer.uninstall.before_uninstall"
# after_uninstall = "pdf_signer.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pdf_signer.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "File": {
        # "on_update": "pdf_signer.custom_events.doc_events.check_file_uploaded",
        "on_trash": "pdf_signer.custom_events.doc_events.remove_file_signed",
    }
    # 	"*": {
    # 		"on_update": "method",
    # 		"on_cancel": "method",
    # 		"on_trash": "method"
    # 	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"pdf_signer.tasks.all"
# 	],
# 	"daily": [
# 		"pdf_signer.tasks.daily"
# 	],
# 	"hourly": [
# 		"pdf_signer.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pdf_signer.tasks.weekly"
# 	],
# 	"monthly": [
# 		"pdf_signer.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "pdf_signer.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pdf_signer.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pdf_signer.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"pdf_signer.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
