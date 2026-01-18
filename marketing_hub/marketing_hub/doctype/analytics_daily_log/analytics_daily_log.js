// Copyright (c) 2026, I-Varse Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Analytics Daily Log', {
    refresh: function (frm) {
        // Show calculated metrics
        if (frm.doc.roas) {
            let roas_color = frm.doc.roas >= 2 ? 'green' : (frm.doc.roas >= 1 ? 'orange' : 'red');
            frm.dashboard.add_comment(__('ROAS: {0}x', [frm.doc.roas.toFixed(2)]), roas_color, true);
        }

        if (frm.doc.ctr) {
            let ctr_color = frm.doc.ctr >= 2 ? 'green' : (frm.doc.ctr >= 1 ? 'orange' : 'red');
            frm.dashboard.add_comment(__('CTR: {0}%', [frm.doc.ctr.toFixed(2)]), ctr_color, true);
        }

        if (frm.doc.conversion_rate) {
            let conv_color = frm.doc.conversion_rate >= 5 ? 'green' : (frm.doc.conversion_rate >= 2 ? 'orange' : 'red');
            frm.dashboard.add_comment(__('Conversion Rate: {0}%', [frm.doc.conversion_rate.toFixed(2)]), conv_color, true);
        }
    },

    connector: function (frm) {
        // Auto-populate channel from connector
        if (frm.doc.connector) {
            frappe.db.get_value('Analytics Connector', frm.doc.connector, 'platform', function (r) {
                if (r && r.platform) {
                    frm.set_value('channel', r.platform);
                }
            });
        }
    }
});
