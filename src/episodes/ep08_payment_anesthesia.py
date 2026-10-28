"""
Episode 08 (Studio v4.3 — Raised Instagram-Safe Subtitle y=1520 + High-Loudness Broadcast Master)
Topic: «آمپولِ بی‌حسیِ پرداخت؛ چرا ۱ میلیون پولِ نقد قلبت رو به درد میاره ولی ۴ قسطِ اینترنتی نه؟»
Page: زاویه ذهن (@zavieh.penhann)

v4.3 Studio Upgrades:
  - Raised Subtitle Safe-Zone (SUBTITLE_BASELINE_Y = 1520.0, CHAPTER_DOTS_Y = 1432.0):
    Clears Instagram's bottom @username / Follow button / caption UI with zero overlap!
  - High-Loudness Commercial Broadcast Master (-11.5 dBFS Voiced RMS / -0.7 dB AAC-safe True Peak)
    + Calm Velvet Dark-Ambient Score (-16 dB below narrator) + bespoke Cash/POS/Syringe Foley SFX!
  - 24 Rapid-Fire @ensan.besham Visual Shots (~2.6s average shot length):
    counting crisp banknotes, contactless POS card waves, fMRI brain pain-center, giant monoline
    anesthesia syringe numbing a wallet, 1M split into 4x250 cubes, 1X vs 2X spending columns,
    paycheck eaten by installment jaws, 20-second card-typing wake-up, cash-in-hand test, and 1-vs-2 CTA!
"""
import os, sys, math, time, json, subprocess
import cairocffi as cairo
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.engine.audio_master import build_episode_audio, LOCKED_SIGNATURE_VOICE
from src.engine.render_core import (
    W, H, FPS, SUBTITLE_BASELINE_Y, FontBank, clamp, ease_out_cubic, ease_in_out_cubic,
    window_fade, fa, get_text_sprite, get_fitted_text_sprite,
    rounded_rect_path, set_stroke_draw, draw_star4,
    draw_human_figure, draw_spotlight_cone, draw_hud_chrome,
    draw_safe_card, draw_pill_badge,
    draw_ambient_particles,
    impact_punch, push_camera, pop_camera_and_transform_texts,
    draw_shockwave_ring, draw_hypnotic_chronograph_ring,
    draw_ecg_waveform,
    draw_character_with_phone, draw_pov_phone_in_hand,
    draw_character_at_desk, draw_observatory_eye,
    composite_oled_frame,
)

EP_CODE = "۰۸"
EP_TITLE = "آمپولِ بی‌حسیِ پرداخت"

# 35 Short, Punchy, Spoken Tehrani Persian Phrases (pure Persian in TTS -> ~63s total, 24 rapid shots!)
SCRIPT_SEGMENTS = [
    # Act I — The Hook: Cash Pain vs Numb Installments (0..8 -> Shots 01..05)
    ("دقت کردی وقتی یه میلیون اسکناس می‌شماری،",           "دقت کردی وقتی ۱ میلیون اسکناس می‌شماری،"),            # 0  -> Shot 01
    ("دستت می‌لرزه و زورت میاد بدی بره؟",                  "دستت می‌لرزه و زورت میاد بدی بره؟"),                  # 1  -> Shot 01
    ("ولی همون پول رو با کارت یا چهار قسطِ اینترنتی،",     "ولی همون رو با کارت یا ۴ قسط اینترنتی،"),             # 2  -> Shot 02
    ("با لبخند و بدونِ هیچ دردی می‌زنی می‌ره!",            "با لبخند و بدون هیچ دردی می‌زنی می‌ره!"),             # 3  -> Shot 02
    ("پول همون پوله و از همون جیب می‌ره؛",                 "پول همون پوله و از همون جیب می‌ره؛"),                 # 4  -> Shot 03
    ("پس چرا حسِ مغزت صد و هشتاد درجه فرق داره؟",          "پس چرا حس مغزت ۱۸۰ درجه فرق داره؟"),                  # 5  -> Shot 03
    ("اسکنِ مغزی یه رازِ عجیب رو لو داده:",                "اسکن مغزی یه راز عجیب رو لو داده:"),                  # 6  -> Shot 04
    ("وقتی پولِ نقد از دستت جدا می‌شه،",                   "وقتی پول نقد از دستت جدا می‌شه،"),                    # 7  -> Shot 04
    ("دقیقاً بخشِ دردِ فیزیکیِ مغزت روشن می‌شه!",          "بخش «درد فیزیکی» مغزت روشن می‌شه!"),                  # 8  -> Shot 05

    # Act II — Natural Brake vs Payment Anesthesia Syringe (9..23 -> Shots 06..13)
    ("اون درد اصلاً چیزِ بدی نبود؛",                       "اون درد اصلاً چیز بدی نبود؛"),                        # 9  -> Shot 06
    ("ترمزِ طبیعیِ مغزت بود تا بیخودی خرج نکنی!",          "ترمز طبیعی مغزت بود تا بیخودی خرج نکنی!"),            # 10 -> Shot 06
    ("اما برندها فهمیدن تا این درد هست،",                  "اما برندها فهمیدن تا این درد هست،"),                  # 11 -> Shot 07
    ("تو جلوی خریدهای هیجانی رو می‌گیری!",                 "تو جلوی خریدهای هیجانی رو می‌گیری!"),                 # 12 -> Shot 07
    ("پس اومدن به کیفِ پولت آمپولِ بی‌حسی زدن!",           "پس به کیف پولت «آمپول بی‌حسی» زدن!"),                 # 13 -> Shot 08
    ("اول پول رو تبدیل کردن به یه کارتِ پلاستیکی؛",        "اول پول رو کردن یه کارت پلاستیکی؛"),                  # 14 -> Shot 08
    ("بعدش کردنش پرداختِ تک‌کلیکیِ ذخیره شده،",            "بعدش کردنش پرداخت تک‌کلیکی ذخیره شده،"),              # 15 -> Shot 09
    ("و آخرش هم قسطیِ بدونِ کارمزد!",                      "و آخرش هم قسطیِ بدون کارمزد!"),                       # 16 -> Shot 09
    ("حقه کجاست؟ لذتِ خرید رو همین ثانیه می‌بری،",         "لذت خرید رو همین ثانیه می‌بری،"),                     # 17 -> Shot 10
    ("ولی دردِ پرداختش می‌افته ماه‌های بعد!",              "ولی درد پرداختش می‌افته ماه‌های بعد!"),               # 18 -> Shot 10
    ("مغزت چهار تا دویست و پنجاهی رو،",                    "مغزت ۴ تا ۲۵۰ هزار تومنی رو،"),                       # 19 -> Shot 11
    ("اصلاً به اندازه‌ی یه میلیون جدی نمی‌گیره!",          "اصلاً به اندازه‌ی ۱ میلیون جدی نمی‌گیره!"),           # 20 -> Shot 11
    ("نتیجه‌ی آزمایش‌های اقتصادی ترسناکه:",                 "نتیجه‌ی آزمایش‌های اقتصادی ترسناکه:"),                 # 21 -> Shot 12
    ("وقتی دردِ پرداخت بی‌حس می‌شه دو برابر خرج می‌کنی!",  "با بی‌حسی پرداخت، تا ۲ برابر خرج می‌کنی!"),           # 22 -> Shot 12
    ("و آخرِ ماه می‌بینی ده تا قسطِ کوچیک،",               "و آخر ماه می‌بینی ۱۰ تا قسط کوچیک،"),                 # 23 -> Shot 13
    ("قبل از رسیدنِ حقوقت کلش رو بلعیدن!",                 "قبل از رسیدن حقوقت کلش رو بلعیدن!"),                  # 24 -> Shot 13

    # Act III — Everyday Banner & The 2 Antidotes + Interactive CTA (25..34 -> Shots 14..24)
    ("همون جمله‌ی قشنگِ الان بخر، چهار ماه دیگه بده!",     "«همین الان بخر، ۴ ماه دیگه بده!»"),                   # 25 -> Shot 14
    ("پس چطور اثرِ این بی‌حسی رو خنثی کنی؟",               "پس چطور اثر این بی‌حسی رو خنثی کنی؟"),                # 26 -> Shot 15
    ("پادزهرِ اول: شماره کارتت رو ذخیره نکن!",             "پادزهر اول: شماره کارتت رو ذخیره نکن!"),              # 27 -> Shot 16
    ("همون بیست ثانیه تایپ کردن، مغزت رو بیدار می‌کنه!",   "۲۰ ثانیه تایپ کردن، مغزت رو بیدار می‌کنه!"),          # 28 -> Shot 17
    ("پادزهرِ دوم: قبل از هر خریدِ قسطی بپرس:",            "پادزهر دوم: قبل از هر خرید قسطی بپرس:"),              # 29 -> Shot 18
    ("اگه کلِ پولش الان نقد تو دستم بود، می‌خریدم؟",       "اگه کل پولش نقد تو دستم بود، می‌خریدم؟"),             # 30 -> Shot 19
    ("اگه نه، اون نیازِ تو نیست؛ اثرِ بی‌حسیه!",           "اگه نه، اون نیازت نیست؛ اثر بی‌حسیه!"),               # 31 -> Shot 20
    ("نذار با بی‌حسیِ امروز، فردات رو پیش‌فروش کنن!",      "نذار با بی‌حسی امروز، فردات رو پیش‌فروش کنن!"),       # 32 -> Shot 21
    ("تو موقعِ خرید کدوم مدلی هستی؟",                      "تو موقع خرید کدوم مدلی هستی؟"),                       # 33 -> Shot 22
    ("یک حساب‌شده، یا دو اسیرِ قسط و کارت؟ بنویس!",        "عدد ۱ یا ۲ رو همین الان تو کامنت بنویس!"),           # 34 -> Shot 23
]

