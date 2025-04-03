#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback

def main():
    try:
        print("Starting application...")
        print(f"Python version: {sys.version}")
        print(f"Current directory: {os.getcwd()}")
        
        # Check PyQt6 installation
        try:
            print("Checking PyQt6...")
            from PyQt6.QtWidgets import QApplication
            print("PyQt6 imported successfully")
        except ImportError as e:
            print(f"Error importing PyQt6: {e}")
            print("Please install PyQt6 with: pip install PyQt6")
            return
        
        # Try to import the config module
        try:
            print("Importing config...")
            from config import Config
            print("Config imported successfully")
        except ImportError as e:
            print(f"Error importing config: {e}")
            print("Make sure config.py is in the current directory")
            return
        
        # Try to import the reader module
        try:
            print("Checking reader module...")
            from reader import __init__
            print("Reader module found")
        except ImportError as e:
            print(f"Error with reader module: {e}")
            print("Make sure the reader directory exists and contains __init__.py")
            return
        
        # Try to import the writer module
        try:
            print("Checking writer module...")
            from writer import __init__
            print("Writer module found")
        except ImportError as e:
            print(f"Error with writer module: {e}")
            print("Make sure the writer directory exists and contains __init__.py")
            return
            
        # If we get here, import the actual application
        try:
            print("Starting the application...")
            from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
            
            app = QApplication(sys.argv)
            
            # Create a simple window to test PyQt works properly
            window = QMainWindow()
            window.setWindowTitle("Test Window")
            window.setGeometry(100, 100, 400, 200)
            
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)
            label = QLabel("If you can see this, PyQt is working!")
            layout.addWidget(label)
            
            window.setCentralWidget(central_widget)
            window.show()
            
            print("Application started successfully. Close the window to exit.")
            sys.exit(app.exec())
            
        except Exception as e:
            print(f"Error starting application: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    # Keep console open to read error messages
    input("Press Enter to exit...")