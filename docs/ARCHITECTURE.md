# Marketing Hub - Architecture Overview

## System Overview
Marketing Hub is a comprehensive marketing automation and analytics application built on the Frappe Framework. It enables businesses to manage multi-channel campaigns, track ad performance, and calculate ROAS (Return on Ad Spend) through direct integrations with ad platforms.

## Core Components

### 1. Campaign Management
- **Campaign**: The central entity grouping activities and tracking aggregated metrics.
- **Campaign Activity**: Individual execution units (e.g., Email Blast, Social Post) linked to a campaign.
- **Marketing Segment**: Dynamic audience lists built from ERPNext data (Leads, Contacts, Customers).

### 2. Content & Creative
- **Content Asset**: Repository for images, videos, and text copy.
- **Marketing Template**: Reusable message templates supporting Jinja variables.
- **Social Post**: Scheduled or immediate posts for social media platforms.

### 3. Integrations & Analytics
- **Ad Account**: Stores OAuth credentials for external platforms (Google, Meta, LinkedIn).
- **Analytics Connector**: Sync engine that fetches performance data.
- **Analytics Daily Log**: Granular daily performance records (Impressions, Clicks, Spend, Revenue).

### 4. Utilities
- **Omni Blast**: Unified executor for sending messages across multiple channels.
- **Attribution Engine**: Logic to link Leads/Sales to Campaigns via UTM parameters.

## Database Schema Structure

### Primary Doctypes
| Doctype | Purpose | Key Relationships |
| :--- | :--- | :--- |
| `Campaign` | Parent container | Has many `Campaign Activity` |
| `Campaign Activity` | Actionable item | Linked to `Campaign`, `Marketing Segment` |
| `Marketing Segment` | Audience definition | Filters on `Lead`/`Customer` |
| `Ad Account` | Credentials | Linked to `Analytics Connector` |
| `Analytics Daily Log` | Performance data | Linked to `Campaign`, `Ad Account` |

## Frontend Architecture
The application features a modern Single Page Application (SPA) portal for the "Desk" experience, built with:
- **Vue.js 3**: Progressive JavaScript framework.
- **Frappe UI**: Component library for consistent design.
- **TailwindCSS**: Utility-first styling.
- **Vue Router**: Client-side routing.

### Key Pages
- `Dashboard.vue`: High-level metrics and KPIs.
- `OmniBlast.vue`: Wizard for creating multi-channel blasts.
- `Segments.vue`: Visual builder for audience targeting.
- `Content.vue`: Digital asset management.
- `Expenses.vue`: Financial tracking usage.

## Integration Flows

### OAuth Handshake
1. User initiating connection from `Ad Account`.
2. Redirected to Platform (Google/Meta) via `get_authorization_url`.
3. Callback handler exchanges auth code for Access/Refresh tokens.

### Data Sync
1. `Analytics Connector` runs scheduled job (Hourly/Daily).
2. Fetches data via Platform API (e.g., Google Ads REST, Meta Graph API).
3. Creates/Updates `Analytics Daily Log` records.
4. Aggregates metrics back to `Campaign` via `api.py`.
