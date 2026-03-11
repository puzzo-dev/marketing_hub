"""
Add unique index to Analytics Daily Log to prevent duplicate records
"""

import frappe


def execute():
	"""Create unique composite index on Analytics Daily Log"""
	try:
		# Check if index already exists
		existing_indexes = frappe.db.sql("""
			SHOW INDEX FROM `tabAnalytics Daily Log`
			WHERE Key_name = 'unique_analytics_log'
		""")
		
		if existing_indexes:
			print("Unique index already exists on Analytics Daily Log")
			return
		
		# Create unique index
		frappe.db.sql("""
			ALTER TABLE `tabAnalytics Daily Log`
			ADD UNIQUE INDEX unique_analytics_log (log_date, campaign, channel, connector)
		""")
		
		print("Successfully created unique index on Analytics Daily Log")
		
	except Exception as e:
		# If there are duplicate records, log them
		if "Duplicate entry" in str(e):
			frappe.log_error(
				f"Cannot create unique index due to existing duplicates: {str(e)}",
				"Analytics Daily Log Index Creation"
			)
			print(f"Warning: Duplicate records exist. Clean up required before creating index.")
			
			# Find duplicates
			duplicates = frappe.db.sql("""
				SELECT log_date, campaign, channel, connector, COUNT(*) as count
				FROM `tabAnalytics Daily Log`
				GROUP BY log_date, campaign, channel, connector
				HAVING count > 1
			""", as_dict=True)
			
			if duplicates:
				print(f"Found {len(duplicates)} sets of duplicate records:")
				for dup in duplicates[:10]:  # Show first 10
					print(f"  - Date: {dup.log_date}, Campaign: {dup.campaign}, Channel: {dup.channel}, Count: {dup.count}")
		else:
			frappe.log_error(f"Error creating unique index: {str(e)}", "Analytics Daily Log Index Creation")
			print(f"Error: {str(e)}")
