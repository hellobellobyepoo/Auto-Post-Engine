"""
Auto Post Engine - v3.0 Windows 11 Native UI
Complete WinUI 3 implementation with Mica backdrop, Fluent Design System,
and authentic Windows 11 animations and styling.
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
from PySide6.QtCore import (
    Qt, Signal, QObject, QPropertyAnimation, QEasingCurve, Property, 
    QPoint, QRect, QTimer, QSize, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QIcon, QTextCursor, QFont, QFontDatabase,
    QPainterPath, QBrush, QLinearGradient, QPalette
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QTextEdit,
    QScrollArea, QListWidget, QListWidgetItem, QMessageBox, QSizePolicy, 
    QStackedWidget, QGraphicsOpacityEffect, QSpinBox, QAbstractItemView,
    QStyle, QStyleOption
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
    now = time.time()
    temp_dl = os.path.join(os.path.dirname(__file__), '..', 'downloads', 'temp')
    if os.path.exists(temp_dl):
        for f in glob.glob(os.path.join(temp_dl, "*")):
            if os.path.getmtime(f) < now - (12 * 3600):
                try: os.remove(f)
                except: pass
    
    main_dl = os.path.join(os.path.dirname(__file__), '..', 'downloads')
    for f in glob.glob(os.path.join(main_dl, "*.mp4")):
         if os.path.getmtime(f) < now - (12 * 3600):
              try: os.remove(f)
              except: pass

    sys_temp = os.environ.get('TEMP')
    if sys_temp:
        for pattern in ["ffmpeg-*", "tmp*.mp4", "tmp*.mp3"]:
            for f in glob.glob(os.path.join(sys_temp, pattern)):
                try: os.remove(f)
                except: pass
wipe_temp()

# ══════════════════════════════════════════════════════════════════════════════
# WINDOWS 11 WINUI 3 COLOR SYSTEM (DARK THEME)
# ══════════════════════════════════════════════════════════════════════════════

class WinUI:
    """
    Windows 11 WinUI 3 Design Tokens
    Authentic Microsoft design system colors with Mica support
    """
    # Accent Colors (Windows 11 Default Blue)
    ACCENT_DEFAULT = "#0078D4"
    ACCENT_LIGHT_1 = "#429CE3"
    ACCENT_LIGHT_2 = "#6BB9F0"
    ACCENT_LIGHT_3 = "#A6D5FA"
    ACCENT_DARK_1 = "#005A9E"
    ACCENT_DARK_2 = "#004578"
    ACCENT_DARK_3 = "#003258"
    
    # Text Colors (Dark Theme) - Exact WinUI 3 values
    TEXT_PRIMARY = "rgba(255, 255, 255, 1.0)"
    TEXT_SECONDARY = "rgba(255, 255, 255, 0.786)"
    TEXT_TERTIARY = "rgba(255, 255, 255, 0.545)"
    TEXT_DISABLED = "rgba(255, 255, 255, 0.363)"
    TEXT_ON_ACCENT = "#000000"
    
    # Fill Colors (Dark Theme) - For controls on Mica
    FILL_CONTROL_DEFAULT = "rgba(255, 255, 255, 0.0605)"
    FILL_CONTROL_SECONDARY = "rgba(255, 255, 255, 0.0837)"
    FILL_CONTROL_TERTIARY = "rgba(255, 255, 255, 0.0326)"
    FILL_CONTROL_INPUT_ACTIVE = "rgba(30, 30, 30, 0.7)"
    FILL_CONTROL_DISABLED = "rgba(255, 255, 255, 0.0419)"
    FILL_SUBTLE_TRANSPARENT = "transparent"
    FILL_SUBTLE_SECONDARY = "rgba(255, 255, 255, 0.0605)"
    FILL_SUBTLE_TERTIARY = "rgba(255, 255, 255, 0.0419)"
    
    # Background Colors (Dark Theme with Mica)
    BG_MICA_BASE = "rgba(32, 32, 32, 0.0)"  # Transparent for Mica
    BG_LAYER_DEFAULT = "rgba(58, 58, 58, 0.3)"
    BG_LAYER_ALT = "rgba(255, 255, 255, 0.0538)"
    BG_CARD_DEFAULT = "rgba(255, 255, 255, 0.0512)"
    BG_CARD_SECONDARY = "rgba(255, 255, 255, 0.0326)"
    BG_SMOKE = "rgba(0, 0, 0, 0.3)"
    BG_ACRYLIC_DEFAULT = "rgba(44, 44, 44, 0.96)"
    BG_ACRYLIC_BASE = "rgba(32, 32, 32, 0.9)"
    
    # Solid fallbacks (when Mica unavailable)
    BG_SOLID_BASE = "#202020"
    BG_SOLID_SECONDARY = "#1C1C1C"
    BG_SOLID_TERTIARY = "#282828"
    BG_SOLID_QUATERNARY = "#2C2C2C"
    
    # Stroke Colors (Dark Theme)
    STROKE_CONTROL_DEFAULT = "rgba(255, 255, 255, 0.0698)"
    STROKE_CONTROL_SECONDARY = "rgba(255, 255, 255, 0.093)"
    STROKE_CONTROL_ON_ACCENT = "rgba(0, 0, 0, 0.14)"
    STROKE_CONTROL_STRONG = "rgba(255, 255, 255, 0.545)"
    STROKE_SURFACE = "rgba(117, 117, 117, 0.4)"
    STROKE_DIVIDER = "rgba(255, 255, 255, 0.0837)"
    STROKE_CARD = "rgba(0, 0, 0, 0.1)"
    STROKE_FOCUS_OUTER = "#FFFFFF"
    STROKE_FOCUS_INNER = "rgba(0, 0, 0, 0.7)"
    
    # System Colors
    ATTENTION = "#60CDFF"
    SUCCESS = "#6CCB5F"
    CAUTION = "#FCE100"
    CRITICAL = "#FF99A4"
    CRITICAL_BG = "rgba(68, 39, 38, 0.7)"
    
    # Animation Timing (Windows 11 Motion - exact values)
    ANIM_FAST = 83      # Fast interactions
    ANIM_NORMAL = 167   # Standard transitions
    ANIM_SLOW = 250     # Emphasized transitions
    ANIM_SLOWER = 333   # Page transitions
    ANIM_SLOWEST = 500  # Large movements
    
    # Easing Curves (Windows 11 Motion)
    @staticmethod
    def ease_out():
        return QEasingCurve.OutCubic
    
    @staticmethod
    def ease_in_out():
        return QEasingCurve.InOutCubic
    
    @staticmethod
    def ease_bounce():
        return QEasingCurve.OutBack
    
    # Typography
    FONT_FAMILY = "Segoe UI Variable, Segoe UI, sans-serif"
    FONT_DISPLAY = 68
    FONT_TITLE_LARGE = 40
    FONT_TITLE = 28
    FONT_SUBTITLE = 20
    FONT_BODY_LARGE = 18
    FONT_BODY = 14
    FONT_BODY_STRONG = 14
    FONT_CAPTION = 12
    
    # Sizing (exact Windows 11 values)
    CONTROL_HEIGHT = 32
    CONTROL_CORNER_RADIUS = 4
    CARD_CORNER_RADIUS = 8
    OVERLAY_CORNER_RADIUS = 8
    NAV_INDICATOR_WIDTH = 3
    NAV_INDICATOR_HEIGHT = 16
    TOGGLE_WIDTH = 40
    TOGGLE_HEIGHT = 20
    TOGGLE_THUMB_SIZE = 12
    TOGGLE_THUMB_HOVER = 14

# ══════════════════════════════════════════════════════════════════════════════
# WINDOWS 11 FLUENT ICONS (Segoe Fluent Icons)
# ══════════════════════════════════════════════════════════════════════════════

class FluentIcons:
    """Windows 11 Segoe Fluent Icons"""
    HOME = "\uE80F"
    SETTINGS = "\uE713"
    HISTORY = "\uE81C"
    SEARCH = "\uE721"
    ADD = "\uE710"
    DELETE = "\uE74D"
    PLAY = "\uE768"
    PAUSE = "\uE769"
    STOP = "\uE71A"
    CHECKMARK = "\uE73E"
    CHEVRON_DOWN = "\uE70D"
    CHEVRON_RIGHT = "\uE76C"
    CHEVRON_UP = "\uE70E"
    EYE = "\uE7B3"
    EYE_OFF = "\uED1A"
    PERSON = "\uE77B"
    CLOUD_UPLOAD = "\uE753"
    DOWNLOAD = "\uE896"
    FOLDER = "\uE8B7"
    VIDEO = "\uE714"
    REFRESH = "\uE72C"
    SAVE = "\uE74E"
    COPY = "\uE8C8"
    INFO = "\uE946"
    WARNING = "\uE7BA"
    ERROR = "\uEA39"
    GLOBE = "\uE774"
    LINK = "\uE71B"
    CLOCK = "\uE823"
    CALENDAR = "\uE787"
    EDIT = "\uE70F"
    MORE = "\uE712"
    NAVIGATION = "\uE700"
    BACK = "\uE72B"
    FORWARD = "\uE72A"
    DISMISS = "\uE711"
    ACCEPT = "\uE8FB"

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STYLESHEET (WINDOWS 11 WINUI 3)
# ══════════════════════════════════════════════════════════════════════════════

def get_stylesheet(mica_enabled=False):
    """Generate stylesheet with Mica-aware backgrounds"""
    # Use transparent backgrounds when Mica is enabled, solid when not
    bg_main = "transparent" if mica_enabled else WinUI.BG_SOLID_BASE
    bg_nav = WinUI.BG_LAYER_DEFAULT if mica_enabled else WinUI.BG_SOLID_SECONDARY
    bg_content = "transparent" if mica_enabled else WinUI.BG_SOLID_BASE
    
    return f"""
    * {{
        font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
        font-size: 14px;
    }}
    
    QMainWindow {{
        background: {bg_main};
    }}
    
    QWidget#centralWidget {{
        background: {bg_main};
    }}
    
    QWidget#navPane {{
        background: {bg_nav};
        border-right: 1px solid {WinUI.STROKE_DIVIDER};
    }}
    
    QWidget#contentArea {{
        background: {bg_content};
    }}
    
    QScrollArea {{
        background: transparent;
        border: none;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    
    QScrollBar:vertical {{
        background: transparent;
        width: 14px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background: {WinUI.FILL_SUBTLE_SECONDARY};
        border-radius: 3px;
        min-height: 30px;
        margin: 3px 4px 3px 4px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {WinUI.FILL_CONTROL_SECONDARY};
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
        background: none;
    }}
    
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
    }}
    
    QLabel {{
        color: {WinUI.TEXT_PRIMARY};
        background: transparent;
    }}
    
    QLabel#title {{
        font-size: 28px;
        font-weight: 600;
        color: {WinUI.TEXT_PRIMARY};
        background: transparent;
    }}
    
    QLabel#subtitle {{
        font-size: 20px;
        font-weight: 600;
        color: {WinUI.TEXT_PRIMARY};
        background: transparent;
    }}
    
    QLabel#bodyStrong {{
        font-size: 14px;
        font-weight: 600;
        color: {WinUI.TEXT_PRIMARY};
        background: transparent;
    }}
    
    QLabel#body {{
        font-size: 14px;
        color: {WinUI.TEXT_PRIMARY};
        background: transparent;
    }}
    
    QLabel#caption {{
        font-size: 12px;
        color: {WinUI.TEXT_SECONDARY};
        background: transparent;
    }}
    
    QLabel#captionDim {{
        font-size: 12px;
        color: {WinUI.TEXT_TERTIARY};
        background: transparent;
    }}
    
    QLineEdit {{
        background: {WinUI.FILL_CONTROL_DEFAULT};
        border: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
        border-bottom: 1px solid {WinUI.STROKE_CONTROL_STRONG};
        border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
        padding: 5px 11px;
        color: {WinUI.TEXT_PRIMARY};
        selection-background-color: {WinUI.ACCENT_DEFAULT};
        min-height: 20px;
    }}
    
    QLineEdit:hover {{
        background: {WinUI.FILL_CONTROL_SECONDARY};
    }}
    
    QLineEdit:focus {{
        background: {WinUI.FILL_CONTROL_INPUT_ACTIVE};
        border: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
        border-bottom: 2px solid {WinUI.ACCENT_DEFAULT};
    }}
    
    QLineEdit:disabled {{
        background: {WinUI.FILL_CONTROL_DISABLED};
        color: {WinUI.TEXT_DISABLED};
        border: 1px solid transparent;
    }}
    
    QTextEdit {{
        background: {WinUI.FILL_CONTROL_DEFAULT};
        border: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
        border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
        padding: 8px 11px;
        color: {WinUI.TEXT_PRIMARY};
        selection-background-color: {WinUI.ACCENT_DEFAULT};
    }}
    
    QTextEdit:focus {{
        background: {WinUI.FILL_CONTROL_INPUT_ACTIVE};
        border: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
        border-bottom: 2px solid {WinUI.ACCENT_DEFAULT};
    }}
    
    QListWidget {{
        background: {WinUI.FILL_CONTROL_DEFAULT};
        border: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
        border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
        padding: 4px;
        color: {WinUI.TEXT_PRIMARY};
        outline: none;
    }}
    
    QListWidget::item {{
        padding: 8px 12px;
        border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
        margin: 2px 0;
        background: transparent;
    }}
    
    QListWidget::item:hover {{
        background: {WinUI.FILL_SUBTLE_SECONDARY};
    }}
    
    QListWidget::item:selected {{
        background: {WinUI.FILL_SUBTLE_TERTIARY};
        color: {WinUI.TEXT_PRIMARY};
    }}
    
    QFrame#card {{
        background: {WinUI.BG_CARD_DEFAULT};
        border: 1px solid {WinUI.STROKE_CARD};
        border-radius: {WinUI.CARD_CORNER_RADIUS}px;
    }}
    
    QFrame#cardAlt {{
        background: {WinUI.BG_CARD_SECONDARY};
        border: 1px solid {WinUI.STROKE_CARD};
        border-radius: {WinUI.CARD_CORNER_RADIUS}px;
    }}
    
    QFrame#separator {{
        background: {WinUI.STROKE_DIVIDER};
    }}
    
    QWidget#settingsRow {{
        background: transparent;
    }}
    """

# ══════════════════════════════════════════════════════════════════════════════
# WINDOWS 11 CUSTOM WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

class Win11Toggle(QWidget):
    """
    Authentic Windows 11 Toggle Switch
    Exact replica of WinUI 3 ToggleSwitch with proper animations
    
    Specs:
    - Track: 40x20px, 10px corner radius
    - Thumb: 12px (14px on hover), centered vertically
    - Off state: transparent track with white border, white thumb
    - On state: accent filled track, black thumb
    - Animation: 167ms cubic-bezier for position, smooth thumb scaling
    """
    toggled = Signal(bool)
    
    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self._hover = False
        self._pressed = False
        
        # Animation properties - exact Windows 11 positions
        # Off: thumb at x=10 (center of left side)
        # On: thumb at x=30 (center of right side)
        self._thumb_x = 30.0 if checked else 10.0
        self._thumb_width = 12.0  # Animates to stretched during transition
        self._track_fill = 1.0 if checked else 0.0
        
        self.setFixedSize(WinUI.TOGGLE_WIDTH, WinUI.TOGGLE_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        
        # Thumb position animation
        self._thumb_anim = QPropertyAnimation(self, b"thumbX", self)
        self._thumb_anim.setDuration(WinUI.ANIM_NORMAL)
        self._thumb_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Thumb width animation (stretch effect)
        self._width_anim = QPropertyAnimation(self, b"thumbWidth", self)
        self._width_anim.setDuration(WinUI.ANIM_NORMAL)
        self._width_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Track fill animation
        self._fill_anim = QPropertyAnimation(self, b"trackFill", self)
        self._fill_anim.setDuration(WinUI.ANIM_NORMAL)
        self._fill_anim.setEasingCurve(QEasingCurve.OutCubic)
    
    # Properties for animation
    def get_thumb_x(self): return self._thumb_x
    def set_thumb_x(self, v): self._thumb_x = v; self.update()
    thumbX = Property(float, get_thumb_x, set_thumb_x)
    
    def get_thumb_width(self): return self._thumb_width
    def set_thumb_width(self, v): self._thumb_width = v; self.update()
    thumbWidth = Property(float, get_thumb_width, set_thumb_width)
    
    def get_track_fill(self): return self._track_fill
    def set_track_fill(self, v): self._track_fill = v; self.update()
    trackFill = Property(float, get_track_fill, set_track_fill)
    
    def isChecked(self): return self._checked
    
    def setChecked(self, checked, animate=True):
        if self._checked != checked:
            self._checked = checked
            if animate:
                self._animate_toggle()
            else:
                self._thumb_x = 30.0 if checked else 10.0
                self._thumb_width = 12.0
                self._track_fill = 1.0 if checked else 0.0
                self.update()
            self.toggled.emit(checked)
    
    def _animate_toggle(self):
        # Stop all animations
        self._thumb_anim.stop()
        self._width_anim.stop()
        self._fill_anim.stop()
        
        # Thumb position
        self._thumb_anim.setStartValue(self._thumb_x)
        self._thumb_anim.setEndValue(30.0 if self._checked else 10.0)
        
        # Thumb stretch effect - Windows 11 stretches thumb during transition
        self._width_anim.setStartValue(12.0)
        self._width_anim.setKeyValueAt(0.3, 17.0)  # Stretch at 30%
        self._width_anim.setEndValue(12.0)
        
        # Track fill
        self._fill_anim.setStartValue(self._track_fill)
        self._fill_anim.setEndValue(1.0 if self._checked else 0.0)
        
        # Start all animations
        self._thumb_anim.start()
        self._width_anim.start()
        self._fill_anim.start()
    
    def enterEvent(self, event):
        self._hover = True
        self.update()
    
    def leaveEvent(self, event):
        self._hover = False
        self.update()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._pressed:
            self._pressed = False
            if self.rect().contains(event.pos()):
                self.setChecked(not self._checked)
            self.update()
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # Track colors based on state
        if self._track_fill > 0:
            # Interpolate between off and on colors
            if self._hover:
                track_color = QColor("#1A86D8") if self._track_fill > 0.5 else QColor(255, 255, 255, int(255 * 0.08))
            elif self._pressed:
                track_color = QColor("#0067B8") if self._track_fill > 0.5 else QColor(255, 255, 255, int(255 * 0.04))
            else:
                track_color = QColor(WinUI.ACCENT_DEFAULT)
            track_color.setAlphaF(self._track_fill)
            
            # Draw filled track
            p.setPen(Qt.NoPen)
            p.setBrush(track_color)
            p.drawRoundedRect(0, 0, w, h, h/2, h/2)
        
        # Draw track border (always visible, fades out when on)
        border_alpha = int(255 * 0.545 * (1.0 - self._track_fill))
        if border_alpha > 0 or self._track_fill < 1.0:
            if self._track_fill < 0.5:
                # Off state border
                if self._hover:
                    p.setPen(QPen(QColor(255, 255, 255, int(255 * 0.786)), 1.5))
                elif self._pressed:
                    p.setPen(QPen(QColor(255, 255, 255, int(255 * 0.545)), 1.5))
                else:
                    p.setPen(QPen(QColor(255, 255, 255, int(255 * 0.545)), 1.5))
                p.setBrush(Qt.NoBrush)
                p.drawRoundedRect(1, 1, w-2, h-2, (h-2)/2, (h-2)/2)
        
        # Thumb size - grows on hover
        base_size = WinUI.TOGGLE_THUMB_SIZE
        if self._hover and not self._pressed:
            thumb_h = WinUI.TOGGLE_THUMB_HOVER
        else:
            thumb_h = base_size
        
        # Thumb width (for stretch animation)
        thumb_w = self._thumb_width
        if self._hover and not self._pressed:
            thumb_w = max(thumb_w, 14.0)
        
        # Thumb position - centered on _thumb_x
        thumb_x = self._thumb_x - thumb_w / 2
        thumb_y = (h - thumb_h) / 2
        
        # Thumb color
        if self._track_fill > 0.5:
            # On state - black thumb
            thumb_color = QColor(WinUI.TEXT_ON_ACCENT)
        else:
            # Off state - white thumb
            thumb_color = QColor(255, 255, 255)
        
        # Draw thumb with rounded rect (pill shape when stretched)
        p.setPen(Qt.NoPen)
        p.setBrush(thumb_color)
        radius = thumb_h / 2
        p.drawRoundedRect(int(thumb_x), int(thumb_y), int(thumb_w), int(thumb_h), radius, radius)


class Win11Button(QPushButton):
    """
    Windows 11 styled button with proper hover/press states
    Matches WinUI 3 Button control exactly
    """
    
    def __init__(self, text="", icon=None, accent=False, parent=None):
        super().__init__(text, parent)
        self._accent = accent
        self._icon = icon
        
        self.setFixedHeight(WinUI.CONTROL_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
    
    def _update_style(self):
        if self._accent:
            # Accent button (primary action)
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {WinUI.ACCENT_DEFAULT};
                    border: 1px solid {WinUI.STROKE_CONTROL_ON_ACCENT};
                    border-bottom: 1px solid rgba(0, 0, 0, 0.4);
                    border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
                    color: {WinUI.TEXT_ON_ACCENT};
                    font-weight: 600;
                    padding: 0 16px;
                }}
                QPushButton:hover {{
                    background: #1A86D8;
                }}
                QPushButton:pressed {{
                    background: #0067B8;
                    border-bottom: 1px solid {WinUI.STROKE_CONTROL_ON_ACCENT};
                    color: rgba(0, 0, 0, 0.6);
                }}
                QPushButton:disabled {{
                    background: {WinUI.FILL_CONTROL_DISABLED};
                    border: 1px solid transparent;
                    color: {WinUI.TEXT_DISABLED};
                }}
            """)
        else:
            # Standard button
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {WinUI.FILL_CONTROL_DEFAULT};
                    border: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
                    border-bottom: 1px solid {WinUI.STROKE_CONTROL_STRONG};
                    border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
                    color: {WinUI.TEXT_PRIMARY};
                    padding: 0 16px;
                }}
                QPushButton:hover {{
                    background: {WinUI.FILL_CONTROL_SECONDARY};
                }}
                QPushButton:pressed {{
                    background: {WinUI.FILL_CONTROL_TERTIARY};
                    border-bottom: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
                    color: {WinUI.TEXT_SECONDARY};
                }}
                QPushButton:disabled {{
                    background: {WinUI.FILL_CONTROL_DISABLED};
                    border: 1px solid transparent;
                    color: {WinUI.TEXT_DISABLED};
                }}
            """)


class Win11IconButton(QPushButton):
    """Windows 11 icon-only button (subtle style)"""
    
    def __init__(self, icon, parent=None):
        super().__init__(parent)
        self._icon = icon
        self.setFixedSize(32, 32)
        self.setCursor(Qt.PointingHandCursor)
        self.setText(icon)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
                color: {WinUI.TEXT_SECONDARY};
                font-family: 'Segoe Fluent Icons', 'Segoe MDL2 Assets';
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: {WinUI.FILL_SUBTLE_SECONDARY};
                color: {WinUI.TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background: {WinUI.FILL_SUBTLE_TERTIARY};
            }}
        """)


