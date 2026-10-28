"""
Episode 09 — Studio v6.0 Sapphire Rim-Lit Glassmorphic UI & 3D Character Master Sample
Reference Style: Sapphire Rim-Lit 3D Character + Travelling-Laser Dark Glass UI (https://pin.it/5EdbcB1Tn)
Topic: «تله‌ی قطعیت؛ چرا همه‌چیز رو درست حساب می‌کنی ولی باز ضرر می‌کنی؟»
Page: زاویه ذهن (@zavieh.penhann)

Key Studio v6.0 Features:
  - Vignetted Architectural Cyan Blueprint Grid over #02050A Obsidian
  - Volumetric 3D Fresnel Rim-Lit Characters (Side Desk + Monitor + Floor Reflection + '???',
    and Front Thinking Pose behind Laptop & Coffee Mug with Blinking Glowing Dot-Eyes)
  - Travelling Saber-Laser Frosted Glass Cards + Horizontal Anamorphic Optical Flares
  - 3D Glass Emerald Check / Crimson Cross Medallions, 3-Row Cyan-Sphere Checklist,
    Amber Shock-Event Cards, 70%/30% Split Probability Bar, Red-Strikethrough Mind-Shift Card,
    Protected Risk-Cap Chart, Twin Speedometer Gauges, & Sapphire Pill CTA!
  - Locked Rasalgethi Voice + -0.34st + Velvet Ambient Score + High-Loudness Broadcast Master (-14 dB)
  - Raised Instagram-Safe Minimalist Subtitle (y = 1515.0, 0.00px baseline lock).
"""
import os, sys, math, time, subprocess
import cairocffi as cairo
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.engine.audio_master import build_episode_audio, LOCKED_SIGNATURE_VOICE
from src.engine.render_core import (
    W, H, FPS, FontBank, clamp, ease_out_cubic, ease_in_out_cubic,
    fa, get_fitted_text_sprite, rounded_rect_path
)
from src.engine.sapphire_ui_core import (
    SAPPHIRE_SUB_Y, C_CYAN_CORE, C_CYAN_MID, C_GREEN, C_RED, C_AMBER,
    exp_in_out, composite_sapphire_frame, get_multitone_persian_sprite,
    draw_laser_glass_card, draw_glass_status_medallion, draw_cyan_sphere_check,
    draw_chart_series, draw_sapphire_desk_scene_side,
    draw_sapphire_thinking_character_front, draw_speedometer_gauge_card
)

EP_CODE = "۰۹"
EP_TITLE = "تله‌ی قطعیت و قانونِ کنترلِ ریسک"

# 28 Crisp, Conversational Tehrani Segments (~63s total -> punchy economy & life storytelling!)
SCRIPT_SEGMENTS = [
    # S01: Side-View 3D Desk Character + Monitor + '???' (0..2)
    ("تا حالا شده قبل از یه خرید یا سرمایه‌گذاری،",         "تا حالا شده قبل از یه خرید یا سرمایه‌گذاری،"),          # 0
    ("همه‌چیز رو مو‌به‌مو حساب و کتاب کنی،",                "همه‌چیز رو مو‌به‌مو حساب و کتاب کنی،"),                 # 1
    ("ولی آخرش ضرر کنی و بگی کجاش اشتباه شد؟",             "ولی آخرش ضرر کنی و بگی کجاش اشتباه شد؟"),              # 2

    # S02: Dual Laser-Rim Chart Cards + 3D Emerald Check & Crimson X (3..5)
    ("عجیبه نه؟ دو نفر یه تصمیمِ کاملاً یکسان می‌گیرن؛",     "دو نفر یه تصمیمِ کاملاً یکسان می‌گیرن؛"),               # 3
    ("اولی سودِ سنگین می‌کنه،",                             "اولی سودِ سنگین می‌کنه،"),                             # 4
    ("ولی دومی همون ماه سرمایه‌ش نصف می‌شه!",               "ولی دومی همون ماه سرمایه‌ش نصف می‌شه!"),               # 5

    # S03: 3-Row Stacked Frosted-Glass Checklist + Multi-Curve Chart (6..9)
    ("شاید قبلِ کار همه‌ی نشونه‌ها عالی بوده:",              "شاید قبلِ کار همه‌ی نشونه‌ها عالی بوده:"),              # 6
    ("روندِ قیمت‌ها دقیقاً طبقِ پیش‌بینی رفته،",              "روندِ قیمت‌ها دقیقاً طبقِ پیش‌بینی رفته،"),              # 7
    ("چند تا آدمِ باتجربه هم تاییدش کردن،",                 "چند تا آدمِ باتجربه هم تاییدش کردن،"),                 # 8
    ("و قبلاً هم با همین روش سود کردی!",                    "و قبلاً هم با همین روش سود کردی!"),                    # 9

    # S04: Shock Event Chart Drop + 3 Amber Factor Cards (10..12)
    ("اما تو دنیای واقعی فقط یه خبرِ ناگهانی،",             "اما تو دنیای واقعی فقط یه خبرِ ناگهانی،"),             # 10
    ("یه تصمیمِ یه‌شبه، یا ترس و هیجانِ بقیه کافیه،",        "یه تصمیمِ یه‌شبه، یا ترس و هیجانِ بقیه کافیه،"),        # 11
    ("تا کلِ نقشه‌ی بی‌نقصت یهویی برعکس بشه!",              "تا کلِ نقشه‌ی بی‌نقصت یهویی برعکس بشه!"),              # 12

    # S05: 70% Cyan vs 30% Red Split Probability Bar (13..15)
    ("چون بهترین تحلیلِ دنیا هم بهت قطعیت نمی‌ده؛",          "بهترین تحلیلِ دنیا هم بهت قطعیت نمی‌ده؛"),             # 13
    ("حتی وقتی هفتاد درصد شانسِ برد داری،",                 "حتی وقتی ۷۰ درصد شانسِ برد داری،"),                   # 14
    ("هنوز سی درصد احتمالِ غافلگیری و شوک هست!",            "هنوز ۳۰ درصد احتمالِ غافلگیری و شوک هست!"),            # 15

    # S06: Cascading 3D Tilted Parallax Cards -> Neon Thought-Cloud (16..17)
    ("آدم‌های عجول با کلِ پولشون می‌پرن وسط،",              "آدم‌های عجول با کلِ پولشون می‌پرن وسط،"),              # 16
    ("چون توی ذهنشون دنبالِ تضمینِ صددرصد می‌گردن!",        "چون دنبالِ تضمینِ ۱۰۰ درصد می‌گردن!"),                 # 17

    # S07: Red-Strikethrough Old Question -> New Question + Front 3D Thinking Character (18..20)
    ("پس از امروز این سؤالِ اشتباه رو بذار کنار:",          "پس از امروز این سؤالِ اشتباه رو بذار کنار:"),          # 18
    ("نگو آیا مطمئنم این کار صددرصد می‌گیره؟",             "نگو: «آیا مطمئنم این کار ۱۰۰٪ می‌گیره؟»"),             # 19
    ("بپرس اگه برعکس شد، چقدر ضرر می‌کنم و راهِ خروجم چیه؟", "بپرس: «اگه برعکس شد، سقفِ ضرر و راهِ خروجم چیه؟»"),     # 20

    # S08: Protected Stop-Loss Risk Shield Card (21..22)
    ("کسی که سقفِ ضررش رو از قبل بسته،",                   "کسی که سقفِ ضررش رو از قبل بسته،"),                    # 21
    ("با یه شوک حذف نمی‌شه؛ می‌مونه و موجِ بعدی رو می‌گیره!", "با یه شوک حذف نمی‌شه و موجِ بعدی رو می‌گیره!"),        # 22

    # S09: Twin Speedometer Gauges — Market Outcome vs Your Exposure (23..25)
    ("قانونِ طلاییِ پول و زندگی فقط یه جمله‌ست:",           "قانونِ طلاییِ پول و زندگی فقط یه جمله‌ست:"),            # 23
    ("تو هیچ‌وقت نتیجه‌ی بازار رو کنترل نمی‌کنی؛",          "تو هیچ‌وقت «نتیجه‌ی بازار» رو کنترل نمی‌کنی؛"),         # 24
    ("تو فقط اندازه‌ی ریسکِ خودت رو کنترل می‌کنی!",         "فقط «اندازه‌ی ریسکِ خودت» رو کنترل می‌کنی!"),          # 25

    # S10: Interactive 1-vs-2 Glass Cards + Sapphire Pill CTA (26..27)
    ("تو موقعِ تصمیم‌های مالی کدوم مدلی هستی؟",             "تو موقعِ تصمیم‌های مالی کدوم مدلی هستی؟"),             # 26
    ("یک با کلِ پولت می‌ری وسط، یا دو سقفِ ریسک می‌ذاری؟ بنویس!", "عدد ۱ یا ۲ رو همین الان تو کامنت بنویس!"),      # 27
]

