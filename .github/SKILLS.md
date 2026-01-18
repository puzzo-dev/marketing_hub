# Marketing Hub - Required Skills & Domain Expertise

## Core Technical Skills

### Framework & Languages
- **Frappe Framework v15+**: Deep understanding of hooks, doc_events, scheduler_events, fixtures, custom fields
- **Python 3.12+**: Backend business logic, API integrations, data processing
- **JavaScript (ES6+)**: Client-side enhancements, form customization
- **Vue 3**: Dashboard components, real-time analytics visualization
- **frappe-ui**: Component library for consistent UI
- **frappe-charts**: Interactive data visualization

### Database & ORM
- **MariaDB/MySQL**: Query optimization, complex joins, aggregations
- **Frappe ORM**: frappe.get_all(), frappe.db.sql(), virtual doctypes
- **Data modeling**: Multi-company, multi-tenant architecture

## Marketing Domain Expertise

### Digital Marketing Fundamentals
- **Omni-channel marketing**: Orchestrating campaigns across 18+ channels (Email, WhatsApp, SMS, Push, Social, Ads, Traditional)
- **Attribution modeling**: UTM tracking, multi-touch attribution, conversion tracking
- **ROAS (Return on Ad Spend)**: Cost analysis, ROI calculation, performance metrics
- **Campaign management**: Planning, execution, monitoring, optimization
- **Marketing automation**: Trigger-based campaigns, drip sequences, behavioral targeting

### Channel-Specific Knowledge
- **Email marketing**: Deliverability, segmentation, A/B testing, templates
- **WhatsApp Business API**: Templates, opt-in/opt-out, interactive messages
- **SMS marketing**: Gateway integration, shortcodes, compliance (TCPA, GDPR)
- **Push notifications**: Web push, mobile push, segmentation
- **Social media marketing**: Content scheduling, engagement tracking, community management

### Advertising Platforms
- **Google Ads**: Campaigns, ad groups, keywords, bidding strategies, Quality Score
- **Meta Ads (Facebook/Instagram)**: Campaign objectives, audiences, creative optimization, Pixel tracking
- **LinkedIn Ads**: Sponsored content, InMail, lead gen forms, account-based marketing
- **TikTok Ads**: Video ads, creator marketplace, algorithm optimization
- **Twitter/X Ads**: Promoted tweets, trends, amplify
- **Reddit Ads**: Community targeting, conversation ads

### Analytics & Measurement
- **KPIs**: CTR, CPC, CPM, CPL, CPA, conversion rate, engagement rate
- **Attribution windows**: First-touch, last-touch, linear, time-decay
- **Funnel analysis**: Awareness → Consideration → Conversion → Retention
- **Cohort analysis**: Customer lifetime value, retention curves
- **A/B testing**: Statistical significance, confidence intervals

### Agency Business Model
- **Client management**: Multi-client operations, white-labeling, reporting
- **Package/subscription models**: Tiered pricing, feature limits, billing cycles
- **Resource allocation**: Campaign limits, channel access, budget management
- **SLAs (Service Level Agreements)**: Response times, deliverables, performance guarantees

## Integration Skills

### OAuth 2.0 & API Authentication
- **OAuth flows**: Authorization code, refresh tokens, token expiration handling
- **API authentication**: API keys, bearer tokens, webhook signatures
- **Secure storage**: Encrypted credentials, secret management

### Platform APIs
- **Google Ads API**: Campaign management, reporting, conversion tracking
- **Meta Graph API**: Page management, ad creation, insights
- **LinkedIn Marketing API**: Campaign creation, targeting, analytics
- **TikTok Marketing API**: Ad groups, creative management, reporting
- **Twitter API v2**: Tweet creation, media upload, analytics
- **WhatsApp Business API**: Message templates, webhooks, media handling
- **SMS gateways**: Twilio, Plivo, MessageBird integration

