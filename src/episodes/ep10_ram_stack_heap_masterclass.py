"""
Episode 10 — Personal Multi-Minute Visual Masterclass:
«رَم (RAM)، اِستَک (Stack) و هیپ (Heap) دقیقاً چی هستن و چه فرقی دارن؟»
Studio v6.1 — Sapphire Rim-Lit Glassmorphic UI + 3D Character + Live Neon Stylus Sketching
  - Slow, calm, unhurried pedagogical narration (`slow_time_ratio=1.15`, ~4 minutes)
  - 12 progressive live-drawn visual chapters covering:
    1. Opening 3D desk character + calm learning roadmap
    2. Hardware trio live sketch: SSD/Hard (permanent slow warehouse) vs CPU (ultra-fast brain)
    3. RAM live sketch: numbered volatile glass workbench (Random Access + Volatility)
    4. Zoom inside RAM: Code, Static, Heap (↑), and Stack (↓) living inside the SAME RAM!
    5. Stack deep dive: live-drawn LIFO trays, main() -> calc() Push/Pop in 1ns via SP
    6. Stack limitation: fixed/small compile-time size vs huge/dynamic runtime data
    7. Heap deep dive: live-drawn open dynamic warehouse for large/flexible objects
    8. Stack + Heap connection: Pointer / Reference (`0x7F40` receipt on Stack -> Object on Heap)
    9. Bug #1: Stack Overflow (infinite recursion smashing the Stack ceiling)
   10. Bug #2: Memory Leak & Garbage Collector (orphaned Heap block swept clean)
   11. Complete Sapphire Master Comparison Matrix (Stack vs Heap) + 3D Character Lightbulb
   12. Signature Sapphire Pill Closing Card (@zavieh.penhann)
"""
import os
import sys
import time
import math
import subprocess
import numpy as np
import cairocffi as cairo
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.engine.render_core import (
    W, H, FontBank, clamp, ease_out_cubic, ease_in_out_cubic,
    get_fitted_text_sprite
)
from src.engine.audio_master import (
    build_slow_masterclass_audio, LOCKED_SIGNATURE_VOICE
)
from src.engine.sapphire_ui_core import (
    SAPPHIRE_SUB_Y, C_CYAN_CORE, C_CYAN_MID, C_GREEN, C_RED, C_AMBER,
    rounded_rect_path, get_multitone_persian_sprite, composite_sapphire_frame,
    draw_laser_glass_card, draw_glass_status_medallion,
    draw_sapphire_desk_scene_side, draw_sapphire_thinking_character_front,
    draw_neon_pen_nib, draw_sketch_poly, draw_sketch_glass_box,
    draw_sketch_bezier_wire, draw_sketch_storage_cylinder, draw_sketch_cpu_die
)

FPS_MC = 30  # Matches Studio v6.0 reference framerate; keeps ~4-min master render nimble & crisp!

CYAN_RGB  = (68, 204, 255)
GREEN_RGB = (82, 255, 136)
RED_RGB   = (255, 76, 82)
AMBER_RGB = (255, 196, 72)