SFX_CUE_MAP = [
    ("c01_open",     0,  0, "screen_on",    -0.01),
    ("_c01_q",       2,  2, "ping",          0.02),
    ("c02_dual",     3,  0, "whip",         -0.05),
    ("_c02_win",     4,  1, "chime",         0.00),
    ("_c02_loss",    5,  2, "impact_boom",   0.00),
    ("c03_check",    6,  0, "whoosh",       -0.04),
    ("c03_r1",       7,  0, "click",         0.00),
    ("c03_r2",       8,  0, "click",         0.00),
    ("c03_r3",       9,  0, "pos_beep",      0.00),
    ("c04_shock",   10,  0, "whip",         -0.05),
    ("_c04_drop",   12,  2, "shatter",      -0.02),
    ("c05_prob",    13,  0, "screen_on",    -0.03),
    ("_c05_70",     14,  2, "scan",          0.00),
    ("c06_cards",   16,  0, "whoosh",       -0.04),
    ("c07_think",   18,  0, "whip",         -0.05),
    ("c07_strike",  19,  1, "slash",         0.00),
    ("c07_newq",    20,  0, "chime",         0.00),
    ("c08_shield",  21,  0, "stamp",        -0.02),
    ("c09_gauges",  23,  0, "whip",         -0.05),
    ("_c09_lock",   25,  2, "button_press",  0.00),
    ("c10_cta",     26,  0, "mirror_ring",  -0.02),
    ("_c10_btn",    27,  2, "button_press",  0.02),
]


def _get_seq_bounds(tc: dict, total_dur: float) -> list[float]:
    outro_t0 = max(tc.get("c10_cta", total_dur - 7.5) + 3.6, total_dur - 3.8)
    raw = [
        0.0,
        tc["c02_dual"],     # S01: 3D Desk Character + Monitor + Floor Reflection + '???'
        tc["c03_check"],    # S02: Dual Stacked Laser-Rim Chart Cards + 3D Check / X Medallions
        tc["c04_shock"],    # S03: 3-Row Frosted Glass Checklist + Multi-Curve Chart
        tc["c05_prob"],     # S04: Shock Event Chart Drop + 3 Amber Factor Cards
        tc["c06_cards"],    # S05: 70% Cyan vs 30% Red Split Probability Bar + Multi-Tone Text
        tc["c07_think"],    # S06: Cascading 3D Tilted Parallax Cards -> Neon Thought-Cloud
        tc["c08_shield"],   # S07: Red-Strikethrough Old Q -> New Q + Front 3D Thinking Character
        tc["c09_gauges"],   # S08: Protected Risk-Cap Shield Chart Bounce
        tc["c10_cta"],      # S09: Twin Speedometer Gauges + Multi-Tone Golden Rule
        outro_t0,           # S10: Interactive 1-vs-2 Sapphire Choice Cards
        total_dur,          # S11: Glowing Sapphire Pill CTA (@zavieh.penhann, exact ref t=49.5s!)
    ]
    out = [raw[0]]
    for v in raw[1:]:
        out.append(max(out[-1] + 0.5, float(v)))
    out[-1] = float(total_dur)
    return out


