# Marketing Hub - Workspace & Role-Based Permissions

## Workspace Overview

The **Marketing Hub** workspace is a custom workspace that provides organized access to all marketing functionality. It's designed with role-based access control where:

- **System Managers** see everything (full workspace)
- Other roles can be assigned specific access to sections
- Users can be individually assigned to campaigns/segments

## Workspace Structure

### 1. Marketing Dashboard (Top Section)
Quick shortcuts to most-used features:
- Campaign (Green)
- Analytics Connector (Blue) - System Manager only
- Marketing Segment (Orange)
- Lead (Yellow)

### 2. Campaign Management
**Visible to**: All marketing roles

**Links**:
- Campaign (DocType) - Create and manage campaigns
- Campaign Activity (DocType) - Campaign execution logs
- Lead (DocType) - View leads attributed to campaigns

### 3. Targeting
**Visible to**: All marketing roles

**Links**:
- Marketing Segment (DocType) - Audience definitions
- Customer (DocType) - View customer data for segmentation

### 4. Content
**Visible to**: All marketing roles

**Links**:
- Marketing Template (DocType) - Message templates for all channels

### 5. Omni-Channel Execution

#### Social Media
**Visible to**: All marketing roles

**Links**:
- Social Post (DocType) - Schedule and publish social posts

#### Advertising
**Visible to**: System Manager only (contains OAuth credentials)

**Links**:
- Ad Account (DocType) - OAuth credentials for ad platforms
- Analytics Connector (DocType) - Configure platform analytics sync

#### Messaging
**Visible to**: All marketing roles

**Links**:
- WhatsApp Message (DocType) - View WhatsApp message history
- Email Queue (DocType) - Monitor email delivery

### 6. Analytics & Reporting
**Visible to**: All marketing roles

**Links**:
- Analytics Daily Log (DocType) - Daily metrics from platforms
- Campaign Performance (Report) - Campaign effectiveness
- ROAS Analysis (Report) - Return on ad spend by campaign

### 7. Agency Management
**Visible to**: System Manager only

**Links**:
- Agency Package (DocType) - Define subscription packages
- Client Subscription (DocType) - Manage client subscriptions

### 8. Settings
**Visible to**: System Manager only

**Links**:
- Marketing Hub Setup (Single DocType) - Global configuration
- Social Login Key (DocType) - OAuth credentials for platforms

## Role-Based Access Control

### Pre-Defined Roles

#### 1. System Manager (Full Access)
**Permissions**:
- ✅ View entire workspace
- ✅ Manage all campaigns
- ✅ Configure OAuth and Ad Accounts
- ✅ Manage agency settings
- ✅ Assign users to campaigns
- ✅ Export all data

**Use Case**: IT administrators, marketing directors

#### 2. Sales Manager (Management Access)
**Permissions**:
- ✅ View most of workspace (except agency/settings)
- ✅ Manage all campaigns
- ✅ View all analytics
- ✅ Execute blasts
- ✅ Assign campaigns to team
- ❌ Configure OAuth
- ❌ Manage agency settings

**Use Case**: Marketing managers, team leads

#### 3. Sales User (Limited Access)
**Permissions**:
- ✅ View assigned campaigns only
- ✅ Edit assigned campaigns
- ✅ View campaign performance
- ✅ Execute approved blasts
- ❌ Create new campaigns (unless granted)
- ❌ View all campaigns
- ❌ Configure settings

**Use Case**: Marketing coordinators, sales reps

#### 4. Employee (Read-Only)
**Permissions**:
- ✅ View assigned campaigns (read-only)
- ✅ View campaign results
- ❌ Edit campaigns
- ❌ Execute blasts
- ❌ Configure anything

**Use Case**: Team members who need visibility

### Custom Roles (To Be Created)

