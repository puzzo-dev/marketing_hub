// Copyright (c) 2026, I-Varse Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Social Media Network', {
	refresh: function(frm) {
		// Add custom buttons or actions
		if (frm.doc.is_active) {
			frm.add_custom_button(__('Test Connection'), function() {
				frappe.call({
					method: 'marketing_hub.marketing_hub.doctype.social_media_network.social_media_network.test_network_connection',
					args: {
						network: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__('Connection successful!'));
						}
					}
				});
			});
		}
	}
});
