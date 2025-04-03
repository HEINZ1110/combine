#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QLineEdit, QGroupBox,
                            QFormLayout, QCheckBox, QDateEdit, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QDate, QRegExp

class AdvancedSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Erweiterte Suche")
        self.setMinimumWidth(600)
        
        self.columns = []  # Will be populated with column names
        self.create_ui()
        
    def create_ui(self):
        layout = QVBoxLayout(self)
        
        # Create search criteria widgets
        criteria_group = QGroupBox("Suchkriterien")
        criteria_layout = QVBoxLayout(criteria_group)
        
        # Text search
        text_search_layout = QHBoxLayout()
        self.column_combo = QComboBox()
        self.column_combo.addItems(self.columns)
        
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["enthält", "beginnt mit", "endet mit", "ist gleich", "ist nicht gleich"])
        
        self.search_value = QLineEdit()
        
        text_search_layout.addWidget(QLabel("Spalte:"))
        text_search_layout.addWidget(self.column_combo)
        text_search_layout.addWidget(QLabel("Bedingung:"))
        text_search_layout.addWidget(self.operator_combo)
        text_search_layout.addWidget(QLabel("Wert:"))
        text_search_layout.addWidget(self.search_value)
        
        criteria_layout.addLayout(text_search_layout)
        
        # Date range (if applicable)
        date_group = QGroupBox("Datumsbereich")
        date_group.setCheckable(True)
        date_group.setChecked(False)
        date_layout = QFormLayout(date_group)
        
        self.date_column = QComboBox()
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit(QDate.currentDate())
        
        date_layout.addRow("Datumsspalte:", self.date_column)
        date_layout.addRow("Von:", self.start_date)
        date_layout.addRow("Bis:", self.end_date)
        
        criteria_layout.addWidget(date_group)
        
        # Case sensitivity
        self.case_sensitive = QCheckBox("Groß-/Kleinschreibung beachten")
        criteria_layout.addWidget(self.case_sensitive)
        
        layout.addWidget(criteria_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        self.search_button = button_box.button(QDialogButtonBox.Ok)
        self.search_button.setText("Suchen")
        
        layout.addWidget(button_box)
        
    def set_columns(self, columns):
        """Update column lists when data changes."""
        self.columns = columns
        self.column_combo.clear()
        self.column_combo.addItems(columns)
        
        # Update date columns (assume columns with 'date' in the name)
        self.date_column.clear()
        date_columns = [col for col in columns if 'date' in col.lower() or 'datum' in col.lower()]
        self.date_column.addItems(date_columns if date_columns else columns)
        
    def get_search_criteria(self):
        """Get the search criteria as a dict."""
        return {
            'column': self.column_combo.currentText(),
            'operator': self.operator_combo.currentText(),
            'value': self.search_value.text(),
            'case_sensitive': self.case_sensitive.isChecked(),
            'use_date_range': self.date_group.isChecked(),
            'date_column': self.date_column.currentText(),
            'start_date': self.start_date.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date.date().toString("yyyy-MM-dd")
        }

class CustomProxyModel(QSortFilterProxyModel):
    """Enhanced proxy model for advanced filtering."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_criteria = {}
        
    def set_filter_criteria(self, criteria):
        self.filter_criteria = criteria
        self.invalidateFilter()
        
    def filterAcceptsRow(self, source_row, source_parent):
        # Implementation