#### 5. Marketing Manager (New Role)
**Recommended Permissions**:
```
DocType Permissions:
├── Campaign: Create, Read, Write, Delete, Submit
├── Campaign Activity: Create, Read, Write, Delete
├── Marketing Segment: Create, Read, Write, Delete
├── Marketing Template: Create, Read, Write, Delete
├── Social Post: Create, Read, Write, Delete, Submit
├── Lead: Read, Write (attribution updates)
├── Customer: Read (segmentation)
├── Analytics Daily Log: Read
├── Analytics Connector: Read, Write (no OAuth config)
├── Ad Account: Read (view accounts, not credentials)
└── Project: Read (campaign linking)
```

**Workspace Access**: All sections except Settings

**Use Case**: Day-to-day marketing operations, campaign execution

#### 6. Marketing Executive (New Role)
**Recommended Permissions**:
```
DocType Permissions:
├── Campaign: Create, Read, Write (own campaigns only)
├── Campaign Activity: Create, Read, Write (own)
├── Marketing Segment: Read, Write
├── Marketing Template: Read, Write
├── Social Post: Create, Read, Write (own)
├── Lead: Read
├── Customer: Read
└── Analytics Daily Log: Read (own campaigns)
```

**Workspace Access**: Campaign Management, Targeting, Content, Social Media, Analytics (limited)

**Use Case**: Individual campaign owners, content creators

#### 7. Marketing Analyst (New Role)
**Recommended Permissions**:
```
DocType Permissions:
├── Campaign: Read (all)
├── Campaign Activity: Read (all)
├── Marketing Segment: Read
├── Lead: Read
├── Customer: Read
├── Analytics Daily Log: Read (all), Export
├── All Reports: Read, Export
└── Social Post: Read
```

**Workspace Access**: Analytics & Reporting (full), Campaign Management (read-only)

**Use Case**: Data analysts, reporting specialists

#### 8. HR Manager (Campaign Assignment)
**Recommended Permissions**:
```
DocType Permissions:
├── Campaign: Read, Assign users
├── Marketing Segment: Read
├── Employee: Read, Write (for assignments)
└── Department: Read
```

**Workspace Access**: Campaign Management (assignment only)

**Use Case**: Assign campaigns to marketing team members

#### 9. HR User (View Assigned)
**Recommended Permissions**:
```
DocType Permissions:
├── Campaign: Read (assigned only)
├── Campaign Activity: Read (assigned only)
└── Lead: Read (from assigned campaigns)
```

**Workspace Access**: Campaign Management (assigned items only)

**Use Case**: HR staff who support marketing campaigns

## User Assignment Workflow

### Assigning Users to Campaigns

#### Method 1: Via Campaign Form
```python
# In Campaign doctype, add custom field:
{
    "fieldname": "assigned_users",
    "fieldtype": "Table",
    "label": "Assigned Users",
    "options": "Campaign User Assignment"  # Child table
}

# Child table: Campaign User Assignment
{
    "fields": [
        {"fieldname": "user", "fieldtype": "Link", "options": "User"},
        {"fieldname": "role", "fieldtype": "Select", "options": "Owner\nCollaborator\nViewer"},
        {"fieldname": "can_edit", "fieldtype": "Check"},
        {"fieldname": "can_execute", "fieldtype": "Check"}
    ]
}
```

#### Method 2: Via User Permissions
System Manager can set User Permissions:
```
Doctype: Campaign
User: john@example.com
Document: CAMPAIGN-001
Permissions: Read, Write
```

This restricts user to see only CAMPAIGN-001.

#### Method 3: Via Custom Permission Rules
In Role Permission Manager:
```javascript
// Apply User Permission on Campaign
frappe.db.set_value("Custom DocPerm", {
    "parent": "Campaign",
    "role": "Marketing Executive",
    "apply_user_permissions": 1,
    "if_owner": 1  // Can edit own campaigns
});
```

### Implementing User Assignment

