# Feature Specification: Project Charter Tab

## Overview

Add a Project Charter creation and management tab to PMHelper GUI application. Users can fill dynamic templates, save data locally, and export professional PDF documents.

## Technology Stack

### Frontend (GUI)

- **Framework**: CustomTkinter (upgraded from Tkinter)
- **Language**: Python 3.x
- **Launch**: `python launch_app.py`
- **Location**: `src/pmhelper/gui/`

### PDF Generation

- **Library**: ReportLab
- **Styling**: Custom PDF templates with professional formatting

### Data Storage

- **Database**: SQLite (location TBD during implementation)
- **Local Storage**: JSON files for templates
- **Backups**: Auto-save drafts locally

## Updated File Structure

```
PMhelper/
├── src/
│   └── pmhelper/
│       └── gui/
│           ├── __init__.py
│           ├── gui.py                      # Main GUI window (existing)
│           │
│           ├── tabs/
│           │   ├── __init__.py
│           │   ├── [existing_tabs].py      # Your current tabs
│           │   ├── charter_tab.py          # 👈 NEW: Main charter tab
│           │   ├── charter_form.py         # 👈 NEW: Form widget
│           │   └── charter_manager.py      # 👈 NEW: Charter list/manager
│           │
│           ├── widgets/
│           │   ├── __init__.py
│           │   ├── [existing_widgets].py   # Your current widgets
│           │   ├── collapsible_section.py  # 👈 NEW: Expandable sections
│           │   ├── table_editor.py         # 👈 NEW: Editable table widget
│           │   └── date_picker.py          # 👈 NEW: Date selection widget
│           │
│           ├── models/
│           │   ├── __init__.py
│           │   ├── charter_model.py        # 👈 NEW: Charter data structure
│           │   └── template_model.py       # 👈 NEW: Template structure
│           │
│           ├── services/
│           │   ├── __init__.py
│           │   ├── charter_service.py      # 👈 NEW: Charter business logic
│           │   ├── pdf_service.py          # 👈 NEW: PDF generation
│           │   ├── template_service.py     # 👈 NEW: Template management
│           │   └── storage_service.py      # 👈 NEW: Data persistence
│           │
│           └── utils/
│               ├── __init__.py
│               ├── validators.py           # 👈 NEW: Field validation
│               └── pdf_styles.py           # 👈 NEW: PDF styling config
│
├── templates/
│   ├── charter/
│   │   ├── standard_charter.json           # 👈 NEW: Standard template
│   │   ├── agile_charter.json              # 👈 NEW: Agile template (future)
│   │   └── template_schema.json            # 👈 NEW: Template structure definition
│   └── pdf/
│       ├── header_logo.png                 # 👈 NEW: PDF header image
│       └── styles.json                     # 👈 NEW: PDF styling config
│
├── data/
│   ├── charters/                           # 👈 NEW: Saved charter files
│   │   ├── drafts/                         # Auto-saved drafts
│   │   └── exports/                        # Exported PDFs (optional backup)
│   └── [database files - TBD]
│
├── assets/
│   ├── guide-project-charter-eng.pdf       # Reference guide (existing)
│   └── [other assets]
│
├── tests/
│   └── gui/
│       ├── test_charter_tab.py             # 👈 NEW: Tab tests
│       ├── test_charter_service.py         # 👈 NEW: Service tests
│       └── test_pdf_generation.py          # 👈 NEW: PDF tests
│
├── docs/
│   ├── FEATURE_PROJECT_CHARTER.md          # This file
│   ├── CHARTER_EXECUTION_PLAN.md           # Execution roadmap
│   └── CHARTER_USER_GUIDE.md               # 👈 NEW: User documentation
│
├── launch_app.py                           # GUI launcher (existing)
├── requirements.txt                        # Updated with new dependencies
└── README.md
```

## Feature Requirements

### Functional Requirements

#### FR1: Template Management