class Win11ComboBox(QPushButton):
    """Windows 11 styled dropdown/combobox"""
    changed = Signal(str)
    
    def __init__(self, options, parent=None):
        super().__init__(parent)
        self._options = options
        self._value = options[0] if options else ""
        self._flyout = None
        
        self.setFixedHeight(WinUI.CONTROL_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        self.setText(self._value)
        
        self._update_style()
        self.clicked.connect(self._show_flyout)
    
    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {WinUI.FILL_CONTROL_DEFAULT};
                border: 1px solid {WinUI.STROKE_CONTROL};
                border-bottom: 1px solid {WinUI.STROKE_CONTROL_STRONG};
                border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
                color: {WinUI.TEXT_PRIMARY};
                padding: 0 36px 0 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {WinUI.FILL_CONTROL_SECONDARY};
            }}
            QPushButton:pressed {{
                background: {WinUI.FILL_CONTROL_TERTIARY};
            }}
        """)
    
    def currentText(self): return self._value
    
    def setCurrentText(self, value):
        if value in self._options:
            self._value = value
            self.setText(value)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Draw chevron
        p.setFont(QFont('Segoe Fluent Icons', 10))
        p.setPen(QColor(WinUI.TEXT_SECONDARY))
        chevron_rect = QRect(self.width() - 28, 0, 20, self.height())
        p.drawText(chevron_rect, Qt.AlignCenter, FluentIcons.CHEVRON_DOWN)
    
    def _show_flyout(self):
        self._flyout = Win11Flyout(self._options, self._on_select, self)
        pos = self.mapToGlobal(QPoint(0, self.height() + 4))
        self._flyout.show_at(pos, self.width())
    
    def _on_select(self, value):
        self._value = value
        self.setText(value)
        self.changed.emit(value)


class Win11Flyout(QFrame):
    """Windows 11 flyout menu"""
    
    def __init__(self, options, callback, parent=None):
        super().__init__(None)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._callback = callback
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        for opt in options:
            btn = QPushButton(opt)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
                    color: {WinUI.TEXT_PRIMARY};
                    padding: 0 12px;
                    text-align: left;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: {WinUI.FILL_SUBTLE_SECONDARY};
                }}
            """)
            btn.clicked.connect(lambda checked, o=opt: self._select(o))
            layout.addWidget(btn)
        
        # Opacity animation
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self._opacity_effect)
        
        self._show_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._show_anim.setDuration(WinUI.ANIM_NORMAL)
        self._show_anim.setEasingCurve(QEasingCurve.OutCubic)
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Background - solid color
        p.setBrush(QColor(WinUI.BG_SOLID_TERTIARY))
        p.setPen(QPen(QColor(WinUI.STROKE_CONTROL), 1))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), WinUI.OVERLAY_CORNER_RADIUS, WinUI.OVERLAY_CORNER_RADIUS)
    
    def show_at(self, pos, width):
        self.setFixedWidth(max(width, 120))
        self.adjustSize()
        self.move(pos)
        self.show()
        
        self._show_anim.stop()
        self._show_anim.setStartValue(0.0)
        self._show_anim.setEndValue(1.0)
        self._show_anim.start()
    
    def _select(self, value):
        self._callback(value)
        self.close()