Add to `marketing_hub/hooks.py`:
```python
permission_query_conditions = {
    "Campaign": "marketing_hub.utils.permissions.get_campaign_permission_query_conditions",
    "Campaign Activity": "marketing_hub.utils.permissions.get_campaign_activity_permission_query_conditions"
}

has_permission = {
    "Campaign": "marketing_hub.utils.permissions.has_campaign_permission",
    "Campaign Activity": "marketing_hub.utils.permissions.has_campaign_activity_permission"
}
```

Create `marketing_hub/utils/permissions.py`:
```python
import frappe

def get_campaign_permission_query_conditions(user):
    if not user:
        user = frappe.session.user
    
    # System Manager sees all
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Marketing Manager sees all
    if "Marketing Manager" in frappe.get_roles(user):
        return ""
    
    # Others see only assigned campaigns or owned campaigns
    return f"""(
        `tabCampaign`.owner = '{user}' 
        OR `tabCampaign`.name IN (
            SELECT parent FROM `tabCampaign User Assignment` 
            WHERE user = '{user}'
        )
    )"""

def has_campaign_permission(doc, ptype, user):
    if not user:
        user = frappe.session.user
    
    # System Manager has full access
    if "System Manager" in frappe.get_roles(user):
        return True
    
    # Marketing Manager has full access
    if "Marketing Manager" in frappe.get_roles(user):
        return True
    
    # Owner has full access
    if doc.owner == user:
        return True
    
    # Check if user is assigned
    assigned_users = frappe.get_all(
        "Campaign User Assignment",
        filters={"parent": doc.name, "user": user},
        fields=["role", "can_edit"]
    )
    
    if not assigned_users:
        return False
    
    assignment = assigned_users[0]
    
    # Check permission type
    if ptype == "read":
        return True  # All assigned users can read
    elif ptype == "write":
        return assignment.can_edit
    elif ptype == "delete":
        return False  # Only System Manager/Marketing Manager can delete
    
    return False
```

## Setup Instructions

### 1. Install Workspace
```bash
cd /home/puxxo/CodeBase/erpNext/frappe-bench-v15
source env/bin/activate
bench --site erpnext-v15.local migrate
bench restart
```

The workspace will automatically appear in the sidebar for users with appropriate permissions.

### 2. Create Custom Roles

Navigate to: **Setup > Users and Permissions > Role**

Create these roles:
1. Marketing Manager
2. Marketing Executive
3. Marketing Analyst

### 3. Configure Role Permissions

Navigate to: **Setup > Permissions > Role Permissions Manager**

For each Marketing Hub doctype:
- Set permissions for new roles
- Enable "Apply User Permissions" for Marketing Executive
- Enable "If Owner" for owned campaigns

### 4. Assign Users to Roles

Navigate to: **Setup > Users and Permissions > User**

For each user:
- Add appropriate marketing role(s)
- Set default workspace to "Marketing Hub" if primary role

### 5. Create User Permissions (Optional)

For restrictive access:

Navigate to: **Setup > Permissions > User Permissions**

Create user permissions:
- User: john@example.com
- Allow: Campaign
- For Value: CAMPAIGN-001

This limits john to see only CAMPAIGN-001.

### 6. Configure Workspace Visibility

By default, workspace is public (visible to all).

To restrict:
```python
# In marketing_hub/hooks.py
on_session_creation = "marketing_hub.utils.workspace.setup_workspace_visibility"
```

```python
# In marketing_hub/utils/workspace.py
def setup_workspace_visibility(login_manager):
    user = frappe.session.user
    roles = frappe.get_roles(user)
    
    # Hide workspace if user doesn't have marketing roles
    marketing_roles = ["System Manager", "Sales Manager", "Marketing Manager", 
                       "Marketing Executive", "Marketing Analyst"]
    
    has_access = any(role in marketing_roles for role in roles)
    
    if not has_access:
        frappe.db.set_value("Workspace", "Marketing Hub", "is_hidden", 1, 
                           update_modified=False)
```

## Assignment UI Enhancement

Add assignment interface to Campaign form:

