#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                           QMessageBox, QStyle, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QPixmap

# Import the modules for both applications
from config import Config
from reader.photo_catalog_reader import MainWindow as ReaderWindow
from writer.main_window import MainWindow as WriterWindow


class LauncherWindow(QMainWindow):
    """Main launcher window to select between Reader and Writer applications."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize configuration
        self.config = Config()
        
        # Set up UI
        self.setWindowTitle("Photo Catalog Application")
        self.setMinimumSize(800, 600)
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        self.create_header()
        
        # App selection buttons
        self.create_app_selection()
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Create the header section with title and description."""
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Photo Catalog Application")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Select which application you want to use:")
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(desc_label)
        
        header_layout.addSpacing(20)
        self.main_layout.addLayout(header_layout)
        
    def create_app_selection(self):
        """Create the application selection buttons."""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        
        # Reader button
        self.reader_button = QPushButton("CSV Reader")
        self.reader_button.setMinimumSize(300, 200)
        self.reader_button.setFont(QFont("Arial", 14))
        self.reader_button.clicked.connect(self.launch_reader)
        self.style_button(self.reader_button, "View and analyze CSV files with metadata")
        buttons_layout.addWidget(self.reader_button)
        
        # Writer button
        self.writer_button = QPushButton("Photo Catalog")
        self.writer_button.setMinimumSize(300, 200)
        self.writer_button.setFont(QFont("Arial", 14))
        self.writer_button.clicked.connect(self.launch_writer)
        self.style_button(self.writer_button, "Manage and organize photos with metadata")
        buttons_layout.addWidget(self.writer_button)
        
        self.main_layout.addLayout(buttons_layout)
        
    def style_button(self, button, description):
        """Add styling and description to a button."""
        # Create a vertical layout for the button content
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add an icon placeholder - you can replace with actual icons
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Add the button text as a label
        text_label = QLabel(button.text())
        text_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Add the description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Set the layout to the button
        button.setLayout(layout)
        
        # Style the button
        button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #dcdcdc;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 2px solid #c0c0c0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
    def create_footer(self):
        """Create the footer section."""
        footer_layout = QHBoxLayout()
        
        # Version information
        version_label = QLabel("Version 1.0.0")
        footer_layout.addWidget(version_label)
        
        # Spacer
        footer_layout.addStretch()
        
        # About button
        about_button = QPushButton("About")
        about_button.clicked.connect(self.show_about)
        footer_layout.addWidget(about_button)
        
        # Exit button
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        footer_layout.addWidget(exit_button)
        
        self.main_layout.addStretch()
        self.main_layout.addLayout(footer_layout)
        
    def launch_reader(self):
        """Launch the CSV Reader application."""
        self.hide()  # Hide the launcher window
        
        self.reader_window = ReaderWindow()
        self.reader_window.setWindowTitle("Photo Catalog - CSV Reader")
        self.reader_window.show()
        
        # Connect the closing signal to reshow this window
        self.reader_window.closeEvent = lambda event: self.on_app_closed(event, self.reader_window)
        
    def launch_writer(self):
        """Launch the Photo Catalog Writer application."""
        self.hide()  # Hide the launcher window
        
        self.writer_window = WriterWindow()
        self.writer_window.setWindowTitle("Photo Catalog - Writer")
        self.writer_window.show()
        
        # Connect the closing signal to reshow this window
        self.writer_window.closeEvent = lambda event: self.on_app_closed(event, self.writer_window)
        
    def on_app_closed(self, event, app_window):
        """Handle the closing of an application window."""
        # Call the original closeEvent if it exists
        if hasattr(app_window, 'original_close_event'):
            app_window.original_close_event(event)
            
        # Show the launcher again
        self.show()
        
    def show_about(self):
        """Show information about the application."""
        QMessageBox.about(
            self,
            "About Photo Catalog Application",
            "Photo Catalog Application\n\n"
            "A unified application for managing, viewing, and organizing photo catalogs.\n\n"
            "Version: 1.0.0\n"
            "© 2025 HEINZ1110"
        )
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = LauncherWindow()
    window.show()
    
    sys.exit(app.exec())