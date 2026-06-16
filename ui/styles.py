from __future__ import annotations


class VSCodeColors:
    """VSCode dark theme color palette."""

    BG_PRIMARY = "#1e1e1e"
    BG_SECONDARY = "#252526"
    BG_TERTIARY = "#2d2d2d"
    BG_INPUT = "#3c3c3c"
    BG_HOVER = "#2a2d2e"
    BG_SELECTED = "#094771"
    BG_SIDEBAR = "#252526"
    BG_STATUS = "#007acc"
    BG_TAB_ACTIVE = "#1e1e1e"
    BG_TAB_INACTIVE = "#2d2d2d"
    BG_TITLEBAR = "#323233"
    BG_DANGER = "#5a1d1d"

    FG_PRIMARY = "#cccccc"
    FG_SECONDARY = "#969696"
    FG_DIMMED = "#6a6a6a"
    FG_BRIGHT = "#e0e0e0"
    FG_WHITE = "#ffffff"
    FG_ACCENT = "#3794ff"
    FG_SUCCESS = "#4ec9b0"
    FG_WARNING = "#cca700"
    FG_ERROR = "#f44747"
    FG_HIGHLIGHT = "#1899e6"

    BORDER = "#3c3c3c"
    BORDER_FOCUS = "#007acc"
    BORDER_ERROR = "#f44747"
    BORDER_SUCCESS = "#4ec9b0"

    SCROLLBAR_BG = "#1e1e1e"
    SCROLLBAR_THUMB = "#424242"