Create `marketing_hub/public/js/campaign_assignment.js`:
```javascript
frappe.ui.form.on('Campaign', {
    refresh: function(frm) {
        if (!frm.is_new() && frappe.user.has_role("System Manager") || 
            frappe.user.has_role("Marketing Manager")) {
            
            frm.add_custom_button(__('Assign Users'), function() {
                let d = new frappe.ui.Dialog({
                    title: __('Assign Users to Campaign'),
                    fields: [
                        {
                            fieldname: 'user',
                            fieldtype: 'Link',
                            label: __('User'),
                            options: 'User',
                            reqd: 1
                        },
                        {
                            fieldname: 'role',
                            fieldtype: 'Select',
                            label: __('Assignment Role'),
                            options: 'Owner\nCollaborator\nViewer',
                            default: 'Collaborator',
                            reqd: 1
                        },
                        {
                            fieldname: 'can_edit',
                            fieldtype: 'Check',
                            label: __('Can Edit'),
                            default: 1
                        },
                        {
                            fieldname: 'can_execute',
                            fieldtype: 'Check',
                            label: __('Can Execute Blasts'),
                            default: 1
                        }
                    ],
                    primary_action_label: __('Assign'),
                    primary_action: function(values) {
                        frappe.call({
                            method: 'marketing_hub.api.campaign.assign_user',
                            args: {
                                campaign: frm.doc.name,
                                user: values.user,
                                role: values.role,
                                can_edit: values.can_edit,
                                can_execute: values.can_execute
                            },
                            callback: function(r) {
                                if (!r.exc) {
                                    frappe.msgprint(__('User assigned successfully'));
                                    frm.reload_doc();
                                }
                            }
                        });
                        d.hide();
                    }
                });
                d.show();
            }, __('Actions'));
        }
    }
});
```

## Best Practices

### 1. Role Hierarchy
```
System Manager (Full Access)
    ├── Marketing Manager (Campaign Management)
    │   ├── Marketing Executive (Own Campaigns)
    │   └── Marketing Analyst (Read-Only)
    ├── Sales Manager (Sales-driven Campaigns)
    │   └── Sales User (Assigned Campaigns)
    └── HR Manager (User Assignment)
        └── HR User (View Assigned)
```

### 2. Permission Strategy
- **System Manager**: Only for technical configuration (OAuth, integrations)
- **Marketing Manager**: Full campaign operations, no technical config
- **Marketing Executive**: Own campaigns only, collaborative features
- **Analysts**: Read-only with export rights
- **Sales**: Campaign execution, lead tracking

### 3. Data Security
- OAuth credentials: System Manager only
- Client data (agency mode): System Manager, Marketing Manager
- Campaign budgets: Marketing Manager and above
- Analytics: All marketing roles (aggregated)
- User assignments: System Manager, Marketing Manager, HR Manager

### 4. Assignment Guidelines
- Assign by campaign (not global access)
- Use role-based defaults (Marketing Executive = all new campaigns they create)
- Review assignments quarterly
- Remove assignments when users change departments

## Testing Permissions

### Test Script
```python
# Run in bench console
import frappe

def test_campaign_permissions():
    # Test as Marketing Executive
    frappe.set_user("executive@example.com")
    
    # Should see only assigned campaigns
    campaigns = frappe.get_all("Campaign")
    print(f"Executive sees {len(campaigns)} campaigns")
    
    # Test as Marketing Manager
    frappe.set_user("manager@example.com")
    campaigns = frappe.get_all("Campaign")
    print(f"Manager sees {len(campaigns)} campaigns")
    
    # Test as System Manager
    frappe.set_user("Administrator")
    campaigns = frappe.get_all("Campaign")
    print(f"Admin sees {len(campaigns)} campaigns")

test_campaign_permissions()
```

---

**Summary**: Marketing Hub workspace provides role-based access with granular control. System Managers see everything and configure integrations. Marketing Managers handle day-to-day operations. Marketing Executives work on assigned campaigns. User assignment can be done via Campaign form, User Permissions, or custom assignment tables.
