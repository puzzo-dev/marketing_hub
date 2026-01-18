// Copyright (c) 2026, Your Name and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marketing Segment', {
	refresh: function(frm) {
		// Add Refresh button
		if (!frm.is_new() && frm.doc.status === 'Active') {
			frm.add_custom_button(__('Refresh Segment'), function() {
				frappe.call({
					method: 'marketing_hub.marketing_hub.doctype.marketing_segment.marketing_segment.refresh_segment',
					args: {
						segment_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.show_alert({
								message: __('Segment refreshed. Size: {0}', [r.message.segment_size]),
								indicator: 'green'
							});
							frm.reload_doc();
						}
					}
				});
			});
		}

		// Add Preview button
		if (frm.doc.filters_json) {
			frm.add_custom_button(__('Preview Members'), function() {
				frappe.call({
					method: 'marketing_hub.marketing_hub.doctype.marketing_segment.marketing_segment.get_segment_preview',
					args: {
						filters_json: frm.doc.filters_json,
						segment_type: frm.doc.segment_type || 'Lead',
						limit: 10
					},
					callback: function(r) {
						if (r.message) {
							show_preview_dialog(r.message);
						}
					}
				});
			});
		}
	},

	filters_json: function(frm) {
		// Auto-validate JSON on change
		if (frm.doc.filters_json) {
			try {
				JSON.parse(frm.doc.filters_json);
				frm.set_df_property('filters_json', 'description', 'Valid JSON format ✓');
			} catch(e) {
				frm.set_df_property('filters_json', 'description', 'Invalid JSON format: ' + e.message);
			}
		}
	}
});

function show_preview_dialog(data) {
	let dialog = new frappe.ui.Dialog({
		title: __('Segment Preview'),
		fields: [
			{
				fieldname: 'html',
				fieldtype: 'HTML'
			}
		]
	});

	let html = `<div class="segment-preview">
		<p><strong>Total Members:</strong> ${data.total_count}</p>
		<p><strong>Preview (first 10):</strong></p>
		<table class="table table-bordered">
			<thead>
				<tr>
					<th>Name</th>
					<th>Email</th>
					<th>Company</th>
				</tr>
			</thead>
			<tbody>`;

	data.preview.forEach(member => {
		html += `<tr>
			<td><a href="/app/${member.doctype || 'lead'}/${member.name}">${member.name}</a></td>
			<td>${member.email_id || member.email || '-'}</td>
			<td>${member.company || '-'}</td>
		</tr>`;
	});

	html += `</tbody></table></div>`;

	dialog.fields_dict.html.$wrapper.html(html);
	dialog.show();
}
