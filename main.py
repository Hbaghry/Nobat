import os
import sys
import json
import datetime
from pathlib import Path

from kivy.config import Config
Config.set('graphics', 'width', '420')
Config.set('graphics', 'height', '880')
Config.set('kivy', 'keyboard_mode', 'systemandmulti')
Config.set('graphics', 'resizable', '1')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty,
    ObjectProperty, ListProperty
)
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import (
    Color, RoundedRectangle, Rectangle, Line, Ellipse
)

# ============================================================
# کتابخانه‌های اختیاری
# ============================================================
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import jdatetime
    HAS_JDATE = True
except ImportError:
    HAS_JDATE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_PERSIAN = True
except ImportError:
    HAS_PERSIAN = False


# ============================================================
# توابع کمکی فارسی
# ============================================================
def fa(text):
    """تبدیل متن فارسی به شکل نمایشی درست (RTL)"""
    if not text:
        return ''
    if not HAS_PERSIAN:
        return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)


FA_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def to_fa(text):
    """تبدیل اعداد لاتین به فارسی"""
    return str(text).translate(FA_DIGITS)


def jnow():
    return jdatetime.datetime.now() if HAS_JDATE else datetime.datetime.now()


def jdate_str():
    return jnow().strftime('%Y/%m/%d')


def jtime_str():
    return jnow().strftime('%H:%M')


def jweekday():
    if HAS_JDATE:
        return ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه',
                'چهارشنبه', 'پنجشنبه', 'جمعه'][jnow().weekday()]
    return ''


# ============================================================
# مسیرهای برنامه (سازگار با اندروید و دسکتاپ)
# ============================================================
def get_app_dir():
    """مسیر ذخیره‌سازی دائمی برنامه"""
    if platform == 'android':
        try:
            from android.storage import app_storage_path
            return Path(app_storage_path())
        except Exception:
            pass
    return Path(__file__).parent


def get_bundle_dir():
    """مسیر فایل‌های همراه برنامه (فونت‌ها)"""
    if platform == 'android':
        # در اندروید فایل‌ها در _python_bundle قرار می‌گیرند
        here = Path(__file__).parent
        candidates = [
            here,
            here.parent,
            Path('/data/data/ir.nobat.nobat/files/app'),
            Path('/data/data/ir.nobat.nobat/files/app/_python_bundle'),
        ]
        for c in candidates:
            if c.exists() and (c / 'fonts').exists():
                return c
        return here
    return Path(__file__).parent


APP_DIR = get_app_dir()
BUNDLE_DIR = get_bundle_dir()


def find_font(names):
    """جستجوی فونت در همه مسیرهای ممکن"""
    search_paths = []
    if platform == 'android':
        search_paths.extend([
            BUNDLE_DIR / 'fonts',
            BUNDLE_DIR,
            APP_DIR / 'fonts',
            Path('/data/data/ir.nobat.nobat/files/app/fonts'),
            Path('/data/data/ir.nobat.nobat/files/app/_python_bundle/fonts'),
            Path('/sdcard/nobat/fonts'),
        ])
    else:
        search_paths.append(Path(__file__).parent / 'fonts')
    search_paths.append(Path('fonts'))

    for name in names:
        # جستجوی مستقیم
        for base in search_paths:
            p = base / name
            try:
                if p.exists():
                    print(f"✅ فونت پیدا شد: {p}")
                    return str(p)
            except Exception:
                pass
        # جستجوی بازگشتی
        for base in search_paths:
            try:
                if base.exists():
                    for found in base.rglob(name):
                        print(f"✅ فونت پیدا شد (rglob): {found}")
                        return str(found)
            except Exception:
                pass
    print(f"⚠️ فونت‌های {names} پیدا نشدند")
    return None


UI_FONT = find_font([
    'Vazirmatn-MediumMonoSpacedNum.ttf',
    'Vazirmatn-Medium.ttf',
])
NUM_FONT = find_font([
    'Vazir.ttf',
    'Sahel.ttf',
    'Vazirmatn-Medium.ttf',
    'Vazirmatn-MediumMonoSpacedNum.ttf',
])

# ثبت فونت‌ها
try:
    if UI_FONT:
        LabelBase.register(name='Vazirmatn-Medium', fn_regular=UI_FONT)
        print(f"✅ فونت UI ثبت شد")
    else:
        LabelBase.register(name='Vazirmatn-Medium', fn_regular='Roboto')
except Exception as e:
    print(f"⚠️ خطا در ثبت فونت UI: {e}")
    LabelBase.register(name='Vazirmatn-Medium', fn_regular='Roboto')

try:
    if NUM_FONT:
        LabelBase.register(name='NumFont', fn_regular=NUM_FONT)
        print(f"✅ فونت اعداد ثبت شد")
    else:
        LabelBase.register(name='NumFont', fn_regular='Roboto')
except Exception as e:
    print(f"⚠️ خطا در ثبت فونت اعداد: {e}")
    LabelBase.register(name='NumFont', fn_regular='Roboto')


# ============================================================
# تنظیمات
# ============================================================
SETTINGS_FILE = APP_DIR / 'settings.json'

DEFAULT_SETTINGS = {
    "daily_reset": True,
    "confirm_before_print": True,
    "print_copies": 1,
    "current_number": 0,
    "last_printed_number": 0,
    "last_reset_date": "",
    "logo_path": "",
    "show_logo": False,
    "header_text": "قهوه باران",
    "footer_text": "خوش آمدید",
    "menu_enabled": False,
    "menu_items_text": "چای\nقهوه\nآب معدنی\nکیک\nشیرینی",
    "print_order_with_number": True,
}


class SettingsManager:
    def __init__(self):
        self.data = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        try:
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self.data.update(json.load(f))
                print(f"✅ تنظیمات بارگذاری شد: {SETTINGS_FILE}")
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تنظیمات: {e}")

    def save(self):
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ خطا در ذخیره تنظیمات: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()


