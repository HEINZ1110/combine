#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                            QLabel, QPushButton, QShortcut, QTableWidget,
                            QTableWidgetItem, QHeaderView, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


class ShortcutDialog(QDialog):
    """Dialog to display available keyboard shortcuts."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tastenkombinationen")
        self.setMinimumSize(600, 400)
        
        self.create_ui()
        
    def create_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel(
            "Folgende Tastenkombinationen sind in der Foto-Katalog Verwaltung verfügbar:"
        )
        layout.addWidget(info_label)
        
        # Create table for shortcuts
        self.shortcuts_table = QTableWidget()
        self.shortcuts_table.setColumnCount(2)
        self.shortcuts_table.setHorizontalHeaderLabels(["Aktion", "Tastenkombination"])
        self.shortcuts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Add shortcuts to table
        self.add_shortcuts()
        
        layout.addWidget(self.shortcuts_table)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
    def add_shortcuts(self):
        """Add all shortcut information to the table."""
        shortcuts = [
            ("Datei öffnen", "Ctrl+O"),
            ("Speichern", "Ctrl+S"),
            ("Speichern unter", "Ctrl+Shift+S"),
            ("CSV-Dateien zusammenführen", "Ctrl+M"),
            ("Portfolio exportieren", "Ctrl+E"),
            ("Suchen", "Ctrl+F"),
            ("Nächstes Bild", "Pfeil rechts"),
            ("Vorheriges Bild", "Pfeil links"),
            ("Zum Hauptpanel", "Alt+1"),
            ("Zum Vorschau-Panel", "Alt+2"),
            ("Hilfe anzeigen", "F1"),
            ("Tastenkombinationen anzeigen", "Ctrl+K"),
            ("Programm beenden", "Ctrl+Q")
        ]
        
        self.shortcuts_table.setRowCount(len(shortcuts))
        
        for i, (action, key) in enumerate(shortcuts):
            self.shortcuts_table.setItem(i, 0, QTableWidgetItem(action))
            self.shortcuts_table.setItem(i, 1, QTableWidgetItem(key))


def enhance_keyboard_navigation(window):
    """Apply keyboard navigation enhancements to the main window."""
    
    # Store references to shortcuts to prevent garbage collection
    window.shortcuts = []
    
    # Add shortcuts for main functions
    merge_shortcut = QShortcut(QKeySequence("Ctrl+M"), window)
    merge_shortcut.activated.connect(window.show_csv_merger)
    window.shortcuts.append(merge_shortcut)
    
    export_shortcut = QShortcut(QKeySequence("Ctrl+E"), window)
    export_shortcut.activated.connect(window.show_portfolio_exporter)
    window.shortcuts.append(export_shortcut)
    
    # Add shortcut to show shortcuts dialog
    show_shortcuts_shortcut = QShortcut(QKeySequence("Ctrl+K"), window)
    show_shortcuts_shortcut.activated.connect(lambda: show_shortcuts_dialog(window))
    window.shortcuts.append(show_shortcuts_shortcut)
    
    # Additional navigation shortcuts
    next_image_shortcut = QShortcut(QKeySequence(Qt.Key_Right), window)
    next_image_shortcut.activated.connect(lambda: navigate_images(window, 1))
    window.shortcuts.append(next_image_shortcut)
    
    prev_image_shortcut = QShortcut(QKeySequence(Qt.Key_Left), window)
    prev_image_shortcut.activated.connect(lambda: navigate_images(window, -1))
    window.shortcuts.append(prev_image_shortcut)
    
    # Panel focus shortcuts
    main_panel_shortcut = QShortcut(QKeySequence("Alt+1"), window)
    main_panel_shortcut.activated.connect(lambda: window.table_view.setFocus())
    window.shortcuts.append(main_panel_shortcut)
    
    preview_panel_shortcut = QShortcut(QKeySequence("Alt+2"), window)
    preview_panel_shortcut.activated.connect(lambda: window.preview_widget.setFocus())
    window.shortcuts.append(preview_panel_shortcut)
    
    # Add menu items for shortcuts
    shortcuts_action = window.help_menu.addAction("Tastenkombinationen...")
    shortcuts_action.setShortcut(QKeySequence("Ctrl+K"))
    shortcuts_action.triggered.connect(lambda: show_shortcuts_dialog(window))
    
    # Update status bar with hint about shortcuts
    window.statusBar.showMessage("Tipp: Drücken Sie Ctrl+K, um alle Tastenkombinationen anzuzeigen")


def show_shortcuts_dialog(window):
    """Show the keyboard shortcuts dialog."""
    dialog = ShortcutDialog(window)
    dialog.exec_()


def navigate_images(window, direction):
    """Navigate to next/previous image in the table."""
    if window.table_view.model() is None:
        return
        
    current_index = window.table_view.currentIndex()
    if not current_index.isValid():
        # Select first row if nothing is selected
        window.table_view.selectRow(0)
        return
        
    row = current_index.row()
    new_row = row + direction
    
    # Check if new row is valid
    if 0 <= new_row < window.table_view.model().rowCount():
        window.table_view.selectRow(new_row)