from dataclasses import dataclass
import flet as ft

class ThemeManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Store themes
        self.themes = {
            "light": {
                "bg":{
                    "base":"#130925",
                     },
                "text": ft.Colors.BLACK,
                "toolbar": ft.Colors.GREY_300,
                "tabs": {
                    "active": ft.Colors.BLUE,
                    "inactive": ft.Colors.GREY_600,
                    "indicator": ft.Colors.LIGHT_BLUE,
                },
            },
            "dark": {
                "bg":{
                     "base":"#130925",
                     },
                "text": ft.Colors.WHITE,
                "toolbar": {
                    "bg": ft.Colors.BLACK,
                    "text": ft.Colors.WHITE,
                    "ready": ft.Colors.GREEN,
                    "not_ready": ft.Colors.RED,
                     },
                "board": {
                    "bg": "#a19bac",
                    },
                "board_bar":{
                    "bg":"#150f1a",
                    "text":"white"
                     },
                "device": {
                    "bg":"#2c2c2c",
                    "header":"black",
                     },
                "board_component": {
                    "bg": "#303030",
                    "content": "#3a4f48",
                     },
                "port": {
                    "bg":"#c7c7c7",
                    "bg_connected": "#feea3b",
                    "bg_hover": "#cf3131",
                     },
                "project_explorer": {
                    "bg": "#0b031a",
                    "color" : "white",
                    },
                "tabs": {
                    "active": ft.Colors.PURPLE,
                    "inactive": ft.Colors.GREY_500,
                    "indicator": ft.Colors.DEEP_PURPLE,
                },
            },
        }

        # Default theme
        self.current_theme = self.themes["dark"]

    def set_theme(self, theme_name):
        """Switch to a new theme."""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
        else:
            raise ValueError(f"Theme '{theme_name}' does not exist.")

    def get_color(self, key):
        """Get a color from the current theme."""
        return self.current_theme.get(key, None)

    def get_nested_color(self, category, key):
        """Get a nested color from the current theme (e.g., tabs)."""
        return self.current_theme.get(category, {}).get(key, None)

    def get_text_style(self, key):
        """Example method for returning a text style."""
        return ft.TextStyle(color=self.get_color(key))
