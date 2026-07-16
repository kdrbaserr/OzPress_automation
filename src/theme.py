"""Uygulamanın tek merkezden yönetilen görsel teması."""

COLORS = {
    "navy": "#132638",
    "navy_light": "#21425E",
    "teal": "#17A2A4",
    "background": "#F5F7FA",
    "surface": "#FFFFFF",
    "border": "#DDE4EA",
    "text": "#132638",
    "muted": "#5C6B76",
    "danger": "#C44536",
}

APPLICATION_STYLESHEET = """
    QWidget { color: #132638; font-family: Segoe UI, Arial, sans-serif; }
    #sidebar { background: #132638; }
    #brandName { color: #FFFFFF; font-size: 19px; font-weight: 700; }
    #brandTagline { color: #B9CAD6; font-size: 11px; }
    QPushButton#navButton { color: #D7E3EC; border: 0; text-align: left; padding: 12px; border-radius: 6px; font-size: 14px; }
    QPushButton#navButton:hover { background: #21425E; }
    QPushButton#navButton:checked { background: #17A2A4; color: white; font-weight: 600; }
    QPushButton#primaryButton { background: #17A2A4; color: white; border: 0; padding: 9px 15px; border-radius: 6px; font-weight: 600; }
    QPushButton#primaryButton:hover { background: #13898B; }
    QPushButton#secondaryButton { background: white; color: #132638; border: 1px solid #DDE4EA; padding: 9px 15px; border-radius: 6px; }
    #page { background: #F5F7FA; }
    #pageTitle { font-size: 28px; font-weight: 700; }
    #subtitle { color: #5C6B76; font-size: 14px; }
    #card { background: #FFFFFF; border: 1px solid #DDE4EA; border-radius: 10px; }
    #cardTitle { font-size: 16px; font-weight: 600; }
    QLineEdit, QComboBox { background: white; border: 1px solid #DDE4EA; border-radius: 6px; padding: 8px; min-height: 18px; }
    QLineEdit:focus, QComboBox:focus { border: 1px solid #17A2A4; }
    QTableWidget { background: #FFFFFF; color: #132638; alternate-background-color: #F2F6F8; border: 1px solid #C9D5DD; border-radius: 8px; gridline-color: #E1E8ED; selection-background-color: #D4F0EE; selection-color: #102A3A; }
    QTableWidget::item { color: #132638; background: transparent; padding: 8px; }
    QTableWidget::item:selected { color: #102A3A; background: #D4F0EE; }
    QHeaderView::section { background: #DDEBF0; color: #102A3A; border: 0; border-bottom: 1px solid #B8C8D2; padding: 10px; font-weight: 700; }
"""