# =============================================================================
# 60-SEGMENT CALM, SLOW-PACED PEDAGOGICAL MASTERCLASS SCRIPT (~4 MINUTES)
# Spoken text is 100% vocalized Persian so Rasalgethi & Whisper align with 0.00s drift!
# =============================================================================
SCRIPT_SEGMENTS = [
    # --- Ch.1 (0..4): Opening 3D Desk Character & Calm Promise ---
    ("تا حالا شده کلمه‌هایِ رَم، اِستَک و هیپ رو زیاد بشنوی،", "تا حالا کلمه‌هایِ رَم، اِستَک و هیپ رو شنیدی،"),
    ("ولی همیشه تو ذهنت، یه هاله‌یِ گُنگ و مبهم دورشون باشه؟", "ولی همیشه تو ذهنت گُنگ و مبهم مونده باشن؟"),
    ("امروز می‌خوایم خیلی آروم، بدونِ عجله و قدم‌به‌قدم،", "امروز خیلی آروم، بدونِ عجله و قدم‌به‌قدم،"),
    ("با نقاشیِ زنده، کلِّ ماجرایِ حافظه رو از صفر باز کنیم؛", "با نقاشیِ زنده، کلِّ ماجرایِ حافظه رو باز می‌کنیم؛"),
    ("طوری که یک‌بار برایِ همیشه، کاملِ کامل درکش کنی.", "تا یک‌بار برایِ همیشه، کاملِ کامل درکش کنی."),

    # --- Ch.2 (5..10): Hardware Trio — SSD Warehouse vs Ultra-Fast CPU ---
    ("بیا از یک تصویرِ خیلی ساده تویِ دنیایِ واقعی شروع کنیم.", "از یک مثالِ ساده تویِ دنیایِ واقعی شروع کنیم."),
    ("تصور کن کامپیوترِ تو، دقیقاً مثلِ کارگاهِ یک نجّارِ ماهره.", "کامپیوترِ تو، مثلِ کارگاهِ یک نجّارِ ماهره."),
    ("سمتِ چپ، هارد یا اِس‌اِس‌دی رو داریم؛ یعنی انبارِ بزرگ و دائمی.", "هارد یا اس‌اس‌دی: انبارِ بزرگ و دائمیِ کارگاه."),
    ("همه‌یِ فیلم‌ها، عکس‌ها و برنامه‌ها، حتی وقتی برق خاموشه، اونجا می‌مونن.", "وقتی برق خاموشه هم، همه‌چیز اونجا امن می‌مونه."),
    ("سمتِ راست، سی‌پی‌یو رو داریم؛ یعنی خودِ نجّار که با سرعتِ نور کار می‌کنه!", "سی‌پی‌یو: مغزِ پردازنده که با سرعتِ نور کار می‌کنه!"),
    ("اما یه مشکلِ بزرگ هست: راهِ رفت‌وآمد به انبارِ هارد، برایِ سی‌پی‌یو خیلی کُنده!", "مشکل: رفت‌وآمدِ مستقیم به هارد، خیلی کُنده!"),

    # --- Ch.3 (11..17): What RAM Really Is (Workbench + Random Access + Volatile) ---
    ("اینجاست که قهرمانِ اول واردِ صحنه می‌شه: یعنی حافظه‌یِ رَم!", "قهرمانِ اول وارد می‌شه: حافظه‌یِ رَم!"),
    ("رَم دقیقاً میزِ کارِ شیشه‌ای و دمِ دستِ سی‌پی‌یوئه.", "رَم، دقیقاً میزِ کارِ دمِ دستِ سی‌پی‌یوئه."),
    ("وقتی برنامه‌ای رو باز می‌کنی، فایل‌هاش از انبارِ هارد میان رویِ میزِ رَم.", "برنامه که باز بشه، از هارد میاد رویِ میزِ رَم."),
    ("رویِ این میز، میلیون‌ها خونه‌یِ کوچیک هست که هر کدوم یه شماره‌یِ دقیق دارن.", "میلیون‌ها خونه‌یِ شماره‌دار با آدرسِ دقیق!"),
    ("چرا بهش می‌گن دسترسیِ تصادفی؟ چون سی‌پی‌یو مستقیم می‌پره سرِ هر خونه‌ای که بخواد!", "سی‌پی‌یو مستقیم و درجا می‌پره سرِ آدرسِ دلخواه!"),
    ("فقط یه قانونِ مهم داره: میزِ رَم، حافظه‌یِ موقّته.", "قانونِ مهم: حافظه‌یِ رَم کاملاً موقّته."),
    ("یعنی به‌محضِ اینکه برق قطع بشه یا سیستم خاموش بشه، رویِ میز کامل پاک می‌شه.", "با قطعِ برق، رویِ میزِ رَم کامل پاک می‌شه."),

    # --- Ch.4 (18..24): How Stack & Heap Relate to RAM! ---
    ("حالا می‌رسیم به سؤالِ طلایی: پس اِستَک و هیپ کجایِ این ماجرا هستن؟", "سؤالِ طلایی: پس اِستَک و هیپ کجایِ کارن؟"),
    ("خیلی دقت کن: اِستَک و هیپ، قطعه‌هایِ سخت‌افزاریِ جدا از رَم نیستن!", "استک و هیپ، قطعه‌یِ سخت‌افزاریِ جدا نیستن!"),
    ("هر دویِ این‌ها، دقیقاً داخلِ همین حافظه‌یِ رَم زندگی می‌کنن!", "هر دوشون دقیقاً داخلِ همین رَم زندگی می‌کنن!"),
    ("وقتی یه برنامه اجرا می‌شه، رَم یه بُرشِ اختصاصی از میز رو می‌ده به اون برنامه.", "رَم یک بُرشِ اختصاصی به برنامه‌یِ در حالِ اجرا می‌ده."),
    ("پایینِ این بُرش، کدهایِ برنامه و متغیرهایِ ثابت می‌شینن.", "پایینِ بُرش: کدهایِ برنامه و متغیرهایِ ثابت."),
    ("و فضایِ بازِ بالایی، تقسیم می‌شه بینِ دو بخشِ هوشمند: اِستَک و هیپ!", "فضایِ اصلی تقسیم می‌شه بینِ دو بخش: استک و هیپ!"),
    ("اِستَک از بالا به پایین رشد می‌کنه، و هیپ از پایین به بالا میاد.", "استک از بالا به پایین میاد، و هیپ از پایین به بالا!"),

    # --- Ch.5 (25..32): Deep Dive into STACK (LIFO + Ultra Fast + Auto Pop) ---
    ("بیا اول بریم سراغِ اِستَک؛ یعنی بخشِ فوق‌العاده منظم و سریعِ رَم.", "بخشِ اول: حافظه‌یِ استک، منظم و فوق‌سریع!"),
    ("اِستَک دقیقاً مثلِ دسته‌یِ سینی‌هایِ رویِ هم تویِ یک کافه‌ست.", "استک دقیقاً مثلِ سینی‌هایِ چیده‌شده رویِ همه."),
    ("قانونش ساده‌ست: آخرین سینی‌ای که می‌ذاری بالا، اولین سینی‌ایه که برمی‌داری!", "آخرین ورودی به استک، اولین خروجیه!"),
    ("هر وقت برنامه‌ت یه تابع رو صدا می‌زنه، یه سینیِ جدید میاد رویِ اِستَک.", "با اجرایِ هر تابع، یک سینیِ تازه میاد رویِ استک."),
    ("عددهایِ ساده و متغیرهایِ کوچیکِ اون تابع، مرتب می‌رن داخلِ همین سینی.", "متغیرهایِ ساده و کوچیک، می‌رن داخلِ همین سینی."),
    ("یه اشاره‌گرِ تندوتیز هم همیشه دقیقاً نوکِ آخرین سینی رو نشون می‌ده.", "اشاره‌گرِ استک، همیشه نوکِ آخرین سینی رو داره."),
    ("قشنگ‌ترین جاش اینجاست: به‌محضِ اینکه کارِ اون تابع تموم بشه،", "به‌محضِ اینکه کارِ اون تابع تموم بشه،"),
    ("سینیِ بالایی خودبه‌خود در یک میلیاردمِ ثانیه پاک می‌شه و می‌پره بیرون!", "سینیِ بالایی خودبه‌خود و درجا پاک می‌شه!"),

    # --- Ch.6 (33..37): Why Stack Alone Is Not Enough ---
    ("شاید بپرسی: وقتی اِستَک انقدر سریع و تمیزه، چرا اصلاً به هیپ نیاز داریم؟", "وقتی استک انقدر سریعه، چرا به هیپ نیاز داریم؟"),
    ("چون اِستَک یه محدودیتِ سفت‌وسخت داره!", "چون استک یک محدودیتِ سفت‌وسخت داره!"),
    ("اِستَک فقط داده‌هایی رو قبول می‌کنه که اندازه‌شون از قبل، دقیق و کوچیک باشه.", "اندازه‌یِ داده تو استک باید از قبل معلوم و کوچیک باشه."),
    ("اما اگه کاربر وسطِ برنامه، یه عکسِ بزرگ آپلود کنه چی؟", "اما اگه کاربر یه عکسِ سنگین آپلود کنه چی؟"),
    ("یا یه لیستِ پیام بسازه که هر لحظه بزرگ‌تر می‌شه؟ اینجا اِستَک جا نداره!", "یا لیستی که مدام بزرگ‌تر می‌شه؟ استک جا نداره!"),

    # --- Ch.7 (38..43): Deep Dive into HEAP (Open Dynamic Warehouse) ---
    ("اینجاست که قهرمانِ دوم میاد وسط: یعنی حافظه‌یِ هیپ!", "قهرمانِ دوم وارد می‌شه: حافظه‌یِ هیپ!"),
    ("هیپ مثلِ یک انبارِ بزرگ، باز و کاملاً منعطف داخلِ رَمه.", "هیپ مثلِ یک انبارِ بزرگ و منعطف داخلِ رَمه."),
    ("هر وقت وسطِ اجرایِ برنامه، به فضایِ بزرگ یا متغیر نیاز داشته باشی،", "هر وقت به فضایِ بزرگ یا قابلِ تغییر نیاز داری،"),
    ("هیپ می‌گرده، یه جایِ خالی به اندازه‌یِ دلخواهت پیدا می‌کنه و تحویلت می‌ده.", "هیپ هر چقدر جا بخوای، وسطِ اجرا بهت می‌ده."),
    ("داده‌هایِ داخلِ هیپ، با تموم شدنِ یک تابع خودبه‌خود پاک نمی‌شن و زنده می‌مونن.", "داده‌هایِ هیپ بعد از پایانِ تابع هم زنده می‌مونن."),
    ("البته گشتن دنبالِ جایِ خالی تویِ این انبارِ بزرگ، کمی از اِستَک زمان‌برتره.", "پیدا کردنِ جا تو هیپ، کمی از استک زمان‌برتره."),

    # --- Ch.8 (44..50): How Stack & Heap Connect Together (Pointer / Reference) ---
    ("حالا قشنگ‌ترین رازِ برنامه‌نویسی رو ببین: اِستَک و هیپ چطوری با هم کار می‌کنن؟", "رازِ طلایی: استک و هیپ چطور با هم کار می‌کنن؟"),
    ("فرض کن برنامه‌ت یه پروفایلِ بزرگِ کاربری می‌سازه.", "فرض کن برنامه یک پروفایلِ بزرگِ کاربری می‌سازه."),
    ("خودِ این پروفایلِ سنگین، می‌ره داخلِ انبارِ هیپ، مثلاً تویِ خونه‌یِ هفت‌اِف‌چهل.", "خودِ جسمِ سنگین می‌ره داخلِ انبارِ هیپ."),
    ("ولی سی‌پی‌یو برایِ اینکه پیداش کنه، کلِّ پروفایل رو نمیاره رویِ اِستَک!", "کلِّ پروفایلِ سنگین نمیاد رویِ سینیِ استک!"),
    ("به‌جاش، یه برگه‌یِ رسیدِ کوچیک که روش فقط آدرسِ اون خونه نوشته شده،", "فقط یک رسیدِ کوچیک شاملِ «آدرسِ خونه»،"),
    ("می‌ذاره رویِ سینیِ اِستَک، درست جلویِ دستِ سی‌پی‌یو!", "می‌شینه رویِ سینیِ استک، دمِ دستِ سی‌پی‌یو!"),
    ("به این رسیدِ آدرس می‌گن پوینتِر یا رِفرِنس؛ پلی که اِستَک رو به هیپ وصل می‌کنه!", "به این رسید می‌گن پوینتر؛ پلِ بینِ استک و هیپ!"),

    # --- Ch.9 (51..53): Bug #1 — Stack Overflow ---
    ("حالا دو تا خطایِ معروفِ دنیایِ کامپیوتر هم مثلِ روز برات روشن می‌شه!", "حالا دو خطایِ معروفِ کامپیوتر برات روشن می‌شه!"),
    ("اولی: اِستَک اُوِرفلو! وقتی یه تابع اشتباهی بی‌نهایت بار خودش رو صدا بزنه،", "استک اورفلو: وقتی تابع بی‌نهایت بار تکرار بشه،"),
    ("سینی‌ها انقدر رویِ هم تلنبار می‌شن تا سقفِ اِستَک می‌ترکه و برنامه متوقف می‌شه!", "سینی‌ها از سقفِ استک رد می‌شن و برنامه می‌ترکه!"),

    # --- Ch.10 (54..56): Bug #2 — Memory Leak & Garbage Collector ---
    ("و دومی: نشتِ حافظه یا مِموری لیک تویِ هیپ!", "خطایِ دوم: نشتِ حافظه یا مِموری لیک در هیپ!"),
    ("اگه رسیدِ رویِ اِستَک پاک بشه، ولی جسمِ بزرگ تویِ هیپ بی‌صاحب جا بمونه، رَم پُر می‌شه؛", "اگه رسید پاک بشه ولی جسم تو هیپ جا بمونه، رَم پر می‌شه؛"),
    ("مگر اینکه خودت پاکش کنی، یا رفتگرِ هوشمندِ حافظه بیاد و تمیزش کنه.", "که رفتگرِ هوشمندِ حافظه میاد و تمیزش می‌کنه."),

    # --- Ch.11 (57..59): Grand Summary Matrix & Lightbulb Takeaway ---
    ("پس خلاصه‌یِ طلاییِ کلِّ این سفر این شد:", "خلاصه‌یِ طلاییِ کلِّ ماجرایِ حافظه:"),
    ("رَم میزِ کارِ موقّتِ سی‌پی‌یوئه؛ اِستَک سینی‌هایِ تند و منظمشه برایِ داده‌هایِ کوچیک،", "رَم میزِ کاره؛ استک سینیِ تندِ داده‌هایِ کوچیکه،"),
    ("و هیپ انبارِ آزاد و بزرگشه برایِ داده‌هایِ سنگین که با آدرس به اِستَک وصل می‌شن.", "و هیپ انبارِ داده‌هایِ بزرگه که با آدرس وصل می‌شه!"),
]

# Chapter boundary & synchronized gentle Foley cues
SFX_CUE_MAP = [
    ("ch1_q",     0, 2, "tick",   0.00),
    ("ch2_hw",    5, 0, "whoosh", -0.05),
    ("ch2_cpu",   9, 0, "tick",   0.00),
    ("ch3_ram",  11, 0, "whoosh", -0.05),
    ("ch3_jump", 15, 0, "pop",    0.00),
    ("ch3_off",  17, 0, "shimmer",0.00),
    ("ch4_map",  18, 0, "whoosh", -0.05),
    ("ch4_split",23, 0, "pop",    0.00),
    ("ch5_stk",  25, 0, "whoosh", -0.05),
    ("ch5_push", 28, 0, "tick",   0.00),
    ("ch5_pop",  32, 0, "pop",    0.00),
    ("ch6_lim",  33, 0, "whoosh", -0.05),
    ("ch6_big",  36, 0, "thud",   0.00),
    ("ch7_heap", 38, 0, "whoosh", -0.05),
    ("ch7_alloc",41, 0, "pop",    0.00),
    ("ch8_ptr",  44, 0, "whoosh", -0.05),
    ("ch8_wire", 48, 0, "shimmer",0.00),
    ("ch9_ovf",  51, 0, "whoosh", -0.05),
    ("ch9_boom", 52, 2, "thud",   0.00),
    ("ch10_leak",54, 0, "whoosh", -0.05),
    ("ch10_gc",  56, 0, "shimmer",0.00),
    ("ch11_sum", 57, 0, "whoosh", -0.05),
]


