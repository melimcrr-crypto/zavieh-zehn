"""
Episode 05 (Studio v4.0 — @ensan.besham Hyper-Cut Character & Foley Cinema Edition)
Topic: «چند ساعت از عمرت رو دادی تا اون گوشی دستت باشه؟ (قیمتِ واقعیِ اجناس به ساعتِ عمر)»
Page: زاویه ذهن (@zavieh.penhann)

v4.0 Hyper-Cut Upgrades:
  - 24 Rapid-Fire Visual Shots across ~69s (~2.7s average shot length — exact @ensan.besham cut velocity!)
  - Human Character Protagonist + POV Hand/Thumb Rig acting in nearly every shot (picking up phone with
    volumetric face glow, thumb swiping prices, soul draining from chest, crumbling life pedestal, hunched
    office typing, social envy pedestals, carrying giant boulder-phone, puppet-strings, snapping chains free!)
  - Giant ExtraBold @ensan.besham Focal Numbers (eb_84 / eb_92) in pure #000000 OLED space (minimalist, zero clutter)
  - 38 Multi-Layer Stereo Foley & Cinema Impact SFX cues (+200° sound design upgrade) + D-minor 120-BPM Score
  - Locked Voice: Gemini 'Rasalgethi' + 129-tap @ensan.besham FIR + -0.34st Formant Calibration
  - Subtitles & Boxes: 0.000px baseline-locked 64px-feathered RTL wipe + 100% Zero-Overflow containers
"""
import os, sys, math, time, json, subprocess
import cairocffi as cairo
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.engine.audio_master import build_episode_audio, LOCKED_SIGNATURE_VOICE
from src.engine.render_core import (
    W, H, FPS, FontBank, clamp, ease_out_cubic, ease_in_out_cubic,
    window_fade, fa, get_text_sprite, get_fitted_text_sprite,
    rounded_rect_path, set_stroke_draw, draw_star4,
    draw_human_figure, draw_spotlight_cone, draw_hud_chrome,
    draw_safe_card, draw_pill_badge,
    draw_ambient_particles, draw_cursor_pointer,
    impact_punch, push_camera, pop_camera_and_transform_texts,
    draw_shockwave_ring, draw_hypnotic_chronograph_ring,
    draw_hourglass_monolith, draw_ecg_waveform,
    draw_character_with_phone, draw_pov_phone_in_hand,
    draw_character_at_desk, draw_observatory_eye,
    composite_oled_frame,
)

EP_CODE = "۰۵"
EP_TITLE = "قیمت به ساعتِ عمر"

SCRIPT_SEGMENTS = [
    # 0..5: Hook Sequence (Shots 1..6)
    ("همین گوشیی که الان توی دستته رو،",                "همین گوشیی که الان توی دستته رو،"),                # 0
    ("چند خریدی؟",                                      "چند خریدی؟"),                                      # 1
    ("پنجاه میلیون؟ شصت میلیون؟",                       "۵۰ میلیون؟ ۶۰ میلیون؟"),                           # 2
    ("بذار یه رازِ ترسناک رو بهت بگم:",                  "بذار یه راز ترسناک رو بهت بگم:"),                  # 3
    ("تو براش شصت میلیون پول ندادی؛",                   "تو براش ۶۰ میلیون پول ندادی؛"),                    # 4
    ("تو شیشصد ساعت از عمرت رو دادی!",                  "تو ۶۰۰ ساعت از عمرت رو دادی!"),                    # 5

    # 6..10: Hidden Currency Sequence (Shots 7..9)
    ("ما فکر می‌کنیم با پول خرید می‌کنیم؛",              "ما فکر می‌کنیم با پول خرید می‌کنیم؛"),              # 6
    ("ولی پول فقط یه کاغذِ واسطه‌ست!",                   "ولی پول فقط یه کاغذ واسطه‌ست!"),                   # 7
    ("واحدِ واقعیِ هر خریدی توی دنیا،",                  "واحد واقعی هر خریدی توی دنیا،"),                   # 8
    ("ساعت‌هایی از زندگیِ توئه،",                        "ساعت‌هایی از زندگی توئه،"),                         # 9
    ("که دیگه هیچ‌وقت برنمی‌گردن!",                      "که دیگه هیچ‌وقت برنمی‌گردن!"),                      # 10

    # 11..16: Brutal Math Sequence (Shots 10..14)
    ("بیا خیلی ساده حسابش کنیم:",                       "بیا خیلی ساده حسابش کنیم:"),                       # 11
    ("اگه با رفت‌وآمد و خستگیِ کار،",                    "اگه با رفت‌وآمد و خستگی کار،"),                     # 12
    ("ساعتی صد هزار تومن دربیاری،",                     "ساعتی ۱۰۰ هزار تومن دربیاری،"),                    # 13
    ("اون گوشیِ شصت میلیونی،",                          "اون گوشی ۶۰ میلیونی،"),                            # 14
    ("یعنی هفتاد و پنج روزِ کاملِ کاری!",                "یعنی ۷۵ روز کامل کاری!"),                          # 15
    ("یعنی کلِ یه فصل از جوونیت!",                       "یعنی کل یه فصل از جوونیت!"),                       # 16

    # 17..21: Everyday X-Ray Sequence (Shots 15..17)
    ("حالا با همین عینک به اطرافت نگاه کن:",             "حالا با همین عینک به اطرافت نگاه کن:"),             # 17
    ("کفشِ شیش میلیونی؟",                                "کفش ۶ میلیونی؟"),                                  # 18
    ("شصت ساعت پای کار موندن!",                         "۶۰ ساعت پای کار موندن!"),                          # 19
    ("شامِ پرزرق‌وبرقِ دو میلیونی؟",                     "شام پرزرق‌وبرق ۲ میلیونی؟"),                       # 20
    ("بیست ساعت از آزادیِ خالصت!",                       "۲۰ ساعت از آزادی خالصت!"),                         # 21

    # 22..25: When Things Own You Sequence (Shots 18..20)
    ("تلخ‌ترین جاش کجاست؟",                              "تلخ‌ترین جاش کجاست؟"),                              # 22
    ("وقتی فقط برای چشم‌وهم‌چشمی خرید می‌کنی،",          "وقتی فقط برای چشم‌وهم‌چشمی خرید می‌کنی،"),          # 23
    ("دیگه تو صاحبِ وسایلت نیستی؛",                     "دیگه تو صاحب وسایلت نیستی؛"),                      # 24
    ("اون وسایل صاحبِ عمر و زندگیِ توئن!",               "اون وسایل صاحب عمر و زندگی توئن!"),                # 25

    # 26..28: 3-Second Antidote & Liberation (Shots 21..22)
    ("از امشب قبلِ هر خریدی،",                          "از امشب قبل هر خریدی،"),                           # 26
    ("قیمتش رو به ساعتِ عمرت تقسیم کن؛",                 "قیمتش رو به ساعت عمرت تقسیم کن؛"),                 # 27
    ("ببین واقعاً به اون‌همه زندگی می‌ارزه یا نه!",      "ببین واقعاً به اون‌همه زندگی می‌ارزه یا نه!"),      # 28

    # 29..31: Meta Mirror CTA (Shot 23) + Outro (Shot 24)
    ("گوشیی که الان دستته،",                            "گوشیی که الان دستته،"),                            # 29
    ("چند ماه از عمرت پاش رفته؟",                       "چند ماه از عمرت پاش رفته؟"),                       # 30
    ("عددش رو همین الان تو کامنت بنویس!",                "عددش رو همین الان تو کامنت بنویس!"),                # 31
]

