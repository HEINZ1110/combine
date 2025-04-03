#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QListWidget, QComboBox, QFileDialog, 
                            QGroupBox, QRadioButton, QProgressBar, QMessageBox,
                            QSplitter, QTableView, QCheckBox, QSpinBox,
                            QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

class PandasPreviewModel(QAbstractTableModel):
    """Model for displaying pandas DataFrame preview in a QTableView."""
    
    def __init__(self, data, max_rows=100):
        super().__init__()
        # Limit the preview to max_rows
        self._data = data.head(max_rows) if len(data) > max_rows else data

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
            
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None


class CSVMergerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSV-Dateien zusammenführen")
        self.setMinimumSize(800, 600)
        
        self.files_to_merge = []  # List to store file paths
        self.file_dataframes = {}  # Dict to store loaded DataFrames
        self.merged_data = None   # To store the merged result
        
        self.create_ui()
        
    def create_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Top section: File selection
        file_group = QGroupBox("CSV-Dateien")
        file_layout = QVBoxLayout(file_group)
        
        file_buttons_layout = QHBoxLayout()
        self.add_file_button = QPushButton("Dateien hinzufügen")
        self.add_file_button.clicked.connect(self.add_files)
        self.remove_file_button = QPushButton("Entfernen")
        self.remove_file_button.clicked.connect(self.remove_file)
        file_buttons_layout.addWidget(self.add_file_button)
        file_buttons_layout.addWidget(self.remove_file_button)
        file_buttons_layout.addStretch()
        file_layout.addLayout(file_buttons_layout)
        
        self.file_list = QListWidget()
        self.file_list.currentRowChanged.connect(self.file_selected)
        file_layout.addWidget(self.file_list)
        
        main_layout.addWidget(file_group)
        
        # Middle section: Merge options
        options_group = QGroupBox("Zusammenführungsoptionen")
        options_layout = QFormLayout(options_group)
        
        self.merge_strategy_combo = QComboBox()
        self.merge_strategy_combo.addItems([
            "Anfügen (Dateien nacheinander anfügen)",
            "Vereinigung (Alle Einträge, keine Duplikate)",
            "Schnittmenge (Nur gemeinsame Einträge)",
            "Aktualisieren (Einträge aktualisieren/hinzufügen)"
        ])
        options_layout.addRow("Strategie:", self.merge_strategy_combo)
        
        self.conflict_resolution_combo = QComboBox()
        self.conflict_resolution_combo.addItems([
            "Erstes Vorkommen behalten",
            "Letztes Vorkommen behalten",
            "Längeren Wert behalten",
            "Werte zusammenführen"
        ])
        options_layout.addRow("Bei Konflikten:", self.conflict_resolution_combo)
        
        self.match_columns_checkbox = QCheckBox("Nach Spalte abgleichen")
        options_layout.addRow("", self.match_columns_checkbox)
        
        self.match_column_combo = QComboBox()
        self.match_column_combo.setEnabled(False)
        options_layout.addRow("Abgleichspalte:", self.match_column_combo)
        
        self.match_columns_checkbox.toggled.connect(self.match_column_combo.setEnabled)
        
        main_layout.addWidget(options_group)
        
        # Preview section
        preview_group = QGroupBox("Vorschau")
        preview_layout = QVBoxLayout(preview_group)
        
        preview_buttons_layout = QHBoxLayout()
        self.preview_button = QPushButton("Vorschau generieren")
        self.preview_button.clicked.connect(self.generate_preview)
        preview_buttons_layout.addWidget(self.preview_button)
        preview_buttons_layout.addStretch()
        
        self.preview_info_label = QLabel("Keine Vorschau verfügbar")
        preview_buttons_layout.addWidget(self.preview_info_label)
        
        preview_layout.addLayout(preview_buttons_layout)
        
        self.preview_table = QTableView()
        preview_layout.addWidget(self.preview_table)
        
        main_layout.addWidget(preview_group)
        
        # Bottom section: Progress and buttons
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)
        
        button_layout = QHBoxLayout()
        self.merge_button = QPushButton("Zusammenführen")
        self.merge_button.clicked.connect(self.merge_files)
        self.merge_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.merge_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
    def add_files(self):
        """Add files to the merge list."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "CSV-Dateien auswählen", "", "CSV-Dateien (*.csv);;Alle Dateien (*)"
        )
        
        if file_paths:
            for path in file_paths:
                # Only add if not already in list
                if path not in self.files_to_merge:
                    self.files_to_merge.append(path)
                    self.file_list.addItem(os.path.basename(path))
                    
                    # Load the file data
                    try:
                        df = pd.read_csv(path, sep=None, engine='python')
                        self.file_dataframes[path] = df
                        
                        # Update match column combo box with column names from first file
                        if len(self.files_to_merge) == 1:
                            self.match_column_combo.clear()
                            self.match_column_combo.addItems(df.columns.tolist())
                    except Exception as e:
                        QMessageBox.warning(self, "Fehler beim Laden", 
                                           f"Die Datei {os.path.basename(path)} konnte nicht geladen werden: {str(e)}")
            
            # Enable merge button if we have at least two files
            self.merge_button.setEnabled(len(self.files_to_merge) >= 2)
            
    def remove_file(self):
        """Remove the selected file from the list."""
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            file_path = self.files_to_merge[current_row]
            self.files_to_merge.pop(current_row)
            if file_path in self.file_dataframes:
                del self.file_dataframes[file_path]
            self.file_list.takeItem(current_row)
            
            # Disable merge button if we have less than two files
            self.merge_button.setEnabled(len(self.files_to_merge) >= 2)
            
    def file_selected(self, row):
        """Handle file selection in the list."""
        self.remove_file_button.setEnabled(row >= 0)
        
    def generate_preview(self):
        """Generate a preview of the merged data."""
        if len(self.files_to_merge) < 2:
            QMessageBox.warning(self, "Warnung", "Mindestens zwei Dateien müssen zum Zusammenführen ausgewählt werden.")
            return
            
        try:
            # Store the merge result temporarily
            self.merged_data = self.perform_merge()
            
            # Show preview in table
            preview_model = PandasPreviewModel(self.merged_data, max_rows=100)
            self.preview_table.setModel(preview_model)
            
            # Update preview info
            rows, cols = self.merged_data.shape
            self.preview_info_label.setText(f"Vorschau: {rows} Zeilen, {cols} Spalten")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler bei der Vorschau", f"Fehler beim Erstellen der Vorschau: {str(e)}")
            self.preview_info_label.setText("Fehler bei der Vorschau")
            
    def merge_files(self):
        """Perform the merge operation and return the result."""
        if len(self.files_to_merge) < 2:
            QMessageBox.warning(self, "Warnung", "Mindestens zwei Dateien müssen zum Zusammenführen ausgewählt werden.")
            return
            
        try:
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # If we didn't generate a preview, do the merge now
            if self.merged_data is None:
                self.merged_data = self.perform_merge()
            
            self.progress_bar.setValue(50)
            
            # Ask user for save location
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Zusammengeführte CSV-Datei speichern", "", "CSV-Dateien (*.csv);;Alle Dateien (*)"
            )
            
            if save_path:
                self.merged_data.to_csv(save_path, index=False)
                self.progress_bar.setValue(100)
                
                QMessageBox.information(
                    self, 
                    "Zusammenführung abgeschlossen", 
                    f"Die Dateien wurden erfolgreich zusammengeführt und unter {save_path} gespeichert."
                )
                self.accept()  # Close dialog with success
            else:
                self.progress_bar.setVisible(False)
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Fehler bei der Zusammenführung", f"Fehler beim Zusammenführen: {str(e)}")
            
    def perform_merge(self):
        """Perform the actual merge operation based on selected options."""
        if not self.file_dataframes:
            raise ValueError("Keine Dateien geladen")
            
        # Get options
        strategy_index = self.merge_strategy_combo.currentIndex()
        conflict_index = self.conflict_resolution_combo.currentIndex()
        use_match_column = self.match_columns_checkbox.isChecked()
        match_column = self.match_column_combo.currentText() if use_match_column else None
        
        # Get dataframes list
        dfs = list(self.file_dataframes.values())
        
        # Perform merge based on strategy
        if strategy_index == 0:  # Append
            result = pd.concat(dfs, ignore_index=True)
            
            # Handle duplicates based on conflict resolution
            if use_match_column and match_column in result.columns:
                if conflict_index == 0:  # Keep first occurrence
                    result = result.drop_duplicates(subset=match_column, keep='first')
                elif conflict_index == 1:  # Keep last occurrence
                    result = result.drop_duplicates(subset=match_column, keep='last')
                elif conflict_index == 2:  # Keep longer value
                    # This is more complex, group by match column and pick the longest value for each column
                    pass  # Would need custom implementation
                elif conflict_index == 3:  # Merge values
                    # This is more complex, would need to join values
                    pass  # Would need custom implementation
                    
        elif strategy_index == 1:  # Union
            # Concatenate all and remove duplicates
            result = pd.concat(dfs, ignore_index=True)
            if use_match_column and match_column in result.columns:
                result = result.drop_duplicates(subset=match_column)
            else:
                result = result.drop_duplicates()
                
        elif strategy_index == 2:  # Intersection
            # This is more complex, find common records
            # Start with the first dataframe
            result = dfs[0]
            for df in dfs[1:]:
                if use_match_column and match_column in result.columns and match_column in df.columns:
                    # Inner merge on the match column
                    result = pd.merge(result, df, on=match_column, how='inner')
                else:
                    # Without a match column, we can use all columns, but this might not be what user expects
                    common_cols = list(set(result.columns) & set(df.columns))
                    if common_cols:
                        result = pd.merge(result, df, on=common_cols, how='inner')
                    else:
                        # No common columns to merge on
                        result = pd.DataFrame()  # Empty result
                        break
                        
        elif strategy_index == 3:  # Update
            # Start with the first dataframe
            result = dfs[0].copy()
            for df in dfs[1:]:
                if use_match_column and match_column in result.columns and match_column in df.columns:
                    # Update existing records and add new ones
                    common_rows = result[match_column].isin(df[match_column])
                    # For common rows, update values
                    if conflict_index == 0:  # Keep first occurrence (don't update)
                        pass  # Nothing to do
                    elif conflict_index == 1:  # Keep last occurrence (update)
                        for idx, row in df[df[match_column].isin(result[match_column])].iterrows():
                            match_value = row[match_column]
                            result.loc[result[match_column] == match_value, df.columns] = row
                    # Add new rows
                    new_rows = df[~df[match_column].isin(result[match_column])]
                    result = pd.concat([result, new_rows], ignore_index=True)
                else:
                    # Without a match column, just append
                    result = pd.concat([result, df], ignore_index=True)
        
        return result