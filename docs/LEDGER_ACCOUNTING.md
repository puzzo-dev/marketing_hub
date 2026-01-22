# Marketing Hub Ledger & Accounting Integration

## Overview
This document describes the ledger and accounting functionality added to Marketing Hub, enabling proper financial tracking of all marketing expenses and integration with ERPNext's General Ledger system.

## New DocTypes Created

### 1. Marketing Expense
**Purpose**: Track all marketing expenses with proper accounting integration

**Key Features**:
- Submittable document with GL entry creation
- Categorized expenses (Advertising, Content, Social Media, etc.)
- Direct link to campaigns for budget tracking
- Automatic GL entries on submit/cancel
- Payment tracking (paid/unpaid status)
- Cost center and project allocation
- Budget validation support

**Fields**:
- `naming_series`: Auto-naming (MEXP-.YYYY.-)
- `company`: Link to Company
- `posting_date`: Date of expense
- `campaign`: Link to Campaign (optional)
- `cost_center`: Link to Cost Center
- `project`: Link to Project (optional)
- `expense_category`: Select (Advertising, Content Creation, Social Media, etc.)
- `expense_type`: Data (descriptive name)
- `description`: Text Editor
- `expense_account`: Link to Account (required)
- `amount`: Currency
- `currency`: Link to Currency
- `is_paid`: Check (paid status)
- `payment_account`: Link to Account (for paid expenses)
- `journal_entry`: Link to Journal Entry (read-only)
- `gl_entry_posted`: Check (GL status indicator)
- `remarks`: Small Text

**Controllers** (`marketing_expense.py`):
```python
class MarketingExpense(Document):
    def validate(self):
        self.validate_accounts()
        self.set_currency()

    def on_submit(self):
        self.make_gl_entries()

    def on_cancel(self):
        self.make_gl_entries(cancel=True)

    def make_gl_entries(self, cancel=False):
        """Create GL entries using ERPNext patterns"""
        # Debit: Marketing Expense Account
        # Credit: Payment Account (if paid)
```

**Permissions**:
- System Manager: Full access
- Marketing Manager: Create, submit, amend, cancel
- Marketing User: Read only

---

### 2. Marketing Hub Connection
**Purpose**: Track which DocTypes are integrated/connected to Marketing Hub

**Fields**:
- `doctype_name`: Data (DocType name)
- `integration_type`: Select (Source, Target, Bidirectional)
- `status`: Select (Active, Inactive, Pending)
- `last_synced`: Datetime
- `description`: Text

**Integration Types**:
- **Source**: Marketing Hub pushes data to this DocType (e.g., Campaign → Lead)
- **Target**: Marketing Hub receives data from this DocType (e.g., Journal Entry → Marketing Hub)
- **Bidirectional**: Two-way sync (e.g., Contact ↔ Marketing Hub)

**Default Connections**:
1. Campaign - Source - Marketing campaigns and initiatives
2. Social Post - Source - Social media posts and scheduling
3. Marketing Expense - Target - Marketing expense tracking
4. Lead - Target - Leads from campaigns
5. Contact - Bidirectional - Contact management
6. Email Queue - Target - Email blast campaigns
7. Journal Entry - Target - Accounting entries
8. GL Entry - Target - General ledger tracking

---

## Marketing Hub Settings Updates

### New Section: Accounting & Ledger Settings

**Fields Added**:
1. `enable_gl_entry` (Check): Enable/disable GL entry creation (default: 1)
2. `default_expense_account` (Link to Account): Default marketing expense account
3. `default_cost_center` (Link to Cost Center): Default cost center for marketing
4. `validate_budget` (Check): Enable budget validation (default: 1)

### New Section: Connected DocTypes

**Fields Added**:
1. `connected_doctypes` (Table): Child table showing all connected DocTypes

**New Methods**:
```python
def validate_accounting_settings(self):
    """Validate expense account is not a group account"""

def load_connected_doctypes(self):
    """Auto-load connections on document load"""

def sync_connected_doctypes(self):
    """Sync and populate connected DocTypes"""
```

**New Whitelisted Method**:
```python
@frappe.whitelist()
def sync_connections(docname):
    """Sync connected doctypes (callable from UI)"""
```

---

## Utility Module: accounting.py

**Location**: `marketing_hub/utils/accounting.py`

### Key Functions:

#### 1. `make_marketing_gl_entry()`
Create GL entries for marketing expenses with ERPNext integration.

```python
make_marketing_gl_entry(
    voucher_type="Campaign",
    voucher_no="CAMP-0001",
    company="My Company",
    posting_date="2026-01-18",
    expense_account="Marketing Expenses - MC",
    amount=5000.0,
    payment_account="Bank - MC",  # Optional
    cost_center="Marketing - MC",
    project="Q1 Campaign",
    campaign="CAMP-0001",
    remarks="Facebook Ads Spend",
    cancel=False
)
```

**Features**:
- Automatic account fetching from Marketing Hub Settings
- Budget validation integration
- Debit/Credit entry creation
- Support for paid/unpaid expenses
- Accounting dimension support

