import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (QMainWindow, QWidget, QListWidget, QListWidgetItem, 
                            QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QComboBox, QTabWidget, QDialog, 
                            QTextEdit, QSplitter, QFileDialog, QMenu, 
                            QMessageBox, QRadioButton, QButtonGroup, QLayout,
                            QLayoutItem, QSpacerItem, QSizePolicy, QScrollArea,
                            QStatusBar, QToolBar, QAction)
from PyQt5.QtCore import Qt, QSize, QMimeData, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QDragEnterEvent, QImage, QTransform, QDropEvent

# Import from parent directory
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config
from writer.image_service import ImageService
from writer.metadata import ImageMetadata

CONFIG_DIR = Path.home() / ".photo_catalog"
CONFIG_FILE = CONFIG_DIR / "config.json"
CATEGORIES_FILE = CONFIG_DIR / "categories.json"

class ImageItem:
    """Class to represent an image item with all its metadata"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.image_service = ImageService()
        self.metadata = ImageMetadata(self.filename)
        self._image = None
        self._thumbnail = None
        self._load_image_info()
        self._calculate_physical_size()
        
    def _load_image_info(self):
        try:
            self._image = self.image_service.load_image(self.file_path)
            # Additional image info loading could go here
        except Exception as e:
            print(f"Error loading image {self.file_path}: {e}")
            
    def _calculate_physical_size(self):
        # This would calculate physical size based on DPI and pixel dimensions
        # For now, just placeholder
        self.metadata.physical_size = "Unknown"
        
    def get_thumbnail(self, size=QSize(120, 120)):
        if self._thumbnail is None or self._thumbnail.size() != size:
            if self._image and not self._image.isNull():
                self._thumbnail = self.image_service.generate_thumbnail(self._image, size)
            else:
                # Create an empty thumbnail with text
                self._thumbnail = QPixmap(size)
                self._thumbnail.fill(Qt.lightGray)
        return self._thumbnail
        
    def to_dict(self) -> Dict:
        """Convert image item to dictionary for saving"""
        result = self.metadata.to_dict()
        result["file_path"] = self.file_path
        return result
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'ImageItem':
        """Create image item from dictionary"""
        if "file_path" not in data:
            raise ValueError("Missing file_path in data")
            
        item = cls(data["file_path"])
        item.metadata = ImageMetadata.from_dict({k: v for k, v in data.items() if k != "file_path"})
        return item


class ImageListWidget(QListWidget):
    """Custom list widget for displaying images with thumbnails"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(100, 100))
        self.main_window = None
        
    def set_main_window(self, main_window):
        self.main_window = main_window
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls() and self.main_window:
            file_paths = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if os.path.isfile(file_path):
                        file_paths.append(file_path)
            
            if file_paths and self.main_window:
                self.main_window.add_images(file_paths)
                
            event.accept()
        else:
            event.ignore()
            
    def get_selected_indices(self) -> List[int]:
        """Get indices of selected items"""
        return [self.row(item) for item in self.selectedItems()]


