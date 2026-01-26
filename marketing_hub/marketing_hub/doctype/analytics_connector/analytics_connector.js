//Copyright (c) 2026, I-Varse Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Analytics Connector', {
    refresh: function (frm) {
        // Add custom buttons
        if (!frm.is_new()) {
            frm.add_custom_button(__('Sync Now'), function () {
                sync_analytics(frm);
            }, __('Actions'));

            frm.add_custom_button(__('Get Platform Campaigns'), function () {
                get_platform_campaigns(frm);
            }, __('Actions'));
        }

        // Show sync status
        if (frm.doc.sync_status === 'Active') {
            frm.dashboard.set_headline_alert(__('Sync Active'), 'green');
        } else if (frm.doc.sync_status === 'Error') {
            frm.dashboard.set_headline_alert(__('Sync Error'), 'red');
        } else if (frm.doc.sync_status === 'Paused') {
            frm.dashboard.set_headline_alert(__('Sync Paused'), 'orange');
        }

        // Show next sync time
        if (frm.doc.next_sync_date) {
            let next_sync = frappe.datetime.str_to_obj(frm.doc.next_sync_date);
            let now = frappe.datetime.now_datetime();
            let hours_left = frappe.datetime.get_hour_diff(next_sync, now);

            if (hours_left > 0) {
                frm.dashboard.add_comment(__('Next sync in {0} hours', [Math.round(hours_left)]), 'blue', true);
            }
        }

        // Show sync stats
        if (frm.doc.total_syncs > 0) {
            let success_rate = ((frm.doc.total_syncs - (frm.doc.failed_syncs || 0)) / frm.doc.total_syncs * 100).toFixed(1);
            frm.dashboard.add_comment(__('Success Rate: {0}% ({1}/{2} syncs)', [success_rate, frm.doc.total_syncs - (frm.doc.failed_syncs || 0), frm.doc.total_syncs]), 'green', true);
        }
    },

    platform: function (frm) {
        // Filter ad_account by platform
        frm.set_query('ad_account', function () {
            return {
                filters: {
                    'platform': frm.doc.platform,
                    'is_active': 1
                }
            };
        });

        // Set default connector name
        if (frm.is_new() && !frm.doc.connector_name) {
            frm.set_value('connector_name', frm.doc.platform + ' Analytics');
        }
    },

    ad_account: function (frm) {
        // Auto-populate company and platform from ad_account
        if (frm.doc.ad_account) {
            frappe.db.get_value('Ad Account', frm.doc.ad_account, ['company', 'social_media_network'], function (r) {
                if (r) {
                    if (r.company) frm.set_value('company', r.company);
                    if (r.social_media_network) frm.set_value('platform', r.social_media_network);
                }
            });
        }
    }
});

function sync_analytics(frm) {
    frappe.call({
        method: 'marketing_hub.marketing_hub.doctype.analytics_connector.analytics_connector.sync_connector',
        args: {
            connector_name: frm.doc.name
        },
        freeze: true,
        freeze_message: __('Syncing analytics data...'),
        callback: function (r) {
            if (r.message && r.message.status === 'Success') {
                frappe.show_alert({
                    message: __('Synced {0} records successfully!', [r.message.records]),
                    indicator: 'green'
                }, 5);
                frm.reload_doc();
            } else {
                frappe.msgprint({
                    title: __('Sync Failed'),
                    message: r.message ? r.message.message : __('Unknown error'),
                    indicator: 'red'
                });
            }
        }
    });
}

function get_platform_campaigns(frm) {
    frappe.call({
        method: 'marketing_hub.marketing_hub.doctype.analytics_connector.analytics_connector.get_campaigns_from_platform',
        args: {
            connector_name: frm.doc.name
        },
        freeze: true,
        freeze_message: __('Fetching campaigns from platform...'),
        callback: function (r) {
            if (r.message && r.message.status === 'Success') {
                // Show campaigns in a dialog
                let campaigns = r.message.campaigns;
                let html = '<table class="table table-bordered"><thead><tr><th>ID</th><th>Name</th><th>Status</th></tr></thead><tbody>';

                campaigns.forEach(function (campaign) {
                    html += `<tr><td>${campaign.id}</td><td>${campaign.name}</td><td>${campaign.status}</td></tr>`;
                });

                html += '</tbody></table>';

                frappe.msgprint({
                    title: __('Platform Campaigns'),
                    message: html,
                    indicator: 'blue',
                    wide: true
                });
            } else {
                frappe.msgprint({
                    title: __('Failed to Fetch Campaigns'),
                    message: r.message ? r.message.message : __('Unknown error'),
                    indicator: 'red'
                });
            }
        }
    });
}
