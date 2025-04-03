#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                            QTableView, QStatusBar, QAction, QMenu, QMessageBox,
                            QTabWidget, QSplitter)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PyQt5.QtGui import QIcon, QKeySequence, QFont

class PandasModel(QAbstractTableModel):
    """Model for displaying pandas DataFrame in a QTableView."""
    
    def __init__(self, data):
        super().__init__()
        self._data = data

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Variables to store current data
        self.current_file = None
        self.current_data = None
        
        self.setWindowTitle("Foto-Katalog Verwaltung")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set up the status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Bereit")
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar with buttons
        self.create_toolbar()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main content area with table view
        self.create_content_area()
        
        # Initialize empty data
        self.update_table_view(pd.DataFrame())

    def create_toolbar(self):
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.open_button = QPushButton("Öffnen")
        self.open_button.clicked.connect(self.open_file)
        toolbar_layout.addWidget(self.open_button)
        
        self.save_button = QPushButton("Speichern")
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setEnabled(False)
        toolbar_layout.addWidget(self.save_button)
        
        toolbar_layout.addStretch()
        
        self.main_layout.addWidget(toolbar_widget)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&Datei")
        
        open_action = QAction("&Öffnen", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Speichern", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Speichern &als...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Placeholder for other menus to be added by enhancements
        self.tools_menu = menu_bar.addMenu("&Werkzeuge")
        self.help_menu = menu_bar.addMenu("&Hilfe")
        
        about_action = QAction("Ü&ber", self)
        about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(about_action)

    def create_content_area(self):
        # Create splitter for flexible layout
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Table view for the catalog data
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.splitter.addWidget(self.table_view)
        
        # Add preview placeholder (to be used for image preview)
        self.preview_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_widget)
        preview_layout.addWidget(QLabel("Vorschau"))
        self.preview_image = QLabel("Kein Bild ausgewählt")
        self.preview_image.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_image)
        self.splitter.addWidget(self.preview_widget)
        
        # Set initial sizes
        self.splitter.setSizes([700, 500])
        
        self.main_layout.addWidget(self.splitter)
        
    def update_table_view(self, data):
        """Update the table view with new data."""
        self.current_data = data
        model = PandasModel(data)
        self.table_view.setModel(model)
        
        # Update status bar with row/column count
        if not data.empty:
            self.statusBar.showMessage(f"Zeilen: {data.shape[0]}, Spalten: {data.shape[1]}")
            self.save_button.setEnabled(True)
        else:
            self.statusBar.showMessage("Keine Daten geladen")
            self.save_button.setEnabled(False)

    def open_file(self):
        """Open a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CSV-Datei öffnen", "", "CSV-Dateien (*.csv);;Alle Dateien (*)"
        )
        
        if file_path:
            try:
                # Try to detect encoding and separator
                data = pd.read_csv(file_path, sep=None, engine='python')
                self.current_file = file_path
                self.update_table_view(data)
                self.setWindowTitle(f"Foto-Katalog Verwaltung - {os.path.basename(file_path)}")
                self.statusBar.showMessage(f"Datei geöffnet: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Fehler beim Öffnen", f"Die Datei konnte nicht geladen werden: {str(e)}")

    def save_file(self):
        """Save current data to the current file."""
        if not self.current_file:
            self.save_file_as()
            return
            
        if self.current_data is not None and not self.current_data.empty:
            try:
                self.current_data.to_csv(self.current_file, index=False)
                self.statusBar.showMessage(f"Datei gespeichert: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Fehler beim Speichern", f"Die Datei konnte nicht gespeichert werden: {str(e)}")

    def save_file_as(self):
        """Save current data to a new file."""
        if self.current_data is None or self.current_data.empty:
            QMessageBox.warning(self, "Warnung", "Keine Daten zum Speichern vorhanden.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "CSV-Datei speichern", "", "CSV-Dateien (*.csv);;Alle Dateien (*)"
        )
        
        if file_path:
            try:
                self.current_data.to_csv(file_path, index=False)
                self.current_file = file_path
                self.setWindowTitle(f"Foto-Katalog Verwaltung - {os.path.basename(file_path)}")
                self.statusBar.showMessage(f"Datei gespeichert: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Fehler beim Speichern", f"Die Datei konnte nicht gespeichert werden: {str(e)}")

    def show_about(self):
        """Show information about the application."""
        QMessageBox.about(
            self, 
            "Über Foto-Katalog Verwaltung",
            "Foto-Katalog Verwaltung\n\n"
            "Ein Programm zur Verwaltung und Erweiterung von Fotokatalogen.\n\n"
            "Version: 1.0.0"
        )


if __name__ == "__main__":
    from csv_reader_enhancements import integrate_enhancements
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application style
    palette = app.palette()
    app.setPalette(palette)
    
    window = MainWindow()
    
    # Add the enhancements
    integrate_enhancements(window)
    
    window.show()
    
    sys.exit(app.exec_())