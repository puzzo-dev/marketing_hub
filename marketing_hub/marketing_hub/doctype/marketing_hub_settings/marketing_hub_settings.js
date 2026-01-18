// Marketing Hub Settings Client Script

frappe.ui.form.on('Marketing Hub Settings', {
	refresh: function(frm) {
		// Add custom buttons
		if (!frm.is_new()) {
			frm.add_custom_button(__('Test Email Configuration'), function() {
				test_email_config(frm);
			}, __('Actions'));

			frm.add_custom_button(__('Test WhatsApp Integration'), function() {
				test_whatsapp_integration(frm);
			}, __('Actions'));

			frm.add_custom_button(__('Sync Analytics Now'), function() {
				sync_analytics_now(frm);
			}, __('Actions'));
		}

		// Show/hide sections based on settings
		toggle_agency_fields(frm);
	},

	agency_mode: function(frm) {
		toggle_agency_fields(frm);
	},

	enable_google_ads: function(frm) {
		if (frm.doc.enable_google_ads) {
			show_oauth_setup_message(frm, 'Google Ads');
		}
	},

	enable_meta_ads: function(frm) {
		if (frm.doc.enable_meta_ads) {
			show_oauth_setup_message(frm, 'Meta Ads');
		}
	},

	enable_linkedin_ads: function(frm) {
		if (frm.doc.enable_linkedin_ads) {
			show_oauth_setup_message(frm, 'LinkedIn Ads');
		}
	},

	enable_whatsapp_blast: function(frm) {
		if (frm.doc.enable_whatsapp_blast) {
			frappe.msgprint({
				title: __('WhatsApp Integration Required'),
				message: __('Please ensure frappe_whatsapp app is installed and configured before enabling WhatsApp Blast.'),
				indicator: 'orange'
			});
		}
	},

	enable_sms_blast: function(frm) {
		if (frm.doc.enable_sms_blast) {
			frappe.msgprint({
				title: __('SMS Gateway Required'),
				message: __('Please configure an SMS gateway integration before enabling SMS Blast.'),
				indicator: 'orange'
			});
		}
	}
});

function toggle_agency_fields(frm) {
	if (frm.doc.agency_mode) {
		frm.set_df_property('agency_settings_section', 'hidden', 0);
	} else {
		frm.set_df_property('agency_settings_section', 'hidden', 1);
	}
}

function show_oauth_setup_message(frm, platform) {
	frappe.msgprint({
		title: __('{0} OAuth Setup', [platform]),
		message: __('Please configure OAuth credentials in Social Login Key or Ad Account for {0} integration.', [platform]),
		indicator: 'blue'
	});
}

function test_email_config(frm) {
	frappe.call({
		method: 'frappe.email.doctype.email_account.email_account.test_email_connection',
		args: {
			email_account: frm.doc.default_email_sender
		},
		callback: function(r) {
			if (r.message) {
				frappe.msgprint({
					title: __('Email Test Successful'),
					message: __('Email configuration is working correctly'),
					indicator: 'green'
				});
			} else {
				frappe.msgprint({
					title: __('Email Test Failed'),
					message: __('Please check your email configuration'),
					indicator: 'red'
				});
			}
		}
	});
}

function test_whatsapp_integration(frm) {
	if (!frm.doc.enable_whatsapp_blast) {
		frappe.msgprint(__('WhatsApp Blast is not enabled'));
		return;
	}

	frappe.call({
		method: 'frappe.client.get_value',
		args: {
			doctype: 'WhatsApp Settings',
			fieldname: 'default_outgoing_account',
			filters: {}
		},
		callback: function(r) {
			if (r.message && r.message.default_outgoing_account) {
				frappe.msgprint({
					title: __('WhatsApp Integration Active'),
					message: __('Default WhatsApp account is configured: {0}', [r.message.default_outgoing_account]),
					indicator: 'green'
				});
			} else {
				frappe.msgprint({
					title: __('WhatsApp Not Configured'),
					message: __('Please configure WhatsApp Settings first'),
					indicator: 'orange'
				});
			}
		}
	});
}

function sync_analytics_now(frm) {
	if (!frm.doc.enable_analytics_sync) {
		frappe.msgprint(__('Analytics Sync is not enabled'));
		return;
	}

	frappe.call({
		method: 'marketing_hub.utils.analytics_sync.sync_all_connectors',
		callback: function(r) {
			frappe.msgprint({
				title: __('Analytics Sync Triggered'),
				message: __('Analytics sync is running in the background. Check Analytics Daily Log for results.'),
				indicator: 'blue'
			});
		}
	});
}