#### 2. `get_campaign_ledger_summary(campaign, company)`
Get ledger summary for a specific campaign.

**Returns**:
```json
{
  "campaign": "CAMP-0001",
  "company": "My Company",
  "total_expenses": 15000.0,
  "budget": 20000.0,
  "remaining": 5000.0,
  "utilization_percentage": 75.0,
  "over_budget": false
}
```

#### 3. `get_marketing_ledger_summary(company, from_date, to_date)`
Get overall marketing ledger summary.

**Returns**:
```json
{
  "company": "My Company",
  "from_date": "2026-01-01",
  "to_date": "2026-01-31",
  "total_expenses": 45000.0,
  "expenses_by_category": [
    {"expense_category": "Advertising", "total": 25000.0, "count": 15},
    {"expense_category": "Social Media", "total": 12000.0, "count": 8},
    {"expense_category": "Content Creation", "total": 8000.0, "count": 5}
  ],
  "category_count": 3
}
```

---

## Marketing Ledger Report

**Type**: Script Report
**Ref DocType**: Marketing Expense
**Location**: `marketing_hub/report/marketing_ledger/`

### Columns:
1. Posting Date
2. Expense ID (Link)
3. Campaign (Link)
4. Category
5. Type
6. Account (Link)
7. Cost Center (Link)
8. Project (Link)
9. Amount (Currency)
10. Currency
11. Paid (Check)
12. Payment Account (Link)
13. GL Posted (Check)
14. Remarks

### Filters:
- Company (required)
- From Date
- To Date
- Campaign
- Expense Category
- Cost Center
- Project
- Expense Account

### Features:
- Total row for amount
- Sortable by all columns
- Export to Excel/PDF
- Role-based access (System Manager, Marketing Manager, Accounts Manager)

---

## UI Enhancements

### Marketing Hub Settings Form

**New Buttons**:
1. **Sync Connections** (Actions menu): Manually sync connected DocTypes
2. **View Marketing Ledger** (Reports menu): Quick access to ledger report (shown when GL entry enabled)

**Client Script Updates** (`marketing_hub_settings.js`):
```javascript
// Auto-require expense account when GL enabled
enable_gl_entry: function(frm) {
    frm.toggle_reqd('default_expense_account', frm.doc.enable_gl_entry);
}

// Auto-fetch expense account on company change
company: function(frm) {
    // Fetch default expense account
}

// Sync connections button
sync_connections: function(frm) {
    // Call sync_connections method
}
```

---

## GL Entry Pattern

### How It Works:

1. **Marketing Expense Created**:
   - User creates Marketing Expense document
   - Links to campaign, sets amount, category, accounts
   - Selects if paid or unpaid

2. **On Submit**:
   ```python
   def on_submit(self):
       self.make_gl_entries()
   ```

   Creates two GL entries:
   - **Debit**: Marketing Expense Account (increases expense)
   - **Credit**: Payment Account (decreases cash/bank) [if paid]

3. **GL Entry Structure**:
   ```python
   {
       "posting_date": "2026-01-18",
       "account": "Marketing Expenses - MC",
       "debit": 5000.0,
       "voucher_type": "Marketing Expense",
       "voucher_no": "MEXP-2026-0001",
       "company": "My Company",
       "cost_center": "Marketing - MC",
       "project": "Q1 Campaign",
       "remarks": "Facebook Ads Spend"
   }
   ```

4. **Budget Validation**:
   - If `validate_budget` enabled in settings
   - Calls ERPNext's `validate_expense_against_budget()`
   - Throws error if over budget

5. **On Cancel**:
   ```python
   def on_cancel(self):
       self.make_gl_entries(cancel=True)
   ```

   Reverses the GL entries.

---

## Usage Examples

### Example 1: Record Facebook Ads Spend

```python
# Create Marketing Expense
expense = frappe.get_doc({
    "doctype": "Marketing Expense",
    "company": "My Company",
    "posting_date": "2026-01-18",
    "campaign": "Summer Sale 2026",
    "expense_category": "Advertising",
    "expense_type": "Facebook Ads",
    "expense_account": "Marketing Expenses - MC",
    "amount": 2500.0,
    "cost_center": "Marketing - MC",
    "is_paid": 1,
    "payment_account": "Bank Account - MC",
    "description": "Facebook ad campaign for summer sale",
    "remarks": "Paid via company credit card"
})
expense.insert()
expense.submit()

# GL entries created automatically:
# Dr. Marketing Expenses - MC: 2500.0
# Cr. Bank Account - MC: 2500.0
```

### Example 2: Get Campaign Budget Status

```python
from marketing_hub.marketing_hub.utils.accounting import get_campaign_ledger_summary

summary = get_campaign_ledger_summary("Summer Sale 2026", "My Company")

# Returns:
# {
#   "total_expenses": 15000.0,
#   "budget": 20000.0,
#   "remaining": 5000.0,
#   "utilization_percentage": 75.0,
#   "over_budget": False
# }
```