def _get_chapter_bounds(tc: dict, sub_lines: list[dict], total_dur: float) -> list[float]:
    def t_seg(idx: int, fallback: float) -> float:
        if idx < len(sub_lines):
            return float(sub_lines[idx]["start"])
        return fallback

    s_end_vo = float(sub_lines[-1]["end"]) + 0.35 if sub_lines else (total_dur - 3.8)
    return [
        0.0,
        tc.get("ch2_hw",   t_seg(5,  22.0)),   # B[1]: S02 SSD vs CPU
        tc.get("ch3_ram",  t_seg(11, 48.0)),   # B[2]: S03 RAM Workbench
        tc.get("ch4_map",  t_seg(18, 78.0)),   # B[3]: S04 RAM Internal Map
        tc.get("ch5_stk",  t_seg(25, 108.0)),  # B[4]: S05 Stack LIFO Trays
        tc.get("ch6_lim",  t_seg(33, 140.0)),  # B[5]: S06 Stack Limitation
        tc.get("ch7_heap", t_seg(38, 162.0)),  # B[6]: S07 Heap Open Warehouse
        tc.get("ch8_ptr",  t_seg(44, 188.0)),  # B[7]: S08 Pointer Connection
        tc.get("ch9_ovf",  t_seg(51, 216.0)),  # B[8]: S09 Stack Overflow
        tc.get("ch10_leak",t_seg(54, 228.0)),  # B[9]: S10 Memory Leak & GC
        tc.get("ch11_sum", t_seg(57, 240.0)),  # B[10]: S11 Summary Matrix
        min(total_dur - 3.4, s_end_vo),        # B[11]: S12 Sapphire Pill CTA
        total_dur + 0.2,
    ]


def _draw_chapter_pill(cb, ce, sharp_texts: list, fonts: FontBank, badge_txt: str, al: float, col_mid=C_CYAN_MID):
    draw_laser_glass_card(cb, ce, 310, 128, 460, 62, 31, al * 0.94, col_mid, C_CYAN_CORE, 0.25, False, 0.86)
    sharp_texts.append((get_fitted_text_sprite(badge_txt, fonts.med_32, 410, (175, 232, 255, 255)), 540, 159, al))


