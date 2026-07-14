# Project Charter Feature

The Project Charter feature enables users to create professional project documentation following PMI (Project Management Institute) standards.

## ✨ Features

- **Template-Based Charter Creation**: Start with a comprehensive standard template
- **Dynamic Form Interface**: Intuitive form with 7 different field types
- **Auto-Save**: Automatic draft saving every 5 minutes
- **Charter Management**: View, search, sort, and manage all your charters
- **PDF Export**: Generate professional PDF documents
- **Validation**: Real-time field validation ensures data quality
- **Keyboard Shortcuts**: Speed up your workflow with hotkeys

## 🚀 Quick Start

### Creating a New Charter

1. Click **"New Charter"** or press `Ctrl+N`
2. Fill out the form sections (required fields marked with \*)
3. Click **"Save"** or press `Ctrl+S` to save your charter
4. Click **"Export PDF"** or press `Ctrl+E` to generate a PDF

### Opening an Existing Charter

1. Click **"Open"** or press `Ctrl+O`
2. Browse to select a charter file
3. Edit and save as needed

### Managing Charters

1. Go to the **"Charter Manager"** tab
2. View all saved charters with completion status
3. Use the search box to filter by title or status
4. Sort by modified date, title, or status
5. Double-click to open, or use right-click menu for more options

## 📋 Charter Sections

A standard project charter includes 9 comprehensive sections:

### 1. Project Identification

- Project Name\*
- Project Code
- Sponsor Name\*
- Start Date\*
- End Date\*
- Project Description\*

### 2. Objectives & Business Case

- Business Objectives\*
- Success Criteria
- Expected Benefits

### 3. Scope

- In Scope\*
- Out of Scope\*
- Key Deliverables\*
- Assumptions
- Constraints

### 4. Budget

- Total Budget\*
- Funding Source
- Budget Notes
- Budget Breakdown (table)

### 5. Schedule

- Project Start Date\*
- Project End Date\*

### 6. Project Team

- Project Manager
- Team Members (table)

### 7. Stakeholders

- Key Stakeholders\* (table with Name, Role, Contact)

### 8. Risks & Constraints

- Key Risks (table)
- Major Constraints

### 9. Approval & Sign-off

- Approval Date
- Approved By
- Signature
- Authorization Date

## 🎨 Field Types

The charter form supports various field types:

| Field Type   | Description        | Example                   |
| ------------ | ------------------ | ------------------------- |
| **Text**     | Single-line input  | Project name, sponsor     |
| **Textarea** | Multi-line text    | Descriptions, objectives  |
| **Date**     | Date picker        | Start/end dates           |
| **Currency** | Monetary values    | Budget amounts            |
| **Number**   | Numeric input      | Team size, percentages    |
| **Dropdown** | Predefined choices | Priority, status          |
| **Table**    | Structured data    | Stakeholders, team, risks |

## ⌨️ Keyboard Shortcuts

| Shortcut    | Action                     |
| ----------- | -------------------------- |
| `Ctrl+N`    | Create new charter         |
| `Ctrl+O`    | Open existing charter      |
| `Ctrl+S`    | Save current charter       |
| `Ctrl+E`    | Export to PDF              |
| `F1`        | Show help dialog           |
| `Tab`       | Navigate to next field     |
| `Shift+Tab` | Navigate to previous field |

## 💾 Auto-Save

Your work is automatically saved to the `data/charters/drafts/` folder every 5 minutes. This prevents data loss if the application closes unexpectedly.

- Auto-save runs in the background
- Draft files are named with the charter ID
- Manual save (Ctrl+S) lets you choose the location
- Last saved time is displayed in the status bar

## ✅ Validation

The charter feature includes comprehensive validation:

- **Required Fields**: Must be filled before saving
- **Date Format**: Validates dates are in correct format
- **Currency**: Ensures numeric values for money fields
- **Email**: Validates email addresses
- **Max Length**: Enforces character limits

Validation errors are shown when you try to save. You can still export to PDF with warnings if needed.