- **FR1.1**: System provides 2+ pre-built templates in `templates/charter/`
- **FR1.2**: User can select template from dropdown in charter tab
- **FR1.3**: User can create custom templates (future phase)
- **FR1.4**: Templates stored as JSON files with defined structure

#### FR2: Charter Creation

- **FR2.1**: User creates new charter from selected template
- **FR2.2**: Form dynamically generated based on template sections:
  - Project Identification (title, date, PM, sponsor)
  - Objectives (primary goals, success criteria, KPIs)
  - Scope (in/out scope, deliverables, assumptions)
  - Budget (total, breakdown, cost assumptions)
  - Schedule (duration, milestones, key dates)
  - Team (structure, roles & responsibilities)
  - Stakeholders (list, communication plan)
  - Risks (risk register, mitigation strategies)
  - Approval (signatures, date)
- **FR2.3**: Field validation for required fields
- **FR2.4**: Collapsible sections for better UX
- **FR2.5**: Progress indicator showing completion percentage

#### FR3: Data Persistence

- **FR3.1**: Auto-save draft every 5 minutes to `data/charters/drafts/`
- **FR3.2**: Manual save button saves to chosen location
- **FR3.3**: Load existing charters from file browser
- **FR3.4**: Charter file format: JSON with metadata
- **FR3.5**: Delete charter with confirmation dialog
- **FR3.6**: Duplicate/copy charter functionality

#### FR4: PDF Export

- **FR4.1**: Export button generates professional PDF
- **FR4.2**: PDF includes:
  - Company header with logo (optional)
  - All filled sections with proper formatting
  - Tables with borders and styling
  - Page numbers and generation date
  - Professional typography
- **FR4.3**: User selects PDF save location via dialog
- **FR4.4**: PDF filename: `ProjectCharter_[ProjectName]_[Date].pdf`
- **FR4.5**: Validation check before export (warn if incomplete)

#### FR5: Charter Management

- **FR5.1**: Charter list view showing saved charters
- **FR5.2**: Search/filter charters by name, date, status
- **FR5.3**: Open charter from list
- **FR5.4**: Status indicator (Draft/Final/Archived)
- **FR5.5**: Quick actions: Open, Export, Duplicate, Delete

#### FR6: UI/UX

- **FR6.1**: Charter tab accessible from main GUI tabs
- **FR6.2**: Toolbar with: New, Open, Save, Export, Help
- **FR6.3**: Collapsible sections for long forms
- **FR6.4**: Progress bar showing completion (%)
- **FR6.5**: Tooltips for field guidance
- **FR6.6**: Clear/Reset form with confirmation
- **FR6.7**: Keyboard shortcuts (Ctrl+S save, Ctrl+E export)

### Non-Functional Requirements

#### NFR1: Performance

- Tab loads in < 1 second
- Form generation from template < 0.5 seconds
- PDF generation < 3 seconds
- Auto-save non-blocking (runs in background)

#### NFR2: Reliability

- No data loss (auto-save mechanism)
- Graceful error handling for PDF generation
- File corruption prevention (atomic writes)

#### NFR3: Usability

- Intuitive form layout following template order
- Clear field labels and validation messages
- Responsive UI (no freezing during operations)
- Professional appearance with CustomTkinter

#### NFR4: Maintainability

- Modular code structure (MVC-like pattern)
- Template system easily extensible
- Comprehensive docstrings
- Unit test coverage > 70%

## Template Structure (JSON Schema)

### Standard Charter Template

