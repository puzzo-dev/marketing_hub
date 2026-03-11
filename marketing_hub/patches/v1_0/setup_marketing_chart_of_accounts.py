# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute():
	"""Setup default Chart of Accounts for Marketing Hub"""
	
	companies = frappe.get_all("Company", fields=["name", "abbr", "default_currency"])
	
	for company in companies:
		try:
			setup_marketing_accounts(company.name, company.abbr)
			print(f"Setup marketing accounts for company: {company.name}")
		except Exception as e:
			print(f"Error setting up accounts for {company.name}: {str(e)}")
			frappe.log_error(f"Marketing Accounts Setup Error for {company.name}", str(e))


def setup_marketing_accounts(company, abbr):
	"""Create marketing accounts under Indirect Expenses"""
	
	# Check if company has chart of accounts
	root_account = frappe.db.get_value("Account", {
		"company": company,
		"is_group": 1,
		"account_type": "Expense Account"
	}, "name")
	
	if not root_account:
		# Try to find Indirect Expenses
		root_account = frappe.db.get_value("Account", {
			"company": company,
			"account_name": ["in", ["Indirect Expenses", "Expenses", "Operating Expenses"]],
			"is_group": 1
		}, "name")
	
	if not root_account:
		print(f"No expense account found for company {company}, skipping")
		return
	
	# Check if Marketing Expenses already exists
	existing_marketing_account = frappe.db.get_value("Account", {
		"account_name": "Marketing Expenses",
		"company": company
	}, ["name", "is_group"], as_dict=True)
	
	if existing_marketing_account:
		# If it exists but is not a group, skip creating sub-accounts
		if not existing_marketing_account.is_group:
			print(f"Marketing Expenses exists as ledger account in {company}, using it directly")
			# Update Marketing Expense Categories to use this account
			update_expense_categories_with_single_account(company, existing_marketing_account.name)
			return
		else:
			marketing_group = existing_marketing_account.name
			print(f"Using existing Marketing Expenses group account: {marketing_group}")
	else:
		# Create Marketing Expenses group account
		marketing_group = create_account_if_not_exists({
			"account_name": "Marketing Expenses",
			"parent_account": root_account,
			"is_group": 1,
			"company": company,
			"account_type": "Expense Account"
		})
		print(f"Created Marketing Expenses group account: {marketing_group}")
	
	# Create sub-accounts for each marketing expense category
	marketing_accounts = [
		{
			"account_name": "Advertising Expense",
			"description": "Paid advertising campaigns across all platforms"
		},
		{
			"account_name": "Content Creation Expense",
			"description": "Content production, copywriting, design costs"
		},
		{
			"account_name": "Social Media Marketing",
			"description": "Social media campaigns and influencer partnerships"
		},
		{
			"account_name": "Email Marketing",
			"description": "Email campaign costs and marketing automation"
		},
		{
			"account_name": "SEO and SEM",
			"description": "Search engine optimization and marketing"
		},
		{
			"account_name": "Events and Trade Shows",
			"description": "Event sponsorships, trade shows, conferences"
		},
		{
			"account_name": "Print Media",
			"description": "Print advertising, brochures, catalogs"
		},
		{
			"account_name": "Influencer Marketing",
			"description": "Influencer partnerships and sponsorships"
		},
		{
			"account_name": "Agency and Consulting Fees",
			"description": "Marketing agency fees and consulting services"
		},
		{
			"account_name": "Marketing Software and Tools",
			"description": "Marketing software subscriptions and tools"
		},
		{
			"account_name": "Out of Home Advertising",
			"description": "Billboard, transit, and outdoor advertising"
		},
		{
			"account_name": "Public Relations",
			"description": "PR services, press releases, media relations"
		},
		{
			"account_name": "Market Research",
			"description": "Market research, surveys, focus groups"
		},
		{
			"account_name": "Other Marketing Expenses",
			"description": "Miscellaneous marketing costs"
		}
	]
	
	for account_data in marketing_accounts:
		create_account_if_not_exists({
			"account_name": account_data["account_name"],
			"parent_account": marketing_group,
			"is_group": 0,
			"company": company,
			"account_type": "Expense Account",
			"description": account_data["description"]
		})
	
	# Update Marketing Expense Categories with default accounts
	update_expense_categories_with_accounts(company)


def create_account_if_not_exists(account_data):
	"""Create account if it doesn't exist"""
	
	existing = frappe.db.get_value("Account", {
		"account_name": account_data["account_name"],
		"company": account_data["company"]
	}, "name")
	
	if existing:
		return existing
	
	account = frappe.get_doc({
		"doctype": "Account",
		**account_data
	})
	account.insert(ignore_permissions=True)
	return account.name


def update_expense_categories_with_accounts(company):
	"""Link Marketing Expense Categories to their default accounts"""
	
	category_account_mapping = {
		"Advertising": "Advertising Expense",
		"Content Creation": "Content Creation Expense",
		"Social Media": "Social Media Marketing",
		"Email Marketing": "Email Marketing",
		"SEO/SEM": "SEO and SEM",
		"Events": "Events and Trade Shows",
		"Print Media": "Print Media",
		"Influencer Marketing": "Influencer Marketing",
		"Agency Fees": "Agency and Consulting Fees",
		"Software Tools": "Marketing Software and Tools",
		"Out of Home (OOH)": "Out of Home Advertising",
		"PR & Communications": "Public Relations",
		"Market Research": "Market Research",
		"Other": "Other Marketing Expenses"
	}
	
	for category_name, account_name in category_account_mapping.items():
		# Get the category
		category = frappe.db.get_value("Marketing Expense Category", category_name, "name")
		if not category:
			continue
		
		# Get the account
		account = frappe.db.get_value("Account", {
			"account_name": account_name,
			"company": company
		}, "name")
		
		if account:
			# Update category with accounting account
			frappe.db.set_value(
				"Marketing Expense Category",
				category,
				"accounting_account",
				account,
				update_modified=False
			)
			print(f"Linked category '{category_name}' to account '{account_name}'")


def update_expense_categories_with_single_account(company, account_name):
	"""Link all Marketing Expense Categories to a single account when only one exists"""
	
	categories = frappe.get_all("Marketing Expense Category", fields=["name"])
	
	for category in categories:
		frappe.db.set_value(
			"Marketing Expense Category",
			category.name,
			"accounting_account",
			account_name,
			update_modified=False
		)
		print(f"Linked category '{category.name}' to single account '{account_name}'")