class QueueManager:
    def __init__(self, settings):
        self.settings = settings
        self._check_daily_reset()

    def _check_daily_reset(self):
        if not self.settings.get('daily_reset'):
            return
        today = jdate_str()
        if self.settings.get('last_reset_date', '') != today:
            self.settings.set('current_number', 0)
            self.settings.set('last_printed_number', 0)
            self.settings.set('last_reset_date', today)
            print(f"🔄 ریست روزانه انجام شد ({today})")

    def get_last_printed(self):
        self._check_daily_reset()
        return self.settings.get('last_printed_number', 0)

    def get_next_suggested(self):
        return self.get_last_printed() + 1

    def set_printed(self, n):
        self.settings.set('last_printed_number', int(n))
        self.settings.set('current_number', int(n))
        self.settings.set('last_reset_date', jdate_str())

    def reset_today(self):
        self.settings.set('current_number', 0)
        self.settings.set('last_printed_number', 0)
        self.settings.set('last_reset_date', jdate_str())


# ============================================================
# ساخت رسید (Pillow)
# ============================================================
class ReceiptRenderer:
    WIDTH = 384

    @staticmethod
    def _fa(text):
        if not HAS_PERSIAN or not text:
            return str(text) if text else ''
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except Exception:
            return str(text)

    @staticmethod
    def _text_size(d, text, font):
        bbox = d.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    @staticmethod
    def render(number, header, footer, logo_path=None, order_items=None):
        if not HAS_PIL:
            print("⚠️ Pillow نصب نیست")
            return None, b''

        # بارگذاری فونت‌ها
        font_num = font_mid = font_small = font_tiny = font_item = None
        try:
            font_num = ImageFont.truetype(NUM_FONT or UI_FONT or 'arial.ttf', 110)
        except Exception:
            try:
                font_num = ImageFont.truetype(UI_FONT or 'arial.ttf', 110)
            except Exception:
                font_num = ImageFont.load_default()

        for size, attr in [(32, 'font_mid'), (24, 'font_small'),
                           (20, 'font_tiny'), (26, 'font_item')]:
            try:
                f = ImageFont.truetype(UI_FONT or 'arial.ttf', size)
            except Exception:
                f = ImageFont.load_default()
            if attr == 'font_mid':
                font_mid = f
            elif attr == 'font_small':
                font_small = f
            elif attr == 'font_tiny':
                font_tiny = f
            elif attr == 'font_item':
                font_item = f

        tmp = Image.new('L', (1, 1), 255)
        td = ImageDraw.Draw(tmp)

        # محاسبه ارتفاع
        H = 20
        logo_img = None
        if logo_path and os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path).convert('L')
                ratio = 180 / logo_img.width
                logo_img = logo_img.resize(
                    (180, int(logo_img.height * ratio)), Image.LANCZOS
                )
                H += logo_img.height + 10
            except Exception as e:
                print(f"⚠️ خطا لوگو: {e}")
                logo_img = None

        H += 22
        H += ReceiptRenderer._text_size(
            td, ReceiptRenderer._fa(header), font_mid)[1] + 25
        H += 22
        H += 30 + 30 + 30
        H += 17
        H += ReceiptRenderer._text_size(
            td, ReceiptRenderer._fa("شماره نوبت شما"), font_mid)[1] + 20
        H += ReceiptRenderer._text_size(
            td, to_fa(f"{number:03d}"), font_num)[1] + 35

        if order_items:
            H += 22
            H += ReceiptRenderer._text_size(
                td, ReceiptRenderer._fa("سفارش شما"), font_mid)[1] + 20
            for _ in order_items:
                H += ReceiptRenderer._text_size(td, "x", font_item)[1] + 12
            H += 15

        H += 27
        H += ReceiptRenderer._text_size(
            td, ReceiptRenderer._fa(footer), font_small)[1] + 25
        H += 45
        H += 30

        img = Image.new('L', (ReceiptRenderer.WIDTH, int(H) + 30), 255)
        d = ImageDraw.Draw(img)
        y = 15

        def center(text, font, yy, is_fa=True, fill=0):
            t = ReceiptRenderer._fa(text) if is_fa else text
            bbox = d.textbbox((0, 0), t, font=font)
            tw = bbox[2] - bbox[0]
            d.text(((ReceiptRenderer.WIDTH - tw) // 2, yy),
                   t, font=font, fill=fill)
            return bbox[3] - bbox[1]

        def hline(yy, width=1):
            d.line([(20, yy), (ReceiptRenderer.WIDTH - 20, yy)],
                   fill=0, width=width)

        if logo_img:
            img.paste(logo_img,
                      ((ReceiptRenderer.WIDTH - logo_img.width) // 2, y))
            y += logo_img.height + 10

        hline(y, 2)
        y += 12
        y += center(header or 'سیستم نوبت‌دهی', font_mid, y) + 18
        hline(y, 1)
        y += 12

        y += center(f"تاریخ: {to_fa(jdate_str())}", font_small, y) + 8
        if jweekday():
            y += center(jweekday(), font_tiny, y) + 5
        y += center(f"ساعت: {to_fa(jtime_str())}", font_small, y) + 25

        hline(y, 1)
        y += 15
        y += center("شماره نوبت شما", font_mid, y) + 18
        num_text = to_fa(f"{number:03d}")
        y += center(num_text, font_num, y, is_fa=False) + 25

        if order_items:
            y += 15
            y += center("سفارش شما", font_mid, y) + 15
            for item in order_items:
                y += center(f"• {item}", font_item, y) + 10
            y += 10

        hline(y, 1)
        y += 15
        y += center(footer or 'لطفاً منتظر بمانید', font_small, y) + 20
        center("─ ─ ─ ─ ─ ─", font_small, y)
        y += 25
        center("با تشکر از همراهی شما", font_tiny, y)
        y += 25

        img = img.crop((0, 0, ReceiptRenderer.WIDTH,
                        min(y + 10, img.height)))
        return img, ReceiptRenderer.to_escpos_raster(img)

    @staticmethod
    def to_escpos_raster(img):
        width_bytes = (img.width + 7) // 8
        header = bytes([
            0x1D, 0x76, 0x30, 0x00,
            width_bytes & 0xFF, (width_bytes >> 8) & 0xFF,
            img.height & 0xFF, (img.height >> 8) & 0xFF,
        ])
        data = bytearray(header)
        pixels = img.load()
        for y in range(img.height):
            byte = 0
            bit = 0
            for x in range(img.width):
                if pixels[x, y] < 128:
                    byte |= (0x80 >> bit)
                bit += 1
                if bit == 8:
                    data.append(byte)
                    byte = 0
                    bit = 0
            if bit > 0:
                data.append(byte)
        data.extend(b'\n\n\n\n')
        data.extend(b'\x1D\x56\x00')
        return bytes(data)


# ============================================================
# پرینتر
# ============================================================
class POSPrinter:
    def __init__(self):
        self.method = None
        self.connected = False
        self._init_printer()

    def _init_printer(self):
        if platform != 'android':
            self.method = 'mock'
            self.connected = False
            print("ℹ️ حالت دسکتاپ — شبیه‌ساز")
            return
        if self._try_sunmi():
            return
        if self._try_wooyou():
            return
        if self._try_serial():
            return
        self.method = 'mock'
        print("ℹ️ پرینتر واقعی پیدا نشد — شبیه‌ساز")

    def _try_sunmi(self):
        try:
            from jnius import autoclass
            autoclass('com.sunmi.peripheral.printer.InnerPrinterManager')
            self.method = 'sunmi'
            self.connected = True
            print("✅ پرینتر Sunmi پیدا شد")
            return True
        except Exception:
            return False

    def _try_wooyou(self):
        try:
            from jnius import autoclass
            autoclass('woyou.aidlservice.jiuiv5.IWoyouService')
            self.method = 'wooyou'
            self.connected = True
            print("✅ پرینتر Wooyou پیدا شد")
            return True
        except Exception:
            return False

    def _try_serial(self):
        for port in ['/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2']:
            if os.path.exists(port):
                self.method = f'serial:{port}'
                self.connected = True
                print(f"✅ پرینتر سریال پیدا شد: {port}")
                return True
        return False

    def print_receipt(self, number, copies=1, logo_path=None,
                      header="", footer="", order_items=None):
        img, escpos = ReceiptRenderer.render(
            number, header, footer, logo_path, order_items
        )
        if img is not None:
            try:
                img.save(APP_DIR / 'last_receipt.png')
                print(f"📄 پیش‌نمایش ذخیره شد: {APP_DIR / 'last_receipt.png'}")
            except Exception as e:
                print(f"⚠️ خطا ذخیره پیش‌نمایش: {e}")

        for _ in range(copies):
            self._send(escpos, img)
        return True

    def _send(self, escpos, img):
        if self.method == 'mock' or not self.connected:
            print("🖨️ [شبیه‌ساز] چاپ شد")
            return True
        try:
            if self.method.startswith('serial:'):
                port = self.method.split(':', 1)[1]
                with open(port, 'wb') as f:
                    f.write(escpos)
                return True
            return True
        except Exception as e:
            print(f"❌ خطا چاپ: {e}")
            return False


# ============================================================
# ویجت‌های سفارشی
# ============================================================
class SwitchRow(BoxLayout):
    """ردیف سوئیچ: متن سمت راست، سوئیچ سمت چپ"""
    row_label = StringProperty('')
    row_active = BooleanProperty(False)
    row_callback = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(54)
        self.spacing = dp(12)
        self.padding = [dp(2), 0, dp(2), 0]

        self._switch = Switch(
            size_hint=(None, None),
            width=dp(58),
            height=dp(38),
            pos_hint={'center_y': 0.5},
            active=self.row_active,
        )
        self._switch.bind(active=self._on_switch_active)

        self._label = Label(
            font_name='Vazirmatn-Medium',
            font_size=sp(15),
            color=(0.13, 0.18, 0.28, 1),
            halign='right',
            valign='middle',
        )
        self._label.bind(size=lambda *a: setattr(
            self._label, 'text_size',
            (self._label.width, self._label.height)
        ))
        self.add_widget(self._switch)
        self.add_widget(self._label)

        self.bind(row_label=self._update_label,
                  row_active=self._update_active)
        self._update_label()

    def _update_label(self, *a):
        self._label.text = fa(self.row_label) if self.row_label else ''

    def _update_active(self, *a):
        if self._switch.active != self.row_active:
            self._switch.active = self.row_active

    def _on_switch_active(self, inst, val):
        if val != self.row_active and self.row_callback:
            try:
                self.row_callback(val)
            except Exception as e:
                print(f"callback err: {e}")


class FaTextInput(FloatLayout):
    """ورودی متن با نمایش فارسی (RTL)"""
    text = StringProperty('')
    hint_text = StringProperty('')
    multiline = BooleanProperty(False)
    font_size = NumericProperty(sp(16))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._updating = False
        self.size_hint_y = 1

        with self.canvas.before:
            Color(0.98, 0.99, 1, 1)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
            self._border_color = Color(0.85, 0.88, 0.93, 1)
            self._border_line = Line(
                rounded_rectangle=(
                    self.x, self.y, self.width, self.height, dp(12)
                ),
                width=1.2
            )

        self._label = Label(
            font_name='Vazirmatn-Medium',
            font_size=self.font_size,
            color=(0.15, 0.18, 0.25, 1),
            halign='right',
            valign='middle',
            size_hint=(None, None),
        )
        self.add_widget(self._label)

        self._ti = TextInput(
            font_name='Vazirmatn-Medium',
            font_size=self.font_size,
            foreground_color=(0, 0, 0, 0),
            background_normal='',
            background_active='',
            background_color=(0, 0, 0, 0),
            cursor_color=(0.13, 0.5, 0.92, 1),
            halign='right',
            multiline=self.multiline,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0},
            padding=[dp(14), dp(10), dp(14), dp(10)],
        )
        self._ti.bind(text=self._on_ti_text, focus=self._on_focus)
        self.add_widget(self._ti)

        self.bind(pos=self._redraw, size=self._redraw,
                  text=self._on_self_text,
                  hint_text=self._update_label,
                  multiline=self._update_multiline,
                  font_size=self._update_font)
        self._update_label()

    def _redraw(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        try:
            self._border_line.rounded_rectangle = (
                self.x, self.y, self.width, self.height, dp(12)
            )
        except Exception:
            pass
        pad_x = dp(14)
        pad_y = dp(10)
        self._label.pos = (self.x + pad_x, self.y + pad_y)
        self._label.size = (
            max(0, self.width - 2 * pad_x),
            max(0, self.height - 2 * pad_y)
        )
        self._label.text_size = self._label.size

    def _update_multiline(self, *a):
        self._ti.multiline = self.multiline
        self._label.valign = 'top' if self.multiline else 'middle'

    def _update_font(self, *a):
        self._label.font_size = self.font_size
        self._ti.font_size = self.font_size

    def _on_ti_text(self, inst, val):
        if self._updating:
            return
        self._updating = True
        self.text = val
        self._updating = False
        self._update_label()

    def _on_self_text(self, inst, val):
        if self._updating:
            self._update_label()
            return
        self._updating = True
        if self._ti.text != val:
            self._ti.text = val
        self._updating = False
        self._update_label()

    def _on_focus(self, inst, focused):
        if focused:
            self._border_color.rgba = (0.13, 0.5, 0.92, 1)
            self._border_line.width = 2.0
        else:
            self._border_color.rgba = (0.85, 0.88, 0.93, 1)
            self._border_line.width = 1.2

    def _update_label(self, *a):
        if self.text:
            self._label.text = fa(self.text)
            self._label.color = (0.15, 0.18, 0.25, 1)
        elif self.hint_text:
            self._label.text = fa(self.hint_text)
            self._label.color = (0.62, 0.66, 0.74, 1)
        else:
            self._label.text = ''


# ============================================================
# KV Layout
# ============================================================
KV = r"""
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp
#:import fa main.fa
#:import Animation kivy.animation.Animation


<Card@BoxLayout>:
    orientation: 'vertical'
    padding: dp(16)
    spacing: dp(10)
    size_hint_y: None
    height: self.minimum_height
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.05
        RoundedRectangle:
            pos: self.x + dp(2), self.y - dp(4)
            size: self.width, self.height
            radius: [dp(20)]
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(20)]
        Color:
            rgba: 0.90, 0.93, 0.97, 1
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(20))
            width: 1


<PrimaryButton@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    font_name: 'Vazirmatn-Medium'
    font_size: sp(19)
    bold: True
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: 0.10, 0.35, 0.72, 0.25
        RoundedRectangle:
            pos: self.x, self.y - dp(3)
            size: self.size
            radius: [dp(16)]
        Color:
            rgba: (0.16, 0.55, 0.95, 1) if self.state == 'normal' else (0.10, 0.40, 0.78, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
        Color:
            rgba: 1, 1, 1, 0.12
        RoundedRectangle:
            pos: self.x + dp(6), self.y + self.height * 0.55
            size: self.width - dp(12), self.height * 0.4
            radius: [dp(12)]


<SecondaryButton@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    font_name: 'Vazirmatn-Medium'
    font_size: sp(16)
    color: 0.13, 0.5, 0.92, 1
    canvas.before:
        Color:
            rgba: (0.95, 0.97, 1, 1) if self.state == 'normal' else (0.86, 0.91, 0.98, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: 0.13, 0.5, 0.92, 0.35
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(14))
            width: 1.3


<SectionLabel@Label>:
    font_name: 'Vazirmatn-Medium'
    font_size: sp(13)
    bold: True
    color: 0.42, 0.48, 0.58, 1
    halign: 'right'
    valign: 'middle'
    text_size: self.size
    size_hint_y: None
    height: dp(26)


<BigDisplay@BoxLayout>:
    orientation: 'vertical'
    padding: dp(18)
    spacing: dp(6)
    size_hint_y: None
    height: dp(120)
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.05
        RoundedRectangle:
            pos: self.x + dp(2), self.y - dp(3)
            size: self.size
            radius: [dp(22)]
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(22)]
        Color:
            rgba: 0.13, 0.5, 0.92, 0.35
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(22))
            width: 1.5


<MainScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.96, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: dp(14)
        spacing: dp(12)

        BoxLayout:
            id: header_box
            size_hint_y: None
            height: dp(96)
            canvas.before:
                Color:
                    rgba: 0.06, 0.30, 0.62, 0.30
                RoundedRectangle:
                    pos: self.x, self.y - dp(4)
                    size: self.size
                    radius: [dp(22)]
                Color:
                    rgba: 0.13, 0.50, 0.92, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(22)]
                Color:
                    rgba: 0.20, 0.62, 1.0, 1
                RoundedRectangle:
                    pos: self.x, self.y + self.height * 0.5
                    size: self.width, self.height * 0.5
                    radius: [dp(22), dp(22), 0, 0]
                Color:
                    rgba: 1, 1, 1, 0.10
                Ellipse:
                    pos: self.x + self.width - dp(110), self.y + dp(10)
                    size: dp(140), dp(140)
                Color:
                    rgba: 1, 1, 1, 0.08
                Ellipse:
                    pos: self.x + self.width - dp(60), self.y - dp(40)
                    size: dp(100), dp(100)
            BoxLayout:
                padding: [dp(20), dp(14), dp(20), dp(14)]
                BoxLayout:
                    orientation: 'vertical'
                    Label:
                        text: fa('سیستم نوبت‌دهی')
                        font_name: 'Vazirmatn-Medium'
                        font_size: sp(24)
                        bold: True
                        color: 1, 1, 1, 1
                        halign: 'right'
                        valign: 'middle'
                        text_size: self.size
                    Label:
                        text: fa('برای چاپ نوبت، شماره را وارد کنید')
                        font_name: 'Vazirmatn-Medium'
                        font_size: sp(12)
                        color: 1, 1, 1, 0.85
                        halign: 'right'
                        valign: 'middle'
                        text_size: self.size
                Label:
                    text: '🎫'
                    font_size: sp(40)
                    size_hint_x: None
                    width: dp(60)
                    halign: 'center'
                    valign: 'middle'

        BigDisplay:
            id: prev_display
            Label:
                text: fa('آخرین نوبت چاپ‌شده')
                font_name: 'Vazirmatn-Medium'
                font_size: sp(14)
                color: 0.5, 0.55, 0.65, 1
                halign: 'center'
                size_hint_y: None
                height: dp(22)
            Label:
                id: prev_label
                text: root.previous_display
                font_name: 'NumFont'
                font_size: sp(52)
                bold: True
                color: 0.13, 0.5, 0.92, 1
                halign: 'center'
                valign: 'middle'
                text_size: self.size

        BigDisplay:
            id: input_display_box
            height: dp(150)
            Label:
                text: fa('شماره نوبت جدید')
                font_name: 'Vazirmatn-Medium'
                font_size: sp(14)
                color: 0.5, 0.55, 0.65, 1
                halign: 'center'
                size_hint_y: None
                height: dp(22)
            TextInput:
                id: number_input
                text: root.input_display
                font_name: 'NumFont'
                font_size: sp(38)
                bold: True
                halign: 'center'
                multiline: False
                input_filter: 'int'
                input_type: 'number'
                keyboard_suggestions: False
                background_normal: ''
                background_active: ''
                background_color: 0, 0, 0, 0
                foreground_color: 0.1, 0.15, 0.25, 1
                cursor_color: 0.13, 0.5, 0.92, 1
                padding: [0, dp(15), 0, dp(15)]
                on_text: root.on_input_change(self.text)
                on_focus: root.on_input_focus(self.focus)

        PrimaryButton:
            id: print_btn
            text: fa('چاپ نوبت')
            size_hint_y: None
            height: dp(70)
            on_release: root.on_print_clicked()

        SecondaryButton:
            id: settings_btn
            text: fa('⚙️  تنظیمات')
            size_hint_y: None
            height: dp(55)
            on_release: root.go_settings()

        Widget:


<SettingsScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.96, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: dp(14)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(70)
            canvas.before:
                Color:
                    rgba: 0.06, 0.30, 0.62, 0.30
                RoundedRectangle:
                    pos: self.x, self.y - dp(3)
                    size: self.size
                    radius: [dp(20)]
                Color:
                    rgba: 0.13, 0.50, 0.92, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(20)]
                Color:
                    rgba: 1, 1, 1, 0.10
                Ellipse:
                    pos: self.x + self.width - dp(80), self.y + dp(5)
                    size: dp(90), dp(90)
            BoxLayout:
                padding: [dp(12), dp(8), dp(12), dp(8)]
                Button:
                    text: '←'
                    font_size: sp(26)
                    size_hint_x: None
                    width: dp(50)
                    background_normal: ''
                    background_color: 0, 0, 0, 0
                    color: 1, 1, 1, 1
                    on_release: root.go_back()
                Label:
                    text: fa('تنظیمات')
                    font_name: 'Vazirmatn-Medium'
                    font_size: sp(21)
                    bold: True
                    color: 1, 1, 1, 1
                    halign: 'center'
                    valign: 'middle'
                    text_size: self.size

        ScrollView:
            id: settings_scroll
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
                padding: [0, dp(5), 0, dp(20)]

                SectionLabel:
                    text: fa('🖨️  چاپ و نوبت')

                Card:
                    size_hint_y: None
                    height: dp(54)
                    padding: 0
                    SwitchRow:
                        row_label: 'ریست خودکار روزانه'
                        row_active: root.daily_reset
                        row_callback: root.set_daily_reset

                Card:
                    size_hint_y: None
                    height: dp(54)
                    padding: 0
                    SwitchRow:
                        row_label: 'تایید قبل از چاپ'
                        row_active: root.confirm_before_print
                        row_callback: root.set_confirm

                Card:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: dp(90)
                        spacing: dp(5)
                        BoxLayout:
                            size_hint_y: None
                            height: dp(40)
                            Label:
                                text: fa('تعداد پرینت هر نوبت')
                                font_name: 'Vazirmatn-Medium'
                                font_size: sp(15)
                                color: 0.13, 0.18, 0.28, 1
                                halign: 'right'
                                valign: 'middle'
                                text_size: self.size
                            Label:
                                text: root.copies_display
                                font_name: 'NumFont'
                                font_size: sp(22)
                                bold: True
                                color: 0.13, 0.5, 0.92, 1
                                size_hint_x: None
                                width: dp(50)
                                halign: 'center'
                                valign: 'middle'
                        Slider:
                            min: 1
                            max: 5
                            step: 1
                            value: root.print_copies
                            on_value: root.set_copies(int(self.value))

                SectionLabel:
                    text: fa('🎨  ظاهر رسید')

                Card:
                    size_hint_y: None
                    height: dp(54)
                    padding: 0
                    SwitchRow:
                        row_label: 'نمایش لوگو در رسید'
                        row_active: root.show_logo
                        row_callback: root.set_logo_toggle

                SecondaryButton:
                    text: fa('🖼️   انتخاب لوگو از گالری')
                    size_hint_y: None
                    height: dp(55)
                    on_release: root.pick_logo()

                Card:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: dp(120)
                        spacing: dp(6)
                        Label:
                            text: fa('متن هدر رسید')
                            font_name: 'Vazirmatn-Medium'
                            font_size: sp(13)
                            color: 0.42, 0.48, 0.58, 1
                            halign: 'right'
                            size_hint_y: None
                            height: dp(22)
                        FaTextInput:
                            id: inp_header
                            text: root.header_text_raw
                            hint_text: 'متن هدر...'
                            on_text: root.on_header(self.text)

                Card:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: dp(120)
                        spacing: dp(6)
                        Label:
                            text: fa('متن فوتر رسید')
                            font_name: 'Vazirmatn-Medium'
                            font_size: sp(13)
                            color: 0.42, 0.48, 0.58, 1
                            halign: 'right'
                            size_hint_y: None
                            height: dp(22)
                        FaTextInput:
                            id: inp_footer
                            text: root.footer_text_raw
                            hint_text: 'متن فوتر...'
                            on_text: root.on_footer(self.text)

                SectionLabel:
                    text: fa('📋  منوی سفارش')

                Card:
                    size_hint_y: None
                    height: dp(54)
                    padding: 0
                    SwitchRow:
                        row_label: 'فعال‌سازی منوی سفارش'
                        row_active: root.menu_enabled
                        row_callback: root.set_menu_enabled

                Card:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: dp(240)
                        spacing: dp(6)
                        Label:
                            text: fa('آیتم‌های منو (هر خط یک آیتم)')
                            font_name: 'Vazirmatn-Medium'
                            font_size: sp(13)
                            color: 0.42, 0.48, 0.58, 1
                            halign: 'right'
                            size_hint_y: None
                            height: dp(22)
                        FaTextInput:
                            id: inp_menu
                            text: root.menu_items_raw
                            hint_text: 'چای\nقهوه\n...'
                            multiline: True
                            on_text: root.on_menu_items(self.text)

                Card:
                    size_hint_y: None
                    height: dp(54)
                    padding: 0
                    SwitchRow:
                        row_label: 'چاپ سفارش همراه نوبت'
                        row_active: root.print_order_with_number
                        row_callback: root.set_print_order

                SectionLabel:
                    text: fa('🔌  وضعیت پرینتر')

                Card:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: dp(70)
                        spacing: dp(4)
                        Label:
                            text: fa('اتصال پرینتر')
                            font_name: 'Vazirmatn-Medium'
                            font_size: sp(12)
                            color: 0.42, 0.48, 0.58, 1
                            halign: 'right'
                            size_hint_y: None
                            height: dp(20)
                        Label:
                            text: fa(root.printer_status)
                            font_name: 'Vazirmatn-Medium'
                            font_size: sp(14)
                            color: 0.13, 0.18, 0.28, 1
                            halign: 'right'
                            valign: 'middle'
                            size_hint_y: None
                            height: dp(35)
                            text_size: self.width, None

                Button:
                    text: fa('🔄  ریست دستی شماره نوبت')
                    font_name: 'Vazirmatn-Medium'
                    font_size: sp(16)
                    size_hint_y: None
                    height: dp(58)
                    background_normal: ''
                    background_color: 0, 0, 0, 0
                    color: 1, 1, 1, 1
                    canvas.before:
                        Color:
                            rgba: 0.90, 0.25, 0.30, 0.25
                        RoundedRectangle:
                            pos: self.x, self.y - dp(3)
                            size: self.size
                            radius: [dp(14)]
                        Color:
                            rgba: (0.93, 0.30, 0.35, 1) if self.state == 'normal' else (0.80, 0.22, 0.28, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(14)]
                    on_release: root.confirm_reset()

                Widget:
                    size_hint_y: None
                    height: dp(20)
"""


# ============================================================
# Screens
# ============================================================
class MainScreen(Screen):
    previous_display = StringProperty('۰۰۰')
    input_display = StringProperty('')
    current_input = NumericProperty(0)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh(), 0.05)
        Clock.schedule_once(lambda dt: self.animate_in(), 0.1)

    def animate_in(self):
        try:
            widgets = ['header_box', 'prev_display', 'input_display_box',
                       'print_btn', 'settings_btn']
            for i, wid_id in enumerate(widgets):
                w = self.ids.get(wid_id)
                if w:
                    w.opacity = 0
                    anim = Animation(opacity=1, duration=0.35, t='out_quad')
                    Clock.schedule_once(
                        lambda dt, ww=w, aa=anim: aa.start(ww),
                        i * 0.05
                    )
        except Exception as e:
            print(f"anim err: {e}")

    def refresh(self):
        app = App.get_running_app()
        last = app.queue.get_last_printed()
        self.previous_display = to_fa(f"{last:03d}")
        try:
            if not self.ids.number_input.text:
                nxt = app.queue.get_next_suggested()
                self.ids.number_input.text = str(nxt)
        except Exception:
            pass

    def on_input_change(self, text):
        clean = ''.join(c for c in text if c.isdigit())
        if clean != text:
            self.ids.number_input.text = clean
            return
        self.current_input = int(clean) if clean else 0
        self.input_display = clean

    def on_input_focus(self, focused):
        if focused:
            try:
                w = self.ids.input_display_box
                orig_h = w.height
                Animation.cancel_all(w, 'height')
                Animation(height=orig_h + dp(4), duration=0.1).start(w)
                Clock.schedule_once(
                    lambda dt: Animation(height=orig_h, duration=0.15).start(w),
                    0.15
                )
            except Exception:
                pass

    def on_print_clicked(self):
        try:
            w = self.ids.print_btn
            Animation.cancel_all(w, 'opacity')
            Animation(opacity=0.7, duration=0.08).start(w)
            Clock.schedule_once(
                lambda dt: Animation(opacity=1, duration=0.15).start(w),
                0.1
            )
        except Exception:
            pass

        app = App.get_running_app()
        try:
            text = self.ids.number_input.text.strip()
        except Exception:
            return
        if not text:
            app.toast('لطفاً شماره نوبت را وارد کنید')
            return
        number = int(text)

        if (app.settings.get('menu_enabled') and
                app.settings.get('print_order_with_number')):
            self.show_menu_picker(number)
            return

        if app.settings.get('confirm_before_print'):
            self.show_confirm(number, [])
        else:
            self.do_print(number, [])

    def show_menu_picker(self, number):
        app = App.get_running_app()
        menu_text = app.settings.get('menu_items_text', '')
        items = [x.strip() for x in menu_text.split('\n') if x.strip()]

        if not items:
            if app.settings.get('confirm_before_print'):
                self.show_confirm(number, [])
            else:
                self.do_print(number, [])
            return

        content = BoxLayout(orientation='vertical',
                            padding=dp(12), spacing=dp(8))

        content.add_widget(Label(
            text=fa(f'شماره نوبت: {to_fa(f"{number:03d}")}'),
            font_name='Vazirmatn-Medium', font_size=sp(18), bold=True,
            color=(0.13, 0.5, 0.92, 1),
            size_hint_y=None, height=dp(35)
        ))
        content.add_widget(Label(
            text=fa('می‌توانید چند مورد انتخاب کنید:'),
            font_name='Vazirmatn-Medium', font_size=sp(14),
            color=(0.3, 0.35, 0.45, 1),
            size_hint_y=None, height=dp(25)
        ))

        sv = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None,
                        spacing=dp(6), padding=[0, dp(5)])
        box.bind(minimum_height=box.setter('height'))

        selected = set()

        def make_item(item_text):
            container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None, height=dp(50),
                spacing=dp(8)
            )
            chk = Button(
                text='☐',
                font_size=sp(24),
                size_hint_x=None, width=dp(50),
                background_normal='',
                background_color=(0, 0, 0, 0),
                color=(0.13, 0.5, 0.92, 1)
            )
            lbl = Button(
                text=fa(item_text),
                font_name='Vazirmatn-Medium',
                font_size=sp(16),
                background_normal='',
                background_color=(0.95, 0.96, 0.98, 1),
                color=(0.15, 0.18, 0.25, 1),
                halign='right'
            )
            container.add_widget(lbl)
            container.add_widget(chk)

            state = {'on': False}

            def toggle(*_):
                state['on'] = not state['on']
                if state['on']:
                    chk.text = '☑'
                    chk.color = (0.2, 0.7, 0.3, 1)
                    lbl.background_color = (0.9, 0.95, 1, 1)
                    selected.add(item_text)
                else:
                    chk.text = '☐'
                    chk.color = (0.13, 0.5, 0.92, 1)
                    lbl.background_color = (0.95, 0.96, 0.98, 1)
                    selected.discard(item_text)

            lbl.bind(on_release=toggle)
            chk.bind(on_release=toggle)
            return container

        for it in items:
            box.add_widget(make_item(it))
        sv.add_widget(box)
        content.add_widget(sv)

        btns = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        b_ok = Button(text=fa('ادامه'), font_name='Vazirmatn-Medium',
                      font_size=sp(17),
                      background_normal='',
                      background_color=(0.13, 0.5, 0.92, 1))
        b_skip = Button(text=fa('بدون سفارش'), font_name='Vazirmatn-Medium',
                        font_size=sp(17),
                        background_normal='',
                        background_color=(0.6, 0.6, 0.7, 1))
        btns.add_widget(b_ok)
        btns.add_widget(b_skip)
        content.add_widget(btns)

        popup = Popup(title=fa('انتخاب سفارش'),
                      title_font='Vazirmatn-Medium', title_size=sp(16),
                      content=content,
                      size_hint=(0.92, 0.88), auto_dismiss=False,
                      separator_color=(0.13, 0.5, 0.92, 1))

        def ok(*_):
            popup.dismiss()
            items_sel = list(selected)
            if app.settings.get('confirm_before_print'):
                self.show_confirm(number, items_sel)
            else:
                self.do_print(number, items_sel)

        def skip(*_):
            popup.dismiss()
            if app.settings.get('confirm_before_print'):
                self.show_confirm(number, [])
            else:
                self.do_print(number, [])

        b_ok.bind(on_release=ok)
        b_skip.bind(on_release=skip)
        popup.open()

    def show_confirm(self, number, order_items):
        content = BoxLayout(orientation='vertical',
                            padding=dp(15), spacing=dp(10))
        content.add_widget(Label(
            text=fa(f'آیا شماره {to_fa(f"{number:03d}")} چاپ شود؟'),
            font_name='Vazirmatn-Medium', font_size=sp(18),
            color=(0.1, 0.15, 0.25, 1),
            halign='center', valign='middle'
        ))
        if order_items:
            content.add_widget(Label(
                text=fa(f'سفارش‌ها: {", ".join(order_items)}'),
                font_name='Vazirmatn-Medium', font_size=sp(13),
                color=(0.3, 0.35, 0.45, 1),
                halign='center'
            ))
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        b_yes = Button(text=fa('بله'), font_name='Vazirmatn-Medium',
                       background_normal='',
                       background_color=(0.13, 0.5, 0.92, 1))
        b_no = Button(text=fa('انصراف'), font_name='Vazirmatn-Medium',
                      background_normal='',
                      background_color=(0.7, 0.7, 0.75, 1))
        btns.add_widget(b_yes)
        btns.add_widget(b_no)
        content.add_widget(btns)

        popup = Popup(title=fa('تایید چاپ'), title_font='Vazirmatn-Medium',
                      title_size=sp(16), content=content,
                      size_hint=(0.85, 0.42), auto_dismiss=False,
                      separator_color=(0.13, 0.5, 0.92, 1))

        def yes(*_):
            popup.dismiss()
            self.do_print(number, order_items)

        b_yes.bind(on_release=yes)
        b_no.bind(on_release=popup.dismiss)
        popup.open()

    def do_print(self, number, order_items):
        app = App.get_running_app()
        copies = app.settings.get('print_copies', 1)
        show_logo = app.settings.get('show_logo', False)
        logo = app.settings.get('logo_path', '') if show_logo else None

        try:
            w = self.ids.print_btn
            Animation.cancel_all(w, 'opacity')
            seq = (Animation(opacity=0.4, duration=0.1) +
                   Animation(opacity=1, duration=0.1) +
                   Animation(opacity=0.4, duration=0.1) +
                   Animation(opacity=1, duration=0.15))
            seq.start(w)
        except Exception:
            pass

        app.printer.print_receipt(
            number=number, copies=copies, logo_path=logo,
            header=app.settings.get('header_text', ''),
            footer=app.settings.get('footer_text', ''),
            order_items=order_items if order_items else None
        )

        app.queue.set_printed(number)
        app.toast(f'✅ نوبت {to_fa(f"{number:03d}")} چاپ شد')

        try:
            self.ids.number_input.text = str(number + 1)
        except Exception:
            pass
        self.refresh()

    def go_settings(self):
        try:
            w = self.ids.settings_btn
            Animation.cancel_all(w, 'opacity')
            Animation(opacity=0.6, duration=0.1).start(w)
            Clock.schedule_once(
                lambda dt: Animation(opacity=1, duration=0.15).start(w), 0.12
            )
        except Exception:
            pass
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'settings'


