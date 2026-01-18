// Copyright (c) 2026, Your Name and contributors
// For license information, please see license.txt

frappe.ui.form.on('Social Post', {
	refresh: function(frm) {
		// Add custom buttons based on status
		if (frm.doc.status === 'Draft') {
			frm.add_custom_button(__('Publish Now'), function() {
				frappe.call({
					method: 'marketing_hub.marketing_hub.doctype.social_post.social_post.publish_post',
					args: {
						post_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.show_alert({
								message: r.message.message,
								indicator: 'green'
							});
							frm.reload_doc();
						}
					}
				});
			}, __('Actions'));

			frm.add_custom_button(__('Schedule'), function() {
				show_schedule_dialog(frm);
			}, __('Actions'));
		}

		if (frm.doc.status === 'Scheduled') {
			frm.add_custom_button(__('Cancel Schedule'), function() {
				frm.set_value('status', 'Draft');
				frm.set_value('scheduled_time', null);
				frm.save();
			}, __('Actions'));
		}

		// Add Best Time button
		if (frm.doc.platform) {
			frm.add_custom_button(__('Best Time to Post'), function() {
				frappe.call({
					method: 'marketing_hub.marketing_hub.doctype.social_post.social_post.get_platform_best_time',
					args: {
						platform: frm.doc.platform
					},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint({
								title: __('Best Time to Post on {0}', [frm.doc.platform]),
								message: r.message,
								indicator: 'blue'
							});
						}
					}
				});
			}, __('Info'));
		}

		// Add Refresh Metrics button
		if (frm.doc.status === 'Published') {
			frm.add_custom_button(__('Refresh Metrics'), function() {
				frappe.msgprint(__('Metrics refresh functionality will be implemented with platform API integration'));
			}, __('Actions'));
		}

		// Show character count
		if (frm.doc.content) {
			update_character_count(frm);
		}
	},

	content: function(frm) {
		update_character_count(frm);
	},

	platform: function(frm) {
		update_character_count(frm);
	},

	media_attachment: function(frm) {
		// Auto-detect media type
		if (frm.doc.media_attachment) {
			let ext = frm.doc.media_attachment.split('.').pop().toLowerCase();
			if (['jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
				frm.set_value('media_type', 'Image');
			} else if (['mp4', 'mov', 'avi', 'webm'].includes(ext)) {
				frm.set_value('media_type', 'Video');
			} else if (ext === 'gif') {
				frm.set_value('media_type', 'GIF');
			}
		}
	}
});

function update_character_count(frm) {
	if (!frm.doc.content) return;

	// Strip HTML tags for accurate count
	let temp = document.createElement('div');
	temp.innerHTML = frm.doc.content;
	let clean_text = temp.textContent || temp.innerText || '';
	let char_count = clean_text.length;

	// Platform limits
	let platform_limits = {
		'Twitter/X': 280,
		'Instagram': 2200,
		'Facebook': 63206,
		'LinkedIn': 3000,
		'TikTok': 2200,
		'YouTube': 5000,
		'Pinterest': 500
	};

	let limit = platform_limits[frm.doc.platform] || 'N/A';
	let color = 'green';

	if (typeof limit === 'number' && char_count > limit) {
		color = 'red';
	} else if (typeof limit === 'number' && char_count > limit * 0.9) {
		color = 'orange';
	}

	let count_html = `<span style="color: ${color}; font-weight: bold;">
		${char_count} / ${limit} characters
	</span>`;

	frm.set_df_property('content', 'description', count_html);
}

function show_schedule_dialog(frm) {
	let dialog = new frappe.ui.Dialog({
		title: __('Schedule Post'),
		fields: [
			{
				fieldname: 'scheduled_time',
				fieldtype: 'Datetime',
				label: __('Schedule Time'),
				reqd: 1,
				default: frappe.datetime.add_days(frappe.datetime.now_datetime(), 1)
			}
		],
		primary_action_label: __('Schedule'),
		primary_action: function(values) {
			frappe.call({
				method: 'marketing_hub.marketing_hub.doctype.social_post.social_post.schedule_post',
				args: {
					post_name: frm.doc.name,
					scheduled_time: values.scheduled_time
				},
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: r.message.message,
							indicator: 'green'
						});
						frm.reload_doc();
						dialog.hide();
					}
				}
			});
		}
	});

	dialog.show();
}