### Data Sync & ETL
- **Daily sync patterns**: Incremental updates, delta detection, conflict resolution
- **Rate limiting**: Exponential backoff, queue management, throttling
- **Error handling**: Retry logic, dead letter queues, alerting
- **Data transformation**: API response normalization, metric calculation

## Business Logic Patterns

### Attribution Engine
- **Priority-based attribution**: UTM params → Campaign links → Session data → Referrals
- **Lead source tagging**: Channel-Campaign format standardization
- **Conversion tracking**: Multi-step funnels, assisted conversions
- **Channel breakdown**: Performance comparison across channels

### Omni-Blast Execution
- **Segment targeting**: Dynamic audience building, deduplication
- **Template management**: Channel-specific templates, variable substitution
- **Scheduled execution**: Time zone handling, delivery windows
- **Results tracking**: Sent, delivered, opened, clicked, converted

### Auto-Post Scheduling
- **Queue management**: FIFO processing, priority queues
- **Platform-specific formatting**: Character limits, media requirements, hashtags
- **Posting windows**: Optimal timing, frequency capping
- **Approval workflows**: Draft → Review → Scheduled → Published

### Analytics Sync
- **Daily aggregation**: Date-based partitioning, incremental sync
- **Metric calculation**: Derived metrics (CTR, CPC, ROAS), YoY comparisons
- **Anomaly detection**: Spending spikes, performance drops
- **Connector management**: Active/inactive status, sync frequency

### Agency Mode
- **Subscription lifecycle**: Creation, renewal, expiration, grace periods
- **Limit enforcement**: Campaign caps, channel restrictions, overage handling
- **Client isolation**: Data segregation, permission boundaries
- **Dashboard aggregation**: Cross-client reporting, trends

## Architecture Patterns

### Event-Driven Design
- **Doc events**: on_update, before_save, after_insert triggers
- **Scheduler events**: Cron-based execution (daily, hourly, every 15 min)
- **Webhooks**: External platform notifications, two-way sync

### Multi-Tenancy
- **Company filtering**: Automatic company context in queries
- **Permission management**: Role-based access, user permissions
- **Data isolation**: Preventing cross-company data leakage

### Async Processing
- **Background jobs**: Long-running tasks (blasts, syncs, imports)
- **Queue management**: Redis-based job queues, workers
- **Progress tracking**: Real-time status updates, cancellation

### Caching Strategy
- **Redis caching**: Segment results, template rendering, API responses
- **Cache invalidation**: Time-based expiry, event-based clearing
- **Cache warming**: Pre-loading frequently accessed data

## Testing & Quality

### Unit Testing
- **Utils module testing**: Pure function testing, mocking external APIs
- **Edge cases**: Empty data, null values, invalid inputs
- **Assertions**: Expected outputs, error conditions

### Integration Testing
- **End-to-end workflows**: Campaign creation → Blast execution → Results tracking
- **API mocking**: Simulating platform responses, error scenarios
- **Database state**: Setup, execution, teardown, rollback

### Performance Testing
- **Load testing**: High-volume blasts, concurrent campaigns
- **Query optimization**: Index usage, query explain plans
- **Memory profiling**: Large dataset handling, memory leaks

## Documentation Requirements

### API Documentation
- **Endpoint specifications**: Request/response schemas, authentication
- **Error codes**: Standardized error handling, troubleshooting
- **Rate limits**: Request quotas, throttling behavior

### User Documentation
- **Setup guides**: Installation, configuration, initial setup
- **Feature tutorials**: Step-by-step workflows, screenshots
- **Best practices**: Optimization tips, common pitfalls

### Developer Documentation
- **Architecture diagrams**: System design, data flow
- **Code conventions**: Style guides, naming patterns
- **Extension guides**: Custom channels, platform integrations

## Compliance & Security

### Data Privacy
- **GDPR compliance**: Right to be forgotten, data portability, consent management
- **CCPA compliance**: California privacy rights, opt-out mechanisms
- **Data retention**: Automatic purging, archival strategies