class SettingsScreen(Screen):
    daily_reset = BooleanProperty(True)
    confirm_before_print = BooleanProperty(True)
    print_copies = NumericProperty(1)
    copies_display = StringProperty('۱')
    show_logo = BooleanProperty(False)
    header_text_raw = StringProperty('')
    footer_text_raw = StringProperty('')
    menu_enabled = BooleanProperty(False)
    menu_items_raw = StringProperty('')
    print_order_with_number = BooleanProperty(True)
    printer_status = StringProperty('در حال بررسی...')

    def on_enter(self):
        app = App.get_running_app()
        self.daily_reset = app.settings.get('daily_reset', True)
        self.confirm_before_print = app.settings.get(
            'confirm_before_print', True)
        self.print_copies = app.settings.get('print_copies', 1)
        self.copies_display = to_fa(str(self.print_copies))
        self.show_logo = app.settings.get('show_logo', False)
        self.header_text_raw = app.settings.get('header_text', '')
        self.footer_text_raw = app.settings.get('footer_text', '')
        self.menu_enabled = app.settings.get('menu_enabled', False)
        self.menu_items_raw = app.settings.get('menu_items_text', '')
        self.print_order_with_number = app.settings.get(
            'print_order_with_number', True)

        if app.printer.connected:
            self.printer_status = f"✅ متصل ({app.printer.method})"
        else:
            self.printer_status = f"⚠️ شبیه‌ساز ({app.printer.method})"

        Clock.schedule_once(lambda dt: self.animate_in(), 0.1)

    def animate_in(self):
        try:
            sv = self.ids.settings_scroll
            sv.opacity = 0
            Animation(opacity=1, duration=0.35).start(sv)
        except Exception:
            pass

    def set_daily_reset(self, *args):
        val = args[-1] if args else False
        self.daily_reset = bool(val)
        App.get_running_app().settings.set('daily_reset', bool(val))

    def set_confirm(self, *args):
        val = args[-1] if args else False
        self.confirm_before_print = bool(val)
        App.get_running_app().settings.set('confirm_before_print', bool(val))

    def set_copies(self, *args):
        val = args[-1] if args else 1
        self.print_copies = int(val)
        self.copies_display = to_fa(str(int(val)))
        App.get_running_app().settings.set('print_copies', int(val))

    def set_logo_toggle(self, *args):
        val = args[-1] if args else False
        self.show_logo = bool(val)
        App.get_running_app().settings.set('show_logo', bool(val))

    def set_menu_enabled(self, *args):
        val = args[-1] if args else False
        self.menu_enabled = bool(val)
        App.get_running_app().settings.set('menu_enabled', bool(val))

    def set_print_order(self, *args):
        val = args[-1] if args else False
        self.print_order_with_number = bool(val)
        App.get_running_app().settings.set(
            'print_order_with_number', bool(val))

    def on_header(self, txt):
        App.get_running_app().settings.set('header_text', txt)

    def on_footer(self, txt):
        App.get_running_app().settings.set('footer_text', txt)

    def on_menu_items(self, txt):
        App.get_running_app().settings.set('menu_items_text', txt)

    def pick_logo(self):
        app = App.get_running_app()
        if platform != 'android':
            app.toast('انتخاب لوگو فقط در اندروید')
            return
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.READ_MEDIA_IMAGES
            ])
        except Exception as e:
            print(f"⚠️ خطا مجوز: {e}")
        try:
            from jnius import autoclass, cast
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            intent = Intent(Intent.ACTION_PICK)
            intent.setType("image/*")
            current = cast('android.app.Activity', PythonActivity.mActivity)
            current.startActivityForResult(intent, 1001)
        except Exception as e:
            app.toast(f'خطا: {e}')
            print(f"⚠️ خطا انتخاب لوگو: {e}")

    def confirm_reset(self):
        content = BoxLayout(orientation='vertical',
                            padding=dp(15), spacing=dp(15))
        content.add_widget(Label(
            text=fa('شماره نوبت به ۰ برگردد؟'),
            font_name='Vazirmatn-Medium', font_size=sp(17),
            color=(0.1, 0.15, 0.25, 1),
            halign='center'
        ))
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        b_yes = Button(text=fa('بله'), font_name='Vazirmatn-Medium',
                       background_normal='',
                       background_color=(0.95, 0.35, 0.35, 1))
        b_no = Button(text=fa('انصراف'), font_name='Vazirmatn-Medium',
                      background_normal='',
                      background_color=(0.7, 0.7, 0.75, 1))
        btns.add_widget(b_yes)
        btns.add_widget(b_no)
        content.add_widget(btns)

        popup = Popup(title=fa('تایید ریست'), title_font='Vazirmatn-Medium',
                      title_size=sp(16), content=content,
                      size_hint=(0.85, 0.35), auto_dismiss=False,
                      separator_color=(0.95, 0.35, 0.35, 1))

        def yes(*_):
            App.get_running_app().queue.reset_today()
            popup.dismiss()
            App.get_running_app().toast('✅ ریست شد')

        b_yes.bind(on_release=yes)
        b_no.bind(on_release=popup.dismiss)
        popup.open()

    def go_back(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'main'


# ============================================================
# App
# ============================================================
class NobatApp(App):
    def build(self):
        self.title = 'سیستم نوبت‌دهی'
        self.settings = SettingsManager()
        self.queue = QueueManager(self.settings)
        self.printer = POSPrinter()

        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def on_activity_result(self, request_code, result_code, intent):
        if request_code != 1001:
            return
        try:
            from jnius import autoclass
            Activity = autoclass('android.app.Activity')
            if result_code != Activity.RESULT_OK:
                return
            uri = intent.getData()
            dest = APP_DIR / 'user_logo.png'
            self._copy_uri_to_file(uri, str(dest))
            self.settings.set('logo_path', str(dest))
            self.settings.set('show_logo', True)
            self.toast('✅ لوگو ذخیره شد')
            print(f"✅ لوگو در {dest} ذخیره شد")
        except Exception as e:
            print(f"⚠️ خطا در لوگو: {e}")

    def _copy_uri_to_file(self, uri, dest):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            FileOutputStream = autoclass('java.io.FileOutputStream')
            resolver = PythonActivity.mActivity.getContentResolver()
            input_stream = resolver.openInputStream(uri)
            output_stream = FileOutputStream(dest)
            buffer = bytearray(4096)
            while True:
                n = input_stream.read(buffer)
                if n == -1:
                    break
                output_stream.write(buffer, 0, n)
            input_stream.close()
            output_stream.close()
        except Exception as e:
            print(f"⚠️ خطا در کپی لوگو: {e}")

    def toast(self, msg):
        print(f'📢 {msg}')
        if platform != 'android':
            return
        try:
            from android.runnable import run_on_ui_thread
            from jnius import autoclass, cast
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Toast = autoclass('android.widget.Toast')
            String = autoclass('java.lang.String')

            @run_on_ui_thread
            def show():
                Toast.makeText(
                    PythonActivity.mActivity,
                    cast('java.lang.CharSequence', String(msg)),
                    Toast.LENGTH_SHORT
                ).show()

            show()
        except Exception as e:
            print(f'⚠️ Toast error: {e}')


if __name__ == '__main__':
    NobatApp().run()