"""
Studio v8.0 Ultra-Blogger VFX, Behind-Person AI Rotoscope & 17-Logo Edition — DentEye • Aidite Rapid 5
======================================================================================================
Upgrades over v7.0:
1. Real AI Human Rotoscoping (u2net_human_seg.onnx) on Talking-Head frames (0..32.13s):
   Giant 3D glowing titles ('DENTEYE', 'GRADE A+', 'AIDITE', '100% QC'), rotating HUD radar rings,
   volumetric diagonal god-rays, and floating particles appear BEHIND Milad's head & shoulders
   with optical edge light-wrap ("افکت‌های پشت صحنه").
2. 17 Custom Vector Logos & Official Brand Marks ('Aidite', 'Instagram', 'DentEye', 'Verified',
   'USB', 'Scanner Wand', 'Stand', '4 Tips', 'Autoclave Steam', 'Feather 162g', '25mm Laser',
   'No Calibration', 'Stopwatch', 'Micron Reticle', 'Soft-Tissue AI') synced to every topic!
3. Powerful Spring-Scale Animations, Travelling Saber Laser Borders, Glass Specular Sheen Sweeps,
   Live Rolling Number Counters (0->100, 0->162, 0->25, 0->60, 0->10), and Live Instagram Typing CTA!
4. Ultra-Legible Lalezar Display + Vazirmatn-Black (900) Stroked Typography (zero small thin text!).
"""
import os, sys, re, math, json, wave, subprocess
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.signal import butter, filtfilt
import cairocffi as cairo
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.engine.render_core import (
    W, H, fa, clamp, ease_out_cubic, ease_in_out_cubic, spring_pop, window_fade
)
from src.engine.blogger_vfx_logos import (
    BloggerFontPack, get_stroked_text_sprite, precompute_talking_head_mattes,
    composite_talking_head_with_depth_vfx, draw_broll_ambient_vfx, draw_topic_logo,
    _cairo_surface_to_pil_rgba
)

FPS_EDIT = 30
RAW_W, RAW_H = 804, 1428

RAW_PRIMARY_URL = "https://github.com/melimcrr-crypto/zavieh-zehn/releases/download/client-raw-denteye/raw_client_denteye.mp4"
RAW_FALLBACK_URL = "https://tempfile.org/JGCj2Vqc8kq/download"

# Exact frame-verified cut timestamps (30.00 fps)
F_TH_CUT     = 383   # 12.767s: Talking Head 1 -> Talking Head 2
F_UNBOX_1    = 964   # 32.133s: Talking Head 2 -> Open Case B-Roll
F_UNBOX_2    = 1097  # 36.567s: Stand Box
F_UNBOX_3    = 1224  # 40.800s: Scanner on Stand
F_UNBOX_4    = 1267  # 42.233s: USB Flash Drive
F_UNBOX_5    = 1350  # 45.000s: 4 Scan Tips in Hand
F_MACRO_HEAD = 1622  # 54.067s: Macro Scanner Optical Tip (100x Autoclave)
F_BODY_162G  = 1738  # 57.933s: Sleek Handheld Body (162g)
F_SPEC_TBL   = 1911  # 63.700s: White Spec Table Screenshot
F_SPEC_25MM  = 1980  # 66.000s: White 25mm DoF Brochure Page
F_CASE_CAL   = 2069  # 68.967s: Scanner in Case (Calibration-Free)
F_SW_ORDER   = 2234  # 74.467s: Sideways 90° Software Order Screen (Aidite | DENTEYE A)
F_SPEC_10UM  = 2648  # 88.267s: White 10µm Precision Brochure Page
F_SW_SCAN3D  = 2828  # 94.267s: Sideways 90° Real-Time 3D Intraoral Arch Scan -> End (3673)

CYAN_RGB  = (42, 222, 255)
GREEN_RGB = (72, 252, 152)
AMBER_RGB = (255, 210, 58)
DARK_TXT  = (6, 12, 24, 255)

POWER_KEYWORDS = {
    "دنت‌آی", "کرامتی‌پور", "میلاد", "آیدایت", "رپید", "فایو",
    "استوک", "فیلترهای", "سلامت", "کیفیت", "استند", "فلش", "چهار",
    "اتوکلاو", "۱۰۰", "سبک", "۱۶۲", "۲۵", "کالیبراسیون",
    "سرعت", "۶۰", "دقت", "۱۰", "۲۰", "میکرون", "بافت‌های", "کامنت", "قیمت"
}