# Synchronized Luxury Foley & Whip-Cut Cues
SFX_CUE_MAP = [
    ("c01_cash",     0,  0, "cash_rustle",  -0.01),
    ("_c01_hb",      1,  1, "heartbeat",     0.02),
    ("c02_pos",      2,  0, "whip",         -0.05),
    ("_c02_beep",    3,  2, "pos_beep",      0.00),
    ("c03_scale",    4,  0, "scale_tip",    -0.02),
    ("c04_scan",     6,  0, "scan",         -0.02),
    ("c05_pain",     8,  0, "impact_boom",  -0.02),
    ("_c05_hb2",     8,  2, "heartbeat",     0.04),

    ("c06_brake",    9,  0, "whip",         -0.05),
    ("_c06_stamp",  10,  1, "stamp",         0.00),
    ("c07_brands",  11,  0, "whoosh",       -0.04),
    ("c08_syringe", 13,  0, "syringe_hiss", -0.02),
    ("_c08_card",   14,  3, "screen_on",     0.00),
    ("c09_oneclick",15,  0, "button_press", -0.02),
    ("_c09_pos2",   16,  2, "pos_beep",      0.02),
    ("c10_split",   17,  0, "whip",         -0.05),
    ("c11_four",    19,  0, "slash",        -0.02),
    ("c12_2x",      21,  0, "whip",         -0.05),
    ("c12_boom",    22,  3, "impact_boom",  -0.02),
    ("c13_eat",     23,  0, "crab_pinch",   -0.02),
    ("_c13_clink",  24,  2, "chain_clink",   0.02),

    ("c14_bnpl",    25,  0, "screen_on",    -0.02),
    ("c15_cut",     26,  0, "slash",        -0.02),
    ("c16_anti1",   27,  0, "whip",         -0.05),
    ("c17_type",    28,  0, "typing",        0.00),
    ("c18_anti2",   29,  0, "whip",         -0.05),
    ("c19_cashtest",30,  0, "cash_rustle",   0.00),
    ("c20_stamp",   31,  0, "stamp",        -0.02),
    ("c21_free",    32,  0, "shatter",      -0.02),
    ("c22_ask",     33,  0, "mirror_ring",  -0.02),
    ("c23_cta",     34,  0, "button_press",  0.00),
]


# =============================================================================
# BESPOKE EPISODE 08 MONOCHROME @ENSAN.BESHAM VECTOR ACTORS & METAPHORS
# =============================================================================
def draw_glow_line(cs, cg, x1, y1, x2, y2, alpha=1.0, lw_s=2.4, lw_g=5.5, dashed=False):
    if alpha <= 0.01:
        return
    for ctx, lw, al in ((cs, lw_s, alpha * 0.92), (cg, lw_g, alpha * 0.38)):
        ctx.save()
        ctx.set_dash([8.0, 7.0] if dashed else [])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()
        ctx.restore()


