"""
Auto Post Engine - v2.2 Refined UI
Restored custom Flyout Dropdowns to match v1.0 exactly.
"""

import sys
import os
import threading
import time
import glob
import ctypes
import json
import logging
import zipfile
import datetime
from PySide6.QtCore import Qt, Signal, QObject, QPropertyAnimation, QEasingCurve, Property, QPoint, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QIcon, QTextCursor, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QTextEdit,
    QScrollArea, QListWidget, QListWidgetItem, QMessageBox, QSizePolicy, QStackedWidget,
    QGraphicsOpacityEffect
)

# Mica import
try:
    from win32mica import ApplyMica, MicaTheme, MicaStyle
    MICA_AVAILABLE = True
except ImportError:
    MICA_AVAILABLE = False

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.downloader import VideoDownloader
from modules.processor import VideoProcessor
from modules.uploader import TikTokUploader
from modules.database import HistoryManager
from modules.state_manager import StateManager

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING & MAINTENANCE
# ══════════════════════════════════════════════════════════════════════════════

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

def rotate_logs():
    now = time.time()
    for f in glob.glob(os.path.join(LOG_DIR, "*.txt")):
        if os.stat(f).st_mtime < now - (72 * 3600):
            try:
                zip_name = f"{f}.zip"
                with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(f, os.path.basename(f))
                os.remove(f)
            except: pass
rotate_logs()

log_file = os.path.join(LOG_DIR, f"session_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def wipe_temp():
    # Cleanup downloads/temp and logs > 12h
    now = time.time()
    temp_dl = os.path.join(os.path.dirname(__file__), '..', 'downloads', 'temp')
    if os.path.exists(temp_dl):
        for f in glob.glob(os.path.join(temp_dl, "*")):
            if os.path.getmtime(f) < now - (12 * 3600):
                try: os.remove(f)
                except: pass
    
    # Also clean finished downloads if > 12h
    main_dl = os.path.join(os.path.dirname(__file__), '..', 'downloads')
    for f in glob.glob(os.path.join(main_dl, "*.mp4")):
         if os.path.getmtime(f) < now - (12 * 3600):
              try: os.remove(f)
              except: pass

    # Clean OS %TEMP% for ffmpeg remnants
    sys_temp = os.environ.get('TEMP')
    if sys_temp:
        # Search for typical FFmpeg/MoviePy/Python temp patterns
        for pattern in ["ffmpeg-*", "tmp*.mp4", "tmp*.mp3"]:
            for f in glob.glob(os.path.join(sys_temp, pattern)):
                try: os.remove(f)
                except: pass
wipe_temp()

# ══════════════════════════════════════════════════════════════════════════════
# UI & STYLING (Restored)
# ══════════════════════════════════════════════════════════════════════════════

CARD = "rgba(50, 50, 50, 0.65)"
BORDER = "rgba(255, 255, 255, 0.08)"
INPUT = "rgba(0, 0, 0, 0.2)"
TEXT = "#FFFFFF"
DIM = "#888888"
ACCENT = "#0078D4"
RED = "#C42B1C"
GREEN = "#107C10"

CSS = f"""
* {{ font-family: 'Segoe UI', sans-serif; }}
QMainWindow {{ background: transparent; }}
QWidget#main {{ background: rgba(25, 25, 25, 0.4); }}
QScrollArea {{ background: transparent; border: none; }}

QFrame#card {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
}}

QLabel#title {{ color: {TEXT}; font-size: 13px; font-weight: 600; }}
QLabel#lbl {{ color: {TEXT}; font-size: 13px; }}
QLabel#sub {{ color: {DIM}; font-size: 11px; }}

QLineEdit, QComboBox, QTextEdit, QListWidget, QSpinBox {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-top: 1px solid rgba(255, 255, 255, 0.15); /* Top lighting */
    border-radius: 4px;
    padding: 8px 12px;
    color: {TEXT};
    font-size: 13px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border-color: {ACCENT}; }}

QScrollBar:vertical {{ background: transparent; width: 6px; }}
QScrollBar::handle:vertical {{ background: #555; border-radius: 3px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QPushButton#action {{
    background: {ACCENT}; 
    border: none; 
    border-radius: 4px; 
    color: white; 
    font-weight: 600;
}}
QPushButton#action:hover {{
    background: #1984D8;
}}
"""

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

class SidebarBtn(QPushButton):
    def __init__(self, icon, text, active=False):
        super().__init__()
        self.setCheckable(True)
        self.setChecked(active)
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.icon_char = icon
        self.label_text = text
        self.setStyleSheet("border: none; background: transparent;")
        
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Background hover/active
        if self.isChecked():
            p.setBrush(QColor(255, 255, 255, 20))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(0, 0, self.width(), self.height(), 4, 4)
        elif self.underMouse():
            p.setBrush(QColor(255, 255, 255, 10))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(0, 0, self.width(), self.height(), 4, 4)
            
        # Icon
        p.setFont(QFont('Segoe MDL2 Assets', 12))
        p.setPen(QColor(TEXT if self.isChecked() or self.underMouse() else DIM))
        p.drawText(QRect(12, 0, 30, 40), Qt.AlignVCenter | Qt.AlignLeft, self.icon_char)
        
        # Text
        p.setFont(QFont('Segoe UI', 10, QFont.DemiBold if self.isChecked() else QFont.Normal))
        p.drawText(QRect(48, 0, self.width()-48, 40), Qt.AlignVCenter | Qt.AlignLeft, self.label_text)

class Toggle(QWidget):
    toggled = Signal(bool)
    def __init__(self, on=False):
        super().__init__()
        self._on = on
        self._x = 26.0 if on else 4.0
        self.setFixedSize(48, 24)
        self.setCursor(Qt.PointingHandCursor)
        self._anim = QPropertyAnimation(self, b"xpos", self)
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.OutQuint)
    
    def get_xpos(self): return self._x
    def set_xpos(self, v): self._x = v; self.update()
    xpos = Property(float, get_xpos, set_xpos)
    def isChecked(self): return self._on
    def setChecked(self, c):
        if self._on != c:
            self._on = c
            self._x = 26.0 if c else 4.0
            self.update()
            self.toggled.emit(c)
    def mousePressEvent(self, e):
        self._on = not self._on
        self._anim.stop()
        self._anim.setStartValue(self._x)
        self._anim.setEndValue(26.0 if self._on else 4.0)
        self._anim.start()
        self.toggled.emit(self._on)
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Track
        if self._on:
            p.setBrush(QColor(ACCENT))
            p.setPen(Qt.NoPen)
        else:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 100), 1))
        p.drawRoundedRect(0, 2, 44, 20, 10, 10)
        
        # Handle
        p.setBrush(QColor("#000000" if self._on else "#FFFFFF"))
        p.setPen(Qt.NoPen)
        # Use simple interpolation or the animated _x
        p.drawEllipse(int(self._x), 5, 14, 14)