class CategoryManager(QDialog):
    """Dialog for managing categories"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Category Manager")
        self.setMinimumSize(600, 400)
        self.categories = {}
        self.load_categories()
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for category groups
        self.tab_widget = QTabWidget()
        
        # Populate tabs from categories
        self.refresh_tabs()
        
        main_layout.addWidget(self.tab_widget)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        add_group_button = QPushButton("Add Group")
        add_group_button.clicked.connect(self.add_group)
        buttons_layout.addWidget(add_group_button)
        
        buttons_layout.addStretch()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_categories)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
    def refresh_tabs(self):
        """Refresh the tab widget with current categories"""
        self.tab_widget.clear()
        
        for group_name, values in self.categories.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            # List widget for values
            list_widget = QListWidget()
            for value in values:
                item = QListWidgetItem(value)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                list_widget.addItem(item)
            
            list_widget.itemChanged.connect(lambda item: self.value_changed(group_name, item))
            list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            list_widget.customContextMenuRequested.connect(
                lambda pos, lw=list_widget, gn=group_name: self.show_value_context_menu(pos, lw, gn)
            )
            
            tab_layout.addWidget(list_widget)
            
            # Add value button
            add_button = QPushButton("Add Value")
            add_button.clicked.connect(lambda _, gn=group_name: self.add_value(gn, "New Value"))
            tab_layout.addWidget(add_button)
            
            self.tab_widget.addTab(tab, group_name)
            
    def add_group(self):
        """Add a new category group"""
        group_name, ok = QFileDialog.getSaveFileName(
            self, "New Category Group", "", "Text files (*.txt)"
        )
        
        if ok and group_name:
            group_name = os.path.basename(group_name).replace(".txt", "")
            if group_name and group_name not in self.categories:
                self.categories[group_name] = ["New Value"]
                self.refresh_tabs()
                
    def delete_group(self, group_name):
        """Delete a category group"""
        if group_name in self.categories:
            confirm = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete the category group '{group_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                del self.categories[group_name]
                self.refresh_tabs()
                
    def add_value(self, group_name, value):
        """Add a value to a category group"""
        if group_name in self.categories:
            self.categories[group_name].append(value)
            self.refresh_tabs()
            
    def value_changed(self, group_name, item):
        """Handle value changes in the list widget"""
        if group_name in self.categories:
            row = item.listWidget().row(item)
            if 0 <= row < len(self.categories[group_name]):
                self.categories[group_name][row] = item.text()
                
    def show_value_context_menu(self, pos, list_widget, group_name):
        """Show context menu for category values"""
        item = list_widget.itemAt(pos)
        if item:
            menu = QMenu()
            delete_action = menu.addAction("Delete")
            action = menu.exec_(list_widget.mapToGlobal(pos))
            
            if action == delete_action:
                row = list_widget.row(item)
                if 0 <= row < len(self.categories[group_name]):
                    self.categories[group_name].pop(row)
                    self.refresh_tabs()
                    
    def save_categories(self):
        """Save categories to file"""
        config = Config()
        config.save_categories(self.categories)
        self.accept()
        
    def load_categories(self):
        """Load categories from file"""
        config = Config()
        self.categories = config.load_categories()


class ImagePreviewDialog(QDialog):
    """Dialog for image preview with manipulation options"""
    
    def __init__(self, images: List[ImageItem], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.setMinimumSize(800, 600)
        
        self.images = images
        self.current_index = 0
        self.zoom_factor = 1.0
        self.rotation = 0
        
        self.init_ui()
        self.update_preview()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous)
        nav_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next)
        nav_layout.addWidget(self.next_button)
        
        nav_layout.addStretch()
        
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        nav_layout.addWidget(self.zoom_in_button)
        
        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        nav_layout.addWidget(self.zoom_out_button)
        
        self.zoom_reset_button = QPushButton("Reset Zoom")
        self.zoom_reset_button.clicked.connect(self.zoom_reset)
        nav_layout.addWidget(self.zoom_reset_button)
        
        self.rotate_left_button = QPushButton("Rotate Left")
        self.rotate_left_button.clicked.connect(self.rotate_left)
        nav_layout.addWidget(self.rotate_left_button)
        
        self.rotate_right_button = QPushButton("Rotate Right")
        self.rotate_right_button.clicked.connect(self.rotate_right)
        nav_layout.addWidget(self.rotate_right_button)
        
        main_layout.addLayout(nav_layout)
        
        # Image preview area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Use a scroll area for larger images
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        
        main_layout.addWidget(scroll_area)
        
        # Info area
        self.info_label = QLabel()
        main_layout.addWidget(self.info_label)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
    def update_preview(self):
        """Update the image preview"""
        if not self.images:
            return
            
        image_item = self.images[self.current_index]
        
        # Update navigation buttons
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.images) - 1)
        
        # Load the image
        try:
            image = QImage(image_item.file_path)
            if image.isNull():
                self.image_label.setText("Error loading image")
                return
                
            # Apply rotation if needed
            if self.rotation != 0:
                transform = QTransform().rotate(self.rotation)
                image = image.transformed(transform)
                
            # Create pixmap and scale with zoom factor
            pixmap = QPixmap.fromImage(image)
            scaled_size = pixmap.size() * self.zoom_factor
            scaled_pixmap = pixmap.scaled(
                scaled_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            
            # Update the label size to match the pixmap
            self.image_label.setFixedSize(scaled_pixmap.size())
            
            # Update info
            file_size = os.path.getsize(image_item.file_path)
            file_size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
            
            info_text = (
                f"Filename: {image_item.filename} | "
                f"Size: {image.width()}x{image.height()} px | "
                f"File size: {file_size_str} | "
                f"Category: {image_item.metadata.category} | "
                f"Zoom: {self.zoom_factor*100:.0f}%"
            )
            self.info_label.setText(info_text)
            
        except Exception as e:
            self.image_label.setText(f"Error displaying image: {str(e)}")
            
    def show_next(self):
        """Show the next image"""
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.update_preview()
            
    def show_previous(self):
        """Show the previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_preview()
            
    def zoom_in(self):
        """Zoom in the image"""
        self.zoom_factor *= 1.2
        self.update_preview()
        
    def zoom_out(self):
        """Zoom out the image"""
        self.zoom_factor /= 1.2
        self.update_preview()
        
    def zoom_reset(self):
        """Reset zoom to original size"""
        self.zoom_factor = 1.0
        self.update_preview()
        
    def rotate_left(self):
        """Rotate the image left (counter-clockwise)"""
        self.rotation = (self.rotation - 90) % 360
        self.update_preview()
        
    def rotate_right(self):
        """Rotate the image right (clockwise)"""
        self.rotation = (self.rotation + 90) % 360
        self.update_preview()


