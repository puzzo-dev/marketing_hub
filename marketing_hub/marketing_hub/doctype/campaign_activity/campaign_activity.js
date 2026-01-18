// Copyright (c) 2026, I-Varse Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Campaign Activity', {
    refresh: function (frm) {
        // Add custom buttons
        if (!frm.is_new() && frm.doc.status !== 'Completed') {
            frm.add_custom_button(__('Execute Now'), function () {
                execute_activity(frm);
            }, __('Actions'));
        }

        if (frm.doc.status === 'Failed' && frm.doc.retry_count < frm.doc.max_retries) {
            frm.add_custom_button(__('Retry'), function () {
                retry_activity(frm);
            }, __('Actions'));
        }

        // Show status indicator
        if (frm.doc.status === 'Completed') {
            frm.dashboard.set_headline_alert(__('Activity Completed'), 'green');
        } else if (frm.doc.status === 'Failed') {
            frm.dashboard.set_headline_alert(__('Activity Failed'), 'red');
        } else if (frm.doc.status === 'In Progress') {
            frm.dashboard.set_headline_alert(__('Activity In Progress'), 'blue');
        }

        // Show execution metrics
        if (frm.doc.sent_count > 0) {
            let success_rate = ((frm.doc.delivered_count / frm.doc.sent_count) * 100).toFixed(1);
            frm.dashboard.add_comment(__('Delivery Rate: {0}% ({1}/{2})', [success_rate, frm.doc.delivered_count, frm.doc.sent_count]), 'green', true);
        }

        // Show scheduled time
        if (frm.doc.status === 'Scheduled' && frm.doc.scheduled_date) {
            let scheduled = frappe.datetime.str_to_obj(frm.doc.scheduled_date);
            let now = frappe.datetime.now_datetime();
            let hours_left = frappe.datetime.get_hour_diff(scheduled, now);

            if (hours_left > 0) {
                frm.dashboard.add_comment(__('Scheduled in {0} hours', [Math.round(hours_left)]), 'blue', true);
            } else {
                frm.dashboard.add_comment(__('Scheduled time passed - ready to execute'), 'orange', true);
            }
        }
    },

    activity_type: function (frm) {
        // Set default activity name
        if (frm.is_new() && !frm.doc.activity_name && frm.doc.campaign) {
            frappe.db.get_value('Campaign', frm.doc.campaign, 'campaign_name', function (r) {
                if (r && r.campaign_name) {
                    frm.set_value('activity_name', r.campaign_name + ' - ' + frm.doc.activity_type);
                }
            });
        }
    },

    segment: function (frm) {
        // Calculate target count from segment
        if (frm.doc.segment) {
            frappe.call({
                method: 'frappe.client.get_count',
                args: {
                    doctype: 'Lead',
                    filters: {
                        // This would use segment's filter criteria
                    }
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('target_count', r.message);
                    }
                }
            });
        }
    }
});

function execute_activity(frm) {
    frappe.confirm(
        __('Execute this campaign activity now?'),
        function () {
            frappe.call({
                method: 'marketing_hub.marketing_hub.doctype.campaign_activity.campaign_activity.execute_activity',
                args: {
                    activity_name: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Executing campaign activity...'),
                callback: function (r) {
                    if (r.message && r.message.status === 'Success') {
                        frappe.show_alert({
                            message: __('Activity executed successfully!'),
                            indicator: 'green'
                        }, 5);
                        frm.reload_doc();
                    } else {
                        frappe.msgprint({
                            title: __('Execution Failed'),
                            message: r.message ? r.message.message : __('Unknown error'),
                            indicator: 'red'
                        });
                    }
                }
            });
        }
    );
}

function retry_activity(frm) {
    frappe.confirm(
        __('Retry this failed activity?'),
        function () {
            frappe.call({
                method: 'marketing_hub.marketing_hub.doctype.campaign_activity.campaign_activity.retry_activity',
                args: {
                    activity_name: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Retrying activity...'),
                callback: function (r) {
                    if (r.message && r.message.status === 'Success') {
                        frappe.show_alert({
                            message: __('Activity retried successfully!'),
                            indicator: 'green'
                        }, 5);
                        frm.reload_doc();
                    } else {
                        frappe.msgprint({
                            title: __('Retry Failed'),
                            message: r.message ? r.message.message : __('Unknown error'),
                            indicator: 'red'
                        });
                    }
                }
            });
        }
    );
}