def _build_verified_blogger_phrases() -> list:
    """55 human-proofread Persian blogger caption pills locked 1-to-1 to acoustic word timestamps."""
    spec = [
        (0.00, 1.62,  [("درود", 0.00, 0.32), ("بر", 0.32, 0.48), ("شما", 0.48, 0.76), ("همراهان", 0.76, 1.20), ("عزیز،", 1.20, 1.62)]),
        (1.62, 3.58,  [("بنده", 1.62, 1.84), ("میلاد", 1.84, 2.22), ("کرامتی‌پور", 2.22, 2.96), ("هستم", 2.96, 3.58)]),
        (3.58, 5.10,  [("و", 3.58, 3.78), ("اینجا", 3.78, 4.08), ("دنت‌آی", 4.08, 4.62), ("هست.", 4.62, 5.06)]),
        (5.16, 6.74,  [("قراره", 5.16, 5.64), ("توی", 5.64, 5.84), ("این", 5.84, 6.08), ("پیج،", 6.08, 6.74)]),
        (6.74, 8.80,  [("تجهیزات", 6.74, 7.36), ("دندانپزشکی", 7.36, 8.24), ("استوک", 8.24, 8.78)]),
        (8.80, 10.30, [("و", 8.80, 8.90), ("در", 8.90, 9.08), ("حد", 9.08, 9.26), ("نو", 9.26, 9.50), ("رو", 9.50, 9.74), ("خدمتتون", 9.74, 10.30)]),
        (10.30, 11.56,[("معرفی", 10.30, 10.84), ("و", 10.84, 10.94), ("بررسی", 10.94, 11.36), ("کنیم.", 11.36, 11.56)]),
        (11.60, 12.90,[("ممنون", 11.60, 11.86), ("می‌شم", 11.86, 12.12), ("با", 12.12, 12.24), ("ما", 12.24, 12.36), ("همراه", 12.36, 12.60), ("باشید.", 12.60, 12.90)]),
        (12.96, 14.96,[("موجودی", 12.96, 13.34), ("حال", 13.34, 13.60), ("حاضر", 13.60, 13.98), ("دنت‌آی،", 13.98, 14.96)]),
        (14.96, 17.22,[("یک", 14.96, 15.12), ("دستگاه", 15.12, 15.60), ("اورال", 15.60, 16.00), ("اسکنر", 16.00, 16.42), ("آیدایت", 16.42, 17.22)]),
        (17.22, 18.48,[("مدل", 17.22, 17.48), ("رپید", 17.48, 17.84), ("فایو", 17.84, 18.14), ("هستش.", 18.14, 18.48)]),
        (18.48, 20.48,[("البته", 18.48, 18.84), ("این", 18.84, 18.98), ("نکته", 18.98, 19.24), ("رو", 19.24, 19.34), ("خدمتتون", 19.34, 19.74), ("عرض", 19.74, 20.08), ("بکنم", 20.08, 20.48)]),
        (20.48, 22.90,[("که", 20.48, 20.60), ("ما", 20.60, 20.74), ("هر", 20.74, 20.96), ("دستگاهی", 20.96, 21.40), ("داخل", 21.40, 21.72), ("دنت‌آی", 21.72, 22.12), ("موجود", 22.12, 22.44), ("نمی‌کنیم!", 22.44, 22.90)]),
        (22.98, 24.46,[("دستگاه‌هایی", 22.98, 23.40), ("که", 23.40, 23.52), ("ما", 23.52, 23.66), ("موجود", 23.66, 23.94), ("می‌کنیم،", 23.94, 24.46)]),
        (24.46, 27.56,[("از", 24.46, 24.62), ("فیلترهای", 24.62, 25.20), ("کارشناسان", 25.20, 25.78), ("فنی‌مون", 25.78, 26.28), ("گذر", 26.28, 26.70), ("می‌کنه", 26.70, 27.56)]),
        (27.56, 29.80,[("و", 27.56, 27.70), ("از", 27.70, 27.82), ("بالاترین", 27.82, 28.28), ("سلامت", 28.28, 28.72), ("و", 28.72, 28.84), ("کیفیت", 28.84, 29.24), ("برخورداره.", 29.24, 29.80)]),
        (29.84, 32.18,[("حالا", 29.84, 30.06), ("بریم", 30.06, 30.34), ("سراغ", 30.34, 30.72), ("تست", 30.72, 30.94), ("و", 30.94, 31.10), ("بررسی", 31.10, 31.64), ("اسکنرمون!", 31.64, 32.18)]),
        (32.24, 34.76,[("اول", 32.24, 32.52), ("از", 32.52, 32.76), ("همه", 32.76, 33.24), ("نگاهی", 33.24, 33.88), ("به", 33.88, 34.04), ("خود", 34.04, 34.26), ("دستگاه", 34.26, 34.76)]),
        (34.76, 36.60,[("و", 34.76, 34.98), ("اقلام", 34.98, 35.42), ("همراهش", 35.42, 35.94), ("بندازیم.", 35.94, 36.60)]),
        (36.60, 39.04,[("این", 36.60, 36.88), ("دستگاه", 36.88, 37.54), ("شامل", 37.54, 38.02), ("استند", 38.02, 39.04)]),
        (39.04, 41.00,[("که", 39.04, 39.32), ("اسکنر", 39.32, 39.80), ("روش", 39.80, 40.06), ("قرار", 40.06, 40.38), ("می‌گیره،", 40.38, 41.00)]),
        (41.00, 42.46,[("خود", 41.00, 41.32), ("اسکنر،", 41.32, 42.46)]),
        (42.46, 45.18,[("یک", 42.46, 42.62), ("فلش", 42.62, 43.00), ("حاوی", 43.00, 43.42), ("نرم‌افزار", 43.42, 44.16), ("برای", 44.16, 44.54), ("نصب،", 44.54, 45.18)]),
        (45.18, 47.16,[("و", 45.18, 45.30), ("چهار", 45.30, 45.72), ("عدد", 45.72, 46.06), ("تیپ", 46.06, 46.36), ("اسکنره.", 46.36, 47.16)]),
        (47.22, 48.74,[("سه", 47.22, 47.42), ("تیپش", 47.42, 47.80), ("استاندارده،", 47.80, 48.74)]),
        (48.74, 50.26,[("یک", 48.74, 48.96), ("تیپش", 48.96, 49.32), ("هم", 49.32, 49.48), ("مینیه،", 49.48, 50.26)]),
        (50.26, 52.18,[("که", 50.26, 50.42), ("متناسب", 50.42, 50.94), ("با", 50.94, 51.14), ("شرایط", 51.14, 51.56), ("مختلف", 51.56, 52.18)]),
        (52.18, 54.10,[("می‌تونید", 52.18, 52.68), ("ازشون", 52.68, 53.20), ("استفاده", 53.20, 53.84), ("کنید.", 53.84, 54.10)]),
        (54.16, 56.66,[("تیپ‌های", 54.16, 54.62), ("اسکنر", 54.62, 55.20), ("قابلیت", 55.20, 55.98), ("اتوکلاو", 55.98, 56.66)]),
        (56.66, 58.05,[("دارن", 56.66, 57.02), ("تا", 57.02, 57.24), ("۱۰۰", 57.24, 57.58), ("بار!", 57.58, 58.05)]),
        (58.16, 60.84,[("از", 58.16, 58.34), ("نظر", 58.34, 58.70), ("طراحی", 58.70, 59.35), ("هم،", 59.35, 59.76), ("رپید", 59.76, 60.30), ("فایو", 60.30, 60.84)]),
        (60.84, 63.86,[("یکی", 60.84, 61.32), ("از", 61.32, 61.46), ("اسکنرهای", 61.46, 62.24), ("سبک", 62.24, 62.90), ("بازاره،", 62.90, 63.86)]),
        (63.86, 66.06,[("که", 63.86, 64.02), ("با", 64.02, 64.20), ("وزن", 64.20, 64.60), ("۱۶۲", 64.60, 65.54), ("گرم", 65.54, 66.06)]),
        (66.06, 69.16,[("و", 66.06, 66.30), ("عمق", 66.30, 66.70), ("اسکن", 66.70, 67.30), ("۲۵", 67.30, 67.68), ("میلی‌متری", 67.68, 68.18), ("طراحی", 68.18, 68.80), ("شده.", 68.80, 69.16)]),
        (69.26, 72.38,[("یکی", 69.26, 69.50), ("دیگه", 69.50, 69.72), ("از", 69.72, 69.88), ("ویژگی‌های", 69.88, 70.48), ("مهم", 70.48, 71.36), ("این", 71.36, 71.58), ("دستگاه،", 71.58, 72.38)]),
        (72.38, 74.56,[("عدم", 72.38, 72.60), ("نیاز", 72.60, 73.02), ("به", 73.02, 73.22), ("کالیبراسیون", 73.22, 73.94), ("دوره‌ایه!", 73.94, 74.56)]),
        (74.56, 76.64,[("حالا", 74.56, 74.80), ("بهتره", 74.80, 75.28), ("عملکرد", 75.28, 76.06), ("دستگاه", 76.06, 76.64)]),
        (76.64, 78.80,[("رو", 76.64, 76.82), ("حین", 76.82, 77.12), ("اسکن", 77.12, 77.72), ("واقعی", 77.72, 78.12), ("هم", 78.12, 78.26), ("ببینیم.", 78.26, 78.80)]),
        (78.86, 82.46,[("از", 78.86, 79.10), ("نظر", 79.10, 79.52), ("سرعت،", 79.52, 80.56), ("اسکن", 80.56, 81.46), ("یک", 81.46, 81.74), ("آرچ", 81.74, 82.46)]),
        (82.46, 84.04,[("حدود", 82.46, 82.70), ("۲۵", 82.70, 83.22), ("ثانیه", 83.22, 84.04)]),
        (84.04, 86.16,[("و", 84.04, 84.36), ("فول‌آرچ", 84.36, 84.96), ("حدود", 84.96, 85.30), ("۶۰", 85.30, 85.64), ("ثانیه", 85.64, 86.00), ("است.", 86.00, 86.16)]),
        (86.24, 88.42,[("طبق", 86.24, 86.56), ("مشخصات", 86.56, 87.34), ("اعلام‌شده،", 87.34, 88.42)]),
        (88.42, 90.76,[("دقت", 88.42, 89.06), ("اسکن", 89.06, 89.50), ("برای", 89.50, 89.92), ("سینگل‌کراون", 89.92, 90.76)]),
        (90.76, 91.82,[("تا", 90.76, 91.00), ("۱۰", 91.00, 91.36), ("میکرون", 91.36, 91.82)]),
        (91.82, 94.34,[("و", 91.82, 92.16), ("فول‌آرچ", 92.16, 92.80), ("تا", 92.80, 93.10), ("۲۰", 93.10, 93.42), ("میکرون", 93.42, 93.78), ("هستش.", 93.78, 94.34)]),
        (94.48, 98.60,[("یکی", 94.48, 94.70), ("دیگه", 94.70, 94.92), ("از", 94.92, 95.10), ("موارد", 95.10, 95.52), ("مهم،", 95.52, 96.02), ("بازیابی", 96.02, 97.68), ("تصویر", 97.68, 98.60)]),
        (98.60, 100.12,[("در", 98.60, 98.86), ("نواحی", 98.86, 99.34), ("مختلف،", 99.34, 100.12)]),
        (100.12, 101.56,[("از", 100.12, 100.28), ("جمله", 100.28, 100.54), ("همین", 100.54, 100.74), ("بافت‌های", 100.74, 101.18), ("نرم؛", 101.18, 101.56)]),
        (101.56, 103.82,[("این", 101.56, 101.76), ("چیزیه", 101.76, 102.18), ("که", 102.18, 102.32), ("خود", 102.32, 102.50), ("کمپانی", 102.50, 103.02), ("اعلام", 103.02, 103.42), ("کرده.", 103.42, 103.82)]),
        (103.88, 108.08,[("در", 103.88, 104.22), ("مجموع", 104.22, 104.78), ("اگر", 104.78, 105.36), ("دنبال", 105.36, 105.88), ("یک", 105.88, 106.18), ("اسکنر", 106.18, 106.86), ("سبک،", 106.86, 108.08)]),
        (108.08, 111.28,[("سریع", 108.08, 108.62), ("و", 108.62, 108.92), ("کاربردی", 108.92, 110.08), ("برای", 110.08, 110.50), ("استفاده‌ی", 110.50, 111.28)]),
        (111.28, 113.76,[("روزمره‌تون", 111.28, 112.22), ("توی", 112.22, 112.48), ("مطب", 112.48, 112.92), ("هستید،", 112.92, 113.76)]),
        (113.76, 116.68,[("گزینه‌ایه", 113.76, 114.22), ("که", 114.22, 114.44), ("ارزش", 114.44, 115.02), ("بررسی", 115.02, 115.66), ("کردن", 115.66, 115.98), ("رو", 115.98, 116.16), ("داره.", 116.16, 116.68)]),
        (116.68, 120.28,[("جهت", 116.68, 117.14), ("استعلام", 117.14, 117.62), ("قیمت", 117.62, 118.32), ("و", 118.32, 118.48), ("دریافت", 118.48, 118.98), ("اطلاعات", 118.98, 119.54), ("بیشتر،", 119.54, 120.28)]),
        (120.28, 122.40,[("کلمه‌ی", 120.28, 120.84), ("«آیدایت»", 120.84, 121.36), ("رو", 121.36, 121.56), ("کامنت", 121.56, 121.90), ("کنید!", 121.90, 122.35)]),
    ]
    phrases = []
    for ps, pe, wlist in spec:
        wdicts = [{"word": w, "start": round(ws, 3), "end": round(we, 3)} for (w, ws, we) in wlist]
        phrases.append({
            "start": round(ps, 3),
            "end": round(pe, 3),
            "words": wdicts,
            "full": " ".join(x["word"] for x in wdicts),
        })
    return phrases


