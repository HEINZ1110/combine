import json
from pathlib import Path

class Config:
    """Manages application configuration settings."""

    def __init__(self, config_dir: Path = Path.home() / ".photo_catalog", 
                 config_file: str = "config.json", 
                 categories_file: str = "categories.json"):
        self.config_dir = config_dir
        self.config_file = self.config_dir / config_file
        self.categories_file = self.config_dir / categories_file
        self.config_dir.mkdir(exist_ok=True)
        self.settings = self.load_config()

    def load_config(self) -> dict:
        """Loads configuration settings from file."""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # Return an empty dictionary if the file doesn't exist
        except json.JSONDecodeError:
            print("Error: Invalid JSON in config file. Using default settings.")
            return {}

    def save_config(self, settings: dict):
        """Saves configuration settings to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(settings, f, indent=4)
            self.settings = settings
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_setting(self, key: str, default=None):
        """Gets a configuration setting."""
        return self.settings.get(key, default)

    def set_setting(self, key: str, value):
        """Sets a configuration setting."""
        self.settings[key] = value
        self.save_config(self.settings)
        
    def load_categories(self) -> dict:
        """Loads category settings from file."""
        try:
            with open(self.categories_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default categories if the file doesn't exist
            return {
                "category": ["Art", "Document", "Photograph", "Postcard", "Other"],
                "condition": ["Excellent", "Good", "Fair", "Poor"],
                "location": ["Box 1", "Box 2", "Album 1", "Album 2", "Wall", "Storage"]
            }
        except json.JSONDecodeError:
            print("Error: Invalid JSON in categories file. Using default categories.")
            return {}
            
    def save_categories(self, categories: dict):
        """Saves category settings to file."""
        try:
            with open(self.categories_file, "w") as f:
                json.dump(categories, f, indent=4)
        except Exception as e:
            print(f"Error saving categories: {e}")