def _draw_tilted_chart_card(cb, ce, cx: float, cy: float, w: float, h: float, ang: float, ys: list[float], col_line, alpha: float, lp: float):
    if alpha <= 0.01:
        return
    cb.save(); ce.save()
    cb.translate(cx, cy); cb.rotate(ang)
    ce.translate(cx, cy); ce.rotate(ang)
    draw_laser_glass_card(cb, ce, -w * 0.5, -h * 0.5, w, h, 18, alpha, (0.20, 0.50, 0.80), C_CYAN_CORE, lp, False, 0.90)
    draw_chart_series(cb, ce, -w * 0.43, -h * 0.34, w * 0.86, h * 0.68, ys, 1.0, col_line, col_line, alpha * 0.92, True)
    ce.restore(); cb.restore()


# =============================================================================
# MASTER SAPPHIRE SCENE CHOREOGRAPHER (11 Signature Sequences @ 60fps)
# =============================================================================
def render_sapphire_scene(
    t: float,
    total_dur: float,
    tc: dict,
    sub_lines: list[dict],
    fonts: FontBank,
    surf_base,
    cb,
    surf_emissive,
    ce,
) -> bytes:
    for c_cl in (cb, ce):
        c_cl.save()
        c_cl.set_operator(cairo.OPERATOR_CLEAR)
        c_cl.paint()
        c_cl.restore()

    sharp_texts = []
    emissive_texts = []
    grid_strength = 1.0
    B = _get_seq_bounds(tc, total_dur)

    def _fade_io(t0: float, t1: float, fi: float = 0.28, fo: float = 0.26) -> float:
        if t < t0 - 0.05 or t > t1 + 0.05:
            return 0.0
        a = clamp((t - t0) / max(0.05, fi))
        b = clamp((t1 - t) / max(0.05, fo))
        return ease_out_cubic(min(a, b))

    # -------------------------------------------------------------------------
    # S01 (B[0]..B[1]): 3D Fresnel Rim-Lit Desk Character + Monitor + Floor Reflection + '???'
    # -------------------------------------------------------------------------
    if B[0] <= t <= B[1]:
        al = _fade_io(B[0], B[1], 0.25, 0.28)
        grid_strength = 0.28
        q_t0 = B[0] + (B[1] - B[0]) * 0.38
        q_pop = clamp((t - q_t0) / 0.55)
        draw_sapphire_desk_scene_side(cb, ce, t, al, q_pop)

    # -------------------------------------------------------------------------
    # S02 (B[1]..B[2]): Dual Stacked Laser-Rim Chart Cards + 3D Emerald Check & Crimson X
    # -------------------------------------------------------------------------
    elif B[1] < t <= B[2]:
        tl = t - B[1]
        dur = B[2] - B[1]
        al = _fade_io(B[1], B[2])
        u_top = ease_out_cubic(clamp(tl / 0.65))
        u_bot = ease_out_cubic(clamp((tl - dur * 0.34) / 0.65))

        # Top winning card + Emerald 3D Check Medallion
        y_top = 525 + (1.0 - u_top) * 36.0
        draw_laser_glass_card(cb, ce, 108, y_top, 605, 290, 20, al * u_top, C_CYAN_MID, C_CYAN_CORE, t * 0.16)
        draw_chart_series(
            cb, ce, 140, y_top + 48, 535, 195,
            [0.20, 0.26, 0.22, 0.36, 0.44, 0.39, 0.58, 0.53, 0.74, 0.88, 0.95],
            clamp(tl / 1.15), (0.86, 0.96, 1.0), C_CYAN_MID, al * u_top, True
        )
        chk_pop = ease_out_cubic(clamp((tl - 0.55) / 0.38))
        draw_glass_status_medallion(cb, ce, 862, y_top + 145, 70, True, al, chk_pop)
        sharp_texts.append((get_fitted_text_sprite("تصمیمِ یکسان (نفر اول: سود)", fonts.reg_26, 510, (190, 225, 250, 235)), 410, y_top + 34, al * u_top))

        # Bottom losing card + Crimson 3D X Medallion
        if u_bot > 0.02:
            y_bot = 885 + (1.0 - u_bot) * 36.0
            draw_laser_glass_card(cb, ce, 108, y_bot, 605, 290, 20, al * u_bot, C_CYAN_MID, C_CYAN_CORE, t * 0.16 + 0.5)
            draw_chart_series(
                cb, ce, 140, y_bot + 48, 535, 195,
                [0.86, 0.82, 0.88, 0.68, 0.56, 0.62, 0.42, 0.35, 0.40, 0.20, 0.12],
                clamp((tl - dur * 0.34) / 1.05), (1.0, 0.75, 0.78), C_RED, al * u_bot, True
            )
            x_pop = ease_out_cubic(clamp((tl - dur * 0.52) / 0.38))
            draw_glass_status_medallion(cb, ce, 862, y_bot + 145, 70, False, al, x_pop)
            sharp_texts.append((get_fitted_text_sprite("همون تصمیم (نفر دوم: نصف شدن سرمایه!)", fonts.reg_26, 540, (255, 185, 190, 235)), 410, y_bot + 34, al * u_bot))

    # -------------------------------------------------------------------------
    # S03 (B[2]..B[3]): 3-Row Stacked Frosted Glass Checklist + Live Multi-Curve Chart
    # -------------------------------------------------------------------------
    elif B[2] < t <= B[3]:
        tl = t - B[2]
        al = _fade_io(B[2], B[3])
        sharp_texts.append((get_fitted_text_sprite("شاید همه‌ی نشونه‌ها عالی بوده:", fonts.bold_44, 800), 540, 435, al * 0.98))

        rows = [
            (0.18, "روندِ قیمت‌ها دقیقاً طبقِ پیش‌بینیه"),
            (0.95, "آدم‌های باتجربه تاییدش کردن"),
            (1.75, "قبلاً هم با همین روش سود کردی"),
        ]
        for ri, (rt0, rtxt) in enumerate(rows):
            ru = ease_out_cubic(clamp((tl - rt0) / 0.45))
            if ru > 0.02:
                ry = 515 + ri * 124 + (1.0 - ru) * 26.0
                draw_laser_glass_card(cb, ce, 130, ry, 820, 102, 14, al * ru, C_CYAN_MID, C_CYAN_CORE, t * 0.14 + ri * 0.31)
                draw_cyan_sphere_check(cb, ce, 892, ry + 51, 24, al * ru)
                sharp_texts.append((get_fitted_text_sprite(rtxt, fonts.bold_30, 680), 485, ry + 51, al * ru * 0.97))

        cu = ease_out_cubic(clamp((tl - 0.55) / 0.75))
        if cu > 0.02:
            draw_laser_glass_card(cb, ce, 130, 912, 820, 325, 18, al * cu, C_CYAN_MID, C_CYAN_CORE, t * 0.12 + 0.4)
            rev = clamp((tl - 0.55) / 2.2)
            draw_chart_series(cb, ce, 162, 962, 756, 228, [0.38,0.44,0.41,0.54,0.61,0.57,0.71,0.68,0.82,0.79,0.91], rev, (0.95,0.58,0.90), (0.76,0.26,0.86), al * cu, True)
            draw_chart_series(cb, ce, 162, 962, 756, 228, [0.30,0.34,0.39,0.44,0.50,0.54,0.60,0.66,0.71,0.77,0.85], rev, (0.58,0.96,1.0), C_CYAN_MID, al * cu, False)

    # -------------------------------------------------------------------------
    # S04 (B[3]..B[4]): Shock Event Chart Drop + 3 Amber Factor Cards (ref t=21.87s!)
    # -------------------------------------------------------------------------
    elif B[3] < t <= B[4]:
        tl = t - B[3]
        dur = B[4] - B[3]
        al = _fade_io(B[3], B[4])

        # Main chart card with sudden cliff drop at x=50%!
        draw_laser_glass_card(cb, ce, 115, 505, 850, 360, 20, al, (0.28, 0.52, 0.76), C_CYAN_CORE, t * 0.14, False)
        ys_shock = [0.62, 0.72, 0.78, 0.86, 0.84, 0.89, 0.54, 0.28, 0.22, 0.14, 0.18]
        rev_s = clamp(tl / (dur * 0.62))
        draw_chart_series(cb, ce, 155, 555, 770, 265, ys_shock, rev_s, (0.94, 0.96, 1.0), C_AMBER, al, True)

        # Glowing Amber Event Pin at peak before drop (idx=5 -> x = 155 + 0.5*770 = 540, y = 555 + 0.11*265 = 584)
        if rev_s > 0.46:
            pa = al * clamp((rev_s - 0.46) / 0.15)
            for ctx_t, r_p in ((ce, 16.0), (cb, 10.5)):
                ctx_t.save()
                ctx_t.arc(540, 584, r_p, 0, 2 * math.pi)
                ctx_t.set_source_rgba(C_AMBER[0], C_AMBER[1], C_AMBER[2], pa * 0.95)
                ctx_t.fill(); ctx_t.restore()
            sharp_texts.append((get_fitted_text_sprite("شوک!", fonts.bold_30, 130, (255, 210, 105, 250)), 540, 540, pa))

        # 3 Frosted Amber-Accented Event Cards below (exact t=21.87s layout!)
        ev_cards = ["خبرِ ناگهانی", "تصمیمِ یه‌شبه", "هیجانِ بقیه"]
        for ei, etxt in enumerate(ev_cards):
            eu = ease_out_cubic(clamp((tl - 0.35 - ei * 0.32) / 0.48))
            if eu > 0.02:
                ex = 115 + ei * 295
                ey = 915 + (1.0 - eu) * 32.0
                draw_laser_glass_card(cb, ce, ex, ey, 260, 175, 16, al * eu, C_AMBER, (1.0, 0.90, 0.58), 0.18 + ei * 0.25, False)
                # Minimalist glowing amber lightning/pulse icon inside top of mini-card
                for ctx_t, lw in ((ce, 4.2), (cb, 2.6)):
                    ctx_t.save()
                    cx_i, cy_i = ex + 130, ey + 56
                    ctx_t.move_to(cx_i + 6, cy_i - 18); ctx_t.line_to(cx_i - 10, cy_i + 2)
                    ctx_t.line_to(cx_i + 4, cy_i + 2); ctx_t.line_to(cx_i - 6, cy_i + 20)
                    ctx_t.set_source_rgba(C_AMBER[0], C_AMBER[1], C_AMBER[2], al * eu * 0.95)
                    ctx_t.set_line_width(lw); ctx_t.stroke(); ctx_t.restore()
                sharp_texts.append((get_fitted_text_sprite(etxt, fonts.bold_30, 224), ex + 130, ey + 124, al * eu * 0.96))

    # -------------------------------------------------------------------------
    # S05 (B[4]..B[5]): 70% Cyan vs 30% Crimson Split Probability Bar (ref t=26.23s!)
    # -------------------------------------------------------------------------
    elif B[4] < t <= B[5]:
        tl = t - B[4]
        al = _fade_io(B[4], B[5])
        bar_u = ease_out_cubic(clamp(tl / 0.95))

        draw_laser_glass_card(cb, ce, 110, 710, 860, 215, 22, al, (0.22, 0.54, 0.82), C_CYAN_CORE, t * 0.14, False)

        # Cyan 70% bar + Crimson 30% bar
        w_cyan = max(14.0, 535.0 * bar_u)
        w_red = max(14.0, 232.0 * ease_out_cubic(clamp((tl - 0.45) / 0.70)))
        cb.save(); rounded_rect_path(cb, 152, 822, w_cyan, 34, 9); cb.set_source_rgba(0.16, 0.72, 0.98, al * 0.96); cb.fill(); cb.restore()
        ce.save(); rounded_rect_path(ce, 152, 822, w_cyan, 34, 9); ce.set_source_rgba(0.16, 0.72, 0.98, al * 0.46); ce.fill(); ce.restore()

        if tl > 0.42:
            ra = al * clamp((tl - 0.42) / 0.35)
            cb.save(); rounded_rect_path(cb, 698, 822, w_red, 34, 9); cb.set_source_rgba(0.98, 0.24, 0.26, ra * 0.96); cb.fill(); cb.restore()
            ce.save(); rounded_rect_path(ce, 698, 822, w_red, 34, 9); ce.set_source_rgba(0.98, 0.24, 0.26, ra * 0.46); ce.fill(); ce.restore()
            sharp_texts.append((get_fitted_text_sprite("۳۰٪ احتمالِ شوک", fonts.reg_26, 225, (255, 100, 104, 242)), 814, 888, ra))

        pct_val = int(round(70 * bar_u))
        sp_p_s, sp_p_e = get_multitone_persian_sprite(f"{fa(pct_val)}٪", [(f"{fa(pct_val)}٪", (72, 204, 255))], fonts.eb_68, 220)
        sp_1_s, sp_1_e = get_multitone_persian_sprite("بهترین تحلیل هم بهت نمی‌گه", [("نمی‌گه", (72, 204, 255))], fonts.bold_36, 860)
        sp_2_s, sp_2_e = get_multitone_persian_sprite("فردا قطعاً چی پیش میاد!", [("قطعاً چی پیش میاد!", (255, 78, 82))], fonts.bold_36, 860)

        sharp_texts.extend([
            (sp_p_s, 848, 766, al * 0.98),
            (get_fitted_text_sprite("احتمالِ بردِ تحلیل", fonts.reg_26, 260, (185, 210, 235, 235)), 262, 782, al * 0.92),
            (sp_1_s, 540, 1055, al * 0.98),
            (sp_2_s, 540, 1124, al * 0.98),
        ])
        emissive_texts.extend([
            (sp_p_e, 848, 766, al * 0.80),
            (sp_1_e, 540, 1055, al * 0.82),
            (sp_2_e, 540, 1124, al * 0.82),
        ])

    # -------------------------------------------------------------------------
    # S06 (B[5]..B[6]): Cascading 3D Tilted Parallax Cards -> Neon Thought-Cloud (ref t=29.8..32.8s!)
    # -------------------------------------------------------------------------
    elif B[5] < t <= B[6]:
        tl = t - B[5]
        dur = B[6] - B[5]
        al = _fade_io(B[5], B[6])
        morph_u = exp_in_out(clamp((tl - dur * 0.52) / 0.55))

        if morph_u < 0.95:
            ca = al * (1.0 - morph_u)
            specs = [
                (470, 620, -0.10, [0.3,0.5,0.4,0.7,0.6,0.85,0.45,0.2], C_RED, 0.0),
                (590, 775,  0.08, [0.2,0.4,0.65,0.55,0.8,0.5,0.3,0.18], C_AMBER, 0.16),
                (455, 945, -0.13, [0.4,0.6,0.5,0.75,0.9,0.6,0.35,0.22], C_CYAN_MID, 0.32),
            ]
            for sx, sy, sang, sys_l, scol, sdt in specs:
                su = ease_out_cubic(clamp((tl - sdt) / 0.45))
                drift = math.sin(t * 2.0 + sdt * 5.0) * 10.0
                _draw_tilted_chart_card(cb, ce, sx, sy + drift, 560, 255, sang, sys_l, scol, ca * su, t * 0.14 + sdt)

        if morph_u > 0.06:
            ta = al * clamp((morph_u - 0.06) / 0.45)
            # Clean outer scalloped Neon Thought-Cloud + Rising Candlestick Chart inside (exact ref t=32.77s!)
            def _cloud_outline(c):
                c.new_path()
                c.move_to(-185, 36)
                c.curve_to(-235, 18, -228, -58, -158, -68)
                c.curve_to(-148, -138, -52, -162, 6, -118)
                c.curve_to(62, -162, 165, -135, 168, -62)
                c.curve_to(236, -48, 238, 38, 172, 58)
                c.curve_to(162, 118, 72, 132, 14, 102)
                c.curve_to(-45, 134, -148, 118, -185, 36)
                c.close_path()

            cb.save()
            cb.translate(540, 770)
            _cloud_outline(cb)
            cb.set_source_rgba(0.04, 0.08, 0.15, ta * 0.88)
            cb.fill_preserve()
            cb.set_source_rgba(0.70, 0.92, 1.0, ta * 0.85)
            cb.set_line_width(2.8); cb.stroke()
            cb.restore()

            ce.save()
            ce.translate(540, 770)
            _cloud_outline(ce)
            ce.set_source_rgba(C_CYAN_MID[0], C_CYAN_MID[1], C_CYAN_MID[2], ta * 0.72)
            ce.set_line_width(5.0); ce.stroke()
            ce.restore()

            for ctx_t, col, lw in ((ce, C_CYAN_MID, 4.5), (cb, C_CYAN_CORE, 2.8)):
                ctx_t.save()
                ctx_t.translate(540, 770)
                ctx_t.set_line_cap(cairo.LINE_CAP_ROUND); ctx_t.set_line_join(cairo.LINE_JOIN_ROUND)
                # Thought bubbles below-left
                ctx_t.arc(-155, 135, 19, 0, 2 * math.pi)
                ctx_t.set_source_rgba(col[0], col[1], col[2], ta * 0.82); ctx_t.set_line_width(lw); ctx_t.stroke()
                ctx_t.arc(-194, 172, 11, 0, 2 * math.pi); ctx_t.stroke()
                # Mini rising candlesticks inside cloud
                for ck in range(7):
                    cx_k = -115 + ck * 36
                    cy_k = 46 - ck * 14 + (ck % 2) * 10
                    ctx_t.move_to(cx_k, cy_k - 18); ctx_t.line_to(cx_k, cy_k + 18); ctx_t.stroke()
                # Rising neon trend arrow + arrowhead inside cloud
                ctx_t.move_to(-125, 52); ctx_t.line_to(-42, 16); ctx_t.line_to(28, 26); ctx_t.line_to(126, -58)
                ctx_t.set_source_rgba(1.0, 1.0, 1.0, ta * 0.96); ctx_t.set_line_width(lw * 1.25); ctx_t.stroke()
                ctx_t.move_to(102, -58); ctx_t.line_to(126, -58); ctx_t.line_to(122, -34); ctx_t.stroke()
                ctx_t.restore()

            sp_c_s, sp_c_e = get_multitone_persian_sprite("توی دنیای واقعی دنبالِ «تضمینِ صددرصد» نگرد!", [("«تضمینِ صددرصد»", (72, 204, 255))], fonts.bold_36, 860)
            sharp_texts.append((sp_c_s, 540, 1055, ta * 0.98))
            emissive_texts.append((sp_c_e, 540, 1055, ta * 0.82))

    # -------------------------------------------------------------------------
    # S07 (B[6]..B[7]): Old Q (Red Strikethrough!) -> New Q + Front 3D Thinking Character (ref t=37.13s!)
    # -------------------------------------------------------------------------
    elif B[6] < t <= B[7]:
        tl = t - B[6]
        al = _fade_io(B[6], B[7])
        strike_t0 = tc.get("c07_strike", B[6] + 1.1)
        newq_t0 = tc.get("c07_newq", B[6] + 2.4)
        strike_u = ease_out_cubic(clamp((t - strike_t0) / 0.48))
        newq_u = ease_out_cubic(clamp((t - (newq_t0 - 0.15)) / 0.52))

        draw_laser_glass_card(cb, ce, 115, 420, 850, 455, 22, al, (0.22, 0.50, 0.76), C_CYAN_CORE, t * 0.12, False)
        draw_laser_glass_card(cb, ce, 152, 502, 776, 132, 14, al * 0.95, (0.48, 0.18, 0.20), (1.0, 0.35, 0.35), 0.12, False, 0.78)

        # Red status dot + header
        cb.save(); cb.arc(896, 464, 6.5, 0, 2 * math.pi); cb.set_source_rgba(1, 0.28, 0.30, al * 0.98); cb.fill(); cb.restore()
        sharp_texts.append((get_fitted_text_sprite("سؤالِ اشتباه رو متوقف کن", fonts.reg_26, 420, (195, 210, 230, 225)), 718, 464, al * 0.92))
        sharp_texts.append((get_fitted_text_sprite("«آیا مطمئنم این کار صددرصد می‌گیره؟»", fonts.med_32, 710, (180, 192, 212, 220)), 540, 568, al * 0.94))

        # Animated Crimson Strikethrough slicing RTL across old question!
        if strike_u > 0.01:
            x_r = 865.0
            x_l = x_r - 650.0 * strike_u
            ce.save(); ce.move_to(x_r, 568); ce.line_to(x_l, 568); ce.set_source_rgba(1.0, 0.26, 0.28, al * 0.40); ce.set_line_width(4.4); ce.stroke(); ce.restore()
            cb.save(); cb.move_to(x_r, 568); cb.line_to(x_l, 568); cb.set_source_rgba(1.0, 0.30, 0.32, al * 0.96); cb.set_line_width(3.0); cb.stroke(); cb.restore()

        if newq_u > 0.02:
            draw_laser_glass_card(cb, ce, 152, 692, 776, 150, 14, al * newq_u, C_CYAN_MID, C_CYAN_CORE, t * 0.18 + 0.5, True, 0.86)
            sharp_texts.append((get_fitted_text_sprite("به‌جاش اینو بپرس:", fonts.reg_26, 300, (105, 212, 255, 245)), 785, 728, al * newq_u))
            sharp_texts.append((get_fitted_text_sprite("«اگه برعکس شد، سقفِ ضرر و راهِ خروجم چیه؟»", fonts.bold_30, 720, (248, 252, 255, 255)), 540, 788, al * newq_u * 0.99))

        # Volumetric 3D Fresnel Rim-Lit Thinking Character + Laptop + Coffee Mug below!
        draw_sapphire_thinking_character_front(cb, ce, 540, 1142, t, al)

    # -------------------------------------------------------------------------
    # S08 (B[7]..B[8]): Protected Stop-Loss Risk Shield Card (ref t=41.47s!)
    # -------------------------------------------------------------------------
    elif B[7] < t <= B[8]:
        tl = t - B[7]
        dur = B[8] - B[7]
        al = _fade_io(B[7], B[8])
        rev_p = clamp(tl / (dur * 0.72))

        draw_laser_glass_card(cb, ce, 115, 520, 850, 410, 22, al, C_CYAN_MID, C_CYAN_CORE, t * 0.14)
        # Protected Risk Shield line at y_norm = 0.32: dips down, touches shield, then rockets up!
        ys_prot = [0.55, 0.62, 0.48, 0.33, 0.32, 0.46, 0.64, 0.78, 0.88, 0.95]
        draw_chart_series(cb, ce, 158, 575, 764, 305, ys_prot, rev_p, (0.65, 1.0, 0.82), C_GREEN, al, True)

        # Horizontal glowing Stop-Loss Shield Floor at y = 575 + (1 - 0.32)*305 = 782
        for ctx_t, col, lw in ((ce, C_CYAN_MID, 4.0), (cb, C_CYAN_CORE, 2.2)):
            ctx_t.save()
            ctx_t.set_dash([10.0, 8.0])
            ctx_t.move_to(158, 782); ctx_t.line_to(922, 782)
            ctx_t.set_source_rgba(col[0], col[1], col[2], al * 0.85)
            ctx_t.set_line_width(lw); ctx_t.stroke(); ctx_t.restore()

        # Two sleek metric badges underneath (exact ref t=41.47s layout!)
        draw_laser_glass_card(cb, ce, 115, 965, 405, 145, 18, al, C_RED, (1.0, 0.55, 0.55), 0.22, False)
        draw_laser_glass_card(cb, ce, 560, 965, 405, 145, 18, al, C_GREEN, (0.65, 1.0, 0.80), 0.72, False)
        sharp_texts.extend([
            (get_fitted_text_sprite("سقفِ ضررِ بسته شده", fonts.reg_26, 350, (255, 140, 145, 240)), 318, 1012, al * 0.95),
            (get_fitted_text_sprite("حداکثر ۱۰٪", fonts.bold_36, 320, (255, 95, 100, 255)), 318, 1066, al * 0.98),
            (get_fitted_text_sprite("اصلِ سرمایه‌ی امن", fonts.reg_26, 350, (150, 255, 190, 240)), 762, 1012, al * 0.95),
            (get_fitted_text_sprite("۹۰٪ آماده برای موجِ بعد", fonts.bold_30, 365, (95, 255, 150, 255)), 762, 1066, al * 0.98),
        ])

    # -------------------------------------------------------------------------
    # S09 (B[8]..B[9]): Twin Speedometer Gauges — Outcome vs Your Exposure (ref t=45.83s!)
    # -------------------------------------------------------------------------
    elif B[8] < t <= B[9]:
        tl = t - B[8]
        al = _fade_io(B[8], B[9])
        # Left gauge swings erratically (uncontrolled market outcome!)
        needle_left = 0.50 + 0.34 * math.sin(t * 3.7) + 0.12 * math.cos(t * 7.3)
        # Right gauge locks smoothly & steadily onto controlled 18% safe exposure!
        needle_right = 0.26 * ease_out_cubic(clamp((tl - 0.25) / 0.75))

        draw_speedometer_gauge_card(cb, ce, 135, 620, 380, needle_left, False, al, t * 0.08)
        draw_speedometer_gauge_card(cb, ce, 565, 620, 380, needle_right, True, al, t * 0.16 + 0.5)

        sp_10_s, sp_10_e = get_multitone_persian_sprite("۱۰٪", [("۱۰٪", (95, 215, 255))], fonts.bold_44, 160)
        sp_g1_s, sp_g1_e = get_multitone_persian_sprite("تو نتیجه‌ی بازار رو کنترل نمی‌کنی؛", [("نتیجه‌ی بازار", (72, 204, 255))], fonts.bold_36, 880)
        sp_g2_s, sp_g2_e = get_multitone_persian_sprite("فقط اندازه‌ی ریسکِ خودت رو کنترل می‌کنی!", [("اندازه‌ی ریسکِ خودت", (255, 78, 82))], fonts.bold_36, 880)

        sharp_texts.extend([
            (get_fitted_text_sprite("نتیجه‌ی بازار (غیرقابل کنترل)", fonts.reg_26, 330, (145, 165, 190, 215)), 325, 945, al * 0.92),
            (sp_10_s, 755, 872, al * 0.98),
            (get_fitted_text_sprite("سقفِ ریسکِ تو (در دستِ تو)", fonts.reg_26, 330, (205, 235, 255, 245)), 755, 945, al * 0.96),
            (sp_g1_s, 540, 1098, al * 0.98),
            (sp_g2_s, 540, 1166, al * 0.98),
        ])
        emissive_texts.extend([
            (sp_10_e, 755, 872, al * 0.82),
            (sp_g1_e, 540, 1098, al * 0.85),
            (sp_g2_e, 540, 1166, al * 0.85),
        ])

    # -------------------------------------------------------------------------
    # S10 (B[9]..B[10]): Interactive 1-vs-2 Sapphire Glass Choice Cards!
    # -------------------------------------------------------------------------
    elif B[9] < t <= B[10]:
        tl = t - B[9]
        al = _fade_io(B[9], B[10])
        u1 = ease_out_cubic(clamp(tl / 0.45))
        u2 = ease_out_cubic(clamp((tl - 0.30) / 0.45))

        sharp_texts.append((get_fitted_text_sprite("تو کدوم مدلی تصمیم می‌گیری؟", fonts.bold_44, 820), 540, 520, al * 0.98))

        # Right card (RTL #1): All-in gamble (Crimson)
        draw_laser_glass_card(cb, ce, 560, 625, 395, 395, 22, al * u1, C_RED, (1.0, 0.58, 0.58), t * 0.16, False)
        draw_glass_status_medallion(cb, ce, 757, 735, 50, False, al * u1, u1)
        sharp_texts.extend([
            (get_fitted_text_sprite("مدلِ ۱", fonts.eb_68, 260, (255, 95, 100, 255)), 757, 855, al * u1),
            (get_fitted_text_sprite("ورود با کلِ پول", fonts.bold_30, 340, (235, 210, 215, 240)), 757, 945, al * u1),
        ])

        # Left card (RTL #2): Smart risk-capped (Cyan + Emerald)
        draw_laser_glass_card(cb, ce, 125, 625, 395, 395, 22, al * u2, C_CYAN_MID, C_CYAN_CORE, t * 0.16 + 0.5, True)
        draw_glass_status_medallion(cb, ce, 322, 735, 50, True, al * u2, u2)
        sharp_texts.extend([
            (get_fitted_text_sprite("مدلِ ۲", fonts.eb_68, 260, (95, 220, 255, 255)), 322, 855, al * u2),
            (get_fitted_text_sprite("بستنِ سقفِ ریسک", fonts.bold_30, 340, (215, 245, 255, 245)), 322, 945, al * u2),
        ])

    # -------------------------------------------------------------------------
    # S11 (B[10]..total_dur): Signature Glowing Sapphire Pill CTA (exact ref t=49.53s!)
    # -------------------------------------------------------------------------
    else:
        tl = max(0.0, t - B[10])
        al = clamp(tl / 0.35) * clamp((total_dur - t + 0.08) / 0.35)
        pop = ease_out_cubic(clamp(tl / 0.55))
        pw_p = 560.0 * (0.86 + 0.14 * pop)
        ph_p = 138.0
        px_p = 540.0 - pw_p * 0.5
        py_p = 790.0

        # Deep sapphire glowing pill button (modeled directly on ref t=49.53s!)
        cb.save()
        rounded_rect_path(cb, px_p, py_p, pw_p, ph_p, ph_p * 0.5)
        lg_p = cairo.LinearGradient(px_p, py_p, px_p, py_p + ph_p)
        lg_p.add_color_stop_rgba(0.0, 0.08, 0.24, 0.48, al * 0.96)
        lg_p.add_color_stop_rgba(1.0, 0.03, 0.10, 0.24, al * 0.98)
        cb.set_source(lg_p); cb.fill_preserve()
        cb.set_source_rgba(0.35, 0.76, 1.0, al * 0.92)
        cb.set_line_width(3.2); cb.stroke()
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
# MULTIPROCESSING CLOUD WORKER + QA VERIFICATION SHEETS
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
    t = fn / float(FPS)
    return render_sapphire_scene(
        t, _W_META["total_dur"], _W_META["t_cues"], _W_META["sub_lines"],
        _W_FONTS, _W_SB, _W_CB, _W_SE, _W_CE
    )