# =============================================================================
# 38 Multi-Layer Stereo Foley, Whip-Cut & Cinema Impact Cues (Studio v4.0)
# Format: (cue_name, seg_idx, word_idx, sfx_kind, time_offset_sec)
# =============================================================================
SFX_CUE_MAP = [
    ("c01_pickup",   0, 0, "screen_on",    0.18),  # Shot 01: Character lifts phone, screen cone lights face
    ("c02_pov",      1, 0, "whip",        -0.05),  # Shot 02: Whip zoom into POV hand holding phone
    ("c03_p50",      2, 0, "swipe",       -0.06),  # Shot 03: Thumb swipes -> 50M
    ("_c03_slam1",   2, 0, "cash_slam",    0.04),
    ("c03_p60",      2, 2, "swipe",       -0.06),  # Thumb swipes -> 60M!
    ("_c03_slam2",   2, 2, "cash_slam",    0.04),
    ("c04_eye",      3, 0, "whip",        -0.04),  # Shot 04: Observatory Eye X-ray scan
    ("_c04_scan",    3, 2, "scan",         0.00),
    ("c05_slash",    4, 0, "whip",        -0.04),  # Shot 05: 60M banknote sliced in half!
    ("_c05_blade",   4, 2, "slash",        0.05),
    ("_c06_riser",   5, 0, "riser",       -0.68),  # Pre-beat tension riser into 600 HOURS!
    ("c06_600",      5, 1, "impact_boom", -0.02),  # Shot 06: 600 HOURS boom + soul stream!
    ("_c06_hb",      5, 3, "heartbeat",    0.05),

    ("c07_paper",    6, 0, "whip",        -0.04),  # Shot 07: Two humans exchanging ghost paper
    ("_c07_vanish",  7, 3, "whoosh",       0.00),
    ("c08_chest",    8, 0, "whip",        -0.04),  # Shot 08: Dive inside human chest heart-clock!
    ("_c08_hb1",     8, 2, "heartbeat",    0.02),
    ("c08_life",     9, 0, "heartbeat",    0.00),
    ("c09_crumble", 10, 0, "crumble",     -0.02),  # Shot 09: Life pedestal crumbles into abyss!

    ("c10_desk",    11, 0, "whip",        -0.04),  # Shot 10: Hunched office worker typing fast
    ("_c10_type1",  12, 0, "typing",       0.02),
    ("_c10_type2",  12, 3, "typing",       0.05),
    ("c11_100k",    13, 0, "stamp",       -0.02),  # Shot 11: 100,000 Toman hourly stamp + worker
    ("_c11_reg",    13, 1, "cash_slam",    0.04),
    ("c12_iphone",  14, 0, "whip",        -0.04),  # Shot 12: Rear Pro iPhone = spinning counter
    ("c13_75d",     15, 0, "domino_burst", 0.00),  # Shot 13: 75-day calendar machine-gun domino burst!
    ("_c13_hit",    15, 2, "stamp",        0.05),
    ("c14_season",  16, 0, "whoosh",      -0.04),  # Shot 14: Whole season of youth blowing away
    ("_c14_ping",   16, 3, "ping",         0.02),

    ("c15_glasses", 17, 0, "click",       -0.02),  # Shot 15: X-ray glasses snap onto character's eyes
    ("_c15_scan",   17, 2, "scan",         0.04),
    ("c16_shoe",    18, 0, "whip",        -0.04),  # Shot 16: Sneaker -> 60 HOURS + treadmill runner
    ("c16_60h",     19, 0, "stamp",       -0.02),
    ("c17_dinner",  20, 0, "whip",        -0.04),  # Shot 17: Silver cloche lifts -> 20 HOURS!
    ("_c17_ding",   20, 1, "bell_ding",    0.04),
    ("c17_20h",     21, 0, "stamp",       -0.02),

    ("c18_envy",    22, 0, "whip",        -0.04),  # Shot 18: Social comparison pedestals
    ("_c18_ping",   23, 2, "ping",         0.02),
    ("c19_boulder", 24, 0, "chain_clink", -0.02),  # Shot 19: Character carrying giant boulder-phone on back!
    ("_c20_riser",  25, 0, "riser",       -0.65),
    ("c20_puppet",  25, 0, "impact_boom", -0.02),  # Shot 20: Puppet-master phone holding human on strings!
    ("_c20_hb",     25, 3, "heartbeat",    0.04),

    ("c21_filter",  26, 0, "whip",        -0.04),  # Shot 21: POV checkout pause (Price / Hourly Life)
    ("_c21_tick",   27, 2, "tick",         0.00),
    ("c22_free",    28, 0, "shatter",      0.06),  # Shot 22: Chains shatter -> character drops phone & awakens!

    ("c23_cta",     29, 0, "whip",        -0.04),  # Shot 23: Mirror meta-shot + 3 rising choice pillars!
    ("_c23_c1",     30, 1, "click",        0.00),
    ("_c23_c2",     31, 0, "click",        0.05),
]


# =============================================================================
# Episode 05 Bespoke Rapid-Shot Vector Helpers
# =============================================================================

def draw_glow_line(cs, cg, x0: float, y0: float, x1: float, y1: float, alpha: float = 1.0, lw_s: float = 2.2, lw_g: float = 5.2):
    if alpha <= 0.01:
        return
    cs.save(); cg.save(); cs.set_dash([]); cg.set_dash([])
    cs.move_to(x0, y0); cs.line_to(x1, y1); cs.set_source_rgba(1, 1, 1, 0.92 * alpha); cs.set_line_width(lw_s); cs.stroke()
    cg.move_to(x0, y0); cg.line_to(x1, y1); cg.set_source_rgba(1, 1, 1, 0.55 * alpha); cg.set_line_width(lw_g); cg.stroke()
    cs.restore(); cg.restore()


def draw_pro_rear_iphone(cs, cg, cx: float, cy: float, w: float, h: float, alpha: float = 1.0, draw_p: float = 1.0):
    """Exact @ensan.besham v03_4M Flagship Rear Triple-Camera Smartphone silhouette."""
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    dp = clamp(draw_p)
    x0, y0 = cx - w / 2.0, cy - h / 2.0
    rad = w * 0.17
    for ctx, lw, al in ((cs, 2.8, alpha * 0.96), (cg, 6.0, alpha * 0.45)):
        ctx.save()
        set_stroke_draw(ctx, dp, 2.2 * (w + h))
        rounded_rect_path(ctx, x0, y0, w, h, rad)
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        # Camera bump module (top-left)
        cw = w * 0.44
        rounded_rect_path(ctx, x0 + w * 0.09, y0 + w * 0.09, cw, cw, cw * 0.26)
        ctx.set_line_width(lw * 0.78); ctx.stroke()
        ctx.set_dash([])
        if dp > 0.45:
            r_lens = cw * 0.17
            bx, by = x0 + w * 0.09, y0 + w * 0.09
            for lx_o, ly_o in ((0.28, 0.28), (0.28, 0.72), (0.72, 0.50)):
                ctx.arc(bx + cw * lx_o, by + cw * ly_o, r_lens, 0, 2 * math.pi); ctx.stroke()
        ctx.restore()


def draw_running_human_60fps(cs, cg, cx: float, foot_y: float, scale: float, t: float, alpha: float = 1.0, facing_left: bool = True):
    """60fps articulated running human figure."""
    if alpha <= 0.01:
        return
    sgn = -1.0 if facing_left else 1.0
    ph = t * 9.5
    hip_x = cx
    hip_y = foot_y - 68.0 * scale + abs(math.sin(ph)) * 7.0 * scale
    sh_x  = hip_x + sgn * 14.0 * scale
    sh_y  = hip_y - 54.0 * scale
    hd_x  = sh_x + sgn * 8.0 * scale
    hd_y  = sh_y - 24.0 * scale

    for ctx, lw, al in ((cs, 2.8, alpha * 0.96), (cg, 5.5, alpha * 0.42)):
        ctx.save(); ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
        ctx.arc(hd_x, hd_y, 15.0 * scale, 0, 2 * math.pi); ctx.stroke()
        ctx.move_to(sh_x, sh_y); ctx.line_to(hip_x, hip_y); ctx.stroke()
        for leg_off, op_m in ((0.0, 1.0), (math.pi, 0.65)):
            sw = math.sin(ph + leg_off)
            lift = max(0.0, math.cos(ph + leg_off))
            kx = hip_x + sgn * (20.0 * sw + 8.0) * scale
            ky = hip_y + (34.0 - 10.0 * lift) * scale
            fx = kx + sgn * (16.0 * sw - 12.0 * lift) * scale
            fy = hip_y + (66.0 - 22.0 * lift) * scale
            ctx.set_source_rgba(1, 1, 1, al * op_m)
            ctx.move_to(hip_x, hip_y); ctx.line_to(kx, ky); ctx.line_to(fx, fy); ctx.stroke()
        for arm_off, op_m in ((math.pi, 1.0), (0.0, 0.65)):
            aw = math.sin(ph + arm_off)
            ex = sh_x + sgn * (18.0 * aw + 6.0) * scale
            ey = sh_y + 24.0 * scale
            hx = ex + sgn * (18.0 * max(-0.2, aw) + 10.0) * scale
            hy = ey - (10.0 + 10.0 * aw) * scale
            ctx.set_source_rgba(1, 1, 1, al * op_m)
            ctx.move_to(sh_x, sh_y); ctx.line_to(ex, ey); ctx.line_to(hx, hy); ctx.stroke()
        ctx.restore()


