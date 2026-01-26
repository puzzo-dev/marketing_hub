# Marketing Hub - Verification User Story

**Role**: Marketing Manager / System User
**Goal**: Validate the end-to-end flow of the Marketing Hub application, ensuring all components (Desk UI, Portal, Integrations, backend) work cohesively.

## Scenario: The "Summer Sale 2026" Campaign

> As a Marketing Manager, I need to launch a multi-channel campaign for the upcoming Summer Sale, track its performance across Google and Meta, and report on the ROI to my stakeholders.

---

### Phase 1: Setup & Configuration (Standard Desk)
**Workspace**: `/app/marketing-settings`

1.  **Check Configuration**:
    *   Navigate to **Marketing Settings** workspace.
    *   Open **Marketing Hub Settings**. Ensure "Enable SMS Blast" and "Enable Email Blast" are checked.
    *   Verify **Master Data**: Click on links for **Blast Type**, **Media Type**, and **Post Type** to confirm they are populated with defaults (e.g., 'Email', 'Image', 'Standard Post').

2.  **Connect Accounts**:
    *   Switch to (`/app/marketing-connect`).
    *   Open **Ad Account**. Verify your Google Ads account shows "Active".
    *   Open **Analytics Connector**. Confirm the 'Google Ads Sync' connector is scheduled (Next Sync Date is set).

---

### Phase 2: Campaign & Content (Portal UI)
**URL**: `/marketing` (Desk App)

3.  **Create Campaign**:
    *   On the **Dashboard**, click **New Campaign** (Quick Action).
    *   Title: "Summer Sale 2026".
    *   Budget: $5,000.
    *   Dates: June 1st - June 30th.
    *   *Effect*: Campaign is created and visible in the Active Campaigns list.

4.  **Prepare Assets**:
    *   Navigate to **Content** in the sidebar.
    *   Upload a banner image (`summer_banner.jpg`).
    *   Tag it as "Summer", "Sale".
    *   *Effect*: Asset appears in the library with thumbnail.

5.  **Define Audience**:
    *   Go to **Segments**.
    *   Create a new Segment: "High Value Customers".
    *   Filter: `Total Spend > 1000`.
    *   *Check*: The "Live Preview" shows a count of matching customers.

---

### Phase 3: Execution (Omni Blast)
**URL**: `/marketing/blast/new`

6.  **Launch Blast**:
    *   Select Campaign: "Summer Sale 2026".
    *   Select Segment: "High Value Customers".
    *   Channel: Select **Email**.
    *   Content: Pick the "Summer Sale Template" and attach `summer_banner.jpg`.
    *   Action: Click **Send Now**.
    *   *Effect*: A `Campaign Activity` and multiple `Communication` logs are created in the backend.

---

### Phase 4: Financials & Analytics (Desk & Portal)

7.  **Track Expenses** (Portal):
    *   Go to **Expenses**.
    *   Log a manual expense: "Graphic Design Agency" - $500.
    *   *Check*: The "Budget Utilized" bar for the campaign increases.

8.  **Review Performance** (Standard Desk):
    *   Go to **Marketing Hub** workspace (`/app/marketing-hub`).
    *   Click on **ROAS Analysis** shortcut.
    *   *Check*: The report loads data. Verify the "Actual ROAS" vs "Target ROAS" chart is rendered.

9.  **Deep Dive** (Portal):
    *   Go to **Analytics** page.
    *   Review the "Channel Attribution" chart.
    *   *Effect*: Confirm Google Ads and Email attributes are displayed correctly.

---

### Verification Checklist
- [ ] All 4 Workspaces (`Hub`, `Connect`, `Operations`, `Settings`) load without error.
- [ ] New Doctypes (`Blast Type` etc.) are accessible from Settings.
- [ ] Portal Dashboard loads stats from `api.get_dashboard_data`.
- [ ] `Omni Blast` wizard completes successfully.
- [ ] Reports (`ROAS Analysis`) render data.
