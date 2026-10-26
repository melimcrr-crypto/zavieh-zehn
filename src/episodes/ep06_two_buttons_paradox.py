"""
Episode 06 (Studio v4.1 — Hyper-Cut Character & Velvet Dark-Ambient Cinema)
Topic: «کدوم دکمه رو می‌زنی؟ ۱۰ میلیاردِ قطعی، یا شیریاخط برای ۱۰۰ میلیارد؟»
Page: زاویه ذهن (@zavieh.penhann)

v4.1 Studio Upgrades:
  - 24 Rapid-Fire @ensan.besham Visual Shots (~2.5s average shot length across ~62s)
  - Expressive Human Character & First-Person POV Hand/Finger Rig acting out every beat:
    facing the glowing two-button console, POV finger pressing Button 1 (10B guaranteed) &
    Button 2 (50/50 100B coin toss), split destiny pedestals, calculator vs human heartbeat,
    climbing the steep 0->10B curve, shattering debt chains, leaning over the cliff-edge
    gamble, 3 AM empty-handed regret, POV phone Golden Rule, and interactive 1-vs-2 arena!
  - Velvet Dark-Ambient & Sparse Felt-Piano Score (-32.5 dBFS under speech, calm & clutter-free)
    + clean, tactile luxury Foley SFX (button_press, coin_flip, scale_tip, whip, shatter, chime)
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
    draw_ambient_particles, draw_cursor_pointer,
    impact_punch, push_camera, pop_camera_and_transform_texts,
    draw_shockwave_ring, draw_hypnotic_chronograph_ring,
    draw_hourglass_monolith, draw_ecg_waveform,
    draw_character_with_phone, draw_pov_phone_in_hand,
    draw_character_at_desk, draw_observatory_eye,
    composite_oled_frame,
)

EP_CODE = "۰۶"
EP_TITLE = "دو دکمه‌ی سرنوشت"

# 35 Short, Punchy, Spoken Tehrani Persian Phrases (4-6 words per line -> ~62s total, 24 rapid shots!)
SCRIPT_SEGMENTS = [
    # Act I — The Hook: Two Glowing Buttons (0..8 -> Shots 01..06)
    ("فرض کن همین الان جلوی دستت،",                      "فرض کن همین الان جلوی دستت،"),                      # 0  -> Shot 01
    ("دو تا دکمه‌ی نورانی گذاشتن:",                       "دو تا دکمه‌ی نورانی گذاشتن:"),                       # 1  -> Shot 02
    ("دکمه‌ی اول رو بزنی،",                               "دکمه‌ی اول رو بزنی،"),                               # 2  -> Shot 03
    ("همین ثانیه ده میلیاردِ نقد می‌گیری!",               "همین ثانیه ۱۰ میلیارد نقد می‌گیری!"),               # 3  -> Shot 03
    ("دکمه‌ی دوم رو بزنی،",                               "دکمه‌ی دوم رو بزنی،"),                               # 4  -> Shot 04
    ("یه شیر یا خطِ پنجاه پنجاهه:",                       "یه شیر یا خط ۵۰-۵۰ئه:"),                             # 5  -> Shot 04
    ("یا صد میلیارد می‌بری،",                             "یا ۱۰۰ میلیارد می‌بری،"),                             # 6  -> Shot 05
    ("یا دستِ خالی برمی‌گردی خونه!",                      "یا دست خالی برمی‌گردی خونه!"),                       # 7  -> Shot 05
    ("و فقط یه بار حقِ انتخاب داری!",                     "و فقط ۱ بار حق انتخاب داری!"),                       # 8  -> Shot 06

    # Act II — The Paper Math Trap vs Smart People (9..16 -> Shots 07..10)
    ("اگه از ماشین‌حساب بپرسی،",                          "اگه از ماشین‌حساب بپرسی،"),                          # 9  -> Shot 07
    ("بدونِ مکث می‌گه دکمه‌ی دوم!",                       "بدون مکث می‌گه دکمه‌ی دوم!"),                        # 10 -> Shot 07
    ("چون روی کاغذ ارزشِ اون شانس،",                      "چون روی کاغذ ارزش اون شانس،"),                       # 11 -> Shot 08
    ("پنجاه میلیارده؛ یعنی پنج برابرِ اولی!",             "۵۰ میلیارده؛ یعنی ۵ برابر اولی!"),                   # 12 -> Shot 08
    ("پس چرا بیشترِ آدمای باهوش،",                        "پس چرا بیشتر آدمای باهوش،"),                         # 13 -> Shot 09
    ("بازم دکمه‌ی ده میلیارد رو می‌زنن؟",                 "بازم دکمه‌ی ۱۰ میلیارد رو می‌زنن؟"),                 # 14 -> Shot 09
    ("چون زندگی ماشین‌حساب نیست؛",                        "چون زندگی ماشین‌حساب نیست؛"),                        # 15 -> Shot 10
    ("تو هزار بار شانسِ امتحان نداری!",                   "تو ۱۰۰۰ بار شانس امتحان نداری!"),                    # 16 -> Shot 10

    # Act III — Hidden Law of Diminishing Utility of Money (17..24 -> Shots 11..16)
    ("رازِ پنهانِ پول اینجاست:",                          "راز پنهان پول اینجاست:"),                            # 17 -> Shot 11
    ("ده میلیاردِ اول زندگیت رو می‌سازه!",                "۱۰ میلیارد اول زندگیت رو می‌سازه!"),                 # 18 -> Shot 11
    ("خیالت رو از قسط و اجاره راحت می‌کنه،",              "خیالت رو از قسط و اجاره راحت می‌کنه،"),              # 19 -> Shot 12
    ("و بهت قدرتِ نه گفتن می‌ده!",                        "و بهت قدرت «نه گفتن» می‌ده!"),                       # 20 -> Shot 13
    ("یعنی هشتاد درصدِ آرامشِ واقعی!",                    "یعنی ۸۰٪ آرامش واقعی!"),                             # 21 -> Shot 14
    ("اما از ده تا صد میلیارد چطور؟",                    "اما از ۱۰ تا ۱۰۰ میلیارد چطور؟"),                    # 22 -> Shot 15
    ("خونه‌ت بزرگ‌تر می‌شه و ماشینت لوکس‌تر؛",            "خونه‌ت بزرگ‌تر می‌شه و ماشینت لوکس‌تر؛"),            # 23 -> Shot 15
    ("ولی ده برابر خوشبخت‌ترت نمی‌کنه!",                  "ولی ۱۰ برابر خوشبخت‌ترت نمی‌کنه!"),                  # 24 -> Shot 16

    # Act IV — Regret Asymmetry & Golden Rule of Life Risk (25..34 -> Shots 17..24)
    ("توی دکمه‌ی دوم، تو هشتاد درصدِ آرامشت رو،",         "توی دکمه‌ی دوم، تو ۸۰٪ آرامشت رو،"),                 # 25 -> Shot 17
    ("سرِ بیست درصد تجملِ بیشتر قمار می‌کنی!",            "سر ۲۰٪ تجمل بیشتر قمار می‌کنی!"),                    # 26 -> Shot 17
    ("و اگه خط بیاد و دستِ خالی بمونی،",                  "و اگه «خط» بیاد و دست خالی بمونی،"),                 # 27 -> Shot 18
    ("حسرتش تا آخرِ عمر باهاته!",                         "حسرتش تا آخر عمر باهاته!"),                          # 28 -> Shot 18
    ("توی بازار و تصمیم‌های زندگیت هم،",                  "توی بازار و تصمیم‌های زندگیت هم،"),                  # 29 -> Shot 19
    ("قانونِ طلاییِ ریسک همینه:",                         "قانون طلایی ریسک همینه:"),                           # 30 -> Shot 20
    ("چیزی که نیاز داری رو،",                             "چیزی که نیاز داری رو،"),                             # 31 -> Shot 21
    ("پای چیزی که لازم نداری قمار نکن!",                 "پای چیزی که لازم نداری قمار نکن!"),                  # 32 -> Shot 21
    ("با وضعِ الانِ زندگیت کدوم رو می‌زنی؟",              "با وضع الان زندگیت کدوم رو می‌زنی؟"),                # 33 -> Shot 22
    ("دکمه‌ی یک یا دو؟ تو کامنت بنویس!",                  "دکمه‌ی ۱ یا ۲؟ تو کامنت بنویس!"),                    # 34 -> Shot 23
]

# 45 Clean, Tactile Luxury Foley & Cut Cues (5-tuple: cue_name, seg_idx, word_idx, sfx_kind, t_offset)
SFX_CUE_MAP = [
    ("c01_console",  0,  0, "screen_on",     0.05),
    ("c02_pov",      1,  0, "whoosh",       -0.05),
    ("_c02_hum",     1,  2, "ping",          0.02),
    ("c03_btn1",     2,  0, "whip",         -0.05),
    ("_c03_press",   2,  2, "button_press",  0.00),
    ("c03_10b",      3,  2, "cash_slam",    -0.02),
    ("c04_btn2",     4,  0, "whip",         -0.05),
    ("_c04_press",   4,  2, "button_press",  0.00),
    ("c04_coin",     5,  1, "coin_flip",    -0.02),
    ("c05_split",    6,  1, "impact_boom",  -0.03),
    ("c05_zero",     7,  1, "crumble",       0.00),
    ("c06_eye",      8,  0, "whoosh",       -0.05),
    ("_c06_scan",    8,  2, "scan",          0.02),

    ("c07_calc",     9,  0, "whip",         -0.05),
    ("_c07_keys",    9,  2, "typing",        0.00),
    ("c07_ans",     10,  2, "stamp",         0.00),
    ("c08_scale",   11,  0, "whoosh",       -0.05),
    ("c08_50b",     12,  0, "scale_tip",    -0.02),
    ("c09_smart",   13,  0, "whip",         -0.05),
    ("_c09_slash",  14,  2, "slash",         0.00),
    ("c10_heart",   15,  0, "whoosh",       -0.05),
    ("_c10_hb",     15,  2, "heartbeat",     0.02),

    ("c11_curve",   17,  0, "whip",         -0.05),
    ("_c11_rise",   18,  0, "riser",        -0.25),
    ("c11_peak",    18,  2, "ping",          0.00),
    ("c12_chains",  19,  0, "shatter",       0.02),
    ("c13_door",    20,  0, "whoosh",       -0.05),
    ("_c13_bell",   20,  3, "bell_ding",     0.00),
    ("c14_80pct",   21,  1, "impact_boom",  -0.03),
    ("c15_lux",     22,  0, "whip",         -0.05),
    ("_c15_tick",   23,  2, "click",         0.02),
    ("c16_pillars", 24,  1, "scale_tip",     0.00),

    ("c17_cliff",   25,  0, "whip",         -0.05),
    ("_c17_crack",  26,  2, "crumble",       0.02),
    ("c18_regret",  27,  0, "whoosh",       -0.05),
    ("_c18_drop",   27,  2, "stamp",         0.02),
    ("_c18_hb",     28,  1, "heartbeat",     0.04),
    ("c19_market",  29,  0, "whip",         -0.05),
    ("_c19_scan",   29,  2, "scan",          0.02),
    ("c20_rule",    30,  0, "screen_on",    -0.02),
    ("c21_bridge",  31,  0, "whoosh",       -0.05),
    ("c21_free",    32,  3, "shatter",       0.00),
    ("c22_return",  33,  0, "whip",         -0.05),
    ("c23_cta",     34,  0, "button_press",  0.00),
    ("_c23_p2",     34,  2, "ping",          0.05),
]


# =============================================================================
# BESPOKE EPISODE 06 PURE B&W @ENSAN.BESHAM VECTOR ACTORS & PROPS
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


def draw_two_button_console(
    cs, cg, cx: float, floor_y: float, scale: float = 1.0,
    active_btn: int = 0, press_p: float = 0.0, t: float = 0.0, alpha: float = 1.0, draw_p: float = 1.0
):
    """
    Sleek waist-high @ensan.besham futuristic pedestal console holding two glowing dome buttons:
    Right = Button 1 (solid guaranteed aura), Left = Button 2 (dashed 50/50 gamble aura).
    """
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    top_y = floor_y - 168 * scale
    b1_x = cx + 68 * scale   # Right button (Button 1)
    b2_x = cx - 68 * scale   # Left button (Button 2)

    # Soft upward light cones from the two glowing buttons!
    for bx, is_act in ((b1_x, active_btn in (0, 1)), (b2_x, active_btn in (0, 2))):
        cone_al = alpha * draw_p * (0.14 if is_act else 0.05)
        grad = cairo.LinearGradient(bx, top_y, bx, top_y - 230 * scale)
        grad.add_color_stop_rgba(0.0, 1, 1, 1, cone_al)
        grad.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)
        cs.save()
        cs.move_to(bx - 26 * scale, top_y - 8 * scale)
        cs.line_to(bx + 26 * scale, top_y - 8 * scale)
        cs.line_to(bx + 88 * scale, top_y - 230 * scale)
        cs.line_to(bx - 88 * scale, top_y - 230 * scale)
        cs.close_path()
        cs.set_source(grad)
        cs.fill()
        cs.restore()

    for ctx, lw, al in ((cs, 2.7, alpha * 0.94), (cg, 5.8, alpha * 0.40)):
        ctx.save()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        # Slanted tabletop & central pedestal column
        rounded_rect_path(ctx, cx - 135 * scale, top_y, 270 * scale, 26 * scale, 9 * scale)
        if ctx is cs:
            ctx.set_source_rgba(0.04, 0.04, 0.055, 0.95 * alpha)
            ctx.fill_preserve()
        set_stroke_draw(ctx, draw_p, 640 * scale)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()

        # Central column & base plate
        ctx.set_dash([])
        ctx.move_to(cx - 36 * scale, top_y + 26 * scale)
        ctx.line_to(cx - 48 * scale, floor_y)
        ctx.move_to(cx + 36 * scale, top_y + 26 * scale)
        ctx.line_to(cx + 48 * scale, floor_y)
        ctx.set_source_rgba(1, 1, 1, al * 0.78)
        ctx.set_line_width(lw * 0.88)
        ctx.stroke()

        # Button 1 dome (Right — Solid Crisp Dome)
        d1 = (7.0 * scale * press_p) if active_btn == 1 else 0.0
        rounded_rect_path(ctx, b1_x - 36 * scale, top_y - 22 * scale + d1, 72 * scale, 22 * scale - d1 * 0.6, 10 * scale)
        if ctx is cs and active_btn in (0, 1):
            ctx.set_source_rgba(1, 1, 1, (0.28 if active_btn == 1 else 0.12) * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al * (1.0 if active_btn in (0, 1) else 0.45))
        ctx.set_line_width(lw)
        ctx.stroke()

        # Button 2 dome (Left — Gamble Dome)
        d2 = (7.0 * scale * press_p) if active_btn == 2 else 0.0
        rounded_rect_path(ctx, b2_x - 36 * scale, top_y - 22 * scale + d2, 72 * scale, 22 * scale - d2 * 0.6, 10 * scale)
        if ctx is cs and active_btn == 2:
            ctx.set_source_rgba(1, 1, 1, 0.26 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al * (1.0 if active_btn in (0, 2) else 0.45))
        ctx.set_line_width(lw)
        ctx.stroke()
        ctx.restore()


def draw_character_at_console(
    cs, cg, char_x: float, floor_y: float, scale: float = 1.65,
    reach_mode: int = 0, reach_p: float = 0.0, t: float = 0.0, alpha: float = 1.0
):
    """
    Expressive human character standing beside the two-button console:
    reach_mode=0 -> hand poised thoughtfully in air; reach_mode=1 -> pressing right button; reach_mode=2 -> pressing left!
    """
    if alpha <= 0.01:
        return
    breathe = math.sin(t * 2.2) * 2.2
    head_y = floor_y - 148 * scale + breathe
    sh_y   = floor_y - 116 * scale + breathe
    hip_y  = floor_y - 58 * scale + breathe

    for ctx, lw, al in ((cs, 2.8, alpha * 0.96), (cg, 6.0, alpha * 0.40)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)

        # Head slightly angled toward console
        ctx.arc(char_x - 4 * scale, head_y, 19.5 * scale, 0, 2 * math.pi)
        ctx.stroke()

        # Torso
        rounded_rect_path(ctx, char_x - 24 * scale, sh_y, 48 * scale, 58 * scale, 14 * scale)
        if ctx is cs:
            ctx.set_source_rgba(0.03, 0.03, 0.045, 0.92 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.stroke()

        # Legs planted firmly on floor
        ctx.move_to(char_x - 12 * scale, hip_y)
        ctx.line_to(char_x - 14 * scale, floor_y)
        ctx.move_to(char_x + 12 * scale, hip_y)
        ctx.line_to(char_x + 14 * scale, floor_y)
        ctx.stroke()

        # Back arm relaxed at side
        ctx.move_to(char_x + 24 * scale, sh_y + 10 * scale)
        ctx.line_to(char_x + 32 * scale, sh_y + 52 * scale)
        ctx.stroke()

        # Front acting arm reaching over toward the console buttons!
        sx, sy = char_x - 24 * scale, sh_y + 10 * scale
        if reach_mode == 0:
            ex, ey = char_x - 52 * scale, sh_y + 24 * scale
            hx, hy = char_x - 86 * scale, sh_y + (6 - 12 * reach_p) * scale
        elif reach_mode == 1:
            ex, ey = char_x - 56 * scale, sh_y + 18 * scale
            hx, hy = char_x - 98 * scale, sh_y + (8 + 18 * reach_p) * scale
        else:
            ex, ey = char_x - 68 * scale, sh_y + 14 * scale
            hx, hy = char_x - 128 * scale, sh_y + (8 + 18 * reach_p) * scale
        ctx.move_to(sx, sy)
        ctx.line_to(ex, ey)
        ctx.line_to(hx, hy)
        ctx.stroke()
        ctx.restore()


def draw_pov_hand_and_two_buttons(
    cs, cg, fonts: FontBank, stx: list,
    target_btn: int = 0, press_p: float = 0.0, t: float = 0.0, alpha: float = 1.0, draw_p: float = 1.0
):
    """
    Signature First-Person POV Shot:
    Two large glowing circular glass buttons side-by-side (Right = Button 1, Left = Button 2),
    with an anatomical human hand + extended index finger hovering or pressing down!
    """
    if alpha <= 0.01:
        return
    b1_x, b1_y = 735.0, 770.0   # Right: Button 1 (10B Certain)
    b2_x, b2_y = 345.0, 770.0   # Left:  Button 2 (100B Coin Toss)
    r_outer = 132.0

    for idx_b, (bx, by, is_b1) in enumerate(((b1_x, b1_y, True), (b2_x, b2_y, False))):
        b_num = 1 if is_b1 else 2
        is_pressed = (target_btn == b_num)
        dep = press_p if is_pressed else 0.0
        rad_cur = r_outer * (1.0 - 0.055 * dep)
        dim_f = 1.0 if (target_btn in (0, b_num)) else 0.36

        if target_btn in (0, b_num):
            rg = cairo.RadialGradient(bx, by, 10.0, bx, by, rad_cur * 1.45)
            rg.add_color_stop_rgba(0.0, 1, 1, 1, (0.22 + 0.16 * dep) * alpha)
            rg.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)
            cs.save()
            cs.arc(bx, by, rad_cur * 1.45, 0, 2 * math.pi)
            cs.set_source(rg)
            cs.fill()
            cs.restore()

        for ctx, lw, al in ((cs, 3.0, alpha * 0.96 * dim_f), (cg, 6.8, alpha * 0.44 * dim_f)):
            ctx.save()
            ctx.arc(bx, by, rad_cur, 0, 2 * math.pi)
            if ctx is cs:
                ctx.set_source_rgba(0.035, 0.035, 0.05, 0.94 * alpha)
                ctx.fill_preserve()
            set_stroke_draw(ctx, draw_p, 2 * math.pi * rad_cur)
            ctx.set_source_rgba(1, 1, 1, al)
            ctx.set_line_width(lw)
            ctx.stroke()

            ctx.save()
            ctx.translate(bx, by)
            if not is_b1:
                ctx.rotate(t * 0.75)
                ctx.set_dash([14.0, 10.0])
            else:
                ctx.set_dash([])
            ctx.arc(0, 0, rad_cur * 0.76, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, al * 0.75)
            ctx.set_line_width(lw * 0.72)
            ctx.stroke()
            ctx.restore()
            ctx.restore()

        lbl_num = "۱" if is_b1 else "۲"
        sub_lbl = "۱۰ میلیاردِ قطعی" if is_b1 else "شیریاخطِ ۱۰۰ میلیارد"
        sp_n = get_text_sprite(lbl_num, fonts.eb_68, (255, 255, 255, 255), glow=0.75 if is_pressed else 0.35)
        sp_s = get_fitted_text_sprite(sub_lbl, fonts.bold_30, 290, (230, 230, 242, 255))
        stx.append((sp_n, bx, by, alpha * dim_f))
        # Place button caption cleanly ABOVE the button ring so the bottom-entering POV hand never overlaps text!
        if target_btn == 0:
            stx.append((sp_s, bx, by - 176, alpha * dim_f))

    # First-Person POV Right Hand + Extended Index Finger hovering or pressing!
    hover_x = 540.0 + math.sin(t * 2.1) * 26.0
    hover_y = 955.0 + math.cos(t * 3.0) * 8.0
    if target_btn == 1:
        tip_x = hover_x + (b1_x - hover_x) * ease_out_cubic(clamp(press_p * 1.4))
        tip_y = hover_y + (b1_y + 28.0 - hover_y) * ease_out_cubic(press_p)
    elif target_btn == 2:
        tip_x = hover_x + (b2_x - hover_x) * ease_out_cubic(clamp(press_p * 1.4))
        tip_y = hover_y + (b2_y + 28.0 - hover_y) * ease_out_cubic(press_p)
    else:
        tip_x, tip_y = hover_x, hover_y

    for ctx, lw, al in ((cs, 3.0, alpha * 0.96), (cg, 6.2, alpha * 0.42)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.new_path()
        ctx.move_to(tip_x - 52, tip_y + 390)
        ctx.curve_to(tip_x - 68, tip_y + 255, tip_x - 82, tip_y + 165, tip_x - 48, tip_y + 115)
        ctx.curve_to(tip_x - 32, tip_y + 98, tip_x - 20, tip_y + 112, tip_x - 18, tip_y + 92)
        ctx.line_to(tip_x - 16, tip_y + 18)
        ctx.curve_to(tip_x - 15, tip_y - 6, tip_x + 15, tip_y - 6, tip_x + 16, tip_y + 18)
        ctx.line_to(tip_x + 18, tip_y + 98)
        ctx.curve_to(tip_x + 34, tip_y + 88, tip_x + 48, tip_y + 98, tip_x + 48, tip_y + 118)
        ctx.curve_to(tip_x + 64, tip_y + 108, tip_x + 76, tip_y + 118, tip_x + 76, tip_y + 138)
        ctx.curve_to(tip_x + 90, tip_y + 130, tip_x + 100, tip_y + 144, tip_x + 98, tip_y + 168)
        ctx.curve_to(tip_x + 96, tip_y + 250, tip_x + 78, tip_y + 325, tip_x + 66, tip_y + 390)
        if ctx is cs:
            ctx.set_source_rgba(0.025, 0.025, 0.038, 0.96 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()
        ctx.arc(tip_x, tip_y + 12, 8.5, math.pi * 1.1, math.pi * 1.9)
        ctx.set_line_width(lw * 0.65)
        ctx.stroke()
        ctx.restore()


def draw_spinning_coin_3d(cs, cg, cx: float, cy: float, r: float, phase: float, alpha: float = 1.0):
    """True 60fps 3D foreshortened metallic silver coin flipping in mid-air!"""
    if alpha <= 0.01:
        return
    c_cos = math.cos(phase)
    rx = max(7.0, r * abs(c_cos))
    rim = 13.0 * math.sin(phase)

    for ctx, lw, al in ((cs, 2.8, alpha * 0.96), (cg, 6.2, alpha * 0.45)):
        ctx.save()
        ctx.set_dash([])
        ctx.save()
        ctx.translate(cx + rim, cy)
        ctx.scale(rx / r, 1.0)
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(1, 1, 1, al * 0.45)
        ctx.set_line_width(lw * 0.78)
        ctx.stroke()

        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(rx / r, 1.0)
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.restore()
        if ctx is cs:
            ctx.set_source_rgba(0.05, 0.05, 0.07, 0.94 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()

        if rx > 22.0:
            ctx.save()
            ctx.translate(cx, cy)
            ctx.scale((rx * 0.78) / r, 0.78)
            ctx.set_dash([7.0, 6.0])
            ctx.arc(0, 0, r, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(1, 1, 1, al * 0.65)
            ctx.set_line_width(lw * 0.65)
            ctx.stroke()
        ctx.restore()

    glint = max(0.0, 1.0 - abs(c_cos) * 2.5)
    if glint > 0.05:
        draw_star4(cs, cx, cy - r * 0.68, 22.0 * glint, alpha * glint)
        draw_star4(cg, cx, cy - r * 0.68, 34.0 * glint, alpha * glint * 0.6)


def draw_precision_scale(cs, cg, cx: float, base_y: float, span_w: float, tilt_rad: float, alpha: float = 1.0):
    """Architectural @ensan.besham balance scale tipping between Paper EV (left) and Certainty (right)."""
    if alpha <= 0.01:
        return
    piv_y = base_y - 310.0
    lx = cx - span_w * 0.5 * math.cos(tilt_rad)
    ly = piv_y - span_w * 0.5 * math.sin(tilt_rad)
    rx = cx + span_w * 0.5 * math.cos(tilt_rad)
    ry = piv_y + span_w * 0.5 * math.sin(tilt_rad)

    for ctx, lw, al in ((cs, 2.7, alpha * 0.94), (cg, 5.8, alpha * 0.40)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        rounded_rect_path(ctx, cx - 95, base_y - 18, 190, 18, 8)
        ctx.stroke()
        ctx.move_to(cx, base_y - 18)
        ctx.line_to(cx, piv_y)
        ctx.stroke()
        ctx.arc(cx, piv_y, 16, 0, 2 * math.pi)
        if ctx is cs:
            ctx.set_source_rgba(0.04, 0.04, 0.06, 0.95 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.stroke()
        ctx.move_to(lx, ly)
        ctx.line_to(rx, ry)
        ctx.set_line_width(lw * 1.15)
        ctx.stroke()
        for px, py in ((lx, ly), (rx, ry)):
            ctx.set_line_width(lw * 0.72)
            ctx.move_to(px, py); ctx.line_to(px - 62, py + 98)
            ctx.move_to(px, py); ctx.line_to(px + 62, py + 98)
            ctx.stroke()
            ctx.set_line_width(lw)
            ctx.move_to(px - 78, py + 98)
            ctx.curve_to(px - 42, py + 122, px + 42, py + 122, px + 78, py + 98)
            ctx.stroke()
        ctx.restore()


def draw_slumped_regret_figure(cs, cg, cx: float, floor_y: float, scale: float, t: float, alpha: float = 1.0):
    """3 AM dark room: character sitting slumped on the floor holding their lowered head in regret."""
    if alpha <= 0.01:
        return
    shiver = math.sin(t * 7.5) * 1.2
    for ctx, lw, al in ((cs, 2.9, alpha * 0.95), (cg, 6.0, alpha * 0.40)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.move_to(cx - 210, floor_y); ctx.line_to(cx + 210, floor_y); ctx.stroke()
        hip_x, hip_y = cx - 22 * scale + shiver, floor_y - 10 * scale
        sh_x, sh_y   = cx + 6 * scale + shiver,  floor_y - 72 * scale
        hd_x, hd_y   = cx + 28 * scale + shiver, floor_y - 78 * scale
        kn_x, kn_y   = cx + 42 * scale,          floor_y - 52 * scale
        ft_x, ft_y   = cx + 68 * scale,          floor_y - 4 * scale
        ctx.move_to(hip_x, hip_y)
        ctx.curve_to(hip_x - 8 * scale, floor_y - 46 * scale, sh_x - 10 * scale, sh_y + 12 * scale, sh_x, sh_y)
        ctx.stroke()
        ctx.move_to(hip_x, hip_y); ctx.line_to(kn_x, kn_y); ctx.line_to(ft_x, ft_y); ctx.stroke()
        ctx.arc(hd_x, hd_y, 17 * scale, 0, 2 * math.pi)
        if ctx is cs:
            ctx.set_source_rgba(0.03, 0.03, 0.04, 0.94 * alpha); ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al); ctx.stroke()
        ctx.move_to(sh_x, sh_y + 8 * scale)
        ctx.line_to(kn_x - 4 * scale, kn_y - 4 * scale)
        ctx.line_to(hd_x + 4 * scale, hd_y + 6 * scale)
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
        tc["c02_pov"],
        tc["c03_btn1"],
        tc["c04_btn2"],
        tc["c05_split"] - 0.08,
        tc["c06_eye"],
        tc["c07_calc"],
        tc["c08_scale"],
        tc["c09_smart"],
        tc["c10_heart"],
        tc["c11_curve"],
        tc["c12_chains"] - 0.08,
        tc["c13_door"],
        tc["c14_80pct"] - 0.08,
        tc["c15_lux"],
        tc["c16_pillars"] - 0.08,
        tc["c17_cliff"],
        tc["c18_regret"],
        tc["c19_market"],
        tc["c20_rule"],
        tc["c21_bridge"],
        tc["c22_return"],
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

    chapters = [0.0, b05, b07, b11, b15, b17, b22]
    draw_hud_chrome(cs, cg, txts, fonts, t, total_dur, EP_CODE, EP_TITLE, chapters)
    draw_ambient_particles(cs, t, alpha=0.82 * clamp((outro_t0 - t) / 0.8))

    # =========================================================================
    # SHOT 01 (b01..b02): Character in dark room facing the glowing 2-button console!
    # =========================================================================
    w = _shot_win(t, b01, b02)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b01, b02, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=900)
        p_in = ease_out_cubic(clamp((t - b01) / 0.65))
        draw_glow_line(cs, cg, 160, 1130, 920, 1130, w * 0.45)
        draw_two_button_console(cs, cg, 430, 1130, scale=1.22, active_btn=0, t=t, alpha=w, draw_p=p_in)
        draw_character_at_console(cs, cg, 695, 1130, scale=1.82, reach_mode=0, reach_p=0.5 + 0.5*math.sin(t*2.4), t=t, alpha=w)
        sp_lbl = get_fitted_text_sprite("تو — جلوی دو انتخاب", fonts.light_22, 340, (175, 175, 192, 255))
        stx.append((sp_lbl, 695, 1175, w * 0.85))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=900)

    # =========================================================================
    # SHOT 02 (b02..b03): First-Person POV Hand hovering between Button 1 & 2!
    # =========================================================================
    w = _shot_win(t, b02, b03)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b02, b03, base_in=0.92)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        p_in = ease_out_cubic(clamp((t - b02) / 0.45))
        sp_top = get_fitted_text_sprite("کدوم دکمه رو فشار می‌دی؟", fonts.bold_44, 820, (255, 255, 255, 255), glow=0.65)
        stx.append((sp_top, 540, 390, w))
        draw_pov_hand_and_two_buttons(cs, cg, fonts, stx, target_btn=0, press_p=0.0, t=t, alpha=w, draw_p=p_in)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 03 (b03..b04): POV Finger presses Button 1 -> 10,000,000,000 Toman!
    # =========================================================================
    w = _shot_win(t, b03, b04)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b03, b04, base_in=0.93) + impact_punch(t, tc["c03_10b"], 0.045, 0.42)
        push_camera(cs, cg, zoom=cz, px=620, py=780)
        pp = ease_out_cubic(clamp((t - (b03 + 0.12)) / 0.35))
        draw_pov_hand_and_two_buttons(cs, cg, fonts, stx, target_btn=1, press_p=pp, t=t, alpha=w, draw_p=1.0)
        draw_shockwave_ring(cs, cg, 735, 770, clamp((t - tc["_c03_press"]) / 0.65), max_r=260, alpha=w * 0.85)

        p10 = ease_out_cubic(clamp((t - (tc["c03_10b"] - 0.15)) / 0.40))
        if p10 > 0.02:
            sp_big = get_fitted_text_sprite("۱۰,۰۰۰,۰۰۰,۰۰۰", fonts.eb_84, 880, (255, 255, 255, 255), glow=0.95)
            sp_sub = get_fitted_text_sprite("تومانِ نقد و ۱۰۰٪ قطعی!", fonts.bold_36, 760, (235, 235, 248, 255), glow=0.5)
            stx.append((sp_big, 540, 385, w * p10))
            stx.append((sp_sub, 540, 488, w * p10))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=620, py=780)

    # =========================================================================
    # SHOT 04 (b04..b05): POV Finger taps Button 2 -> 3D Spinning Silver Coin!
    # =========================================================================
    w = _shot_win(t, b04, b05)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b04, b05, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=480, py=760)
        pp = ease_out_cubic(clamp((t - (b04 + 0.10)) / 0.32))
        coin_p = ease_out_cubic(clamp((t - (tc["c04_coin"] - 0.25)) / 0.55))

        draw_pov_hand_and_two_buttons(cs, cg, fonts, stx, target_btn=2, press_p=pp, t=t, alpha=w * (1.0 - 0.55 * coin_p), draw_p=1.0)
        if coin_p > 0.02:
            cy_coin = 740.0 - 210.0 * coin_p
            draw_spinning_coin_3d(cs, cg, 540, cy_coin, 108.0, (t - b04) * 9.5, alpha=w * coin_p)
            sp_50 = get_fitted_text_sprite("شیر یا خطِ ۵۰٪ — ۵۰٪", fonts.eb_68, 860, (255, 255, 255, 255), glow=0.85)
            stx.append((sp_50, 540, 345, w * coin_p))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=480, py=760)

    # =========================================================================
    # SHOT 05 (b05..b06): Split Destiny Cut — 100B Tower vs 0 Toman Cracked Floor!
    # =========================================================================
    w = _shot_win(t, b05, b06)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b05, b06, base_in=0.94) + impact_punch(t, b05 + 0.06, 0.04, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        draw_glow_line(cs, cg, 540, 370, 540, 1340, w * 0.45, dashed=True)

        win_p = ease_out_cubic(clamp((t - b05) / 0.45))
        for ctx, lw, al in ((cs, 2.8, w * 0.96), (cg, 6.0, w * 0.44)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 685, 880, 210, 380 * win_p, 12)
            if ctx is cs:
                ctx.set_source_rgba(0.05, 0.05, 0.07, 0.94 * w); ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()
        draw_character_with_phone(cs, cg, 790, 880, scale=1.35, raise_p=1.0, screen_glow=1.0, alpha=w * win_p, t=t)
        sp_w1 = get_fitted_text_sprite("شیر: ۱۰۰ میلیارد!", fonts.bold_44, 410, (255, 255, 255, 255), glow=0.85)
        sp_w2 = get_fitted_text_sprite("برنده‌ی ۵۰٪", fonts.reg_26, 380, (205, 205, 220, 255))
        stx.append((sp_w1, 790, 445, w * win_p))
        stx.append((sp_w2, 790, 520, w * win_p))

        lose_p = ease_out_cubic(clamp((t - (tc["c05_zero"] - 0.15)) / 0.45))
        if lose_p > 0.02:
            draw_glow_line(cs, cg, 145, 1260, 435, 1260, w * lose_p * 0.65)
            draw_glow_line(cs, cg, 290, 1260, 265, 1315, w * lose_p * 0.7, lw_s=2.0)
            draw_glow_line(cs, cg, 290, 1260, 322, 1308, w * lose_p * 0.7, lw_s=2.0)
            draw_human_figure(cs, 290, 1260, scale=1.42, alpha=w * lose_p * 0.85, lw=2.6)
            sp_l1 = get_fitted_text_sprite("خط: ۰ تومان!", fonts.bold_44, 410, (215, 215, 228, 255))
            sp_l2 = get_fitted_text_sprite("دستِ خالی (پوچ!)", fonts.reg_26, 380, (175, 175, 192, 255))
            stx.append((sp_l1, 290, 445, w * lose_p))
            stx.append((sp_l2, 290, 520, w * lose_p))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 06 (b06..b07): Overhead AI Observatory Eye scanning the lone choice!
    # =========================================================================
    w = _shot_win(t, b06, b07)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b06, b07, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=820)
        draw_observatory_eye(cs, cg, 540, 360, 56.0, t, alpha=w, scan_targets=[(365, 1005), (525, 1005), (675, 965)])
        draw_two_button_console(cs, cg, 445, 1185, scale=1.08, active_btn=0, t=t, alpha=w)
        draw_character_at_console(cs, cg, 675, 1185, scale=1.62, reach_mode=0, reach_p=0.4, t=t, alpha=w)
        sp_one = get_fitted_text_sprite("فقط ۱ بار در کلِ عمر!", fonts.eb_68, 860, (255, 255, 255, 255), glow=0.8)
        stx.append((sp_one, 540, 625, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=820)

    # =========================================================================
    # SHOT 07 (b07..b08): Cold Calculator Equation -> 50% x 100B = 50B!
    # =========================================================================
    w = _shot_win(t, b07, b08)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b07, b08, base_in=0.92) + impact_punch(t, tc["c07_ans"], 0.038, 0.38)
        push_camera(cs, cg, zoom=cz, px=540, py=840)
        p_c = ease_out_cubic(clamp((t - b07) / 0.45))

        for ctx, lw, al in ((cs, 2.8, w * 0.95), (cg, 6.2, w * 0.42)):
            ctx.save()
            rounded_rect_path(ctx, 210, 430, 660, 740, 32)
            if ctx is cs:
                ctx.set_source_rgba(0.03, 0.03, 0.045, 0.94 * w); ctx.fill_preserve()
            set_stroke_draw(ctx, p_c, 2800)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.set_dash([])
            rounded_rect_path(ctx, 255, 480, 570, 260, 18)
            ctx.set_line_width(lw * 0.8); ctx.stroke()
            for kr in range(2):
                for kc in range(3):
                    kx = 265 + kc * 188
                    ky = 790 + kr * 165
                    is_eq = (kr == 1 and kc == 2)
                    rounded_rect_path(ctx, kx, ky, 154, 130, 14)
                    if ctx is cs and is_eq:
                        ctx.set_source_rgba(1, 1, 1, 0.22 * w); ctx.fill_preserve()
                    ctx.set_source_rgba(1, 1, 1, al * (0.95 if is_eq else 0.45))
                    ctx.stroke()
            ctx.restore()

        sp_m1 = get_fitted_text_sprite("۵۰٪ × ۱۰۰ میلیارد", fonts.bold_36, 520, (210, 210, 225, 255))
        sp_m2 = get_fitted_text_sprite("= ۵۰ میلیارد!", fonts.eb_68, 520, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_m1, 540, 548, w))
        stx.append((sp_m2, 540, 650, w))

        ans_p = ease_out_cubic(clamp((t - (tc["c07_ans"] - 0.12)) / 0.35))
        if ans_p > 0.02:
            draw_safe_card(cs, cg, stx, 540, 1285, 780, 102, [("حکمِ ماشین‌حساب: حتماً دکمه‌ی ۲ رو بزن!", fonts.bold_30, 0, (255, 255, 255, 255), 0.5)], alpha=w * ans_p, glow_border=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=840)

    # =========================================================================
    # SHOT 08 (b08..b09): Precision Balance Scale tipping 5x toward 50 Billion!
    # =========================================================================
    w = _shot_win(t, b08, b09)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b08, b09, base_in=0.93) + impact_punch(t, tc["c08_50b"], 0.038, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        tip_p = ease_out_cubic(clamp((t - (b08 + 0.15)) / 0.55))
        tilt = -0.24 * tip_p
        draw_precision_scale(cs, cg, 540, 1235, 580, tilt, alpha=w)

        piv_y = 1235 - 310.0
        lx = 540 - 290 * math.cos(tilt)
        ly = piv_y - 290 * math.sin(tilt)
        rx = 540 + 290 * math.cos(tilt)
        ry = piv_y + 290 * math.sin(tilt)

        sp_50b = get_fitted_text_sprite("۵۰ میلیارد", fonts.bold_44, 300, (255, 255, 255, 255), glow=0.8)
        sp_10b = get_fitted_text_sprite("۱۰ میلیارد", fonts.bold_36, 280, (195, 195, 210, 255))
        sp_top = get_fitted_text_sprite("روی کاغذ: ۵ برابر باارزش‌تر!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_top, 540, 425, w))
        stx.append((sp_50b, lx, ly + 152, w))
        stx.append((sp_10b, rx, ry + 152, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 09 (b09..b10): 85% of Smart People Slash the Paper Formula & Pick 10B!
    # =========================================================================
    w = _shot_win(t, b09, b10)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b09, b10, base_in=0.93) + impact_punch(t, tc["_c09_slash"], 0.04, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=850)

        sp_85 = get_fitted_text_sprite("۸۵٪ آدمای باهوش", fonts.eb_84, 880, (255, 255, 255, 255), glow=0.90)
        sp_ch = get_fitted_text_sprite("بازم دکمه‌ی ۱۰ میلیارد رو می‌زنن!", fonts.bold_36, 840, (235, 235, 248, 255))
        stx.append((sp_85, 540, 420, w))
        stx.append((sp_ch, 540, 535, w))

        for ctx, lw, al in ((cs, 2.6, w * 0.92), (cg, 5.6, w * 0.38)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 250, 1085, 580, 165, 16)
            if ctx is cs:
                ctx.set_source_rgba(0.04, 0.04, 0.06, 0.94 * w); ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

        for fi, fx in enumerate((330, 435, 540, 645, 750)):
            if fi == 2:
                draw_character_with_phone(cs, cg, fx, 1085, scale=1.42, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)
            else:
                draw_human_figure(cs, fx, 1085, scale=1.28, alpha=w * 0.86, lw=2.5)

        sp_p1 = get_fitted_text_sprite("انتخابِ واقعی: دکمه‌ی ۱ (۱۰ میلیاردِ قطعی)", fonts.bold_30, 530, (255, 255, 255, 255), glow=0.55)
        stx.append((sp_p1, 540, 1168, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=850)

    # =========================================================================
    # SHOT 10 (b10..b11): Life Is Not a Calculator — 1 Heartbeat, Not 1,000 Trials!
    # =========================================================================
    w = _shot_win(t, b10, b11)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b10, b11, base_in=0.94) + impact_punch(t, tc["_c10_hb"], 0.038, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        draw_human_figure(cs, 540, 1125, scale=3.5, alpha=w * 0.54, lw=2.1)
        draw_human_figure(cg, 540, 1125, scale=3.5, alpha=w * 0.22, lw=4.5)
        draw_hypnotic_chronograph_ring(cs, cg, 540, 855, 128.0, t, alpha=w * 0.92, draw_p=1.0, speed=1.6)
        draw_ecg_waveform(cs, cg, 150, 930, 1215, t, amp=46.0, alpha=w)

        sp_x1 = get_text_sprite("×۱", fonts.eb_68, (255, 255, 255, 255), glow=0.9)
        sp_h1 = get_fitted_text_sprite("زندگی ماشین‌حساب نیست!", fonts.bold_44, 840, (255, 255, 255, 255), glow=0.75)
        sp_h2 = get_fitted_text_sprite("فقط ۱ بار زندگی می‌کنی، نه ۱۰۰۰ بار!", fonts.reg_26, 800, (205, 205, 222, 255))
        stx.append((sp_x1, 540, 855, w))
        stx.append((sp_h1, 540, 355, w))
        stx.append((sp_h2, 540, 432, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 11 (b11..b12): Diminishing Utility Curve (0 -> 10B Rocket vs 10 -> 100B Flat)!
    # =========================================================================
    w = _shot_win(t, b11, b12)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b11, b12, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        cp = ease_out_cubic(clamp((t - b11) / 0.85))

        gx0, gy0, gw, gh = 175.0, 1140.0, 730.0, 490.0
        draw_glow_line(cs, cg, gx0, gy0, gx0 + gw, gy0, w * 0.72)
        draw_glow_line(cs, cg, gx0, gy0, gx0, gy0 - gh, w * 0.72)

        n_pts = max(3, int(60 * cp))
        for ctx, lw, al in ((cs, 3.6, w * 0.98), (cg, 8.0, w * 0.48)):
            ctx.save(); ctx.set_dash([])
            for k in range(n_pts):
                u = (k / 59.0) * cp
                px = gx0 + u * gw
                py = gy0 - (math.log(1.0 + 26.0 * u) / math.log(27.0)) * (gh * 0.90)
                if k == 0:
                    ctx.move_to(px, py)
                else:
                    ctx.line_to(px, py)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

        kx = gx0 + 0.22 * gw
        ky = gy0 - (math.log(1.0 + 26.0 * 0.22) / math.log(27.0)) * (gh * 0.90)
        if cp > 0.25:
            draw_glow_line(cs, cg, kx, gy0, kx, ky, w * 0.55, dashed=True)
            draw_character_with_phone(cs, cg, kx, ky, scale=1.08, raise_p=1.0, screen_glow=1.0, alpha=w, t=t)

        sp_t11 = get_fitted_text_sprite("منحنیِ واقعیِ پول و تغییرِ زندگی", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        sp_k10 = get_fitted_text_sprite("۱۰ میلیاردِ اول (+۸۰٪ جهش!)", fonts.bold_30, 420, (255, 255, 255, 255), glow=0.6)
        sp_x0  = get_text_sprite("۰", fonts.reg_26, (190, 190, 208, 255))
        sp_x10 = get_text_sprite("۱۰ میلیارد", fonts.bold_30, (255, 255, 255, 255))
        sp_x100 = get_text_sprite("۱۰۰ میلیارد", fonts.reg_26, (190, 190, 208, 255))
        stx.append((sp_t11, 540, 385, w))
        stx.append((sp_k10, 625, 560, w * clamp((cp - 0.25) * 2.5)))
        stx.append((sp_x0, gx0, gy0 + 42, w))
        stx.append((sp_x10, kx, gy0 + 42, w))
        stx.append((sp_x100, gx0 + gw - 35, gy0 + 42, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 12 (b12..b13): Heavy Debt & Rent Blocks Shattering off Character!
    # =========================================================================
    w = _shot_win(t, b12, b13)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b12, b13, base_in=0.93) + impact_punch(t, b12 + 0.08, 0.04, 0.40)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        brk = ease_out_cubic(clamp((t - b12) / 0.70))

        draw_glow_line(cs, cg, 220, 1185, 860, 1185, w * 0.5)
        draw_character_with_phone(cs, cg, 540, 1185, scale=1.95, raise_p=0.85, screen_glow=1.0, alpha=w, t=t)
        draw_shockwave_ring(cs, cg, 540, 940, clamp((t - b12) / 0.75), max_r=340, alpha=w * 0.85)

        for side, lbl_b in ((-1, "قسط و بدهی"), (1, "استرسِ اجاره")):
            bx = 540 + side * (175 + 120 * brk)
            by = 850 - 75 * brk
            rot = side * 0.38 * brk
            al_b = w * (1.0 - 0.35 * brk)
            for ctx, lw, al in ((cs, 2.5, al_b * 0.90), (cg, 5.5, al_b * 0.36)):
                ctx.save(); ctx.translate(bx, by); ctx.rotate(rot); ctx.set_dash([])
                rounded_rect_path(ctx, -108, -48, 216, 96, 14)
                if ctx is cs:
                    ctx.set_source_rgba(0.04, 0.04, 0.06, 0.92 * al_b); ctx.fill_preserve()
                ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
                ctx.restore()
            sp_b = get_fitted_text_sprite(lbl_b, fonts.bold_30, 185, (220, 220, 235, 255))
            stx.append((sp_b, bx, by, al_b))

        sp_h12 = get_fitted_text_sprite("پایانِ استرسِ شبانه‌ی قسط و اجاره!", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.8)
        stx.append((sp_h12, 540, 415, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 13 (b13..b14): Open Glowing Doorway — Power to Say "NO" & Start Fresh!
    # =========================================================================
    w = _shot_win(t, b13, b14)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b13, b14, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        dp = ease_out_cubic(clamp((t - b13) / 0.55))

        draw_spotlight_cone(cs, cg, 540, 560, 345, 735, 1210, alpha=w * 0.48 * dp)
        for ctx, lw, al in ((cs, 3.0, w * 0.96), (cg, 6.8, w * 0.45)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 410, 560, 260, 620, 22)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()
        draw_glow_line(cs, cg, 210, 1180, 870, 1180, w * 0.55)
        draw_character_with_phone(cs, cg, 540, 1180, scale=1.82, raise_p=0.90, screen_glow=1.0, alpha=w, t=t)

        sp_no = get_fitted_text_sprite("قدرتِ «نه گفتن» و آزادیِ انتخاب!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_no, 540, 395, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 14 (b14..b15): Giant 80% Real-Life Peace OLED Gauge + Character!
    # =========================================================================
    w = _shot_win(t, b14, b15)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b14, b15, base_in=0.92) + impact_punch(t, b14 + 0.08, 0.045, 0.42)
        push_camera(cs, cg, zoom=cz, px=540, py=840)
        fp = ease_out_cubic(clamp((t - b14) / 0.65))

        sp_80 = get_fitted_text_sprite("۸۰٪", fonts.eb_92, 600, (255, 255, 255, 255), glow=0.95)
        sp_80s = get_fitted_text_sprite("آرامشِ واقعیِ زندگی فقط با دکمه‌ی اول!", fonts.bold_36, 860, (235, 235, 248, 255))
        stx.append((sp_80, 540, 385, w))
        stx.append((sp_80s, 540, 495, w))

        gx, gy, gw_b, gh_b = 330, 620, 210, 520
        for ctx, lw, al in ((cs, 2.8, w * 0.95), (cg, 6.0, w * 0.42)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, gx, gy, gw_b, gh_b, 22)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            n_lit = int(round(8 * fp))
            for bi in range(10):
                by_seg = gy + gh_b - 22 - (bi + 1) * 47
                lit = (bi < n_lit)
                rounded_rect_path(ctx, gx + 20, by_seg, gw_b - 40, 34, 8)
                if ctx is cs and lit:
                    ctx.set_source_rgba(1, 1, 1, 0.86 * w); ctx.fill()
                elif not lit:
                    ctx.set_source_rgba(1, 1, 1, al * 0.22); ctx.set_line_width(1.6); ctx.stroke()
            ctx.restore()

        draw_character_with_phone(cs, cg, 695, 1140, scale=1.82, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=840)

    # =========================================================================
    # SHOT 15 (b15..b16): 10B -> 100B Luxury Upgrade (Bigger House/Car = Only +20%)!
    # =========================================================================
    w = _shot_win(t, b15, b16)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b15, b16, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)

        sp_h15 = get_fitted_text_sprite("از ۱۰ تا ۱۰۰ میلیارد چقدر فرق داره؟", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.7)
        stx.append((sp_h15, 540, 395, w))

        for ctx, lw, al in ((cs, 2.6, w * 0.92), (cg, 5.6, w * 0.38)):
            ctx.save(); ctx.set_dash([])
            ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            ctx.move_to(675, 795); ctx.line_to(755, 720); ctx.line_to(835, 795); ctx.stroke()
            rounded_rect_path(ctx, 695, 795, 120, 115, 8); ctx.stroke()
            ctx.move_to(175, 775); ctx.line_to(315, 665); ctx.line_to(455, 775); ctx.stroke()
            rounded_rect_path(ctx, 195, 775, 240, 135, 10); ctx.stroke()
            rounded_rect_path(ctx, 285, 825, 60, 85, 6); ctx.stroke()
            ctx.restore()

        sp_r1 = get_fitted_text_sprite("۱۰ میلیارد: خونه و آرامش", fonts.bold_30, 360, (215, 215, 230, 255))
        sp_l1 = get_fitted_text_sprite("۱۰۰ میلیارد: فقط لوکس‌تر (+۲۰٪)", fonts.bold_30, 410, (255, 255, 255, 255), glow=0.5)
        stx.append((sp_r1, 755, 975, w))
        stx.append((sp_l1, 315, 975, w))
        draw_safe_card(cs, cg, stx, 540, 1165, 780, 102, [("تجمل بیشتر می‌شه، ولی آرامش همونه!", fonts.bold_30, 0, (255, 255, 255, 255), 0.45)], alpha=w, glow_border=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 16 (b16..b17): 10x Money Pillar vs 1.2x Happiness Pillar Comparison!
    # =========================================================================
    w = _shot_win(t, b16, b17)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b16, b17, base_in=0.93) + impact_punch(t, b16 + 0.08, 0.04, 0.38)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        pp = ease_out_cubic(clamp((t - b16) / 0.55))

        sp_h16 = get_fitted_text_sprite("۱۰ برابر پول ≠ ۱۰ برابر خوشبختی!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_h16, 540, 390, w))

        draw_glow_line(cs, cg, 170, 1225, 910, 1225, w * 0.55)
        h_money = 510 * pp
        h_happy = 135 * pp
        for ctx, lw, al in ((cs, 2.8, w * 0.95), (cg, 6.0, w * 0.42)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 645, 1225 - h_money, 200, h_money, 14)
            ctx.set_source_rgba(1, 1, 1, al * 0.85); ctx.set_line_width(lw); ctx.stroke()
            rounded_rect_path(ctx, 235, 1225 - h_happy, 200, h_happy, 14)
            if ctx is cs:
                ctx.set_source_rgba(1, 1, 1, 0.16 * w); ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al); ctx.stroke()
            ctx.restore()

        draw_character_with_phone(cs, cg, 335, 1225 - h_happy, scale=1.55, raise_p=0.85, screen_glow=0.95, alpha=w, t=t)
        sp_c1 = get_fitted_text_sprite("۱۰ برابر پول", fonts.bold_30, 260, (215, 215, 230, 255))
        sp_c2 = get_fitted_text_sprite("فقط ۱.۲ برابر حالِ خوب!", fonts.bold_30, 320, (255, 255, 255, 255), glow=0.6)
        stx.append((sp_c1, 745, 1278, w))
        stx.append((sp_c2, 335, 1278, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 17 (b17..b18): Cliff-Edge Gamble — Risking 80% Peace for +20% Luxury!
    # =========================================================================
    w = _shot_win(t, b17, b18)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b17, b18, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        lean = 0.16 + 0.05 * math.sin(t * 4.5)

        sp_h17 = get_fitted_text_sprite("قمارِ ۸۰٪ آرامش، سرِ ۲۰٪ تجمل!", fonts.eb_68, 880, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_h17, 540, 390, w))

        for ctx, lw, al in ((cs, 2.8, w * 0.95), (cg, 6.2, w * 0.42)):
            ctx.save(); ctx.set_dash([])
            rounded_rect_path(ctx, 565, 965, 340, 340, 14)
            if ctx is cs:
                ctx.set_source_rgba(0.04, 0.04, 0.055, 0.94 * w); ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

        cs.save(); cg.save()
        for ctx in (cs, cg):
            ctx.translate(605, 965); ctx.rotate(-lean); ctx.translate(-605, -965)
        draw_human_figure(cs, 605, 965, scale=1.72, alpha=w * 0.96, lw=2.8)
        draw_human_figure(cg, 605, 965, scale=1.72, alpha=w * 0.40, lw=5.8)
        cs.restore(); cg.restore()

        star_y = 755 + math.sin(t * 3.2) * 14.0
        draw_star4(cs, 285, star_y, 38.0, w * 0.95)
        draw_star4(cg, 285, star_y, 62.0, w * 0.55)
        sp_20 = get_fitted_text_sprite("+۲۰٪ تجمل", fonts.bold_30, 240, (255, 255, 255, 255), glow=0.6)
        sp_80p = get_fitted_text_sprite("صخره‌ی ۸۰٪ آرامش", fonts.bold_30, 300, (220, 220, 235, 255))
        sp_void = get_fitted_text_sprite("پرتگاهِ ۵۰٪ پوچ!", fonts.reg_26, 280, (175, 175, 192, 255))
        stx.append((sp_20, 285, star_y - 68, w))
        stx.append((sp_80p, 735, 1085, w))
        stx.append((sp_void, 295, 1235, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 18 (b18..b19): 3 AM Dark Room Regret — Coin Lands "Khat = 0 Toman"!
    # =========================================================================
    w = _shot_win(t, b18, b19)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b18, b19, base_in=0.95)
        push_camera(cs, cg, zoom=cz, px=540, py=900)

        for ctx, lw, al in ((cs, 2.0, w * 0.48), (cg, 4.5, w * 0.20)):
            ctx.save(); ctx.set_dash([])
            ctx.arc(540, 560, 68, 0, 2 * math.pi)
            ctx.move_to(540, 560); ctx.line_to(540 + 38, 560)
            ctx.move_to(540, 560); ctx.line_to(540, 560 - 52)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

        draw_slumped_regret_figure(cs, cg, 610, 1185, scale=2.15, t=t, alpha=w)
        draw_spinning_coin_3d(cs, cg, 355, 1168, 54.0, 1.32, alpha=w * 0.85)

        sp_r18 = get_fitted_text_sprite("اگه «خط» بیاد: ۰ تومان و حسرتِ همیشگی...", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.75)
        sp_th  = get_fitted_text_sprite("«ای کاش همون ۱۰ میلیارد رو زده بودم...»", fonts.reg_26, 760, (195, 195, 212, 255))
        stx.append((sp_r18, 540, 395, w))
        stx.append((sp_th, 540, 1265, w * 0.90))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=900)

    # =========================================================================
    # SHOT 19 (b19..b20): Real-Life Markets & Decisions — Character + Volatile Chart!
    # =========================================================================
    w = _shot_win(t, b19, b20)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b19, b20, base_in=0.93)
        push_camera(cs, cg, zoom=cz, px=540, py=860)
        cp = ease_out_cubic(clamp((t - b19) / 0.55))

        pts_m = [(160, 880), (265, 760), (355, 850), (465, 620), (555, 790), (665, 540), (775, 920), (910, 895)]
        for ctx, lw, al in ((cs, 3.0, w * 0.92), (cg, 6.8, w * 0.42)):
            ctx.save()
            ctx.move_to(*pts_m[0])
            for px, py in pts_m[1:]:
                ctx.line_to(px, py)
            set_stroke_draw(ctx, cp, 1250)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

        draw_glow_line(cs, cg, 220, 1210, 860, 1210, w * 0.48)
        draw_character_with_phone(cs, cg, 540, 1210, scale=1.78, raise_p=0.95, screen_glow=1.0, alpha=w, t=t)
        sp_m19 = get_fitted_text_sprite("توی بازار و تصمیم‌های مالی هم همینه!", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_m19, 540, 395, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=860)

    # =========================================================================
    # SHOT 20 (b20..b21): POV Hand Holding Phone — The Golden Rule of Smart Risk!
    # =========================================================================
    w = _shot_win(t, b20, b21)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b20, b21, base_in=0.92)
        push_camera(cs, cg, zoom=cz, px=540, py=835)
        draw_pov_phone_in_hand(cs, cg, 540, 835, 355, 635, thumb_swipe=0.0, thumb_tap=0.0, alpha=w, draw_p=1.0)
        sp_g1 = get_fitted_text_sprite("قانونِ طلاییِ ریسک:", fonts.reg_26, 280, (195, 195, 212, 255))
        sp_g2 = get_fitted_text_sprite("نیازِ واقعیت رو", fonts.bold_44, 280, (255, 255, 255, 255), glow=0.6)
        sp_g3 = get_fitted_text_sprite("پای طمعِ بیشتر", fonts.bold_36, 280, (235, 235, 248, 255))
        sp_g4 = get_fitted_text_sprite("قمار نکن!", fonts.bold_44, 280, (255, 255, 255, 255), glow=0.85)
        stx.append((sp_g1, 540, 602, w))
        stx.append((sp_g2, 540, 682, w))
        stx.append((sp_g3, 540, 760, w))
        stx.append((sp_g4, 540, 840, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=835)

    # =========================================================================
    # SHOT 21 (b21..b22): Liberation Star — Stepping onto Solid Foundation!
    # =========================================================================
    w = _shot_win(t, b21, b22)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b21, b22, base_in=0.94) + impact_punch(t, tc["c21_free"], 0.042, 0.45)
        push_camera(cs, cg, zoom=cz, px=540, py=880)

        burst_u = clamp((t - (tc["c21_free"] - 0.15)) / 1.15)
        if burst_u > 0.01:
            al_sh = w * (1.0 - burst_u * 0.65)
            for k in range(24):
                ang = k * (2 * math.pi / 24.0) + 0.15
                r_in = 85.0 + 275.0 * ease_out_cubic(burst_u)
                x1, y1 = 540 + math.cos(ang) * r_in, 880 + math.sin(ang) * r_in
                x2, y2 = 540 + math.cos(ang) * (r_in + 22), 880 + math.sin(ang) * (r_in + 22)
                draw_glow_line(cs, cg, x1, y1, x2, y2, al_sh, lw_s=2.4, lw_g=5.5)

        draw_glow_line(cs, cg, 220, 1185, 860, 1185, w * 0.65)
        draw_character_with_phone(cs, cg, 540, 1185, scale=2.05, raise_p=0.10, screen_glow=0.0, alpha=w, t=t)
        draw_star4(cs, 540, 1185 - 148 * 2.05, 22.0, w)
        draw_star4(cg, 540, 1185 - 148 * 2.05, 38.0, w * 0.75)

        sp_f21 = get_fitted_text_sprite("اول زیرِ پات رو محکم کن؛ بعد ریسک کن!", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.8)
        stx.append((sp_f21, 540, 405, w))
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cz, px=540, py=880)

    # =========================================================================
    # SHOT 22 (b22..b23): Return to the Console — Now It's YOUR Real-Life Turn!
    # =========================================================================
    w = _shot_win(t, b22, b23)
    if w > 0.01:
        stx = []
        cz = _shot_cam_z(t, b22, b23, base_in=0.94)
        push_camera(cs, cg, zoom=cz, px=540, py=880)
        draw_glow_line(cs, cg, 160, 1150, 920, 1150, w * 0.50)
        draw_two_button_console(cs, cg, 430, 1150, scale=1.24, active_btn=0, t=t, alpha=w)
        draw_character_at_console(cs, cg, 695, 1150, scale=1.84, reach_mode=0, reach_p=0.8, t=t, alpha=w)
        sp_q22 = get_fitted_text_sprite("با وضعِ الانِ زندگیت، کدوم رو می‌زنی؟", fonts.bold_44, 880, (255, 255, 255, 255), glow=0.8)
        stx.append((sp_q22, 540, 415, w))
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

        sp_q23 = get_fitted_text_sprite("انتخابِ امشبِ تو کدومه؟", fonts.bold_44, 860, (255, 255, 255, 255), glow=0.75)
        stx.append((sp_q23, 540, 385, w))

        for bx, num_s, t1_s, t2_s in (
            (745, "۱", "۱۰ میلیاردِ قطعی", "آرامش و شروعِ مطمئن"),
            (335, "۲", "شیریاخطِ ۱۰۰ میلیارد", "۵۰٪ پادشاهی یا ۰!"),
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
        draw_safe_card(cs, cg, stx, 540, 1255, 820, 104, [("همین الان عددش رو تو کامنت بنویس: ۱ یا ۲؟", fonts.bold_30, 0, (255, 255, 255, 255), 0.6)], alpha=w, glow_border=True)
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
    test_ln = meta["sub_lines"][min(3, len(meta["sub_lines"]) - 1)]
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
    ts_24[2] = clamp(tc["c03_10b"] + 0.35, bounds[2] + 0.25, bounds[3] - 0.20)
    ts_24[3] = clamp(tc["c04_coin"] + 0.35, bounds[3] + 0.25, bounds[4] - 0.20)
    ts_24[4] = clamp(tc["c05_zero"] + 0.35, bounds[4] + 0.25, bounds[5] - 0.20)

    pw24, ph24 = 270, 480
    grid24 = Image.new("RGB", (pw24 * 6, ph24 * 4), (16, 16, 20))
    for i, ts in enumerate(ts_24):
        ts_c = max(0.08, min(td - 0.12, ts))
        raw = render_scene_frame(ts_c, td, tc, meta["sub_lines"], fonts, sg, cg, ss, cs)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw24, ph24), Image.Resampling.LANCZOS)
        r, c = divmod(i, 6)
        grid24.paste(im, (c * pw24, r * ph24))
    grid24.save(os.path.join(qa_dir, "storyboard_24_shots.png"))

    pick_12 = [0, 1, 2, 3, 4, 6, 8, 10, 13, 16, 19, 22]
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

    print("=== [1/3] Building Studio v4.1 Master Audio (Locked Rasalgethi + Velvet Dark-Ambient Score + Clean Foley) ===", flush=True)
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
        print("Usage: python src/episodes/ep06_two_buttons_paradox.py --cloud-render <fonts> <work> <out.mp4> <qa_dir> [whisper_size]")