def draw_sisyphus_human_boulder_phone(cs, cg, cx: float, ground_y: float, scale: float, t: float, alpha: float = 1.0):
    """Human bent at 45 deg pushing/carrying a gigantic monolithic smartphone up a steep slope!"""
    if alpha <= 0.01:
        return
    step_ph = t * 5.6
    bob = abs(math.sin(step_ph)) * 6.5
    # Steep uphill slope line (left-low -> right-high: y(x) = ground_y - (x - cx)*0.24)
    for ctx, lw, al in ((cs, 2.4, alpha * 0.72), (cg, 4.8, alpha * 0.28)):
        ctx.save(); ctx.set_dash([])
        ctx.move_to(110, ground_y + 102); ctx.line_to(970, ground_y - 104)
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        ctx.restore()

    # 1. Draw GIGANTIC Smartphone boulder FIRST on upper-left of character's back so human stays 100% visible!
    for ctx, lw, al in ((cs, 3.2, alpha * 0.96), (cg, 6.8, alpha * 0.48)):
        ctx.save(); ctx.set_dash([])
        ctx.translate(cx - 58 * scale, ground_y - 238 * scale - bob)
        ctx.rotate(-0.58)
        rounded_rect_path(ctx, -92 * scale, -162 * scale, 184 * scale, 324 * scale, 26 * scale)
        if ctx is cs:
            ctx.set_source_rgba(0.03, 0.03, 0.045, 0.94 * alpha); ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        rounded_rect_path(ctx, -28 * scale, -142 * scale, 56 * scale, 10 * scale, 5 * scale); ctx.stroke()
        ctx.restore()

    # 2. Draw Strained Bent Human Body ON TOP (clearly visible head, curved spine, bracing arms & trudging legs!)
    hx_base = cx + 48 * scale
    hy_ground = ground_y - (hx_base - cx) * 0.24
    hip_x, hip_y = hx_base - 24 * scale, hy_ground - 72 * scale - bob
    sh_x, sh_y   = hx_base + 34 * scale, hy_ground - 118 * scale - bob
    hd_x, hd_y   = hx_base + 66 * scale, hy_ground - 122 * scale - bob

    for ctx, lw, al in ((cs, 3.4, alpha * 0.98), (cg, 6.5, alpha * 0.48)):
        ctx.save(); ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
        # Head strained forward
        ctx.arc(hd_x, hd_y, 18 * scale, 0, 2 * math.pi); ctx.stroke()
        # Bent spine
        ctx.move_to(hip_x, hip_y); ctx.line_to(sh_x, sh_y); ctx.stroke()
        # Two trudging legs planted on the slope
        for loff in (0.0, math.pi):
            sw = math.sin(step_ph + loff) * 24 * scale
            fx = hip_x + 8 * scale + sw
            fy = ground_y - (fx - cx) * 0.24 - max(0.0, math.cos(step_ph + loff)) * 14 * scale
            kx = 0.5 * (hip_x + fx) + 14 * scale
            ky = 0.5 * (hip_y + fy) - 6 * scale
            ctx.move_to(hip_x, hip_y); ctx.line_to(kx, ky); ctx.line_to(fx, fy); ctx.stroke()
        # Arms reaching up & back to grip the massive smartphone strap!
        ctx.move_to(sh_x, sh_y)
        ctx.line_to(sh_x - 8 * scale, sh_y - 38 * scale)
        ctx.line_to(sh_x - 46 * scale, sh_y - 54 * scale)
        ctx.stroke()
        # Glowing tether chain across chest holding the boulder-phone
        ctx.set_dash([6.0, 5.0])
        ctx.move_to(sh_x + 8 * scale, sh_y + 8 * scale)
        ctx.line_to(cx - 25 * scale, ground_y - 185 * scale - bob)
        ctx.set_line_width(lw * 0.72); ctx.stroke()
        ctx.restore()


def draw_clock_gear(cs, cg, cx: float, cy: float, r_pitch: float, n_teeth: int, rot_rad: float, alpha: float = 1.0):
    if alpha <= 0.01:
        return
    r_in, r_out = r_pitch - 10.0, r_pitch + 10.0
    step = 2.0 * math.pi / n_teeth
    for ctx, lw, al in ((cs, 2.2, alpha * 0.85), (cg, 4.8, alpha * 0.35)):
        ctx.save(); ctx.set_dash([])
        for i in range(n_teeth):
            a0 = rot_rad + i * step
            pts = [
                (cx + math.cos(a0) * r_in, cy + math.sin(a0) * r_in),
                (cx + math.cos(a0 + step * 0.22) * r_out, cy + math.sin(a0 + step * 0.22) * r_out),
                (cx + math.cos(a0 + step * 0.48) * r_out, cy + math.sin(a0 + step * 0.48) * r_out),
                (cx + math.cos(a0 + step * 0.70) * r_in, cy + math.sin(a0 + step * 0.70) * r_in),
            ]
            if i == 0: ctx.move_to(*pts[0])
            else: ctx.line_to(*pts[0])
            for px, py in pts[1:]: ctx.line_to(px, py)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        ctx.arc(cx, cy, r_pitch * 0.80, 0, 2 * math.pi); ctx.set_line_width(1.4); ctx.stroke()
        ctx.restore()


# =============================================================================
# Master 24-Shot Hyper-Cut Renderer (60fps)
# =============================================================================

def _shot_win(t: float, t0: float, t1: float, fi: float = 0.14, fo: float = 0.16) -> float:
    """Snappy @ensan.besham shot window with fast 8-frame whip transitions (zero sluggish overlap!)."""
    return window_fade(t, t0 - 0.02, t1 + 0.02, fi=fi, fo=fo)


def _shot_cam_z(t: float, t0: float, t1: float, base_in: float = 0.92) -> float:
    """Snappy entry zoom-snap + continuous forward drift + whip-zoom exit!"""
    dur = max(0.35, t1 - t0)
    u = clamp((t - t0) / dur)
    z_in = base_in + (1.0 - base_in) * ease_out_cubic(clamp((t - t0) / 0.28))
    z_drift = 0.032 * u
    z_out = clamp((t - (t1 - 0.18)) / 0.20) ** 2 * 0.09
    return z_in + z_drift + z_out