def save_qa_sheets(font_dir: str, meta: dict, qa_dir: str):
    """Generates 12-panel Sapphire Storyboard Grid + y=1515 Subtitle Baseline Strip."""
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    sb = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cb = cairo.Context(sb)
    se = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ce = cairo.Context(se)

    tc = meta["t_cues"]
    td = meta["total_dur"]
    B = _get_seq_bounds(tc, td)

    # Sample 12 hero moments across all 11 sequences (including both halves of S06!)
    sample_ts = [
        B[0] + (B[1] - B[0]) * 0.65,   # 1. S01 Desk Character + '???'
        B[1] + (B[2] - B[1]) * 0.72,   # 2. S02 Dual Charts + Check / X
        B[2] + (B[3] - B[2]) * 0.78,   # 3. S03 3-Row Checklist + Chart
        B[3] + (B[4] - B[3]) * 0.76,   # 4. S04 Shock Drop + 3 Amber Cards
        B[4] + (B[5] - B[4]) * 0.72,   # 5. S05 70%/30% Split Probability Bar
        B[5] + (B[6] - B[5]) * 0.30,   # 6. S06a 3D Tilted Parallax Cards
        B[5] + (B[6] - B[5]) * 0.82,   # 7. S06b Neon Thought-Cloud
        B[6] + (B[7] - B[6]) * 0.78,   # 8. S07 Strikethrough Q + Front 3D Character
        B[7] + (B[8] - B[7]) * 0.75,   # 9. S08 Protected Stop-Loss Shield
        B[8] + (B[9] - B[8]) * 0.70,   # 10. S09 Twin Speedometer Gauges
        B[9] + (B[10] - B[9]) * 0.68,  # 11. S10 1-vs-2 Choice Cards
        B[10] + (B[11] - B[10]) * 0.55,# 12. S11 Sapphire Pill CTA
    ]

    pw, ph = 360, 640
    grid12 = Image.new("RGB", (pw * 4, ph * 3), (0, 0, 0))
    for i, ts in enumerate(sample_ts):
        ts_c = max(0.1, min(td - 0.15, ts))
        raw = render_sapphire_scene(ts_c, td, tc, meta["sub_lines"], fonts, sb, cb, se, ce)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw, ph), Image.Resampling.LANCZOS)
        r, c = divmod(i, 4)
        grid12.paste(im, (c * pw, r * ph))
    grid12.save(os.path.join(qa_dir, "storyboard_12_sapphire.png"))

    sub_strip = Image.new("RGB", (920, 10 * 100), (0, 0, 0))
    test_ln = meta["sub_lines"][min(4, len(meta["sub_lines"]) - 1)]
    t0_s = test_ln["times"][0]
    crop_y0 = int(round(SAPPHIRE_SUB_Y - 58))
    for k in range(10):
        tk = t0_s + k * 0.09
        raw = render_sapphire_scene(tk, td, tc, meta["sub_lines"], fonts, sb, cb, se, ce)
        im = Image.frombytes("RGB", (W, H), raw)
        crop = im.crop((80, crop_y0, 1000, crop_y0 + 100))
        for x in range(36):
            crop.putpixel((x, 58), (0, 220, 90))
            crop.putpixel((919 - x, 58), (0, 220, 90))
        sub_strip.paste(crop, (0, k * 100))
    sub_strip.save(os.path.join(qa_dir, "subtitle_strip_sapphire.png"))