DARK_STYLE = f"""
QMainWindow {{
    background-color: {VSCodeColors.BG_PRIMARY};
    color: {VSCodeColors.FG_PRIMARY};
}}
QWidget {{
    background-color: {VSCodeColors.BG_PRIMARY};
    color: {VSCodeColors.FG_PRIMARY};
    font-family: 'Segoe UI', 'Ubuntu', 'Cantarell', sans-serif;
    font-size: 13px;
}}
QMenuBar {{
    background-color: {VSCodeColors.BG_TITLEBAR};
    color: {VSCodeColors.FG_PRIMARY};
    border-bottom: 1px solid {VSCodeColors.BORDER};
    padding: 2px;
}}
QMenuBar::item:selected {{
    background-color: {VSCodeColors.BG_HOVER};
}}
QMenu {{
    background-color: {VSCodeColors.BG_SECONDARY};
    color: {VSCodeColors.FG_PRIMARY};
    border: 1px solid {VSCodeColors.BORDER};
}}
QMenu::item:selected {{
    background-color: {VSCodeColors.BG_SELECTED};
}}
QToolBar {{
    background-color: {VSCodeColors.BG_TITLEBAR};
    border-bottom: 1px solid {VSCodeColors.BORDER};
    spacing: 2px;
    padding: 2px;
}}
QToolButton {{
    background-color: transparent;
    color: {VSCodeColors.FG_PRIMARY};
    border: none;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 13px;
}}
QToolButton:hover {{
    background-color: {VSCodeColors.BG_HOVER};
}}
QToolButton:pressed {{
    background-color: {VSCodeColors.BG_SELECTED};
}}
QSplitter::handle {{
    background-color: {VSCodeColors.BORDER};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:vertical {{
    height: 1px;
}}
QListView, QTreeView {{
    background-color: {VSCodeColors.BG_SECONDARY};
    color: {VSCodeColors.FG_PRIMARY};
    border: none;
    outline: none;
    padding: 4px;
    font-size: 13px;
}}
QListView::item, QTreeView::item {{
    padding: 8px 10px;
    border-radius: 4px;
    margin: 1px 2px;
    min-height: 32px;
}}
QListView::item:selected, QTreeView::item:selected {{
    background-color: {VSCodeColors.BG_SELECTED};
    color: {VSCodeColors.FG_WHITE};
}}
QListView::item:hover, QTreeView::item:hover {{
    background-color: {VSCodeColors.BG_HOVER};
}}
QHeaderView::section {{
    background-color: {VSCodeColors.BG_SECONDARY};
    color: {VSCodeColors.FG_SECONDARY};
    border: none;
    border-right: 1px solid {VSCodeColors.BORDER};
    border-bottom: 2px solid {VSCodeColors.BORDER};
    padding: 8px 12px;
    font-weight: bold;
    font-size: 12px;
}}
QTableWidget {{
    background-color: {VSCodeColors.BG_SECONDARY};
    color: {VSCodeColors.FG_PRIMARY};
    border: none;
    gridline-color: {VSCodeColors.BORDER};
    selection-background-color: {VSCodeColors.BG_SELECTED};
    font-size: 13px;
}}
QTableWidget::item {{
    padding: 8px 10px;
    border: none;
    min-height: 36px;
}}
QTableWidget::item:selected {{
    background-color: {VSCodeColors.BG_SELECTED};
    color: {VSCodeColors.FG_WHITE};
}}
QLineEdit {{
    background-color: {VSCodeColors.BG_INPUT};
    color: {VSCodeColors.FG_PRIMARY};
    border: 1px solid {VSCodeColors.BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    selection-background-color: {VSCodeColors.BG_SELECTED};
    font-size: 13px;
}}
QLineEdit:focus {{
    border-color: {VSCodeColors.BORDER_FOCUS};
}}
QLineEdit:disabled {{
    background-color: {VSCodeColors.BG_TERTIARY};
    color: {VSCodeColors.FG_DIMMED};
}}
QTextEdit, QPlainTextEdit {{
    background-color: {VSCodeColors.BG_INPUT};
    color: {VSCodeColors.FG_PRIMARY};
    border: 1px solid {VSCodeColors.BORDER};
    border-radius: 4px;
    padding: 8px;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
    selection-background-color: {VSCodeColors.BG_SELECTED};
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {VSCodeColors.BORDER_FOCUS};
}}
QSpinBox, QDoubleSpinBox {{
    background-color: {VSCodeColors.BG_INPUT};
    color: {VSCodeColors.FG_PRIMARY};
    border: 1px solid {VSCodeColors.BORDER};
    border-radius: 4px;
    padding: 4px 8px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {VSCodeColors.BORDER_FOCUS};
}}
QComboBox {{
    background-color: {VSCodeColors.BG_INPUT};
    color: {VSCodeColors.FG_PRIMARY};
    border: 1px solid {VSCodeColors.BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    min-height: 20px;
}}
QComboBox:focus {{
    border-color: {VSCodeColors.BORDER_FOCUS};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {VSCodeColors.FG_SECONDARY};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {VSCodeColors.BG_SECONDARY};
    color: {VSCodeColors.FG_PRIMARY};
    border: 1px solid {VSCodeColors.BORDER};
    selection-background-color: {VSCodeColors.BG_SELECTED};
    padding: 4px;
}}
QCheckBox {{
    color: {VSCodeColors.FG_PRIMARY};
    spacing: 8px;
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {VSCodeColors.BORDER};
    border-radius: 3px;
    background-color: {VSCodeColors.BG_INPUT};
}}
QCheckBox::indicator:checked {{
    background-color: {VSCodeColors.BG_STATUS};
    border-color: {VSCodeColors.BG_STATUS};
}}
QCheckBox::indicator:hover {{
    border-color: {VSCodeColors.FG_ACCENT};
}}
QPushButton {{
    background-color: {VSCodeColors.BG_INPUT};
    color: {VSCodeColors.FG_PRIMARY};
    border: 1px solid {VSCodeColors.BORDER};
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 13px;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {VSCodeColors.BG_HOVER};
    border-color: {VSCodeColors.FG_SECONDARY};
}}
QPushButton:pressed {{
    background-color: {VSCodeColors.BG_SELECTED};
}}
QPushButton:disabled {{
    background-color: {VSCodeColors.BG_TERTIARY};
    color: {VSCodeColors.FG_DIMMED};
    border-color: {VSCodeColors.BG_TERTIARY};
}}
QPushButton#primaryBtn {{
    background-color: {VSCodeColors.BG_STATUS};
    color: {VSCodeColors.FG_WHITE};
    border: none;
}}
QPushButton#primaryBtn:hover {{
    background-color: #1a8ae8;
}}
QPushButton#dangerBtn {{
    background-color: {VSCodeColors.BG_DANGER};
    color: {VSCodeColors.FG_ERROR};
    border: 1px solid {VSCodeColors.FG_ERROR};
}}
QPushButton#dangerBtn:hover {{
    background-color: #6b2222;
}}
QTabWidget::pane {{
    border: none;
    background-color: {VSCodeColors.BG_PRIMARY};
}}
QTabBar {{
    background-color: {VSCodeColors.BG_SECONDARY};
    border-bottom: 1px solid {VSCodeColors.BORDER};
}}
QTabBar::tab {{
    background-color: {VSCodeColors.BG_SECONDARY};
    color: {VSCodeColors.FG_SECONDARY};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 20px;
    margin-right: 0px;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    background-color: {VSCodeColors.BG_PRIMARY};
    color: {VSCodeColors.FG_WHITE};
    border-bottom: 2px solid {VSCodeColors.FG_ACCENT};
}}
QTabBar::tab:hover:!selected {{
    background-color: {VSCodeColors.BG_HOVER};
    color: {VSCodeColors.FG_PRIMARY};
}}
QScrollBar:vertical {{
    background-color: {VSCodeColors.SCROLLBAR_BG};
    width: 10px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:vertical {{
    background-color: {VSCodeColors.SCROLLBAR_THUMB};
    min-height: 30px;
    border-radius: 5px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: #555;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background-color: {VSCodeColors.SCROLLBAR_BG};
    height: 10px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background-color: {VSCodeColors.SCROLLBAR_THUMB};
    min-width: 30px;
    border-radius: 5px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: #555;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QGroupBox {{
    border: 1px solid {VSCodeColors.BORDER};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    font-size: 13px;
    color: {VSCodeColors.FG_PRIMARY};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {VSCodeColors.FG_SECONDARY};
}}
QLabel {{
    color: {VSCodeColors.FG_PRIMARY};
    font-size: 13px;
}}
QLabel#sectionTitle {{
    color: {VSCodeColors.FG_WHITE};
    font-size: 16px;
    font-weight: bold;
    padding: 8px 0;
}}
QLabel#subtitleLabel {{
    color: {VSCodeColors.FG_SECONDARY};
    font-size: 12px;
}}
QStatusBar {{
    background-color: {VSCodeColors.BG_SECONDARY};
    color: {VSCodeColors.FG_SECONDARY};
    border-top: 1px solid {VSCodeColors.BORDER};
    font-size: 12px;
    padding: 2px 8px;
}}
QStatusBar::item {{
    border: none;
}}
QStatusBar QLabel {{
    background: transparent;
    color: {VSCodeColors.FG_SECONDARY};
    padding: 0 4px;
}}
QScrollBar {{
    background-color: {VSCodeColors.SCROLLBAR_BG};
}}
"""