class QFlowLayout(QLayout):
    """Custom flow layout for the image preview area"""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.item_list = []
        
    def __del__(self):
        while self.item_list:
            item = self.item_list.pop()
            item.widget().deleteLater()
            
    def addItem(self, item):
        self.item_list.append(item)
        
    def count(self):
        return len(self.item_list)
        
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
        
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
        
    def expandingDirections(self):
        return Qt.Horizontal | Qt.Vertical
        
    def hasHeightForWidth(self):
        return True
        
    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height
        
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)
        
    def sizeHint(self):
        return self.minimumSize()
        
    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
            
        margin = self.contentsMargins()
        size += QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size
        
    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            widget = item.widget()
            item_width = item.sizeHint().width()
            item_height = item.sizeHint().height()
            
            if x + item_width > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing
                line_height = 0
                
            if not testOnly:
                item.setGeometry(QRect(x, y, item_width, item_height))
                
            x = x + item_width + spacing
            line_height = max(line_height, item_height)
            
        return y + line_height - rect.y()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize services and data
        self.config = Config()
        self.image_service = ImageService()
        self.image_items = []
        
        # Set up UI
        self.setWindowTitle("Photo Catalog")
        self.setMinimumSize(1200, 800)
        self.init_ui()
        
        # Load settings
        self.load_settings()
        
    def init_ui(self):
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu
        self.create_menus()
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side (image lists)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # List 1 (main catalog)
        list1_label = QLabel("Image Catalog")
        left_layout.addWidget(list1_label)
        
        self.list_widget = ImageListWidget()
        self.list_widget.setMinimumHeight(300)
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.list_widget.itemSelectionChanged.connect(self.update_preview)
        self.list_widget.set_main_window(self)
        left_layout.addWidget(self.list_widget)
        
        # Buttons for list manipulation
        list_buttons_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected)
        list_buttons_layout.addWidget(self.delete_button)
        
        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self.move_selected_up)
        list_buttons_layout.addWidget(self.move_up_button)
        
        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self.move_selected_down)
        list_buttons_layout.addWidget(self.move_down_button)
        
        left_layout.addLayout(list_buttons_layout)
        
        splitter.addWidget(left_widget)
        
        # Right side (preview and metadata)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Preview section
        preview_label = QLabel("Preview")
        right_layout.addWidget(preview_label)
        
        self.preview_image = QLabel()
        self.preview_image.setFixedSize(300, 300)
        self.preview_image.setAlignment(Qt.AlignCenter)
        self.preview_image.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        right_layout.addWidget(self.preview_image, 0, Qt.AlignCenter)
        
        # Metadata section
        metadata_label = QLabel("Metadata")
        right_layout.addWidget(metadata_label)
        
        # Category selection
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(
            lambda text: self.category_selected("category", text)
        )
        category_layout.addWidget(self.category_combo)
        
        right_layout.addLayout(category_layout)
        
        # Text content
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(100)
        self.text_edit.textChanged.connect(self.update_text)
        text_layout.addWidget(self.text_edit)
        
        right_layout.addLayout(text_layout)
        
        # Comments
        comment_layout = QHBoxLayout()
        comment_layout.addWidget(QLabel("Comment:"))
        
        self.comment_edit = QTextEdit()
        self.comment_edit.setMaximumHeight(100)
        self.comment_edit.textChanged.connect(self.update_comment)
        comment_layout.addWidget(self.comment_edit)
        
        right_layout.addLayout(comment_layout)
        
        # Condition
        condition_layout = QHBoxLayout()
        condition_layout.addWidget(QLabel("Condition:"))
        
        self.condition_combo = QComboBox()
        self.condition_combo.currentTextChanged.connect(self.update_condition)
        condition_layout.addWidget(self.condition_combo)
        
        right_layout.addLayout(condition_layout)
        
        # Additional metadata fields could be added here
        
        # Add to splitter
        splitter.addWidget(right_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Update categories
        self.reload_categories()
        
    def create_toolbar(self):
        """Create the main toolbar"""
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        
        # Add actions
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file_dialog)
        self.toolbar.addAction(open_action)
        
        # Add more toolbar actions as needed
        
    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        export_menu = file_menu.addMenu("&Export")
        
        export_csv_action = QAction("Export to &CSV...", self)
        export_csv_action.triggered.connect(self.export_csv)
        export_menu.addAction(export_csv_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        deselect_all_action = QAction("&Deselect All", self)
        deselect_all_action.setShortcut("Ctrl+D")
        deselect_all_action.triggered.connect(self.deselect_all)
        edit_menu.addAction(deselect_all_action)
        
        edit_menu.addSeparator()
        
        category_manager_action = QAction("&Category Manager...", self)
        category_manager_action.triggered.connect(self.open_category_manager)
        edit_menu.addAction(category_manager_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        preview_action = QAction("&Preview Selected Images...", self)
        preview_action.triggered.connect(self.open_preview_dialog)
        view_menu.addAction(preview_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def open_file_dialog(self):
        """Open file dialog to select images"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        
        if file_paths:
            self.add_images(file_paths)
            
    def add_images(self, file_paths):
        """Add images to the catalog"""
        for file_path in file_paths:
            try:
                # Create image item
                image_item = ImageItem(file_path)
                self.image_items.append(image_item)
                
                # Create list item
                list_item = QListWidgetItem(os.path.basename(file_path))
                list_item.setIcon(QIcon(image_item.get_thumbnail()))
                list_item.setToolTip(file_path)
                
                self.list_widget.addItem(list_item)
                
            except Exception as e:
                self.status_bar.showMessage(f"Error adding image {file_path}: {str(e)}")
                
        # Update status
        self.status_bar.showMessage(f"Added {len(file_paths)} images")
        
    def get_selected_image_indices(self) -> List[int]:
        """Get indices of selected images"""
        return self.list_widget.get_selected_indices()
        
    def get_selected_images(self) -> List[ImageItem]:
        """Get selected image items"""
        indices = self.get_selected_image_indices()
        return [self.image_items[i] for i in indices if i < len(self.image_items)]
        
    def update_preview(self):
        """Update the preview image"""
        selected_images = self.get_selected_images()
        
        if selected_images:
            # Show first selected image
            image_item = selected_images[0]
            
            # Display thumbnail
            pixmap = image_item.get_thumbnail(QSize(300, 300))
            self.preview_image.setPixmap(pixmap)
            
            # Update metadata display
            self.update_details(image_item)
        else:
            # Clear preview
            self.preview_image.clear()
            self.preview_image.setText("No image selected")
            
    def update_details(self, image: ImageItem):
        """Update metadata fields for selected image"""
        # Temporarily block signals to prevent recursive updates
        self.text_edit.blockSignals(True)
        self.comment_edit.blockSignals(True)
        self.category_combo.blockSignals(True)
        self.condition_combo.blockSignals(True)
        
        # Update text fields
        self.text_edit.setText(image.metadata.text)
        self.comment_edit.setText(image.metadata.comment)
        
        # Update category
        index = self.category_combo.findText(image.metadata.category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
            
        # Update condition
        index = self.condition_combo.findText(image.metadata.condition)
        if index >= 0:
            self.condition_combo.setCurrentIndex(index)
            
        # Re-enable signals
        self.text_edit.blockSignals(False)
        self.comment_edit.blockSignals(False)
        self.category_combo.blockSignals(False)
        self.condition_combo.blockSignals(False)
        
    def update_text(self):
        """Update text for selected images"""
        selected_images = self.get_selected_images()
        if selected_images:
            text = self.text_edit.toPlainText()
            for image in selected_images:
                image.metadata.text = text
                
    def update_comment(self):
        """Update comment for selected images"""
        selected_images = self.get_selected_images()
        if selected_images:
            comment = self.comment_edit.toPlainText()
            for image in selected_images:
                image.metadata.comment = comment
                
    def update_condition(self, condition):
        """Update condition for selected images"""
        selected_images = self.get_selected_images()
        if selected_images:
            for image in selected_images:
                image.metadata.condition = condition
                
    def reload_categories(self):
        """Reload categories from configuration"""
        categories = self.config.load_categories()
        
        # Update category combo boxes
        self.category_combo.clear()
        if "category" in categories:
            self.category_combo.addItems(categories["category"])
            
        self.condition_combo.clear()
        if "condition" in categories:
            self.condition_combo.addItems(categories["condition"])
            
    def category_selected(self, group, text):
        """Handle category selection"""
        selected_images = self.get_selected_images()
        if selected_images:
            for image in selected_images:
                if group == "category":
                    image.metadata.category = text
                elif group == "condition":
                    image.metadata.condition = text
                    
    def move_selected_up(self):
        """Move selected items up in the list"""
        indices = sorted(self.get_selected_image_indices())
        if not indices or indices[0] == 0:
            return
            
        for i in indices:
            if i > 0:
                # Swap items in the list widget
                item = self.list_widget.takeItem(i)
                self.list_widget.insertItem(i - 1, item)
                
                # Swap items in the data list
                self.image_items[i], self.image_items[i - 1] = self.image_items[i - 1], self.image_items[i]
                
                # Re-select the item
                self.list_widget.setCurrentRow(i - 1)
                
    def move_selected_down(self):
        """Move selected items down in the list"""
        indices = sorted(self.get_selected_image_indices(), reverse=True)
        if not indices or indices[-1] >= self.list_widget.count() - 1:
            return
            
        for i in indices:
            if i < self.list_widget.count() - 1:
                # Swap items in the list widget
                item = self.list_widget.takeItem(i)
                self.list_widget.insertItem(i + 1, item)
                
                # Swap items in the data list
                self.image_items[i], self.image_items[i + 1] = self.image_items[i + 1], self.image_items[i]
                
                # Re-select the item
                self.list_widget.setCurrentRow(i + 1)
                
    def delete_selected(self):
        """Delete selected items"""
        indices = sorted(self.get_selected_image_indices(), reverse=True)
        if not indices:
            return
            
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {len(indices)} selected images?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            for i in indices:
                self.list_widget.takeItem(i)
                self.image_items.pop(i)
                
            self.status_bar.showMessage(f"Deleted {len(indices)} images")
            
    def open_preview_dialog(self):
        """Open image preview dialog"""
        selected_images = self.get_selected_images()
        if selected_images:
            dialog = ImagePreviewDialog(selected_images, self)
            dialog.exec_()
            
    def open_category_manager(self):
        """Open category manager dialog"""
        dialog = CategoryManager(self)
        if dialog.exec_() == QDialog.Accepted:
            self.reload_categories()
            
    def select_all(self):
        """Select all items in the list"""
        self.list_widget.selectAll()
        
    def deselect_all(self):
        """Deselect all items in the list"""
        self.list_widget.clearSelection()
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Photo Catalog",
            "Photo Catalog\n\n"
            "A tool for organizing and cataloging photo collections.\n\n"
            "Version 1.0.0\n"
            "© 2025 HEINZ1110"
        )
        
    def load_settings(self):
        """Load application settings"""
        # Window geometry
        geometry = self.config.get_setting("window_geometry")
        if geometry:
            self.restoreGeometry(bytes.fromhex(geometry))
            
        # Other settings can be loaded here
        
    def save_settings(self):
        """Save application settings"""
        # Window geometry
        self.config.set_setting("window_geometry", self.saveGeometry().hex())
        
        # Other settings can be saved here
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save settings
        self.save_settings()
        
        # Accept the event
        event.accept()
        
    def export_csv(self):
        """Export data to CSV file"""
        if not self.image_items:
            QMessageBox.warning(self, "Warning", "No images to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    "Filename", "Category", "Text", "Comment", "Condition",
                    "Physical Size", "Date", "Location", "Artist", "Provenance", "File Path"
                ])
                
                # Write data
                for img in self.image_items:
                    writer.writerow([
                        img.filename,
                        img.metadata.category,
                        img.metadata.text,
                        img.metadata.comment,
                        img.metadata.condition,
                        img.metadata.physical_size,
                        img.metadata.date,
                        img.metadata.location,
                        img.metadata.artist,
                        img.metadata.provenance,
                        img.file_path
                    ])
                    
            self.status_bar.showMessage(f"Exported {len(self.image_items)} images to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV: {e}")