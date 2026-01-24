# Marketing Hub - Accounting & Financial Tracking

**Date**: January 24, 2026
**Status**: ✅ COMPLETE - Full Accounting Integration Implemented

## Overview

Marketing Hub now includes comprehensive accounting functionality to track all marketing expenses with proper integration into ERPNext's Chart of Accounts and General Ledger. This works globally in both in-house and agency mode.

---

## Features Implemented

### 1. Chart of Accounts Integration

**Automatic Account Setup**:
- Creates "Marketing Expenses" group account under Indirect Expenses
- Creates 14 sub-accounts for different expense categories:
  - Advertising Expense
  - Content Creation Expense
  - Social Media Marketing
  - Email Marketing
  - SEO and SEM
  - Events and Trade Shows
  - Print Media
  - Influencer Marketing
  - Agency and Consulting Fees
  - Marketing Software and Tools
  - Out of Home Advertising
  - Public Relations
  - Market Research
  - Other Marketing Expenses

**Auto-linking**:
- Marketing Expense Categories automatically linked to corresponding accounts
- Expense account auto-populated when selecting category

### 2. General Ledger Integration

**Automatic GL Entries**:
When Marketing Expense is submitted, GL entries are created:

**For Paid Expenses**:
```
Debit:  Marketing Expense Account (e.g., Advertising Expense)
Credit: Payment Account (Bank/Cash)
```

**For Unpaid Expenses**:
```
Debit:  Marketing Expense Account
Credit: Accounts Payable
```

**Features**:
- Automatic GL posting on submit
- Automatic GL reversal on cancel
- Cost Center assignment
- Project tracking
- Multi-currency support

### 3. Budget Tracking

**Campaign Budget Fields** (Custom Fields):
- `budget_amount` - Total allocated budget
- `total_spent` - Auto-calculated from expenses
- `budget_utilization` - Percentage spent
- `budget_remaining` - Remaining budget

**Budget Alerts**:
- Warning when expense exceeds campaign budget
- Real-time budget utilization tracking
- Budget vs Actual reports

### 4. Accounting Reports

#### Report 1: Marketing Expense Analysis
**Path**: Marketing Hub > Reports > Marketing Expense Analysis

**Features**:
- Filter by: Company, Date Range, Campaign, Category, Cost Center, Project
- Columns: Date, Expense ID, Campaign, Category, Amount, Payment Status, GL Status
- Chart: Bar chart showing top 10 expense categories
- Color-coded paid/unpaid status
- GL posting status indicator

#### Report 2: Campaign Budget vs Actual
**Path**: Marketing Hub > Reports > Campaign Budget vs Actual

**Features**:
- Filter by: Company, Campaign Status, Date Range
- Columns:
  - Budget Amount
  - Actual Spent
  - Variance (Budget - Actual)
  - Variance %
  - Budget Utilization %
  - Leads Generated
  - Cost per Lead
  - Revenue
  - ROI %
- Chart: Budget vs Actual comparison (bar chart)
- Color coding:
  - Red: Over budget
  - Orange: >80% utilization
  - Green: Within budget

### 5. Settings & Configuration

**Marketing Hub Settings - Accounting Section**:
- `enable_gl_entry` - Toggle GL posting (default: enabled)
- `default_expense_account` - Default marketing expense account
- `default_cost_center` - Default cost center
- `default_payable_account` - Account for unpaid expenses
- `validate_budget` - Validate against campaign budget (default: enabled)
- `enable_budget_alerts` - Send alerts when over budget
- `auto_reconcile_expenses` - Auto-reconcile with bank statements
- `expense_approval_required` - Require approval workflow

---

## Usage Guide

### Creating a Marketing Expense

1. **Navigate**: Marketing Hub > Marketing Expense > New

2. **Fill Required Fields**:
   - Company (required)
   - Posting Date (default: today)
   - Expense Category (required) - Auto-sets expense account
   - Amount (required)
   - Campaign (optional) - For budget tracking

3. **Accounting Fields**:
   - Expense Account - Auto-filled from category
   - Cost Center - Defaults from company
   - Project - Optional project assignment

4. **Payment Details**:
   - Is Paid checkbox
   - Payment Account (required if paid) - Bank/Cash account

5. **Submit**:
   - Click "Submit" to post expense
   - GL entries created automatically
   - Campaign budget updated
   - Budget alerts shown if exceeded

### Viewing Expenses

**List View**:
- Marketing Hub > Marketing Expense
- Filter by: Company, Campaign, Category, Date, Payment Status

**Reports**:
- Marketing Hub > Reports > Marketing Expense Analysis
- Marketing Hub > Reports > Campaign Budget vs Actual