def render_masterclass_scene(
    t: float,
    total_dur: float,
    tc: dict,
    sub_lines: list[dict],
    fonts: FontBank,
    surf_base: cairo.ImageSurface,
    cb: cairo.Context,
    surf_emissive: cairo.ImageSurface,
    ce: cairo.Context,
) -> bytes:
    # Clear dual RGBA surfaces
    cb.save(); cb.set_operator(cairo.OPERATOR_CLEAR); cb.paint(); cb.restore()
    ce.save(); ce.set_operator(cairo.OPERATOR_CLEAR); ce.paint(); ce.restore()

    sharp_texts = []
    emissive_texts = []
    B = _get_chapter_bounds(tc, sub_lines, total_dur)
    grid_strength = 1.0

    # =========================================================================
    # S01 (B[0]..B[1]): 3D Confused Character at Desk + Live Roadmap Badges
    # =========================================================================
    if t < B[1]:
        dur = max(1.0, B[1] - B[0])
        al = clamp(t / 0.45) * clamp((B[1] - t) / 0.35)
        grid_strength = 0.72
        q_pop = clamp((t - 0.6) / 0.8)
        draw_sapphire_desk_scene_side(cb, ce, t, al, q_pop)

        # Header title
        s_t, e_t = get_multitone_persian_sprite("کالبدشکافیِ کاملِ RAM ، Stack و Heap", [("RAM", CYAN_RGB), ("Stack", CYAN_RGB), ("Heap", GREEN_RGB)], fonts.bold_52, 920)
        sharp_texts.append((s_t, 540, 235, al))
        emissive_texts.append((e_t, 540, 235, al * 0.85))
        sharp_texts.append((get_fitted_text_sprite("آموزشِ بصریِ قدم‌به‌قدم با نقاشیِ زنده", fonts.med_36, 860, (175, 225, 255, 240)), 540, 318, al * clamp((t - 1.5) / 0.7)))

        # 3 live-sketched topic pills appearing sequentially at y=405
        pills = [
            ("1. RAM", 115, C_AMBER, AMBER_RGB, 0.38),
            ("2. Stack", 415, C_CYAN_MID, CYAN_RGB, 0.54),
            ("3. Heap", 715, C_GREEN, GREEN_RGB, 0.70),
        ]
        for lbl, px, cm, crgb, u0 in pills:
            pu = clamp((t - dur * u0) / 1.4)
            if pu > 0.01:
                draw_sketch_glass_box(cb, ce, px, 392, 250, 86, 20, pu, cm, C_CYAN_CORE, al, 0.90, t * 0.16)
                if pu > 0.45:
                    tu = ease_out_cubic(clamp((pu - 0.45) / 0.55))
                    sharp_texts.append((get_fitted_text_sprite(lbl, fonts.bold_36, 210, (*crgb, 255)), px + 125, 435, al * tu))

    # =========================================================================
    # S02 (B[1]..B[2]): Hardware Trio Sketch — SSD Warehouse vs Ultra-Fast CPU
    # =========================================================================
    elif t < B[2]:
        tl = t - B[1]
        dur = max(1.0, B[2] - B[1])
        al = clamp(tl / 0.35) * clamp((B[2] - t) / 0.35)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "فصلِ ۱ • کارگاهِ کامپیوتر", al)
        s_h, e_h = get_multitone_persian_sprite("چرا CPU نمی‌تونه مستقیم با هارد کار کنه؟", [("CPU", CYAN_RGB), ("هارد", AMBER_RGB)], fonts.bold_44, 920)
        sharp_texts.append((s_h, 540, 258, al))
        emissive_texts.append((e_h, 540, 258, al * 0.8))

        # Left card: SSD / Hard Permanent Warehouse (sequential single-stylus sketch!)
        p_ssd = clamp((tl - 0.3) / 1.6)
        draw_sketch_glass_box(cb, ce, 78, 415, 405, 595, 26, p_ssd, C_AMBER, (1.0, 0.90, 0.62), al, 0.88, t * 0.12, show_pen=(p_ssd < 0.98))
        p_cyl = clamp((tl - 1.95) / 1.9)
        draw_sketch_storage_cylinder(cb, ce, 280, 535, 108, 34, 185, p_cyl, C_AMBER, (1.0, 0.92, 0.65), al, show_pen=(0.02 < p_cyl < 0.98))
        if p_ssd > 0.55:
            u1 = clamp((p_ssd - 0.55) / 0.45)
            sharp_texts.extend([
                (get_fitted_text_sprite("SSD / Hard", fonts.bold_44, 350, (*AMBER_RGB, 255)), 280, 822, al * u1),
                (get_fitted_text_sprite("انبارِ دائمی و بزرگ", fonts.bold_36, 350), 280, 888, al * u1),
                (get_fitted_text_sprite("بدونِ برق هم پاک نمی‌شه", fonts.reg_26, 360, (205, 225, 245, 230)), 280, 948, al * u1),
            ])

        # Right card: CPU Ultra-Fast Processor (sequential single-stylus sketch!)
        t_cpu = max(4.0, tc.get("ch2_cpu", B[1] + dur * 0.55) - B[1] - 0.6)
        p_cpu = clamp((tl - t_cpu) / 1.5)
        if p_cpu > 0.01:
            draw_sketch_glass_box(cb, ce, 597, 415, 405, 595, 26, p_cpu, C_CYAN_MID, C_CYAN_CORE, al, 0.88, -t * 0.14, show_pen=(p_cpu < 0.98))
            p_die = clamp((tl - (t_cpu + 1.55)) / 1.8)
            draw_sketch_cpu_die(cb, ce, 800, 625, 188, p_die, t, al, show_pen=(0.02 < p_die < 0.98))
            if p_cpu > 0.55:
                u2 = clamp((p_cpu - 0.55) / 0.45)
                sharp_texts.extend([
                    (get_fitted_text_sprite("CPU", fonts.bold_44, 350, (*CYAN_RGB, 255)), 800, 822, al * u2),
                    (get_fitted_text_sprite("نجّارِ فوق‌سریع", fonts.bold_36, 350), 800, 888, al * u2),
                    (get_fitted_text_sprite("میلیاردها عملیات در ثانیه", fonts.reg_26, 360, (195, 235, 255, 235)), 800, 948, al * u2),
                ])

        # Bottleneck red warning bridge at bottom (when slow bottleneck is explained)
        p_bot = clamp((tl - (dur * 0.74)) / 1.8)
        if p_bot > 0.01:
            draw_sketch_bezier_wire(cb, ce, (280, 1025), (380, 1155), (700, 1155), (800, 1025), p_bot, 0.0, C_RED, (1.0, 0.72, 0.74), 4.4, al)
            draw_sketch_glass_box(cb, ce, 140, 1145, 800, 132, 22, p_bot, C_RED, (1.0, 0.70, 0.72), al, 0.92, t * 0.2, show_pen=False)
            if p_bot > 0.45:
                ub = clamp((p_bot - 0.45) / 0.55)
                sharp_texts.extend([
                    (get_fitted_text_sprite("گلوگاهِ سرعت: فاصله‌یِ هارد تا CPU خیلی کُنده!", fonts.bold_36, 740, (*RED_RGB, 255)), 540, 1192, al * ub),
                    (get_fitted_text_sprite("نیاز به یک «میزِ کارِ فوری» درست بغلِ دستِ CPU داریم", fonts.reg_26, 740, (235, 242, 255, 235)), 540, 1242, al * ub),
                ])

    # =========================================================================
    # S03 (B[2]..B[3]): Live-Sketching RAM (Numbered Cells + Random Access + Volatile)
    # =========================================================================
    elif t < B[3]:
        tl = t - B[2]
        dur = max(1.0, B[3] - B[2])
        al = clamp(tl / 0.35) * clamp((B[3] - t) / 0.35)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "فصلِ ۲ • حافظه‌یِ RAM چیست؟", al)
        s_h, e_h = get_multitone_persian_sprite("RAM = میزِ کارِ شماره‌دار و موقّتِ CPU", [("RAM", CYAN_RGB), ("موقّتِ", AMBER_RGB)], fonts.bold_44, 920)
        sharp_texts.append((s_h, 540, 255, al))
        emissive_texts.append((e_h, 540, 255, al * 0.82))

        # Volatility dim simulation near end of chapter (`ch3_off`)
        t_off_rel = tc.get("ch3_off", B[2] + dur * 0.80) - B[2]
        power_off_dip = 0.0
        if tl > t_off_rel + 0.3:
            u_off = clamp((tl - (t_off_rel + 0.3)) / 1.8)
            power_off_dip = math.sin(u_off * math.pi) * 0.78

        ram_al = al * (1.0 - power_off_dip * 0.75)

        # Outer RAM Workbench (finishes at tl=1.8s, then cells sketch one-by-one!)
        p_wb = clamp((tl - 0.25) / 1.55)
        draw_sketch_glass_box(cb, ce, 82, 345, 916, 675, 28, p_wb, C_CYAN_MID, C_CYAN_CORE, ram_al, 0.90, t * 0.14)
        if p_wb > 0.45:
            sharp_texts.append((get_fitted_text_sprite("میزِ کارِ پرسرعتِ RAM (Random Access Memory)", fonts.bold_36, 840, (*CYAN_RGB, 255)), 540, 405, ram_al))

        # 8 Numbered Memory Address Cells inside RAM (strictly sequential single-stylus!)
        addrs = ["0x01", "0x02", "0x03", "0x04", "0x05", "0x06", "0x07", "0x08"]
        vals  = ["42",   "App",  "Pic",  "99",   "User", "1080", "Key",  "Audio"]
        t_jump_rel = tc.get("ch3_jump", B[2] + dur * 0.52) - B[2]
        jump_active = clamp((tl - t_jump_rel) / 0.7)

        for idx in range(8):
            r_i, c_i = divmod(idx, 4)
            cx0 = 122 + c_i * 214
            cy0 = 468 + r_i * 238
            p_cell = clamp((tl - 1.85 - idx * 0.48) / 0.46)
            if p_cell <= 0.01:
                continue
            is_target = (idx == 3 and jump_active > 0.05)
            cm = C_GREEN if is_target else C_CYAN_MID
            cc = (0.80, 1.0, 0.88) if is_target else C_CYAN_CORE
            draw_sketch_glass_box(cb, ce, cx0, cy0, 192, 198, 18, p_cell, cm, cc, ram_al, 0.92, t * 0.2 + idx * 0.1, show_pen=(0.02 < p_cell < 0.98), pen_scale=0.78)
            if p_cell > 0.55:
                uc = clamp((p_cell - 0.55) / 0.45) * (1.0 - power_off_dip * 0.92)
                sharp_texts.append((get_fitted_text_sprite(addrs[idx], fonts.bold_30, 160, (145, 215, 255, 245)), cx0 + 96, cy0 + 48, al * uc))
                v_col = GREEN_RGB if is_target else (245, 250, 255)
                sharp_texts.append((get_fitted_text_sprite(vals[idx], fonts.bold_36, 165, (*v_col, 255)), cx0 + 96, cy0 + 128, al * uc))

        # Direct Random-Access Laser Beam jumping straight from CPU badge to cell 0x04!
        if jump_active > 0.02:
            draw_sketch_glass_box(cb, ce, 300, 1055, 480, 92, 20, jump_active, C_GREEN, (0.82, 1.0, 0.88), al, 0.92, t * 0.25, show_pen=False)
            sharp_texts.append((get_fitted_text_sprite("پرشِ مستقیمِ CPU به خونه‌یِ چهارم (۱ نانوثانیه)", fonts.bold_30, 445, (*GREEN_RGB, 255)), 540, 1101, al * jump_active))
            draw_sketch_bezier_wire(cb, ce, (540, 1055), (680, 960), (858, 820), (858, 666), jump_active, t, C_GREEN, (0.82, 1.0, 0.88), 4.5, ram_al)

        # Volatility warning badge at bottom
        if tl > t_off_rel - 0.4:
            uv = clamp((tl - (t_off_rel - 0.4)) / 0.8)
            draw_sketch_glass_box(cb, ce, 115, 1178, 850, 108, 22, uv, C_AMBER, (1.0, 0.92, 0.65), al, 0.92, t * 0.18, show_pen=False)
            sharp_texts.append((get_fitted_text_sprite("قانونِ مهم: با خاموش شدنِ برق، تمامِ خانه‌هایِ RAM پاک می‌شن!", fonts.bold_30, 800, (*AMBER_RGB, 255)), 540, 1232, al * uv))

    # =========================================================================
    # S04 (B[3]..B[4]): Inside One Program's RAM Slice (Code / Static / Heap / Stack)
    # =========================================================================
    elif t < B[4]:
        tl = t - B[3]
        dur = max(1.0, B[4] - B[3])
        al = clamp(tl / 0.35) * clamp((B[4] - t) / 0.35)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "فصلِ ۳ • ارتباطِ RAM با Stack و Heap", al, C_GREEN)
        s_h, e_h = get_multitone_persian_sprite("هر دو دقیقاً داخلِ همین RAM زندگی می‌کنن!", [("هر دو", GREEN_RGB), ("RAM", CYAN_RGB)], fonts.bold_44, 920)
        sharp_texts.append((s_h, 540, 255, al))
        emissive_texts.append((e_h, 540, 255, al * 0.85))

        # Outer Tall Sapphire Memory Tower representing Program's Slice inside RAM
        p_tower = clamp((tl - 0.4) / 2.2)
        draw_sketch_glass_box(cb, ce, 165, 338, 750, 965, 30, p_tower, C_CYAN_MID, C_CYAN_CORE, al, 0.88, t * 0.12)
        if p_tower > 0.5:
            sharp_texts.append((get_fitted_text_sprite("سهمِ برنامه‌یِ تو از حافظه‌یِ RAM", fonts.bold_36, 680, (190, 235, 255, 255)), 540, 388, al))

        # Bottom 2 static sections: Code (1175..1270) & Global/Static (1068..1162)
        p_low = clamp((tl - 3.2) / 1.8)
        if p_low > 0.01:
            draw_sketch_glass_box(cb, ce, 205, 1176, 670, 94, 16, p_low, (0.35, 0.55, 0.78), C_CYAN_CORE, al, 0.90, 0.1, show_pen=(p_low < 0.96), pen_scale=0.78)
            draw_sketch_glass_box(cb, ce, 205, 1068, 670, 94, 16, clamp(p_low * 1.1 - 0.15), (0.35, 0.55, 0.78), C_CYAN_CORE, al, 0.90, 0.4, show_pen=False)
            if p_low > 0.5:
                sharp_texts.extend([
                    (get_fitted_text_sprite("بخشِ ۱ (Code): دستوراتِ ثابتی که نوشتی", fonts.bold_30, 620, (205, 230, 255, 245)), 540, 1223, al),
                    (get_fitted_text_sprite("بخشِ ۲ (Static): متغیرهایِ ثابت و سراسری", fonts.bold_30, 620, (205, 230, 255, 245)), 540, 1115, al),
                ])

        # Upper dynamic arena: Stack at TOP growing DOWN (438..668) & Heap below growing UP (815..1045)
        t_sp = max(5.2, tc.get("ch4_split", B[3] + dur * 0.55) - B[3] - 0.5)
        p_sh = clamp((tl - t_sp) / 1.8)
        if p_sh > 0.01:
            draw_sketch_glass_box(cb, ce, 205, 438, 670, 218, 20, p_sh, C_CYAN_MID, C_CYAN_CORE, al, 0.92, t * 0.22, show_pen=(p_sh < 0.97))
            p_hp4 = clamp((tl - (t_sp + 1.85)) / 1.8)
            draw_sketch_glass_box(cb, ce, 205, 815, 670, 225, 20, p_hp4, C_GREEN, (0.80, 1.0, 0.88), al, 0.92, -t * 0.22, show_pen=(0.02 < p_hp4 < 0.97))

            if p_sh > 0.5:
                us = clamp((p_sh - 0.5) / 0.5)
                sharp_texts.extend([
                    (get_fitted_text_sprite("STACK (اِستَک) • منظم و فوق‌سریع", fonts.bold_36, 620, (*CYAN_RGB, 255)), 540, 508, al * us),
                    (get_fitted_text_sprite("رشد از بالا به سمتِ پایین (آدرس‌هایِ بالا)", fonts.med_32, 620, (220, 245, 255, 245)), 540, 578, al * us),
                ])
            if p_hp4 > 0.5:
                uh4 = clamp((p_hp4 - 0.5) / 0.5)
                sharp_texts.extend([
                    (get_fitted_text_sprite("HEAP (هیپ) • انبارِ آزاد و منعطف", fonts.bold_36, 620, (*GREEN_RGB, 255)), 540, 888, al * uh4),
                    (get_fitted_text_sprite("رشد از پایین به سمتِ بالا (هر چقدر جا بخوای)", fonts.med_32, 620, (220, 255, 235, 245)), 540, 958, al * uh4),
                ])

            # Animated breathing arrows between Stack ↓ and Heap ↑ in the free middle zone
            bob = math.sin(t * 3.6) * 10.0
            p_arr = clamp((tl - t_sp - 2.6) / 1.2)
            if p_arr > 0.02:
                draw_sketch_bezier_wire(cb, ce, (390, 662), (390, 695), (390, 720), (390, 755 + bob), p_arr, 0.0, C_CYAN_MID, C_CYAN_CORE, 4.6, al, True, False)
                draw_sketch_bezier_wire(cb, ce, (690, 810), (690, 775), (690, 750), (690, 718 - bob), p_arr, 0.0, C_GREEN, (0.80, 1.0, 0.88), 4.6, al, True, False)
                sharp_texts.append((get_fitted_text_sprite("فضایِ آزادِ مشترک", fonts.reg_26, 230, (180, 215, 240, 220)), 540, 740, al * p_arr))

    # =========================================================================
    # S05 (B[4]..B[5]): Deep Dive into STACK — LIFO Cafeteria Trays & Auto Pop!
    # =========================================================================
    elif t < B[5]:
        tl = t - B[4]
        dur = max(1.0, B[5] - B[4])
        al = clamp(tl / 0.35) * clamp((B[5] - t) / 0.35)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "فصلِ ۴ • حافظه‌یِ Stack چطور کار می‌کنه؟", al)
        s_h, e_h = get_multitone_persian_sprite("Stack = سینی‌هایِ رویِ هم (آخرین ورودی، اولین خروجی)", [("Stack", CYAN_RGB), ("آخرین ورودی، اولین خروجی", GREEN_RGB)], fonts.bold_44, 930)
        sharp_texts.append((s_h, 540, 255, al))
        emissive_texts.append((e_h, 540, 255, al * 0.82))

        # Left Panel: Function Call Code Card
        p_code = clamp((tl - 0.5) / 1.8)
        draw_sketch_glass_box(cb, ce, 68, 365, 410, 780, 24, p_code, (0.22, 0.55, 0.88), C_CYAN_CORE, al, 0.90, t * 0.14)
        if p_code > 0.5:
            sharp_texts.extend([
                (get_fitted_text_sprite("اجرایِ توابع", fonts.bold_36, 360, (*CYAN_RGB, 255)), 273, 430, al),
                (get_fitted_text_sprite("func main() {", fonts.bold_30, 360, (235, 245, 255, 255)), 273, 525, al),
                (get_fitted_text_sprite("  x = 2", fonts.reg_30, 340, (175, 225, 255, 245)), 273, 585, al),
                (get_fitted_text_sprite("  calc(5, 10)", fonts.bold_30, 340, (*GREEN_RGB, 255)), 273, 645, al),
                (get_fitted_text_sprite("}", fonts.bold_30, 340, (235, 245, 255, 255)), 273, 705, al),
                (get_fitted_text_sprite("func calc(a, b) {", fonts.bold_30, 360, (*CYAN_RGB, 255)), 273, 815, al),
                (get_fitted_text_sprite("  sum = a + b", fonts.reg_30, 340, (235, 245, 255, 245)), 273, 875, al),
                (get_fitted_text_sprite("  return sum", fonts.bold_30, 340, (*AMBER_RGB, 255)), 273, 935, al),
                (get_fitted_text_sprite("}", fonts.bold_30, 340, (*CYAN_RGB, 255)), 273, 995, al),
            ])

        # Right Panel: Live LIFO Stack Container (512..1012)
        draw_sketch_glass_box(cb, ce, 512, 365, 500, 780, 24, clamp((tl - 0.8) / 1.8), C_CYAN_MID, C_CYAN_CORE, al, 0.88, -t * 0.14)
        if tl > 1.6:
            sharp_texts.append((get_fitted_text_sprite("برجِ سینی‌هایِ Stack (LIFO)", fonts.bold_36, 450, (*CYAN_RGB, 255)), 762, 430, al))

        t_push = max(3.5, tc.get("ch5_push", B[4] + dur * 0.38) - B[4] - 0.4)
        t_pop  = max(t_push + 3.5, tc.get("ch5_pop", B[4] + dur * 0.84) - B[4] - 0.3)

        # Tray #1 (Bottom): main() -> x = 2
        p_t1 = clamp((tl - 2.2) / 1.4)
        if p_t1 > 0.01:
            draw_sketch_glass_box(cb, ce, 548, 945, 428, 155, 18, p_t1, C_CYAN_MID, C_CYAN_CORE, al, 0.94, 0.2, show_pen=(p_t1 < 0.96))
            if p_t1 > 0.5:
                sharp_texts.extend([
                    (get_fitted_text_sprite("سینیِ ۱: main()", fonts.bold_30, 380, (*CYAN_RGB, 255)), 762, 995, al),
                    (get_fitted_text_sprite("x = 2   (۸ بایت)", fonts.reg_30, 380, (235, 248, 255, 245)), 762, 1052, al),
                ])

        # Tray #2 (Stacked on top, then POPPED automatically at t_pop!): calc(a=5, b=10)
        p_in2 = clamp((tl - t_push) / 1.3)
        p_out2 = clamp((tl - t_pop) / 0.65)
        t2_al = p_in2 * (1.0 - ease_in_out_cubic(p_out2))
        if t2_al > 0.02:
            y_slide = -65.0 * ease_in_out_cubic(p_out2) - 40.0 * (1.0 - ease_out_cubic(p_in2))
            draw_sketch_glass_box(cb, ce, 548, 755 + y_slide, 428, 168, 18, p_in2, C_GREEN, (0.82, 1.0, 0.88), al * t2_al, 0.95, t * 0.25, show_pen=(p_in2 < 0.96 and p_out2 < 0.01))
            if p_in2 > 0.45:
                sharp_texts.extend([
                    (get_fitted_text_sprite("سینیِ ۲: calc()  [PUSH]", fonts.bold_30, 390, (*GREEN_RGB, 255)), 762, 805 + y_slide, al * t2_al),
                    (get_fitted_text_sprite("a = 5 , b = 10 , sum = 15", fonts.reg_30, 390, (240, 255, 245, 250)), 762, 868 + y_slide, al * t2_al),
                ])

        # Live Stack Pointer (SP) glowing badge tracking top active tray!
        if p_t1 > 0.7:
            sp_y = 945.0 - 190.0 * (ease_out_cubic(p_in2) * (1.0 - ease_in_out_cubic(p_out2)))
            draw_laser_glass_card(cb, ce, 558, sp_y - 84, 408, 64, 16, al, C_AMBER, (1.0, 0.92, 0.65), t * 0.3, False, 0.92)
            sp_lbl = "پاک‌سازیِ خودکار در ۱ نانوثانیه!" if p_out2 > 0.25 else "اشاره‌گرِ SP رویِ نوکِ فعلیِ Stack"
            sharp_texts.append((get_fitted_text_sprite(sp_lbl, fonts.bold_30, 380, (*AMBER_RGB, 255)), 762, sp_y - 52, al))

        # Bottom takeaway bar
        draw_laser_glass_card(cb, ce, 95, 1182, 890, 102, 22, al * clamp((tl - 2.8) / 0.9), C_CYAN_MID, C_CYAN_CORE, 0.5, False, 0.90)
        sharp_texts.append((get_fitted_text_sprite("مزیتِ طلاییِ Stack: سرعتِ فوق‌العاده بالا + پاک‌سازیِ ۱۰۰٪ خودکار!", fonts.bold_30, 840, (215, 245, 255, 255)), 540, 1233, al * clamp((tl - 2.8) / 0.9)))

    # =========================================================================
    # S06 (B[5]..B[6]): Why Stack Alone Fails (Fixed Narrow Slot vs Big Dynamic Data)
    # =========================================================================
    elif t < B[6]:
        tl = t - B[5]
        dur = max(1.0, B[6] - B[5])
        al = clamp(tl / 0.35) * clamp((B[6] - t) / 0.35)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "فصلِ ۵ • محدودیتِ بزرگِ Stack", al, C_RED)
        s_h, e_h = get_multitone_persian_sprite("چرا همه‌چیز رو نمی‌ذاریم داخلِ Stack؟", [("Stack", CYAN_RGB)], fonts.bold_44, 920)
        sharp_texts.append((s_h, 540, 258, al))
        emissive_texts.append((e_h, 540, 258, al * 0.82))

        # Left Card: Tiny Fixed-Size Stack Slot (Accepts small fixed int, rejects big dynamic)
        p_l = clamp((tl - 0.4) / 1.8)
        draw_sketch_glass_box(cb, ce, 85, 395, 910, 295, 24, p_l, C_CYAN_MID, C_CYAN_CORE, al, 0.88, t * 0.15)
        if p_l > 0.45:
            draw_glass_status_medallion(cb, ce, 900, 542, 42, True, al, clamp((p_l - 0.45) / 0.5))
            sharp_texts.extend([
                (get_fitted_text_sprite("قانونِ سخت‌گیرانه‌یِ Stack:", fonts.bold_36, 720, (*CYAN_RGB, 255)), 465, 468, al),
                (get_fitted_text_sprite("اندازه‌یِ داده باید «قبل از اجرا» دقیق و کوچک معلوم باشد", fonts.med_32, 730), 465, 542, al),
                (get_fitted_text_sprite("مثالِ مجاز:   age = 27   |   price = 99.5   |   isLogin = true", fonts.reg_26, 720, (175, 230, 255, 235)), 465, 616, al),
            ])

        # Bottom Rejected Dynamic Data Card (Crimson X + Live Sketch)
        t_big = max(2.8, tc.get("ch6_big", B[5] + dur * 0.55) - B[5] - 0.4)
        p_b = clamp((tl - t_big) / 1.9)
        if p_b > 0.01:
            draw_sketch_glass_box(cb, ce, 85, 745, 910, 465, 26, p_b, C_RED, (1.0, 0.72, 0.74), al, 0.90, -t * 0.18)
            if p_b > 0.45:
                ub = clamp((p_b - 0.45) / 0.55)
                draw_glass_status_medallion(cb, ce, 900, 855, 46, False, al * ub, ub)
                sharp_texts.extend([
                    (get_fitted_text_sprite("داده‌هایِ بزرگ و غیرقابلِ پیش‌بینی:", fonts.bold_36, 700, (*RED_RGB, 255)), 460, 835, al * ub),
                    (get_fitted_text_sprite("• عکس یا ویدیویی که کاربر وسطِ برنامه آپلود می‌کنه (8 MB)", fonts.med_32, 790), 520, 945, al * ub),
                    (get_fitted_text_sprite("• لیستِ پیام‌ها و کامنت‌هایی که هر لحظه بزرگ‌تر می‌شن", fonts.med_32, 790), 520, 1025, al * ub),
                    (get_fitted_text_sprite("• داده‌ای که باید بعد از پایانِ تابع هم زنده بمونه!", fonts.bold_30, 790, (*AMBER_RGB, 255)), 520, 1115, al * ub),
                ])

    # =========================================================================
    # S07 (B[6]..B[7]): Deep Dive into HEAP — Open Dynamic Warehouse inside RAM
    # =========================================================================
    elif t < B[7]:
        tl = t - B[6]
        dur = max(1.0, B[7] - B[6])
        al = clamp(tl / 0.35) * clamp((B[7] - t) / 0.35)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "فصلِ ۶ • حافظه‌یِ Heap چیست؟", al, C_GREEN)
        s_h, e_h = get_multitone_persian_sprite("Heap = انبارِ بزرگ، آزاد و کاملاً منعطفِ RAM", [("Heap", GREEN_RGB), ("RAM", CYAN_RGB)], fonts.bold_44, 920)
        sharp_texts.append((s_h, 540, 255, al))
        emissive_texts.append((e_h, 540, 255, al * 0.85))

        # Large Open Emerald Warehouse Grid
        p_wh = clamp((tl - 0.4) / 2.2)
        draw_sketch_glass_box(cb, ce, 82, 348, 916, 760, 28, p_wh, C_GREEN, (0.80, 1.0, 0.88), al, 0.88, t * 0.12)
        if p_wh > 0.45:
            sharp_texts.append((get_fitted_text_sprite("فضایِ آزادِ Heap (تخصیصِ پویا در زمانِ اجرا)", fonts.bold_36, 840, (*GREEN_RGB, 255)), 540, 410, al))

        # Variable-sized dynamic allocations sketched sequentially inside Heap!
        blocks = [
            (125, 475, 485, 225, "0x7F40  |  User Profile", "نام، بیو، تنظیماتِ ماندگار", C_GREEN, GREEN_RGB, 2.25),
            (638, 475, 318, 225, "0x8B10  |  Audio", "ویسِ ۲ دقیقه‌ای", C_CYAN_MID, CYAN_RGB, 3.65),
            (125, 735, 565, 320, "0x9A00  |  4K Photo (8 MB)", "عکسِ سنگین با اندازه‌یِ متغیر در زمانِ اجرا", C_AMBER, AMBER_RGB, 5.05),
            (718, 735, 238, 320, "FREE SPACE", "آماده‌یِ رزرو", (0.28, 0.42, 0.56), (170, 205, 235), 6.45),
        ]
        for bx, by, bw, bh, b_title, b_sub, b_cm, b_rgb, t_d in blocks:
            pb = clamp((tl - t_d) / 1.32)
            if pb <= 0.01:
                continue
            draw_sketch_glass_box(cb, ce, bx, by, bw, bh, 20, pb, b_cm, C_CYAN_CORE, al, 0.92, t * 0.18 + bx * 0.001, show_pen=(0.02 < pb < 0.98), pen_scale=0.82)
            if pb > 0.5:
                ub = clamp((pb - 0.5) / 0.5)
                sharp_texts.extend([
                    (get_fitted_text_sprite(b_title, fonts.bold_30, bw - 34, (*b_rgb, 255)), bx + bw * 0.5, by + bh * 0.36, al * ub),
                    (get_fitted_text_sprite(b_sub, fonts.reg_26, bw - 34, (230, 242, 255, 240)), bx + bw * 0.5, by + bh * 0.68, al * ub),
                ])

        # Trade-off footer badge
        p_ft = clamp((tl - (dur * 0.72)) / 1.2)
        if p_ft > 0.01:
            draw_laser_glass_card(cb, ce, 95, 1148, 890, 125, 22, al * p_ft, C_AMBER, (1.0, 0.92, 0.65), 0.3, False, 0.92)
            sharp_texts.extend([
                (get_fitted_text_sprite("بهایِ این انعطاف: گشتن دنبالِ جایِ خالی در Heap کمی از Stack کندتره", fonts.bold_30, 840, (*AMBER_RGB, 255)), 540, 1190, al * p_ft),
                (get_fitted_text_sprite("و داده تا وقتی خودت یا Garbage Collector پاکش نکنه، باقی می‌مونه!", fonts.reg_26, 840, (235, 245, 255, 240)), 540, 1240, al * p_ft),
            ])

    # =========================================================================
    # S08 (B[7]..B[8]): THE GOLDEN BRIDGE — How Stack & Heap Work Together via Pointer!
    # =========================================================================
    elif t < B[8]:
        tl = t - B[7]
        dur = max(1.0, B[8] - B[7])
        al = clamp(tl / 0.35) * clamp((B[8] - t) / 0.35)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "فصلِ ۷ • پلِ ارتباطیِ Stack و Heap", al, C_GREEN)
        s_h, e_h = get_multitone_persian_sprite("رسیدِ آدرس (Pointer) در Stack و جسمِ بزرگ در Heap", [("Pointer", AMBER_RGB), ("Stack", CYAN_RGB), ("Heap", GREEN_RGB)], fonts.bold_44, 930)
        sharp_texts.append((s_h, 540, 255, al))
        emissive_texts.append((e_h, 540, 255, al * 0.85))

        # Left Column: STACK (sequential sketch: 0.4..1.8)
        p_st = clamp((tl - 0.4) / 1.4)
        draw_sketch_glass_box(cb, ce, 68, 365, 392, 735, 24, p_st, C_CYAN_MID, C_CYAN_CORE, al, 0.88, t * 0.14)
        if p_st > 0.45:
            sharp_texts.extend([
                (get_fitted_text_sprite("STACK (سینیِ سریع)", fonts.bold_36, 350, (*CYAN_RGB, 255)), 264, 428, al),
                (get_fitted_text_sprite("دمِ دستِ CPU", fonts.reg_26, 340, (180, 228, 255, 230)), 264, 478, al),
            ])

        # Right Column: HEAP (sequential sketch: 1.85..3.25)
        p_hp = clamp((tl - 1.85) / 1.4)
        draw_sketch_glass_box(cb, ce, 558, 365, 454, 735, 24, p_hp, C_GREEN, (0.80, 1.0, 0.88), al, 0.88, -t * 0.14)
        if p_hp > 0.45:
            sharp_texts.extend([
                (get_fitted_text_sprite("HEAP (انبارِ بزرگ)", fonts.bold_36, 410, (*GREEN_RGB, 255)), 785, 428, al),
                (get_fitted_text_sprite("محلِ نگهداریِ جسمِ سنگین", fonts.reg_26, 410, (195, 250, 215, 230)), 785, 478, al),
            ])

        # Heavy User Object inside Heap at 0x7F40 (3.3..4.8)
        p_obj = clamp((tl - 3.3) / 1.5)
        if p_obj > 0.01:
            draw_sketch_glass_box(cb, ce, 592, 565, 386, 465, 22, p_obj, C_GREEN, (0.82, 1.0, 0.88), al, 0.94, t * 0.2, show_pen=(0.02 < p_obj < 0.98))
            if p_obj > 0.5:
                sharp_texts.extend([
                    (get_fitted_text_sprite("ADDR:  0x7F40", fonts.bold_30, 345, (*AMBER_RGB, 255)), 785, 628, al),
                    (get_fitted_text_sprite("پروفایلِ کاملِ کاربر", fonts.bold_36, 345, (*GREEN_RGB, 255)), 785, 712, al),
                    (get_fitted_text_sprite("name: \"Ali\"", fonts.reg_30, 340, (240, 252, 245, 250)), 785, 792, al),
                    (get_fitted_text_sprite("avatar: 8 MB Photo", fonts.reg_30, 340, (240, 252, 245, 250)), 785, 855, al),
                    (get_fitted_text_sprite("posts: [ 240 items ]", fonts.reg_30, 340, (240, 252, 245, 250)), 785, 918, al),
                ])

        # Lightweight 8-Byte Pointer Receipt Card on Stack (`user = 0x7F40`)
        t_w = max(5.0, tc.get("ch8_wire", B[7] + dur * 0.52) - B[7] - 1.2)
        p_rcp = clamp((tl - t_w) / 1.35)
        if p_rcp > 0.01:
            draw_sketch_glass_box(cb, ce, 98, 635, 332, 215, 20, p_rcp, C_AMBER, (1.0, 0.92, 0.65), al, 0.95, t * 0.25, show_pen=(0.02 < p_rcp < 0.98))
            if p_rcp > 0.45:
                sharp_texts.extend([
                    (get_fitted_text_sprite("رسیدِ آدرس (Pointer)", fonts.bold_30, 300, (*AMBER_RGB, 255)), 264, 690, al),
                    (get_fitted_text_sprite("user = 0x7F40", fonts.bold_36, 300, (255, 255, 255, 255)), 264, 755, al),
                    (get_fitted_text_sprite("فقط ۸ بایت!", fonts.reg_26, 280, (*CYAN_RGB, 245)), 264, 812, al),
                ])

        # Live Glowing Bezier Pointer Bridge connecting Stack `0x7F40` -> Heap `0x7F40` with flowing photons!
        p_bridge = clamp((tl - (t_w + 1.4)) / 1.8)
        if p_bridge > 0.01:
            draw_sketch_bezier_wire(
                cb, ce,
                (430, 742), (495, 650), (525, 650), (592, 742),
                p_bridge, t, C_AMBER, (1.0, 0.94, 0.70), 5.2, al, True, True
            )

        # Bottom Golden Rule Card
        if p_bridge > 0.5:
            ub = clamp((p_bridge - 0.5) / 0.5)
            draw_laser_glass_card(cb, ce, 82, 1142, 916, 128, 22, al * ub, C_CYAN_MID, C_CYAN_CORE, 0.4, True, 0.92)
            sharp_texts.extend([
                (get_fitted_text_sprite("فرمولِ طلایی: جسمِ سنگین در انبارِ Heap + رسیدِ سبکِ آدرس رویِ میزِ Stack!", fonts.bold_30, 865, (235, 250, 255, 255)), 540, 1186, al * ub),
                (get_fitted_text_sprite("این‌طوری هم سرعتِ Stack رو داریم، هم فضایِ بزرگِ Heap رو!", fonts.reg_26, 850, (*GREEN_RGB, 245)), 540, 1236, al * ub),
            ])

    # =========================================================================
    # S09 (B[8]..B[9]): Famous Bug #1 — STACK OVERFLOW!
    # =========================================================================
    elif t < B[9]:
        tl = t - B[8]
        dur = max(1.0, B[9] - B[8])
        al = clamp(tl / 0.30) * clamp((B[9] - t) / 0.30)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "خطایِ معروفِ ۱ • Stack Overflow", al, C_RED)
        s_h, e_h = get_multitone_persian_sprite("Stack Overflow = ترکیدنِ سقفِ سینی‌هایِ استک!", [("Stack Overflow", RED_RGB)], fonts.bold_44, 920)
        sharp_texts.append((s_h, 540, 258, al))
        emissive_texts.append((e_h, 540, 258, al * 0.85))

        # Stack Tower + Clean Crimson Ceiling Line at y=532 (cleanly between Tray #6 at 552 and Tray #7 at 425!)
        draw_laser_glass_card(cb, ce, 190, 520, 700, 610, 26, al, C_RED, (1.0, 0.72, 0.74), t * 0.28, True, 0.88)
        ce.save(); ce.set_dash([18.0, 12.0], 0); ce.move_to(135, 532); ce.line_to(945, 532)
        ce.set_source_rgba(1.0, 0.28, 0.30, al * 0.95); ce.set_line_width(5.0); ce.stroke(); ce.restore()
        sharp_texts.append((get_fitted_text_sprite("MAX STACK LIMIT • سقفِ مجازِ استک", fonts.bold_30, 640, (*RED_RGB, 255)), 540, 382, al))

        # Rapidly piling recursive trays smashing cleanly above y=532!
        for k in range(7):
            pk = clamp((tl - 0.35 - k * 0.42) / 0.40)
            if pk <= 0.01:
                continue
            over = (k == 6)
            ty = 428 if over else (1022 - k * 93)
            cm = C_RED if over else C_CYAN_MID
            draw_sketch_glass_box(cb, ce, 245, ty, 590, 76, 14, pk, cm, C_CYAN_CORE, al, 0.94, k * 0.15, show_pen=(0.02 < pk < 0.96), pen_scale=0.72)
            if pk > 0.4:
                lbl = "سینیِ ۷: عبور از سقفِ مجاز (سرریزِ استک!)" if over else f"سینیِ {k+1}: فراخوانیِ تکراریِ همان تابع"
                sharp_texts.append((get_fitted_text_sprite(lbl, fonts.bold_30, 540, (*RED_RGB, 255) if over else (225, 245, 255, 250)), 540, ty + 38, al))

        p_warn = clamp((tl - dur * 0.55) / 0.7)
        if p_warn > 0.02:
            draw_glass_status_medallion(cb, ce, 540, 1225, 48, False, al * p_warn, p_warn)

    # =========================================================================
    # S10 (B[9]..B[10]): Famous Bug #2 — MEMORY LEAK & GARBAGE COLLECTOR!
    # =========================================================================
    elif t < B[10]:
        tl = t - B[9]
        dur = max(1.0, B[10] - B[9])
        al = clamp(tl / 0.30) * clamp((B[10] - t) / 0.30)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "خطایِ معروفِ ۲ • Memory Leak و رفتگرِ حافظه", al, C_AMBER)
        s_h, e_h = get_multitone_persian_sprite("Memory Leak = جا موندنِ جسمِ بی‌صاحب در انبارِ Heap", [("Memory Leak", AMBER_RGB), ("Heap", GREEN_RGB)], fonts.bold_44, 930)
        sharp_texts.append((s_h, 540, 258, al))
        emissive_texts.append((e_h, 540, 258, al * 0.85))

        t_gc = max(3.5, tc.get("ch10_gc", B[9] + dur * 0.62) - B[9] - 0.3)
        gc_u = clamp((tl - t_gc) / 1.6)

        # Left empty Stack card (Receipt deleted!)
        draw_laser_glass_card(cb, ce, 78, 430, 350, 490, 24, al, (0.30, 0.45, 0.65), C_CYAN_CORE, 0.2, False, 0.88)
        sharp_texts.extend([
            (get_fitted_text_sprite("STACK", fonts.bold_36, 300, (*CYAN_RGB, 255)), 253, 495, al),
            (get_fitted_text_sprite("رسید پاک شد!", fonts.bold_30, 300, (*RED_RGB, 255)), 253, 665, al),
            (get_fitted_text_sprite("user = null", fonts.reg_26, 290, (190, 210, 235, 225)), 253, 725, al),
        ])

        # Severed red X wire between Stack and Heap
        draw_glass_status_medallion(cb, ce, 492, 675, 38, False, al * (1.0 - gc_u * 0.5), clamp(tl / 0.7))

        # Right Heap Warehouse with orphaned heavy block -> swept clean by Emerald GC beam!
        draw_laser_glass_card(cb, ce, 558, 430, 444, 490, 24, al, C_GREEN if gc_u > 0.3 else C_RED, C_CYAN_CORE, t * 0.2, True, 0.88)
        sharp_texts.append((get_fitted_text_sprite("HEAP", fonts.bold_36, 390, (*GREEN_RGB, 255)), 780, 495, al))

        orphan_al = al * (1.0 - ease_in_out_cubic(clamp((gc_u - 0.35) / 0.65)))
        if orphan_al > 0.02:
            draw_laser_glass_card(cb, ce, 598, 575, 364, 265, 20, orphan_al, C_RED, (1.0, 0.72, 0.74), 0.5, False, 0.94)
            sharp_texts.extend([
                (get_fitted_text_sprite("جسمِ بی‌صاحب (50 MB)", fonts.bold_30, 330, (*RED_RGB, 255)), 780, 665, orphan_al),
                (get_fitted_text_sprite("اشغالِ الکیِ حافظه‌یِ RAM!", fonts.reg_26, 330, (255, 225, 225, 240)), 780, 735, orphan_al),
            ])

        # Sweeping Emerald Garbage Collector Scanner Beam!
        if gc_u > 0.02:
            scan_y = 545.0 + 330.0 * gc_u
            ce.save()
            ce.move_to(568, scan_y); ce.line_to(992, scan_y)
            ce.set_source_rgba(0.32, 1.0, 0.52, al * math.sin(gc_u * math.pi))
            ce.set_line_width(10.0); ce.stroke()
            ce.restore()
            if gc_u > 0.55:
                ug = clamp((gc_u - 0.55) / 0.45)
                draw_glass_status_medallion(cb, ce, 780, 695, 44, True, al * ug, ug)
                sharp_texts.append((get_fitted_text_sprite("پاک‌سازیِ خودکار با رفتگرِ حافظه (GC)", fonts.bold_30, 385, (*GREEN_RGB, 255)), 780, 805, al * ug))

        draw_laser_glass_card(cb, ce, 92, 1005, 896, 145, 22, al, C_AMBER, (1.0, 0.92, 0.65), 0.3, False, 0.90)
        sharp_texts.extend([
            (get_fitted_text_sprite("در زبان‌هایی مثلِ Python / Java / JS: رفتگرِ حافظه خودکار تمیزش می‌کنه", fonts.bold_30, 845, (*GREEN_RGB, 255)), 540, 1052, al),
            (get_fitted_text_sprite("در C / C++: برنامه‌نویس خودش باید دستورِ آزادسازی (free / delete) بده!", fonts.reg_26, 845, (235, 245, 255, 240)), 540, 1106, al),
        ])

    # =========================================================================
    # S11 (B[10]..B[11]): Complete Sapphire Master Comparison Matrix + 3D Character
    # =========================================================================
    elif t < B[11]:
        tl = t - B[10]
        al = clamp(tl / 0.35) * clamp((B[11] - t) / 0.35)

        _draw_chapter_pill(cb, ce, sharp_texts, fonts, "جمع‌بندیِ نهایی • جدولِ مقایسه‌یِ کامل", al, C_CYAN_MID)

        # Comparison Table Card (y = 225..885)
        p_tb = clamp(tl / 1.6)
        draw_sketch_glass_box(cb, ce, 68, 225, 944, 645, 26, p_tb, C_CYAN_MID, C_CYAN_CORE, al, 0.92, t * 0.14)
        if p_tb > 0.35:
            ut = clamp((p_tb - 0.35) / 0.65)
            # Column headers
            sharp_texts.extend([
                (get_fitted_text_sprite("ویژگی", fonts.bold_36, 220, (185, 215, 245, 255)), 865, 288, al * ut),
                (get_fitted_text_sprite("STACK (اِستَک)", fonts.bold_36, 310, (*CYAN_RGB, 255)), 565, 288, al * ut),
                (get_fitted_text_sprite("HEAP (هیپ)", fonts.bold_36, 310, (*GREEN_RGB, 255)), 235, 288, al * ut),
            ])
            rows = [
                ("محلِ زندگی",   "داخلِ RAM",         "داخلِ RAM"),
                ("سرعت",        "فوق‌سریع (۱ نانوثانیه)", "کمی کندتر"),
                ("اندازه‌یِ داده", "ثابت و کوچک",       "بزرگ و متغیر"),
                ("نظمِ چیدمان",  "سینیِ منظم (LIFO)",   "انبارِ آزاد (پویا)"),
                ("پاک‌سازی",     "۱۰۰٪ خودکار با تابع", "دستی / رفتگرِ حافظه"),
            ]
            for ri, (r_lbl, r_stk, r_hp) in enumerate(rows):
                ry = 378 + ri * 94
                cb.save()
                cb.move_to(96, ry - 44); cb.line_to(984, ry - 44)
                cb.set_source_rgba(0.25, 0.55, 0.85, al * ut * 0.32); cb.set_line_width(1.5); cb.stroke()
                cb.restore()
                sharp_texts.extend([
                    (get_fitted_text_sprite(r_lbl, fonts.bold_30, 225, (215, 232, 250, 250)), 865, ry, al * ut),
                    (get_fitted_text_sprite(r_stk, fonts.bold_30, 315, (*CYAN_RGB, 255)), 565, ry, al * ut),
                    (get_fitted_text_sprite(r_hp,  fonts.bold_30, 315, (*GREEN_RGB, 255)), 235, ry, al * ut),
                ])

        # Front-view Volumetric 3D Sapphire Character at bottom desk with Emerald Check / Mastery!
        draw_sapphire_thinking_character_front(cb, ce, 540, 1215, t, al)
        draw_glass_status_medallion(cb, ce, 755, 985, 44, True, al, clamp((tl - 1.0) / 0.8))

    # =========================================================================
    # S12 (B[11]..total_dur): Signature Glowing Sapphire Pill Outro
    # =========================================================================
    else:
        tl = max(0.0, t - B[11])
        al = clamp(tl / 0.35) * clamp((total_dur - t + 0.08) / 0.35)
        pop = ease_out_cubic(clamp(tl / 0.55))
        pw_p = 560.0 * (0.86 + 0.14 * pop)
        ph_p = 138.0
        px_p = 540.0 - pw_p * 0.5
        py_p = 790.0

        cb.save()
        rounded_rect_path(cb, px_p, py_p, pw_p, ph_p, ph_p * 0.5)
        lg_p = cairo.LinearGradient(px_p, py_p, px_p, py_p + ph_p)
        lg_p.add_color_stop_rgba(0.0, 0.08, 0.24, 0.48, al * 0.96)
        lg_p.add_color_stop_rgba(1.0, 0.03, 0.10, 0.24, al * 0.98)
        cb.set_source(lg_p); cb.fill_preserve()
        cb.set_source_rgba(0.35, 0.76, 1.0, al * 0.92); cb.set_line_width(3.2); cb.stroke()
        cb.restore()

        ce.save()
        rounded_rect_path(ce, px_p, py_p, pw_p, ph_p, ph_p * 0.5)
        ce.set_source_rgba(C_CYAN_MID[0], C_CYAN_MID[1], C_CYAN_MID[2], al * 0.72)
        ce.set_line_width(4.5); ce.stroke()
        ce.restore()

        sharp_texts.extend([
            (get_fitted_text_sprite("زاویه ذهن", fonts.bold_52, 460), 540, py_p + ph_p * 0.5, al * 0.99),
            (get_fitted_text_sprite("@zavieh.penhann", fonts.med_32, 420, (150, 215, 255, 235)), 540, py_p + ph_p + 62, al * 0.92),
        ])

    return composite_sapphire_frame(
        surf_base=surf_base,
        surf_emissive=surf_emissive,
        sharp_texts=sharp_texts,
        emissive_texts=emissive_texts,
        fonts=fonts,
        t=t,
        sub_lines=sub_lines,
        grid_strength=grid_strength,
    )