# =============================================================================
# STUDIO AUDIO ENHANCEMENT + ENERGETIC BLOGGER SOUND DESIGN (28 SFX CUES)
# =============================================================================
def _synth_blogger_music_and_sfx(dur_sec: float, voice_env_48k: np.ndarray, sr: int = 48000) -> np.ndarray:
    n = int(dur_sec * sr)
    t = np.arange(n, dtype=np.float64) / sr
    mix_l = np.zeros(n, dtype=np.float64)
    mix_r = np.zeros(n, dtype=np.float64)

    chords = [
        [110.0, 220.0, 261.63, 329.63, 392.00, 493.88],
        [87.31, 174.61, 220.00, 261.63, 329.63, 440.00],
        [130.81, 196.00, 246.94, 293.66, 392.00],
        [98.00, 196.00, 246.94, 293.66, 329.63],
    ]
    bar_len = 4.0
    for b in range(int(math.ceil(dur_sec / bar_len))):
        i0 = int(b * bar_len * sr)
        i1 = min(n, int((b + 1.15) * bar_len * sr))
        if i0 >= n:
            break
        lt = np.arange(i1 - i0, dtype=np.float64) / sr
        env = np.clip(lt / 0.45, 0.0, 1.0) * np.exp(-lt * 0.42)
        notes = chords[b % len(chords)]
        ch_l = np.zeros_like(lt)
        ch_r = np.zeros_like(lt)
        for ni, f in enumerate(notes):
            s1 = np.sin(2 * np.pi * f * lt) + 0.22 * np.sin(2 * np.pi * f * 2.0 * lt) * np.exp(-lt * 1.8)
            pan = 0.35 + 0.30 * ((ni % 3) / 2.0)
            ch_l += s1 * (1.0 - pan * 0.45)
            ch_r += s1 * (0.55 + pan * 0.45)
        mix_l[i0:i1] += ch_l * env * 0.015
        mix_r[i0:i1] += ch_r * env * 0.015

    beat_dt = 60.0 / 114.0
    for bi in range(int(dur_sec / beat_dt)):
        ib = int(bi * beat_dt * sr)
        ln = min(int(0.11 * sr), n - ib)
        if ln <= 64:
            continue
        bt = np.arange(ln, dtype=np.float64) / sr
        if bi % 2 == 0:
            f_sw = 52.0 + 70.0 * np.exp(-bt * 42.0)
            pulse = np.sin(2 * np.pi * np.cumsum(f_sw) / sr) * np.exp(-bt * 26.0) * 0.027
            mix_l[ib:ib + ln] += pulse
            mix_r[ib:ib + ln] += pulse
        else:
            hat = np.random.default_rng(bi + 77).normal(0, 1, ln) * np.exp(-bt * 95.0) * 0.0048
            mix_l[ib:ib + ln] += hat * 0.9
            mix_r[ib:ib + ln] += hat * 1.1

    duck = 1.0 - 0.60 * np.clip(voice_env_48k[:n] * 3.5, 0.0, 1.0)
    fade_out = np.clip((dur_sec - t) / 1.1, 0.0, 1.0)
    mix_l *= duck * fade_out
    mix_r *= duck * fade_out

    def add_pop(ts: float, freq: float = 820.0, gain: float = 0.088):
        i0 = int(ts * sr)
        ln = min(int(0.085 * sr), n - i0)
        if i0 < 0 or ln <= 64:
            return
        pt = np.arange(ln, dtype=np.float64) / sr
        f_c = freq * (0.68 + 0.58 * (1.0 - np.exp(-pt * 55.0)))
        sig = np.sin(2 * np.pi * np.cumsum(f_c) / sr) * np.exp(-pt * 44.0) * gain
        mix_l[i0:i0 + ln] += sig
        mix_r[i0:i0 + ln] += sig * 0.96

    def add_whoosh(ts: float, dur_w: float = 0.28, gain: float = 0.078):
        i0 = max(0, int((ts - dur_w * 0.45) * sr))
        ln = min(int(dur_w * sr), n - i0)
        if ln <= 128:
            return
        wt = np.arange(ln, dtype=np.float64) / ln
        env = np.sin(np.pi * wt) ** 1.8
        noise = np.random.default_rng(int(ts * 100) + 19).normal(0, 1, ln)
        b_lp, a_lp = butter(2, [300 / (sr * 0.5), 2600 / (sr * 0.5)], btype="band")
        sw = filtfilt(b_lp, a_lp, noise) * env * gain
        mix_l[i0:i0 + ln] += sw * (1.15 - 0.45 * wt)
        mix_r[i0:i0 + ln] += sw * (0.70 + 0.45 * wt)

    def add_chime(ts: float, gain: float = 0.105):
        i0 = int(ts * sr)
        ln = min(int(0.65 * sr), n - i0)
        if i0 < 0 or ln <= 128:
            return
        ct = np.arange(ln, dtype=np.float64) / sr
        sig = (
            np.sin(2 * np.pi * 1046.5 * ct) * np.exp(-ct * 6.2)
            + 0.65 * np.sin(2 * np.pi * 1318.5 * ct) * np.exp(-ct * 5.0)
            + 0.45 * np.sin(2 * np.pi * 1568.0 * ct) * np.exp(-ct * 4.4)
        ) * gain
        mix_l[i0:i0 + ln] += sig * 0.95
        mix_r[i0:i0 + ln] += sig * 1.05

    for w_ts in [0.06, 5.10, 12.76, 19.10, 32.13, 54.06, 63.70, 74.46, 88.26, 94.26, 115.1]:
        add_whoosh(w_ts)
    for p_ts in [0.45, 5.20, 13.30, 19.20, 35.2, 39.8, 42.0, 45.0, 58.1, 61.0, 69.1, 78.2, 88.5, 95.0, 104.0]:
        add_pop(p_ts, 840.0, 0.082)
    # Typing keyticks on Instagram CTA («آیدایت»)
    for k_ts in [116.2, 116.42, 116.64, 116.86, 117.08, 117.30]:
        add_pop(k_ts, 1250.0, 0.045)
    add_chime(19.25, 0.075)
    add_chime(117.5, 0.110)
    return np.stack([mix_l, mix_r], axis=1)