def run_cloud_render(font_dir: str, work_dir: str, out_mp4: str, qa_dir: str, whisper_size: str = "medium"):
    import multiprocessing as mp
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(qa_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)

    print("=== [1/3] Building Studio v6.0 Master Audio (Locked Rasalgethi + Velvet Score + Foley) ===", flush=True)
    meta = build_episode_audio(
        segments=SCRIPT_SEGMENTS,
        sfx_cue_map=SFX_CUE_MAP,
        work_dir=work_dir,
        voice_name=LOCKED_SIGNATURE_VOICE,
        tail_pad_sec=3.8,
        whisper_size=whisper_size,
    )

    total_dur = meta["total_dur"]
    total_frames = int(round(total_dur * FPS))
    workers = max(1, mp.cpu_count())
    print(f"=== [2/3] Rendering {total_frames} Sapphire Glass-UI frames @ {W}x{H} {FPS}fps on {workers} CPU cores (CRF 14) ===", flush=True)

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

    with mp.Pool(processes=workers, initializer=_worker_init, initargs=(font_dir, meta), maxtasksperchild=400) as pool:
        for fn, rgb_bytes in enumerate(pool.imap(_worker_render_frame, range(total_frames), chunksize=10)):
            proc.stdin.write(rgb_bytes)
            if fn % 360 == 0 or fn == total_frames - 1:
                el = time.time() - t0
                print(f"  Frame {fn+1:4d}/{total_frames} ({(fn+1)/total_frames*100:5.1f}%) | {(fn+1)/max(0.01,el):5.1f} fps", flush=True)

    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg exited with code {rc}")

    print("=== [3/3] Generating Sapphire 12-Panel QA Sheets ===", flush=True)
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
        print("Usage: python src/episodes/ep09_sapphire_risk_control.py --cloud-render <fonts> <work> <out.mp4> <qa_dir> [whisper_size]")
