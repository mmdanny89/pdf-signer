app_name = "pdf_signer"
app_title = "PDF Signer"
app_publisher = "Danny Molina Morales"
app_description = "Application for signing PDF files"
app_email = "mmdanny89@gmail.com"
app_license = "MIT"

# Apps
# ------------------

# required_apps = []

app_home = "/desk/pdf-signer"

# Each item in the list will be shown as an app in the apps page
# No logo yet: the desk draws a letter icon from the app title.
add_to_apps_screen = [
	{
		"name": app_name,
		"title": app_title,
		"route": app_home,
		"has_permission": "pdf_signer.utils.permission.has_app_permission",
	}
]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `pdf_signer/dock/pdf_signer/pdf_signer.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pdf_signer/css/pdf_signer.css"
app_include_js = ["pdf_signer.bundle.js"]

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
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "pdf_signer/public/icons.svg"

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

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

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

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "pdf_signer.utils.before_app_install"
# after_app_install = "pdf_signer.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "pdf_signer.utils.before_app_uninstall"
# after_app_uninstall = "pdf_signer.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "pdf_signer.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "pdf_signer.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pdf_signer.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["pdf_signer.search.awesomebar_results"]

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"File": {
		"on_update": "pdf_signer.custom_events.doc_events.check_file_uploaded",
		"on_trash": "pdf_signer.custom_events.doc_events.remove_file_signed",
		"before_save": "pdf_signer.custom_events.doc_events.validate_extension",
	}
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

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "pdf_signer.custom.task.CustomTaskMixin"
# }

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

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["pdf_signer.utils.before_request"]
# after_request = ["pdf_signer.utils.after_request"]

# Job Events
# ----------
# before_job = ["pdf_signer.utils.before_job"]
# after_job = ["pdf_signer.utils.after_job"]

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

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
