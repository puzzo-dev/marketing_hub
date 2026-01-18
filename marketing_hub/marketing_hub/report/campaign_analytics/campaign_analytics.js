// Copyright (c) 2026, I-Varse Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Campaign Analytics"] = {
    "filters": [
        {
            "fieldname": "campaign",
            "label": __("Campaign"),
            "fieldtype": "Link",
            "options": "Campaign"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        }
    ],

    "onload": function(report) {
        // Add chart button
        report.page.add_inner_button(__("Show Charts"), function() {
            report.show_charts = !report.show_charts;
            if (report.show_charts) {
                report.refresh();
            }
        });
    },

    "after_datatable_render": function(datatable) {
        // Auto-show charts after data loads
        if (datatable && datatable.datamanager.data.length > 0) {
            frappe.query_reports["Campaign Analytics"].show_charts = true;
        }
    },

    "get_chart_data": function(columns, result) {
        if (!result || result.length === 0) {
            return null;
        }

        // Prepare data for multiple charts
        let campaign_names = [];
        let leads_data = [];
        let revenue_data = [];
        let roas_data = [];
        let engagement_data = {
            impressions: [],
            clicks: [],
            ctr: []
        };

        result.forEach(row => {
            campaign_names.push(row.campaign || 'Unknown');
            leads_data.push(row.leads || 0);
            revenue_data.push(row.revenue || 0);
            roas_data.push(row.roas || 0);
            engagement_data.impressions.push(row.impressions || 0);
            engagement_data.clicks.push(row.clicks || 0);
            engagement_data.ctr.push(row.ctr || 0);
        });

        return {
            // Primary chart - Funnel metrics
            data: {
                labels: campaign_names,
                datasets: [
                    {
                        name: __("Leads"),
                        values: leads_data,
                        chartType: 'bar'
                    },
                    {
                        name: __("Revenue"),
                        values: revenue_data,
                        chartType: 'bar'
                    }
                ]
            },
            type: 'bar',
            height: 300,
            colors: ['#3b82f6', '#10b981']
        };
    },

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Color code ROAS values
        if (column.fieldname === "roas" && !isNaN(value)) {
            let roas_value = parseFloat(value);
            if (roas_value >= 3) {
                value = `<span style="color: #10b981; font-weight: bold;">${value}</span>`;
            } else if (roas_value >= 2) {
                value = `<span style="color: #f59e0b; font-weight: bold;">${value}</span>`;
            } else if (roas_value > 0) {
                value = `<span style="color: #ef4444;">${value}</span>`;
            }
        }

        // Format CTR as percentage
        if (column.fieldname === "ctr" && !isNaN(value)) {
            value = `${parseFloat(value).toFixed(2)}%`;
        }

        return value;
    },

    // Custom charts section
    "custom_charts": function(report) {
        if (!report.data || report.data.length === 0) {
            return;
        }

        // Create container for custom charts
        let chart_area = report.page.wrapper.find('.chart-wrapper');
        if (!chart_area.length) {
            chart_area = $('<div class="chart-wrapper" style="margin: 15px 0;"></div>')
                .insertBefore(report.page.wrapper.find('.datatable'));
        }
        chart_area.empty();

        // Prepare data
        let campaigns = report.data.map(row => row.campaign);
        let leads = report.data.map(row => row.leads || 0);
        let revenue = report.data.map(row => row.revenue || 0);
        let roas = report.data.map(row => row.roas || 0);
        let impressions = report.data.map(row => row.impressions || 0);
        let clicks = report.data.map(row => row.clicks || 0);

        // Chart 1: Funnel - Leads to Revenue
        let funnel_chart_wrapper = $('<div class="col-md-6" style="padding: 10px;"></div>').appendTo(
            $('<div class="row"></div>').appendTo(chart_area)
        );
        $('<div><h5 style="margin-bottom: 15px;">Campaign Funnel</h5></div>').appendTo(funnel_chart_wrapper);
        let funnel_chart_div = $('<div class="funnel-chart"></div>').appendTo(funnel_chart_wrapper);

        new frappe.Chart(funnel_chart_div[0], {
            title: "",
            data: {
                labels: campaigns,
                datasets: [
                    {
                        name: "Leads",
                        values: leads
                    },
                    {
                        name: "Revenue",
                        values: revenue
                    }
                ]
            },
            type: 'bar',
            height: 250,
            colors: ['#3b82f6', '#10b981'],
            barOptions: {
                spaceRatio: 0.3
            },
            axisOptions: {
                xIsSeries: true
            }
        });

        // Chart 2: ROAS Performance
        let roas_chart_wrapper = $('<div class="col-md-6" style="padding: 10px;"></div>').appendTo(
            chart_area.find('.row')
        );
        $('<div><h5 style="margin-bottom: 15px;">ROAS Performance</h5></div>').appendTo(roas_chart_wrapper);
        let roas_chart_div = $('<div class="roas-chart"></div>').appendTo(roas_chart_wrapper);

        new frappe.Chart(roas_chart_div[0], {
            title: "",
            data: {
                labels: campaigns,
                datasets: [
                    {
                        name: "ROAS",
                        values: roas
                    }
                ]
            },
            type: 'bar',
            height: 250,
            colors: ['#f59e0b'],
            barOptions: {
                spaceRatio: 0.3
            },
            axisOptions: {
                xIsSeries: true
            }
        });

        // Chart 3: Engagement - Impressions vs Clicks
        let engagement_chart_wrapper = $('<div class="col-md-12" style="padding: 10px; margin-top: 20px;"></div>').appendTo(
            $('<div class="row"></div>').appendTo(chart_area)
        );
        $('<div><h5 style="margin-bottom: 15px;">Engagement Metrics</h5></div>').appendTo(engagement_chart_wrapper);
        let engagement_chart_div = $('<div class="engagement-chart"></div>').appendTo(engagement_chart_wrapper);

        new frappe.Chart(engagement_chart_div[0], {
            title: "",
            data: {
                labels: campaigns,
                datasets: [
                    {
                        name: "Impressions",
                        values: impressions
                    },
                    {
                        name: "Clicks",
                        values: clicks
                    }
                ]
            },
            type: 'axis-mixed',
            height: 300,
            colors: ['#8b5cf6', '#ec4899'],
            axisOptions: {
                xIsSeries: true
            }
        });
    }
};
