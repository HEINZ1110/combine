#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback

try:
    from photo_catalog_reader import MainWindow
    from PyQt5.QtWidgets import QApplication
    
    print("Module erfolgreich importiert")
    
    app = QApplication(sys.argv)
    print("QApplication erstellt")
    
    window = MainWindow()
    print("MainWindow erstellt")
    
    # Integrieren der Erweiterungen ohne Import
    window.csv_merger_dialog = None
    window.show()
    print("Fenster angezeigt")
    
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"Fehler beim Starten des Programms: {e}")
    traceback.print_exc()