class Win11PasswordInput(QLineEdit):
    """Windows 11 password input with reveal button"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setEchoMode(QLineEdit.Password)
        self.setFixedHeight(WinUI.CONTROL_HEIGHT)
        
        # Reveal button
        self._reveal_btn = QPushButton(FluentIcons.EYE, self)
        self._reveal_btn.setFixedSize(28, 28)
        self._reveal_btn.setCursor(Qt.PointingHandCursor)
        self._reveal_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
                color: {WinUI.TEXT_TERTIARY};
                font-family: 'Segoe Fluent Icons', 'Segoe MDL2 Assets';
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {WinUI.FILL_SUBTLE_SECONDARY};
                color: {WinUI.TEXT_PRIMARY};
            }}
        """)
        self._reveal_btn.pressed.connect(self._show_password)
        self._reveal_btn.released.connect(self._hide_password)
        
        # Adjust padding for button
        self.setStyleSheet(self.styleSheet() + "padding-right: 36px;")
    
    def _show_password(self):
        self.setEchoMode(QLineEdit.Normal)
        self._reveal_btn.setText(FluentIcons.EYE_OFF)
    
    def _hide_password(self):
        self.setEchoMode(QLineEdit.Password)
        self._reveal_btn.setText(FluentIcons.EYE)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reveal_btn.move(self.width() - 32, (self.height() - 28) // 2)


class Win11NavButton(QPushButton):
    """Windows 11 Navigation View item button"""
    
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._text = text
        self._selected = False
        
        self.setCheckable(True)
        self.setFixedHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")
    
    def setSelected(self, selected):
        self._selected = selected
        self.setChecked(selected)
        self.update()
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Background - semi-transparent for Mica compatibility
        if self._selected:
            p.setBrush(QColor(255, 255, 255, int(255 * 0.0605)))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(4, 0, self.width() - 8, self.height(), WinUI.CONTROL_CORNER_RADIUS, WinUI.CONTROL_CORNER_RADIUS)
        elif self.underMouse():
            p.setBrush(QColor(255, 255, 255, int(255 * 0.0419)))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(4, 0, self.width() - 8, self.height(), WinUI.CONTROL_CORNER_RADIUS, WinUI.CONTROL_CORNER_RADIUS)
        
        # Icon
        p.setFont(QFont('Segoe Fluent Icons', 14))
        if self._selected:
            p.setPen(QColor(255, 255, 255))
        else:
            p.setPen(QColor(255, 255, 255, int(255 * 0.786)))
        p.drawText(QRect(16, 0, 24, self.height()), Qt.AlignVCenter | Qt.AlignLeft, self._icon)
        
        # Text
        font = QFont('Segoe UI Variable', 13)
        font.setWeight(QFont.DemiBold if self._selected else QFont.Normal)
        p.setFont(font)
        if self._selected or self.underMouse():
            p.setPen(QColor(255, 255, 255))
        else:
            p.setPen(QColor(255, 255, 255, int(255 * 0.786)))
        p.drawText(QRect(52, 0, self.width() - 60, self.height()), Qt.AlignVCenter | Qt.AlignLeft, self._text)


class Win11NavIndicator(QWidget):
    """Windows 11 Navigation selection indicator with fluid animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(WinUI.NAV_INDICATOR_WIDTH)
        self.setFixedHeight(WinUI.NAV_INDICATOR_HEIGHT)
        
        self._target_y = 0
        
        # Position animation
        self._pos_anim = QPropertyAnimation(self, b"geometry", self)
        self._pos_anim.setDuration(WinUI.ANIM_SLOW)
        self._pos_anim.setEasingCurve(QEasingCurve.OutCubic)
    
    def move_to(self, y, animate=True):
        self._target_y = y
        
        if animate:
            start_rect = self.geometry()
            end_rect = QRect(0, y, WinUI.NAV_INDICATOR_WIDTH, WinUI.NAV_INDICATOR_HEIGHT)
            
            self._pos_anim.stop()
            self._pos_anim.setStartValue(start_rect)
            
            # Stretch effect during animation
            dist = abs(start_rect.y() - y)
            if dist > 20:
                mid_y = min(start_rect.y(), y)
                mid_h = dist + WinUI.NAV_INDICATOR_HEIGHT
                self._pos_anim.setKeyValueAt(0.35, QRect(0, mid_y, WinUI.NAV_INDICATOR_WIDTH, mid_h))
            
            self._pos_anim.setEndValue(end_rect)
            self._pos_anim.start()
        else:
            self.setGeometry(0, y, WinUI.NAV_INDICATOR_WIDTH, WinUI.NAV_INDICATOR_HEIGHT)
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(WinUI.ACCENT_DEFAULT))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 1.5, 1.5)


class Win11Card(QFrame):
    """Windows 11 card container"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 12)
        self._layout.setSpacing(12)
        
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("bodyStrong")
            self._layout.addWidget(title_label)
    
    def addWidget(self, widget):
        self._layout.addWidget(widget)
    
    def addLayout(self, layout):
        self._layout.addLayout(layout)
    
    def addSpacing(self, spacing):
        self._layout.addSpacing(spacing)


class Win11SettingsRow(QWidget):
    """Windows 11 Settings-style row with label and control"""
    
    def __init__(self, label, description=None, control=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)
        
        # Text column
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        
        label_widget = QLabel(label)
        label_widget.setObjectName("body")
        text_col.addWidget(label_widget)
        
        if description:
            desc_widget = QLabel(description)
            desc_widget.setObjectName("captionDim")
            text_col.addWidget(desc_widget)
        
        layout.addLayout(text_col, 1)
        
        if control:
            layout.addWidget(control)


class Win11HeroCard(QFrame):
    """Windows 11 Settings hero card (like the device info card)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setCursor(Qt.PointingHandCursor)
        
        # Accent-tinted background with gradient overlay
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(0, 120, 212, 0.15), 
                    stop:1 rgba(0, 120, 212, 0.05));
                border: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
                border-radius: {WinUI.CARD_CORNER_RADIUS}px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(0, 120, 212, 0.2), 
                    stop:1 rgba(0, 120, 212, 0.08));
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Icon/Image
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setText(FluentIcons.VIDEO)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            background: {WinUI.ACCENT_DEFAULT};
            border-radius: 8px;
            color: {WinUI.TEXT_ON_ACCENT};
            font-family: 'Segoe Fluent Icons', 'Segoe MDL2 Assets';
            font-size: 24px;
        """)
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        self._title = QLabel("Auto Post Engine")
        self._title.setStyleSheet(f"color: {WinUI.TEXT_PRIMARY}; font-size: 16px; font-weight: 600; background: transparent;")
        info_layout.addWidget(self._title)
        
        self._subtitle = QLabel("v3.0 • Windows 11 Native")
        self._subtitle.setStyleSheet(f"color: {WinUI.TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        info_layout.addWidget(self._subtitle)
        
        self._status = QLabel(f"{FluentIcons.CHECKMARK} Ready")
        self._status.setStyleSheet(f"color: {WinUI.SUCCESS}; font-size: 12px; font-family: 'Segoe Fluent Icons', 'Segoe UI'; background: transparent;")
        info_layout.addWidget(self._status)
        
        layout.addLayout(info_layout, 1)
        
        # Chevron
        chevron = QLabel(FluentIcons.CHEVRON_RIGHT)
        chevron.setStyleSheet(f"color: {WinUI.TEXT_TERTIARY}; font-family: 'Segoe Fluent Icons'; font-size: 12px; background: transparent;")
        layout.addWidget(chevron)
    
    def setStatus(self, text, color=None):
        self._status.setText(text)
        if color:
            self._status.setStyleSheet(f"color: {color}; font-size: 12px; font-family: 'Segoe Fluent Icons', 'Segoe UI'; background: transparent;")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    log_signal = Signal(dict)
    status_signal = Signal(dict)
    
    def __init__(self):
        super().__init__()
        
        # Track Mica state
        self._mica_enabled = False
        
        # Windows App ID for taskbar grouping
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'ape.v3.winui')
        except:
            pass
        
        self.setWindowTitle("Auto Post Engine")
        self.setMinimumSize(1000, 700)
        self.resize(1150, 800)
        
        # Icon
        icon_path = os.path.join(os.path.dirname(__file__), "win_logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        
        # Apply Mica effect FIRST (before stylesheet)
        if MICA_AVAILABLE:
            try:
                self.setAttribute(Qt.WA_TranslucentBackground)
                ApplyMica(int(self.winId()), MicaTheme.DARK, MicaStyle.DEFAULT)
                self._mica_enabled = True
            except Exception as e:
                logging.warning(f"Mica not available: {e}")
                self._mica_enabled = False
        
        # Apply stylesheet with Mica awareness
        self.setStyleSheet(get_stylesheet(mica_enabled=self._mica_enabled))
        
        # Initialize modules
        self.downloader = VideoDownloader()
        self.processor = VideoProcessor()
        self.uploader = TikTokUploader()
        self.db = HistoryManager()
        self.state = StateManager()
        self.running = False
        self.paused = False
        
        # Connect signals
        self.log_signal.connect(self._log_handler, Qt.QueuedConnection)
        self.status_signal.connect(self._status_handler, Qt.QueuedConnection)
        
        # Build UI
        self._build_ui()
        self._load_config()
        self._check_recovery()
        
        # Initial navigation
        self._navigate(0, animate=False)
    
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        # Navigation Pane - semi-transparent for Mica, solid fallback
        nav_pane = QFrame()
        nav_pane.setObjectName("navPane")
        nav_pane.setFixedWidth(280)
        nav_bg = WinUI.BG_LAYER_DEFAULT if self._mica_enabled else WinUI.BG_SOLID_SECONDARY
        nav_pane.setStyleSheet(f"""
            QFrame#navPane {{
                background: {nav_bg};
                border-right: 1px solid {WinUI.STROKE_DIVIDER};
            }}
        """)
        nav_layout = QVBoxLayout(nav_pane)
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(4)
        
        # App title in nav
        app_title = QLabel("Auto Post Engine")
        app_title.setStyleSheet(f"color: {WinUI.TEXT_PRIMARY}; font-size: 20px; font-weight: 600; padding: 8px 12px; background: transparent;")
        nav_layout.addWidget(app_title)
        
        nav_layout.addSpacing(8)
        
        # Search box (decorative)
        search_box = QLineEdit()
        search_box.setPlaceholderText(f"  {FluentIcons.SEARCH}  Search")
        search_box.setFixedHeight(36)
        nav_layout.addWidget(search_box)
        
        nav_layout.addSpacing(12)
        
        # Navigation buttons container (for indicator positioning)
        nav_buttons_container = QWidget()
        nav_buttons_container.setStyleSheet("background: transparent;")
        nav_buttons_layout = QVBoxLayout(nav_buttons_container)
        nav_buttons_layout.setContentsMargins(0, 0, 0, 0)
        nav_buttons_layout.setSpacing(4)
        
        # Navigation indicator
        self.nav_indicator = Win11NavIndicator(nav_buttons_container)
        self.nav_indicator.hide()
        
        # Navigation buttons
        self.nav_home = Win11NavButton(FluentIcons.HOME, "Home")
        self.nav_home.clicked.connect(lambda: self._navigate(0))
        nav_buttons_layout.addWidget(self.nav_home)
        
        self.nav_history = Win11NavButton(FluentIcons.HISTORY, "History")
        self.nav_history.clicked.connect(lambda: self._navigate(1))
        nav_buttons_layout.addWidget(self.nav_history)
        
        self.nav_settings = Win11NavButton(FluentIcons.SETTINGS, "Settings")
        self.nav_settings.clicked.connect(lambda: self._navigate(2))
        nav_buttons_layout.addWidget(self.nav_settings)
        
        nav_layout.addWidget(nav_buttons_container)
        nav_layout.addStretch()
        
        # Status at bottom
        self.status_label = QLabel(f"{FluentIcons.CHECKMARK} Ready")
        self.status_label.setObjectName("captionDim")
        self.status_label.setStyleSheet(f"color: {WinUI.TEXT_TERTIARY}; font-size: 12px; padding: 8px 12px; background: transparent;")
        nav_layout.addWidget(self.status_label)
        
        root_layout.addWidget(nav_pane)
        
        # Separator (hidden when Mica is enabled since nav pane has border)
        if not self._mica_enabled:
            separator = QFrame()
            separator.setFixedWidth(1)
            separator.setStyleSheet(f"background: {WinUI.STROKE_DIVIDER};")
            root_layout.addWidget(separator)
        
        # Content area - transparent for Mica, solid fallback
        self.content_stack = QStackedWidget()
        content_bg = "transparent" if self._mica_enabled else WinUI.BG_SOLID_BASE
        self.content_stack.setStyleSheet(f"background: {content_bg};")
        
        # Opacity effect for transitions
        self.content_opacity = QGraphicsOpacityEffect(self.content_stack)
        self.content_stack.setGraphicsEffect(self.content_opacity)
        
        # Page 0: Home
        self.page_home = QWidget()
        self._build_home_page(self.page_home)
        self.content_stack.addWidget(self.page_home)
        
        # Page 1: History
        self.page_history = QWidget()
        self._build_history_page(self.page_history)
        self.content_stack.addWidget(self.page_history)
        
        # Page 2: Settings
        self.page_settings = QWidget()
        self._build_settings_page(self.page_settings)
        self.content_stack.addWidget(self.page_settings)
        
        root_layout.addWidget(self.content_stack, 1)
    
    def _navigate(self, index, animate=True):
        if self.content_stack.currentIndex() == index and self.content_opacity.opacity() > 0.9:
            return
        
        def finish_navigation():
            self.content_stack.setCurrentIndex(index)
            
            # Update nav button states
            self.nav_home.setSelected(index == 0)
            self.nav_history.setSelected(index == 1)
            self.nav_settings.setSelected(index == 2)
            
            # Move indicator
            target_btn = [self.nav_home, self.nav_history, self.nav_settings][index]
            self.nav_indicator.show()
            indicator_y = target_btn.y() + (target_btn.height() - WinUI.NAV_INDICATOR_HEIGHT) // 2
            self.nav_indicator.move_to(indicator_y, animate)
            
            if animate:
                # Fade in
                self._fade_in = QPropertyAnimation(self.content_opacity, b"opacity", self)
                self._fade_in.setDuration(WinUI.ANIM_NORMAL)
                self._fade_in.setStartValue(0.0)
                self._fade_in.setEndValue(1.0)
                self._fade_in.setEasingCurve(QEasingCurve.OutCubic)
                self._fade_in.start()
            else:
                self.content_opacity.setOpacity(1.0)
        
        if animate:
            # Fade out
            self._fade_out = QPropertyAnimation(self.content_opacity, b"opacity", self)
            self._fade_out.setDuration(WinUI.ANIM_FAST)
            self._fade_out.setStartValue(self.content_opacity.opacity())
            self._fade_out.setEndValue(0.0)
            self._fade_out.setEasingCurve(QEasingCurve.InCubic)
            self._fade_out.finished.connect(finish_navigation)
            self._fade_out.start()
        else:
            finish_navigation()
    
    def _build_home_page(self, parent):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(24)
        
        # Page title
        title = QLabel("Home")
        title.setObjectName("title")
        title.setStyleSheet(f"color: {WinUI.TEXT_PRIMARY}; font-size: 28px; font-weight: 600; background: transparent;")
        layout.addWidget(title)
        
        # Hero card
        self.hero_card = Win11HeroCard()
        layout.addWidget(self.hero_card)
        
        # Two column layout
        columns = QHBoxLayout()
        columns.setSpacing(24)
        
        # Left column
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        
        # Queue card
        queue_card = Win11Card("Batch Queue")
        
        # URL input row
        url_row = QHBoxLayout()
        url_row.setSpacing(8)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL...")
        url_row.addWidget(self.url_input, 1)
        
        add_btn = Win11Button("Add", accent=True)
        add_btn.clicked.connect(self._add_to_queue)
        url_row.addWidget(add_btn)
        
        queue_card.addLayout(url_row)
        
        # Queue list
        self.queue_list = QListWidget()
        self.queue_list.setDragDropMode(QListWidget.InternalMove)
        self.queue_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.queue_list.setFixedHeight(140)
        queue_card.addWidget(self.queue_list)
        
        # Clear button
        clear_btn = Win11Button("Clear Queue")
        clear_btn.clicked.connect(self.queue_list.clear)
        queue_card.addWidget(clear_btn)
        
        left_col.addWidget(queue_card)
        
        # Processing settings card
        proc_card = Win11Card("Processing")
        
        # Duration
        self.duration_combo = Win11ComboBox(["30", "45", "60", "90", "120", "180", "240", "300"])
        self.duration_combo.setCurrentText("60")
        proc_card.addWidget(Win11SettingsRow("Part Duration", "Seconds per segment", self.duration_combo))
        
        # Throttle
        self.throttle_combo = Win11ComboBox(["0", "5", "10", "15", "30", "60", "120"])
        proc_card.addWidget(Win11SettingsRow("Job Gap", "Minutes between uploads", self.throttle_combo))
        
        # Crop toggle
        self.crop_toggle = Win11Toggle(True)
        proc_card.addWidget(Win11SettingsRow("Fit 9:16", "Crop for TikTok vertical", self.crop_toggle))
        
        # Speed toggle
        self.speed_toggle = Win11Toggle(False)
        proc_card.addWidget(Win11SettingsRow("1.25x Speed", "Helps evade copyright", self.speed_toggle))
        
        left_col.addWidget(proc_card)
        
        # Action buttons
        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        
        self.start_btn = Win11Button("Start Batch", accent=True)
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self._start_batch)
        action_row.addWidget(self.start_btn, 2)
        
        self.pause_btn = Win11Button("Pause")
        self.pause_btn.setFixedHeight(40)
        self.pause_btn.setVisible(False)
        self.pause_btn.clicked.connect(self._toggle_pause)
        action_row.addWidget(self.pause_btn, 1)
        
        self.stop_btn = Win11Button("Stop")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setVisible(False)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: {WinUI.CRITICAL};
                border: none;
                border-radius: {WinUI.CONTROL_CORNER_RADIUS}px;
                color: {WinUI.TEXT_ON_ACCENT};
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #FFB3BA; }}
            QPushButton:pressed {{ background: #FF8A94; }}
        """)
        self.stop_btn.clicked.connect(self._stop)
        action_row.addWidget(self.stop_btn, 1)
        
        left_col.addLayout(action_row)
        
        columns.addLayout(left_col, 1)
        
        # Right column
        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        
        # Account card
        account_card = Win11Card("TikTok Account")
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Email or Username")
        account_card.addWidget(Win11SettingsRow("Login", None, self.user_input))
        
        self.pwd_input = Win11PasswordInput("Password")
        account_card.addWidget(Win11SettingsRow("Password", None, self.pwd_input))
        
        # Upload toggle
        self.upload_toggle = Win11Toggle(True)
        account_card.addWidget(Win11SettingsRow("Upload to TikTok", "Enable automatic upload", self.upload_toggle))
        
        right_col.addWidget(account_card)
        
        # Metadata card
        meta_card = Win11Card("Metadata")
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Optional title override")
        meta_card.addWidget(Win11SettingsRow("Title", None, self.title_input))
        
        self.tags_input = QLineEdit()
        self.tags_input.setText("#fyp #viral")
        meta_card.addWidget(Win11SettingsRow("Hashtags", None, self.tags_input))
        
        # Auto-delete toggle
        self.autodel_toggle = Win11Toggle(False)
        meta_card.addWidget(Win11SettingsRow("Auto-Delete", "Remove source after upload", self.autodel_toggle))
        
        right_col.addWidget(meta_card)
        
        # Activity log card
        log_card = Win11Card("Activity Log")
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(180)
        log_card.addWidget(self.log_output)
        
        right_col.addWidget(log_card)
        
        columns.addLayout(right_col, 1)
        
        layout.addLayout(columns)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        page_layout = QVBoxLayout(parent)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
    
    def _build_history_page(self, parent):
        parent.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("History")
        title.setStyleSheet(f"color: {WinUI.TEXT_PRIMARY}; font-size: 28px; font-weight: 600; background: transparent;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("View and export your posting history")
        subtitle.setStyleSheet(f"color: {WinUI.TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(8)
        
        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        refresh_btn = Win11Button(f"{FluentIcons.REFRESH} Refresh")
        refresh_btn.clicked.connect(self._refresh_history)
        btn_row.addWidget(refresh_btn)
        
        export_btn = Win11Button(f"{FluentIcons.SAVE} Export to TXT")
        export_btn.clicked.connect(self._export_history)
        btn_row.addWidget(export_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # History list
        self.history_output = QTextEdit()
        self.history_output.setReadOnly(True)
        self.history_output.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 12px;
                background: {WinUI.FILL_CONTROL_DEFAULT};
                border: 1px solid {WinUI.STROKE_CONTROL_DEFAULT};
                border-radius: {WinUI.CARD_CORNER_RADIUS}px;
                padding: 12px;
            }}
        """)
        layout.addWidget(self.history_output, 1)
    
    def _build_settings_page(self, parent):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(24)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet(f"color: {WinUI.TEXT_PRIMARY}; font-size: 28px; font-weight: 600; background: transparent;")
        layout.addWidget(title)
        
        # About card
        about_card = Win11Card("About")
        
        about_info = QLabel("Auto Post Engine v3.0\nWindows 11 Native UI with WinUI 3 Design")
        about_info.setStyleSheet(f"color: {WinUI.TEXT_PRIMARY}; background: transparent;")
        about_card.addWidget(about_info)
        
        layout.addWidget(about_card)
        
        # Advanced card
        advanced_card = Win11Card("Advanced")
        
        # Browser preference (placeholder)
        browser_combo = Win11ComboBox(["Chrome", "Brave", "Edge"])
        advanced_card.addWidget(Win11SettingsRow("Browser", "For TikTok automation", browser_combo))
        
        layout.addWidget(advanced_card)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        page_layout = QVBoxLayout(parent)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
    
    # ══════════════════════════════════════════════════════════════════════════
    # LOGIC HANDLERS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _add_to_queue(self):
        url = self.url_input.text().strip()
        if url:
            if self.db.check_exists(url):
                reply = QMessageBox.question(
                    self, "Duplicate Detected",
                    "This URL exists in history. Add anyway?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            self.queue_list.addItem(url)
            self.url_input.clear()
    
    def _refresh_history(self):
        rows = self.db.get_all_history()
        txt = f"{'Date':<20} | {'Status':<10} | {'Title'}\n"
        txt += "─" * 90 + "\n"
        for r in rows:
            txt += f"{r[2]:<20} | {r[4]:<10} | {r[1]}\n"
        self.history_output.setText(txt)
    
    def _export_history(self):
        if self.db.export_to_txt():
            QMessageBox.information(self, "Export Complete", "History saved to history_export.txt")
    
    def _log_handler(self, data):
        logging.info(data['m'])
        color = data.get('c', WinUI.TEXT_PRIMARY)
        update = data.get('u', False)
        msg = data['m']
        
        html = f'<span style="color:{color}">› {msg}</span>'
        
        scrollbar = self.log_output.verticalScrollBar()
        at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
        
        if update:
            cursor = self.log_output.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertHtml(html)
        else:
            self.log_output.append(html)
        
        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
    
    def _status_handler(self, data):
        self.status_label.setText(data['m'])
        self.hero_card.setStatus(data['m'])
    
    def _check_recovery(self):
        state = self.state.load_state()
        if state and state.get('active') and state.get('queue'):
            reply = QMessageBox.question(
                self, "Session Recovery",
                "A previous session was interrupted. Resume?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for url in state['queue']:
                    self.queue_list.addItem(url)
                self.log_signal.emit({'m': "Session restored.", 'c': WinUI.ACCENT_DEFAULT, 'u': False})
    
    def _start_batch(self):
        queue = [self.queue_list.item(i).text() for i in range(self.queue_list.count())]
        if not queue:
            return
        
        self.running = True
        self.paused = False
        self.start_btn.setVisible(False)
        self.pause_btn.setVisible(True)
        self.pause_btn.setText("Pause")
        self.stop_btn.setVisible(True)
        
        config = {
            'dur': int(self.duration_combo.currentText()),
            'crop': self.crop_toggle.isChecked(),
            'speed': self.speed_toggle.isChecked(),
            'user': self.user_input.text(),
            'pwd': self.pwd_input.text(),
            'title': self.title_input.text(),
            'tags': self.tags_input.text(),
            'upload': self.upload_toggle.isChecked(),
            'del': self.autodel_toggle.isChecked(),
            'throttle': int(self.throttle_combo.currentText()),
            'queue': queue
        }
        
        self._save_config()
        
        if config['user']:
            self.uploader.set_credentials(config['user'], config['pwd'])
        
        threading.Thread(target=self._batch_work, args=(config,), daemon=True).start()
    
    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.setText("Resume")
            self.log_signal.emit({'m': "Paused. Waiting for current step...", 'c': WinUI.ACCENT_DEFAULT, 'u': False})
        else:
            self.pause_btn.setText("Pause")
            self.log_signal.emit({'m': "Resumed.", 'c': WinUI.SUCCESS, 'u': False})
    
    def _stop(self):
        self.running = False
        self.paused = False
        self.processor.cancel()
        self.uploader.cancel()
        self.log_signal.emit({'m': "Stopped.", 'c': WinUI.CRITICAL, 'u': False})
    
    def _batch_work(self, config):
        queue = config['queue']
        
        for i, url in enumerate(queue):
            if not self.running:
                break
            
            while self.paused and self.running:
                self.status_signal.emit({'m': f"{FluentIcons.PAUSE} Paused"})
                time.sleep(1)
            
            if not self.running:
                break
            
            if self.db.check_exists(url):
                self.log_signal.emit({'m': f"Skipping duplicate: {url}", 'c': WinUI.CRITICAL, 'u': False})
                continue
            
            self.state.save_state(queue, i)
            self.log_signal.emit({'m': f"─── Processing {i+1}/{len(queue)} ───", 'c': WinUI.TEXT_PRIMARY, 'u': False})
            
            try:
                # Download
                self.status_signal.emit({'m': f"{FluentIcons.DOWNLOAD} Downloading..."})
                
                def progress_callback(pct, msg):
                    if not self.running:
                        return
                    self.log_signal.emit({'m': msg, 'c': WinUI.TEXT_TERTIARY, 'u': '%' in msg or 'Part' in msg})
                
                filepath = self.downloader.download_video(url, progress_callback=progress_callback)
                if not filepath:
                    continue
                if not os.path.exists(filepath):
                    base = os.path.splitext(filepath)[0] + ".mp4"
                    if os.path.exists(base):
                        filepath = base
                
                while self.paused and self.running:
                    self.status_signal.emit({'m': f"{FluentIcons.PAUSE} Paused"})
                    time.sleep(1)
                if not self.running:
                    break
                
                # Process
                self.status_signal.emit({'m': f"{FluentIcons.VIDEO} Processing..."})
                parts = self.processor.segment_video(filepath, config['dur'], config['crop'], config['speed'], progress_callback=progress_callback)
                if not parts:
                    continue
                
                while self.paused and self.running:
                    self.status_signal.emit({'m': f"{FluentIcons.PAUSE} Paused"})
                    time.sleep(1)
                if not self.running:
                    break
                
                # Upload
                if config['upload']:
                    video_title = config['title'] or self.downloader.last_title
                    
                    for j, part in enumerate(parts):
                        if not self.running:
                            break
                        
                        while self.paused and self.running:
                            self.status_signal.emit({'m': f"{FluentIcons.PAUSE} Paused"})
                            time.sleep(1)
                        if not self.running:
                            break
                        
                        part_info = f"Part {j+1}/{len(parts)}"
                        caption = f"{video_title} ({part_info}) {config['tags']}"
                        
                        def upload_callback(pct, m):
                            progress_callback(pct, f"[{part_info}] {m}")
                        
                        self.log_signal.emit({'m': f"Uploading {part_info}", 'c': WinUI.ACCENT_DEFAULT, 'u': False})
                        
                        if self.uploader.upload_video(part, caption, config['tags'], progress_callback=upload_callback):
                            self.log_signal.emit({'m': f"Uploaded {part_info}", 'c': WinUI.SUCCESS, 'u': False})
                            if config['del']:
                                os.remove(part)
                
                self.db.add_entry(url, self.downloader.last_title, config['user'])
                
                if config['del'] and os.path.exists(filepath):
                    os.remove(filepath)
                
                # Throttle
                if config['throttle'] > 0 and i < len(queue) - 1:
                    mins = config['throttle']
                    self.log_signal.emit({'m': f"Waiting {mins} minutes before next job...", 'c': WinUI.TEXT_TERTIARY, 'u': False})
                    
                    for m in range(mins * 60):
                        if not self.running:
                            break
                        while self.paused and self.running:
                            self.status_signal.emit({'m': f"{FluentIcons.PAUSE} Paused"})
                            time.sleep(1)
                        if m % 60 == 0:
                            remaining = mins - (m // 60)
                            self.status_signal.emit({'m': f"{FluentIcons.CLOCK} Next job in {remaining}m"})
                        time.sleep(1)
            
            except Exception as e:
                self.log_signal.emit({'m': f"Error: {e}", 'c': WinUI.CRITICAL, 'u': False})
        
        self.state.clear_state()
        self.running = False
        self.paused = False
        self.status_signal.emit({'m': f"{FluentIcons.CHECKMARK} Done"})
        
        # Restore UI
        from PySide6.QtCore import QMetaObject, Q_ARG
        QMetaObject.invokeMethod(self.start_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, True))
        QMetaObject.invokeMethod(self.pause_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
        QMetaObject.invokeMethod(self.stop_btn, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
    
    def _save_config(self):
        data = {
            'title': self.title_input.text(),
            'tags': self.tags_input.text(),
            'dur': self.duration_combo.currentText(),
            'crop': self.crop_toggle.isChecked(),
            'speed': self.speed_toggle.isChecked(),
            'user': self.user_input.text(),
            'pwd': self.pwd_input.text(),
            'upload': self.upload_toggle.isChecked(),
            'autodel': self.autodel_toggle.isChecked(),
            'browser': self.uploader.browser_type,
            'throttle': self.throttle_combo.currentText()
        }
        try:
            with open("config.json", 'w') as f:
                json.dump(data, f, indent=4)
        except:
            pass
    
    def _load_config(self):
        if not os.path.exists("config.json"):
            return
        try:
            with open("config.json", 'r') as f:
                data = json.load(f)
            
            if 'title' in data:
                self.title_input.setText(data['title'])
            if 'tags' in data:
                self.tags_input.setText(data['tags'])
            if 'user' in data:
                self.user_input.setText(data['user'])
            if 'pwd' in data:
                self.pwd_input.setText(data['pwd'])
            if 'dur' in data:
                self.duration_combo.setCurrentText(str(data['dur']))
            if 'crop' in data:
                self.crop_toggle.setChecked(data['crop'], animate=False)
            if 'speed' in data:
                self.speed_toggle.setChecked(data['speed'], animate=False)
            if 'upload' in data:
                self.upload_toggle.setChecked(data['upload'], animate=False)
            if 'autodel' in data:
                self.autodel_toggle.setChecked(data['autodel'], animate=False)
            if 'throttle' in data:
                self.throttle_combo.setCurrentText(str(data['throttle']))
            if 'browser' in data:
                self.uploader.set_browser_preference(data['browser'])
        except:
            pass


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set dark palette for non-styled widgets
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(32, 32, 32))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(32, 32, 32))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(32, 32, 32))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(0, 120, 212))
    palette.setColor(QPalette.Highlight, QColor(0, 120, 212))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
