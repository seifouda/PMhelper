"""PDF report generator for DPCI assessments."""

from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..models.dpci_model import DPCIAssessment, DPCICalculator


class DPCIPDFGenerator:
    """PDF report generator for DPCI assessments."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if ReportLab is available."""
        return REPORTLAB_AVAILABLE
    
    @staticmethod
    def generate_pdf(assessment: DPCIAssessment, output_path: str) -> bool:
        """Generate PDF report for DPCI assessment."""
        if not REPORTLAB_AVAILABLE:
            print("ReportLab not available. Cannot generate PDF.")
            return False
        
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#34495E'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            story = []
            
            # Title
            story.append(Paragraph("DPCI Assessment Report", title_style))
            story.append(Paragraph(
                f"Design-Complexity Project Index Analysis",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.3*inch))
            
            # Project info
            story.append(Paragraph("Project Information", heading_style))
            project_data = [
                ['Project Name:', assessment.project_name or 'N/A'],
                ['Assessment ID:', assessment.assessment_id],
                ['Date:', assessment.created_date.split('T')[0] if assessment.created_date else 'N/A'],
                ['Assessed By:', assessment.assessed_by or 'N/A']
            ]
            project_table = Table(project_data, colWidths=[2*inch, 4*inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(project_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))
            dpci = assessment.get_dpci_index()
            risk_level = assessment.get_overall_risk_level()
            
            risk_colors = {
                'LOW': colors.HexColor('#27AE60'),
                'MODERATE': colors.HexColor('#F39C12'),
                'HIGH': colors.HexColor('#E67E22'),
                'CRITICAL': colors.HexColor('#E74C3C')
            }
            
            summary_data = [
                ['DPCI Index:', dpci],
                ['Risk Level:', risk_level.value],
                ['Overall Score:', f'{assessment.get_total_score()}/64']
            ]
            summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
                ('BACKGROUND', (1, 1), (1, 1), risk_colors.get(risk_level.value, colors.white)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Dimension scores
            story.append(Paragraph("Dimension Analysis", heading_style))
            
            calculator = DPCICalculator()
            questionnaire = calculator.get_questionnaire_structure()
            dimensions_data = [['Dimension', 'Score', 'Max', 'Percentage', 'Risk']]
            
            for dim_key, dim_info in questionnaire.items():
                score_attr = f"{dim_key.lower()}_score"
                dim_score = getattr(assessment, score_attr)
                max_score = 16
                percentage = (dim_score / max_score) * 100
                risk = calculator.get_dimension_risk_level(dim_score)
                dimensions_data.append([
                    dim_info['title'],
                    str(dim_score),
                    str(max_score),
                    f'{percentage:.1f}%',
                    risk.value
                ])
            
            dimensions_table = Table(dimensions_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
            dimensions_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8)
            ]))
            story.append(dimensions_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Recommendations
            story.append(Paragraph("Recommendations", heading_style))
            pm_rec = assessment.get_pm_recommendations()
            control_rec = assessment.get_control_recommendations()
            
            story.append(Paragraph(f"<b>Project Manager Level:</b> {pm_rec['level']}", styles['Normal']))
            story.append(Paragraph(pm_rec['description'], styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
            
            story.append(Paragraph(f"<b>Control Level:</b> {control_rec['level']}", styles['Normal']))
            story.append(Paragraph(control_rec['description'], styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Actions
            if pm_rec.get('actions'):
                story.append(Paragraph("<b>Recommended Actions:</b>", styles['Normal']))
                for action in pm_rec['actions']:
                    story.append(Paragraph(f"• {action}", styles['Normal']))
            
            # Page break before detailed scores
            story.append(PageBreak())
            
            # Detailed scores
            story.append(Paragraph("Detailed Assessment Scores", heading_style))
            
            questionnaire = calculator.get_questionnaire_structure()
            for dim_key, dim_info in questionnaire.items():
                story.append(Paragraph(f"<b>{dim_info['title']}</b>", styles['Heading3']))
                
                dim_details_attr = f"{dim_key.lower()}_details"
                dim_details = getattr(assessment, dim_details_attr)
                
                criteria_data = [['Criterion', 'Score', 'Response']]
                for criterion in dim_info['criteria']:
                    crit_key = criterion['id']
                    score = dim_details.get(crit_key, 0)
                    response = criterion['levels'].get(score, 'N/A')
                    criteria_data.append([
                        criterion['question'],
                        str(score),
                        response
                    ])
                
                criteria_table = Table(criteria_data, colWidths=[3*inch, 0.6*inch, 3*inch])
                criteria_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#95A5A6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                story.append(criteria_table)
                story.append(Spacer(1, 0.2*inch))
            
            # Footer
            story.append(Spacer(1, 0.4*inch))
            story.append(Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_RIGHT)
            ))
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
