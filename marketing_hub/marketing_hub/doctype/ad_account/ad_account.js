// Copyright (c) 2026, I-Varse Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ad Account', {
    refresh: function (frm) {
        // Add custom buttons
        if (!frm.is_new()) {
            frm.add_custom_button(__('Test Connection'), function () {
                test_connection(frm);
            }, __('Actions'));

            frm.add_custom_button(__('Refresh Token'), function () {
                refresh_token(frm);
            }, __('Actions'));
        }

        // Show token expiry warning
        if (frm.doc.token_expiry) {
            let expiry = frappe.datetime.str_to_obj(frm.doc.token_expiry);
            let now = frappe.datetime.now_datetime();
            let hours_left = frappe.datetime.get_hour_diff(expiry, now);

            if (hours_left < 24 && hours_left > 0) {
                frm.dashboard.add_comment(__('Token expires in {0} hours', [Math.round(hours_left)]), 'yellow', true);
            } else if (hours_left <= 0) {
                frm.dashboard.add_comment(__('Token has expired. Please refresh.'), 'red', true);
            }
        }

        // Show sync status indicator
        if (frm.doc.sync_status === 'Success') {
            frm.dashboard.set_headline_alert(__('Connection Active'), 'green');
        } else if (frm.doc.sync_status === 'Failed') {
            frm.dashboard.set_headline_alert(__('Connection Failed'), 'red');
        }
    },

    platform: function (frm) {
        // Set default naming based on platform
        if (frm.is_new() && !frm.doc.account_name) {
            frm.set_value('account_name', frm.doc.platform + ' Account');
        }
    }
});

function test_connection(frm) {
    frappe.call({
        method: 'marketing_hub.marketing_hub.doctype.ad_account.ad_account.test_account_connection',
        args: {
            ad_account_name: frm.doc.name
        },
        freeze: true,
        freeze_message: __('Testing connection...'),
        callback: function (r) {
            if (r.message && r.message.status === 'Success') {
                frappe.show_alert({
                    message: __('Connection successful!'),
                    indicator: 'green'
                }, 5);
                frm.reload_doc();
            } else {
                frappe.msgprint({
                    title: __('Connection Failed'),
                    message: r.message ? r.message.message : __('Unknown error'),
                    indicator: 'red'
                });
            }
        }
    });
}

function refresh_token(frm) {
    frappe.confirm(
        __('This will refresh the access token using the refresh token. Continue?'),
        function () {
            frappe.call({
                method: 'marketing_hub.marketing_hub.doctype.ad_account.ad_account.refresh_token',
                args: {
                    ad_account_name: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Refreshing token...'),
                callback: function (r) {
                    if (r.message && r.message.status === 'Success') {
                        frappe.show_alert({
                            message: __('Token refreshed successfully!'),
                            indicator: 'green'
                        }, 5);
                        frm.reload_doc();
                    } else {
                        frappe.msgprint({
                            title: __('Token Refresh Failed'),
                            message: r.message ? r.message.message : __('Unknown error'),
                            indicator: 'red'
                        });
                    }
                }
            });
        }
    );
}