### Example 3: View Marketing Ledger Report

1. Navigate to Marketing Hub Settings
2. Click "View Marketing Ledger" button
3. Set filters (company, date range, campaign)
4. View all marketing expenses with GL status
5. Export to Excel for analysis

---

## Integration with ERPNext Accounting

### Chart of Accounts Setup

**Recommended Account Structure**:
```
Assets
  └─ Current Assets
      └─ Bank Accounts
Expenses
  └─ Direct Expenses
      └─ Marketing Expenses (set as default_expense_account)
          ├─ Advertising Expenses
          ├─ Social Media Marketing
          ├─ Content Creation
          ├─ SEO/SEM Expenses
          └─ Other Marketing Expenses
```

### Cost Center Setup

**Recommended Structure**:
```
Main Company
  └─ Marketing Department (set as default_cost_center)
      ├─ Digital Marketing
      ├─ Traditional Marketing
      └─ Events & Promotions
```

### Budget Setup

1. Create Budget for Marketing Cost Center
2. Set budget amounts per account
3. Enable `validate_budget` in Marketing Hub Settings
4. Marketing Expense will validate against budget on submit

---

## Permissions & Security

### Marketing Expense
- **System Manager**: Full access
- **Marketing Manager**: Create, submit, amend, cancel, read, export
- **Marketing User**: Read, export
- **Accounts Manager**: Read, report, export

### Marketing Hub Settings
- **System Manager**: Full access
- **Marketing Manager**: Read, write, sync connections

### Marketing Ledger Report
- **System Manager**: Full access
- **Marketing Manager**: Read, export
- **Accounts Manager**: Read, export

---

## Database Schema

### Marketing Expense Table
```sql
CREATE TABLE `tabMarketing Expense` (
  `name` varchar(140) PRIMARY KEY,
  `company` varchar(140),
  `posting_date` date,
  `campaign` varchar(140),
  `cost_center` varchar(140),
  `project` varchar(140),
  `expense_category` varchar(140),
  `expense_type` varchar(140),
  `expense_account` varchar(140),
  `amount` decimal(18,6),
  `currency` varchar(140),
  `is_paid` tinyint(1),
  `payment_account` varchar(140),
  `gl_entry_posted` tinyint(1),
  `docstatus` tinyint(1),
  INDEX idx_company (company),
  INDEX idx_campaign (campaign),
  INDEX idx_posting_date (posting_date),
  INDEX idx_docstatus (docstatus)
);
```

### Marketing Hub Connection Table
```sql
CREATE TABLE `tabMarketing Hub Connection` (
  `name` varchar(140) PRIMARY KEY,
  `parent` varchar(140),
  `parentfield` varchar(140),
  `parenttype` varchar(140),
  `doctype_name` varchar(140),
  `integration_type` varchar(140),
  `status` varchar(140),
  `last_synced` datetime,
  INDEX idx_parent (parent)
);
```

---

## Testing Checklist

### Marketing Expense
- [ ] Create Marketing Expense without campaign
- [ ] Create Marketing Expense with campaign
- [ ] Submit expense and verify GL entries created
- [ ] Cancel expense and verify GL entries reversed
- [ ] Test budget validation (over budget)
- [ ] Test with paid/unpaid expenses
- [ ] Verify cost center allocation
- [ ] Test project allocation

### Marketing Hub Settings
- [ ] Set default expense account
- [ ] Set default cost center
- [ ] Enable/disable GL entry
- [ ] Enable/disable budget validation
- [ ] Sync connections manually
- [ ] Verify connections table populated
- [ ] View Marketing Ledger report

### Marketing Ledger Report
- [ ] Run report with company filter
- [ ] Test date range filters
- [ ] Filter by campaign
- [ ] Filter by expense category
- [ ] Export to Excel
- [ ] Verify total row calculation

---

## Future Enhancements

1. **Budget Alerts**: Send notifications when campaign reaches 80% budget
2. **Multi-Currency Support**: Handle foreign currency expenses
3. **Expense Approvals**: Add approval workflow for large expenses
4. **Recurring Expenses**: Support for subscription-based marketing tools
5. **Expense Allocation**: Split expenses across multiple campaigns
6. **ROI Calculation**: Compare expenses with campaign revenue
7. **Vendor Integration**: Link expenses to suppliers
8. **Payment Tracking**: Integrate with Payment Entry
9. **Tax Support**: Handle GST/VAT on marketing expenses
10. **Dashboard**: Visual summary of marketing spend by category/time

---

## Support & Documentation

- **User Guide**: See Marketing Hub documentation
- **Developer Guide**: See this document
- **API Reference**: `marketing_hub.marketing_hub.utils.accounting`
- **Report Issues**: GitHub Issues
- **Community**: Frappe Forum

---

## Changelog

### Version 1.0.0 (2026-01-18)
- Initial release
- Marketing Expense DocType
- Marketing Hub Connection tracking
- Accounting utility functions
- Marketing Ledger report
- GL entry integration
- Budget validation support
