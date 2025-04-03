#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QFileDialog, QGroupBox, 
                            QRadioButton, QProgressBar, QMessageBox, QSpinBox,
                            QCheckBox, QFormLayout, QLineEdit, QTabWidget,
                            QTextEdit, QDialogButtonBox, QWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import webbrowser
import time

# Optional imports - these would be used for PDF generation and image processing
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ExportThread(QThread):
    """Thread to handle export operations without freezing the UI."""
    progress_updated = pyqtSignal(int)
    export_finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, export_format, data, settings):
        super().__init__()
        self.export_format = export_format
        self.data = data
        self.settings = settings
        
    def run(self):
        try:
            # Simulate export progress
            total_steps = 100
            for i in range(total_steps):
                self.progress_updated.emit(i)
                time.sleep(0.01)  # Just to make the progress visible
                
                # Do the actual export work here based on format
                if i == 30:
                    if self.export_format == "HTML":
                        self.export_html()
                    elif self.export_format == "PDF":
                        self.export_pdf()
                    elif self.export_format == "Gallery":
                        self.export_gallery()
            
            self.progress_updated.emit(100)
            self.export_finished.emit(True, f"{self.export_format}-Export abgeschlossen")
            
        except Exception as e:
            self.export_finished.emit(False, f"Fehler beim Export: {str(e)}")
            
    def export_html(self):
        """Export data to HTML format."""
        output_path = self.settings.get('output_path')
        title = self.settings.get('title', 'Foto-Katalog')
        include_images = self.settings.get('include_images', False)
        template = self.settings.get('template', 'grid')
        
        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
        .grid-item {{ border: 1px solid #ddd; padding: 10px; }}
        .grid-item img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
"""
        
        # Add content based on template
        if template == "grid":
            html_content += '        <div class="grid">\n'
            for _, row in self.data.iterrows():
                html_content += '            <div class="grid-item">\n'
                if include_images and 'image_path' in row:
                    html_content += f'                <img src="{row["image_path"]}" alt="{row.get("title", "")}">\n'
                for col, value in row.items():
                    if col != 'image_path' or not include_images:
                        html_content += f'                <p><strong>{col}:</strong> {value}</p>\n'
                html_content += '            </div>\n'
            html_content += '        </div>\n'
        else:  # table view
            html_content += '        <table>\n'
            html_content += '            <tr>\n'
            for col in self.data.columns:
                html_content += f'                <th>{col}</th>\n'
            html_content += '            </tr>\n'
            
            for _, row in self.data.iterrows():
                html_content += '            <tr>\n'
                for col in self.data.columns:
                    cell_value = row[col]
                    if include_images and col == 'image_path':
                        cell_value = f'<img src="{cell_value}" style="max-width: 100px; max-height: 100px;">'
                    html_content += f'                <td>{cell_value}</td>\n'
                html_content += '            </tr>\n'
            html_content += '        </table>\n'
            
        html_content += """    </div>
</body>
</html>"""
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    def export_pdf(self):
        """Export data to PDF format."""
        if not HAS_REPORTLAB:
            raise ImportError("ReportLab ist nicht installiert. Für PDF-Export wird ReportLab benötigt.")
            
        output_path = self.settings.get('output_path')
        title = self.settings.get('title', 'Foto-Katalog')
        page_size = self.settings.get('page_size', 'A4')
        include_images = self.settings.get('include_images', False)
        
        # Choose page size
        page_size_map = {'A4': A4, 'Letter': letter}
        doc_page_size = page_size_map.get(page_size, A4)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=doc_page_size)
        styles = getSampleStyleSheet()
        
        # Create content elements
        elements = []
        
        # Add title
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Create table for data
        table_data = [self.data.columns.tolist()]
        for _, row in self.data.iterrows():
            row_data = []
            for col in self.data.columns:
                cell_value = row[col]
                if include_images and col == 'image_path':
                    if os.path.exists(cell_value):
                        img = PILImage.open(cell_value)
                        img.thumbnail((100, 100), PILImage.ANTIALIAS)
                        img.save("temp_image.jpg")
                        row_data.append(Image("temp_image.jpg", width=1*inch, height=1*inch))
                    else:
                        row_data.append(cell_value)
                else:
                    row_data.append(cell_value)
            table_data.append(row_data)
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
    
    def export_gallery(self):
        """Export data as a simple image gallery."""
        output_path = self.settings.get('output_path')
        title = self.settings.get('title', 'Foto-Katalog')
        
        # Ensure output directory exists
       