def _compute_shot_bounds(tc: dict, outro_t0: float) -> list[float]:
    raw = [
        0.0,
        tc["c02_pov"],
        tc["c03_p50"],
        tc["c04_eye"],
        tc["c05_slash"],
        tc["c06_600"] - 0.12,
        tc["c07_paper"],
        tc["c08_chest"],
        tc["c09_crumble"] - 0.10,
        tc["c10_desk"],
        tc["c11_100k"] - 0.10,
        tc["c12_iphone"],
        tc["c13_75d"] - 0.10,
        tc["c14_season"],
        tc["c15_glasses"],
        tc["c16_shoe"],
        tc["c17_dinner"],
        tc["c18_envy"],
        tc["c19_boulder"],
        tc["c20_puppet"] - 0.10,
        tc["c21_filter"],
        tc["c22_free"] - 0.10,
        tc["c23_cta"],
        outro_t0,
    ]
    sb = [0.0]
    for v in raw[1:-1]:
        sb.append(max(sb[-1] + 0.70, float(v)))
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

    # Exact 24-Shot Timeline Boundaries anchored directly to Whisper word timestamps!
    (b01, b02, b03, b04, b05, b06, b07, b08, b09, b10, b11, b12,
     b13, b14, b15, b16, b17, b18, b19, b20, b21, b22, b23, b24) = _compute_shot_bounds(tc, outro_t0)

    chapters = [0.0, b07, b10, b15, b18, b21, b23]
    draw_hud_chrome(cs, cg, txts, fonts, t, total_dur, EP_CODE, EP_TITLE, chapters)
    draw_ambient_particles(cs, t, alpha=0.88 * clamp((outro_t0 - t) / 0.8))

    # -------------------------------------------------------------------------
    # SHOT 01 (b01..b02): Character in dark room lifts smartphone up to face!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b01, b02)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b01, b02, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        rp = ease_out_cubic(clamp((t - 0.08) / 0.85))
        sg_p = ease_out_cubic(clamp((t - 0.35) / 0.55))

        # Ground line + subtle night window & wall clock (exact v04_11M mood!)
        draw_glow_line(cs, cg, 220, 1085, 860, 1085, w * 0.45, lw_s=1.6, lw_g=3.5)
        draw_hypnotic_chronograph_ring(cs, cg, 815, 455, 52.0, t, alpha=w * 0.45, draw_p=rp, speed=1.2)

        draw_character_with_phone(cs, cg, 520, 1085, scale=1.85, raise_p=rp, screen_glow=sg_p, t=t, alpha=w, draw_p=min(1.0, t / 0.45 + 0.2))
        sp_tu = get_fitted_text_sprite("تو — همین الان", fonts.reg_26, 300, (190, 190, 205, 255))
        stx.append((sp_tu, 520, 1145, w * rp))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # -------------------------------------------------------------------------
    # SHOT 02 (b02..b03): Extreme POV Close-Up — Hand & Thumb gripping Phone!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b02, b03)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b02, b03, base_in=0.86)
        push_camera(cs, cg, zoom=cz, px=540, py=830)
        p_in = ease_out_cubic(clamp((t - b02) / 0.32))
        draw_pov_phone_in_hand(cs, cg, 540, 825, 340, 620, thumb_swipe=0.0, thumb_tap=0.0, alpha=w, draw_p=p_in)
        sp_q = get_fitted_text_sprite("؟", fonts.eb_92, 240, (255, 255, 255, 255), glow=0.85)
        sp_sub = get_fitted_text_sprite("فاکتورِ خرید", fonts.reg_30, 240, (195, 195, 210, 255))
        stx.append((sp_q, 540, 760, w * p_in))
        stx.append((sp_sub, 540, 855, w * p_in))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=830)

    # -------------------------------------------------------------------------
    # SHOT 03 (b03..b04): POV Hand Thumb Swiping Giant 50,000,000 -> 60,000,000!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b03, b04)
    if w > 0.01:
        stx = []
        t60 = tc["c03_p60"]
        is_60 = (t >= t60 - 0.04)
        cz = _shot_cam_z(t, b03, b04, base_in=0.95) + impact_punch(t, b03, 0.035, 0.35) + impact_punch(t, t60, 0.042, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=830)

        sw1 = clamp((t - (b03 - 0.06)) / 0.28) if not is_60 else 0.0
        sw2 = clamp((t - (t60 - 0.06)) / 0.28) if is_60 else 0.0
        draw_pov_phone_in_hand(cs, cg, 540, 825, 340, 620, thumb_swipe=max(sw1, sw2), thumb_tap=max(sw1, sw2), alpha=w, draw_p=1.0)

        num_str = "۶۰,۰۰۰,۰۰۰" if is_60 else "۵۰,۰۰۰,۰۰۰"
        sp_n = get_fitted_text_sprite(num_str, fonts.eb_68, 285, (255, 255, 255, 255), glow=0.85)
        sp_t = get_fitted_text_sprite("تومان", fonts.bold_36, 260, (215, 215, 228, 255))
        stx.append((sp_n, 540, 745, w))
        stx.append((sp_t, 540, 825, w))
        if is_60 and sw2 < 0.95:
            draw_shockwave_ring(cs, cg, 540, 765, sw2, max_r=250.0, alpha=w * 0.75)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=830)

    # -------------------------------------------------------------------------
    # SHOT 04 (b04..b05): Top AI Observatory Eye Scanning Character & Phone!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b04, b05)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b04, b05, base_in=0.92)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        phx, phy, chx, chy = draw_character_with_phone(cs, cg, 520, 1140, scale=1.75, raise_p=1.0, screen_glow=0.9, t=t, alpha=w)
        draw_observatory_eye(cs, cg, 540, 345, radius=58.0, t=t, alpha=w, scan_targets=[(phx, phy), (chx, chy)])
        draw_spotlight_cone(cs, cg, 540, 405, 330, 750, 1140, alpha=w * 0.65)
        # Glowing target reticle pulsing on character's chest!
        pr = 18.0 + math.sin(t * 9.0) * 5.0
        cs.arc(chx, chy, pr, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.90 * w); cs.set_line_width(2.2); cs.stroke()
        cg.arc(chx, chy, pr + 6, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.55 * w); cg.set_line_width(5.0); cg.stroke()
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # -------------------------------------------------------------------------
    # SHOT 05 (b05..b06): Razor Blade Slash Slicing 60,000,000 Banknote in Half!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b05, b06)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b05, b06, base_in=0.93) + impact_punch(t, tc["_c05_blade"], 0.04, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        sl_u = ease_out_cubic(clamp((t - (b05 + 0.28)) / 0.42))
        sep = sl_u * 36.0

        # Giant Banknote splitting apart!
        for half_s in (-1.0, 1.0):
            cs.save(); cs.set_dash([])
            cs.translate(half_s * sep, -half_s * sep * 0.45)
            cs.rotate(half_s * sl_u * 0.06)
            rounded_rect_path(cs, 540 - 330, 760 - 135, 660, 270, 20)
            cs.set_source_rgba(1, 1, 1, (0.80 - 0.45 * sl_u) * w); cs.set_line_width(2.6); cs.stroke()
            cs.restore()

        sp_60m = get_fitted_text_sprite("۶۰,۰۰۰,۰۰۰ تومان", fonts.eb_68, 600, (225, 225, 235, 255))
        stx.append((sp_60m, 540, 760, w * (1.0 - 0.55 * sl_u)))
        if sl_u > 0.02:
            # Diagonal razor light-slash!
            lx1 = 190 + 700 * sl_u
            ly1 = 945 - 370 * sl_u
            draw_glow_line(cs, cg, 190, 945, lx1, ly1, w, lw_s=4.0, lw_g=10.0)
            sp_no = get_fitted_text_sprite("فقط ظاهرِ ماجراست!", fonts.bold_36, 620, (255, 255, 255, 255), glow=0.7)
            stx.append((sp_no, 540, 1045, w * sl_u))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # -------------------------------------------------------------------------
    # SHOT 06 (b06..b07): BOOM REVEAL — GIANT «۶۰۰ ساعت» + SOUL STREAM TO PHONE!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b06, b07)
    if w > 0.01:
        stx = []
        shk = math.sin((t - b06) * 48.0) * 9.0 * math.exp(-max(0.0, t - b06) * 7.5) if t >= b06 else 0.0
        cz = _shot_cam_z(t, b06, b07, base_in=0.88) + impact_punch(t, tc["c06_600"], 0.055, 0.55)
        push_camera(cs, cg, zoom=cz, dx=shk, dy=-shk * 0.5, px=540, py=820)

        sh_u = clamp((t - b06) / 0.70)
        draw_shockwave_ring(cs, cg, 540, 480, sh_u, max_r=440.0, alpha=w)

        # Giant @ensan.besham Focal Number in pure black space!
        sp_big = get_fitted_text_sprite("۶۰۰ ساعت", fonts.eb_92, 860, (255, 255, 255, 255), glow=0.95)
        sp_lbl = get_fitted_text_sprite("از عمرِ واقعیِ تو!", fonts.bold_44, 760, (235, 235, 248, 255), glow=0.5)
        stx.append((sp_big, 540, 435, w))
        stx.append((sp_lbl, 540, 545, w))

        # Below: Character on right holding phone on left while torrent of soul-sparks drains from chest -> phone!
        phx, phy, chx, chy = draw_character_with_phone(
            cs, cg, 690, 1185, scale=1.75, raise_p=1.0, screen_glow=1.0, t=t, alpha=w, facing_right=False
        )
        # Giant floating hourglass ghost behind phone
        draw_hourglass_monolith(cs, cg, 335, 965, 130, 235, sand_top=clamp(0.75 - 0.45 * clamp((t - b06) / 2.5)), flowing=True, t=t, alpha=w * 0.90)
        for oi in range(14):
            ou = ((t * 1.45 + oi / 14.0) % 1.0)
            ox = (1 - ou) ** 2 * chx + 2 * (1 - ou) * ou * 520 + ou ** 2 * 335
            oy = (1 - ou) ** 2 * chy + 2 * (1 - ou) * ou * 785 + ou ** 2 * 965
            oa = math.sin(math.pi * ou) * w
            cs.arc(ox, oy, 4.0, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.96 * oa); cs.fill()
            cg.arc(ox, oy, 9.5, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.68 * oa); cg.fill()
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, dx=shk, dy=-shk * 0.5, px=540, py=820)

    # -------------------------------------------------------------------------
    # SHOT 07 (b07..b08): Two Characters Exchanging Dissolving Paper Bills!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b07, b08)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b07, b08, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=840)
        u7 = clamp((t - b07) / max(0.8, b08 - b07))
        draw_glow_line(cs, cg, 140, 1085, 940, 1085, w * 0.5, lw_s=1.8, lw_g=3.5)

        draw_human_figure(cs, 755, 1085, scale=1.55, alpha=w * 0.95); draw_human_figure(cg, 755, 1085, scale=1.55, alpha=w * 0.35, lw=4.5)
        draw_human_figure(cs, 325, 1085, scale=1.55, alpha=w * 0.55)
        sp_r = get_fitted_text_sprite("تو", fonts.bold_30, 180, (245, 245, 255, 255))
        sp_l = get_fitted_text_sprite("فروشنده", fonts.reg_26, 200, (175, 175, 190, 255))
        stx.append((sp_r, 755, 1138, w)); stx.append((sp_l, 325, 1138, w))

        # Paper bills flying from right -> left and dissolving into dashed ghost smoke mid-air!
        for bi in range(4):
            bu = ((u7 * 1.6 + bi * 0.25) % 1.0)
            bx = 685.0 - bu * 310.0
            by = 885.0 - math.sin(math.pi * bu) * 65.0 - bu * 35.0
            ba = (1.0 - 0.78 * bu) * w
            cs.save()
            cs.translate(bx, by); cs.rotate(-bu * 0.5)
            if bu > 0.45:
                cs.set_dash([6.0, 6.0])
            rounded_rect_path(cs, -48, -24, 96, 48, 6)
            cs.set_source_rgba(1, 1, 1, ba); cs.set_line_width(2.2); cs.stroke()
            cs.restore()

        sp_t7 = get_fitted_text_sprite("پول فقط «کاغذِ واسطه» است", fonts.bold_44, 820, (255, 255, 255, 255), glow=0.55)
        stx.append((sp_t7, 540, 495, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=840)

    # -------------------------------------------------------------------------
    # SHOT 08 (b08..b09): X-Ray Dive Inside Human Torso — Heartbeat & Watch!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b08, b09)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b08, b09, base_in=0.88) + impact_punch(t, tc["c08_life"], 0.038, 0.48)
        push_camera(cs, cg, zoom=cz, px=540, py=840)

        # Giant upper-body silhouette (head at y=608, chest at y=835) framing the ticking heart-chronograph!
        draw_human_figure(cs, 540, 1125, scale=3.5, alpha=w * 0.52, lw=2.0)
        draw_human_figure(cg, 540, 1125, scale=3.5, alpha=w * 0.22, lw=4.5)
        draw_hypnotic_chronograph_ring(cs, cg, 540, 855, 132.0, t, alpha=w * 0.92, draw_p=1.0, speed=1.8)
        draw_hourglass_monolith(cs, cg, 540, 855, 76, 132, sand_top=0.48, flowing=True, t=t, alpha=w * 0.96)
        draw_ecg_waveform(cs, cg, 150, 930, 1215, t, amp=46.0, alpha=w)

        sp_h8 = get_fitted_text_sprite("واحدِ واقعی: ساعتِ زندگیت!", fonts.bold_44, 840, (255, 255, 255, 255), glow=0.7)
        stx.append((sp_h8, 540, 355, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=840)

    # -------------------------------------------------------------------------
    # SHOT 09 (b09..b10): @ensan.besham Crumbling Life-Pedestal into the Abyss!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b09, b10)
    if w > 0.01:
        stx = []
        cr_u = ease_in_out_cubic(clamp((t - b09) / max(0.7, (b10 - b09) * 0.80)))
        cz = _shot_cam_z(t, b09, b10, base_in=0.94) + impact_punch(t, b09 + 0.08, 0.042, 0.50)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        # Standing base column (drops as top blocks fall off!)
        rem_top_y = 760.0 + cr_u * 165.0
        for ctx, lw, al in ((cs, 2.6, w * 0.92), (cg, 5.2, w * 0.36)):
            ctx.save(); ctx.set_dash([])
            ctx.rectangle(465, rem_top_y, 150, 1320 - rem_top_y)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

        # 3 detaching stone life-blocks tumbling down into darkness!
        for blk_i in range(3):
            bu = clamp(cr_u * 1.35 - blk_i * 0.18)
            bx = 540 + (1 if blk_i % 2 == 0 else -1) * (45.0 + bu * 165.0)
            by = 730.0 + blk_i * 52.0 + (bu ** 2) * 460.0
            rot_b = (1 if blk_i % 2 == 0 else -1) * bu * 1.45
            ba = (1.0 - 0.85 * bu) * w
            cs.save(); cs.set_dash([])
            cs.translate(bx, by); cs.rotate(rot_b)
            rounded_rect_path(cs, -72, -24, 144, 48, 5)
            cs.set_source_rgba(1, 1, 1, ba); cs.set_line_width(2.2); cs.stroke()
            cs.restore()

        # Character standing on top of the shrinking pedestal holding phone!
        draw_character_with_phone(cs, cg, 540, rem_top_y, scale=1.42, raise_p=1.0, screen_glow=0.9, t=t, alpha=w)
        sp_c9 = get_fitted_text_sprite("ساعت‌هایی که دیگه برنمی‌گردن!", fonts.bold_44, 840, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_c9, 540, 345, w))
        sp_col = get_fitted_text_sprite("ستونِ عمر", fonts.reg_30, 140, (200, 200, 215, 255))
        stx.append((sp_col, 540, 1145, w * 0.85))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # -------------------------------------------------------------------------
    # SHOT 10 (b10..b11): Hunched Office Worker at Laptop + Fast Spinning Clock!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b10, b11)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b10, b11, base_in=0.92)
        push_camera(cs, cg, zoom=cz, px=540, py=840)

        # Fast-spinning office wall clock overhead (speed=6.5x!)
        draw_hypnotic_chronograph_ring(cs, cg, 540, 465, 115.0, t, alpha=w * 0.92, draw_p=1.0, speed=6.5)
        draw_character_at_desk(cs, cg, 540, 1055, scale=1.95, t=t, alpha=w)

        sp_w10 = get_fitted_text_sprite("کار + ترافیک + خستگیِ روزانه", fonts.bold_36, 820, (245, 245, 255, 255), glow=0.45)
        stx.append((sp_w10, 540, 1165, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=840)

    # -------------------------------------------------------------------------
    # SHOT 11 (b11..b12): @ensan.besham v03_4M Payslip + Giant «۱۰۰,۰۰۰» + Worker!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b11, b12)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b11, b12, base_in=0.90) + impact_punch(t, b11 + 0.08, 0.042, 0.45)
        push_camera(cs, cg, zoom=cz, px=540, py=830)

        # Clean Payslip document icon at top (540, 395)
        cs.save(); cs.set_dash([])
        rounded_rect_path(cs, 445, 285, 190, 210, 12)
        cs.set_source_rgba(1, 1, 1, 0.88 * w); cs.set_line_width(2.3); cs.stroke()
        for ly_p in (335, 368, 401, 434):
            cs.move_to(475, ly_p); cs.line_to(605, ly_p); cs.set_source_rgba(1, 1, 1, 0.45 * w); cs.set_line_width(1.6); cs.stroke()
        cs.restore()
        sp_ps = get_fitted_text_sprite("فیشِ ۱ ساعت عمر", fonts.light_22, 170, (215, 215, 228, 255))
        stx.append((sp_ps, 540, 308, w))

        # Giant ExtraBold 100,000 center focal!
        sp_100 = get_fitted_text_sprite("۱۰۰,۰۰۰", fonts.eb_92, 820, (255, 255, 255, 255), glow=0.90)
        sp_tom = get_fitted_text_sprite("تومان در هر ساعت", fonts.bold_36, 700, (220, 220, 235, 255))
        stx.append((sp_100, 540, 625, w))
        stx.append((sp_tom, 540, 725, w))

        draw_human_figure(cs, 540, 1155, scale=1.55, alpha=w * 0.95)
        draw_human_figure(cg, 540, 1155, scale=1.55, alpha=w * 0.35, lw=4.5)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=830)

    # -------------------------------------------------------------------------
    # SHOT 12 (b12..b13): Rear Flagship Pro iPhone = Spinning 0->600 Odometer!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b12, b13)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b12, b13, base_in=0.91)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        u12 = ease_out_cubic(clamp((t - b12) / max(0.5, (b13 - b12) * 0.85)))

        draw_pro_rear_iphone(cs, cg, 735, 760, 210, 390, alpha=w, draw_p=1.0)
        sp_eq = get_fitted_text_sprite("=", fonts.eb_84, 120, (255, 255, 255, 255), glow=0.6)
        stx.append((sp_eq, 535, 760, w))

        cur_h = int(round(600 * u12))
        h_fa = str(cur_h).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))
        sp_cnt = get_fitted_text_sprite(h_fa, fonts.eb_92, 340, (255, 255, 255, 255), glow=0.90)
        sp_unit = get_fitted_text_sprite("ساعت کار!", fonts.bold_36, 320, (220, 220, 235, 255))
        stx.append((sp_cnt, 315, 730, w))
        stx.append((sp_unit, 315, 830, w))
        sp_p60 = get_fitted_text_sprite("گوشیِ ۶۰ میلیونی", fonts.bold_30, 320, (215, 215, 228, 255))
        stx.append((sp_p60, 735, 1015, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # -------------------------------------------------------------------------
    # SHOT 13 (b13..b14): Giant «۷۵ روز کاری» + 75-Cell Domino Wall + Tiny Human!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b13, b14)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b13, b14, base_in=0.90) + impact_punch(t, b13 + 0.08, 0.04, 0.45)
        push_camera(cs, cg, zoom=cz, px=540, py=830)
        dom_u = clamp((t - b13) / max(0.65, (b14 - b13) * 0.72))

        sp_75 = get_fitted_text_sprite("۷۵ روزِ کاملِ کاری!", fonts.eb_84, 860, (255, 255, 255, 255), glow=0.92)
        stx.append((sp_75, 540, 355, w))

        # 15 x 5 crisp calendar blocks towering like a monolith above a tiny human!
        cols, rows = 15, 5
        cw_c, ch_c, gx_c, gy_c = 44.0, 56.0, 11.0, 14.0
        gw = cols * cw_c + (cols - 1) * gx_c
        x_start = 540.0 - gw / 2.0
        y_start = 475.0
        lit_f = dom_u * 75.0
        cs.save(); cg.save(); cs.set_dash([]); cg.set_dash([])
        for ri in range(rows):
            for ci in range(cols):
                idx_d = ri * cols + (cols - 1 - ci)
                cx_d = x_start + ci * (cw_c + gx_c)
                cy_d = y_start + ri * (ch_c + gy_c)
                act = clamp(lit_f - idx_d)
                rounded_rect_path(cs, cx_d, cy_d, cw_c, ch_c, 7.0)
                if act > 0.02:
                    cs.set_source_rgba(1, 1, 1, (0.25 + 0.62 * act) * w); cs.fill_preserve()
                    cs.set_source_rgba(1, 1, 1, 0.96 * w); cs.set_line_width(1.9); cs.stroke()
                    if 0.01 < act < 0.99:
                        rounded_rect_path(cg, cx_d - 2, cy_d - 2, cw_c + 4, ch_c + 4, 8.0)
                        cg.set_source_rgba(1, 1, 1, 0.88 * w); cg.set_line_width(4.5); cg.stroke()
                else:
                    cs.set_source_rgba(1, 1, 1, 0.16 * w); cs.set_line_width(1.2); cs.stroke()
        cs.restore(); cg.restore()

        # Tiny human figure at bottom looking up at the giant 75-day wall!
        draw_character_with_phone(cs, cg, 540, 1215, scale=1.18, raise_p=0.85, screen_glow=0.8, t=t, alpha=w)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=830)

    # -------------------------------------------------------------------------
    # SHOT 14 (b14..b15): Poetic Season Cut — Canopy of Youth Blowing Away!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b14, b15)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b14, b15, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=840)
        u14 = clamp((t - b14) / max(0.6, b15 - b14))

        sp_s14 = get_fitted_text_sprite("۱ فصلِ کامل از جوونیت!", fonts.eb_68, 860, (255, 255, 255, 255), glow=0.88)
        stx.append((sp_s14, 540, 395, w))

        draw_glow_line(cs, cg, 140, 1145, 940, 1145, w * 0.45, lw_s=1.8, lw_g=3.5)
        draw_character_with_phone(cs, cg, 330, 1145, scale=1.65, raise_p=1.0, screen_glow=1.0, t=t, alpha=w)

        # 22 glowing calendar/leaf particles blowing away from the character into the wind!
        for li in range(22):
            lu = ((u14 * 0.85 + (li * 0.043)) % 1.0)
            lx_p = 390.0 + lu * 560.0
            ly_p = 945.0 - lu * 280.0 + math.sin(lu * 7.0 + li) * 38.0
            la = math.sin(math.pi * lu) * w * 0.90
            cs.save(); cs.translate(lx_p, ly_p); cs.rotate(lu * 2.4 + li)
            cs.move_to(-11, 0); cs.curve_to(-4, -8, 4, -8, 11, 0); cs.curve_to(4, 8, -4, 8, -11, 0)
            cs.set_source_rgba(1, 1, 1, la); cs.set_line_width(1.8); cs.stroke()
            cs.restore()
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=840)

    # -------------------------------------------------------------------------
    # SHOT 15 (b15..b16): Close-Up Character Head Snapping on X-Ray Glasses!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b15, b16)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b15, b16, base_in=0.86) + impact_punch(t, b15 + 0.05, 0.038, 0.38)
        push_camera(cs, cg, zoom=cz, px=540, py=840)
        gp = ease_out_cubic(clamp((t - b15) / 0.40))

        # Large portrait of character + glowing geometric X-ray lenses snapping onto eyes!
        draw_human_figure(cs, 540, 1245, scale=3.1, alpha=w * 0.92)
        draw_human_figure(cg, 540, 1245, scale=3.1, alpha=w * 0.35, lw=4.5)
        hx_c, hy_c = 540.0, 1245.0 - 148.0 * 3.1  # y = 786.2
        slide_y = (1.0 - gp) * -90.0
        for ctx, lw, al in ((cs, 3.0, w * gp), (cg, 6.5, w * gp * 0.65)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, hx_c - 64, hy_c - 20 + slide_y, 56, 36, 8)
            rounded_rect_path(ctx, hx_c + 8,  hy_c - 20 + slide_y, 56, 36, 8)
            ctx.move_to(hx_c - 8, hy_c - 2 + slide_y); ctx.line_to(hx_c + 8, hy_c - 2 + slide_y)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()
        if gp > 0.5:
            draw_spotlight_cone(cs, cg, hx_c, hy_c, 220, 860, 360, alpha=w * (gp - 0.5) * 1.4)
        sp_g15 = get_fitted_text_sprite("عینکِ «قیمت به ساعتِ عمر»", fonts.bold_44, 820, (255, 255, 255, 255), glow=0.7)
        stx.append((sp_g15, 540, 395, w * gp))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=840)

    # -------------------------------------------------------------------------
    # SHOT 16 (b16..b17): Sneaker Showcase -> Giant «۶۰ ساعت» + Treadmill Runner!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b16, b17)
    if w > 0.01:
        stx = []
        t_60h = tc["c16_60h"]
        rev = ease_out_cubic(clamp((t - (t_60h - 0.12)) / 0.38))
        cz = _shot_cam_z(t, b16, b17, base_in=0.91) + impact_punch(t, t_60h, 0.042, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        # Large minimalist Sneaker icon at top (540, 445)
        for ctx, lw, al in ((cs, 3.0, w * 0.95), (cg, 6.2, w * 0.45)):
            ctx.save(); ctx.set_dash([]); ctx.translate(540, 445); ctx.scale(2.3, 2.3)
            ctx.move_to(-44, 20); ctx.line_to(44, 20)
            ctx.curve_to(46, 5, 30, 1, 12, -5); ctx.line_to(-6, -24); ctx.line_to(-26, -19); ctx.line_to(-40, 4)
            ctx.close_path(); ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw / 2.3); ctx.stroke()
            ctx.move_to(-44, 12); ctx.line_to(43, 12); ctx.stroke()
            ctx.restore()

        if rev < 0.25:
            sp_sh1 = get_fitted_text_sprite("کفشِ ۶,۰۰۰,۰۰۰ تومانی؟", fonts.bold_52, 820, (240, 240, 250, 255))
            stx.append((sp_sh1, 540, 690, w))
        else:
            sp_sh2 = get_fitted_text_sprite("۶۰ ساعت", fonts.eb_92, 820, (255, 255, 255, 255), glow=0.92)
            sp_sh3 = get_fitted_text_sprite("پایِ کار موندن!", fonts.bold_44, 720, (230, 230, 245, 255))
            stx.append((sp_sh2, 540, 665, w * rev))
            stx.append((sp_sh3, 540, 775, w * rev))
            draw_running_human_60fps(cs, cg, 540, 1135, scale=1.45, t=t, alpha=w * rev, facing_left=True)
            draw_glow_line(cs, cg, 360, 1142, 720, 1142, w * rev * 0.85, lw_s=3.0, lw_g=6.0)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # -------------------------------------------------------------------------
    # SHOT 17 (b17..b18): Silver Cloche Lifting -> Giant «۲۰ ساعت آزادی»!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b17, b18)
    if w > 0.01:
        stx = []
        t_20h = tc["c17_20h"]
        lift_u = ease_out_cubic(clamp((t - (b17 + 0.25)) / 0.70))
        rev20 = ease_out_cubic(clamp((t - (t_20h - 0.12)) / 0.38))
        cz = _shot_cam_z(t, b17, b18, base_in=0.91) + impact_punch(t, t_20h, 0.042, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=820)

        # Platter at y=535 + Cloche dome lifting upward by 135px to reveal spinning clock!
        draw_glow_line(cs, cg, 350, 545, 730, 545, w * 0.9, lw_s=3.0, lw_g=6.0)
        dome_y = 538.0 - lift_u * 145.0
        for ctx, lw, al in ((cs, 2.8, w * 0.94), (cg, 6.0, w * 0.42)):
            ctx.save(); ctx.set_dash([])
            ctx.arc(540, dome_y, 135.0, math.pi, 2 * math.pi); ctx.close_path()
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.arc(540, dome_y - 145.0, 12.0, 0, 2 * math.pi); ctx.stroke()
            ctx.restore()

        if lift_u > 0.25:
            draw_hypnotic_chronograph_ring(cs, cg, 540, 480, 62.0, t, alpha=w * lift_u, draw_p=1.0, speed=3.0)

        if rev20 < 0.20:
            sp_d1 = get_fitted_text_sprite("شامِ ۲,۰۰۰,۰۰۰ تومانی؟", fonts.bold_52, 820, (240, 240, 250, 255))
            stx.append((sp_d1, 540, 745, w))
        else:
            sp_d2 = get_fitted_text_sprite("۲۰ ساعت", fonts.eb_92, 820, (255, 255, 255, 255), glow=0.92)
            sp_d3 = get_fitted_text_sprite("از آزادیِ خالصت!", fonts.bold_44, 760, (235, 235, 248, 255))
            stx.append((sp_d2, 540, 735, w * rev20))
            stx.append((sp_d3, 540, 845, w * rev20))
            draw_human_figure(cs, 540, 1185, scale=1.35, alpha=w * rev20 * 0.90)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # -------------------------------------------------------------------------
    # SHOT 18 (b18..b19): @ensan.besham Social Comparison Pedestals (چشم‌وهم‌چشمی)!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b18, b19)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b18, b19, base_in=0.92)
        push_camera(cs, cg, zoom=cz, px=540, py=840)
        u18 = ease_out_cubic(clamp((t - b18) / 0.75))

        draw_glow_line(cs, cg, 120, 1185, 960, 1185, w * 0.5, lw_s=1.8, lw_g=3.5)
        # Left & Right tall rival pedestals ("رفیقت", "بغل‌دستی") holding bright phones!
        for px_r, lbl_r, ph_h in ((255.0, "بغل‌دستی", 330.0 * u18), (825.0, "همکار", 285.0 * u18)):
            cs.save(); cs.set_dash([])
            cs.rectangle(px_r - 58, 1185 - ph_h, 116, ph_h)
            cs.set_source_rgba(1, 1, 1, 0.55 * w); cs.set_line_width(2.0); cs.stroke()
            cs.restore()
            draw_character_with_phone(cs, cg, px_r, 1185 - ph_h, scale=1.18, raise_p=1.0, screen_glow=1.0, t=t, alpha=w * 0.88)
            sp_rl = get_fitted_text_sprite(lbl_r, fonts.reg_26, 180, (185, 185, 200, 255))
            stx.append((sp_rl, px_r, 1230, w))

        # Center lower pedestal: "تو" looking up enviously along dashed sightlines!
        cs.save(); cs.set_dash([])
        cs.rectangle(540 - 62, 1185 - 110, 124, 110)
        cs.set_source_rgba(1, 1, 1, 0.90 * w); cs.set_line_width(2.4); cs.stroke()
        cs.set_dash([6.0, 6.0], -t * 24.0)
        cs.move_to(540, 910); cs.line_to(255, 710); cs.move_to(540, 910); cs.line_to(825, 755)
        cs.set_source_rgba(1, 1, 1, 0.42 * w); cs.set_line_width(1.6); cs.stroke()
        cs.restore()
        draw_human_figure(cs, 540, 1075, scale=1.28, alpha=w * 0.98)
        draw_human_figure(cg, 540, 1075, scale=1.28, alpha=w * 0.38, lw=4.5)
        sp_tu18 = get_fitted_text_sprite("تو (تله‌ی مقایسه)", fonts.bold_30, 260, (255, 255, 255, 255), glow=0.5)
        stx.append((sp_tu18, 540, 1230, w))
        sp_top18 = get_fitted_text_sprite("خرید برای چشم‌وهم‌چشمی!", fonts.bold_44, 840, (255, 255, 255, 255), glow=0.65)
        stx.append((sp_top18, 540, 365, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=840)

    # -------------------------------------------------------------------------
    # SHOT 19 (b19..b20): Sisyphus Character Crushed Under Giant Boulder-Phone!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b19, b20)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b19, b20, base_in=0.90) + impact_punch(t, b19 + 0.05, 0.038, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=850)

        draw_sisyphus_human_boulder_phone(cs, cg, 515, 1125, scale=1.32, t=t, alpha=w)
        sp_s19 = get_fitted_text_sprite("دیگه تو صاحبِ وسایلت نیستی...", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_s19, 540, 385, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=850)

    # -------------------------------------------------------------------------
    # SHOT 20 (b20..b21): Puppet-Master Phone Above Holding Human on Strings!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b20, b21)
    if w > 0.01:
        stx = []
        shk20 = math.sin((t - b20) * 44.0) * 8.0 * math.exp(-max(0.0, t - b20) * 7.0) if t >= b20 else 0.0
        cz = _shot_cam_z(t, b20, b21, base_in=0.88) + impact_punch(t, tc["c20_puppet"], 0.052, 0.55)
        push_camera(cs, cg, zoom=cz, dx=shk20, px=540, py=830)

        draw_shockwave_ring(cs, cg, 540, 455, clamp((t - b20) / 0.72), max_r=400.0, alpha=w)

        # Giant rotating clockwork gear + horizontal Master Smartphone at top (540, 445)
        draw_clock_gear(cs, cg, 540, 445, 175.0, 20, t * 0.75, alpha=w * 0.55)
        cs.save(); cg.save(); cs.set_dash([]); cg.set_dash([])
        rounded_rect_path(cs, 540 - 165, 445 - 82, 330, 164, 26)
        cs.set_source_rgba(0.03, 0.03, 0.04, 0.96 * w); cs.fill_preserve()
        cs.set_source_rgba(1, 1, 1, 0.98 * w); cs.set_line_width(3.2); cs.stroke()
        rounded_rect_path(cg, 540 - 165, 445 - 82, 330, 164, 26)
        cg.set_source_rgba(1, 1, 1, 0.65 * w); cg.set_line_width(7.0); cg.stroke()
        cs.restore(); cg.restore()
        sp_pm = get_fitted_text_sprite("اربابِ زمانِ تو", fonts.bold_36, 290, (255, 255, 255, 255), glow=0.7)
        stx.append((sp_pm, 540, 445, w))

        # Puppet human dangling below at (540, 1135) with 4 glowing marionette strings!
        sway = math.sin(t * 3.2) * 14.0
        hx_p = 540.0 + sway
        draw_human_figure(cs, hx_p, 1135, scale=1.75, alpha=w * 0.96)
        draw_human_figure(cg, hx_p, 1135, scale=1.75, alpha=w * 0.40, lw=4.5)
        for sx_top, tx_bot, ty_bot in (
            (430, hx_p - 68, 1135 - 105),
            (495, hx_p,      1135 - 260),
            (585, hx_p,      1135 - 205),
            (650, hx_p + 68, 1135 - 105),
        ):
            draw_glow_line(cs, cg, sx_top, 527, tx_bot, ty_bot, w * 0.82, lw_s=1.8, lw_g=4.2)

        sp_own = get_fitted_text_sprite("وسایلت صاحبِ عمرِ توئن!", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_own, 540, 1230, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, dx=shk20, px=540, py=830)

    # -------------------------------------------------------------------------
    # SHOT 21 (b21..b22): POV Hand Checkout Pause — Price ÷ 1 Hour of Life!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b21, b22)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b21, b22, base_in=0.91)
        push_camera(cs, cg, zoom=cz, px=540, py=830)

        draw_pov_phone_in_hand(cs, cg, 540, 835, 345, 625, thumb_swipe=0.0, thumb_tap=0.0, alpha=w, draw_p=1.0)
        sp_f1 = get_fitted_text_sprite("قانونِ ۳ ثانیه:", fonts.reg_26, 275, (195, 195, 210, 255))
        sp_f2 = get_fitted_text_sprite("قیمتِ جنس", fonts.bold_44, 275, (255, 255, 255, 255), glow=0.5)
        sp_f3 = get_fitted_text_sprite("÷ درآمدِ ۱ ساعتت", fonts.bold_30, 275, (235, 235, 248, 255))
        sp_f4 = get_fitted_text_sprite("= چند ساعت عمر؟", fonts.bold_30, 275, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_f1, 540, 608, w))
        stx.append((sp_f2, 540, 682, w))
        stx.append((sp_f3, 540, 756, w))
        stx.append((sp_f4, 540, 828, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=830)

    # -------------------------------------------------------------------------
    # SHOT 22 (b22..b23): LIBERATION! Character Lowers Phone & Shatters Chains!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b22, b23)
    if w > 0.01:
        stx = []
        shat_u = clamp((t - b22) / 0.85)
        drop_u = ease_in_out_cubic(clamp((t - b22) / 0.75))
        cz = _shot_cam_z(t, b22, b23, base_in=0.90) + impact_punch(t, tc["c22_free"], 0.048, 0.55)
        push_camera(cs, cg, zoom=cz, px=540, py=830)

        draw_shockwave_ring(cs, cg, 540, 860, shat_u, max_r=430.0, alpha=w)
        # Character lowers the phone arm (raise_p: 1.0 -> 0.0!) as star_mind ignites inside head!
        draw_character_with_phone(
            cs, cg, 540, 1135, scale=1.95, raise_p=(1.0 - drop_u), screen_glow=(1.0 - drop_u),
            t=t, alpha=w, star_mind=(drop_u > 0.35)
        )
        # 24 shattered chain shards rising into free fireflies!
        for si in range(24):
            ang_s = si * (2 * math.pi / 24.0) + 0.15
            rad_s = 45.0 + ease_out_cubic(shat_u) * 320.0
            sx = 540.0 + math.cos(ang_s) * rad_s
            sy = 910.0 + math.sin(ang_s) * rad_s - shat_u * 85.0
            sa = (1.0 - 0.55 * shat_u) * w
            draw_star4(cs, sx, sy, 6.5, sa)
            draw_star4(cg, sx, sy, 11.0, sa * 0.7)

        sp_fr = get_fitted_text_sprite("عمرت رو مفت نفروش؛ آزاد بمون!", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_fr, 540, 385, w * drop_u))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=830)

    # -------------------------------------------------------------------------
    # SHOT 23 (b23..b24): Meta Mirror Shot — Character + 3 Rising Choice Pillars!
    # -------------------------------------------------------------------------
    w = _shot_win(t, b23, b24, fo=0.32)
    if w > 0.01:
        stx = []
        p23 = ease_out_cubic(clamp((t - b23) / 0.55))
        cz = 0.94 + 0.06 * p23 + 0.02 * clamp((t - b23) / max(1.0, b24 - b23))
        push_camera(cs, cg, zoom=cz, px=540, py=830)

        sp_q23 = get_fitted_text_sprite("گوشیِ توی دستت = چند ماه از عمرت؟", fonts.bold_36, 860, (255, 255, 255, 255), glow=0.65)
        stx.append((sp_q23, 540, 275, w * p23))

        # 3 @ensan.besham vertical choice pedestals rising side-by-side!
        cyc = ((t - b23) * 1.65) % 3.0
        pillars = [
            (840.0, 210.0, "۱", "زیرِ ۱ ماه",   0),
            (540.0, 320.0, "۲", "۱ تا ۳ ماه",   1),
            (240.0, 440.0, "۳", "بالای ۳ ماه!", 2),
        ]
        base_y23 = 1065.0
        draw_glow_line(cs, cg, 110, base_y23, 970, base_y23, w * 0.5, lw_s=1.8, lw_g=3.5)
        for px_c, ph_full, num_c, lbl_c, idx_c in pillars:
            hi = math.exp(-((cyc - idx_c) ** 2) / 0.28)
            ph_cur = ph_full * ease_out_cubic(clamp((t - (b23 + idx_c * 0.14)) / 0.50))
            cs.save(); cg.save(); cs.set_dash([]); cg.set_dash([])
            rounded_rect_path(cs, px_c - 105, base_y23 - ph_cur, 210, max(12.0, ph_cur), 14)
            cs.set_source_rgba(0.035, 0.035, 0.05, 0.92 * w); cs.fill_preserve()
            cs.set_source_rgba(1, 1, 1, (0.42 + 0.56 * hi) * w); cs.set_line_width(2.4); cs.stroke()
            if hi > 0.45:
                rounded_rect_path(cg, px_c - 105, base_y23 - ph_cur, 210, max(12.0, ph_cur), 14)
                cg.set_source_rgba(1, 1, 1, 0.55 * hi * w); cg.set_line_width(5.5); cg.stroke()
            cs.restore(); cg.restore()

            if idx_c == 1:
                draw_character_with_phone(cs, cg, px_c, base_y23 - ph_cur, scale=0.98, raise_p=1.0, screen_glow=1.0, t=t, alpha=w * p23)

            sp_nc = get_fitted_text_sprite(num_c, fonts.eb_68, 170, (255, 255, 255, 255), glow=0.8 * hi)
            sp_lc = get_fitted_text_sprite(lbl_c, fonts.bold_30, 185, (230, 230, 245, 255))
            stx.append((sp_nc, px_c, base_y23 - ph_cur * 0.55 - 16, w * p23))
            stx.append((sp_lc, px_c, base_y23 + 44, w * p23))

        draw_pill_badge(cs, cg, stx, "عددش رو همین الان تو کامنت بنویس: ۱، ۲ یا ۳؟", 540, 1225, fonts.bold_30, w * p23, glow=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=830)

    # -------------------------------------------------------------------------
    # SHOT 24 (b24..total_dur): SIGNATURE OLED ENDPLATE (@zavieh.penhann)
    # -------------------------------------------------------------------------
    w9 = window_fade(t, outro_t0 - 0.12, total_dur + 0.5, fi=0.40, fo=0.55)
    if w9 > 0.01:
        lt = max(0.0, t - outro_t0)
        p_logo = ease_out_cubic(clamp(lt / 1.05))
        cx, cy = 540.0, 725.0
        draw_hypnotic_chronograph_ring(cs, cg, cx, cy, 228.0, t, alpha=w9 * p_logo * 0.38, draw_p=p_logo, speed=0.65)

        cs.save(); cs.set_dash([])
        cs.arc(cx, cy, 152, 0, 2 * math.pi * p_logo)
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
        txts.append((sp_brand, 540, 1065, w9 * ease_out_cubic(clamp((lt - 0.15) / 0.7))))
        txts.append((sp_tag,   540, 1168, w9 * ease_out_cubic(clamp((lt - 0.30) / 0.7))))

        pill_a = w9 * ease_out_cubic(clamp((lt - 0.45) / 0.7))
        draw_pill_badge(cs, cg, txts, "@zavieh.penhann", 540, 1290, fonts.med_36, pill_a, glow=True, pad_x=44, pad_y=15)

    return composite_oled_frame(surf_glow, surf_sharp, txts, fonts, t, sub_lines)