### Marketing Regulations
- **CAN-SPAM**: Email compliance, unsubscribe links, sender identification
- **TCPA**: SMS/phone consent, do-not-call lists
- **CASL (Canada)**: Anti-spam legislation, consent requirements

### Security Best Practices
- **Input validation**: SQL injection prevention, XSS protection
- **API security**: Token rotation, IP whitelisting, request signing
- **Audit logging**: User actions, data changes, access logs

## Domain-Specific Terminology

### Marketing Lexicon
- **MQL (Marketing Qualified Lead)**: Lead meeting qualification criteria
- **SQL (Sales Qualified Lead)**: Lead ready for sales handoff
- **CAC (Customer Acquisition Cost)**: Total marketing spend ÷ new customers
- **LTV (Lifetime Value)**: Total revenue per customer over lifetime
- **Churn rate**: Percentage of customers lost over period
- **Engagement rate**: Interactions ÷ impressions × 100
- **Virality coefficient**: New users generated per existing user

### Platform Terminology
- **Pixel/Tag**: Tracking code for conversion measurement
- **Lookalike audience**: Audience similar to existing customers
- **Retargeting**: Ads shown to previous visitors
- **Frequency cap**: Maximum ad impressions per user per time period
- **Ad fatigue**: Declining performance from repeated exposure
- **Quality Score**: Google Ads metric for ad relevance
- **Relevance Score**: Meta's ad quality metric

## Project-Specific Context

### Current Implementation Status
- ✅ **Complete**: Attribution engine, omni-blast (email), agency mode, custom fields, hooks
- 🔧 **Stubs**: WhatsApp/SMS/Push blasts, social posting, analytics sync (all platform APIs)
- ⏳ **Pending**: 10 doctypes creation, Vue dashboard, real API integrations

### Key Doctypes
1. **Marketing Segment**: Audience definitions with dynamic filters
2. **Marketing Template**: Channel-specific message templates
3. **Social Post**: Scheduled posts with platform targeting
4. **Ad Account**: Platform credentials and OAuth tokens
5. **Analytics Connector**: Daily sync configuration
6. **Analytics Daily Log**: Time-series metrics storage
7. **Marketing Hub Setup**: Single doctype for global settings
8. **Agency Package**: Tiered subscription offerings
9. **Client Subscription**: Active client subscriptions
10. **Campaign Activity**: Child table for campaign execution

### Integration Priority
1. **High**: Email (✅ complete), WhatsApp Business API, Google Ads, Meta Ads
2. **Medium**: LinkedIn Ads, TikTok Ads, SMS gateways
3. **Low**: Twitter Ads, Reddit Ads, traditional channels

### Success Metrics
- **Attribution accuracy**: >90% of leads properly attributed
- **Blast execution time**: <5 minutes for 10K recipients
- **Analytics sync latency**: Daily updates within 1 hour of platform availability
- **Agency client limits**: 100% enforcement, zero overages
- **System uptime**: 99.5% availability

## Learning Resources

### Frappe Framework
- Frappe Framework Documentation: https://frappeframework.com/docs
- ERPNext Developer Guide: https://docs.erpnext.com/docs/developer
- Frappe School: https://frappe.school

### Marketing Platforms
- Google Ads API: https://developers.google.com/google-ads/api
- Meta Marketing API: https://developers.facebook.com/docs/marketing-apis
- LinkedIn Marketing: https://docs.microsoft.com/en-us/linkedin/marketing
- TikTok Business API: https://business-api.tiktok.com

### Marketing Concepts
- HubSpot Academy: Free marketing certification courses
- Google Analytics Academy: Web analytics and measurement
- Meta Blueprint: Facebook/Instagram marketing certification

---

**Note**: This is a complex, domain-specific application requiring both deep technical expertise in Frappe Framework and substantial marketing operations knowledge. Successful implementation requires understanding the "why" behind marketing workflows, not just the "how" of technical implementation.