def draw_banknote(cs, cg, cx: float, cy: float, w: float = 210.0, h: float = 104.0, rot: float = 0.0, alpha: float = 1.0):
    """Crisp geometric @ensan.besham banknote with inner border, emblem circle, and corner marks."""
    if alpha <= 0.01:
        return
    for ctx, lw, al in ((cs, 2.5, alpha * 0.95), (cg, 5.4, alpha * 0.38)):
        ctx.save()
        ctx.set_dash([])
        ctx.translate(cx, cy)
        ctx.rotate(rot)
        rounded_rect_path(ctx, -w * 0.5, -h * 0.5, w, h, 10)
        if ctx is cs:
            ctx.set_source_rgba(0.035, 0.035, 0.05, 0.94 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()
        # Inner decorative frame + central medallion
        rounded_rect_path(ctx, -w * 0.42, -h * 0.36, w * 0.84, h * 0.72, 6)
        ctx.set_line_width(lw * 0.65)
        ctx.stroke()
        ctx.arc(0, 0, h * 0.22, 0, 2 * math.pi)
        ctx.stroke()
        ctx.restore()


def draw_credit_card(cs, cg, cx: float, cy: float, w: float = 290.0, h: float = 182.0, rot: float = 0.0, alpha: float = 1.0, waves: bool = False):
    """Minimalist contactless bank card with EMV chip and NFC radio waves."""
    if alpha <= 0.01:
        return
    for ctx, lw, al in ((cs, 2.8, alpha * 0.96), (cg, 6.2, alpha * 0.44)):
        ctx.save()
        ctx.set_dash([])
        ctx.translate(cx, cy)
        ctx.rotate(rot)
        rounded_rect_path(ctx, -w * 0.5, -h * 0.5, w, h, 18)
        if ctx is cs:
            ctx.set_source_rgba(0.04, 0.04, 0.06, 0.95 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()

        # EMV gold-style monoline chip on left
        rounded_rect_path(ctx, -w * 0.35, -h * 0.14, 48, 36, 7)
        ctx.stroke()
        # 4 minimalist card number blocks along lower strip
        for bi in range(4):
            bx = -w * 0.35 + bi * (w * 0.19)
            ctx.move_to(bx, h * 0.24)
            ctx.line_to(bx + w * 0.13, h * 0.24)
            ctx.stroke()

        # Contactless NFC waves on right
        if waves:
            for wi in range(1, 4):
                ctx.arc(w * 0.22, -h * 0.06, wi * 13.0, -0.65, 0.65)
                ctx.stroke()
        ctx.restore()


def draw_anesthesia_syringe(cs, cg, tip_x: float, tip_y: float, angle: float, plunge_p: float, alpha: float = 1.0):
    """
    Iconic @ensan.besham clinical monoline syringe injecting numbing anesthesia!
    Origin (tip_x, tip_y) is the sharp needle tip; barrel extends backward along -angle.
    """
    if alpha <= 0.01:
        return
    barrel_len = 205.0
    barrel_w = 56.0
    needle_len = 68.0
    plunger_ext = 26.0 + 72.0 * (1.0 - clamp(plunge_p))

    for ctx, lw, al in ((cs, 2.9, alpha * 0.97), (cg, 6.6, alpha * 0.48)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.translate(tip_x, tip_y)
        ctx.rotate(angle)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)

        # Sharp hypodermic needle (0,0) -> (-needle_len, 0)
        ctx.move_to(0, 0)
        ctx.line_to(-needle_len, 0)
        ctx.stroke()

        # Needle hub collar
        rounded_rect_path(ctx, -needle_len - 16, -12, 16, 24, 4)
        ctx.stroke()

        # Graduated glass barrel
        bx0 = -needle_len - 16 - barrel_len
        rounded_rect_path(ctx, bx0, -barrel_w * 0.5, barrel_len, barrel_w, 8)
        if ctx is cs:
            ctx.set_source_rgba(0.035, 0.035, 0.05, 0.94 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.stroke()

        # Measurement graduation ticks along barrel
        for gi in range(1, 6):
            gx = bx0 + gi * (barrel_len / 6.0)
            ctx.move_to(gx, -barrel_w * 0.5)
            ctx.line_to(gx, -barrel_w * 0.5 + 15.0)
            ctx.stroke()

        # Finger flange ears at back of barrel
        ctx.move_to(bx0, -barrel_w * 0.82)
        ctx.line_to(bx0, barrel_w * 0.82)
        ctx.stroke()

        # Plunger rod + thumb pad pushing in!
        ctx.move_to(bx0 + barrel_len * clamp(plunge_p) * 0.72, -barrel_w * 0.40)
        ctx.line_to(bx0 + barrel_len * clamp(plunge_p) * 0.72, barrel_w * 0.40)
        ctx.stroke()
        ctx.move_to(bx0, 0)
        ctx.line_to(bx0 - plunger_ext, 0)
        ctx.stroke()
        ctx.move_to(bx0 - plunger_ext, -26)
        ctx.line_to(bx0 - plunger_ext, 26)
        ctx.stroke()
        ctx.restore()


# =============================================================================
# 24-SHOT HYPER-CUT TIMELINE ENGINE
# =============================================================================
def _shot_win(t: float, t0: float, t1: float, fi: float = 0.13, fo: float = 0.13) -> float:
    if t < t0 - 0.02 or t > t1 + fo:
        return 0.0
    return clamp((t - t0 + 0.02) / max(0.04, fi)) * clamp((t1 + fo - t) / max(0.04, fo))


def _shot_cam_z(t: float, t0: float, t1: float, base_in: float = 0.93) -> float:
    dur = max(0.35, t1 - t0)
    u = clamp((t - t0) / dur)
    z_in = base_in + (1.0 - base_in) * ease_out_cubic(clamp((t - t0) / 0.28))
    z_drift = 0.030 * u
    z_out = clamp((t - (t1 - 0.18)) / 0.20) ** 2 * 0.08
    return z_in + z_drift + z_out


def _compute_shot_bounds(tc: dict, outro_t0: float) -> list[float]:
    raw = [
        0.0,
        tc["c02_pos"],
        tc["c03_scale"],
        tc["c04_scan"],
        tc["c05_pain"] - 0.05,
        tc["c06_brake"],
        tc["c07_brands"],
        tc["c08_syringe"] - 0.05,
        tc["c09_oneclick"],
        tc["c10_split"],
        tc["c11_four"],
        tc["c12_2x"],
        tc["c13_eat"],
        tc["c14_bnpl"],
        tc["c15_cut"] - 0.05,
        tc["c16_anti1"],
        tc["c17_type"],
        tc["c18_anti2"],
        tc["c19_cashtest"],
        tc["c20_stamp"],
        tc["c21_free"],
        tc["c22_ask"],
        tc["c23_cta"],
        outro_t0,
    ]
    sb = [0.0]
    for v in raw[1:-1]:
        sb.append(max(sb[-1] + 0.72, float(v)))
    sb.append(max(sb[-1] + 0.90, float(outro_t0)))
    return sb


def render_scene_frame(
    t: float, total_dur: float, tc: dict, sub_lines: list[dict],
    fonts: FontBank, surf_glow, ctx_glow, surf_sharp, ctx_sharp
) -> bytes:
    for ctx in (ctx_glow, ctx_sharp):
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.restore()

    cs, cg = ctx_sharp, ctx_glow
    txts = []
    outro_t0 = total_dur - 4.0

    (b01, b02, b03, b04, b05, b06, b07, b08, b09, b10, b11, b12,
     b13, b14, b15, b16, b17, b18, b19, b20, b21, b22, b23, b24) = _compute_shot_bounds(tc, outro_t0)

    chapters = [0.0, b05, b08, b11, b15, b18, b23]
    draw_hud_chrome(cs, cg, txts, fonts, t, total_dur, EP_CODE, EP_TITLE, chapters)
    draw_ambient_particles(cs, t, alpha=0.82 * clamp((b24 - t) / 0.8))

    # =========================================================================
    # SHOT 01 (b01..b02): Counting Physical 1M Cash — Hand Trembles & Hesitates!
    # =========================================================================
    w = _shot_win(t, b01, b02)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b01, b02, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=830)
        p_in = ease_out_cubic(clamp((t - b01) / 0.65))

        sp_h1 = get_fitted_text_sprite("۱,۰۰۰,۰۰۰ تومن پولِ نقد...", fonts.eb_68, 860, (255, 255, 255, 255), glow=0.85)
        sp_s1 = get_fitted_text_sprite("شمردنش قلبت رو به درد میاره!", fonts.bold_30, 740, (212, 212, 228, 255))
        stx.append((sp_h1, 540, 365, w))
        stx.append((sp_s1, 540, 455, w))

        # Fanning stack of 4 physical banknotes peeling away upward!
        for bi in range(4):
            ang = (-0.20 + bi * 0.13) * p_in
            bx = 540 + (bi - 1.5) * 62.0 * p_in
            by = 760 - bi * 32.0 * p_in + math.sin(t * 9.0 + bi) * 3.0
            draw_banknote(cs, cg, bx, by, w=235, h=114, rot=ang, alpha=w * (0.65 + 0.1 * bi))

        draw_human_figure(cs, 540, 1215, scale=1.82, alpha=w * 0.92, lw=2.7)
        draw_ecg_waveform(cs, cg, 210, 870, 1265, t, amp=34.0, alpha=w * 0.85)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=830)

    # =========================================================================
    # SHOT 02 (b02..b03): Contactless Card / 4 Installments — Zero Pain!
    # =========================================================================
    w = _shot_win(t, b02, b03)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b02, b03, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_h2 = get_fitted_text_sprite("اما با کارت یا ۴ قسطِ اینترنتی...", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.78)
        sp_s2 = get_fitted_text_sprite("با لبخند و بدونِ هیچ حسی می‌زنی می‌ره!", fonts.bold_30, 780, (215, 215, 232, 255))
        stx.append((sp_h2, 540, 365, w))
        stx.append((sp_s2, 540, 448, w))

        draw_credit_card(cs, cg, 540, 780, w=360, h=224, rot=-0.06, alpha=w, waves=True)
        draw_shockwave_ring(cs, cg, 620, 765, clamp((t - b02 - 0.18) / 0.80), max_r=240, alpha=w * 0.75)
        draw_pill_badge(cs, cg, stx, "پرداخت موفق  •  ۴ قسطِ راحت!", 540, 1065, fonts.bold_30, alpha=w, glow=True, pad_x=34, pad_y=12)
        # Flat numbed horizontal line instead of ECG spike!
        draw_glow_line(cs, cg, 220, 1215, 860, 1215, w * 0.65, lw_s=2.4)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 03 (b03..b04): Balance Scale — Exact Same 1,000,000, Opposite Feeling!
    # =========================================================================
    w = _shot_win(t, b03, b04)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b03, b04, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        tilt = 0.20 * ease_out_cubic(clamp((t - b03) / 0.55))

        sp_h3 = get_fitted_text_sprite("پول همون پوله؛ چرا حسش ۱۸۰ درجه فرق داره؟", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_h3, 540, 370, w))

        # Central fulcrum + tilted beam (cash feels heavy on right, 4x250 feels feather-light on left!)
        draw_glow_line(cs, cg, 540, 765, 540, 1185, w * 0.9, lw_s=3.0)
        draw_glow_line(cs, cg, 390, 1185, 690, 1185, w * 0.85, lw_s=3.0)
        bx_l, by_l = 540 - 275 * math.cos(tilt), 785 - 275 * math.sin(tilt)
        bx_r, by_r = 540 + 275 * math.cos(tilt), 785 + 275 * math.sin(tilt)
        draw_glow_line(cs, cg, bx_l, by_l, bx_r, by_r, w * 0.95, lw_s=3.2)

        draw_credit_card(cs, cg, bx_l, by_l - 85, w=195, h=122, alpha=w, waves=True)
        draw_banknote(cs, cg, bx_r, by_r - 70, w=205, h=100, alpha=w)
        sp_cl = get_fitted_text_sprite("۴ قسط (سبک و بی‌حس)", fonts.reg_26, 260, (205, 205, 222, 255))
        sp_cr = get_fitted_text_sprite("۱ میلیون نقد (سنگین!)", fonts.bold_30, 260, (255, 255, 255, 255), glow=0.5)
        stx.append((sp_cl, bx_l, by_l + 58, w))
        stx.append((sp_cr, bx_r, by_r + 58, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 04 (b04..b05): fMRI Brain Scan — Separating Cash Triggers Physical Pain!
    # =========================================================================
    w = _shot_win(t, b04, b05)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b04, b05, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_h4 = get_fitted_text_sprite("کشفِ عجیبِ اسکنِ مغزی:", fonts.eb_68, 860, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_h4, 540, 370, w))

        draw_human_figure(cs, 540, 1215, scale=3.35, alpha=w * 0.80, lw=2.5)
        draw_human_figure(cg, 540, 1215, scale=3.35, alpha=w * 0.30, lw=5.2)
        # Pulsing fMRI target centered directly on character's head (y = 752)!
        head_y = 1215 - 138 * 3.35
        draw_hypnotic_chronograph_ring(cs, cg, 540, head_y, 78.0, t, alpha=w * 0.95, draw_p=1.0, speed=2.2)
        draw_star4(cs, 540, head_y, 20.0, w)
        draw_star4(cg, 540, head_y, 36.0, w * 0.85)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 05 (b05..b06): Physical Pain Center Explodes on Cash Handover!
    # =========================================================================
    w = _shot_win(t, b05, b06)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b05, b06, base_in=0.92) + impact_punch(t, b05 + 0.06, 0.048, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_h5 = get_fitted_text_sprite("مرکزِ «دردِ فیزیکی» روشن می‌شه!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.92)
        stx.append((sp_h5, 540, 375, w))

        draw_shockwave_ring(cs, cg, 540, 775, clamp((t - b05) / 0.70), max_r=290, alpha=w * 0.88)
        draw_hypnotic_chronograph_ring(cs, cg, 540, 775, 135.0, t, alpha=w * 0.95, draw_p=1.0, speed=2.6)
        draw_banknote(cs, cg, 540, 775, w=205, h=98, alpha=w)
        draw_ecg_waveform(cs, cg, 145, 935, 1085, t, amp=58.0, alpha=w)
        draw_safe_card(cs, cg, stx, 540, 1225, 760, 96, [("شمردنِ اسکناس = روشن شدنِ آژیرِ درد در مغز!", fonts.bold_30, 0, (255, 255, 255, 255), 0.5)], alpha=w, glow_border=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 06 (b06..b07): Natural Emergency Brake Stopping Impulse Cliff!
    # =========================================================================
    w = _shot_win(t, b06, b07)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b06, b07, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        bp = ease_out_cubic(clamp((t - b06) / 0.50))

        sp_h6 = get_fitted_text_sprite("این درد، «ترمزِ محافظِ» جیبِ تو بود!", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.8)
        stx.append((sp_h6, 540, 375, w))

        # Cliff edge on left + glowing vertical shield wall stopping character safely!
        draw_glow_line(cs, cg, 330, 1145, 900, 1145, w * 0.85, lw_s=3.0)
        draw_glow_line(cs, cg, 330, 1145, 255, 1285, w * 0.70, lw_s=2.6, dashed=True)
        # Glowing brake barrier slamming down at x=435
        bar_y = 775 + (1.0 - bp) * (-120)
        for ctx, lw, al in ((cs, 3.2, w * 0.96), (cg, 7.0, w * 0.48)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 412, bar_y, 44, 370 * bp, 10)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()
        draw_character_with_phone(cs, cg, 625, 1145, scale=1.75, raise_p=0.85, screen_glow=0.9, alpha=w, t=t)
        sp_cl6 = get_fitted_text_sprite("پرتگاهِ خریدِ هیجانی", fonts.reg_26, 260, (195, 195, 212, 255))
        stx.append((sp_cl6, 235, 1085, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 07 (b07..b08): Brands & Platforms Scanning How to Remove Your Brake!
    # =========================================================================
    w = _shot_win(t, b07, b08)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b07, b08, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        draw_observatory_eye(cs, cg, 540, 355, 52.0, t, alpha=w, scan_targets=[(380, 1060), (540, 1020), (700, 1060)])
        sp_h7 = get_fitted_text_sprite("چطور این ترمزِ مغز رو از کار بندازن؟", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.78)
        stx.append((sp_h7, 540, 525, w))
        draw_character_with_phone(cs, cg, 540, 1185, scale=1.95, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 08 (b08..b09): HERO SHOT — Giant Anesthesia Syringe Injecting Card!
    # =========================================================================
    w = _shot_win(t, b08, b09)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b08, b09, base_in=0.92) + impact_punch(t, b08 + 0.06, 0.05, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        inj_p = ease_out_cubic(clamp((t - b08) / 0.65))

        sp_h8 = get_fitted_text_sprite("«آمپولِ بی‌حسیِ پرداخت»", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.94)
        stx.append((sp_h8, 540, 370, w))

        draw_credit_card(cs, cg, 445, 925, w=330, h=206, alpha=w, waves=True)
        # Giant syringe descending diagonally from upper right into the card!
        draw_anesthesia_syringe(cs, cg, 545, 845, angle=math.radians(142), plunge_p=inj_p, alpha=w)
        draw_shockwave_ring(cs, cg, 545, 845, clamp((t - b08) / 0.70), max_r=220, alpha=w * 0.85)

        draw_safe_card(cs, cg, stx, 540, 1205, 780, 96, [("حذفِ لمسِ اسکناس = بی‌حس شدنِ مرکزِ درد!", fonts.bold_30, 0, (255, 255, 255, 255), 0.55)], alpha=w, glow_border=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 09 (b09..b10): POV 1-Click Saved Card + Zero-Fee Installments!
    # =========================================================================
    w = _shot_win(t, b09, b10)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b09, b10, base_in=0.92)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        tap_u = ease_out_cubic(clamp((t - b09 - 0.15) / 0.35))
        draw_pov_phone_in_hand(cs, cg, 540, 835, 386, 650, thumb_swipe=0.0, thumb_tap=tap_u, alpha=w, draw_p=1.0)

        sp_p1 = get_fitted_text_sprite("پرداختِ ۱ کلیکی", fonts.bold_44, 248, (255, 255, 255, 255), glow=0.7)
        sp_p2 = get_fitted_text_sprite("شماره کارت: ذخیره‌شده", fonts.reg_26, 248, (205, 205, 222, 255))
        sp_p3 = get_fitted_text_sprite("۴ قسطِ بدونِ کارمزد!", fonts.bold_30, 248, (255, 255, 255, 255), glow=0.6)
        stx.append((sp_p1, 534, 608, w))
        stx.append((sp_p2, 534, 678, w))
        stx.append((sp_p3, 534, 745, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 10 (b10..b11): Pleasure Now vs Pain Months Later (Split Timeline)!
    # =========================================================================
    w = _shot_win(t, b10, b11)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b10, b11, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_h10 = get_fitted_text_sprite("جداسازیِ «لذتِ خرید» از «دردِ پرداخت»:", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.78)
        stx.append((sp_h10, 540, 370, w))

        draw_glow_line(cs, cg, 540, 520, 540, 1210, w * 0.45, dashed=True)
        # Right (Today: Instant Dopamine) | Left (Months Later: Debt Weight)
        draw_character_with_phone(cs, cg, 765, 1085, scale=1.65, raise_p=1.0, screen_glow=1.0, alpha=w, t=t)
        draw_star4(cs, 765, 735, 24.0, w)
        draw_human_figure(cs, 315, 1085, scale=1.65, alpha=w * 0.72, lw=2.5)
        draw_safe_card(cs, cg, stx, 315, 735, 290, 88, [("سررسیدِ قسط‌ها!", fonts.bold_30, 0, (230, 230, 245, 255), 0.3)], alpha=w)

        sp_r10 = get_fitted_text_sprite("امروز: دوپامینِ خرید!", fonts.bold_30, 340, (255, 255, 255, 255), glow=0.55)
        sp_l10 = get_fitted_text_sprite("ماه‌های بعد: فشارِ قسط!", fonts.bold_30, 340, (198, 198, 215, 255))
        stx.append((sp_r10, 765, 1185, w))
        stx.append((sp_l10, 315, 1185, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 11 (b11..b12): Slicing 1,000,000 into 4 Tiny Harmless 250 Cubes!
    # =========================================================================
    w = _shot_win(t, b11, b12)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b11, b12, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        sp_p = ease_out_cubic(clamp((t - b11) / 0.55))

        sp_h11 = get_fitted_text_sprite("خطای دیدِ مغز روی اعدادِ خُردشده:", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_h11, 540, 370, w))

        # Top: Giant 1,000,000 block -> Bottom: 4 small 250 blocks separated!
        draw_safe_card(cs, cg, stx, 540, 575, 520, 122, [("۱,۰۰۰,۰۰۰ تومن (ترسناک!)", fonts.bold_44, 0, (255, 255, 255, 255), 0.7)], alpha=w * 0.9, glow_border=True)
        for qi in range(4):
            qx = 195 + qi * 230
            qy = 925 + (1.0 - sp_p) * (-80)
            draw_safe_card(cs, cg, stx, qx, qy, 192, 138, [("۲۵۰", fonts.eb_68, -14, (255, 255, 255, 255), 0.5), ("قسط " + fa(qi + 1), fonts.light_22, 42, (195, 195, 212, 255), 0.0)], alpha=w * sp_p)
        sp_b11 = get_fitted_text_sprite("مغزت ۴ تا ۲۵۰ رو «تقریباً رایگان» حس می‌کنه!", fonts.bold_30, 820, (220, 220, 236, 255))
        stx.append((sp_b11, 540, 1165, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 12 (b12..b13): 1X Cash vs 2X Numbed Spending Columns!
    # =========================================================================
    w = _shot_win(t, b12, b13)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b12, b13, base_in=0.92) + impact_punch(t, tc["c12_boom"], 0.045, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        rp = ease_out_cubic(clamp((t - b12) / 0.65))

        sp_h12 = get_fitted_text_sprite("تا ۲ برابر خرجِ بیشتر!", fonts.eb_84, 880, (255, 255, 255, 255), glow=0.92)
        stx.append((sp_h12, 540, 380, w))

        draw_glow_line(cs, cg, 165, 1175, 915, 1175, w * 0.6)
        # Right column: 1X Cash (210px) | Left column: 2X Card/BNPL (440px)!
        for bx, bh, num_t, lbl_t, hi in (
            (745, 210 * rp, "۱ برابر", "پرداختِ نقدی", False),
            (335, 440 * rp, "۲ برابر!", "کارت و قسطی", True),
        ):
            for ctx, lw, al in ((cs, 3.0 if hi else 2.5, w * 0.95), (cg, 6.6 if hi else 5.0, w * 0.42)):
                ctx.save(); ctx.set_dash([])
                rounded_rect_path(ctx, bx - 135, 1175 - bh, 270, bh, 16)
                if ctx is cs and hi:
                    ctx.set_source_rgba(1, 1, 1, 0.15 * w); ctx.fill_preserve()
                ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
                ctx.restore()
            sp_n = get_fitted_text_sprite(num_t, fonts.eb_68 if hi else fonts.bold_44, 240, (255, 255, 255, 255), glow=0.8 if hi else 0.2)
            sp_l = get_fitted_text_sprite(lbl_t, fonts.bold_30, 260, (255, 255, 255, 255) if hi else (190, 190, 208, 255))
            stx.append((sp_n, bx, 1175 - bh - 54, w * rp))
            stx.append((sp_l, bx, 1235, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 13 (b13..b14): Paycheck Bar Devoured by 10 Tiny Installments!
    # =========================================================================
    w = _shot_win(t, b13, b14)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b13, b14, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        drain_p = ease_in_out_cubic(clamp((t - b13) / max(0.55, (b14 - b13) * 0.78)))

        sp_h13 = get_fitted_text_sprite("اولِ ماه: حقوقت قبل از رسیدن بلعیده شده!", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.78)
        stx.append((sp_h13, 540, 375, w))

        # Horizontal paycheck battery draining from 100% down to 12%!
        rem_w = 720 * (1.0 - 0.86 * drain_p)
        for ctx, lw, al in ((cs, 2.9, w * 0.96), (cg, 6.2, w * 0.44)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 180, 625, 720, 108, 18)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            if ctx is cs:
                rounded_rect_path(ctx, 188, 633, max(24, rem_w - 16), 92, 12)
                ctx.set_source_rgba(1, 1, 1, 0.82 * w); ctx.fill()
            ctx.restore()

        # 4 Tethered installment weights hanging underneath draining the bar!
        for wi_k, wx_k in enumerate((255, 445, 635, 825)):
            draw_glow_line(cs, cg, wx_k, 733, wx_k, 885, w * 0.68, dashed=True)
            draw_safe_card(cs, cg, stx, wx_k, 935, 165, 84, [("قسط " + fa(wi_k + 1), fonts.bold_30, 0, (235, 235, 248, 255), 0.35)], alpha=w)
        draw_human_figure(cs, 540, 1245, scale=1.55, alpha=w * 0.85, lw=2.6)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 14 (b14..b15): POV Phone — Tempting "Buy Now, Pay in 4 Months" Hook!
    # =========================================================================
    w = _shot_win(t, b14, b15)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b14, b15, base_in=0.92)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        draw_pov_phone_in_hand(cs, cg, 540, 835, 386, 650, thumb_swipe=0.0, thumb_tap=0.0, alpha=w, draw_p=1.0)

        sp_b0 = get_fitted_text_sprite("شعارِ محبوبِ فروشگاه‌ها:", fonts.light_22, 248, (185, 185, 202, 255))
        sp_b1 = get_fitted_text_sprite("«همین الان بخر،", fonts.bold_44, 248, (255, 255, 255, 255), glow=0.7)
        sp_b2 = get_fitted_text_sprite("۴ ماه دیگه بده!»", fonts.bold_44, 248, (255, 255, 255, 255), glow=0.7)
        stx.append((sp_b0, 534, 595, w))
        stx.append((sp_b1, 534, 678, w))
        stx.append((sp_b2, 534, 755, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 15 (b15..b16): Light-Blade Slicing the Anesthesia Syringe in Half!
    # =========================================================================
    w = _shot_win(t, b15, b16)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b15, b16, base_in=0.92) + impact_punch(t, b15 + 0.06, 0.048, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        sl_p = ease_out_cubic(clamp((t - b15) / 0.45))

        sp_h15 = get_fitted_text_sprite("چطور اثرِ این بی‌حسی رو خنثی کنی؟", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.88)
        stx.append((sp_h15, 540, 385, w))

        draw_anesthesia_syringe(cs, cg, 420, 885, angle=0.15, plunge_p=0.5, alpha=w * 0.85)
        draw_glow_line(cs, cg, 210, 1045, 210 + 660 * sl_p, 1045 - 320 * sl_p, w, lw_s=4.2, lw_g=10.5)
        draw_star4(cs, 210 + 660 * sl_p, 1045 - 320 * sl_p, 24.0, w)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 16 (b16..b17): Antidote 1 — Delete Saved Card Numbers!
    # =========================================================================
    w = _shot_win(t, b16, b17)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b16, b17, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_a1 = get_fitted_text_sprite("پادزهرِ ۱: شماره کارتت رو ذخیره نکن!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.86)
        stx.append((sp_a1, 540, 385, w))

        draw_credit_card(cs, cg, 540, 815, w=370, h=230, alpha=w, waves=False)
        # Bold glowing X deleting auto-saved card!
        draw_glow_line(cs, cg, 385, 725, 695, 905, w * 0.95, lw_s=3.8, lw_g=8.5)
        draw_glow_line(cs, cg, 695, 725, 385, 905, w * 0.95, lw_s=3.8, lw_g=8.5)
        draw_pill_badge(cs, cg, stx, "حذفِ پرداختِ خودکار", 540, 1085, fonts.bold_30, alpha=w, glow=True, pad_x=34, pad_y=12)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 17 (b17..b18): 20 Seconds of Manual Typing Wakes Up the Prefrontal Brain!
    # =========================================================================
    w = _shot_win(t, b17, b18)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b17, b18, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_h17 = get_fitted_text_sprite("۲۰ ثانیه تایپ = بیدار شدنِ منطقِ مغز!", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.8)
        stx.append((sp_h17, 540, 385, w))

        draw_hypnotic_chronograph_ring(cs, cg, 540, 650, 92.0, t, alpha=w * 0.92, draw_p=1.0, speed=1.8)
        sp_20 = get_text_sprite(fa("20s"), fonts.bold_44, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_20, 540, 650, w))
        draw_character_at_desk(cs, cg, 540, 1145, scale=1.22, t=t, alpha=w)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 18 (b18..b19): Antidote 2 — Pause Before Any Installment Purchase!
    # =========================================================================
    w = _shot_win(t, b18, b19)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b18, b19, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_a2 = get_fitted_text_sprite("پادزهرِ ۲: تستِ «اسکناسِ توی دست»!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.86)
        stx.append((sp_a2, 540, 385, w))
        draw_character_with_phone(cs, cg, 540, 1145, scale=1.95, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)
        sp_q18 = get_text_sprite("؟", fonts.eb_84, (255, 255, 255, 255), glow=0.9)
        stx.append((sp_q18, 540, 675, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 19 (b19..b20): "If Full Cash Were in My Hand Right Now, Would I Buy It?"
    # =========================================================================
    w = _shot_win(t, b19, b20)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b19, b20, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_h19 = get_fitted_text_sprite("«اگه کلِ پولش الان نقد دستم بود، می‌خریدم؟»", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.82)
        stx.append((sp_h19, 540, 385, w))

        draw_spotlight_cone(cs, cg, 540, 480, 330, 750, 960, alpha=w * 0.35)
        for bi in range(5):
            draw_banknote(cs, cg, 540 + (bi - 2) * 28, 795 - bi * 18, w=250, h=122, rot=(bi - 2) * 0.05, alpha=w)
        draw_safe_card(cs, cg, stx, 540, 1095, 760, 102, [("تصورِ شمردنِ اسکناس، بی‌حسی رو فوری می‌شکنه!", fonts.bold_30, 0, (255, 255, 255, 255), 0.5)], alpha=w, glow_border=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 20 (b20..b21): If NO -> It's Not Need, It's Anesthesia!
    # =========================================================================
    w = _shot_win(t, b20, b21)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b20, b21, base_in=0.92) + impact_punch(t, b20 + 0.06, 0.045, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_h20 = get_fitted_text_sprite("اگه جوابت «نه» بود = تله‌ی بی‌حسی!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.88)
        stx.append((sp_h20, 540, 405, w))
        draw_safe_card(cs, cg, stx, 540, 815, 680, 210, [
            ("نیازِ واقعی نیست؛", fonts.bold_44, -36, (255, 255, 255, 255), 0.65),
            ("فقط دردِ پرداختش بی‌حس شده!", fonts.bold_30, 42, (215, 215, 232, 255), 0.35),
        ], alpha=w, glow_border=True)
        draw_shockwave_ring(cs, cg, 540, 815, clamp((t - b20) / 0.65), max_r=310, alpha=w * 0.78)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 21 (b21..b22): Liberation — Don't Pre-Sell Your Tomorrow!
    # =========================================================================
    w = _shot_win(t, b21, b22)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b21, b22, base_in=0.94) + impact_punch(t, b21 + 0.06, 0.042, 0.44)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        burst_u = clamp((t - b21) / 1.10)
        if burst_u > 0.01:
            al_sh = w * (1.0 - burst_u * 0.65)
            for k in range(20):
                ang = k * (2 * math.pi / 20.0)
                r_in = 85.0 + 260.0 * ease_out_cubic(burst_u)
                draw_glow_line(cs, cg, 540 + math.cos(ang)*r_in, 835 + math.sin(ang)*r_in,
                               540 + math.cos(ang)*(r_in+22), 835 + math.sin(ang)*(r_in+22), al_sh, lw_s=2.4)

        sp_h21 = get_fitted_text_sprite("فردات رو با بی‌حسیِ امروز پیش‌فروش نکن!", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_h21, 540, 390, w))
        draw_glow_line(cs, cg, 220, 1155, 860, 1155, w * 0.65)
        draw_character_with_phone(cs, cg, 540, 1155, scale=1.95, raise_p=0.12, screen_glow=0.0, alpha=w, t=t)
        draw_star4(cs, 540, 1155 - 148 * 1.95, 22.0, w)
        draw_star4(cg, 540, 1155 - 148 * 1.95, 38.0, w * 0.78)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 22 (b22..b23): Transition Question — Which Buyer Type Are You?
    # =========================================================================
    w = _shot_win(t, b22, b23)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b22, b23, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        sp_h22 = get_fitted_text_sprite("تو موقعِ خرید کدوم مدلی هستی؟", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.88)
        stx.append((sp_h22, 540, 420, w))
        draw_banknote(cs, cg, 735, 845, w=250, h=124, rot=0.06, alpha=w)
        draw_credit_card(cs, cg, 345, 845, w=250, h=156, rot=-0.06, alpha=w, waves=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 23 (b23..b24): Interactive Two-Pedestal Comment Arena (1 vs 2)!
    # =========================================================================
    w = _shot_win(t, b23, b24)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b23, b24, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=815)
        rp = ease_out_cubic(clamp((t - b23) / 0.45))

        sp_q23 = get_fitted_text_sprite("صادقانه انتخاب کن: ۱ یا ۲؟", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.78)
        stx.append((sp_q23, 540, 365, w))

        for bx, num_s, t1_s, t2_s in (
            (745, "۱", "نقد و حساب‌شده", "ترمزِ خرج‌کردنم فعاله!"),
            (335, "۲", "اسیرِ قسط و کارت!", "بی‌حسی کارِ دستم داده"),
        ):
            ph = 350 * rp
            by_top = 1065 - ph
            for ctx, lw, al in ((cs, 2.9, w * 0.96), (cg, 6.4, w * 0.44)):
                ctx.save(); ctx.set_dash([])
                rounded_rect_path(ctx, bx - 165, by_top, 330, ph, 22)
                if ctx is cs:
                    ctx.set_source_rgba(0.04, 0.04, 0.06, 0.94 * w); ctx.fill_preserve()
                ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
                ctx.restore()
            sp_n = get_text_sprite(num_s, fonts.eb_84, (255, 255, 255, 255), glow=0.85)
            sp_a = get_fitted_text_sprite(t1_s, fonts.bold_30, 290, (255, 255, 255, 255))
            sp_b = get_fitted_text_sprite(t2_s, fonts.light_22, 290, (195, 195, 212, 255))
            stx.append((sp_n, bx, by_top + 105, w * rp))
            stx.append((sp_a, bx, by_top + 215, w * rp))
            stx.append((sp_b, bx, by_top + 278, w * rp))

        draw_character_with_phone(cs, cg, 540, 695, scale=1.15, raise_p=0.95, screen_glow=1.0, alpha=w * rp, t=t)
        draw_safe_card(cs, cg, stx, 540, 1185, 820, 96, [("عددش رو همین الان تو کامنت بنویس: ۱ یا ۲؟", fonts.bold_30, 0, (255, 255, 255, 255), 0.6)], alpha=w, glow_border=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=815)

    # =========================================================================
    # SHOT 24 (b24..total_dur): Signature @zavieh.penhann Brand Endplate
    # =========================================================================
    w9 = window_fade(t, b24, total_dur + 0.5, fi=0.36, fo=0.55)
    if w9 > 0.01:
        lt = max(0.0, t - b24)
        p_logo = ease_out_cubic(clamp(lt / 1.05))
        cx, cy = 540.0, 695.0
        draw_hypnotic_chronograph_ring(cs, cg, cx, cy, 224.0, t, alpha=w9 * p_logo * 0.38, draw_p=p_logo, speed=0.65)

        cs.save(); cs.set_dash([])
        cs.arc(cx, cy, 150, 0, 2 * math.pi * p_logo)
        cs.set_source_rgba(1, 1, 1, 0.22 * w9); cs.set_line_width(1.4); cs.stroke()
        cs.restore()

        vx, vy = cx + 62, cy + 16
        for ctx, lw, al in ((cs, 5.2, w9 * 0.98), (cg, 11.5, w9 * 0.82)):
            set_stroke_draw(ctx, p_logo, 360.0)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            ctx.move_to(vx, vy); ctx.line_to(cx - 102, cy - 84); ctx.stroke()
            ctx.set_source_rgba(1, 1, 1, al * 0.52); ctx.set_line_width(lw * 0.72)
            ctx.move_to(vx, vy); ctx.line_to(cx - 102, cy + 90); ctx.stroke()
            ctx.set_dash([])

        cs.arc(cx - 24, cy + 6, 94, math.radians(142), math.radians(218))
        cs.set_source_rgba(1, 1, 1, 0.45 * w9 * p_logo); cs.set_line_width(1.8); cs.stroke()
        draw_star4(cs, vx, vy, 16 * p_logo, w9)
        draw_star4(cg, vx, vy, 28 * p_logo, w9 * 0.92)

        sp_brand = get_text_sprite(fa("زاویه ذهن"), fonts.eb_84, (255, 255, 255, 255), glow=0.82)
        sp_tag   = get_fitted_text_sprite("زوایایِ پنهانِ اقتصاد، ذهن و زندگی", fonts.reg_34, 880, (198, 198, 210, 255))
        txts.append((sp_brand, 540, 1035, w9 * ease_out_cubic(clamp((lt - 0.15) / 0.7))))
        txts.append((sp_tag,   540, 1138, w9 * ease_out_cubic(clamp((lt - 0.30) / 0.7))))

        pill_a = w9 * ease_out_cubic(clamp((lt - 0.45) / 0.7))
        draw_pill_badge(cs, cg, txts, "@zavieh.penhann", 540, 1255, fonts.med_36, pill_a, glow=True, pad_x=44, pad_y=15)

    return composite_oled_frame(surf_glow, surf_sharp, txts, fonts, t, sub_lines)


# =============================================================================
# MULTIPROCESSING WORKER & CLOUD RENDER PIPELINE
# =============================================================================
_W_FONTS = None
_W_META = None
_W_SG = None
_W_CG = None
_W_SS = None
_W_CS = None


def _worker_init(font_dir: str, meta: dict):
    global _W_FONTS, _W_META, _W_SG, _W_CG, _W_SS, _W_CS
    _W_FONTS = FontBank(font_dir)
    _W_META = meta
    _W_SG = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CG = cairo.Context(_W_SG)
    _W_SS = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CS = cairo.Context(_W_SS)


def _worker_render_frame(frame_idx: int) -> bytes:
    t = frame_idx / FPS
    return render_scene_frame(
        t, _W_META["total_dur"], _W_META["t_cues"], _W_META["sub_lines"],
        _W_FONTS, _W_SG, _W_CG, _W_SS, _W_CS
    )


def save_qa_sheets(font_dir: str, meta: dict, qa_dir: str):
    """Generates raised-subtitle baseline QA strip (y=1520) + 24-shot & 12-scene contact sheets."""
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    sg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cg = cairo.Context(sg)
    ss = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cs = cairo.Context(ss)

    sub_strip = Image.new("RGB", (920, 14 * 105), (0, 0, 0))
    test_ln = meta["sub_lines"][min(4, len(meta["sub_lines"]) - 1)]
    t0_s = test_ln["times"][0]
    crop_y0 = int(round(SUBTITLE_BASELINE_Y - 62))
    for k in range(14):
        tk = t0_s + k * 0.09
        raw = render_scene_frame(tk, meta["total_dur"], meta["t_cues"], meta["sub_lines"], fonts, sg, cg, ss, cs)
        im = Image.frombytes("RGB", (W, H), raw)
        crop = im.crop((80, crop_y0, 1000, crop_y0 + 105))
        for x in range(40):
            crop.putpixel((x, 62), (0, 220, 90))
            crop.putpixel((919 - x, 62), (0, 220, 90))
        sub_strip.paste(crop, (0, k * 105))
    sub_strip.save(os.path.join(qa_dir, "subtitle_strip_verify.png"))

    tc = meta["t_cues"]
    td = meta["total_dur"]
    outro_t0 = td - 4.0

    bounds = _compute_shot_bounds(tc, outro_t0) + [td]
    ts_24 = [0.5 * (bounds[i] + bounds[i + 1]) for i in range(24)]

    pw24, ph24 = 270, 480
    grid24 = Image.new("RGB", (pw24 * 6, ph24 * 4), (16, 16, 20))
    for i, ts in enumerate(ts_24):
        ts_c = max(0.08, min(td - 0.12, ts))
        raw = render_scene_frame(ts_c, td, tc, meta["sub_lines"], fonts, sg, cg, ss, cs)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw24, ph24), Image.Resampling.LANCZOS)
        r, c = divmod(i, 6)
        grid24.paste(im, (c * pw24, r * ph24))
    grid24.save(os.path.join(qa_dir, "storyboard_24_shots.png"))

    pick_12 = [0, 1, 2, 4, 5, 7, 9, 10, 11, 12, 18, 22]
    pw12, ph12 = 360, 640
    grid12 = Image.new("RGB", (pw12 * 4, ph12 * 3), (18, 18, 22))
    for idx_p, s_i in enumerate(pick_12):
        ts_c = max(0.08, min(td - 0.12, ts_24[s_i]))
        raw = render_scene_frame(ts_c, td, tc, meta["sub_lines"], fonts, sg, cg, ss, cs)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw12, ph12), Image.Resampling.LANCZOS)
        r, c = divmod(idx_p, 4)
        grid12.paste(im, (c * pw12, r * ph12))
    grid12.save(os.path.join(qa_dir, "storyboard_12_scenes.png"))


def run_cloud_render(font_dir: str, work_dir: str, out_mp4: str, qa_dir: str, whisper_size: str = "medium"):
    import multiprocessing as mp
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(qa_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)

    print("=== [1/3] Building Studio v4.3 High-Loudness Master Audio (Locked Rasalgethi + Velvet Score + Foley) ===", flush=True)
    meta = build_episode_audio(
        segments=SCRIPT_SEGMENTS,
        sfx_cue_map=SFX_CUE_MAP,
        work_dir=work_dir,
        voice_name=LOCKED_SIGNATURE_VOICE,
        tail_pad_sec=4.0,
        whisper_size=whisper_size,
    )

    total_dur = meta["total_dur"]
    total_frames = int(round(total_dur * FPS))
    workers = max(1, mp.cpu_count())
    print(f"=== [2/3] Rendering {total_frames} frames (24 Rapid Shots) @ {W}x{H} {FPS}fps on {workers} CPU cores (CRF 14) ===", flush=True)

    ff_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
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

    with mp.Pool(processes=workers, initializer=_worker_init, initargs=(font_dir, meta), maxtasksperchild=450) as pool:
        for fn, rgb_bytes in enumerate(pool.imap(_worker_render_frame, range(total_frames), chunksize=10)):
            proc.stdin.write(rgb_bytes)
            if fn % 360 == 0 or fn == total_frames - 1:
                el = time.time() - t0
                print(f"  Frame {fn+1:4d}/{total_frames} ({(fn+1)/total_frames*100:5.1f}%) | {(fn+1)/max(0.01,el):5.1f} fps", flush=True)

    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg exited with code {rc}")

    print("=== [3/3] Generating 24-Shot & 12-Scene QA Verification Sheets ===", flush=True)
    save_qa_sheets(font_dir, meta, qa_dir)
    subprocess.check_call(["cp", meta["align_json"], os.path.join(qa_dir, "alignment.json")])
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"=== COMPLETE: {out_mp4} ({sz_mb:.2f} MB, {total_dur:.2f}s @ 60fps) ===", flush=True)


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
        print("Usage: python src/episodes/ep08_payment_anesthesia.py --cloud-render <fonts> <work> <out.mp4> <qa_dir> [whisper_size]")
