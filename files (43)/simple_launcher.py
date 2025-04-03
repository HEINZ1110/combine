#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class LauncherWindow(QMainWindow):
    """Simple launcher window to start either CSV Reader or Photo Catalog Writer."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Catalog Application")
        self.setMinimumSize(600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Photo Catalog Application")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel("Choose which application to launch:")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)
        
        # Reader button
        self.reader_button = QPushButton("CSV Reader")
        self.reader_button.setMinimumSize(200, 100)
        self.reader_button.clicked.connect(self.launch_reader)
        buttons_layout.addWidget(self.reader_button)
        
        # Writer button
        self.writer_button = QPushButton("Photo Catalog Writer")
        self.writer_button.setMinimumSize(200, 100)
        self.writer_button.clicked.connect(self.launch_writer)
        buttons_layout.addWidget(self.writer_button)
        
        # Exit button
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        main_layout.addWidget(exit_button, alignment=Qt.AlignmentFlag.AlignRight)
    
    def launch_reader(self):
        """Launch CSV Reader application."""
        try:
            self.hide()
            # First, make sure we can import the reader
            from PyQt5.QtWidgets import QApplication, QMainWindow
            
            # Import the reader MainWindow class - adjust path as needed
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'reader'))
            from photo_catalog_reader import MainWindow
            
            self.reader_app = MainWindow()
            self.reader_app.show()
            
            # Store the original close event
            self.reader_app.original_close_event = self.reader_app.closeEvent
            
            # Override close event to show launcher again
            def new_close_event(event):
                if hasattr(self.reader_app, 'original_close_event'):
                    self.reader_app.original_close_event(event)
                self.show()
                
            self.reader_app.closeEvent = new_close_event
            
        except Exception as e:
            self.show()
            QMessageBox.critical(self, "Error", f"Failed to start CSV Reader: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def launch_writer(self):
        """Launch Photo Catalog Writer application."""
        try:
            self.hide()
            # First, make sure we can import writer modules
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'writer'))
            
            # Basic imports for the writer
            from PyQt6.QtWidgets import QMainWindow, QApplication
            
            # Use a simpler, direct approach for launching the writer
            from main_window import MainWindow
            
            self.writer_app = MainWindow()
            self.writer_app.show()
            
            # Store the original close event
            self.writer_app.original_close_event = self.writer_app.closeEvent
            
            # Override close event to show launcher again
            def new_close_event(event):
                if hasattr(self.writer_app, 'original_close_event'):
                    self.writer_app.original_close_event(event)
                self.show()
                
            self.writer_app.closeEvent = new_close_event
            
        except Exception as e:
            self.show()
            QMessageBox.critical(self, "Error", f"Failed to start Photo Catalog Writer: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        window = LauncherWindow()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")