**General Ledger**:
- Accounts > General Ledger
- Filter by: Account = Marketing Expense Account
- View all GL entries for marketing expenses

### Budget Management

1. **Set Campaign Budget**:
   - Open Campaign
   - Go to "Budget & Tracking" section
   - Set Budget Amount
   - Save

2. **Track Spending**:
   - `total_spent` updates automatically when expenses submitted
   - `budget_utilization` shows percentage used
   - `budget_remaining` shows available budget

3. **Budget Alerts**:
   - Orange warning when approaching budget (>80%)
   - Red alert when exceeding budget
   - Alerts shown on expense submission

---

## API Reference

### Utility Functions

**File**: `marketing_hub/utils/accounting.py`

#### make_gl_entries(doc, cancel=False)
```python
from marketing_hub.utils.accounting import make_gl_entries

# Create GL entries for Marketing Expense
make_gl_entries(marketing_expense_doc, cancel=False)
```

#### validate_accounting_entries(doc)
```python
from marketing_hub.utils.accounting import validate_accounting_entries

# Validate accounts before submission
validate_accounting_entries(marketing_expense_doc)
```

#### check_budget_exceeded(doc)
```python
from marketing_hub.utils.accounting import check_budget_exceeded

# Check if expense exceeds campaign budget
is_exceeded = check_budget_exceeded(marketing_expense_doc)
```

#### update_campaign_spent_amount(doc)
```python
from marketing_hub.utils.accounting import update_campaign_spent_amount

# Update campaign's total_spent field
update_campaign_spent_amount(marketing_expense_doc)
```

#### get_expense_account_from_category(category, company)
```python
from marketing_hub.utils.accounting import get_expense_account_from_category

# Get expense account from category
account = get_expense_account_from_category("Advertising", "My Company")
```

---

## Database Schema

### Marketing Expense Fields

**Accounting Fields**:
```json
{
  "expense_account": "Link to Account (required)",
  "amount": "Currency (required)",
  "currency": "Link to Currency",
  "cost_center": "Link to Cost Center",
  "project": "Link to Project",
  "is_paid": "Check (default: 0)",
  "payment_account": "Link to Account (required if is_paid)",
  "journal_entry": "Link to Journal Entry (read-only)",
  "gl_entry_posted": "Check (read-only)"
}
```

### Campaign Custom Fields

**Budget Tracking**:
```json
{
  "budget_amount": "Currency",
  "total_spent": "Currency (read-only)",
  "budget_utilization": "Percent (read-only)",
  "budget_remaining": "Currency (read-only)"
}
```

---

## Accounting Workflow

### Expense Lifecycle

1. **Draft**:
   - Expense created, not submitted
   - No GL entries
   - Can be edited/deleted

2. **Submitted**:
   - Expense submitted
   - GL entries created
   - Campaign budget updated
   - Cannot be edited

3. **Cancelled**:
   - Expense cancelled
   - GL entries reversed
   - Campaign budget recalculated
   - Cannot be resubmitted

### GL Entry Structure

**Expense Posting**:
```
Account                         Debit    Credit
--------------------------------------------
Marketing Expenses - Ads        1000
  Bank Account                            1000

Remarks: Category: Advertising | Campaign: Summer Sale | Type: Google Ads
Voucher Type: Marketing Expense
Voucher No: MEXP-2026-00001
```

**With Cost Center**:
```
Account                         Debit    Credit   Cost Center
-----------------------------------------------------------
Marketing Expenses - Ads        1000              Marketing
  Bank Account                            1000     Marketing
```

---

## Agency Mode

**Multi-Company Support**:
- Each company has separate Chart of Accounts
- Marketing accounts created per company
- Expenses tracked per company
- Reports filtered by company

**Client Tracking**:
- Campaign.client field links to Customer
- Track expenses per client in agency mode
- Client-specific budget tracking
- Client-wise profitability reports

**Permissions**:
- Marketing Manager: Full access to all expenses
- Marketing User: Read-only access
- Accounts Manager: View accounting reports
- System Manager: Full administrative access

---

## Configuration Examples

### Example 1: Setup for New Company

```python
# Run this in Frappe console
from marketing_hub.patches.setup_marketing_chart_of_accounts import setup_marketing_accounts

company = "My New Company"
abbr = frappe.get_value("Company", company, "abbr")

setup_marketing_accounts(company, abbr)
# Creates all marketing accounts and links categories
```

### Example 2: Create Expense with GL Posting

