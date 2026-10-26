"""
Episode 07 (Studio v4.2 — High-Loudness Commercial Master + 24-Shot Hyper-Cut Character Cinema)
Topic: «قانونِ سطلِ خرچنگ‌ها؛ چرا نزدیک‌ترین آدم‌ها گاهی نمی‌خوان پیشرفت کنی؟»
Page: زاویه ذهن (@zavieh.penhann)

v4.2 Studio Upgrades:
  - High-Volume Commercial Broadcast Audio Master (-11.3 dBFS Voiced RMS / -0.40 dBFS True-Peak
    6ms Lookahead Limiter — +6 dB louder & crystal-clear on phone speakers with zero clipping!)
  - Calm, Clutter-Free Velvet Dark-Ambient & Sparse Felt-Piano Score (-16 dB below narrator)
    + bespoke Crab-Bucket Foley SFX (crab_pinch, mirror_ring, slash, typing, shatter, chime)
  - 24 Rapid-Fire @ensan.besham Visual Shots (~2.6s average shot length):
    open lidless crab bucket, lone crab escaping, 10 crabs pulling climber down, extreme pincer
    zoom, human pit + AI observatory eye, ladder ankle-grab by inner circle, excuse wall shattering,
    blazing full-length mirror, smiling mask hiding iron anchor, POV chat notifications, silent
    focus dome, ascending circle of builders, and 1-vs-2 interactive comment arena!
  - Locked Voice: Gemini 'Rasalgethi' + 129-tap @ensan.besham FIR + -0.34st Formant Calibration
  - Subtitles & Boxes: 0.000px baseline-locked 64px-feathered RTL wipe + 100% Zero-Overflow
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
    draw_ambient_particles,
    impact_punch, push_camera, pop_camera_and_transform_texts,
    draw_shockwave_ring, draw_hypnotic_chronograph_ring,
    draw_ecg_waveform,
    draw_character_with_phone, draw_pov_phone_in_hand,
    draw_character_at_desk, draw_observatory_eye,
    composite_oled_frame,
)

EP_CODE = "۰۷"
EP_TITLE = "قانونِ سطلِ خرچنگ‌ها"

# 35 Short, Punchy, Spoken Tehrani Persian Phrases (4-6 words per line -> ~64s total, 24 rapid shots!)
SCRIPT_SEGMENTS = [
    # Act I — The Hook: Lidless Bucket of Crabs (0..8 -> Shots 01..05)
    ("دقت کردی ماهیگیرها،",                                "دقت کردی ماهیگیرها،"),                                # 0  -> Shot 01
    ("هیچ‌وقت درِ سطلِ خرچنگ‌ها رو نمی‌بندن؟",             "هیچ‌وقت در سطل خرچنگ‌ها رو نمی‌بندن؟"),               # 1  -> Shot 01
    ("چون یه خرچنگِ تنها توی سطل،",                        "چون ۱ خرچنگ تنها توی سطل،"),                          # 2  -> Shot 02
    ("راحت از لبه‌ی سطل میاد بیرون!",                      "راحت از لبه‌ی سطل میاد بیرون!"),                      # 3  -> Shot 02
    ("ولی ده تا خرچنگ توی سطل باشن،",                     "ولی ۱۰ تا خرچنگ توی سطل باشن،"),                      # 4  -> Shot 03
    ("تا یکیشون به لبه‌ی نور می‌رسه،",                     "تا یکیشون به لبه‌ی نور می‌رسه،"),                     # 5  -> Shot 03
    ("بقیه پاشو می‌گیرن و می‌کشن پایین!",                  "بقیه پاشو می‌گیرن و می‌کشن پایین!"),                  # 6  -> Shot 04
    ("توی دنیای آدم‌ها بهش می‌گن:",                        "توی دنیای آدم‌ها بهش می‌گن:"),                        # 7  -> Shot 05
    ("قانونِ سطلِ خرچنگ‌ها!",                              "«قانون سطل خرچنگ‌ها»!"),                              # 8  -> Shot 05

    # Act II — The Painful Truth: Inner Circle & The Mirror Effect (9..20 -> Shots 06..12)
    ("تلخ‌ترین بخشِ ماجرا کجاست؟",                         "تلخ‌ترین بخش ماجرا کجاست؟"),                          # 9  -> Shot 06
    ("غریبه‌ها پات رو نمی‌کشن؛",                           "غریبه‌ها پات رو نمی‌کشن؛"),                           # 10 -> Shot 06
    ("گاهی نزدیک‌ترین آدم‌ها این کارو می‌کنن!",            "گاهی نزدیک‌ترین آدم‌ها این کارو می‌کنن!"),            # 11 -> Shot 07
    ("همون رفیق، فامیل یا همکارِ همیشگیت!",                "همون رفیق، فامیل یا همکار همیشگیت!"),                 # 12 -> Shot 08
    ("چرا کسی که دشمنت نیست،",                            "چرا کسی که دشمنت نیست،"),                             # 13 -> Shot 09
    ("از تغییر و رشدِ تو معذب می‌شه؟",                     "از تغییر و رشد تو معذب می‌شه؟"),                      # 14 -> Shot 09
    ("جوابش یه رازِ روان‌شناسیه:",                         "جوابش یه راز روان‌شناسیه:"),                          # 15 -> Shot 10
    ("تا وقتی تو هم درجا بزنی،",                          "تا وقتی تو هم درجا بزنی،"),                           # 16 -> Shot 10
    ("خیالشون راحته مشکل از شرایطه!",                      "خیالشون راحته مشکل از شرایطه!"),                      # 17 -> Shot 11
    ("ولی تا از همون شرایط اوج بگیری،",                   "ولی تا از همون شرایط اوج بگیری،"),                    # 18 -> Shot 11
    ("موفقیتت می‌شه یه آینه‌ی تمام‌قد،",                   "موفقیتت می‌شه یه آینه‌ی تمام‌قد،"),                   # 19 -> Shot 12
    ("که ترس و تنبلیِ خودشون رو لو می‌ده!",                "که ترس و تنبلی خودشون رو لو می‌ده!"),                 # 20 -> Shot 12

    # Act III — The Mask of "Caring" & Everyday Sabotage Quotes (21..25 -> Shots 13..16)
    ("مستقیم هم نمی‌گن پیشرفت نکن!",                       "مستقیم هم نمی‌گن پیشرفت نکن!"),                       # 21 -> Shot 13
    ("پشتِ نقابِ دلسوزی و شوخی قایم می‌شن:",              "پشت نقاب دلسوزی و شوخی قایم می‌شن:"),                # 22 -> Shot 13
    ("می‌گن ول کن بابا، تو این بازار نمیشه!",             "«ول کن بابا، تو این بازار نمیشه!»"),                 # 23 -> Shot 14
    ("یا به شوخی می‌گن چقدر عوض و جوگیر شدی!",            "«چقدر عوض و جوگیر شدی!»"),                            # 24 -> Shot 15
    ("پس چطور از این سطل بیای بیرون؟",                    "پس چطور از این سطل بیای بیرون؟"),                    # 25 -> Shot 16

    # Act IV — The 2 Escape Laws & Interactive CTA (26..34 -> Shots 17..24)
    ("قانونِ اول: توی سکوتِ مطلق بساز!",                   "قانون اول: توی سکوت مطلق بساز!"),                     # 26 -> Shot 17
    ("تصمیمی که کسی خبر نداره رو،",                       "تصمیمی که کسی خبر نداره رو،"),                        # 27 -> Shot 18
    ("هیچ‌کس با ترسش خراب نمی‌کنه!",                       "هیچ‌کس با ترسش خراب نمی‌کنه!"),                       # 28 -> Shot 18
    ("قانونِ دوم: محیطِ اطرافت رو عوض کن!",                "قانون دوم: محیط اطرافت رو عوض کن!"),                  # 29 -> Shot 19
    ("جایی بشین که رشدت عادی باشه، نه تهدید!",            "جایی بشین که رشدت عادی باشه، نه تهدید!"),             # 30 -> Shot 20
    ("یادت باشه: کسی که بالاتر از توئه،",                 "یادت باشه: کسی که بالاتر از توئه،"),                  # 31 -> Shot 21
    ("هیچ‌وقت از پایین پاتو نمی‌کشه!",                     "هیچ‌وقت از پایین پاتو نمی‌کشه!"),                     # 32 -> Shot 22
    ("تو هم این جمله‌های دلسوزانه رو شنیدی؟",             "تو هم این جمله‌های «دلسوزانه» رو شنیدی؟"),           # 33 -> Shot 22
    ("عددِ یک یا دو رو تو کامنت بنویس!",                   "عدد ۱ یا ۲ رو تو کامنت بنویس!"),                      # 34 -> Shot 23
]

# 46 Synchronized Luxury Foley & Whip-Cut Cues
SFX_CUE_MAP = [
    ("c01_bucket",   0,  0, "whoosh",       -0.02),
    ("_c01_rim",     1,  2, "ping",          0.02),
    ("c02_one",      2,  0, "whip",         -0.05),
    ("_c02_free",    3,  3, "bell_ding",     0.00),
    ("c03_ten",      4,  0, "whip",         -0.05),
    ("_c03_light",   5,  2, "riser",        -0.20),
    ("c04_pull",     6,  0, "crab_pinch",   -0.02),
    ("_c04_thud",    6,  4, "impact_boom",   0.02),
    ("c05_law",      7,  0, "whoosh",       -0.05),
    ("_c05_scan",    7,  2, "scan",          0.00),
    ("c05_title",    8,  0, "stamp",        -0.02),

    ("c06_stranger", 9,  0, "whip",         -0.05),
    ("c07_close",   11,  0, "crab_pinch",   -0.02),
    ("c08_circle",  12,  0, "scale_tip",    -0.02),
    ("c09_why",     13,  0, "whoosh",       -0.05),
    ("_c09_hb",     14,  2, "heartbeat",     0.02),
    ("c10_excuse",  15,  0, "whip",         -0.05),
    ("_c10_stamp",  16,  3, "stamp",         0.00),
    ("c11_rise",    17,  0, "whoosh",       -0.05),
    ("c11_break",   18,  3, "shatter",      -0.02),
    ("c12_mirror",  19,  0, "mirror_ring",  -0.02),
    ("_c12_glare",  20,  2, "scan",          0.02),

    ("c13_mask",    21,  0, "whip",         -0.05),
    ("_c13_drop",   22,  2, "chain_clink",   0.02),
    ("c14_quote1",  23,  0, "screen_on",    -0.02),
    ("_c14_slam",   23,  4, "stamp",         0.00),
    ("c15_quote2",  24,  0, "whip",         -0.05),
    ("_c15_chain",  24,  3, "chain_clink",   0.02),
    ("c16_cut",     25,  0, "slash",        -0.02),

    ("c17_silent",  26,  0, "whip",         -0.05),
    ("_c17_keys",   26,  3, "typing",        0.02),
    ("c18_lock",    27,  0, "button_press", -0.02),
    ("c19_room",    29,  0, "whip",         -0.05),
    ("c20_climb",   30,  0, "ping",          0.00),
    ("c21_above",   31,  0, "scale_tip",    -0.02),
    ("c22_summit",  32,  0, "shatter",      -0.02),
    ("_c22_chime",  33,  1, "mirror_ring",   0.02),
    ("c23_cta",     34,  0, "button_press",  0.00),
    ("_c23_p2",     34,  3, "ping",          0.05),
]


# =============================================================================
# BESPOKE EPISODE 07 MONOCHROME @ENSAN.BESHAM VECTOR ACTORS & METAPHORS
# =============================================================================
def draw_glow_line(cs, cg, x1, y1, x2, y2, alpha=1.0, lw_s=2.4, lw_g=5.5, dashed=False):
    if alpha <= 0.01:
        return
    for ctx, lw, al in ((cs, lw_s, alpha * 0.90), (cg, lw_g, alpha * 0.36)):
        ctx.save()
        ctx.set_dash([8.0, 7.0] if dashed else [])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()
        ctx.restore()


def draw_crab_monoline(
    cs, cg, cx: float, cy: float, scale: float = 1.0,
    pinch_open: float = 0.5, rot: float = 0.0, alpha: float = 1.0
):
    """
    Minimalist geometric @ensan.besham monoline crab:
    Crisp elliptical shell + 2 eye stalks + 6 jointed walking legs + 2 raised pincer claws!
    """
    if alpha <= 0.01:
        return
    for ctx, lw, al in ((cs, 2.5, alpha * 0.96), (cg, 5.4, alpha * 0.40)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.translate(cx, cy)
        ctx.rotate(rot)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)

        # Oval carapace shell
        ctx.save()
        ctx.scale(1.35, 0.90)
        ctx.arc(0, 0, 26.0 * scale, 0, 2 * math.pi)
        ctx.restore()
        if ctx is cs:
            ctx.set_source_rgba(0.035, 0.035, 0.05, 0.94 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.stroke()

        # Two small stalked eyes
        for sx in (-10.0, 10.0):
            ctx.move_to(sx * scale, -22 * scale)
            ctx.line_to(sx * 1.15 * scale, -32 * scale)
            ctx.stroke()
            ctx.arc(sx * 1.15 * scale, -35 * scale, 2.8 * scale, 0, 2 * math.pi)
            ctx.fill()

        # 3 jointed walking legs on each side
        for side in (-1.0, 1.0):
            for li, ly_off in enumerate((-8.0, 3.0, 14.0)):
                x0_l = side * 32.0 * scale
                y0_l = ly_off * scale
                xk = side * (52.0 - li * 3.0) * scale
                yk = (ly_off - 6.0 + li * 4.0) * scale
                xf = side * (62.0 - li * 5.0) * scale
                yf = (ly_off + 16.0 + li * 4.0) * scale
                ctx.move_to(x0_l, y0_l)
                ctx.line_to(xk, yk)
                ctx.line_to(xf, yf)
                ctx.stroke()

        # Two raised pincer arms & snapping claws reaching UPWARD!
        for side in (-1.0, 1.0):
            ax0, ay0 = side * 24.0 * scale, -18.0 * scale
            aex, aey = side * 42.0 * scale, -40.0 * scale
            acx, acy = side * 32.0 * scale, -62.0 * scale
            ctx.move_to(ax0, ay0)
            ctx.line_to(aex, aey)
            ctx.line_to(acx, acy)
            ctx.stroke()
            # Two pincer jaws opening/closing
            jaw = (0.18 + 0.36 * pinch_open)
            for j_sign in (-1.0, 1.0):
                ang = -math.pi / 2 + j_sign * jaw - side * 0.15
                jx = acx + math.cos(ang) * 18.0 * scale
                jy = acy + math.sin(ang) * 18.0 * scale
                ctx.move_to(acx, acy)
                ctx.line_to(jx, jy)
                ctx.stroke()
        ctx.restore()


def draw_open_bucket(
    cs, cg, cx: float, top_y: float, top_w: float, bot_w: float, h: float,
    alpha: float = 1.0, draw_p: float = 1.0
):
    """Architectural tapered open-top bucket in pure monochrome OLED space."""
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    bot_y = top_y + h
    rx_t, ry_t = top_w * 0.5, 30.0
    rx_b, ry_b = bot_w * 0.5, 22.0

    for ctx, lw, al in ((cs, 2.8, alpha * 0.94), (cg, 6.2, alpha * 0.42)):
        ctx.save()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        # Side walls + curved bottom
        ctx.new_path()
        ctx.move_to(cx - rx_t, top_y)
        ctx.line_to(cx - rx_b, bot_y)
        ctx.curve_to(cx - rx_b * 0.5, bot_y + ry_b * 1.35, cx + rx_b * 0.5, bot_y + ry_b * 1.35, cx + rx_b, bot_y)
        ctx.line_to(cx + rx_t, top_y)
        set_stroke_draw(ctx, draw_p, h * 2.4 + bot_w)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()

        # Glowing open elliptical top rim (lidless!)
        ctx.set_dash([])
        ctx.save()
        ctx.translate(cx, top_y)
        ctx.scale(1.0, ry_t / rx_t)
        ctx.arc(0, 0, rx_t, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(1, 1, 1, al * 0.95)
        ctx.set_line_width(lw)
        ctx.stroke()
        ctx.restore()


def draw_pulling_hand_from_below(cs, cg, x0: float, y0: float, tx: float, ty: float, alpha: float = 1.0):
    """Anatomical vector arm + gripping hand reaching upward from the pit to tug the climber's ankle!"""
    if alpha <= 0.01:
        return
    for ctx, lw, al in ((cs, 2.8, alpha * 0.94), (cg, 5.8, alpha * 0.40)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        mx = 0.5 * (x0 + tx) + (18.0 if x0 > tx else -18.0)
        my = 0.5 * (y0 + ty) + 22.0
        ctx.move_to(x0, y0)
        ctx.curve_to(mx, my, tx + (10 if x0 > tx else -10), ty + 28, tx, ty)
        ctx.stroke()
        # Three gripping fingers wrapping around ankle target!
        for fi in (-1, 0, 1):
            ctx.move_to(tx, ty + fi * 6)
            ctx.line_to(tx + (-16 if x0 > tx else 16), ty - 6 + fi * 6)
            ctx.stroke()
        ctx.restore()


def draw_caring_mask_and_anchor(cs, cg, cx: float, cy: float, split_p: float, t: float, alpha: float = 1.0):
    """
    Minimalist smiling 'caring/joking' mask sliding sideways to reveal a heavy downward iron anchor!
    """
    if alpha <= 0.01:
        return
    mask_x = cx + 115.0 * split_p
    anc_x  = cx - 85.0 * split_p

    # 1. Heavy downward anchor behind the mask!
    if split_p > 0.04:
        al_a = alpha * clamp(split_p * 1.4)
        ay = cy + 15.0 + math.sin(t * 3.0) * 5.0
        for ctx, lw, al in ((cs, 3.0, al_a * 0.95), (cg, 6.4, al_a * 0.42)):
            ctx.save(); ctx.set_dash([])
            ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            # Top ring + vertical shank + crossbar + curved flukes
            ctx.arc(anc_x, ay - 115, 18, 0, 2 * math.pi); ctx.stroke()
            ctx.move_to(anc_x, ay - 97); ctx.line_to(anc_x, ay + 95); ctx.stroke()
            ctx.move_to(anc_x - 52, ay - 52); ctx.line_to(anc_x + 52, ay - 52); ctx.stroke()
            ctx.arc(anc_x, ay + 15, 82, math.radians(22), math.radians(158)); ctx.stroke()
            # Arrowheads on flukes
            for sgn in (-1, 1):
                fx = anc_x + sgn * 76
                fy = ay + 46
                ctx.move_to(fx, fy); ctx.line_to(fx - sgn * 18, fy + 6); ctx.stroke()
            ctx.restore()

    # 2. Smiling outer mask ("نقابِ دلسوزی و شوخی")
    for ctx, lw, al in ((cs, 2.8, alpha * 0.96), (cg, 6.0, alpha * 0.42)):
        ctx.save(); ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        rounded_rect_path(ctx, mask_x - 96, cy - 125, 192, 240, 82)
        if ctx is cs:
            ctx.set_source_rgba(0.035, 0.035, 0.05, 0.95 * alpha); ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        # Happy curved eyes
        ctx.arc(mask_x - 36, cy - 32, 18, math.pi * 1.15, math.pi * 1.85); ctx.stroke()
        ctx.arc(mask_x + 36, cy - 32, 18, math.pi * 1.15, math.pi * 1.85); ctx.stroke()
        # Big polite smile arc
        ctx.arc(mask_x, cy + 12, 48, math.radians(22), math.radians(158)); ctx.stroke()
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
        tc["c02_one"],
        tc["c03_ten"],
        tc["c04_pull"] - 0.06,
        tc["c05_law"],
        tc["c06_stranger"],
        tc["c07_close"] - 0.06,
        tc["c08_circle"],
        tc["c09_why"],
        tc["c10_excuse"],
        tc["c11_rise"],
        tc["c12_mirror"] - 0.06,
        tc["c13_mask"],
        tc["c14_quote1"],
        tc["c15_quote2"],
        tc["c16_cut"] - 0.06,
        tc["c17_silent"],
        tc["c18_lock"],
        tc["c19_room"],
        tc["c20_climb"],
        tc["c21_above"],
        tc["c22_summit"] - 0.06,
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

    chapters = [0.0, b05, b06, b10, b13, b17, b23]
    draw_hud_chrome(cs, cg, txts, fonts, t, total_dur, EP_CODE, EP_TITLE, chapters)
    draw_ambient_particles(cs, t, alpha=0.82 * clamp((outro_t0 - t) / 0.8))

    # =========================================================================
    # SHOT 01 (b01..b02): Open Lidless Crab Bucket in Pitch-Black OLED Space!
    # =========================================================================
    w = _shot_win(t, b01, b02)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b01, b02, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=880)
        p_in = ease_out_cubic(clamp((t - b01) / 0.70))

        # Dashed lid floating away above to highlight "NO LID!"
        lid_y = 575.0 - 55.0 * p_in
        for ctx, lw, al in ((cs, 2.2, w * 0.55), (cg, 4.8, w * 0.22)):
            ctx.save(); ctx.set_dash([10.0, 8.0])
            ctx.translate(540, lid_y); ctx.rotate(-0.12 * p_in); ctx.scale(1.0, 0.09)
            ctx.arc(0, 0, 225, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

        draw_open_bucket(cs, cg, 540, 745, 430, 330, 445, alpha=w, draw_p=p_in)
        draw_crab_monoline(cs, cg, 540, 1085, scale=1.18, pinch_open=0.5 + 0.4*math.sin(t*4), alpha=w * p_in)

        sp_h1 = get_fitted_text_sprite("چرا سطلِ خرچنگ‌ها «دَر» نداره؟", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        sp_s1 = get_fitted_text_sprite("بدونِ درپوش — کاملاً باز!", fonts.light_22, 420, (195, 195, 212, 255))
        stx.append((sp_h1, 540, 385, w))
        stx.append((sp_s1, 540, 500, w * p_in))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=880)

    # =========================================================================
    # SHOT 02 (b02..b03): ONE Lone Crab Climbs Out Easily into Freedom!
    # =========================================================================
    w = _shot_win(t, b02, b03)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b02, b03, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        cp = ease_in_out_cubic(clamp((t - b02) / max(0.6, (b03 - b02) * 0.78)))

        draw_spotlight_cone(cs, cg, 540, 480, 355, 725, 920, alpha=w * 0.35)
        draw_open_bucket(cs, cg, 540, 790, 420, 325, 420, alpha=w)
        # Lone crab climbs smoothly up right wall and over the rim!
        crab_x = 540 + 145 * math.sin(cp * math.pi * 0.65)
        crab_y = 1095 - 395 * cp
        draw_crab_monoline(cs, cg, crab_x, crab_y, scale=1.22, pinch_open=0.7, rot=-0.25 * (1.0 - cp), alpha=w)

        sp_1c = get_fitted_text_sprite("۱ خرچنگِ تنها = فرارِ راحت!", fonts.eb_68, 860, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_1c, 540, 390, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 03 (b03..b04): 10 Crabs in the Bucket — One Reaches the Rim of Light!
    # =========================================================================
    w = _shot_win(t, b03, b04)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b03, b04, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        up_p = ease_out_cubic(clamp((t - b03) / max(0.5, (b04 - b03) * 0.80)))

        draw_spotlight_cone(cs, cg, 540, 510, 370, 710, 880, alpha=w * 0.38)
        draw_open_bucket(cs, cg, 540, 780, 450, 350, 440, alpha=w)

        # Crowd of crabs clustered at bottom of bucket
        for cx_c, cy_c, sc_c in ((435, 1135, 0.90), (540, 1150, 0.95), (645, 1135, 0.90), (480, 1055, 0.92), (600, 1055, 0.92)):
            draw_crab_monoline(cs, cg, cx_c, cy_c, scale=sc_c, pinch_open=0.6 + 0.3*math.sin(t*6 + cx_c), alpha=w * 0.85)

        # Climber crab nearing the bright top rim!
        top_cy = 965 - 175 * up_p
        draw_crab_monoline(cs, cg, 540, top_cy, scale=1.25, pinch_open=0.8, alpha=w)

        sp_10 = get_fitted_text_sprite("۱۰ خرچنگ توی یه سطل...", fonts.eb_68, 860, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_10, 540, 390, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 04 (b04..b05): Extreme Zoom — Claws Yank the Climber Back Down!
    # =========================================================================
    w = _shot_win(t, b04, b05)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b04, b05, base_in=0.92) + impact_punch(t, b04 + 0.06, 0.05, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=880)
        yank_p = ease_in_out_cubic(clamp((t - (b04 + 0.08)) / 0.55))

        draw_open_bucket(cs, cg, 540, 720, 480, 375, 490, alpha=w * 0.75)
        climber_y = 755 + 215 * yank_p
        draw_crab_monoline(cs, cg, 540, climber_y, scale=1.42, pinch_open=0.3, alpha=w)
        # Two lower crabs clamping onto its legs & dragging down!
        draw_crab_monoline(cs, cg, 455, climber_y + 135, scale=1.18, pinch_open=0.05, rot=0.18, alpha=w)
        draw_crab_monoline(cs, cg, 625, climber_y + 135, scale=1.18, pinch_open=0.05, rot=-0.18, alpha=w)
        draw_shockwave_ring(cs, cg, 540, climber_y + 60, clamp((t - b04) / 0.65), max_r=250, alpha=w * 0.85)

        sp_y1 = get_fitted_text_sprite("می‌کشنش پایین!", fonts.eb_84, 860, (255, 255, 255, 255), glow=0.92)
        sp_y2 = get_fitted_text_sprite("«اگه ما نمی‌ریم بیرون، تو هم نباید بری!»", fonts.bold_30, 820, (215, 215, 232, 255))
        stx.append((sp_y1, 540, 385, w))
        stx.append((sp_y2, 540, 492, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=880)

    # =========================================================================
    # SHOT 05 (b05..b06): AI Observatory Eye + Human Inside the Crab Bucket!
    # =========================================================================
    w = _shot_win(t, b05, b06)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b05, b06, base_in=0.93) + impact_punch(t, tc["c05_title"], 0.045, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=850)

        draw_observatory_eye(cs, cg, 540, 345, 52.0, t, alpha=w, scan_targets=[(380, 1080), (540, 1050), (700, 1080)])
        draw_open_bucket(cs, cg, 540, 795, 450, 355, 435, alpha=w)
        draw_character_with_phone(cs, cg, 540, 1210, scale=1.78, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)

        tp = ease_out_cubic(clamp((t - (tc["c05_title"] - 0.15)) / 0.40))
        sp_law = get_fitted_text_sprite("قانونِ سطلِ خرچنگ‌ها", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.95)
        stx.append((sp_law, 540, 585, w * max(0.25, tp)))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=850)

    # =========================================================================
    # SHOT 06 (b06..b07): Strangers Walk Past Indifferently While You Climb!
    # =========================================================================
    w = _shot_win(t, b06, b07)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b06, b07, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        # Central glowing ladder
        draw_glow_line(cs, cg, 485, 560, 485, 1240, w * 0.85, lw_s=2.8)
        draw_glow_line(cs, cg, 595, 560, 595, 1240, w * 0.85, lw_s=2.8)
        for ry in range(630, 1210, 95):
            draw_glow_line(cs, cg, 485, ry, 595, ry, w * 0.72, lw_s=2.2)

        # Distant dim strangers on left & right ignoring you completely
        draw_human_figure(cs, 225, 1235, scale=1.35, alpha=w * 0.32, lw=2.0)
        draw_human_figure(cs, 855, 1235, scale=1.35, alpha=w * 0.32, lw=2.0)
        draw_character_with_phone(cs, cg, 540, 985, scale=1.62, raise_p=0.9, screen_glow=1.0, alpha=w, t=t)

        sp_st = get_fitted_text_sprite("غریبه‌ها اصلاً کاری بهت ندارن...", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.7)
        sp_s2 = get_fitted_text_sprite("غریبه", fonts.light_22, 180, (150, 150, 168, 255))
        stx.append((sp_st, 540, 395, w))
        stx.append((sp_s2, 225, 1280, w * 0.65))
        stx.append((sp_s2, 855, 1280, w * 0.65))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 07 (b07..b08): Hands from Below Grabbing Climber's Ankle on Ladder!
    # =========================================================================
    w = _shot_win(t, b07, b08)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b07, b08, base_in=0.92) + impact_punch(t, b07 + 0.06, 0.045, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=900)
        gp = ease_out_cubic(clamp((t - b07) / 0.48))

        draw_glow_line(cs, cg, 480, 520, 480, 1280, w * 0.85, lw_s=3.0)
        draw_glow_line(cs, cg, 600, 520, 600, 1280, w * 0.85, lw_s=3.0)
        for ry in range(590, 1250, 95):
            draw_glow_line(cs, cg, 480, ry, 600, ry, w * 0.72, lw_s=2.4)

        foot_y = 955 + 32 * gp
        draw_character_with_phone(cs, cg, 540, foot_y, scale=1.78, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)

        # Familiar hands reaching up from bottom to grip both ankles!
        draw_pulling_hand_from_below(cs, cg, 355, 1275, 516, foot_y - 12, alpha=w * gp)
        draw_pulling_hand_from_below(cs, cg, 725, 1275, 564, foot_y - 12, alpha=w * gp)
        draw_shockwave_ring(cs, cg, 540, foot_y - 12, clamp((t - b07) / 0.65), max_r=220, alpha=w * 0.8)

        sp_h7 = get_fitted_text_sprite("نزدیک‌ترین آدم‌ها پات رو می‌گیرن!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.88)
        stx.append((sp_h7, 540, 390, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=900)

    # =========================================================================
    # SHOT 08 (b08..b09): Friend, Relative, Coworker Pedestals Pulling You Level!
    # =========================================================================
    w = _shot_win(t, b08, b09)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b08, b09, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        sp_h8 = get_fitted_text_sprite("دایره‌ی آشنای همیشگی:", fonts.bold_44, 840, (255, 255, 255, 255), glow=0.7)
        stx.append((sp_h8, 540, 395, w))

        draw_glow_line(cs, cg, 140, 1225, 940, 1225, w * 0.55)
        for px_c, ph_c, lbl_c, is_you in (
            (255, 140, "فامیل", False),
            (540, 295, "تو (در حالِ رشد)", True),
            (825, 140, "رفیق / همکار", False),
        ):
            for ctx, lw, al in ((cs, 2.7, w * 0.94), (cg, 5.8, w * 0.40)):
                ctx.save(); ctx.set_dash([])
                rounded_rect_path(ctx, px_c - 95, 1225 - ph_c, 190, ph_c, 12)
                if ctx is cs and is_you:
                    ctx.set_source_rgba(1, 1, 1, 0.14 * w); ctx.fill_preserve()
                ctx.set_source_rgba(1, 1, 1, al * (1.0 if is_you else 0.72))
                ctx.set_line_width(lw); ctx.stroke()
                ctx.restore()
            if is_you:
                draw_character_with_phone(cs, cg, px_c, 1225 - ph_c, scale=1.55, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)
            else:
                draw_human_figure(cs, px_c, 1225 - ph_c, scale=1.42, alpha=w * 0.85, lw=2.5)
                # Diagonal tether line pulling center character down toward their low level!
                draw_glow_line(cs, cg, px_c, 1225 - ph_c - 95, 540 + (35 if px_c > 540 else -35), 1225 - 295, w * 0.65, dashed=True)
            sp_l = get_fitted_text_sprite(lbl_c, fonts.bold_30 if is_you else fonts.reg_26, 240, (255, 255, 255, 255) if is_you else (190, 190, 208, 255))
            stx.append((sp_l, px_c, 1278, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 09 (b09..b10): Why Does Your Growth Make Non-Enemies Uncomfortable?
    # =========================================================================
    w = _shot_win(t, b09, b10)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b09, b10, base_in=0.94) + impact_punch(t, tc["_c09_hb"], 0.038, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        draw_human_figure(cs, 540, 1125, scale=3.5, alpha=w * 0.54, lw=2.1)
        draw_human_figure(cg, 540, 1125, scale=3.5, alpha=w * 0.22, lw=4.5)
        draw_hypnotic_chronograph_ring(cs, cg, 540, 855, 128.0, t, alpha=w * 0.92, draw_p=1.0, speed=1.5)
        draw_ecg_waveform(cs, cg, 150, 930, 1215, t, amp=44.0, alpha=w)

        sp_q = get_text_sprite("؟", fonts.eb_84, (255, 255, 255, 255), glow=0.9)
        sp_h9 = get_fitted_text_sprite("چرا رشدِ تو معذبشون می‌کنه؟", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        sp_s9 = get_fitted_text_sprite("از بدجنسی نیست؛ از یه ترسِ پنهانه!", fonts.reg_26, 760, (205, 205, 222, 255))
        stx.append((sp_q, 540, 855, w))
        stx.append((sp_h9, 540, 355, w))
        stx.append((sp_s9, 540, 432, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 10 (b10..b11): The Comforting Excuse Wall ("شرایط خرابه، نمیشه!")
    # =========================================================================
    w = _shot_win(t, b10, b11)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b10, b11, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        sp_h10 = get_fitted_text_sprite("پناه‌گاهِ امنِ بهانه:", fonts.bold_44, 840, (255, 255, 255, 255), glow=0.7)
        stx.append((sp_h10, 540, 395, w))

        # Three stagnant figures standing under one heavy horizontal ceiling ("مشکل از شرایطه!")
        draw_safe_card(cs, cg, stx, 540, 685, 760, 118, [("سقفِ بهانه: «تو این شرایط هیچ‌کس نمی‌تونه!»", fonts.bold_30, 0, (255, 255, 255, 255), 0.5)], alpha=w, glow_border=True)
        draw_glow_line(cs, cg, 180, 1165, 900, 1165, w * 0.55)
        for fx in (330, 540, 750):
            draw_human_figure(cs, fx, 1165, scale=1.65, alpha=w * 0.85, lw=2.6)
        sp_sub10 = get_fitted_text_sprite("وقتی همه درجا می‌زنن، وجدانِ همه راحته!", fonts.reg_26, 800, (195, 195, 212, 255))
        stx.append((sp_sub10, 540, 1235, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 11 (b11..b12): You Rise & Shatter the Excuse Ceiling in Half!
    # =========================================================================
    w = _shot_win(t, b11, b12)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b11, b12, base_in=0.92) + impact_punch(t, tc["c11_break"], 0.045, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        rp = ease_out_cubic(clamp((t - b11) / 0.65))

        # Rising central pillar breaking straight through the horizontal excuse ceiling!
        pil_h = 390 * rp
        for ctx, lw, al in ((cs, 3.0, w * 0.96), (cg, 6.5, w * 0.45)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 445, 1210 - pil_h, 190, pil_h, 14)
            if ctx is cs:
                ctx.set_source_rgba(1, 1, 1, 0.16 * w); ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            # Two cracked halves of the broken ceiling tilting outward!
            for side in (-1, 1):
                ctx.save()
                ctx.translate(540 + side * (195 + 45 * rp), 785 - 25 * rp)
                ctx.rotate(side * 0.34 * rp)
                rounded_rect_path(ctx, -135, -32, 270, 64, 10)
                ctx.stroke()
                ctx.restore()
            ctx.restore()

        draw_character_with_phone(cs, cg, 540, 1210 - pil_h, scale=1.65, raise_p=1.0, screen_glow=1.0, alpha=w, t=t)
        draw_shockwave_ring(cs, cg, 540, 785, clamp((t - tc["c11_break"]) / 0.65), max_r=310, alpha=w * 0.85)
        sp_h11 = get_fitted_text_sprite("اوج گرفتنِ تو = نابودیِ بهونه‌ی اونا!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.88)
        stx.append((sp_h11, 540, 390, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 12 (b12..b13): The Blazing Full-Length Mirror Effect!
    # =========================================================================
    w = _shot_win(t, b12, b13)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b12, b13, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        mp_p = ease_out_cubic(clamp((t - b12) / 0.55))

        sp_h12 = get_fitted_text_sprite("تو می‌شی «آینه‌ی تمام‌قدِ» ترس‌هاشون!", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.8)
        stx.append((sp_h12, 540, 390, w))

        draw_glow_line(cs, cg, 140, 1210, 940, 1210, w * 0.55)
        # Central tall arched full-length mirror!
        for ctx, lw, al in ((cs, 3.2, w * 0.98), (cg, 7.2, w * 0.48)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 488, 640, 104, 570, 52)
            if ctx is cs:
                ctx.set_source_rgba(1, 1, 1, 0.14 * w); ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

        # Right: You standing tall on pedestal | Left: Stagnant figure hit by mirror glare rays!
        for ctx, lw, al in ((cs, 2.6, w * 0.9), (cg, 5.5, w * 0.38)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 705, 980, 170, 230, 12); ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()
        draw_character_with_phone(cs, cg, 790, 980, scale=1.52, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)
        draw_human_figure(cs, 275, 1210, scale=1.62, alpha=w * 0.85, lw=2.6)

        # Glare rays bouncing from mirror onto left figure!
        for ry_m in (760, 880, 1000):
            draw_glow_line(cs, cg, 488, ry_m, 315, ry_m + 95, w * mp_p * 0.72, dashed=True)

        sp_mr = get_fitted_text_sprite("موفقیتِ تو", fonts.bold_30, 220, (255, 255, 255, 255))
        sp_ml = get_fitted_text_sprite("یادآوریِ کم‌کاریِ خودشون!", fonts.reg_26, 300, (200, 200, 218, 255))
        stx.append((sp_mr, 790, 1265, w))
        stx.append((sp_ml, 275, 1265, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 13 (b13..b14): Smiling Mask of "Caring" Hiding a Heavy Iron Anchor!
    # =========================================================================
    w = _shot_win(t, b13, b14)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b13, b14, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        sp_p = ease_out_cubic(clamp((t - (b13 + 0.18)) / 0.65))

        sp_h13 = get_fitted_text_sprite("پشتِ نقابِ «دلسوزی و شوخی»:", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_h13, 540, 405, w))
        draw_caring_mask_and_anchor(cs, cg, 540, 865, sp_p, t, alpha=w)

        sp_m_lbl = get_fitted_text_sprite("ظاهر: شوخی و دلسوزی", fonts.bold_30, 320, (225, 225, 240, 255))
        sp_a_lbl = get_fitted_text_sprite("باطن: لنگرِ توقفِ تو!", fonts.bold_30, 320, (255, 255, 255, 255), glow=0.6)
        stx.append((sp_m_lbl, 685, 1135, w))
        stx.append((sp_a_lbl, 385, 1205, w * sp_p))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 14 (b14..b15): POV Phone — Toxic "Caring" Fear Quotes!
    # =========================================================================
    w = _shot_win(t, b14, b15)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b14, b15, base_in=0.92) + impact_punch(t, tc["_c14_slam"], 0.038, 0.38)
        push_camera(cs, cg, zoom=cz, px=540, py=835)
        draw_pov_phone_in_hand(cs, cg, 540, 845, 386, 665, thumb_swipe=0.0, thumb_tap=0.0, alpha=w, draw_p=1.0)

        sp_c0 = get_fitted_text_sprite("دیالوگ‌های آشنا:", fonts.light_22, 248, (185, 185, 202, 255))
        sp_c1 = get_fitted_text_sprite("«ول کن بابا!»", fonts.bold_44, 248, (255, 255, 255, 255), glow=0.65)
        sp_c2 = get_fitted_text_sprite("«تو این بازار نمیشه!»", fonts.bold_30, 248, (235, 235, 248, 255))
        sp_c3 = get_fitted_text_sprite("«آخرش شکست می‌خوری!»", fonts.bold_30, 248, (255, 255, 255, 255), glow=0.55)
        stx.append((sp_c0, 534, 578, w))
        stx.append((sp_c1, 534, 650, w))
        stx.append((sp_c2, 534, 724, w))
        stx.append((sp_c3, 534, 788, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=835)

    # =========================================================================
    # SHOT 15 (b15..b16): Sarcastic Joke Weights Hanging off Character!
    # =========================================================================
    w = _shot_win(t, b15, b16)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b15, b16, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        sp_h15 = get_fitted_text_sprite("نیش‌و‌کنایه به اسمِ «شوخی»:", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_h15, 540, 395, w))

        draw_glow_line(cs, cg, 200, 1210, 880, 1210, w * 0.5)
        draw_character_with_phone(cs, cg, 540, 1210, scale=1.90, raise_p=0.80, screen_glow=0.9, alpha=w, t=t)

        # Two heavy quote boxes tethered to character's shoulders!
        draw_glow_line(cs, cg, 500, 995, 285, 815, w * 0.65, dashed=True)
        draw_glow_line(cs, cg, 580, 995, 795, 815, w * 0.65, dashed=True)
        draw_safe_card(cs, cg, stx, 285, 760, 340, 96, [("«چه جوگیر شدی!»", fonts.bold_30, 0, (240, 240, 252, 255), 0.4)], alpha=w)
        draw_safe_card(cs, cg, stx, 795, 760, 340, 96, [("«چقدر عوض شدی!»", fonts.bold_30, 0, (240, 240, 252, 255), 0.4)], alpha=w)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 16 (b16..b17): Blazing Light-Blade Slicing Every Downward Rope!
    # =========================================================================
    w = _shot_win(t, b16, b17)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b16, b17, base_in=0.92) + impact_punch(t, b16 + 0.06, 0.048, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        sl_p = ease_out_cubic(clamp((t - b16) / 0.45))

        sp_h16 = get_fitted_text_sprite("چطور از سطلِ خرچنگ‌ها خارج بشی؟", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.88)
        stx.append((sp_h16, 540, 405, w))

        draw_character_with_phone(cs, cg, 540, 990 - 55 * sl_p, scale=1.82, raise_p=1.0, screen_glow=1.0, alpha=w, t=t)
        # Diagonal blazing light-blade slicing cleanly underneath character's feet!
        draw_glow_line(cs, cg, 175, 1145, 175 + 730 * sl_p, 1145 - 165 * sl_p, w, lw_s=4.2, lw_g=10.5)
        draw_star4(cs, 175 + 730 * sl_p, 1145 - 165 * sl_p, 24.0, w)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 17 (b17..b18): Rule 1 — Build in Complete Silence Inside Focus Dome!
    # =========================================================================
    w = _shot_win(t, b17, b18)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b17, b18, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=880)
        dp = ease_out_cubic(clamp((t - b17) / 0.55))

        sp_r1 = get_fitted_text_sprite("قانونِ ۱: توی سکوتِ مطلق بساز!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_r1, 540, 405, w))

        # Protective acoustic dome around character focused at laptop desk!
        for ctx, lw, al in ((cs, 2.8, w * 0.94), (cg, 6.4, w * 0.42)):
            ctx.save()
            ctx.arc(540, 1145, 315, math.pi, 2 * math.pi)
            set_stroke_draw(ctx, dp, math.pi * 315)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.set_dash([10.0, 8.0])
            ctx.arc(540, 1145, 345, math.pi * 1.06, math.pi * 1.94)
            ctx.set_source_rgba(1, 1, 1, al * 0.48); ctx.set_line_width(lw * 0.7); ctx.stroke()
            ctx.restore()

        draw_character_at_desk(cs, cg, 540, 1145, scale=1.22, t=t, alpha=w)
        sp_s17 = get_fitted_text_sprite("قبل از نتیجه، پروژه‌ت رو جار نزن!", fonts.bold_30, 740, (220, 220, 236, 255))
        stx.append((sp_s17, 540, 1235, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=880)

    # =========================================================================
    # SHOT 18 (b18..b19): POV Phone Lock — What They Don't Know, They Can't Ruin!
    # =========================================================================
    w = _shot_win(t, b18, b19)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b18, b19, base_in=0.92)
        push_camera(cs, cg, zoom=cz, px=540, py=835)
        draw_pov_phone_in_hand(cs, cg, 540, 845, 386, 665, thumb_swipe=0.0, thumb_tap=0.0, alpha=w, draw_p=1.0)

        # Clean padlock icon inside upper screen (y=600..665) + crisp text well above thumb!
        for ctx, lw, al in ((cs, 2.8, w * 0.96), (cg, 6.0, w * 0.42)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 498, 608, 72, 58, 12)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.arc(534, 608, 22, math.pi, 2 * math.pi); ctx.stroke()
            ctx.restore()

        sp_l1 = get_fitted_text_sprite("حالتِ بی‌صدا", fonts.bold_44, 248, (255, 255, 255, 255), glow=0.7)
        sp_l2 = get_fitted_text_sprite("فقط نتیجه رو نشون بده،", fonts.reg_26, 248, (215, 215, 230, 255))
        sp_l3 = get_fitted_text_sprite("نه تصمیمِ خام رو!", fonts.bold_30, 248, (255, 255, 255, 255), glow=0.55)
        stx.append((sp_l1, 534, 712, w))
        stx.append((sp_l2, 534, 768, w))
        stx.append((sp_l3, 534, 818, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=835)

    # =========================================================================
    # SHOT 19 (b19..b20): Rule 2 — Leave the Bucket & Step Onto Ascending Stairs!
    # =========================================================================
    w = _shot_win(t, b19, b20)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b19, b20, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        sp_p = ease_out_cubic(clamp((t - b19) / 0.65))

        sp_r2 = get_fitted_text_sprite("قانونِ ۲: محیطِ اطرافت رو عوض کن!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_r2, 540, 395, w))

        # Small dim bucket left behind on left -> 4 glowing ascending steps rising rightwards!
        draw_open_bucket(cs, cg, 225, 1085, 150, 115, 155, alpha=w * 0.42)
        for si in range(4):
            sx = 385 + si * 135
            sh = (95 + si * 82) * sp_p
            for ctx, lw, al in ((cs, 2.7, w * 0.94), (cg, 5.8, w * 0.40)):
                ctx.save(); ctx.set_dash([])
                rounded_rect_path(ctx, sx, 1240 - sh, 118, sh, 10)
                ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
                ctx.restore()
        draw_character_with_phone(cs, cg, 385 + 2 * 135 + 59, 1240 - (95 + 2 * 82) * sp_p, scale=1.48, raise_p=1.0, screen_glow=1.0, alpha=w, t=t)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 20 (b20..b21): Sit Where Growth Is Normal — 3 Rising Pillars Together!
    # =========================================================================
    w = _shot_win(t, b20, b21)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b20, b21, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        rp = ease_out_cubic(clamp((t - b20) / 0.55))

        sp_h20 = get_fitted_text_sprite("جایی بشین که رشدِ تو عادی باشه!", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.8)
        stx.append((sp_h20, 540, 395, w))

        draw_star4(cs, 540, 520, 28.0, w * 0.95)
        draw_star4(cg, 540, 520, 48.0, w * 0.55)
        draw_glow_line(cs, cg, 160, 1230, 920, 1230, w * 0.55)
        for px_b, ph_b, is_mid in ((285, 290, False), (540, 360, True), (795, 325, False)):
            hh = ph_b * rp
            for ctx, lw, al in ((cs, 2.8, w * 0.95), (cg, 6.0, w * 0.42)):
                ctx.save(); ctx.set_dash([])
                rounded_rect_path(ctx, px_b - 88, 1230 - hh, 176, hh, 14)
                if ctx is cs and is_mid:
                    ctx.set_source_rgba(1, 1, 1, 0.15 * w); ctx.fill_preserve()
                ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
                ctx.restore()
            if is_mid:
                draw_character_with_phone(cs, cg, px_b, 1230 - hh, scale=1.52, raise_p=1.0, screen_glow=1.0, alpha=w, t=t)
            else:
                draw_human_figure(cs, px_b, 1230 - hh, scale=1.42, alpha=w * 0.9, lw=2.6, star_mind=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 21 (b21..b22): People Above You Never Pull You Down from Below!
    # =========================================================================
    w = _shot_win(t, b21, b22)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b21, b22, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        sp_h21 = get_fitted_text_sprite("آدمِ بالاتر، هیچ‌وقت پات رو نمی‌کشه!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.88)
        stx.append((sp_h21, 540, 390, w))

        # High summit platform on Right extending helping arm to climber on Left!
        for ctx, lw, al in ((cs, 2.8, w * 0.95), (cg, 6.0, w * 0.42)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 615, 860, 260, 370, 16)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            rounded_rect_path(ctx, 225, 1045, 260, 185, 16)
            ctx.set_source_rgba(1, 1, 1, al * 0.8); ctx.stroke()
            ctx.restore()

        draw_human_figure(cs, 745, 860, scale=1.62, alpha=w * 0.95, lw=2.8, star_mind=True)
        draw_character_with_phone(cs, cg, 355, 1045, scale=1.62, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)
        # Upward helping connection beam between the two!
        draw_glow_line(cs, cg, 415, 895, 685, 725, w * 0.85, lw_s=3.0, lw_g=7.0)
        draw_safe_card(cs, cg, stx, 540, 1305, 800, 98, [("آدمِ بزرگ دستت رو می‌گیره؛ آدمِ راکد پات رو!", fonts.bold_30, 0, (255, 255, 255, 255), 0.5)], alpha=w, glow_border=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 22 (b22..b23): Liberation Summit — 24 Star-Shards & Illuminated Mind!
    # =========================================================================
    w = _shot_win(t, b22, b23)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b22, b23, base_in=0.94) + impact_punch(t, b22 + 0.06, 0.042, 0.45)
        push_camera(cs, cg, zoom=cz, px=540, py=880)

        burst_u = clamp((t - b22) / 1.15)
        if burst_u > 0.01:
            al_sh = w * (1.0 - burst_u * 0.65)
            for k in range(24):
                ang = k * (2 * math.pi / 24.0) + 0.12
                r_in = 85.0 + 275.0 * ease_out_cubic(burst_u)
                x1, y1 = 540 + math.cos(ang) * r_in, 880 + math.sin(ang) * r_in
                x2, y2 = 540 + math.cos(ang) * (r_in + 22), 880 + math.sin(ang) * (r_in + 22)
                draw_glow_line(cs, cg, x1, y1, x2, y2, al_sh, lw_s=2.4, lw_g=5.5)

        draw_spotlight_cone(cs, cg, 540, 460, 345, 735, 1185, alpha=w * 0.35)
        draw_glow_line(cs, cg, 220, 1185, 860, 1185, w * 0.65)
        draw_character_with_phone(cs, cg, 540, 1185, scale=2.05, raise_p=0.12, screen_glow=0.0, alpha=w, t=t)
        draw_star4(cs, 540, 1185 - 148 * 2.05, 22.0, w)
        draw_star4(cg, 540, 1185 - 148 * 2.05, 38.0, w * 0.75)

        sp_f22 = get_fitted_text_sprite("از سطل بیا بیرون و بی‌صدا اوج بگیر!", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.82)
        stx.append((sp_f22, 540, 400, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=880)

    # =========================================================================
    # SHOT 23 (b23..b24): Interactive Two-Pedestal Comment Arena (1 vs 2)!
    # =========================================================================
    w = _shot_win(t, b23, b24)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b23, b24, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        rp = ease_out_cubic(clamp((t - b23) / 0.48))

        sp_q23 = get_fitted_text_sprite("تجربه‌ی واقعیِ تو کدومه؟", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_q23, 540, 385, w))

        for bx, num_s, t1_s, t2_s in (
            (745, "۱", "آره، بارها دیدم!", "از نزدیک‌ترین آدم‌ها"),
            (335, "۲", "توی سکوت می‌سازم!", "بدونِ توضیح به بقیه"),
        ):
            ph = 370 * rp
            by_top = 1130 - ph
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
            stx.append((sp_n, bx, by_top + 110, w * rp))
            stx.append((sp_a, bx, by_top + 225, w * rp))
            stx.append((sp_b, bx, by_top + 292, w * rp))

        draw_character_with_phone(cs, cg, 540, 745, scale=1.18, raise_p=0.95, screen_glow=1.0, alpha=w * rp, t=t)
        draw_safe_card(cs, cg, stx, 540, 1255, 820, 104, [("عددش رو همین الان تو کامنت بنویس: ۱ یا ۲؟", fonts.bold_30, 0, (255, 255, 255, 255), 0.6)], alpha=w, glow_border=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 24 (b24..total_dur): Signature @zavieh.penhann Brand Endplate
    # =========================================================================
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
    """Generates subtitle baseline QA strip + 24-shot full contact sheet + 12-hero-shot sheet."""
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    sg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cg = cairo.Context(sg)
    ss = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cs = cairo.Context(ss)

    sub_strip = Image.new("RGB", (920, 14 * 105), (0, 0, 0))
    test_ln = meta["sub_lines"][min(4, len(meta["sub_lines"]) - 1)]
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

    bounds = _compute_shot_bounds(tc, outro_t0) + [td]
    ts_24 = [0.5 * (bounds[i] + bounds[i + 1]) for i in range(24)]
    ts_24[4] = clamp(tc["c05_title"] + 0.35, bounds[4] + 0.25, bounds[5] - 0.20)
    ts_24[10] = clamp(tc["c11_break"] + 0.35, bounds[10] + 0.25, bounds[11] - 0.20)

    pw24, ph24 = 270, 480
    grid24 = Image.new("RGB", (pw24 * 6, ph24 * 4), (16, 16, 20))
    for i, ts in enumerate(ts_24):
        ts_c = max(0.08, min(td - 0.12, ts))
        raw = render_scene_frame(ts_c, td, tc, meta["sub_lines"], fonts, sg, cg, ss, cs)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw24, ph24), Image.Resampling.LANCZOS)
        r, c = divmod(i, 6)
        grid24.paste(im, (c * pw24, r * ph24))
    grid24.save(os.path.join(qa_dir, "storyboard_24_shots.png"))

    pick_12 = [0, 1, 3, 4, 6, 7, 10, 11, 12, 16, 20, 22]
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

    print("=== [1/3] Building Studio v4.2 High-Loudness Master Audio (Locked Rasalgethi + Velvet Dark-Ambient + Foley) ===", flush=True)
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
        print("Usage: python src/episodes/ep07_crab_bucket_law.py --cloud-render <fonts> <work> <out.mp4> <qa_dir> [whisper_size]")
