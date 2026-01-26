#!/usr/bin/env python3
"""Script to create Marketing Hub Settings for all companies"""

import sys
import os

# Add the apps directory to path
sys.path.insert(0, '/home/puxxo/CodeBase/erpNext/frappe-bench-v15/apps')

import frappe

def create_marketing_hub_settings():
    """Create Marketing Hub Settings for all companies"""
    frappe.init('erpnext-v15.local')
    frappe.connect()
    
    # Get all companies
    companies = frappe.get_all('Company', pluck='name')
    print(f"Found {len(companies)} companies: {companies}")
    
    # Get existing settings
    existing_settings = frappe.get_all('Marketing Hub Settings', pluck='name')
    print(f"Existing Marketing Hub Settings: {existing_settings}")
    
    # Create settings for each company if not exists
    for company in companies:
        if company not in existing_settings:
            print(f"Creating Marketing Hub Settings for {company}...")
            try:
                settings = frappe.new_doc("Marketing Hub Settings")
                settings.company = company
                settings.agency_mode = 0
                settings.insert(ignore_permissions=True)
                frappe.db.commit()
                print(f"✓ Created settings for {company}")
            except Exception as e:
                print(f"✗ Error creating settings for {company}: {e}")
                frappe.db.rollback()
        else:
            print(f"✓ Settings already exist for {company}")
    
    frappe.destroy()
    print("\nDone!")

if __name__ == "__main__":
    create_marketing_hub_settings()
