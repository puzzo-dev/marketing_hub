// Campaign Doctype Client Script
frappe.ui.form.on("Campaign", {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.is_new()) {
            frm.add_custom_button(__("View Analytics"), function() {
                frappe.route_options = {"campaign": frm.doc.name};
                frappe.set_route("query-report", "Campaign Analytics");
            });

            frm.add_custom_button(__("Execute Blast"), function() {
                execute_omni_blast(frm);
            });

            frm.add_custom_button(__("Calculate ROAS"), function() {
                calculate_roas(frm);
            });
        }

        // Show agency fields if in agency mode
        toggle_agency_fields(frm);

        // Setup multi-select for channels field
        setup_channels_multiselect(frm);
    },

    is_omni_campaign: function(frm) {
        if (frm.doc.is_omni_campaign) {
            frappe.msgprint({
                title: __("Omni-Channel Campaign"),
                message: __("This campaign will execute across multiple channels simultaneously"),
                indicator: "blue"
            });
        }
    }
});

function setup_channels_multiselect(frm) {
    const channels = [
        "Email", "WhatsApp", "SMS", "Push Notification",
        "Google Ads", "Meta Ads", "TikTok Ads", "Twitter/X Ads",
        "Reddit Ads", "LinkedIn Ads", "Trade Show", "TV",
        "Radio", "Telecalling", "Outdoor", "Print", "Event", "Omni-Channel"
    ];

    // Add a button to select channels
    frm.fields_dict.channels_used.$wrapper.find('.control-label').append(
        ` <button class="btn btn-xs btn-default" style="margin-left: 10px;"
            onclick="show_channel_selector('${frm.doctype}', '${frm.docname}', ${JSON.stringify(channels).replace(/"/g, '&quot;')})">
            Select Channels
        </button>`
    );
}

// Global function to show channel selector
window.show_channel_selector = function(doctype, docname, channels) {
    const frm = cur_frm;
    const current_channels = frm.doc.channels_used ? frm.doc.channels_used.split(',').map(c => c.trim()) : [];

    const checkboxes = channels.map(channel => {
        const checked = current_channels.includes(channel);
        return `
            <div class="checkbox" style="margin: 5px 0;">
                <label>
                    <input type="checkbox" value="${channel}" ${checked ? 'checked' : ''}>
                    ${channel}
                </label>
            </div>
        `;
    }).join('');

    const d = new frappe.ui.Dialog({
        title: __('Select Channels'),
        fields: [
            {
                fieldtype: 'HTML',
                options: `
                    <div style="max-height: 400px; overflow-y: auto;">
                        <div style="margin-bottom: 10px;">
                            <button class="btn btn-xs btn-default" onclick="
                                $(this).closest('.modal-body').find('input[type=checkbox]').prop('checked', true);
                            ">Select All</button>
                            <button class="btn btn-xs btn-default" onclick="
                                $(this).closest('.modal-body').find('input[type=checkbox]').prop('checked', false);
                            ">Clear All</button>
                        </div>
                        ${checkboxes}
                    </div>
                `
            }
        ],
        primary_action_label: __('Update'),
        primary_action: function() {
            const selected = [];
            d.$wrapper.find('input[type=checkbox]:checked').each(function() {
                selected.push($(this).val());
            });
            frm.set_value('channels_used', selected.join(', '));
            d.hide();
        }
    });

    d.show();
};

function toggle_agency_fields(frm) {
    // Check if agency mode
    frappe.call({
        method: "marketing_hub.utils.agency_mode.get_agency_mode",
        callback: function(r) {
            if (r.message) {
                frm.set_df_property("client", "hidden", 0);
                frm.set_df_property("client", "reqd", 1);
            } else {
                frm.set_df_property("client", "hidden", 1);
                frm.set_df_property("client", "reqd", 0);
            }
        }
    });
}

function execute_omni_blast(frm) {
    frappe.prompt([
        {
            fieldname: "segment",
            fieldtype: "Link",
            options: "Marketing Segment",
            label: __("Target Segment"),
            reqd: 1
        },
        {
            fieldname: "channels",
            fieldtype: "MultiSelect",
            options: marketing_hub.channels.join("\n"),
            label: __("Channels"),
            reqd: 1
        },
        {
            fieldname: "scheduled_time",
            fieldtype: "Datetime",
            label: __("Schedule For"),
            default: frappe.datetime.now_datetime()
        }
    ], function(values) {
        frappe.call({
            method: "marketing_hub.utils.omni_blast.execute_blast",
            args: {
                campaign: frm.doc.name,
                segment: values.segment,
                channels: values.channels,
                scheduled_time: values.scheduled_time
            },
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint({
                        title: __("Blast Executed"),
                        message: __("Omni-channel blast has been executed successfully"),
                        indicator: "green"
                    });
                    frm.reload_doc();
                }
            }
        });
    }, __("Execute Omni-Channel Blast"));
}

function calculate_roas(frm) {
    frappe.call({
        method: "marketing_hub.api.analytics.calculate_campaign_roas",
        args: {
            campaign: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                frm.set_value("roas", r.message.roas);
                frappe.show_alert({
                    message: __("ROAS: {0}", [r.message.roas]),
                    indicator: "green"
                }, 5);
            }
        }
    });
}
