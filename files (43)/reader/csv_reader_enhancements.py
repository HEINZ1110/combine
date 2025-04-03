#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from csv_merger import CSVMergerDialog
from portfolio_exporter import PortfolioExportDialog
from keyboard_navigation import enhance_keyboard_navigation
from PyQt5.QtWidgets import QAction, QMessageBox


def integrate_enhancements(window):
    """Add all enhancements to the main window."""
    
    # Add functions to main window
    add_csv_merger_functionality(window)
    add_portfolio_export_functionality(window)
    
    # Apply keyboard navigation enhancements
    enhance_keyboard_navigation(window)
    
    # Update status bar
    window.statusBar.showMessage("Erweiterungen wurden geladen. Drücken Sie Ctrl+K für Tastenkombinationen.")


def add_csv_merger_functionality(window):
    """Add CSV merger functionality to the main window."""
    
    # Add method to window
    def show_csv_merger():
        if window.csv_merger_dialog is None:
            window.csv_merger_dialog = CSVMergerDialog(window)
        window.csv_merger_dialog.exec_()
        
        # If a file was produced, ask if it should be opened
        if window.csv_merger_dialog.result() == CSVMergerDialog.Accepted:
            response = QMessageBox.question(
                window,
                "Datei öffnen",
                "Möchten Sie die zusammengeführte Datei öffnen?",
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.Yes:
                # This would need to be implemented based on how the merger returns results
                pass
    
    # Store reference for dialog
    window.csv_merger_dialog = None
    
    # Add method to window
    window.show_csv_merger = show_csv_merger
    
    # Add menu item
    merge_action = QAction("CSV-Dateien &zusammenführen...", window)
    merge_action.setShortcut("Ctrl+M")
    merge_action.triggered.connect(window.show_csv_merger)
    window.tools_menu.addAction(merge_action)


def add_portfolio_export_functionality(window):
    """Add portfolio export functionality to the main window."""
    
    # Add method to window
    def show_portfolio_exporter():
        if window.current_data is None or window.current_data.empty:
            QMessageBox.warning(
                window,
                "Keine Daten",
                "Es sind keine Daten zum Exportieren vorhanden. "
                "Bitte öffnen Sie zuerst eine Datei."
            )
            return
            
        exporter_dialog = PortfolioExportDialog(window.current_data, window)
        exporter_dialog.exec_()
    
    # Add method to window
    window.show_portfolio_exporter = show_portfolio_exporter
    
    # Add menu item
    export_action = QAction("Portfolio &exportieren...", window)
    export_action.setShortcut("Ctrl+E")
    export_action.triggered.connect(window.show_portfolio_exporter)
    window.tools_menu.addAction(export_action)