# =============================================================================
# MULTIPROCESSING CLOUD WORKER + 12-PANEL MASTERCLASS QA SHEETS
# =============================================================================
_W_FONTS = None
_W_META = None
_W_SB = None
_W_CB = None
_W_SE = None
_W_CE = None


def _worker_init(font_dir: str, meta: dict):
    global _W_FONTS, _W_META, _W_SB, _W_CB, _W_SE, _W_CE
    _W_FONTS = FontBank(font_dir)
    _W_META = meta
    _W_SB = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CB = cairo.Context(_W_SB)
    _W_SE = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CE = cairo.Context(_W_SE)


def _worker_render_frame(fn: int) -> bytes:
    t = fn / float(FPS_MC)
    return render_masterclass_scene(
        t, _W_META["total_dur"], _W_META["t_cues"], _W_META["sub_lines"],
        _W_FONTS, _W_SB, _W_CB, _W_SE, _W_CE
    )


def save_qa_sheets(font_dir: str, meta: dict, qa_dir: str):
    """Generates 12-panel Masterclass Storyboard Grid + y=1515 Subtitle Strip."""
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    sb = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cb = cairo.Context(sb)
    se = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ce = cairo.Context(se)

    tc = meta["t_cues"]
    td = meta["total_dur"]
    B = _get_chapter_bounds(tc, meta["sub_lines"], td)

    sample_ts = [
        B[0] + (B[1] - B[0]) * 0.78,   # 1. S01 3D Desk + Live Roadmap
        B[1] + (B[2] - B[1]) * 0.82,   # 2. S02 SSD vs CPU Bottleneck
        B[2] + (B[3] - B[2]) * 0.72,   # 3. S03 RAM Numbered Workbench + Jump
        B[3] + (B[4] - B[3]) * 0.80,   # 4. S04 Inside RAM (Code/Static/Heap/Stack)
        B[4] + (B[5] - B[4]) * 0.62,   # 5. S05 Stack LIFO Push + SP
        B[5] + (B[6] - B[5]) * 0.78,   # 6. S06 Stack Fixed-Size Limitation
        B[6] + (B[7] - B[6]) * 0.82,   # 7. S07 Heap Dynamic Open Warehouse
        B[7] + (B[8] - B[7]) * 0.82,   # 8. S08 Stack Pointer 0x7F40 -> Heap Object
        B[8] + (B[9] - B[8]) * 0.78,   # 9. S09 Stack Overflow Explosion
        B[9] + (B[10] - B[9]) * 0.76,  # 10. S10 Memory Leak + Garbage Collector
        B[10] + (B[11] - B[10]) * 0.75,# 11. S11 Complete Comparison Matrix + 3D Char
        B[11] + (B[12] - B[11]) * 0.50,# 12. S12 Sapphire Pill CTA
    ]

    pw, ph = 360, 640
    grid12 = Image.new("RGB", (pw * 4, ph * 3), (0, 0, 0))
    for i, ts in enumerate(sample_ts):
        ts_c = max(0.1, min(td - 0.15, ts))
        raw = render_masterclass_scene(ts_c, td, tc, meta["sub_lines"], fonts, sb, cb, se, ce)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw, ph), Image.Resampling.LANCZOS)
        r, c = divmod(i, 4)
        grid12.paste(im, (c * pw, r * ph))
    grid12.save(os.path.join(qa_dir, "storyboard_12_masterclass.png"))

    sub_strip = Image.new("RGB", (920, 10 * 100), (0, 0, 0))
    test_ln = meta["sub_lines"][min(12, len(meta["sub_lines"]) - 1)]
    t0_s = test_ln["times"][0]
    crop_y0 = int(round(SAPPHIRE_SUB_Y - 58))
    for k in range(10):
        tk = t0_s + k * 0.10
        raw = render_masterclass_scene(tk, td, tc, meta["sub_lines"], fonts, sb, cb, se, ce)
        im = Image.frombytes("RGB", (W, H), raw)
        crop = im.crop((80, crop_y0, 1000, crop_y0 + 100))
        for x in range(36):
            crop.putpixel((x, 58), (0, 220, 90))
            crop.putpixel((919 - x, 58), (0, 220, 90))
        sub_strip.paste(crop, (0, k * 100))
    sub_strip.save(os.path.join(qa_dir, "subtitle_strip_masterclass.png"))