## 📄 PDF Export

Generate professional PDF documents with:

- **Professional Styling**: Clean, corporate design
- **Section Headers**: Clear organization
- **Table Formatting**: Properly formatted tables with alternating rows
- **Page Headers/Footers**: Project name and page numbers
- **Metadata**: Generation timestamp and charter info

PDF files are saved to `data/charters/exports/` by default.

## 🗂️ Charter Manager

The Charter Manager tab provides a centralized view of all your charters:

### Features:

- **List View**: Shows title, status, modified date, completion %
- **Search**: Filter charters by title or status
- **Sort**: Order by modified date, title, or status
- **Actions**:
  - Open: Load charter for editing
  - Duplicate: Create a copy with new ID
  - Delete: Remove charter permanently
  - Refresh: Reload charter list

### Status Indicators:

- **DRAFT**: Work in progress
- **FINAL**: Completed charter
- **ARCHIVED**: No longer active

## 📁 File Structure

```
data/
  charters/
    drafts/          # Auto-saved drafts
    exports/         # Generated PDF files
    *.json          # Manually saved charters

templates/
  charter/
    standard_charter.json  # Default template
```

## 🔧 Technical Details

### Data Format

Charters are saved as JSON files with this structure:

```json
{
  "metadata": {
    "charter_id": "uuid",
    "created_date": "ISO datetime",
    "modified_date": "ISO datetime",
    "status": "draft|final|archived",
    "template_id": "standard_charter",
    "template_version": "1.0.0"
  },
  "data": {
    "section_id": {
      "field_id": "value"
    }
  }
}
```

### Templates

Templates define the structure and fields of charters. The standard template includes 30 fields across 9 sections, with 18 required fields.

### Dependencies

- **reportlab**: PDF generation
- **Pillow**: Image handling
- **python-dateutil**: Date parsing
- **jsonschema**: Template validation

## 💡 Tips & Best Practices

1. **Save Frequently**: Use Ctrl+S or let auto-save protect your work
2. **Required Fields First**: Fill required fields (\*) before saving
3. **Use Tables**: Organize stakeholders, team, and risks in tables
4. **Expand/Collapse**: Click section headers to focus on specific areas
5. **Completion Tracking**: Monitor the completion % at the bottom
6. **Export Early**: Generate PDFs periodically to review formatting
7. **Descriptive Names**: Use clear project names for easy identification
8. **Charter Manager**: Use it to track multiple projects
9. **Help Dialog**: Press F1 anytime for quick reference
10. **Search Function**: Quickly find charters in the manager

## 🐛 Troubleshooting

### Charter Won't Save

- Check that all required fields (\*) are filled
- Ensure you have write permissions to the save location
- Try saving to a different folder

### PDF Export Fails

- Verify all data is in correct format
- Check if reportlab is installed: `pip install reportlab`
- Review console for detailed error messages

### Auto-Save Not Working

- Check `data/charters/drafts/` folder exists
- Verify auto-save timer is started (check status bar)
- Restart the application if needed

### Charter Manager Empty

- Ensure charters are saved in `data/charters/` directory
- Click "Refresh" to reload the list
- Check file permissions

## 🔮 Future Enhancements

Potential future additions to the charter feature:

- Multiple charter templates (Agile, Waterfall, etc.)
- Custom template creation
- Collaboration features
- Version history
- Chart/diagram integration
- Export to Word/Excel
- Email integration
- Approval workflow
- Digital signatures

## 📚 Additional Resources

- [PMI Project Charter Guidelines](https://www.pmi.org/)
- [Project Management Body of Knowledge (PMBOK)](https://www.pmi.org/pmbok-guide-standards)
- [Charter Template Best Practices](https://www.projectmanagement.com/)

## 🤝 Support

For issues, questions, or feature requests:

1. Check the built-in help dialog (F1)
2. Review this documentation
3. Check the issue tracker
4. Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: November 2, 2025  
**Status**: Production Ready ✅
