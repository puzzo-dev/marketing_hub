# Marketing Hub Ledger Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Install/Update Marketing Hub
```bash
cd frappe-bench
bench --site your-site.local migrate
bench --site your-site.local build --app marketing_hub
```

### Step 2: Configure Chart of Accounts

1. Go to **Accounts > Chart of Accounts**
2. Under **Expenses**, create:
   - **Marketing Expenses** (Expense account, not a group)
   - Set company to your company

### Step 3: Configure Cost Center

1. Go to **Accounts > Cost Center**
2. Create **Marketing** under your main cost center
3. Enable it and set budget if needed

### Step 4: Configure Marketing Hub Settings

1. Go to **Marketing Hub > Settings > Marketing Hub Settings**
2. Select your company
3. Navigate to **Accounting & Ledger Settings** section:
   - ✅ Enable GL Entry (checked by default)
   - Select **Default Marketing Expense Account**: Marketing Expenses - [Company]
   - Select **Default Cost Center**: Marketing - [Company]
   - ✅ Validate Budget (optional, check if you want budget validation)

4. Navigate to **Connected DocTypes** section:
   - Click **Actions > Sync Connections** button
   - This will populate the connections table with integrated doctypes

5. Save the settings

### Step 5: Test Marketing Expense

1. Go to **Marketing Hub > Documents > Marketing Expense**
2. Click **New**
3. Fill in:
   - Company: Your company
   - Posting Date: Today
   - Campaign: (optional) select a campaign
   - Expense Category: Advertising
   - Expense Type: "Facebook Ads Test"
   - Expense Account: Marketing Expenses - [Company] (auto-filled)
   - Amount: 1000
   - Cost Center: Marketing - [Company] (auto-filled)
   - Is Paid: ✅ (check)
   - Payment Account: Select your bank account
   - Description: "Test marketing expense"

4. Save and Submit
5. Verify:
   - GL Entry Posted = ✅
   - Check **Reports > Accounting > General Ledger** to see entries

### Step 6: View Marketing Ledger Report

1. Go to **Marketing Hub Settings**
2. Click **Reports > View Marketing Ledger**
3. Set company filter
4. View all marketing expenses with their GL status

---

## Creating Your First Marketing Expense

### Scenario: Recording Google Ads Spend

**Monthly Google Ads invoice arrived: $5,000**

1. **Create Marketing Expense**:
   - Go to Marketing Hub > Marketing Expense > New
   - Company: My Company
   - Posting Date: 2026-01-18
   - Campaign: Q1 Digital Campaign
   - Expense Category: Advertising
   - Expense Type: Google Ads - January 2026
   - Expense Account: Marketing Expenses - MC
   - Amount: 5000
   - Currency: USD
   - Cost Center: Digital Marketing - MC
   - Is Paid: Yes (if already paid)
   - Payment Account: Company Bank - MC
   - Description: "Google Ads spend for Q1 digital campaign targeting product launches"

2. **Submit**:
   - Click Save
   - Click Submit
   - GL entries created automatically

3. **Verify in General Ledger**:
   - Go to Reports > General Ledger
   - Filter: Voucher No = your expense name (e.g., MEXP-2026-0001)
   - See:
     - Dr. Marketing Expenses - MC: 5000
     - Cr. Company Bank - MC: 5000

4. **Check Campaign Budget**:
   - Open your campaign
   - In client script console or via API:
     ```javascript
     frappe.call({
         method: 'marketing_hub.marketing_hub.utils.accounting.get_campaign_ledger_summary',
         args: {
             campaign: 'Q1 Digital Campaign',
             company: 'My Company'
         },
         callback: (r) => console.log(r.message)
     });
     ```

---

## Using Marketing Ledger Report

### View All Marketing Expenses

1. Go to **Marketing Hub Settings**
2. Click **Reports > View Marketing Ledger**
3. Filters:
   - Company: My Company
   - From Date: 2026-01-01
   - To Date: 2026-01-31
4. Click **Refresh**

### Export to Excel

1. Open Marketing Ledger report
2. Set your filters
3. Click **Menu > Export**
4. Select **Excel**
5. Download and analyze in Excel/Google Sheets

### Analyze by Campaign

1. Open Marketing Ledger report
2. Set Campaign filter: Your Campaign Name
3. View all expenses for that specific campaign
4. Check total row for campaign total spend