```json
{
  "template_id": "standard_charter_v1",
  "template_name": "Standard Project Charter",
  "version": "1.0",
  "description": "Comprehensive project charter template for traditional projects",
  "sections": [
    {
      "section_id": "identification",
      "section_name": "Project Identification",
      "section_order": 1,
      "is_required": true,
      "fields": [
        {
          "field_id": "project_title",
          "field_label": "Project Title",
          "field_type": "text",
          "is_required": true,
          "max_length": 100,
          "placeholder": "Enter project title...",
          "tooltip": "The official name of the project"
        },
        {
          "field_id": "start_date",
          "field_label": "Project Start Date",
          "field_type": "date",
          "is_required": true,
          "tooltip": "Expected or actual project start date"
        },
        {
          "field_id": "project_manager",
          "field_label": "Project Manager",
          "field_type": "text",
          "is_required": true,
          "max_length": 100,
          "tooltip": "Name of the person responsible for managing the project"
        },
        {
          "field_id": "project_sponsor",
          "field_label": "Project Sponsor",
          "field_type": "text",
          "is_required": false,
          "max_length": 100,
          "tooltip": "Executive sponsor providing support and resources"
        }
      ]
    },
    {
      "section_id": "objectives",
      "section_name": "Project Objectives",
      "section_order": 2,
      "is_required": true,
      "fields": [
        {
          "field_id": "primary_objectives",
          "field_label": "Primary Objectives",
          "field_type": "textarea",
          "is_required": true,
          "max_length": 2000,
          "rows": 6,
          "placeholder": "List the main objectives of this project...",
          "tooltip": "What does this project aim to achieve?"
        },
        {
          "field_id": "success_criteria",
          "field_label": "Success Criteria",
          "field_type": "textarea",
          "is_required": true,
          "max_length": 2000,
          "rows": 6,
          "placeholder": "Define measurable success criteria...",
          "tooltip": "How will you know the project is successful?"
        }
      ]
    },
    {
      "section_id": "scope",
      "section_name": "Project Scope",
      "section_order": 3,
      "is_required": true,
      "fields": [
        {
          "field_id": "in_scope",
          "field_label": "In Scope",
          "field_type": "textarea",
          "is_required": true,
          "max_length": 3000,
          "rows": 8,
          "placeholder": "What is included in this project...",
          "tooltip": "Work that IS part of the project"
        },
        {
          "field_id": "out_scope",
          "field_label": "Out of Scope",
          "field_type": "textarea",
          "is_required": true,
          "max_length": 3000,
          "rows": 8,
          "placeholder": "What is explicitly excluded...",
          "tooltip": "Work that is NOT part of the project"
        },
        {
          "field_id": "deliverables",
          "field_label": "Key Deliverables",
          "field_type": "textarea",
          "is_required": true,
          "max_length": 2000,
          "rows": 6,
          "placeholder": "List major deliverables...",
          "tooltip": "Tangible outputs of the project"
        }
      ]
    },
    {
      "section_id": "budget",
      "section_name": "Budget",
      "section_order": 4,
      "is_required": true,
      "fields": [
        {
          "field_id": "total_budget",
          "field_label": "Total Budget",
          "field_type": "currency",
          "is_required": true,
          "min_value": 0,
          "tooltip": "Total estimated project budget"
        },
        {
          "field_id": "budget_breakdown",
          "field_label": "Budget Breakdown",
          "field_type": "table",
          "is_required": false,
          "columns": [
            {
              "id": "category",
              "label": "Category",
              "type": "text",
              "width": 150
            },
            {
              "id": "amount",
              "label": "Amount",
              "type": "currency",
              "width": 100
            },
            { "id": "notes", "label": "Notes", "type": "text", "width": 200 }
          ],
          "tooltip": "Detailed breakdown of budget categories"
        }
      ]
    },
    {
      "section_id": "schedule",
      "section_name": "Schedule & Timeline",
      "section_order": 5,
      "is_required": true,
      "fields": [
        {
          "field_id": "project_duration",
          "field_label": "Project Duration",
          "field_type": "text",
          "is_required": true,
          "placeholder": "e.g., 6 months, 12 weeks",
          "tooltip": "Expected total duration"
        },
        {
          "field_id": "milestones",
          "field_label": "Major Milestones",
          "field_type": "table",
          "is_required": true,
          "columns": [
            {
              "id": "milestone",
              "label": "Milestone",
              "type": "text",
              "width": 200
            },
            {
              "id": "target_date",
              "label": "Target Date",
              "type": "date",
              "width": 100
            },
            { "id": "status", "label": "Status", "type": "text", "width": 100 }
          ],
          "tooltip": "Key project milestones and target dates"
        }
      ]
    },
    {
      "section_id": "team",
      "section_name": "Project Team",
      "section_order": 6,
      "is_required": true,
      "fields": [
        {
          "field_id": "team_structure",
          "field_label": "Team Structure",
          "field_type": "textarea",
          "is_required": true,
          "max_length": 2000,
          "rows": 6,
          "placeholder": "Describe the team organization...",
          "tooltip": "How is the team organized?"
        },
        {
          "field_id": "roles_responsibilities",
          "field_label": "Roles & Responsibilities",
          "field_type": "table",
          "is_required": true,
          "columns": [
            { "id": "role", "label": "Role", "type": "text", "width": 150 },
            { "id": "name", "label": "Name", "type": "text", "width": 150 },
            {
              "id": "responsibility",
              "label": "Responsibility",
              "type": "text",
              "width": 250
            }
          ],
          "tooltip": "Team member roles and what they're responsible for"
        }
      ]
    },
    {
      "section_id": "stakeholders",
      "section_name": "Stakeholders",
      "section_order": 7,
      "is_required": true,
      "fields": [
        {
          "field_id": "stakeholder_list",
          "field_label": "Stakeholder List",
          "field_type": "table",
          "is_required": true,
          "columns": [
            { "id": "name", "label": "Name", "type": "text", "width": 150 },
            {
              "id": "role",
              "label": "Role/Title",
              "type": "text",
              "width": 150
            },
            {
              "id": "interest",
              "label": "Interest Level",
              "type": "dropdown",
              "width": 100,
              "options": ["High", "Medium", "Low"]
            },
            {
              "id": "influence",
              "label": "Influence",
              "type": "dropdown",
              "width": 100,
              "options": ["High", "Medium", "Low"]
            }
          ],
          "tooltip": "Key stakeholders and their engagement level"
        }
      ]
    },
    {
      "section_id": "risks",
      "section_name": "Risks & Mitigation",
      "section_order": 8,
      "is_required": true,
      "fields": [
        {
          "field_id": "risk_register",
          "field_label": "Risk Register",
          "field_type": "table",
          "is_required": true,
          "columns": [
            { "id": "risk", "label": "Risk", "type": "text", "width": 200 },
            {
              "id": "probability",
              "label": "Probability",
              "type": "dropdown",
              "width": 100,
              "options": ["High", "Medium", "Low"]
            },
            {
              "id": "impact",
              "label": "Impact",
              "type": "dropdown",
              "width": 100,
              "options": ["High", "Medium", "Low"]
            },
            {
              "id": "mitigation",
              "label": "Mitigation Strategy",
              "type": "text",
              "width": 250
            }
          ],
          "tooltip": "Identified risks and how to address them"
        }
      ]
    },
    {
      "section_id": "approval",
      "section_name": "Approval",
      "section_order": 9,
      "is_required": true,
      "fields": [
        {
          "field_id": "approval_signatures",
          "field_label": "Approval Signatures",
          "field_type": "table",
          "is_required": true,
          "columns": [
            { "id": "name", "label": "Name", "type": "text", "width": 150 },
            { "id": "role", "label": "Role", "type": "text", "width": 150 },
            { "id": "date", "label": "Date", "type": "date", "width": 100 }
          ],
          "tooltip": "Who approves this charter"
        },
        {
          "field_id": "approval_date",
          "field_label": "Charter Approval Date",
          "field_type": "date",
          "is_required": true,
          "tooltip": "When was this charter officially approved?"
        }
      ]
    }
  ]
}
```

