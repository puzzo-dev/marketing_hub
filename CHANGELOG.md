# Changelog

All notable changes to Marketing Hub will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0-beta.1] - 2026-03-12

### Added
- **Portal**: Vue 3 SPA with 18 pages built on frappe-ui
- **Dashboard**: KPI cards, spend/revenue trend chart, channel donut, leads trend, conversion funnel
- **Campaigns**: Create, manage, and detail view with analytics integration
- **OmniBlast**: Multi-channel campaign sender (3-step wizard: compose → channels → review)
- **Social Media**: Post management with network configuration (LinkedIn, Meta, Twitter, etc.)
- **Content Calendar**: Content management with editor and publishing workflow
- **Segments**: Customer segment builder with criteria-based filtering
- **Expenses**: Marketing expense tracking with budget vs actual charts
- **Analytics**: Performance analytics with spend vs revenue visualization
- **Tracking Links**: QR code / link generation system for OOH ads with click tracking
- **Leads Pipeline**: Marketing-attributed leads dashboard with UTM-based attribution
- **Agency Mode**: Client management, project tracking, agent layouts
- **Settings**: Company configuration, social integrations, marketing settings
- **30 DocTypes**: Full backend data model for marketing operations
- **35+ API endpoints**: Dashboard, campaigns, social, content, tracking, leads, expenses, segments, agency
- **Frappe splash screen**: Native Frappe-style loading screen before app mount

### Fixed
- FormControl inputs now use `type="autocomplete"` for Campaign/Segment/Template selectors
- Channel field names aligned with Social Media Network doctype (`is_active`, `network_name`, `network_type`)
- AxisChart migrated from legacy props API to new ECharts-based `config` prop
- Check field truthiness uses `Number(val) === 1` instead of JavaScript truthy (`!!"0"` bug)
- Migrated 26+ instances of `window.frappe.call` to frappe-ui `call()` (doesn't exist in portal context)

### Technical
- Frappe v15 compatible
- frappe-ui v0.1.54 with Vue 3, Pinia stores, Vue Router
- Tailwind CSS for styling
- Lucide icons throughout
- qrcode Python package for QR generation