### Analyze by Category

1. Open Marketing Ledger report
2. Set Company and Date Range
3. Group by Expense Category (in your Excel export)
4. See spend breakdown:
   - Advertising: $25,000
   - Social Media: $10,000
   - Content Creation: $5,000

---

## Common Workflows

### Workflow 1: Monthly Marketing Budget Reconciliation

**Goal**: Ensure all marketing spend is recorded and matches bank statements

1. **Collect Invoices**:
   - Google Ads invoice: $5,000
   - Meta Ads invoice: $3,500
   - Canva subscription: $120
   - Agency fees: $2,000

2. **Create Marketing Expenses**:
   - One Marketing Expense per invoice
   - Link to relevant campaigns
   - Mark as paid with payment account

3. **Submit All**:
   - Submit each expense
   - GL entries created automatically

4. **Run Report**:
   - Marketing Ledger report
   - Filter: Current month
   - Verify total = $10,620

5. **Cross-Check**:
   - Compare with bank statement
   - Ensure all transactions recorded
   - Reconcile any differences

### Workflow 2: Campaign Budget Tracking

**Goal**: Monitor campaign spend against budget in real-time

1. **Set Campaign Budget**:
   - Open Campaign: "Summer Sale 2026"
   - Set Budget: $20,000
   - Save

2. **Record Expenses as Incurred**:
   - Week 1: Facebook Ads - $2,500
   - Week 2: Google Ads - $3,000
   - Week 3: Influencer payment - $5,000
   - Week 4: Content creation - $1,500

3. **Check Budget Status**:
   ```javascript
   // In browser console or via API
   frappe.call({
       method: 'marketing_hub.marketing_hub.utils.accounting.get_campaign_ledger_summary',
       args: {
           campaign: 'Summer Sale 2026',
           company: 'My Company'
       },
       callback: (r) => {
           let summary = r.message;
           console.log('Total Spent:', summary.total_expenses);
           console.log('Budget:', summary.budget);
           console.log('Remaining:', summary.remaining);
           console.log('Utilization:', summary.utilization_percentage + '%');
       }
   });
   ```

4. **Budget Alert**:
   - Total spent: $12,000
   - Remaining: $8,000
   - Utilization: 60%
   - Still on track!

### Workflow 3: Quarterly Marketing ROI Analysis

**Goal**: Calculate ROI for all marketing campaigns in Q1

1. **Export Marketing Ledger**:
   - Date Range: Q1 (Jan 1 - Mar 31)
   - Export to Excel

2. **Group by Campaign**:
   - Pivot table in Excel
   - Rows: Campaign
   - Values: Sum of Amount

3. **Get Revenue Data**:
   - From Sales Order/Invoice
   - Filter by Campaign attribution

4. **Calculate ROI**:
   ```
   ROI = (Revenue - Marketing Spend) / Marketing Spend * 100

   Example:
   Campaign: Summer Sale 2026
   Revenue: $100,000
   Marketing Spend: $20,000
   ROI = (100,000 - 20,000) / 20,000 * 100 = 400%
   ```

5. **Present to Management**:
   - Show marketing ledger totals
   - Show revenue attribution
   - Show ROI by campaign
   - Identify best performers

---

## Budget Setup (Optional)

### Enable Budget Validation

1. **Create Budget**:
   - Go to **Accounts > Budget**
   - New Budget
   - Fiscal Year: 2026
   - Cost Center: Marketing - MC
   - Budget Against: Cost Center

2. **Add Accounts**:
   - Account: Marketing Expenses - MC
   - Budget Amount: 100,000 (annual budget)

3. **Enable in Marketing Hub Settings**:
   - Go to Marketing Hub Settings
   - Accounting & Ledger Settings
   - ✅ Validate Budget

4. **Test**:
   - Try creating Marketing Expense that exceeds budget
   - System will throw error: "Budget exceeded for Marketing Expenses"

---

## Troubleshooting

### Issue: GL Entry Not Created

**Symptoms**: After submitting Marketing Expense, `gl_entry_posted` is not checked

**Solutions**:
1. Check Marketing Hub Settings:
   - Is "Enable GL Entry" checked?
   - Is "Default Expense Account" set?