## Data Model

### Charter Data Structure (Saved as JSON)

```json
{
  "charter_metadata": {
    "charter_id": "uuid-generated",
    "template_id": "standard_charter_v1",
    "project_title": "Value from form",
    "created_date": "2025-11-02T10:30:00",
    "last_modified": "2025-11-02T14:45:00",
    "status": "draft|final|archived",
    "version": "1.0"
  },
  "charter_data": {
    "identification": {
      "project_title": "PMHelper Enhancement Project",
      "start_date": "2025-11-15",
      "project_manager": "John Doe",
      "project_sponsor": "Jane Smith"
    },
    "objectives": {
      "primary_objectives": "Add project charter functionality...",
      "success_criteria": "Users can create and export charters..."
    },
    "scope": {
      "in_scope": "Charter tab, PDF export...",
      "out_scope": "Server deployment, mobile app...",
      "deliverables": "Functional charter tab, PDF templates..."
    }
  }
}
```

## Dependencies

### New Python Packages

```txt
# Add to requirements.txt

# GUI Enhancement
customtkinter>=5.2.0

# PDF Generation
reportlab>=4.0.0
Pillow>=10.0.0

# Date Handling
python-dateutil>=2.8.0

# JSON Schema Validation (optional)
jsonschema>=4.19.0
```