def run_cloud_render(font_dir: str, work_dir: str, out_mp4: str, qa_dir: str, whisper_size: str = "medium"):
    import multiprocessing as mp
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(qa_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)

    print("=== [1/3] Building Slow-Paced Teacher Masterclass Audio (Locked Rasalgethi, 1.15x Calm Stretch) ===", flush=True)
    meta = build_slow_masterclass_audio(
        segments=SCRIPT_SEGMENTS,
        sfx_cue_map=SFX_CUE_MAP,
        work_dir=work_dir,
        voice_name=LOCKED_SIGNATURE_VOICE,
        chunk_size=10,
        slow_time_ratio=1.15,
        final_tail_sec=4.0,
        whisper_size=whisper_size,
    )

    total_dur = meta["total_dur"]
    total_frames = int(round(total_dur * FPS_MC))
    workers = max(1, mp.cpu_count())
    print(f"=== [2/3] Rendering {total_frames} Masterclass frames @ {W}x{H} {FPS_MC}fps on {workers} CPU cores (CRF 14) ===", flush=True)

    ff_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS_MC),
        "-i", "-",
        "-i", meta["master_wav"],
        "-c:v", "libx264", "-preset", "slow", "-crf", "14",
        "-profile:v", "high", "-level:v", "4.2",
        "-pix_fmt", "yuv420p",
        "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4,
    ]
    proc = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE)
    t0 = time.time()

    with mp.Pool(processes=workers, initializer=_worker_init, initargs=(font_dir, meta), maxtasksperchild=350) as pool:
        for fn, rgb_bytes in enumerate(pool.imap(_worker_render_frame, range(total_frames), chunksize=8)):
            proc.stdin.write(rgb_bytes)
            if fn % 300 == 0 or fn == total_frames - 1:
                el = time.time() - t0
                print(f"  Frame {fn+1:4d}/{total_frames} ({(fn+1)/total_frames*100:5.1f}%) | {(fn+1)/max(0.01,el):5.1f} fps", flush=True)

    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg exited with code {rc}")

    print("=== [3/3] Generating 12-Panel Masterclass QA Sheets ===", flush=True)
    save_qa_sheets(font_dir, meta, qa_dir)
    subprocess.check_call(["cp", meta["align_json"], os.path.join(qa_dir, "alignment.json")])
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"=== COMPLETE: {out_mp4} ({sz_mb:.2f} MB, {total_dur:.2f}s @ {FPS_MC}fps) ===", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cloud-render":
        run_cloud_render(
            font_dir=sys.argv[2],
            work_dir=sys.argv[3],
            out_mp4=sys.argv[4],
            qa_dir=sys.argv[5],
            whisper_size=(sys.argv[6] if len(sys.argv) > 6 else "medium"),
        )
    else:
        print("Usage: python src/episodes/ep10_ram_stack_heap_masterclass.py --cloud-render <fonts> <work> <out.mp4> <qa_dir> [whisper_size]")