# =============================================================================
# Multiprocessing 60fps Cloud Renderer + Automated 12 & 24-Shot QA Sheets
# =============================================================================
_W_FONTS = None
_W_SG = None
_W_CG = None
_W_SS = None
_W_CS = None
_W_META = None

def _worker_init(font_dir: str, meta: dict):
    global _W_FONTS, _W_SG, _W_CG, _W_SS, _W_CS, _W_META
    _W_FONTS = FontBank(font_dir)
    _W_SG = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CG = cairo.Context(_W_SG)
    _W_SS = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CS = cairo.Context(_W_SS)
    _W_META = meta

def _worker_render_frame(frame_idx: int) -> bytes:
    t = frame_idx / FPS
    return render_scene_frame(
        t, _W_META["total_dur"], _W_META["t_cues"], _W_META["sub_lines"],
        _W_FONTS, _W_SG, _W_CG, _W_SS, _W_CS
    )


def save_qa_sheets(font_dir: str, meta: dict, qa_dir: str):
    """Generates subtitle baseline QA strip + 24-shot full contact sheet + 12-hero-shot sheet."""
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    sg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cg = cairo.Context(sg)
    ss = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cs = cairo.Context(ss)

    # 1. Subtitle Baseline Stability & Liquid Wipe Strip
    sub_strip = Image.new("RGB", (920, 14 * 105), (0, 0, 0))
    test_ln = meta["sub_lines"][min(5, len(meta["sub_lines"]) - 1)]
    t0_s = test_ln["times"][0]
    for k in range(14):
        tk = t0_s + k * 0.09
        raw = render_scene_frame(tk, meta["total_dur"], meta["t_cues"], meta["sub_lines"], fonts, sg, cg, ss, cs)
        im = Image.frombytes("RGB", (W, H), raw)
        crop = im.crop((80, 1580, 1000, 1685))
        for x in range(40):
            crop.putpixel((x, 62), (0, 220, 90))
            crop.putpixel((919 - x, 62), (0, 220, 90))
        sub_strip.paste(crop, (0, k * 105))
    sub_strip.save(os.path.join(qa_dir, "subtitle_strip_verify.png"))

    tc = meta["t_cues"]
    td = meta["total_dur"]
    outro_t0 = td - 4.0

    # All 24 shots sampled cleanly at the midpoint of each shot!
    bounds = _compute_shot_bounds(tc, outro_t0) + [td]
    ts_24 = [0.5 * (bounds[i] + bounds[i + 1]) for i in range(24)]
    ts_24[2]  = clamp(tc["c03_p60"] + 0.35, bounds[2] + 0.25, bounds[3] - 0.25)
    ts_24[15] = clamp(tc["c16_60h"] + 0.35, bounds[15] + 0.25, bounds[16] - 0.25)
    ts_24[16] = tc["c17_20h"] + 0.35

    pw24, ph24 = 270, 480
    grid24 = Image.new("RGB", (pw24 * 6, ph24 * 4), (16, 16, 20))
    for i, ts in enumerate(ts_24):
        ts_c = max(0.08, min(td - 0.12, ts))
        raw = render_scene_frame(ts_c, td, tc, meta["sub_lines"], fonts, sg, cg, ss, cs)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw24, ph24), Image.Resampling.LANCZOS)
        r, c = divmod(i, 6)
        grid24.paste(im, (c * pw24, r * ph24))
    grid24.save(os.path.join(qa_dir, "storyboard_24_shots.png"))

    # Also save standard 12-panel highlight storyboard for release compatibility
    pick_12 = [0, 2, 5, 8, 9, 12, 15, 17, 18, 19, 21, 22]
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

    print("=== [1/3] Building Studio v4.0 Master Audio (Locked Rasalgethi + 38 Hyper-Foley SFX + D-Minor Score) ===", flush=True)
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
            whisper_size=sys.argv[6] if len(sys.argv) > 6 else "medium",
        )
    else:
        raise SystemExit("Usage: python ep05_life_hours_price.py --cloud-render <font_dir> <work_dir> <out_mp4> <qa_dir> [whisper_size]")