## Integration Points

### 1. Main GUI (`gui.py`)

```python
# In your main GUI class, add charter tab
from pmhelper.gui.tabs.charter_tab import CharterTab

class MainGUI:
    def __init__(self):
        # ... existing code ...

        # Add charter tab
        self.charter_tab = CharterTab(self.tab_view)
        self.tab_view.add("Project Charter", self.charter_tab)
```

### 2. Launch Script (`launch_app.py`)

No changes needed - existing launch should work.

### 3. Menu/Toolbar Integration

If you have a menu bar:

```python
# Add File menu option
file_menu.add_command(label="New Project Charter", command=self.open_charter_tab)
```

## Success Criteria

Feature is successful when:

- ✅ User can create a complete charter in < 15 minutes
- ✅ PDF generates without errors 99% of time
- ✅ No data loss incidents (auto-save works)
- ✅ Form validation prevents bad data
- ✅ Auto-save prevents work loss
- ✅ PDF looks professional and readable
- ✅ Integrates seamlessly with existing GUI

## Risks & Mitigations

| Risk                           | Impact | Probability | Mitigation                                          |
| ------------------------------ | ------ | ----------- | --------------------------------------------------- |
| ReportLab complexity           | High   | Medium      | Start with simple PDF, iterate; FPDF as backup      |
| CustomTkinter migration issues | Medium | Low         | Keep Tkinter as fallback; gradual migration         |
| Table widget complexity        | High   | Medium      | Use ttk.Treeview as fallback                        |
| PDF rendering errors           | High   | Low         | Comprehensive error handling; preview before export |
| Performance with large forms   | Medium | Low         | Lazy loading; pagination for tables                 |
| Auto-save implementation       | Medium | Low         | Use threading; test thoroughly                      |

## Open Questions

1. **Database vs File Storage**: Implement database first or start with JSON files?
2. **Preview Panel**: Implement in Phase 1 or defer to future?
3. **Template Editor**: User can create custom templates in Phase 1?
4. **Logo Upload**: Allow users to upload custom logos for PDF?
5. **Export Formats**: Support multiple formats (PDF, DOCX) or just PDF?

## Future Enhancements

### Phase 2 (Future)

- Custom template creator UI
- Template import/export
- Charter version control
- Charter comparison (diff between versions)
- Collaboration features (comments, reviews)
- Export to DOCX format
- Integration with project data from CPM/PERT calculations

### Phase 3 (Future)

- Cloud sync for charters
- Charter templates marketplace
- AI-powered charter suggestions
- Multi-language support

---

**Document Version**: 2.0  
**Created**: November 2025  
**Last Updated**: November 2, 2025  
**Status**: Approved - Ready for Implementation

**Next Steps:**

1. Review and approve this specification
2. Proceed with Sprint 1 execution
3. Set up development environment
4. Create foundational code structure
