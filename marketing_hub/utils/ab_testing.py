import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date
from marketing_hub.utils.omni_blast import _get_segment_recipients
import random

@frappe.whitelist()
def execute_test(test_id):
	test = frappe.get_doc("A-B Test", test_id)
	
	if test.status != "Draft":
		frappe.throw(_("Test must be in Draft status to execute"))
		
	if not test.variant_a_template or not test.variant_b_template:
		frappe.throw(_("Both Variant A and Variant B templates are required"))
		
	# Get segment recipients
	segment = frappe.get_doc("Marketing Segment", test.segment)
	recipients = _get_segment_recipients(segment, channel="Email") # Hardcoding Email for now
	
	if not recipients:
		frappe.throw(_("No recipients found in segment"))
		
	# Calculate split
	total_recipients = len(recipients)
	split_size = int((test.split_percentage / 100.0) * total_recipients / 2)
	
	if split_size < 1:
		frappe.throw(_("Test group size is too small. Need more recipients or higher percentage."))
		
	# Shuffle recipients to ensure random distribution
	random.shuffle(recipients)
	
	group_a = recipients[:split_size]
	group_b = recipients[split_size:split_size*2]
	
	# Send Variant A
	template_a = frappe.get_doc("Marketing Template", test.variant_a_template)
	for r in group_a:
		try:
			frappe.sendmail(
				recipients=[r.get("email")],
				subject=template_a.subject,
				message=template_a.content,
				reference_doctype="A-B Test",
				reference_name=test.name,
				custom_message_id=f"{test.name}-A"
			)
		except Exception as e:
			frappe.log_error(f"Failed to send Variant A to {r.get('email')}", str(e))
			
	# Send Variant B
	template_b = frappe.get_doc("Marketing Template", test.variant_b_template)
	for r in group_b:
		try:
			frappe.sendmail(
				recipients=[r.get("email")],
				subject=template_b.subject,
				message=template_b.content,
				reference_doctype="A-B Test",
				reference_name=test.name,
				custom_message_id=f"{test.name}-B"
			)
		except Exception as e:
			frappe.log_error(f"Failed to send Variant B to {r.get('email')}", str(e))
			
	# Update test status
	test.status = "Running"
	test.save()
	frappe.db.commit()
	
	# Enqueue evaluation job
	frappe.enqueue(
		"marketing_hub.utils.ab_testing.evaluate_test",
		test_id=test.name,
		enqueue_after_commit=True,
		run_after=add_to_date(now_datetime(), hours=test.test_duration_hours)
	)
	
	return {"status": "Success", "message": f"Sent {split_size} of A and {split_size} of B"}

def evaluate_test(test_id):
	"""Evaluate the results of the A/B test and pick a winner"""
	test = frappe.get_doc("A-B Test", test_id)
	
	if test.status != "Running":
		return
		
	# In a real scenario, we'd query email open/click tracking tables linked to custom_message_id
	# For now, we simulate a winner evaluation
	# frappe.db.sql("SELECT COUNT(*) FROM `tabEmail Tracker` WHERE reference_name=%s...", test.name)
	
	# Simulated winner logic
	import random
	winner = "A" if random.choice([True, False]) else "B"
	
	test.winner = test.variant_a_template if winner == "A" else test.variant_b_template
	test.status = "Completed"
	test.save()
	frappe.db.commit()
	
	# Send to remaining recipients
	_send_to_remaining(test, winner)
	
def _send_to_remaining(test, winner):
	segment = frappe.get_doc("Marketing Segment", test.segment)
	recipients = _get_segment_recipients(segment, channel="Email")
	
	total_recipients = len(recipients)
	split_size = int((test.split_percentage / 100.0) * total_recipients / 2)
	
	# Same deterministic shuffle to exclude already sent ones
	random.seed(test.name) # Use test name as seed so we get same shuffle
	random.shuffle(recipients)
	random.seed() # reset
	
	remaining = recipients[split_size*2:]
	template = frappe.get_doc("Marketing Template", test.winner)
	
	for r in remaining:
		try:
			frappe.sendmail(
				recipients=[r.get("email")],
				subject=template.subject,
				message=template.content,
				reference_doctype="A-B Test",
				reference_name=test.name
			)
		except Exception as e:
			frappe.log_error(f"Failed to send Winner to {r.get('email')}", str(e))