def prepare_blogger_audio_and_alignment(raw_mp4: str, work_dir: str) -> dict:
    clean_vo_wav = os.path.join(work_dir, "clean_voice_48k.wav")
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", raw_mp4, "-vn",
        "-af", (
            "highpass=f=85,"
            "afftdn=nf=-26:nr=10,"
            "equalizer=f=185:t=q:w=1.2:g=2.5,"
            "equalizer=f=360:t=q:w=1.5:g=-2.0,"
            "equalizer=f=3600:t=q:w=1.1:g=3.2,"
            "equalizer=f=9200:t=h:w=2000:g=1.8,"
            "acompressor=threshold=-24dB:ratio=3.5:attack=7:release=135:makeup=13.2dB,"
            "alimiter=limit=0.88:attack=5:release=50:level=disabled"
        ),
        "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", clean_vo_wav
    ], check=True)

    with wave.open(clean_vo_wav, "rb") as wf:
        vo_mono = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    dur_sec = len(vo_mono) / 48000.0

    rms = np.sqrt(np.mean(vo_mono ** 2) + 1e-12)
    vo_gain = min(3.2, 0.230 / rms)
    vo_mono = np.tanh(vo_mono * vo_gain * 1.10) / np.tanh(1.10) * 0.89

    vo_env = np.convolve(np.abs(vo_mono), np.ones(2400, dtype=np.float64) / 2400.0, mode="same")
    phrases = _build_verified_blogger_phrases()
    word_count = sum(len(p["words"]) for p in phrases)

    bg_sfx_st = _synth_blogger_music_and_sfx(dur_sec, vo_env, 48000)
    master_st = np.zeros_like(bg_sfx_st)
    master_st[:, 0] = vo_mono + bg_sfx_st[:, 0]
    master_st[:, 1] = vo_mono + bg_sfx_st[:, 1]
    peak = np.max(np.abs(master_st)) + 1e-9
    if peak > 0.90:
        master_st = master_st * (0.90 / peak)

    master_wav = os.path.join(work_dir, "master_blogger_v8_48k.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes((np.clip(master_st, -0.96, 0.96) * 32767.0).astype(np.int16).tobytes())

    return {
        "total_dur": round(dur_sec, 3),
        "word_count": word_count,
        "phrase_count": len(phrases),
        "phrases": phrases,
        "master_wav": master_wav,
    }


# =============================================================================
# VIDEO GRADING, AI ROTOSCOPED DEPTH STAGE & UPRIGHT 16:9 MONITOR
# =============================================================================
_VIG_MASK = None
_BG_DARK_CACHE = None

def _get_vignette_mask() -> np.ndarray:
    global _VIG_MASK
    if _VIG_MASK is not None:
        return _VIG_MASK
    yy = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
    top_s = np.clip((0.16 - yy) / 0.16, 0.0, 1.0) * 0.28
    bot_s = np.clip((yy - 0.68) / 0.32, 0.0, 1.0) * 0.56
    rad_s = np.clip((xx ** 2 + ((yy - 0.45) * 1.15) ** 2 - 0.58) * 0.34, 0.0, 0.22)
    _VIG_MASK = np.clip(1.0 - np.maximum(np.maximum(top_s, bot_s), rad_s), 0.36, 1.0)[:, :, None]
    return _VIG_MASK


def _get_studio_dark_backdrop() -> Image.Image:
    global _BG_DARK_CACHE
    if _BG_DARK_CACHE is not None:
        return _BG_DARK_CACHE
    arr = np.zeros((H, W, 3), dtype=np.float32)
    yy = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
    r2 = xx ** 2 + ((yy - 0.46) * 1.35) ** 2
    glow = np.exp(-r2 * 2.1)
    arr[:, :, 0] = 4.0 + 12.0 * glow
    arr[:, :, 1] = 11.0 + 32.0 * glow
    arr[:, :, 2] = 24.0 + 64.0 * glow
    g_col = np.array([3.5, 10.0, 18.0], dtype=np.float32)
    for gx in range(36, W, 72):
        arr[:, gx:gx + 1, :] += glow[:, gx:gx + 1, None] * g_col
    for gy in range(36, H, 72):
        arr[gy:gy + 1, :, :] += glow[gy:gy + 1, :, None] * g_col
    _BG_DARK_CACHE = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    return _BG_DARK_CACHE


def _patch_softbox_corner(crop_rgb: np.ndarray, patch_w: int = 64, patch_h: int = 250) -> np.ndarray:
    h, w, _ = crop_rgb.shape
    pw, ph = min(patch_w, w // 4), min(patch_h, h // 3)
    ref_strip = np.mean(crop_rgb[:ph, pw + 12:pw + 38, :].astype(np.float32), axis=1, keepdims=True)
    yy = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None]
    xx = np.linspace(0.0, 1.0, pw, dtype=np.float32)[None, :]
    alpha = np.clip((1.0 - (xx * 0.92 + yy * 0.78)) * 2.4, 0.0, 1.0)[:, :, None]
    region = crop_rgb[:ph, :pw, :].astype(np.float32)
    crop_rgb[:ph, :pw, :] = np.clip(region * (1.0 - alpha) + ref_strip * alpha, 0, 255).astype(np.uint8)
    return crop_rgb


def _grade_camera_frame(im: Image.Image, contrast: float = 1.07, color: float = 1.09, bright: float = 1.03) -> Image.Image:
    im = ImageEnhance.Brightness(im).enhance(bright)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(color)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.15, percent=58, threshold=3))
    arr = np.asarray(im, dtype=np.float32) * _get_vignette_mask()
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def build_base_video_canvas(frame_idx: int, raw_rgb: np.ndarray, t: float,
                            th_matte_270x480, fonts: BloggerFontPack,
                            stage_surf: cairo.ImageSurface, stage_ctx: cairo.Context) -> Image.Image:
    # A. Talking-Head Shots (0 .. 32.133s) -> Smart Crop + AI Rotoscoped Behind-Person Stage!
    if frame_idx < F_UNBOX_1:
        if frame_idx < F_TH_CUT:
            cx0, cy0, bw0 = 502.0, 784.0, 596.0
            if t < 2.2:
                zm = 1.0 + 0.08 * (1.0 - ease_out_cubic(t / 2.2))
            elif t < 9.1:
                zm = 1.0 + 0.06 * ease_in_out_cubic((t - 2.2) / 6.9)
            else:
                zm = 1.025
        else:
            cx0, cy0, bw0 = 485.0, 742.0, 634.0
            if t < 18.4:
                zm = 1.0 + 0.055 * ease_in_out_cubic((t - 12.77) / 5.63)
            elif t < 25.3:
                zm = 1.090
                cy0 -= 14.0
            elif t < 29.2:
                zm = 1.04 + 0.035 * ease_in_out_cubic((t - 25.3) / 3.9)
            else:
                zm = 1.075 + 0.055 * ease_in_out_cubic((t - 29.2) / 2.93)

        cw = bw0 / zm
        ch = cw * (16.0 / 9.0)
        x0 = int(round(clamp(cx0 - cw * 0.5, 0.0, RAW_W - cw)))
        y0 = int(round(clamp(cy0 - ch * 0.5, 0.0, RAW_H - ch)))
        x1 = min(RAW_W, x0 + int(round(cw)))
        y1 = min(RAW_H, y0 + int(round(ch)))
        sub = raw_rgb[y0:y1, x0:x1, :].copy()
        sub = _patch_softbox_corner(sub, patch_w=64, patch_h=250)
        im_graded = _grade_camera_frame(Image.fromarray(sub, "RGB").resize((W, H), Image.Resampling.LANCZOS))

        if th_matte_270x480 is not None:
            return composite_talking_head_with_depth_vfx(
                im_graded, th_matte_270x480, (x0, y0, x1, y1), (RAW_W, RAW_H),
                t, fonts, stage_surf, stage_ctx
            )
        return im_graded

    # B. Sideways 90° Laptop Software & Live 3D Arch Scan (Shots 13 & 15)
    if (F_SW_ORDER <= frame_idx < F_SPEC_10UM) or (frame_idx >= F_SW_SCAN3D):
        base = _get_studio_dark_backdrop().copy()
        rot_arr = np.rot90(raw_rgb, k=1)
        if frame_idx >= F_SW_SCAN3D:
            tl = (frame_idx - F_SW_SCAN3D) / float(FPS_EDIT)
            zm = 1.04 + 0.055 * math.sin(min(1.0, tl / 26.0) * math.pi * 0.5)
            rw, rh = int(1428 / zm), int(804 / zm)
            rx0 = max(0, min(1428 - rw, (1428 - rw) // 2 + 28))
            ry0 = max(0, min(804 - rh, (804 - rh) // 2 + 12))
            rot_arr = rot_arr[ry0:ry0 + rh, rx0:rx0 + rw, :]

        mon_w, mon_h = 988, 556
        sw_im = ImageEnhance.Contrast(Image.fromarray(rot_arr, "RGB").resize((mon_w, mon_h), Image.Resampling.LANCZOS)).enhance(1.06)
        mask = Image.new("L", (mon_w, mon_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, mon_w - 1, mon_h - 1], radius=22, fill=255)
        base.paste(sw_im, (46, 636), mask)
        return base

    # C. White PDF Spec / Brochure Shots (Shots 10, 11, 14)
    if (F_SPEC_TBL <= frame_idx < F_CASE_CAL) or (F_SPEC_10UM <= frame_idx < F_SW_SCAN3D):
        base = _get_studio_dark_backdrop().copy()
        tl_s = (frame_idx - (F_SPEC_TBL if frame_idx < F_CASE_CAL else F_SPEC_10UM)) / float(FPS_EDIT)
        zm = 1.0 + 0.04 * clamp(tl_s / 5.0)
        cw, ch = int(RAW_W / zm), int(900 / zm)
        x0, y0 = (RAW_W - cw) // 2, 270 + (900 - ch) // 2
        card_im = ImageEnhance.Brightness(
            Image.fromarray(raw_rgb[y0:y0 + ch, x0:x0 + cw, :], "RGB").resize((944, 680), Image.Resampling.LANCZOS)
        ).enhance(0.95)
        mask = Image.new("L", (944, 680), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 943, 679], radius=28, fill=255)
        base.paste(card_im, (68, 578), mask)
        return base

    # D. Hardware & Unboxing B-Roll -> Full 1080x1920 Ken Burns + Grade
    cut_starts = [F_UNBOX_1, F_UNBOX_2, F_UNBOX_3, F_UNBOX_4, F_UNBOX_5, F_MACRO_HEAD, F_BODY_162G, F_CASE_CAL]
    f0 = max(cs for cs in cut_starts if cs <= frame_idx)
    tl_b = (frame_idx - f0) / float(FPS_EDIT)
    zm = 1.0 + 0.065 * clamp(tl_b / 5.2)
    cw, ch = int(RAW_W / zm), int(RAW_H / zm)
    x0, y0 = (RAW_W - cw) // 2, (RAW_H - ch) // 2
    im = Image.fromarray(raw_rgb[y0:y0 + ch, x0:x0 + cw, :], "RGB").resize((W, H), Image.Resampling.LANCZOS)
    return _grade_camera_frame(im, contrast=1.06, color=1.08, bright=1.01)


# =============================================================================
# POWERFUL ANIMATED GLASS CARDS, LIVE COUNTERS, 17 LOGOS & CHUNKY SUBTITLES
# =============================================================================
def _cairo_rrect(ctx, x: float, y: float, w: float, h: float, r: float):
    r = min(r, w * 0.5, h * 0.5)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0.0)
    ctx.arc(x + w - r, y + h - r, r, 0.0, math.pi * 0.5)
    ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
    ctx.close_path()


def _draw_power_glass_card(ctx, x: float, y: float, w: float, h: float, r: float,
                           t: float, enter_p: float, rim_rgb=(0.18, 0.85, 1.0),
                           alpha: float = 1.0):
    """
    Draws an After-Effects-grade Glassmorphic Card with:
    - Spring-scale pop around center
    - Deep ambient shadow
    - Diagonal moving specular sheen sweep
    - Travelling glowing Saber laser rim highlight!
    """
    if alpha <= 0.01:
        return
    sc = 0.82 + 0.18 * spring_pop(clamp(enter_p))
    cx, cy = x + w * 0.5, y + h * 0.5
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(sc, sc)
    ctx.translate(-cx, -cy)

    # Drop shadow
    for si in range(3, 0, -1):
        pad = si * 6.0
        _cairo_rrect(ctx, x - pad * 0.4, y + si * 5.0, w + pad * 0.8, h + pad * 0.4, r + 4)
        ctx.set_source_rgba(0, 0, 0, 0.18 * alpha)
        ctx.fill()

    # Frosted dark-sapphire glass fill
    _cairo_rrect(ctx, x, y, w, h, r)
    lg = cairo.LinearGradient(x, y, x, y + h)
    lg.add_color_stop_rgba(0.0, 0.055, 0.110, 0.215, 0.90 * alpha)
    lg.add_color_stop_rgba(1.0, 0.025, 0.055, 0.120, 0.95 * alpha)
    ctx.set_source(lg)
    ctx.fill()

    # Diagonal Animated Specular Glass Sheen Sweep!
    ctx.save()
    _cairo_rrect(ctx, x, y, w, h, r)
    ctx.clip()
    sh_x = x - 220 + ((t * 340.0) % (w + 480.0))
    sg = cairo.LinearGradient(sh_x - 90, y, sh_x + 90, y + h * 0.6)
    sg.add_color_stop_rgba(0.0, 1, 1, 1, 0.0)
    sg.add_color_stop_rgba(0.5, 1, 1, 1, 0.11 * alpha)
    sg.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)
    ctx.rectangle(x, y, w, h)
    ctx.set_source(sg)
    ctx.fill()
    ctx.restore()

    # Travelling Saber Neon Border!
    ang = t * 2.2
    gx0 = cx + math.cos(ang) * w * 0.55
    gy0 = cy + math.sin(ang) * h * 0.55
    gx1 = cx - math.cos(ang) * w * 0.55
    gy1 = cy - math.sin(ang) * h * 0.55
    rg = cairo.LinearGradient(gx0, gy0, gx1, gy1)
    rg.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.96 * alpha)
    rg.add_color_stop_rgba(0.28, rim_rgb[0], rim_rgb[1], rim_rgb[2], 0.92 * alpha)
    rg.add_color_stop_rgba(0.68, rim_rgb[0] * 0.4, rim_rgb[1] * 0.4, rim_rgb[2] * 0.4, 0.28 * alpha)
    rg.add_color_stop_rgba(1.0, rim_rgb[0], rim_rgb[1], rim_rgb[2], 0.85 * alpha)
    _cairo_rrect(ctx, x, y, w, h, r)
    ctx.set_source(rg)
    ctx.set_line_width(3.2)
    ctx.stroke()

    ctx.restore()


