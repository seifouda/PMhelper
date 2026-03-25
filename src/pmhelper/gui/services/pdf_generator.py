"""PDF Generator service for exporting Project Charters to PDF format."""

from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image, Frame, PageTemplate
)
from reportlab.pdfgen import canvas

from ..models import Charter
from ..models.template_model import Template


class PDFGenerator:
    """Service for generating PDF documents from Project Charters."""
    
    # Page layout constants
    PAGE_SIZE = letter  # 8.5" x 11"
    PAGE_WIDTH = PAGE_SIZE[0]
    PAGE_HEIGHT = PAGE_SIZE[1]
    MARGIN = 0.75 * inch
    
    # Color scheme
    PRIMARY_COLOR = colors.HexColor('#2C3E50')  # Dark blue-gray
    SECONDARY_COLOR = colors.HexColor('#34495E')  # Lighter blue-gray
    ACCENT_COLOR = colors.HexColor('#3498DB')  # Bright blue
    HEADER_BG = colors.HexColor('#ECF0F1')  # Light gray
    
    def __init__(self):
        """Initialize the PDF generator."""
        self.styles = self._create_styles()
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles for the PDF.
        
        Returns:
            Dictionary of style names to ParagraphStyle objects
        """
        base_styles = getSampleStyleSheet()
        
        custom_styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=24,
                textColor=self.PRIMARY_COLOR,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            'Heading1': ParagraphStyle(
                'CustomHeading1',
                parent=base_styles['Heading1'],
                fontSize=16,
                textColor=self.PRIMARY_COLOR,
                spaceAfter=12,
                spaceBefore=20,
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=self.ACCENT_COLOR,
                borderPadding=5,
                backColor=self.HEADER_BG
            ),
            'Heading2': ParagraphStyle(
                'CustomHeading2',
                parent=base_styles['Heading2'],
                fontSize=14,
                textColor=self.SECONDARY_COLOR,
                spaceAfter=8,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            ),
            'FieldLabel': ParagraphStyle(
                'FieldLabel',
                parent=base_styles['Normal'],
                fontSize=10,
                textColor=self.SECONDARY_COLOR,
                spaceAfter=2,
                fontName='Helvetica-Bold'
            ),
            'FieldValue': ParagraphStyle(
                'FieldValue',
                parent=base_styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                fontName='Helvetica',
                alignment=TA_JUSTIFY
            ),
            'Footer': ParagraphStyle(
                'Footer',
                parent=base_styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=TA_CENTER
            ),
            'TableHeader': ParagraphStyle(
                'TableHeader',
                parent=base_styles['Normal'],
                fontSize=10,
                textColor=colors.white,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER
            ),
            'TableCell': ParagraphStyle(
                'TableCell',
                parent=base_styles['Normal'],
                fontSize=9,
                fontName='Helvetica'
            )
        }
        
        return custom_styles
    
    def generate_pdf(
        self,
        charter: Charter,
        template: Template,
        output_path: str
    ) -> bool:
        """Generate a PDF document from a charter.
        
        Args:
            charter: Charter data to export
            template: Template defining charter structure
            output_path: Path to save the PDF file
            
        Returns:
            True if PDF was generated successfully, False otherwise
        """
        try:
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.PAGE_SIZE,
                leftMargin=self.MARGIN,
                rightMargin=self.MARGIN,
                topMargin=self.MARGIN + 0.5 * inch,  # Extra space for header
                bottomMargin=self.MARGIN + 0.5 * inch  # Extra space for footer
            )
            
            # Build content
            story = []
            
            # Add title
            self._add_title(story, charter, template)
            
            # Add metadata section
            self._add_metadata(story, charter)
            
            # Add each template section
            for section in template.sections:
                self._add_section(story, charter, section)
            
            # Build PDF with custom page template for headers/footers
            doc.build(
                story,
                onFirstPage=lambda c, d: self._add_page_decorations(c, d, charter, first_page=True),
                onLaterPages=lambda c, d: self._add_page_decorations(c, d, charter, first_page=False)
            )
            
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _add_title(self, story: List, charter: Charter, template: Template):
        """Add document title to the story.
        
        Args:
            story: List to append content to
            charter: Charter data
            template: Template data
        """
        # Get project name
        project_name = charter.get_field_value('identification', 'project_name')
        if not project_name:
            project_name = 'Project Charter'
        
        # Add title
        title = Paragraph(project_name, self.styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))
        
        # Add subtitle
        subtitle_text = f"<i>{template.template_name}</i>"
        subtitle = Paragraph(subtitle_text, self.styles['FieldValue'])
        story.append(subtitle)
        story.append(Spacer(1, 0.3 * inch))
    
    def _add_metadata(self, story: List, charter: Charter):
        """Add charter metadata section.
        
        Args:
            story: List to append content to
            charter: Charter data
        """
        metadata = charter.metadata
        
        # Create metadata table
        data = [
            ['Charter ID:', metadata.charter_id],
            ['Status:', metadata.status.upper()],
            ['Created:', self._format_datetime(metadata.created_date)],
            ['Last Modified:', self._format_datetime(metadata.modified_date)]
        ]
        
        table = Table(data, colWidths=[1.5 * inch, 4.5 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), self.SECONDARY_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))
    
    def _add_section(self, story: List, charter: Charter, section):
        """Add a template section to the story.
        
        Args:
            story: List to append content to
            charter: Charter data
            section: Template section to render
        """
        # Section heading
        heading = Paragraph(section.section_title, self.styles['Heading1'])
        story.append(heading)
        story.append(Spacer(1, 0.1 * inch))
        
        # Add fields
        for field in section.fields:
            field_value = charter.get_field_value(section.section_id, field.field_id)
            
            if field.field_type == 'table':
                self._add_table_field(story, field, field_value)
            else:
                self._add_simple_field(story, field, field_value)
        
        story.append(Spacer(1, 0.2 * inch))
    
    def _add_simple_field(self, story: List, field, value: Any):
        """Add a simple field (text, date, number, etc.) to the story.
        
        Args:
            story: List to append content to
            field: Template field definition
            value: Field value
        """
        # Format value based on field type
        if value is None or value == '':
            formatted_value = '<i>Not specified</i>'
        elif field.field_type == 'currency':
            formatted_value = self._format_currency(value)
        elif field.field_type == 'date':
            formatted_value = self._format_date(value)
        elif field.field_type == 'number':
            formatted_value = str(value)
        else:
            formatted_value = str(value)
        
        # Create field label and value
        label = Paragraph(f"<b>{field.field_label}:</b>", self.styles['FieldLabel'])
        value_para = Paragraph(formatted_value, self.styles['FieldValue'])
        
        # Add to story
        story.append(label)
        story.append(value_para)
    
    def _add_table_field(self, story: List, field, value: List[List[str]]):
        """Add a table field to the story.
        
        Args:
            story: List to append content to
            field: Template field definition
            value: Table data (list of rows)
        """
        # Field label
        label = Paragraph(f"<b>{field.field_label}:</b>", self.styles['FieldLabel'])
        story.append(label)
        story.append(Spacer(1, 0.1 * inch))
        
        if not value or len(value) <= 1:  # Only header or empty
            no_data = Paragraph('<i>No data entered</i>', self.styles['FieldValue'])
            story.append(no_data)
            return
        
        # Get column headers
        headers = value[0] if value else []
        data_rows = value[1:] if len(value) > 1 else []
        
        # Calculate column widths (distribute available width)
        available_width = self.PAGE_WIDTH - (2 * self.MARGIN)
        num_cols = len(headers)
        col_width = available_width / num_cols if num_cols > 0 else available_width
        col_widths = [col_width] * num_cols
        
        # Format table data with Paragraphs for text wrapping
        table_data = []
        
        # Add headers
        header_row = [Paragraph(str(h), self.styles['TableHeader']) for h in headers]
        table_data.append(header_row)
        
        # Add data rows
        for row in data_rows:
            formatted_row = [Paragraph(str(cell), self.styles['TableCell']) for cell in row]
            table_data.append(formatted_row)
        
        # Create table
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Apply table style
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.PRIMARY_COLOR),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.HEADER_BG]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.1 * inch))
    
    def _add_page_decorations(
        self,
        canvas_obj: canvas.Canvas,
        doc,
        charter: Charter,
        first_page: bool = False
    ):
        """Add headers and footers to pages.
        
        Args:
            canvas_obj: ReportLab canvas object
            doc: Document object
            charter: Charter data
            first_page: Whether this is the first page
        """
        canvas_obj.saveState()
        
        # Add header (not on first page)
        if not first_page:
            project_name = charter.get_field_value('identification', 'project_name') or 'Project Charter'
            canvas_obj.setFont('Helvetica', 9)
            canvas_obj.setFillColor(self.SECONDARY_COLOR)
            canvas_obj.drawString(
                self.MARGIN,
                self.PAGE_HEIGHT - 0.5 * inch,
                project_name[:80]  # Truncate if too long
            )
            
            # Draw header line
            canvas_obj.setStrokeColor(self.ACCENT_COLOR)
            canvas_obj.setLineWidth(1)
            canvas_obj.line(
                self.MARGIN,
                self.PAGE_HEIGHT - 0.6 * inch,
                self.PAGE_WIDTH - self.MARGIN,
                self.PAGE_HEIGHT - 0.6 * inch
            )
        
        # Add footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.gray)
        
        # Page number
        page_num = f"Page {doc.page}"
        canvas_obj.drawRightString(
            self.PAGE_WIDTH - self.MARGIN,
            0.5 * inch,
            page_num
        )
        
        # Generation timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        canvas_obj.drawString(
            self.MARGIN,
            0.5 * inch,
            f"Generated: {timestamp}"
        )
        
        # Draw footer line
        canvas_obj.setStrokeColor(self.ACCENT_COLOR)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(
            self.MARGIN,
            0.7 * inch,
            self.PAGE_WIDTH - self.MARGIN,
            0.7 * inch
        )
        
        canvas_obj.restoreState()
    
    def _format_currency(self, value: Any) -> str:
        """Format a currency value.
        
        Args:
            value: Currency value to format
            
        Returns:
            Formatted currency string
        """
        try:
            amount = float(value)
            return f"${amount:,.2f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_date(self, value: str) -> str:
        """Format a date value.
        
        Args:
            value: Date string in ISO format
            
        Returns:
            Formatted date string
        """
        try:
            if isinstance(value, str) and value:
                # Try parsing as ISO format
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%B %d, %Y')
        except (ValueError, AttributeError):
            pass
        return str(value) if value else ''
    
    def _format_datetime(self, value: str) -> str:
        """Format a datetime value.
        
        Args:
            value: Datetime string in ISO format
            
        Returns:
            Formatted datetime string
        """
        try:
            if isinstance(value, str) and value:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%B %d, %Y at %I:%M %p')
        except (ValueError, AttributeError):
            pass
        return str(value) if value else ''