class PasswordInput(QLineEdit):
    def __init__(self, placeholder="Password"):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setEchoMode(QLineEdit.Password)
        self.setFixedHeight(36)
        
        self.eye_btn = QPushButton("\uE7B3", self) # Eye icon
        self.eye_btn.setFixedSize(30, 30)
        self.eye_btn.setCursor(Qt.PointingHandCursor)
        self.eye_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; border-radius: 4px;
                color: {DIM}; font-family: 'Segoe MDL2 Assets'; font-size: 14px;
            }}
            QPushButton:hover {{ color: {TEXT}; background: rgba(255,255,255,0.1); }}
        """)
        self.eye_btn.clicked.connect(self._toggle_eye)
        
        self.setStyleSheet(f"padding-right: 36px;") # Make room for button
        
    def _toggle_eye(self):
        if self.echoMode() == QLineEdit.Password:
            self.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setText("\uE101") # Eye off icon
        else:
            self.setEchoMode(QLineEdit.Password)
            self.eye_btn.setText("\uE7B3")
        self.eye_btn.update()
            
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.eye_btn.move(self.width() - 34, (self.height() - 32) // 2)

class SidebarIndicator(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedWidth(3)
        self.setFixedHeight(18)
        self.setStyleSheet(f"background: {ACCENT}; border-radius: 1.5px;")
        
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(500)
        self._anim.setEasingCurve(QEasingCurve.OutQuint)
        
    def move_to(self, y):
        self._anim.stop()
        start_rect = self.geometry()
        end_rect = QRect(0, y, 3, 18)
        
        self._anim.setStartValue(start_rect)
        # Dynamic stretch based on distance
        dist = abs(start_rect.y() - end_rect.y())
        if dist > 10:
            mid_y = min(start_rect.y(), end_rect.y())
            mid_h = dist + 18
            self._anim.setKeyValueAt(0.4, QRect(0, mid_y, 3, mid_h))
            
        self._anim.setEndValue(end_rect)
        self._anim.start()

class SidebarBtn(QPushButton):
    def __init__(self, icon, text, active=False):
        super().__init__()
        self.setCheckable(True)
        self.setChecked(active)
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.icon_char = icon
        self.label_text = text
        self.setStyleSheet("border: none; background: transparent;")
        
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Background hover/active
        if self.isChecked():
            p.setBrush(QColor(255, 255, 255, 20))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(0, 0, self.width(), self.height(), 4, 4)
        elif self.underMouse():
            p.setBrush(QColor(255, 255, 255, 10))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(0, 0, self.width(), self.height(), 4, 4)
            
        # Icon
        p.setFont(QFont('Segoe MDL2 Assets', 12))
        p.setPen(QColor(TEXT if self.isChecked() or self.underMouse() else DIM))
        p.drawText(QRect(12, 0, 30, 40), Qt.AlignVCenter | Qt.AlignLeft, self.icon_char)
        
        # Text
        p.setFont(QFont('Segoe UI', 10, QFont.DemiBold if self.isChecked() else QFont.Normal))
        p.drawText(QRect(48, 0, self.width()-48, 40), Qt.AlignVCenter | Qt.AlignLeft, self.label_text)

class Flyout(QFrame):
    def __init__(self, parent, options, callback):
        super().__init__(None) # No parent to be top-level
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.callback = callback
        
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(6, 6, 6, 6)
        self.lay.setSpacing(2)
        
        for opt in options:
            btn = QPushButton(opt)
            btn.setFixedHeight(34)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none; border-radius: 4px;
                    color: {TEXT}; padding: 0 12px; text-align: left; font-size: 13px;
                }}
                QPushButton:hover {{ background: rgba(255,255,255,0.1); }}
            """)
            btn.clicked.connect(lambda checked, o=opt: self._select(o))
            self.lay.addWidget(btn)
        
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#202020"))
        p.setPen(QPen(QColor(255, 255, 255, 35), 1))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
        
    def _select(self, val):
        self.callback(val)
        self.close()

    def show_animated(self, pos, width):
        self.setFixedWidth(width)
        self.move(pos)
        self.show()
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(250)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutQuint)
        self._anim.start()

