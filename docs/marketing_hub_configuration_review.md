# Marketing Hub Configuration Review

**Status**: ✅ Aligned with System Architecture
**Date**: January 25, 2026

## 1. Overview
The `Marketing Hub Settings` doctype serves as the central control panel for the application. Following the recent refactor to a **Tabbed Layout**, it is now organized to match the modular architecture of the system.

## 2. Setting Modules & Data Structure

### 🏠 General
*   **Purpose**: Core defaults and tracking logic.
*   **Key Fields**: `Agency Mode` (Toggles multi-client features), `Naming Series`, `UTM Tracking`.
*   **Architecture Alignment**: Supports the dual-mode nature (Single Company vs. Agency) defined in the project scope.

### 📣 Omni-Channel
*   **Purpose**: Enable/Disable communication channels.
*   **Key Fields**: `Email Blast`, `SMS Blast` (Relies on standard *SMS Settings*), `WhatsApp Blast` (Relies on *Frappe WhatsApp* app).
*   **Review**: Keeps the core lean by leveraging existing ERPNext/Frappe capabilities rather than duplicating gateway logic.

### 📱 Social Media
*   **Purpose**: Content publishing defaults.
*   **Key Fields**: `Auto Post` toggle, `Default Platforms` (Child Table).
*   **Review**: The fix to `Marketing Hub Social Platform` ensures database integrity.

### 🎯 Advertising
*   **Purpose**: Feature flags for ad platforms.
*   **Key Fields**: `Enable Google/Meta/LinkedIn/TikTok Ads`.
*   **Architecture Note**: Actual API credentials (Client ID/Secret) are stored in the **Ad Account** doctype, allowing multiple accounts per platform. This is the correct architecture for scalability.

### 📊 Analytics
*   **Purpose**: Data synchronization rules.
*   **Key Fields**: `Sync Frequency`, `Attribution Model`.
*   **Review**: Centralizes the schedule for the background jobs running in `analytics.py`.

### 💰 Accounting
*   **Purpose**: Financial integration with ERPNext General Ledger.
*   **Key Fields**:
    *   `Enable GL Entry`: Master toggle for posting costs.
    *   `Default Expense Account`: Where marketing spend is booked.
    *   `Default Cost Center`: For budget allocation.
*   **Review**: Provides the necessary link between "Marketing Spend" (Operational) and "General Ledger" (Financial).

### 🔔 Notification
*   **Purpose**: Alerting system.
*   **Key Fields**: `Notify Campaign Completion`, `Budget Alerts`.

## 3. Conclusion
The configuration structure is robust and consistent with the application's design:
*   **Global Toggles** are in *Settings*.
*   **Specific Credentials** are in *Master Data* (Ad Accounts, Connectors).
*   **Financial Logic** links directly to ERPNext Accounting.

The layout refactor to **Tabs** notably improves the user experience by reducing scroll fatigue and grouping related settings logically.