```python
expense = frappe.get_doc({
    "doctype": "Marketing Expense",
    "company": "My Company",
    "posting_date": frappe.utils.today(),
    "campaign": "Summer Sale 2026",
    "expense_category": "Advertising",
    "expense_type": "Google Ads",
    "amount": 5000,
    "currency": "USD",
    "is_paid": 1,
    "payment_account": "Cash - MC",
    "remarks": "Google Ads campaign for summer sale"
})
expense.insert()
expense.submit()  # GL entries created automatically
```

### Example 3: Check Campaign Budget Status

```python
campaign = frappe.get_doc("Campaign", "Summer Sale 2026")

print(f"Budget: {campaign.budget_amount}")
print(f"Spent: {campaign.total_spent}")
print(f"Remaining: {campaign.budget_remaining}")
print(f"Utilization: {campaign.budget_utilization}%")
```

---

## Troubleshooting

### Issue 1: GL Entries Not Created

**Symptom**: Marketing Expense submitted but gl_entry_posted = 0

**Solutions**:
1. Check `enable_gl_entry` in Marketing Hub Settings
2. Verify expense_account is valid and not a group account
3. Verify payment_account (if is_paid) is Bank/Cash type
4. Check error log: Accounting > Error Log

### Issue 2: Marketing Accounts Not Created

**Symptom**: No marketing accounts in Chart of Accounts

**Solutions**:
1. Run patch manually:
   ```bash
   bench --site [site] execute marketing_hub.patches.setup_marketing_chart_of_accounts.execute
   ```
2. Check if Indirect Expenses exists for company
3. Create accounts manually if needed

### Issue 3: Budget Not Updating

**Symptom**: Campaign.total_spent not updating

**Solutions**:
1. Check if expenses are submitted (not draft)
2. Verify campaign field is filled in expense
3. Manually trigger update:
   ```python
   from marketing_hub.utils.accounting import update_campaign_spent_amount
   expense = frappe.get_doc("Marketing Expense", "MEXP-2026-00001")
   update_campaign_spent_amount(expense)
   ```

### Issue 4: Duplicate GL Entries

**Symptom**: Multiple GL entries for same expense

**Solutions**:
1. Check gl_entry_posted flag before creating entries
2. Cancel and re-submit if duplicates exist
3. Check hooks.py for duplicate doc_events

---

## Performance Considerations

**Optimization Tips**:

1. **Use Filters in Reports**:
   - Always filter by company and date range
   - Limit results to necessary data

2. **Batch Processing**:
   - Import expenses in batches of 100-500
   - Use background jobs for large imports

3. **Indexing**:
   - Expense account indexed
   - Campaign indexed
   - Posting date indexed

4. **Caching**:
   - Marketing Hub Settings cached
   - Account details cached
   - Category-account mapping cached

---

## Security & Permissions

**Role-Based Access**:

| Role                | Create | Read | Submit | Cancel | Delete |
|---------------------|--------|------|--------|--------|--------|
| Marketing Manager   | ✓      | ✓    | ✓      | ✓      | ✓      |
| Marketing User      | ✓      | ✓    | ✗      | ✗      | ✗      |
| Accounts Manager    | ✗      | ✓    | ✗      | ✗      | ✗      |
| System Manager      | ✓      | ✓    | ✓      | ✓      | ✓      |

**Data Isolation**:
- Company-based access control
- Campaign-based filtering in agency mode
- Row-level security enforced

---

## Integration with ERPNext

**Connected Modules**:

1. **Accounts**:
   - Chart of Accounts
   - General Ledger
   - Cost Center
   - Project

2. **CRM**:
   - Campaign
   - Lead (for ROI calculation)
   - Opportunity (for revenue tracking)

3. **Selling**:
   - Sales Order (for revenue attribution)
   - Customer (for client tracking in agency mode)

**Data Flow**:
```
Marketing Expense (Submit)
  ↓
GL Entry Created
  ↓
Campaign Budget Updated
  ↓
Lead → Opportunity → Sales Order
  ↓
ROI Calculated in Reports
```

---

## Future Enhancements

**Planned Features**:
1. ✅ Multi-currency expense tracking
2. ✅ Budget alerts via email/notification
3. ⏳ Auto-reconciliation with bank statements
4. ⏳ Expense approval workflow
5. ⏳ Advanced budget allocation (monthly, quarterly)
6. ⏳ Cash flow forecasting for marketing
7. ⏳ Integration with payment gateways
8. ⏳ Expense categorization using AI

---

## Conclusion

Marketing Hub now provides enterprise-grade accounting functionality with:
- ✅ Full GL integration
- ✅ Automated account setup
- ✅ Budget tracking and alerts
- ✅ Comprehensive reports
- ✅ Multi-company support
- ✅ Agency mode support

All marketing spends are properly tracked in ERPNext's accounting system, providing complete financial visibility and control.