class FluentSelect(QPushButton):
    changed = Signal(str)
    
    def __init__(self, options):
        super().__init__()
        self._options = options
        self._val = options[0]
        self.setText(self._val)
        self.setFixedHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        self.arrow = QLabel("\uE70D", self) # Chevron
        self.arrow.setStyleSheet(f"color: {DIM}; font-family: 'Segoe MDL2 Assets'; font-size: 10px;")
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.08); border-top: 1px solid rgba(255, 255, 255, 0.15); border-radius: 4px;
                color: {TEXT}; padding: 0 36px 0 12px; text-align: left; font-size: 13px;
                transition: background 0.3s;
            }}
            QPushButton:hover {{ background: rgba(255,255,255,0.08); }}
        """)
        self.clicked.connect(self._show_flyout)

    def currentText(self): return self._val
    def setCurrentText(self, v): 
        if v in self._options:
            self._val = v; self.setText(v)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.arrow.setGeometry(self.width() - 32, 0, 24, self.height())
        self.arrow.setAlignment(Qt.AlignCenter)

    def _show_flyout(self):
        p = self.mapToGlobal(QPoint(0, self.height() + 4))
        self.flyout = Flyout(self, self._options, self._on_select)
        self.flyout.show_animated(p, self.width())
    
    def _on_select(self, val):
        self._val = val; self.setText(val); self.changed.emit(val)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    log_signal = Signal(dict)
    status_signal = Signal(dict)
    
    def __init__(self):
        super().__init__()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'ape.v2.enterprise')
        self.setWindowTitle("Auto Post Engine v2.3")
        
        # Icon Setup (Taskbar + Titlebar)
        logo_path = os.path.join(os.path.dirname(__file__), "win_logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            
        self.setMinimumSize(950, 650)
        self.resize(1100, 750)
        self.setStyleSheet(CSS)

        if MICA_AVAILABLE:
            self.setAttribute(Qt.WA_TranslucentBackground)
            ApplyMica(int(self.winId()), MicaTheme.DARK, MicaStyle.DEFAULT)

        # Logic
        self.downloader = VideoDownloader()
        self.processor = VideoProcessor()
        self.uploader = TikTokUploader()
        self.db = HistoryManager()
        self.state = StateManager()
        self.running = False
        self.paused = False
        
        self.log_signal.connect(self._log_handler, Qt.QueuedConnection)
        self.status_signal.connect(self._status_handler, Qt.QueuedConnection)

        self._build_ui()
        self._load_config()
        self._check_recovery()
        
        # Initial nav (No animation for instant setup)
        self._nav(0, animate=False)

    def _build_ui(self):
        main = QWidget()
        main.setObjectName("main")
        self.setCentralWidget(main)
        
        # Main Horizontal Layout (Sidebar + Content)
        root = QHBoxLayout(main)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        # SIDEBAR
        sidebar = QFrame()
        sidebar.setFixedWidth(240) # Wider sidebar like Win11
        sidebar.setStyleSheet(f"background: transparent;")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(10, 10, 10, 10)
        sl.setSpacing(4)
        
        # User Profile Header (Windows 11 Style)
        user_card = QWidget()
        user_card.setFixedHeight(60)
        ul = QHBoxLayout(user_card)
        ul.setContentsMargins(8, 0, 8, 20)
        
        # Official User Profile Pic from System
        upic = QLabel()
        upic.setFixedSize(40, 40)
        pic_path = os.path.join(os.path.dirname(__file__), "user_pic.png")
        if os.path.exists(pic_path):
            pix = QIcon(pic_path).pixmap(40, 40)
            upic.setPixmap(pix)
            upic.setStyleSheet("border-radius: 20px;") # Circle
        else:
            upic.setText("\uE77B")
            upic.setAlignment(Qt.AlignCenter)
            upic.setStyleSheet(f"background: rgba(255,255,255,0.1); border-radius: 20px; color: {TEXT}; font-family: 'Segoe MDL2 Assets'; font-size: 20px;")
        
        ul.addWidget(upic)
        
        unames = QVBoxLayout()
        unames.setSpacing(0)
        uname = QLabel("Auto Post Engine")
        uname.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 600;")
        usub = QLabel("Local Account")
        usub.setStyleSheet(f"color: {DIM}; font-size: 11px;")
        unames.addWidget(uname)
        unames.addWidget(usub)
        ul.addLayout(unames)
        ul.addStretch()
        sl.addWidget(user_card)

        # Search Bar (Decorative)
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search settings")
        search_bar.setFixedHeight(36)
        search_bar.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-top: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                padding: 8px 12px 8px 36px; /* Left padding for icon */
                color: {TEXT};
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        
        search_icon = QLabel("\uE721", search_bar) # Search icon
        search_icon.setStyleSheet(f"color: {DIM}; font-family: 'Segoe MDL2 Assets'; font-size: 14px; background: transparent;")
        search_icon.setGeometry(12, 0, 24, 36)
        search_icon.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        sl.addWidget(search_bar)
        sl.addSpacing(10) # Add some space after search bar

        # Nav Buttons (Matching picture icons)
        # Home (E80F), History/System (E770 or E81C)
        self.btn_dash = SidebarBtn("\uE80F", "Home", True)
        self.btn_dash.clicked.connect(lambda: self._nav(0))
        sl.addWidget(self.btn_dash)
        
        self.btn_hist = SidebarBtn("\uE9D5", "System") # Gear/System icon for vibe
        self.btn_hist.clicked.connect(lambda: self._nav(1))
        sl.addWidget(self.btn_hist)
        
        self.nav_indicator = SidebarIndicator(sidebar)
        # Initial position - will be finalized in _nav
        self.nav_indicator.hide() 
        
        sl.addStretch()
        
        # Bottom Status
        self.status = QLabel("\uE73E Ready") # Checkmark
        self.status.setStyleSheet(f"color: {DIM}; font-family: 'Segoe UI', 'Segoe MDL2 Assets'; font-size: 11px; margin-left: 12px;")
        sl.addWidget(self.status)
        
        root.addWidget(sidebar)

        # SEPARATOR
        line = QFrame()
        line.setFixedWidth(1)
        line.setStyleSheet(f"background: {BORDER};")
        root.addWidget(line)

        # CONTENT STACK
        self.stack = QStackedWidget()
        
        # PAGE 1: DASHBOARD
        self.page_dash = QWidget()
        self._build_dashboard(self.page_dash)
        self.stack.addWidget(self.page_dash)
        
        # Opacity Effect for stack transitions
        self.stack_eff = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(self.stack_eff)
        
        # PAGE 2: HISTORY
        self.page_hist = QWidget()
        self._build_history(self.page_hist)
        self.stack.addWidget(self.page_hist)
        
        root.addWidget(self.stack)

    def _nav(self, idx, animate=True):
        if self.stack.currentIndex() == idx and self.stack_eff.opacity() > 0.9 and not animate: 
            return
        
        def finish_nav():
            self.stack.setCurrentIndex(idx)
            self.btn_dash.setChecked(idx == 0)
            self.btn_hist.setChecked(idx == 1)
            
            # Ensure btn y is updated by processing events if needed
            self.btn_dash.updateGeometry()
            self.btn_hist.updateGeometry()
            
            # Move indicator - accurately calculate center of btn
            target_btn = self.btn_dash if idx == 0 else self.btn_hist
            self.nav_indicator.show()
            self.nav_indicator.move_to(target_btn.y() + (target_btn.height() - 18) // 2)
            
            # Update card background using selector to prevent inheritance
            color = "rgba(255, 255, 255, 0.04)"
            for card in self.findChildren(QFrame, "card"):
                card.setStyleSheet(f"QFrame#card {{ background: {color}; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; }}")
            
            if animate:
                # Fade In
                self._fade_in = QPropertyAnimation(self.stack_eff, b"opacity")
                self._fade_in.setDuration(300)
                self._fade_in.setStartValue(0.0)
                self._fade_in.setEndValue(1.0)
                self._fade_in.setEasingCurve(QEasingCurve.OutQuint)
                self._fade_in.start()
            else:
                self.stack_eff.setOpacity(1.0)
            
            self.btn_dash.update()
            self.btn_hist.update()

        if animate:
            # Fade Out effect
            self._fade_anim = QPropertyAnimation(self.stack_eff, b"opacity")
            self._fade_anim.setDuration(150)
            self._fade_anim.setStartValue(self.stack_eff.opacity())
            self._fade_anim.setEndValue(0.0)
            self._fade_anim.finished.connect(finish_nav)
            self._fade_anim.start()
        else:
            finish_nav()

    def _build_dashboard(self, parent):
        # Using ScrollArea for Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(25, 20, 20, 20)
        lay.setSpacing(25)
        
        # Page Title Row
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 15)
        
        self.dash_title = QLabel("Home")
        self.dash_title.setStyleSheet(f"color: {TEXT}; font-size: 28px; font-weight: bold;")
        title_row.addWidget(self.dash_title)
        title_row.addStretch()
        lay.addLayout(title_row)
        
        # Hero Card (Windows 11 Settings Style)
        hero = QFrame()
        hero.setFixedHeight(120)
        hero.setCursor(Qt.PointingHandCursor)
        hero.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0,0,0,0.4), stop:1 transparent);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
            }}
        """)
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(20, 0, 20, 0)
        
        pc_info = QVBoxLayout()
        pc_info.setSpacing(0)
        pc_info.setAlignment(Qt.AlignVCenter)
        
        # Name and Link
        h_name = QHBoxLayout()
        h_name.setSpacing(10)
        pc_name = QLabel(os.environ.get('COMPUTERNAME', 'Windows-PC'))
        pc_name.setStyleSheet(f"color: {TEXT}; font-size: 16px; font-weight: bold;")
        h_name.addWidget(pc_name)
        
        rename = QLabel("Rename")
        rename.setStyleSheet(f"color: {ACCENT}; font-size: 11px; text-decoration: underline;")
        rename.setCursor(Qt.PointingHandCursor)
        h_name.addWidget(rename)
        h_name.addStretch()
        pc_info.addLayout(h_name)
        
        pc_model = QLabel("APE Engine v2.3 Enterprise")
        pc_model.setStyleSheet(f"color: {DIM}; font-size: 12px;")
        pc_info.addWidget(pc_model)
        
        # Connection status
        pc_status = QLabel("Connected, secured")
        pc_status.setStyleSheet(f"color: {DIM}; font-size: 11px;")
        pc_info.addWidget(pc_status)
        
        # Bloom Background (Left side - like picture)
        img_lbl = QLabel()
        img_lbl.setFixedSize(90, 60)
        hero_path = os.path.join(os.path.dirname(__file__), "hero.jpg")
        if os.path.exists(hero_path):
            pix = QIcon(hero_path).pixmap(90, 60)
            img_lbl.setPixmap(pix)
            img_lbl.setStyleSheet("border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);")
        
        hl.addWidget(img_lbl)
        hl.addLayout(pc_info)
        hl.addStretch()
        
        lay.addWidget(hero)
        
        # Two Columns
        cols = QHBoxLayout()
        cols.setSpacing(20)
        
        # LEFT COL
        left = QVBoxLayout()
        left.setSpacing(20)
        
        # 1. Queue Card
        c1, l1 = self._card("Batch Queue")
        
        # Add Input Row
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL...")
        add_btn = QPushButton("Add")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(f"background: {ACCENT}; color: white; border: none; border-radius: 4px; padding: 0 16px; font-weight: 600;")
        add_btn.setFixedHeight(34)
        add_btn.clicked.connect(self._add_to_queue)
        
        h_add = QHBoxLayout()
        h_add.addWidget(self.url_input)
        h_add.addWidget(add_btn)
        l1.addLayout(h_add)
        
        self.queue_list = QListWidget()
        self.queue_list.setDragDropMode(QListWidget.InternalMove)
        self.queue_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.queue_list.setFixedHeight(150)
        l1.addWidget(self.queue_list)
        
        l1.addWidget(self._btn("Clear Queue", self.queue_list.clear, red=True))
        left.addWidget(c1)
        
        # 2. Controls Card
        c2, l2 = self._card("Settings")
        self.dur = FluentSelect(["30", "45", "60", "90", "120", "180", "240", "300"])
        self.dur.setCurrentText("60")
        l2.addWidget(self._row("Part Duration", self.dur, "Seconds"))
        
        self.throttle = FluentSelect(["0", "5", "10", "15", "30", "60", "120"])
        l2.addWidget(self._row("Job Gap (Mins)", self.throttle, "Time between videos"))

        self.crop = Toggle(True)
        l2.addWidget(self._row("Fit 9:16", self.crop))
        
        self.speed = Toggle(False)
        l2.addWidget(self._row("1.25x Speed", self.speed, "Evades Copyright"))
        
        self.upload = Toggle(True)
        l2.addWidget(self._row("Upload to TikTok", self.upload))
        
        self.autodel = Toggle(False)
        l2.addWidget(self._row("Auto-Delete", self.autodel, "Cleanup source"))
        left.addWidget(c2)
        
        # ACTION BUTTONS
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(8)
        
        self.start_btn = QPushButton("Start Batch")
        self.start_btn.setObjectName("action")
        self.start_btn.setFixedHeight(45)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._start_batch)
        btn_lay.addWidget(self.start_btn, 2)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setFixedHeight(45)
        self.pause_btn.setVisible(False)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.setStyleSheet(f"background: {ACCENT}; border: none; border-radius: 6px; color: white; font-weight: 600;")
        self.pause_btn.clicked.connect(self._toggle_pause)
        btn_lay.addWidget(self.pause_btn, 1)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setFixedHeight(45)
        self.stop_btn.setVisible(False)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet(f"background: {RED}; border: none; border-radius: 6px; color: white; font-weight: 600;")
        self.stop_btn.clicked.connect(self._stop)
        btn_lay.addWidget(self.stop_btn, 1)
        
        left.addLayout(btn_lay)
        
        cols.addLayout(left, 4)
        
        # RIGHT COL
        right = QVBoxLayout()
        right.setSpacing(20)
        
        # 3. Account
        c3, l3 = self._card("TikTok Account")
        self.user = QLineEdit()
        self.user.setPlaceholderText("Email or Username")
        l3.addWidget(self._row("Login", self.user))
        self.pwd = PasswordInput()
        l3.addWidget(self._row("Password", self.pwd))
        right.addWidget(c3)
        
        # 4. Meta
        c4, l4 = self._card("Metadata")
        self.title_in = QLineEdit()
        self.title_in.setPlaceholderText("Optional Title Override")
        l4.addWidget(self._row("Title", self.title_in))
        self.tags = QLineEdit()
        self.tags.setText("#fyp #viral")
        l4.addWidget(self._row("Hashtags", self.tags))
        right.addWidget(c4)
        
        # 5. Logs
        c5, l5 = self._card("Activity Log")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        l5.addWidget(self.log)
        right.addWidget(c5)
        
        cols.addLayout(right, 5)
        
        lay.addLayout(cols)
        lay.addStretch()
        
        scroll.setWidget(content)
        
        # Fix layout for scroll
        pl = QVBoxLayout(parent)
        pl.setContentsMargins(0,0,0,0)
        pl.addWidget(scroll)

    def _build_history(self, parent):
        lay = QVBoxLayout(parent)
        lay.setContentsMargins(25, 20, 20, 20)
        lay.setSpacing(15)
        
        # Page Title
        self.hist_title = QLabel("History")
        self.hist_title.setStyleSheet(f"color: {TEXT}; font-size: 28px; font-weight: bold; margin-bottom: 5px;")
        lay.addWidget(self.hist_title)
        
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 10)
        h.addWidget(QLabel("Global Posting History"))
        h.addStretch()
        h.addWidget(self._btn("Export to TXT", self._export_history))
        h.addWidget(self._btn("Refresh", self._refresh_history))
        lay.addLayout(h)
        
        self.hist_list = QTextEdit()
        self.hist_list.setReadOnly(True)
        self.hist_list.setStyleSheet(f"font-family: Consolas; font-size: 11px; background: {INPUT}; border-radius: 8px;")
        lay.addWidget(self.hist_list)

    # HELPER UI FUNCTIONS
    def _card(self, t):
        c = QFrame()
        c.setObjectName("card")
        l = QVBoxLayout(c)
        l.setContentsMargins(16, 14, 16, 14)
        l.setSpacing(10)
        lbl = QLabel(t)
        lbl.setObjectName("title")
        l.addWidget(lbl)
        return c, l

    def _row(self, label, widget, sub=None):
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 4, 0, 4)
        h.setSpacing(16)
        
        lbl_col = QWidget()
        lbl_col.setFixedWidth(130)
        v = QVBoxLayout(lbl_col)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)
        
        lb = QLabel(label)
        lb.setObjectName("lbl")
        v.addWidget(lb)
        if sub:
            s = QLabel(sub)
            s.setObjectName("sub")
            v.addWidget(s)
        
        h.addWidget(lbl_col)
        h.addWidget(widget, 1)
        return w

    def _btn(self, t, cb, red=False):
        b = QPushButton(t)
        b.setCursor(Qt.PointingHandCursor)
        bg = RED if red else "rgba(255,255,255,0.1)"
        b.setStyleSheet(f"background: {bg}; border: none; border-radius: 4px; color: white; padding: 6px 12px;")
        b.clicked.connect(cb)
        return b

    # LOGIC HANDLERS
    def _add_to_queue(self):
        u = self.url_input.text().strip()
        if u:
            if self.db.check_exists(u):
                if QMessageBox.question(self, "Approx Duplicate", "Link in DB. Add anyway?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.No:
                    return
            self.queue_list.addItem(u)
            self.url_input.clear()

    def _refresh_history(self):
        rows = self.db.get_all_history()
        txt = f"{'Date':<20} | {'Status':<10} | {'Title'}\n"
        txt += "-"*90 + "\n"
        for r in rows:
            txt += f"{r[2]:<20} | {r[4]:<10} | {r[1]}\n"
        self.hist_list.setText(txt)

    def _export_history(self):
        if self.db.export_to_txt():
            QMessageBox.information(self, "Done", "Saved to history_export.txt")

    def _log_handler(self, d):
        logging.info(d['m'])
        c, update, msg = d['c'], d['u'], d['m']
        html = f'<span style="color:{c}">› {msg}</span>'
        
        sb = self.log.verticalScrollBar()
        bot = (sb.value() >= sb.maximum() - 10)
        
        if update:
            cursor = self.log.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertHtml(html)
        else:
            self.log.append(html)
        
        if bot: sb.setValue(sb.maximum())

    def _status_handler(self, d):
        self.status.setText(d['m'])

    def _check_recovery(self):
        s = self.state.load_state()
        if s and s['active'] and s['queue']:
            if QMessageBox.question(self, "Crash Detected", "Resume previous session?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                for u in s['queue']: self.queue_list.addItem(u)
                self.log_signal.emit({'m': "Session Restored.", 'c': ACCENT, 'u': False})

    def _start_batch(self):
        q = [self.queue_list.item(i).text() for i in range(self.queue_list.count())]
        if not q: return
        self.running = True
        self.paused = False
        self.start_btn.setVisible(False)
        self.pause_btn.setVisible(True)
        self.pause_btn.setText("Pause")
        self.stop_btn.setVisible(True)
        
        cfg = {
            'dur': int(self.dur.currentText()),
            'crop': self.crop.isChecked(),
            'speed': self.speed.isChecked(),
            'user': self.user.text(),
            'pwd': self.pwd.text(),
            'title': self.title_in.text(),
            'tags': self.tags.text(),
            'upload': self.upload.isChecked(),
            'del': self.autodel.isChecked(),
            'throttle': int(self.throttle.currentText()),
            'queue': q
        }
        self._save_config()
        if cfg['user']: self.uploader.set_credentials(cfg['user'], cfg['pwd'])
        threading.Thread(target=self._batch_work, args=(cfg,), daemon=True).start()

    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.setText("Resume")
            self.log_signal.emit({'m': "Pause requested... Waiting for current step to finish.", 'c': ACCENT, 'u': False})
        else:
            self.pause_btn.setText("Pause")
            self.log_signal.emit({'m': "Automation resumed.", 'c': GREEN, 'u': False})

    def _stop(self):
        self.running = False
        self.paused = False
        self.processor.cancel()
        self.uploader.cancel()
        self.log_signal.emit({'m': "Stop command received.", 'c': RED, 'u': False})

    def _batch_work(self, cfg):
        q = cfg['queue']
        for i, url in enumerate(q):
            if not self.running: break
            
            # Check Pause between jobs
            while self.paused and self.running:
                self.status_signal.emit({'m': "Paused"})
                time.sleep(1)
            
            if not self.running: break
            
            # Skip if duplicate in DB
            if self.db.check_exists(url):
                self.log_signal.emit({'m': f"Skipping Duplicate: {url}", 'c': RED, 'u': False})
                continue

            self.state.save_state(q, i)
            self.log_signal.emit({'m': f"--- Processing {i+1}/{len(q)} ---", 'c': TEXT, 'u': False})
            
            try:
                # 1. Download
                self.status_signal.emit({'m': f"Job {i+1}: Downloading..."})
                def prog(pct, msg):
                    if not self.running: return
                    self.log_signal.emit({'m': msg, 'c': DIM, 'u': ('%' in msg or 'Part' in msg)})
                
                fpath = self.downloader.download_video(url, progress_callback=prog)
                if not fpath: continue
                if not os.path.exists(fpath):
                    base = os.path.splitext(fpath)[0] + ".mp4"
                    if os.path.exists(base): fpath = base

                # Check Pause
                while self.paused and self.running:
                    self.status_signal.emit({'m': "Paused"})
                    time.sleep(1)
                if not self.running: break

                # 2. Process
                self.status_signal.emit({'m': f"Job {i+1}: Processing..."})
                parts = self.processor.segment_video(fpath, cfg['dur'], cfg['crop'], cfg['speed'], progress_callback=prog)
                if not parts: continue

                # Check Pause
                while self.paused and self.running:
                    self.status_signal.emit({'m': "Paused"})
                    time.sleep(1)
                if not self.running: break

                # 3. Upload
                if cfg['upload']:
                    vt = cfg['title'] or self.downloader.last_title
                    for j, part in enumerate(parts):
                        if not self.running: break
                        
                        # Check Pause between parts
                        while self.paused and self.running:
                             self.status_signal.emit({'m': "Paused"})
                             time.sleep(1)
                        if not self.running: break

                        pi = f"Part {j+1}/{len(parts)}"
                        cap = f"{vt} ({pi}) {cfg['tags']}"
                        
                        def up_cb(pct, m): prog(pct, f"[{pi}] {m}")
                        
                        self.log_signal.emit({'m': f"Uploading {pi}", 'c': ACCENT, 'u': False})
                        if self.uploader.upload_video(part, cap, cfg['tags'], progress_callback=up_cb):
                            self.log_signal.emit({'m': f"Uploaded {pi}", 'c': GREEN, 'u': False})
                            if cfg['del']: os.remove(part)
                
                self.db.add_entry(url, self.downloader.last_title, cfg['user'])
                if cfg['del'] and os.path.exists(fpath): os.remove(fpath)
                
                # THROTTLE / GAP
                if cfg['throttle'] > 0 and i < len(q) - 1:
                    mins = cfg['throttle']
                    self.log_signal.emit({'m': f"Throttling: Waiting {mins} mins before next job...", 'c': DIM, 'u': False})
                    for m in range(mins * 60):
                        if not self.running: break
                        # If user pauses during throttle, it still counts down? 
                        # Or should we stop the timer? Let's check pause.
                        while self.paused and self.running:
                             self.status_signal.emit({'m': "Paused"})
                             time.sleep(1)
                        if (m % 60) == 0:
                             rem = mins - (m // 60)
                             self.status_signal.emit({'m': f"Next job in {rem}m"})
                        time.sleep(1)

            except Exception as e:
                self.log_signal.emit({'m': f"Error: {e}", 'c': RED, 'u': False})
        
        self.state.clear_state()
        self.running = False
        self.paused = False
        self.status_signal.emit({'m': "Done"})
        
        # Restore UI via QMetaObject
        from PySide6.QtCore import QMetaObject, Q_ARG
        QMetaObject.invokeMethod(self.start_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, True))
        QMetaObject.invokeMethod(self.pause_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
        QMetaObject.invokeMethod(self.stop_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))

    def _save_config(self):
        data = {
            'title': self.title_in.text(), 'tags': self.tags.text(),
            'dur': self.dur.currentText(), 'crop': self.crop.isChecked(),
            'speed': self.speed.isChecked(), 'user': self.user.text(),
            'pwd': self.pwd.text(), 'upload': self.upload.isChecked(),
            'autodel': self.autodel.isChecked(), 'browser': self.uploader.browser_type,
            'throttle': self.throttle.currentText()
        }
        try:
            with open("config.json", 'w') as f: json.dump(data, f, indent=4)
        except: pass

    def _load_config(self):
        if not os.path.exists("config.json"): return
        try:
            with open("config.json",'r') as f: data = json.load(f)
            if 'title' in data: self.title_in.setText(data['title'])
            if 'tags' in data: self.tags.setText(data['tags'])
            if 'user' in data: self.user.setText(data['user'])
            if 'pwd' in data: self.pwd.setText(data['pwd'])
            if 'dur' in data: self.dur.setCurrentText(str(data['dur']))
            if 'crop' in data: self.crop.setChecked(data['crop'])
            if 'speed' in data: self.speed.setChecked(data['speed'])
            if 'upload' in data: self.upload.setChecked(data['upload'])
            if 'autodel' in data: self.autodel.setChecked(data['autodel'])
            if 'throttle' in data: self.throttle.setCurrentText(str(data['throttle']))
            if 'browser' in data: self.uploader.set_browser_preference(data['browser'])
        except: pass

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
