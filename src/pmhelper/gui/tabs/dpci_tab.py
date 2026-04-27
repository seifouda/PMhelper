"""DPCI Assessment Tab - Design-Complexity Project Index."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
import uuid

from ..models.dpci_model import DPCIAssessment, DPCICalculator
from ..services.dpci_service import DPCIService
from ..utils.dpci_pdf_generator import DPCIPDFGenerator


class DPCITab(ttk.Frame):
    """DPCI Assessment tab for evaluating project complexity and risk."""

    def __init__(self, parent):
        super().__init__(parent)
        self.calculator = DPCICalculator()
        self.service = DPCIService()
        self.current_assessment: Optional[DPCIAssessment] = None
        self.current_file: Optional[str] = None

        self._create_ui()
        self._new_assessment()

    def _create_ui(self):
        """Create the user interface."""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Toolbar
        self._create_toolbar()

        # Main content with scrollbar
        self._create_content()

    def _create_toolbar(self):
        """Create toolbar with actions."""
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        ttk.Button(
            toolbar,
            text="New",
            command=self._new_assessment).pack(
            side='left',
            padx=2)
        ttk.Button(
            toolbar,
            text="Open",
            command=self._open_assessment).pack(
            side='left',
            padx=2)
        ttk.Button(
            toolbar,
            text="Save",
            command=self._save_assessment).pack(
            side='left',
            padx=2)
        ttk.Button(
            toolbar,
            text="Save As",
            command=self._save_as_assessment).pack(
            side='left',
            padx=2)

        ttk.Separator(
            toolbar,
            orient='vertical').pack(
            side='left',
            fill='y',
            padx=5)

        ttk.Button(
            toolbar,
            text="Export PDF",
            command=self._export_pdf).pack(
            side='left',
            padx=2)

        ttk.Separator(
            toolbar,
            orient='vertical').pack(
            side='left',
            fill='y',
            padx=5)

        ttk.Button(
            toolbar,
            text="Calculate",
            command=self._calculate_dpci).pack(
            side='left',
            padx=2)

    def _create_content(self):
        """Create main content area."""
        # Canvas with scrollbar
        canvas_frame = ttk.Frame(self)
        canvas_frame.grid(row=1, column=0, sticky='nsew')
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient='vertical',
            command=canvas.yview)

        self.content_frame = ttk.Frame(canvas)
        self.content_frame.bind(
            '<Configure>', lambda e: canvas.configure(
                scrollregion=canvas.bbox('all')))

        canvas.create_window((0, 0), window=self.content_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind mousewheel
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(
            int(-1 * (e.delta / 120)), 'units'))

        # Project info section
        self._create_project_info()

        # Assessment sections
        self._create_assessment_sections()

        # Results section
        self._create_results_section()

    def _create_project_info(self):
        """Create project information section."""
        info_frame = ttk.LabelFrame(
            self.content_frame,
            text="Project Information",
            padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)

        row = 0
        ttk.Label(
            info_frame,
            text="Project Name:").grid(
            row=row,
            column=0,
            sticky='w',
            pady=5)
        self.project_name_var = tk.StringVar()
        ttk.Entry(
            info_frame,
            textvariable=self.project_name_var,
            width=50).grid(
            row=row,
            column=1,
            sticky='ew',
            pady=5,
            padx=5)

        row += 1
        ttk.Label(
            info_frame,
            text="Assessed By:").grid(
            row=row,
            column=0,
            sticky='w',
            pady=5)
        self.assessed_by_var = tk.StringVar()
        ttk.Entry(
            info_frame,
            textvariable=self.assessed_by_var,
            width=50).grid(
            row=row,
            column=1,
            sticky='ew',
            pady=5,
            padx=5)

        row += 1
        ttk.Label(
            info_frame,
            text="Organization:").grid(
            row=row,
            column=0,
            sticky='w',
            pady=5)
        self.organization_var = tk.StringVar()
        ttk.Entry(
            info_frame,
            textvariable=self.organization_var,
            width=50).grid(
            row=row,
            column=1,
            sticky='ew',
            pady=5,
            padx=5)

        row += 1
        ttk.Label(
            info_frame,
            text="Description:").grid(
            row=row,
            column=0,
            sticky='nw',
            pady=5)
        self.description_text = tk.Text(
            info_frame, height=3, width=50, wrap='word')
        self.description_text.grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)

        info_frame.grid_columnconfigure(1, weight=1)

    def _create_assessment_sections(self):
        """Create assessment questionnaire sections."""
        self.dimension_vars = {}

        questionnaire = self.calculator.get_questionnaire_structure()

        for dim_key, dim_info in questionnaire.items():
            # Create dimension frame
            dim_frame = ttk.LabelFrame(
                self.content_frame,
                text=f"{dim_info['title']} - {dim_info['description']}",
                padding=10
            )
            dim_frame.pack(fill='x', padx=10, pady=10)

            self.dimension_vars[dim_key] = {}

            # Create criteria
            for idx, criterion in enumerate(dim_info['criteria']):
                crit_key = criterion['id']

                # Question label
                q_label = ttk.Label(
                    dim_frame,
                    text=f"{idx + 1}. {criterion['question']}",
                    wraplength=700,
                    font=('TkDefaultFont', 9, 'bold')
                )
                q_label.pack(anchor='w', pady=(10 if idx > 0 else 0, 5))

                # Radio buttons for levels
                var = tk.IntVar(value=0)
                self.dimension_vars[dim_key][crit_key] = var

                # levels is a dict {score: text}
                for score in sorted(criterion['levels'].keys()):
                    text = criterion['levels'][score]
                    rb = ttk.Radiobutton(
                        dim_frame,
                        text=f"[{score}] {text}",
                        variable=var,
                        value=score
                    )
                    rb.pack(anchor='w', padx=20, pady=2)

    def _create_results_section(self):
        """Create results display section."""
        results_frame = ttk.LabelFrame(
            self.content_frame,
            text="Assessment Results",
            padding=10)
        results_frame.pack(fill='x', padx=10, pady=10)

        # Results grid
        row = 0

        # DPCI Index
        ttk.Label(
            results_frame,
            text="DPCI Index:",
            font=(
                'TkDefaultFont',
                10,
                'bold')).grid(
            row=row,
            column=0,
            sticky='w',
            pady=5)
        self.dpci_label = ttk.Label(
            results_frame, text="Not calculated", font=(
                'TkDefaultFont', 12))
        self.dpci_label.grid(row=row, column=1, sticky='w', pady=5, padx=10)

        row += 1

        # Risk Level
        ttk.Label(
            results_frame,
            text="Overall Risk Level:",
            font=(
                'TkDefaultFont',
                10,
                'bold')).grid(
            row=row,
            column=0,
            sticky='w',
            pady=5)
        self.risk_label = ttk.Label(
            results_frame, text="Not calculated", font=(
                'TkDefaultFont', 12))
        self.risk_label.grid(row=row, column=1, sticky='w', pady=5, padx=10)

        row += 1

        # Total Score
        ttk.Label(
            results_frame,
            text="Total Score:",
            font=(
                'TkDefaultFont',
                10,
                'bold')).grid(
            row=row,
            column=0,
            sticky='w',
            pady=5)
        self.score_label = ttk.Label(results_frame, text="0 / 64")
        self.score_label.grid(row=row, column=1, sticky='w', pady=5, padx=10)

        row += 1

        # Dimension scores
        ttk.Label(
            results_frame,
            text="Dimension Scores:",
            font=(
                'TkDefaultFont',
                10,
                'bold')).grid(
            row=row,
            column=0,
            sticky='nw',
            pady=5)
        self.dimensions_label = ttk.Label(
            results_frame, text="Not calculated", justify='left')
        self.dimensions_label.grid(
            row=row, column=1, sticky='w', pady=5, padx=10)

        row += 1

        # Recommendations
        ttk.Label(
            results_frame,
            text="Recommendations:",
            font=(
                'TkDefaultFont',
                10,
                'bold')).grid(
            row=row,
            column=0,
            sticky='nw',
            pady=5)

        rec_frame = ttk.Frame(results_frame)
        rec_frame.grid(row=row, column=1, sticky='ew', pady=5, padx=10)

        self.recommendations_text = tk.Text(
            rec_frame, height=8, width=70, wrap='word', state='disabled')
        self.recommendations_text.pack(fill='both', expand=True)

        results_frame.grid_columnconfigure(1, weight=1)

    def _new_assessment(self):
        """Create new assessment."""
        self.current_assessment = DPCIAssessment(
            assessment_id=str(uuid.uuid4()))
        self.current_file = None
        self._load_assessment_to_ui()

    def _open_assessment(self):
        """Open existing assessment."""
        filepath = filedialog.askopenfilename(
            title="Open DPCI Assessment",
            initialdir=self.service.get_assessments_dir(),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        assessment = self.service.load_assessment(filepath)
        if assessment:
            self.current_assessment = assessment
            self.current_file = filepath
            self._load_assessment_to_ui()
        else:
            messagebox.showerror("Error", "Failed to load assessment file.")

    def _save_assessment(self):
        """Save current assessment."""
        if not self.current_file:
            self._save_as_assessment()
            return

        self._update_assessment_from_ui()

        if self.service.save_assessment(
                self.current_assessment,
                self.current_file):
            messagebox.showinfo("Success", "Assessment saved successfully.")
        else:
            messagebox.showerror("Error", "Failed to save assessment.")

    def _save_as_assessment(self):
        """Save assessment to new file."""
        self._update_assessment_from_ui()

        suggested_name = f"dpci_{
            self.current_assessment.project_name or 'assessment'}_{
            self.current_assessment.assessment_id[
                :8]}.json"
        suggested_name = "".join(
            c for c in suggested_name if c.isalnum() or c in (
                '_', '-', '.'))

        filepath = filedialog.asksaveasfilename(
            title="Save DPCI Assessment As",
            initialdir=self.service.get_assessments_dir(),
            initialfile=suggested_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        if self.service.save_assessment(self.current_assessment, filepath):
            self.current_file = filepath
            messagebox.showinfo("Success", "Assessment saved successfully.")
        else:
            messagebox.showerror("Error", "Failed to save assessment.")

    def _export_pdf(self):
        """Export assessment to PDF."""
        if not DPCIPDFGenerator.is_available():
            messagebox.showerror(
                "Error", "ReportLab library not installed. Cannot export to PDF.")
            return

        self._update_assessment_from_ui()

        suggested_name = f"dpci_report_{
            self.current_assessment.project_name or 'assessment'}_{
            self.current_assessment.assessment_id[
                :8]}.pdf"
        suggested_name = "".join(
            c for c in suggested_name if c.isalnum() or c in (
                '_', '-', '.'))

        filepath = filedialog.asksaveasfilename(
            title="Export DPCI Report as PDF",
            initialdir=self.service.get_export_dir(),
            initialfile=suggested_name,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if not filepath:
            return

        if DPCIPDFGenerator.generate_pdf(self.current_assessment, filepath):
            messagebox.showinfo(
                "Success", f"PDF report exported successfully to:\n{filepath}")
        else:
            messagebox.showerror("Error", "Failed to generate PDF report.")

    def _calculate_dpci(self):
        """Calculate DPCI and update results display."""
        self._update_assessment_from_ui()
        self._update_results_display()

    def _update_assessment_from_ui(self):
        """Update assessment object from UI values."""
        self.current_assessment.project_name = self.project_name_var.get()
        self.current_assessment.assessed_by = self.assessed_by_var.get()
        self.current_assessment.organization = self.organization_var.get()
        self.current_assessment.description = self.description_text.get(
            '1.0', 'end-1c')

        # Update dimension scores
        for dim_key, criteria_vars in self.dimension_vars.items():
            total_score = sum(var.get() for var in criteria_vars.values())
            score_attr = f"{dim_key.lower()}_score"
            setattr(self.current_assessment, score_attr, total_score)

            # Update details
            details = {crit_key: var.get()
                       for crit_key, var in criteria_vars.items()}
            details_attr = f"{dim_key.lower()}_details"
            setattr(self.current_assessment, details_attr, details)

    def _load_assessment_to_ui(self):
        """Load assessment object into UI."""
        self.project_name_var.set(self.current_assessment.project_name or '')
        self.assessed_by_var.set(self.current_assessment.assessed_by or '')
        self.organization_var.set(self.current_assessment.organization or '')

        self.description_text.delete('1.0', 'end')
        if self.current_assessment.description:
            self.description_text.insert(
                '1.0', self.current_assessment.description)

        # Load dimension scores
        for dim_key, criteria_vars in self.dimension_vars.items():
            details_attr = f"{dim_key.lower()}_details"
            details = getattr(self.current_assessment, details_attr)
            for crit_key, var in criteria_vars.items():
                var.set(details.get(crit_key, 0))

        self._update_results_display()

    def _update_results_display(self):
        """Update results display with calculated values."""
        dpci = self.current_assessment.get_dpci_index()
        risk_level = self.current_assessment.get_overall_risk_level()
        total_score = self.current_assessment.get_total_score()

        # Update labels
        self.dpci_label.config(text=dpci)

        # Color code risk level
        risk_colors = {
            'LOW': '#27AE60',
            'MODERATE': '#F39C12',
            'HIGH': '#E67E22',
            'CRITICAL': '#E74C3C'
        }
        self.risk_label.config(
            text=risk_level.value,
            foreground=risk_colors.get(risk_level.value, 'black')
        )

        self.score_label.config(text=f"{total_score} / 64")

        # Dimension scores
        dim_text = ""
        questionnaire = self.calculator.get_questionnaire_structure()
        for dim_key, dim_info in questionnaire.items():
            score_attr = f"{dim_key.lower()}_score"
            score = getattr(self.current_assessment, score_attr)
            risk = self.calculator.get_dimension_risk_level(score)
            dim_text += f"{dim_info['title']}: {score}/16 ({risk.value})\n"
        self.dimensions_label.config(text=dim_text.strip())

        # Recommendations
        pm_rec = self.current_assessment.get_pm_recommendations()
        control_rec = self.current_assessment.get_control_recommendations()

        rec_text = f"Project Manager Level: {pm_rec['level']}\n"
        rec_text += f"{pm_rec['description']}\n\n"
        rec_text += f"Control Level: {control_rec['level']}\n"
        rec_text += f"{control_rec['description']}\n"

        if pm_rec.get('actions'):
            rec_text += "\nRecommended Actions:\n"
            for action in pm_rec['actions']:
                rec_text += f"• {action}\n"

        self.recommendations_text.config(state='normal')
        self.recommendations_text.delete('1.0', 'end')
        self.recommendations_text.insert('1.0', rec_text)
        self.recommendations_text.config(state='disabled')
