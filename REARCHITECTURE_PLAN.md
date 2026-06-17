# Marketing Hub Campaign Engine Re-Architecture Plan

## Objective
Separate channel-specific logic from orchestration. Each campaign mechanism is a standalone DocType, orchestrated by a unified `Campaign Engine` child table. Omni Blast becomes a pure orchestrator.

## Guiding Principles
- **No functional overlap** — reuse existing ERPNext/Frappe DocTypes where they exist
- **Single responsibility** — each engine handles its own channel logic independently
- **Zero channel logic in Omni Blast** — orchestrator only dispatches and aggregates
- **OOH vendors are records, not DocTypes** — new vendors = new records in `OOH Vendor`

---

## Architecture

### Marketing Campaign (updated)
```
Marketing Campaign
├── Campaign Engine (child table)
│   ├── engine_type: Select
│   ├── engine_doc_type: Link / dynamic type indicator
│   ├── engine_doc: Dynamic Link
│   ├── status
│   ├── scheduled_datetime
│   ├── sync_with_omni_blast: Check
│   └── results_json: Code (JSON)
└── ...existing fields...
```

### Engine Registry

| engine_type | Reuses DocType | New DocType | Execution Method |
|---|---|---|---|
| Email Blast | Newsletter (Frappe) | — | `newsletter.send_emails()` |
| Email Sequence | Email Campaign (ERPNext CRM) | — | Hook-driven daily |
| WhatsApp | BulkWhatsAppMessage (frappe_whatsapp) | — | Submit doc, auto-queues |
| Social Media | Social Post (Marketing Hub) | — | `publish_to_platform()` |
| SMS | — | **SMS Campaign** | Custom `execute()` using `frappe.send_sms()` |
| Meta Ads | — | **Meta Ads Campaign** | Custom `execute()` using Meta Marketing API |
| OOH | — | **OOH Campaign** | Custom `execute()` using vendor adapter |

### Omni Blast (refactored)
1. Load all `Campaign Engine` rows where `sync_with_omni_blast = 1`
2. For each engine:
   ```python
   engine_doc = frappe.get_doc(engine.engine_doc_type, engine.engine_doc)
   result = ENGINE_REGISTRY[engine.engine_type].execute(engine_doc)
   ```
3. Update `Campaign Engine` status and `results_json`
4. Aggregate into Omni Blast results
5. **No channel-specific code**

---

## Implementation Order

### Phase 1 — Foundation
1. Create `Campaign Engine` child table DocType
2. Update `Marketing Campaign` JSON — replace `Marketing Campaign Channel` with `Campaign Engine`
3. Update `Marketing Campaign` controller — validation, auto-create engine rows

### Phase 2 — New Engine DocTypes
4. Create `SMS Campaign` DocType + controller
5. Create `Meta Ads Campaign` DocType + controller
6. Create `OOH Vendor` DocType (simple config table)
7. Create `OOH Campaign` DocType + controller (links to OOH Vendor)

### Phase 3 — Orchestration
8. Create `engine_registry.py` utility module
9. Refactor `Omni Blast` into pure orchestrator
10. Update `Campaign Activity` to work with engine registry

### Phase 4 — Integration & Cleanup
11. Migration patch: `Marketing Campaign Channel` → `Campaign Engine`
12. Update API endpoints (`campaigns.py`, etc.)
13. Remove `Marketing Campaign Channel` if no longer needed
14. Security scan with Snyk
15. Write tests

---

## File Changes

### New Files
- `marketing_hub/doctype/campaign_engine/campaign_engine.json`
- `marketing_hub/doctype/campaign_engine/campaign_engine.py`
- `marketing_hub/doctype/sms_campaign/sms_campaign.json`
- `marketing_hub/doctype/sms_campaign/sms_campaign.py`
- `marketing_hub/doctype/meta_ads_campaign/meta_ads_campaign.json`
- `marketing_hub/doctype/meta_ads_campaign/meta_ads_campaign.py`
- `marketing_hub/doctype/ooh_vendor/ooh_vendor.json`
- `marketing_hub/doctype/ooh_vendor/ooh_vendor.py`
- `marketing_hub/doctype/ooh_campaign/ooh_campaign.json`
- `marketing_hub/doctype/ooh_campaign/ooh_campaign.py`
- `marketing_hub/utils/engine_registry.py`
- `marketing_hub/patches/v1_0/migrate_campaign_channels_to_engines.py`

### Modified Files
- `marketing_hub/doctype/marketing_campaign/marketing_campaign.json`
- `marketing_hub/doctype/marketing_campaign/marketing_campaign.py`
- `marketing_hub/doctype/omni_blast/omni_blast.py`
- `marketing_hub/doctype/omni_blast/omni_blast.json` (if needed)
- `marketing_hub/doctype/campaign_activity/campaign_activity.py`
- `marketing_hub/api/campaigns.py`
- `marketing_hub/hooks.py` (add patch)

---

## Frappe Conventions Applied
- DocType names are singular
- Child tables use `istable: 1`
- Controllers inherit from `Document`
- JSON uses `field_order` for display ordering
- Naming series where appropriate
- `frappe.enqueue` for background jobs
- `frappe.get_doc` + `doc.insert()` / `doc.save()` for document lifecycle
- Permissions for System Manager, Marketing Manager, Marketing User