def _paste_rgba(dst_rgba: Image.Image, src_rgba: Image.Image, cx: float, cy: float, alpha_mul: float = 1.0):
    if alpha_mul <= 0.01:
        return
    if alpha_mul < 0.995:
        r, g, b, a = src_rgba.split()
        a = a.point(lambda p: int(p * alpha_mul))
        src_rgba = Image.merge("RGBA", (r, g, b, a))
    x = int(round(cx - src_rgba.width * 0.5))
    y = int(round(cy - src_rgba.height * 0.5))
    dst_rgba.alpha_composite(src_rgba, (x, y))


def render_blogger_overlays_and_subtitles(base_img: Image.Image, frame_idx: int, t: float,
                                          phrases: list, fonts: BloggerFontPack,
                                          surf: cairo.ImageSurface, ctx: cairo.Context) -> bytes:
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    ctx.paint()
    ctx.restore()

    texts = []
    is_dark_stage = (
        (F_SPEC_TBL <= frame_idx < F_CASE_CAL)
        or (F_SW_ORDER <= frame_idx < F_SPEC_10UM)
        or (frame_idx >= F_SPEC_10UM)
    )
    if frame_idx >= F_UNBOX_1:
        draw_broll_ambient_vfx(ctx, t, is_dark_stage=is_dark_stage)

    # -------------------------------------------------------------------------
    # 0. Persistent Brand Pill + Custom DentEye Eye-Tooth Logo (Top-Right)
    # -------------------------------------------------------------------------
    al_b = clamp((t - 0.35) / 0.45)
    if al_b > 0.01:
        _draw_power_glass_card(ctx, 648, 52, 378, 70, 35, t, clamp((t - 0.35) / 0.5), (0.18, 0.85, 1.0), al_b * 0.94)
        draw_topic_logo(ctx, texts, fonts, "denteye", 986, 87, 54, t, al_b)
        sp_en, _, _ = get_stroked_text_sprite("DENTEYE", fonts.bold_30, (*CYAN_RGB, 255), stroke_w=2)
        sp_fa, _, _ = get_stroked_text_sprite("دنت‌آی", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
        ctx.move_to(826, 68); ctx.line_to(826, 106)
        ctx.set_source_rgba(0.45, 0.85, 1.0, 0.5 * al_b); ctx.set_line_width(2.0); ctx.stroke()
        texts.extend([(sp_en, 738, 87, al_b), (sp_fa, 890, 87, al_b)])

    # -------------------------------------------------------------------------
    # 1. Monitor Chrome on Upright 16:9 Live Dental Scan Shots (Shots 13 & 15)
    # -------------------------------------------------------------------------
    if (F_SW_ORDER <= frame_idx < F_SPEC_10UM) or (frame_idx >= F_SW_SCAN3D):
        _cairo_rrect(ctx, 42, 582, 996, 54, 22)
        ctx.set_source_rgba(0.04, 0.09, 0.19, 0.97); ctx.fill()
        _cairo_rrect(ctx, 42, 582, 996, 614, 24)
        ctx.set_source_rgba(0.20, 0.86, 1.0, 0.92); ctx.set_line_width(3.4); ctx.stroke()
        for di, dcol in enumerate([(1.0, 0.35, 0.36), (1.0, 0.76, 0.24), (0.25, 0.92, 0.50)]):
            ctx.arc(78 + di * 26, 609, 7.5, 0, math.pi * 2)
            ctx.set_source_rgba(*dcol, 0.96); ctx.fill()
        sp_m, _, _ = get_stroked_text_sprite("DENTEYE LAB  •  Aidite Rapid 5", fonts.bold_30, (225, 242, 255, 255), stroke_w=2)
        texts.append((sp_m, 535, 609, 1.0))
        ctx.arc(932, 609, 8.0, 0, math.pi * 2)
        ctx.set_source_rgba(0.28, 0.98, 0.58, 0.55 + 0.45 * math.sin(t * 6.0)); ctx.fill()
        sp_lv, _, _ = get_stroked_text_sprite("LIVE", fonts.bold_30, (*GREEN_RGB, 255), stroke_w=2)
        texts.append((sp_lv, 982, 609, 1.0))

    if (F_SPEC_TBL <= frame_idx < F_CASE_CAL) or (F_SPEC_10UM <= frame_idx < F_SW_SCAN3D):
        _cairo_rrect(ctx, 66, 576, 948, 684, 28)
        ctx.set_source_rgba(0.20, 0.86, 1.0, 0.88); ctx.set_line_width(3.4); ctx.stroke()

    # -------------------------------------------------------------------------
    # 2. 13 POWER-ANIMATED CARDS + ALL 17 TOPIC LOGOS & LIVE COUNTERS!
    # -------------------------------------------------------------------------
    # Card 01 (0.45..4.9s): Host Identity + Blue Verified Starburst Badge!
    a1 = window_fade(t, 0.45, 4.90, 0.28, 0.32)
    if a1 > 0.01:
        ep = (t - 0.45) / 0.45
        _draw_power_glass_card(ctx, 72, 1148, 936, 178, 30, t, ep, (0.16, 0.85, 1.0), a1)
        draw_topic_logo(ctx, texts, fonts, "verified_host", 928, 1237, 86, t, a1)
        s1_a, _, _ = get_stroked_text_sprite("میلاد کرامتی‌پور", fonts.lal_56, (255, 255, 255, 255), stroke_w=3)
        s1_b, _, _ = get_stroked_text_sprite("کارشناس تجهیزات دندانپزشکی  •  دنت‌آی", fonts.bold_34, (*CYAN_RGB, 255), stroke_w=2)
        texts.extend([(s1_a, 468, 1204, a1), (s1_b, 468, 1278, a1)])

    # Card 02 (5.10..12.6s): Dental Stock Grade-A+ + Sparkling Molar Tooth Logo!
    a2 = window_fade(t, 5.10, 12.60, 0.28, 0.32)
    if a2 > 0.01:
        ep = (t - 5.10) / 0.45
        _draw_power_glass_card(ctx, 64, 1148, 952, 178, 30, t, ep, (0.26, 0.98, 0.58), a2)
        draw_topic_logo(ctx, texts, fonts, "dental_stock", 930, 1237, 94, t, a2)
        s2_a, _, _ = get_stroked_text_sprite("تجهیزات دندانپزشکی استوک در حد نو", fonts.lal_48, (*GREEN_RGB, 255), stroke_w=3)
        s2_b, _, _ = get_stroked_text_sprite("معرفی، تست واقعی و بررسی تخصصی در دنت‌آی", fonts.bold_34, (245, 250, 255, 255), stroke_w=2)
        texts.extend([(s2_a, 456, 1204, a2), (s2_b, 456, 1278, a2)])

    # Card 03 (12.95..19.0s): Official Aidite Brand Logo + Rapid 5 Laser Scanner Wand Logo!
    a3 = window_fade(t, 12.95, 19.00, 0.28, 0.32)
    if a3 > 0.01:
        ep = (t - 12.95) / 0.45
        _draw_power_glass_card(ctx, 56, 1142, 968, 186, 30, t, ep, (0.18, 0.85, 1.0), a3)
        draw_topic_logo(ctx, texts, fonts, "aidite_brand", 205, 1235, 96, t, a3)
        draw_topic_logo(ctx, texts, fonts, "rapid5_wand", 934, 1235, 96, t, a3)
        s3_a, _, _ = get_stroked_text_sprite("Aidite Rapid 5", fonts.black_58, (*CYAN_RGB, 255), stroke_w=3)
        s3_b, _, _ = get_stroked_text_sprite("اورال اسکنر دیجیتال سه‌بعدی", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
        texts.extend([(s3_a, 575, 1202, a3), (s3_b, 575, 1278, a3)])

    # Card 04 (19.15..31.9s): DentEye Technical QC Shield Logo!
    a4 = window_fade(t, 19.15, 31.90, 0.28, 0.32)
    if a4 > 0.01:
        ep = (t - 19.15) / 0.45
        _draw_power_glass_card(ctx, 58, 1146, 964, 182, 30, t, ep, (0.26, 0.98, 0.56), a4)
        draw_topic_logo(ctx, texts, fonts, "qc_shield", 932, 1237, 98, t, a4)
        s4_a, _, _ = get_stroked_text_sprite("تایید کارشناسان فنی دنت‌آی", fonts.lal_56, (*GREEN_RGB, 255), stroke_w=3)
        s4_b, _, _ = get_stroked_text_sprite("عبور از فیلتر تخصصی سلامت و بالاترین کیفیت", fonts.bold_34, (245, 252, 255, 255), stroke_w=2)
        texts.extend([(s4_a, 462, 1204, a4), (s4_b, 462, 1278, a4)])

    # Card 05 (32.25..53.95s): Interactive 4-Item Unboxing Grid WITH DEDICATED LOGOS FOR EACH ITEM!
    a5 = window_fade(t, 32.25, 53.95, 0.28, 0.32)
    if a5 > 0.01:
        _draw_power_glass_card(ctx, 48, 138, 984, 382, 30, t, (t - 32.25) / 0.45, (0.18, 0.85, 1.0), a5)
        st_u, _, _ = get_stroked_text_sprite("اقلام همراه اورال اسکنر Aidite Rapid 5", fonts.lal_48, (*CYAN_RGB, 255), stroke_w=3)
        texts.append((st_u, 540, 192, a5))
        u_items = [
            (36.6, "stand",       "استند رومیزی",           548, 250),
            (40.8, "rapid5_wand", "هندپیس اسکنر",           68,  250),
            (42.3, "usb_flash",   "فلش نرم‌افزار",          548, 384),
            (45.1, "scan_tips_4", "۳ تیپ عادی + ۱ مینی",    68,  384),
        ]
        for t_on, l_kind, itxt, ix, iy in u_items:
            act = clamp((t - t_on) / 0.38)
            rim = (0.26, 0.98, 0.58) if act > 0.4 else (0.25, 0.42, 0.60)
            _draw_power_glass_card(ctx, ix, iy, 464, 112, 22, t, max(0.35, act), rim, a5 * (0.50 + 0.50 * act))
            draw_topic_logo(ctx, texts, fonts, l_kind, ix + 402, iy + 56, 82, t, a5 * (0.55 + 0.45 * act))
            tcol = (*GREEN_RGB, 255) if act > 0.4 else (225, 238, 252, 225)
            sp_i, _, _ = get_stroked_text_sprite(itxt, fonts.black_36, tcol, stroke_w=2)
            texts.append((sp_i, ix + 175, iy + 56, a5 * (0.60 + 0.40 * act)))

    # Card 06 (54.10..58.00s): Autoclave Rising Steam Logo + Live Rolling Counter 0 -> ۱۰۰ بار!
    a6 = window_fade(t, 54.10, 58.00, 0.24, 0.28)
    if a6 > 0.01:
        cnt_100 = int(round(100 * ease_out_cubic(clamp((t - 54.25) / 1.35))))
        _draw_power_glass_card(ctx, 56, 152, 968, 206, 30, t, (t - 54.10) / 0.42, (1.0, 0.80, 0.24), a6)
        draw_topic_logo(ctx, texts, fonts, "autoclave_100", 922, 255, 122, t, a6)
        s6_a, _, _ = get_stroked_text_sprite(f"قابلیت اتوکلاو: تا {fa(cnt_100)} بار استریل!", fonts.lal_56, (*AMBER_RGB, 255), stroke_w=3)
        s6_b, _, _ = get_stroked_text_sprite("مقاوم در برابر بخار ۱۳۴ درجه و بهداشت کامل مطب", fonts.bold_34, (245, 250, 255, 255), stroke_w=2)
        texts.extend([(s6_a, 452, 218, a6), (s6_b, 452, 302, a6)])

    # Card 07 (58.05..68.95s): Dual Ergonomic Spec Cards + Feather 162g & Laser 25mm Logos + Counters!
    a7 = window_fade(t, 58.05, 68.95, 0.28, 0.30)
    if a7 > 0.01:
        cnt_g = int(round(162 * ease_out_cubic(clamp((t - 58.2) / 1.4))))
        _draw_power_glass_card(ctx, 52, 162, 472, 360, 28, t, (t - 58.05) / 0.45, (0.18, 0.86, 1.0), a7)
        draw_topic_logo(ctx, texts, fonts, "feather_162g", 288, 244, 102, t, a7)
        s7_a1, _, _ = get_stroked_text_sprite(f"{fa(cnt_g)} گرم", fonts.black_72, (*CYAN_RGB, 255), stroke_w=4)
        s7_a2, _, _ = get_stroked_text_sprite("وزن فوق‌سبک و خوش‌دست", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
        texts.extend([(s7_a1, 288, 378, a7), (s7_a2, 288, 466, a7)])

        a7b = a7 * clamp((t - 60.8) / 0.42)
        if a7b > 0.01:
            cnt_m = int(round(25 * ease_out_cubic(clamp((t - 60.9) / 1.2))))
            _draw_power_glass_card(ctx, 556, 162, 472, 360, 28, t, (t - 60.8) / 0.45, (0.26, 0.98, 0.58), a7b)
            draw_topic_logo(ctx, texts, fonts, "laser_25mm", 792, 244, 102, t, a7b)
            s7_b1, _, _ = get_stroked_text_sprite(f"{fa(cnt_m)} میلی‌متر", fonts.lal_68, (*GREEN_RGB, 255), stroke_w=4)
            s7_b2, _, _ = get_stroked_text_sprite("عمق میدان اسکن بالا", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
            texts.extend([(s7_b1, 792, 378, a7b), (s7_b2, 792, 466, a7b)])

    # Card 08 (69.0..74.45s): No-Calibration Precision Lock Logo!
    a8 = window_fade(t, 69.00, 74.45, 0.28, 0.28)
    if a8 > 0.01:
        _draw_power_glass_card(ctx, 54, 158, 972, 206, 30, t, (t - 69.0) / 0.45, (0.26, 0.98, 0.58), a8)
        draw_topic_logo(ctx, texts, fonts, "no_calibration", 928, 261, 120, t, a8)
        s8_1, _, _ = get_stroked_text_sprite("بدون نیاز به کالیبراسیون دوره‌ای!", fonts.lal_56, (*GREEN_RGB, 255), stroke_w=3)
        s8_2, _, _ = get_stroked_text_sprite("دقت پایدار همیشگی و حذف کامل دردسر کالیبره", fonts.bold_34, (245, 252, 255, 255), stroke_w=2)
        texts.extend([(s8_1, 456, 224, a8), (s8_2, 456, 308, a8)])

    # Card 09 (74.5..88.25s): Dual Animated Stopwatch Logos + Live Speed Counters (25s & 60s)!
    a9 = window_fade(t, 74.50, 88.25, 0.28, 0.28)
    if a9 > 0.01:
        c25 = int(round(25 * ease_out_cubic(clamp((t - 79.0) / 1.5)))) if t >= 79.0 else 25
        _draw_power_glass_card(ctx, 556, 168, 472, 378, 28, t, (t - 74.5) / 0.45, (0.18, 0.86, 1.0), a9)
        draw_topic_logo(ctx, texts, fonts, "stopwatch", 792, 252, 104, t, a9)
        s9_a1, _, _ = get_stroked_text_sprite(f"{fa(c25)} ثانیه", fonts.black_72, (*CYAN_RGB, 255), stroke_w=4)
        s9_a2, _, _ = get_stroked_text_sprite("اسکن کامل یک فک", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
        texts.extend([(s9_a1, 792, 388, a9), (s9_a2, 792, 480, a9)])

        a9b = a9 * clamp((t - 78.2) / 0.45)
        if a9b > 0.01:
            c60 = int(round(60 * ease_out_cubic(clamp((t - 83.2) / 1.5)))) if t >= 83.2 else 60
            _draw_power_glass_card(ctx, 52, 168, 472, 378, 28, t, (t - 78.2) / 0.45, (0.26, 0.98, 0.58), a9b)
            draw_topic_logo(ctx, texts, fonts, "stopwatch", 288, 252, 104, t + 1.1, a9b)
            s9_b1, _, _ = get_stroked_text_sprite(f"{fa(c60)} ثانیه", fonts.black_72, (*GREEN_RGB, 255), stroke_w=4)
            s9_b2, _, _ = get_stroked_text_sprite("اسکن فول‌آرچ دو فک", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
            texts.extend([(s9_b1, 288, 388, a9b), (s9_b2, 288, 480, a9b)])

    # Card 10 (88.3..94.25s): Micron Crosshair Reticle Logos + 10µm & 20µm Counters!
    a10 = window_fade(t, 88.30, 94.25, 0.26, 0.28)
    if a10 > 0.01:
        c10 = int(round(10 * ease_out_cubic(clamp((t - 88.5) / 1.1))))
        c20 = int(round(20 * ease_out_cubic(clamp((t - 90.5) / 1.1)))) if t >= 90.5 else 20
        _draw_power_glass_card(ctx, 556, 168, 472, 375, 28, t, (t - 88.3) / 0.45, (0.18, 0.86, 1.0), a10)
        draw_topic_logo(ctx, texts, fonts, "micron_target", 792, 250, 104, t, a10)
        s10_a1, _, _ = get_stroked_text_sprite(f"{fa(c10)} میکرون", fonts.lal_68, (*CYAN_RGB, 255), stroke_w=4)
        s10_a2, _, _ = get_stroked_text_sprite("دقت تک‌واحد (سینگل‌کراون)", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
        texts.extend([(s10_a1, 792, 388, a10), (s10_a2, 792, 478, a10)])

        _draw_power_glass_card(ctx, 52, 168, 472, 375, 28, t, (t - 88.5) / 0.45, (1.0, 0.80, 0.25), a10)
        draw_topic_logo(ctx, texts, fonts, "micron_target", 288, 250, 104, t + 0.8, a10)
        s10_b1, _, _ = get_stroked_text_sprite(f"{fa(c20)} میکرون", fonts.lal_68, (*AMBER_RGB, 255), stroke_w=4)
        s10_b2, _, _ = get_stroked_text_sprite("دقت فک کامل (فول‌آرچ)", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
        texts.extend([(s10_b1, 288, 388, a10), (s10_b2, 288, 478, a10)])

    # Card 11 (94.3..103.8s): Soft-Tissue AI Neural Chip Logo!
    a11 = window_fade(t, 94.30, 103.80, 0.28, 0.30)
    if a11 > 0.01:
        _draw_power_glass_card(ctx, 54, 195, 972, 320, 30, t, (t - 94.3) / 0.45, (0.98, 0.48, 0.70), a11)
        draw_topic_logo(ctx, texts, fonts, "soft_tissue_ai", 916, 355, 130, t, a11)
        s11_1, _, _ = get_stroked_text_sprite("بازیابی تصویر و بافت‌های نرم", fonts.lal_56, (*CYAN_RGB, 255), stroke_w=3)
        s11_2, _, _ = get_stroked_text_sprite("تشخیص پیوسته‌ی جزئیات لثه و دندان حین حرکت", fonts.bold_34, (255, 255, 255, 255), stroke_w=2)
        texts.extend([(s11_1, 448, 302, a11), (s11_2, 448, 412, a11)])

    # Card 12 (103.9..115.0s): 3-Pillar Summary WITH Feather + Stopwatch + Micron Logos!
    a12 = window_fade(t, 103.90, 115.00, 0.28, 0.30)
    if a12 > 0.01:
        _draw_power_glass_card(ctx, 48, 168, 984, 376, 30, t, (t - 103.9) / 0.45, (0.26, 0.98, 0.58), a12)
        s12_t, _, _ = get_stroked_text_sprite("چرا Aidite Rapid 5 انتخاب ایده‌آل مطب است؟", fonts.lal_48, (*GREEN_RGB, 255), stroke_w=3)
        texts.append((s12_t, 540, 224, a12))
        pillars = [
            ("feather_162g",  "فوق‌سبک ۱۶۲g",   706, CYAN_RGB),
            ("stopwatch",     "سریع ۲۵ ثانیه",  390, GREEN_RGB),
            ("micron_target", "دقت ۱۰ میکرون",  74,  AMBER_RGB),
        ]
        for l_k, ptxt, px, prgb in pillars:
            _draw_power_glass_card(ctx, px, 282, 300, 232, 24, t, (t - 104.2) / 0.5, (prgb[0]/255, prgb[1]/255, prgb[2]/255), a12)
            draw_topic_logo(ctx, texts, fonts, l_k, px + 150, 354, 88, t, a12)
            sp_p, _, _ = get_stroked_text_sprite(ptxt, fonts.black_36, (*prgb, 255), stroke_w=2)
            texts.append((sp_p, px + 150, 462, a12))

    # Card 13 (115.1..122.43s): OFFICIAL INSTAGRAM GRADIENT LOGO + LIVE TYPING «آیدایت» CTA!
    a13 = clamp((t - 115.1) / 0.36)
    if a13 > 0.01:
        _draw_power_glass_card(ctx, 46, 164, 988, 376, 32, t, (t - 115.1) / 0.48, (0.28, 0.98, 0.58), a13)
        draw_topic_logo(ctx, texts, fonts, "instagram", 922, 256, 112, t, a13)
        s13_1, _, _ = get_stroked_text_sprite("استعلام قیمت ویژه و دریافت اطلاعات بیشتر:", fonts.eb_38, (255, 255, 255, 255), stroke_w=3)
        texts.append((s13_1, 456, 256, a13))

        # Live Typing Animation inside glowing Instagram Comment Box!
        word_target = "آیدایت"
        n_chars = int(clamp((t - 116.0) / 1.35) * len(word_target))
        typed = word_target[:max(1, n_chars)] if t >= 116.0 else word_target
        cursor = "|" if (int(t * 3.5) % 2 == 0 and t < 118.5) else ""
        cta_txt = f"کامنت کن:  « {typed}{cursor} »"

        _draw_power_glass_card(ctx, 88, 352, 904, 152, 76, t * 1.4, (t - 115.4) / 0.5, (1.0, 0.80, 0.25), a13)
        draw_topic_logo(ctx, texts, fonts, "verified_host", 906, 428, 92, t, a13)
        s13_2, _, _ = get_stroked_text_sprite(cta_txt, fonts.lal_68, (*AMBER_RGB, 255), stroke_w=4)
        texts.append((s13_2, 468, 428, a13))

    # -------------------------------------------------------------------------
    # 3. ULTRA-LEGIBLE STROKED SUBTITLES (Vazirmatn-Black 50px + Active Word Pill!)
    # -------------------------------------------------------------------------
    active_phrase = None
    for ph in phrases:
        if ph["start"] - 0.06 <= t <= ph["end"]:
            active_phrase = ph
            break

    if active_phrase is not None:
        p_al = clamp((t - (active_phrase["start"] - 0.06)) / 0.13) * clamp((active_phrase["end"] - t) / 0.13)
        if p_al > 0.02:
            w_list = active_phrase["words"]
            act_idx = 0
            for wi, wd in enumerate(w_list):
                if t >= wd["start"] - 0.04:
                    act_idx = wi

            font_sub = fonts.black_50
            gap = 18
            measured = []
            total_w = 0
            for wd in w_list:
                _, ww, wh = get_stroked_text_sprite(wd["word"], font_sub, (255, 255, 255, 255), stroke_w=3)
                measured.append((wd["word"], ww, wh))
                total_w += ww
            total_w += gap * max(0, len(measured) - 1)

            if total_w > 900:
                font_sub = fonts.black_42
                gap = 14
                measured = []
                total_w = 0
                for wd in w_list:
                    _, ww, wh = get_stroked_text_sprite(wd["word"], font_sub, (255, 255, 255, 255), stroke_w=3)
                    measured.append((wd["word"], ww, wh))
                    total_w += ww
                total_w += gap * max(0, len(measured) - 1)

            sub_cy = 1488.0 + (1.0 - spring_pop(clamp((t - active_phrase["start"] + 0.06) / 0.22))) * 18.0
            box_w = min(1004.0, total_w + 84.0)
            box_h = 122.0
            _draw_power_glass_card(ctx, 540.0 - box_w * 0.5, sub_cy - box_h * 0.5, box_w, box_h, 34,
                                   t, 1.0, (0.20, 0.84, 1.0), p_al)

            cur_right = 540.0 + total_w * 0.5
            for wi, (w_str, ww, wh) in enumerate(measured):
                w_cx = cur_right - ww * 0.5
                is_act = (wi == act_idx)
                clean_tok = re.sub(r"[\.،؛؟!:«»]", "", w_str)
                is_kw = any(kw in clean_tok for kw in POWER_KEYWORDS)

                if is_act:
                    pill_col = (1.0, 0.82, 0.20) if is_kw else (0.15, 0.88, 1.0)
                    pw = ww + 30.0
                    ph_h = 84.0
                    _cairo_rrect(ctx, w_cx - pw * 0.5, sub_cy - ph_h * 0.5, pw, ph_h, 22.0)
                    ctx.set_source_rgba(pill_col[0], pill_col[1], pill_col[2], 0.98 * p_al)
                    ctx.fill()
                    sp_dark, _, _ = get_stroked_text_sprite(w_str, font_sub, DARK_TXT, stroke_w=0)
                    texts.append((sp_dark, w_cx, sub_cy + 1, p_al))
                elif wi < act_idx:
                    c_sp = (*AMBER_RGB, 255) if is_kw else (255, 255, 255, 255)
                    sp_wh, _, _ = get_stroked_text_sprite(w_str, font_sub, c_sp, stroke_w=3)
                    texts.append((sp_wh, w_cx, sub_cy, p_al))
                else:
                    sp_dim, _, _ = get_stroked_text_sprite(w_str, font_sub, (220, 236, 252, 205), stroke_w=2)
                    texts.append((sp_dim, w_cx, sub_cy, p_al))

                cur_right -= (ww + gap)

    # 4. Energetic Optical Whip-Flash on Cuts
    flash = 0.0
    for tc_cut in (0.0, 12.767, 32.133, 54.067, 63.700, 74.467, 88.267, 94.267, 115.1):
        dt_c = abs(t - tc_cut)
        if dt_c < 0.16:
            flash = max(flash, (1.0 - dt_c / 0.16) * 0.22)
    if flash > 0.01:
        rg = cairo.RadialGradient(540, 760, 40, 540, 760, 940)
        rg.add_color_stop_rgba(0.0, 0.55, 0.92, 1.0, flash)
        rg.add_color_stop_rgba(1.0, 0.10, 0.45, 0.95, 0.0)
        ctx.rectangle(0, 0, W, H)
        ctx.set_source(rg)
        ctx.fill()

    ov_rgba = _cairo_surface_to_pil_rgba(surf)
    for sp, cx, cy, al in texts:
        _paste_rgba(ov_rgba, sp, cx, cy, al)

    out_rgba = base_img.convert("RGBA")
    out_rgba.alpha_composite(ov_rgba)
    return out_rgba.convert("RGB").tobytes()


# =============================================================================
# MULTIPROCESS WORKER & CLOUD PIPELINE
# =============================================================================
_W_FONTS = None
_W_PHRASES = None
_W_MATTES = None
_W_SURF = None
_W_CTX = None
_W_STAGE_SURF = None
_W_STAGE_CTX = None

def _init_blogger_worker(font_dir: str, phrases: list, mattes_npy_path: str):
    global _W_FONTS, _W_PHRASES, _W_MATTES, _W_SURF, _W_CTX, _W_STAGE_SURF, _W_STAGE_CTX
    _W_FONTS = BloggerFontPack(font_dir)
    _W_PHRASES = phrases
    _W_MATTES = np.load(mattes_npy_path, mmap_mode="r") if (mattes_npy_path and os.path.exists(mattes_npy_path)) else None
    _W_SURF = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CTX = cairo.Context(_W_SURF)
    _W_STAGE_SURF = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_STAGE_CTX = cairo.Context(_W_STAGE_SURF)


def _render_blogger_batch(batch_items: list) -> list:
    out = []
    for frame_idx, raw_bytes in batch_items:
        raw_arr = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((RAW_H, RAW_W, 3))
        t = frame_idx / float(FPS_EDIT)
        th_m = _W_MATTES[frame_idx] if (_W_MATTES is not None and frame_idx < len(_W_MATTES)) else None
        base_im = build_base_video_canvas(frame_idx, raw_arr, t, th_m, _W_FONTS, _W_STAGE_SURF, _W_STAGE_CTX)
        rgb_bytes = render_blogger_overlays_and_subtitles(
            base_im, frame_idx, t, _W_PHRASES, _W_FONTS, _W_SURF, _W_CTX
        )
        out.append((frame_idx, rgb_bytes))
    return out


def fetch_raw_client_video(work_dir: str) -> str:
    raw_mp4 = os.path.join(work_dir, "raw_client_denteye.mp4")
    if os.path.exists(raw_mp4) and os.path.getsize(raw_mp4) > 50_000_000:
        return raw_mp4
    for url in (RAW_PRIMARY_URL, RAW_FALLBACK_URL):
        try:
            print(f"[Studio v8.0] Fetching raw client video from {url} ...", flush=True)
            subprocess.run(["curl", "-fSL", "-L", "--retry", "3", "-A", "Mozilla/5.0", url, "-o", raw_mp4], check=True)
            if os.path.getsize(raw_mp4) > 50_000_000:
                return raw_mp4
        except Exception as e:
            print(f"[Warn] Download failed from {url}: {e}", flush=True)
    raise RuntimeError("Could not download raw_client_denteye.mp4")


def save_blogger_qa_sheets(raw_mp4: str, font_dir: str, meta: dict, mattes_npy: str, qa_dir: str):
    os.makedirs(qa_dir, exist_ok=True)
    fonts = BloggerFontPack(font_dir)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    st_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    st_ctx = cairo.Context(st_surf)
    mattes = np.load(mattes_npy, mmap_mode="r") if (mattes_npy and os.path.exists(mattes_npy)) else None
    phrases = meta["phrases"]

    sample_ts = [2.2, 7.5, 15.5, 22.0, 38.5, 48.0, 56.0, 65.0, 71.5, 81.5, 99.0, 118.5]
    grid = Image.new("RGB", (4 * 360, 3 * 640), (0, 0, 0))
    for i, tm in enumerate(sample_ts):
        f_idx = int(round(tm * FPS_EDIT))
        p = subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", f"{tm:.3f}", "-i", raw_mp4,
            "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ], capture_output=True, check=True)
        raw_arr = np.frombuffer(p.stdout, dtype=np.uint8).reshape((RAW_H, RAW_W, 3))
        th_m = mattes[f_idx] if (mattes is not None and f_idx < len(mattes)) else None
        base_im = build_base_video_canvas(f_idx, raw_arr, tm, th_m, fonts, st_surf, st_ctx)
        rgb = render_blogger_overlays_and_subtitles(base_im, f_idx, tm, phrases, fonts, surf, ctx)
        im_out = Image.frombytes("RGB", (W, H), rgb).resize((360, 640), Image.Resampling.LANCZOS)
        grid.paste(im_out, ((i % 4) * 360, (i // 4) * 640))
    grid.save(os.path.join(qa_dir, "storyboard_12_blogger_denteye.png"))

    strip = Image.new("RGB", (W, 8 * 160), (6, 12, 22))
    for k in range(min(8, len(phrases))):
        ph = phrases[min(len(phrases) - 1, k * max(1, len(phrases) // 8))]
        tm = 0.5 * (ph["start"] + ph["end"])
        f_idx = int(round(tm * FPS_EDIT))
        base_im = Image.new("RGB", (W, H), (10, 18, 32))
        rgb = render_blogger_overlays_and_subtitles(base_im, f_idx, tm, phrases, fonts, surf, ctx)
        crop = Image.frombytes("RGB", (W, H), rgb).crop((0, 1408, W, 1568))
        strip.paste(crop, (0, k * 160))
    strip.save(os.path.join(qa_dir, "subtitle_strip_blogger_denteye.png"))


def run_cloud_pipeline(font_dir: str, work_dir: str, out_mp4: str, qa_dir: str, whisper_sz: str = "medium"):
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
    os.makedirs(qa_dir, exist_ok=True)

    raw_mp4 = fetch_raw_client_video(work_dir)
    mattes_npy = precompute_talking_head_mattes(raw_mp4, work_dir, num_th_frames=F_UNBOX_1)
    meta = prepare_blogger_audio_and_alignment(raw_mp4, work_dir)
    with open(os.path.join(qa_dir, "alignment.json"), "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in meta.items() if k != "master_wav"}, f, ensure_ascii=False, indent=2)

    save_blogger_qa_sheets(raw_mp4, font_dir, meta, mattes_npy, qa_dir)

    frame_bytes_len = RAW_W * RAW_H * 3
    dec_proc = subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", raw_mp4, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ], stdout=subprocess.PIPE, bufsize=frame_bytes_len * 4)

    enc_cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS_EDIT),
        "-i", "-",
        "-i", meta["master_wav"],
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "slow", "-crf", "19",
        "-profile:v", "high", "-level:v", "4.2", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-af", "volume=+0.2dB,alimiter=limit=0.895:attack=5:release=50:level=disabled",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-shortest",
        out_mp4
    ]
    enc_proc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE, bufsize=W * H * 3 * 4)

    workers = max(2, min(4, os.cpu_count() or 2))
    print(f"[Studio v8.0] Rendering 1080x1920 @ {FPS_EDIT}fps on {workers} cores with AI Rotoscope VFX...", flush=True)

    def _batch_reader(batch_sz: int = 8):
        f_idx = 0
        batch = []
        while True:
            buf = dec_proc.stdout.read(frame_bytes_len)
            if not buf or len(buf) < frame_bytes_len:
                break
            batch.append((f_idx, buf))
            f_idx += 1
            if len(batch) >= batch_sz:
                yield batch
                batch = []
        if batch:
            yield batch

    rendered = 0
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_blogger_worker,
                             initargs=(font_dir, meta["phrases"], mattes_npy)) as pool:
        for batch_out in pool.map(_render_blogger_batch, _batch_reader(8), chunksize=1):
            for _, out_bytes in batch_out:
                enc_proc.stdin.write(out_bytes)
                rendered += 1
            if rendered % 480 == 0:
                print(f"  -> {rendered} frames ({rendered / FPS_EDIT:.1f}s) composited...", flush=True)

    dec_proc.stdout.close()
    dec_proc.wait()
    enc_proc.stdin.close()
    rc = enc_proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg encode failed with code {rc}")
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"[Studio v8.0] MASTER READY: {out_mp4} ({rendered} frames, {sz_mb:.2f} MB)", flush=True)


if __name__ == "__main__":
    if len(sys.argv) >= 6 and sys.argv[1] == "--cloud-render":
        run_cloud_pipeline(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else "medium")
    else:
        print("Usage: python src/episodes/ep12_denteye_aidite_blogger_edit.py --cloud-render <fonts> <work> <out.mp4> <qa_dir>")
