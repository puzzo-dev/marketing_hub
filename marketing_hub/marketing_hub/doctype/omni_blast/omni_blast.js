// Copyright (c) 2026, Puzzo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Omni Blast', {
	refresh: function(frm) {
		// Add custom buttons based on status
		if (frm.doc.status === "Draft" && frm.doc.networks && frm.doc.networks.length > 0) {
			frm.add_custom_button(__('Generate Posts'), function() {
				frappe.call({
					method: 'generate_posts',
					doc: frm.doc,
					callback: function(r) {
						frm.reload_doc();
					}
				});
			}).addClass('btn-primary');
		}
		
		if ((frm.doc.status === "Scheduled" || frm.doc.status === "Draft") && 
		    frm.doc.created_posts && frm.doc.created_posts.length > 0) {
			frm.add_custom_button(__('Execute Blast'), function() {
				frappe.confirm(
					'Are you sure you want to execute this blast and publish all posts?',
					function() {
						frappe.call({
							method: 'execute_blast',
							doc: frm.doc,
							callback: function(r) {
								frm.reload_doc();
								if (r.message) {
									frappe.show_alert({
										message: `Published: ${r.message.published}, Failed: ${r.message.failed}`,
										indicator: r.message.failed > 0 ? 'orange' : 'green'
									});
								}
							}
						});
					}
				);
			}).addClass('btn-primary');
		}
		
		// Show created posts section
		if (frm.doc.created_posts && frm.doc.created_posts.length > 0) {
			frm.set_df_property('created_posts', 'hidden', 0);
		}
	},
	
	blast_type: function(frm) {
		// Show/hide scheduled_time based on blast_type
		if (frm.doc.blast_type === "Scheduled") {
			frm.set_df_property('scheduled_time', 'reqd', 1);
		} else {
			frm.set_df_property('scheduled_time', 'reqd', 0);
		}
	}
});

// Child table: Omni Blast Network
frappe.ui.form.on('Omni Blast Network', {
	network: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.network) {
			// Fetch network details
			frappe.db.get_doc('Social Media Network', row.network).then(network => {
				// Set post types options from network's post_types
				if (network.post_types) {
					frappe.meta.get_docfield('Omni Blast Network', 'post_type', frm.doc.name).options = 
						network.post_types.split('\n').join('\n');
				}
			});
		}
	},
	
	override_content: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.override_content && !row.custom_content) {
			// Pre-fill with main content
			frappe.model.set_value(cdt, cdn, 'custom_content', frm.doc.content || '');
		}
	}
});