2. Check Account Configuration:
   - Is expense account a group account? (should not be)
   - Is account disabled? (should be enabled)

3. Check Permissions:
   - Does user have permission to create GL Entry?

4. Check Error Log:
   - Go to Error Log
   - Look for GL entry errors
   - Fix the root cause

### Issue: Budget Validation Failing

**Symptoms**: Cannot submit expense due to budget exceeded error

**Solutions**:
1. Check Budget:
   - Go to Budget list
   - Find budget for your cost center
   - Is budget amount sufficient?

2. Increase Budget:
   - Edit budget
   - Increase budget amount
   - Save

3. Disable Validation (temporary):
   - Marketing Hub Settings
   - Uncheck "Validate Budget"
   - Save

### Issue: Connections Not Showing

**Symptoms**: Connected DocTypes table is empty

**Solutions**:
1. Click "Sync Connections":
   - Open Marketing Hub Settings
   - Click Actions > Sync Connections
   - Table should populate

2. Check DocType Installation:
   - Verify Marketing Hub Connection doctype exists
   - Run `bench migrate` if needed

---

## API Reference

### Get Campaign Ledger Summary

```python
from marketing_hub.marketing_hub.utils.accounting import get_campaign_ledger_summary

summary = get_campaign_ledger_summary(
    campaign="Summer Sale 2026",
    company="My Company"
)

print(summary)
# {
#   'campaign': 'Summer Sale 2026',
#   'company': 'My Company',
#   'total_expenses': 15000.0,
#   'budget': 20000.0,
#   'remaining': 5000.0,
#   'utilization_percentage': 75.0,
#   'over_budget': False
# }
```

### Get Marketing Ledger Summary

```python
from marketing_hub.marketing_hub.utils.accounting import get_marketing_ledger_summary

summary = get_marketing_ledger_summary(
    company="My Company",
    from_date="2026-01-01",
    to_date="2026-01-31"
)

print(summary)
# {
#   'company': 'My Company',
#   'from_date': '2026-01-01',
#   'to_date': '2026-01-31',
#   'total_expenses': 45000.0,
#   'expenses_by_category': [
#     {'expense_category': 'Advertising', 'total': 25000.0, 'count': 15},
#     {'expense_category': 'Social Media', 'total': 12000.0, 'count': 8}
#   ],
#   'category_count': 2
# }
```

### Create Marketing Expense Programmatically

```python
import frappe

expense = frappe.get_doc({
    "doctype": "Marketing Expense",
    "company": "My Company",
    "posting_date": "2026-01-18",
    "campaign": "Q1 Digital Campaign",
    "expense_category": "Advertising",
    "expense_type": "Facebook Ads",
    "expense_account": "Marketing Expenses - MC",
    "amount": 5000.0,
    "cost_center": "Marketing - MC",
    "is_paid": 1,
    "payment_account": "Bank Account - MC",
    "description": "Facebook ad campaign spend",
    "remarks": "Paid via credit card"
})

expense.insert()
expense.submit()

print(f"Marketing Expense created: {expense.name}")
print(f"GL Entry Posted: {expense.gl_entry_posted}")
```

---

## Best Practices

1. **Always Link to Campaigns**: Link expenses to campaigns for better tracking
2. **Use Descriptive Expense Types**: "Facebook Ads - Q1 2026" instead of just "Ads"
3. **Record Immediately**: Don't wait until month-end, record as expenses occur
4. **Reconcile Monthly**: Compare with bank statements monthly
5. **Review Budget Quarterly**: Adjust budgets based on performance
6. **Use Cost Centers**: Allocate to specific cost centers (Digital, Events, etc.)
7. **Add Remarks**: Include invoice numbers, payment methods in remarks
8. **Run Reports Regularly**: Weekly/monthly ledger reports for visibility

---

## Next Steps

After setting up the ledger:

1. **Train Team**: Show marketing team how to create expenses
2. **Set Budgets**: Create annual budgets for each campaign/cost center
3. **Automate**: Look into automating expense creation from ad platform APIs
4. **Dashboard**: Build a dashboard showing marketing spend trends
5. **Integrate**: Connect with Campaign performance to calculate ROI

---

## Support

- Documentation: See `docs/LEDGER_ACCOUNTING.md`
- Issues: GitHub Issues
- Community: Frappe Forum
- Email: support@yourcompany.com
