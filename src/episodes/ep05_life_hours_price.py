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
    draw_safe_card, draw_pill_badge, draw_folder_window,
    draw_ambient_particles, draw_curved_arrow, draw_cursor_pointer,
    impact_punch, push_camera, pop_camera_and_transform_texts,
    draw_shockwave_ring, draw_hypnotic_chronograph_ring,
    draw_hourglass_monolith, draw_ecg_waveform,
    composite_oled_frame,
)


def draw_glow_line(cs, cg, x0: float, y0: float, x1: float, y1: float, alpha: float = 1.0, lw_s: float = 2.0, lw_g: float = 5.0):
    if alpha <= 0.01:
        return
    cs.save(); cg.save(); cs.set_dash([]); cg.set_dash([])
    cs.move_to(x0, y0); cs.line_to(x1, y1); cs.set_source_rgba(1, 1, 1, 0.92 * alpha); cs.set_line_width(lw_s); cs.stroke()
    cg.move_to(x0, y0); cg.line_to(x1, y1); cg.set_source_rgba(1, 1, 1, 0.55 * alpha); cg.set_line_width(lw_g); cg.stroke()
    cs.restore(); cg.restore()

EP_CODE = "۰۵"
EP_TITLE = "قیمت به ساعتِ عمر"

# =============================================================================
# 32 Colloquial Gut-Punching Segments (~64-67s @ ~175 WPM + 4.0s D-Minor Outro)
# Zero English loanwords; 100% matched to _NUM_WORDS_FA for sub-pixel Whisper sync
# =============================================================================
SCRIPT_SEGMENTS = [
    # Scene 1: Hypnotic X-Ray Smartphone Hook (0 - 10s)
    ("همین گوشیی که الان توی دستته رو،",                "همین گوشیی که الان توی دستته رو،"),                # 0
    ("چند خریدی؟",                                      "چند خریدی؟"),                                      # 1
    ("پنجاه میلیون؟ شصت میلیون؟",                       "۵۰ میلیون؟ ۶۰ میلیون؟"),                           # 2
    ("بذار یه رازِ ترسناک رو بهت بگم:",                  "بذار یه راز ترسناک رو بهت بگم:"),                  # 3
    ("تو براش شصت میلیون پول ندادی؛",                   "تو براش ۶۰ میلیون پول ندادی؛"),                    # 4
    ("تو شیشصد ساعت از عمرت رو دادی!",                  "تو ۶۰۰ ساعت از عمرت رو دادی!"),                    # 5

    # Scene 2: The Hidden Currency — Paper vs Irreversible Life-Hours (10 - 19s)
    ("ما فکر می‌کنیم با پول خرید می‌کنیم؛",              "ما فکر می‌کنیم با پول خرید می‌کنیم؛"),              # 6
    ("ولی پول فقط یه کاغذِ واسطه‌ست!",                   "ولی پول فقط یه کاغذ واسطه‌ست!"),                   # 7
    ("واحدِ واقعیِ هر خریدی توی دنیا،",                  "واحد واقعی هر خریدی توی دنیا،"),                   # 8
    ("ساعت‌هایی از زندگیِ توئه،",                        "ساعت‌هایی از زندگی توئه،"),                         # 9
    ("که دیگه هیچ‌وقت برنمی‌گردن!",                      "که دیگه هیچ‌وقت برنمی‌گردن!"),                      # 10

    # Scene 3: Brutal Math — 600 Hours = 75 Full Workdays = 1 Season of Youth (19 - 30s)
    ("بیا خیلی ساده حسابش کنیم:",                       "بیا خیلی ساده حسابش کنیم:"),                       # 11
    ("اگه با رفت‌وآمد و خستگیِ کار،",                    "اگه با رفت‌وآمد و خستگی کار،"),                     # 12
    ("ساعتی صد هزار تومن دربیاری،",                     "ساعتی ۱۰۰ هزار تومن دربیاری،"),                    # 13
    ("اون گوشیِ شصت میلیونی،",                          "اون گوشی ۶۰ میلیونی،"),                            # 14
    ("یعنی هفتاد و پنج روزِ کاملِ کاری!",                "یعنی ۷۵ روز کامل کاری!"),                          # 15
    ("یعنی کلِ یه فصل از جوونیت!",                       "یعنی کل یه فصل از جوونیت!"),                       # 16

    # Scene 4: Everyday X-Ray Scanner — Shoes, Luxury Dinner, Upgrades (30 - 40s)
    ("حالا با همین عینک به اطرافت نگاه کن:",             "حالا با همین عینک به اطرافت نگاه کن:"),             # 17
    ("کفشِ شیش میلیونی؟",                                "کفش ۶ میلیونی؟"),                                  # 18
    ("شصت ساعت پای کار موندن!",                         "۶۰ ساعت پای کار موندن!"),                          # 19
    ("شامِ پرزرق‌وبرقِ دو میلیونی؟",                     "شام پرزرق‌وبرق ۲ میلیونی؟"),                       # 20
    ("بیست ساعت از آزادیِ خالصت!",                       "۲۰ ساعت از آزادی خالصت!"),                         # 21

    # Scene 5: The Clockwork Wheel — When Things Own You (40 - 50s)
    ("تلخ‌ترین جاش کجاست؟",                              "تلخ‌ترین جاش کجاست؟"),                              # 22
    ("وقتی فقط برای چشم‌وهم‌چشمی خرید می‌کنی،",          "وقتی فقط برای چشم‌وهم‌چشمی خرید می‌کنی،"),          # 23
    ("دیگه تو صاحبِ وسایلت نیستی؛",                     "دیگه تو صاحب وسایلت نیستی؛"),                      # 24
    ("اون وسایل صاحبِ عمر و زندگیِ توئن!",               "اون وسایل صاحب عمر و زندگی توئن!"),                # 25

    # Scene 6: 3-Second Mental Antidote — Break the Chain (50 - 58s)
    ("از امشب قبلِ هر خریدی،",                          "از امشب قبل هر خریدی،"),                           # 26
    ("قیمتش رو به ساعتِ عمرت تقسیم کن؛",                 "قیمتش رو به ساعت عمرت تقسیم کن؛"),                 # 27
    ("ببین واقعاً به اون‌همه زندگی می‌ارزه یا نه!",      "ببین واقعاً به اون‌همه زندگی می‌ارزه یا نه!"),      # 28

    # Scene 7: Interactive Self-Calculation CTA (58 - 64s)
    ("گوشیی که الان دستته،",                            "گوشیی که الان دستته،"),                            # 29
    ("چند ماه از عمرت پاش رفته؟",                       "چند ماه از عمرت پاش رفته؟"),                       # 30
    ("عددش رو همین الان تو کامنت بنویس!",                "عددش رو همین الان تو کامنت بنویس!"),                # 31
]

# Synchronized Hypnotic Editing & Micro-SFX Cues
SFX_CUE_MAP = [
    ("s1_price",   2, 0, "ping"),       # "۵۰ میلیون؟ ۶۰ میلیون؟"
    ("s1_secret",  3, 2, "scan"),       # "راز ترسناک" -> X-ray reveals hourglass inside phone!
    ("s1_600",     5, 1, "stamp"),      # "۶۰۰ ساعت" -> 3D card flip + shockwave punch!
    ("s2_paper",   6, 0, "whoosh"),     # Scene 2 transition -> Astronomical Balance Scale
    ("s2_life",    9, 0, "heartbeat"),  # "ساعت‌هایی از زندگی توئه" -> Scale tips + ECG pulse
    ("s3_calc",   11, 0, "whoosh"),     # Scene 3 -> Live HUD Life-Calculator
    ("s3_rate",   13, 1, "click"),      # "۱۰۰ هزار تومن" -> Rate locks in
    ("s3_75d",    15, 1, "tick"),       # "۷۵ روز کامل کاری" -> 75-day domino wave completes
    ("s3_season", 16, 2, "stamp"),      # "یه فصل از جوونیت!" -> Shockwave badge
    ("s4_lens",   17, 0, "scan"),       # Scene 4 -> Everyday X-ray scanner
    ("s4_shoe",   19, 0, "ping"),       # "۶۰ ساعت"
    ("s4_din",    21, 0, "ping"),       # "۲۰ ساعت"
    ("s5_wheel",  22, 0, "whoosh"),     # Scene 5 -> Giant Clockwork Wheel + Running Human
    ("s5_own",    25, 1, "heartbeat"),  # "صاحب عمر و زندگی توئن!" -> Chain pulse
    ("s6_rule",   26, 0, "whoosh"),     # Scene 6 -> 3-Second Filter Portal
    ("s6_worth",  28, 3, "shatter"),    # "زندگی می‌ارزه" -> Chains shatter into fireflies!
    ("s7_cta",    29, 0, "click"),      # Scene 7 -> 1 / 2 / 3 Comment Trigger
]


# =============================================================================
# Bespoke 60fps Vector Art Primitives for Episode 05
# =============================================================================

def draw_flagship_phone(
    cs, cg, cx: float, cy: float, w: float, h: float,
    alpha: float = 1.0, draw_p: float = 1.0, glow: bool = True
):
    """Minimalist museum-grade flagship smartphone bezel + Dynamic Island + side buttons."""
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    dp = clamp(draw_p)
    x0, y0 = cx - w / 2.0, cy - h / 2.0
    rad = min(40.0, w * 0.15)

    # Subtle obsidian inner glass fill
    cs.save()
    cs.set_dash([])
    rounded_rect_path(cs, x0, y0, w, h, rad)
    cs.set_source_rgba(0.03, 0.03, 0.045, 0.90 * alpha * dp)
    cs.fill()
    cs.restore()

    for ctx, lw, al in ((cs, 3.0, alpha * 0.96), (cg, 6.2, alpha * (0.55 if glow else 0.22))):
        ctx.save()
        set_stroke_draw(ctx, dp, 2.0 * (w + h))
        rounded_rect_path(ctx, x0, y0, w, h, rad)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()
        # Inner bezel hairline
        rounded_rect_path(ctx, x0 + 10, y0 + 10, w - 20, h - 20, max(16.0, rad - 8.0))
        ctx.set_source_rgba(1, 1, 1, al * 0.35)
        ctx.set_line_width(1.2)
        ctx.stroke()
        ctx.restore()

    if dp > 0.55:
        cs.save(); cg.save()
        cs.set_dash([]); cg.set_dash([])
        # Dynamic Island pill
        iw, ih = w * 0.30, 14.0
        rounded_rect_path(cs, cx - iw / 2.0, y0 + 22.0, iw, ih, 7.0)
        cs.set_source_rgba(1, 1, 1, 0.72 * alpha); cs.set_line_width(1.7); cs.stroke()
        # Side tactile buttons
        cs.move_to(x0 - 3, cy - 75); cs.line_to(x0 - 3, cy - 30); cs.stroke()
        cs.move_to(x0 - 3, cy - 12); cs.line_to(x0 - 3, cy + 32); cs.stroke()
        cs.move_to(x0 + w + 3, cy - 45); cs.line_to(x0 + w + 3, cy + 18); cs.stroke()
        cs.restore(); cg.restore()


def draw_clock_gear(
    cs, cg, cx: float, cy: float, r_pitch: float, n_teeth: int,
    rot_rad: float, alpha: float = 1.0, glow: bool = False
):
    """Precision involute-style mechanical clockwork gear with inner spokes."""
    if alpha <= 0.01:
        return
    r_in = r_pitch - 11.0
    r_out = r_pitch + 11.0
    step = 2.0 * math.pi / n_teeth

    for ctx, lw, al in ((cs, 2.2, alpha * 0.88), (cg, 4.8, alpha * (0.42 if glow else 0.18))):
        ctx.save()
        ctx.set_dash([])
        for i in range(n_teeth):
            a0 = rot_rad + i * step
            a1 = a0 + step * 0.22
            a2 = a0 + step * 0.48
            a3 = a0 + step * 0.70
            p0 = (cx + math.cos(a0) * r_in,  cy + math.sin(a0) * r_in)
            p1 = (cx + math.cos(a1) * r_out, cy + math.sin(a1) * r_out)
            p2 = (cx + math.cos(a2) * r_out, cy + math.sin(a2) * r_out)
            p3 = (cx + math.cos(a3) * r_in,  cy + math.sin(a3) * r_in)
            if i == 0:
                ctx.move_to(*p0)
            else:
                ctx.line_to(*p0)
            ctx.line_to(*p1); ctx.line_to(*p2); ctx.line_to(*p3)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()

        # Inner rim + 6 structural spokes
        r_hub = r_pitch * 0.20
        r_rim = r_pitch * 0.82
        ctx.arc(cx, cy, r_rim, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, al * 0.55); ctx.set_line_width(1.5); ctx.stroke()
        ctx.arc(cx, cy, r_hub, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, al * 0.75); ctx.set_line_width(1.8); ctx.stroke()
        for sp_i in range(6):
            sa = rot_rad + sp_i * (math.pi / 3.0)
            ctx.move_to(cx + math.cos(sa) * r_hub, cy + math.sin(sa) * r_hub)
            ctx.line_to(cx + math.cos(sa) * r_rim, cy + math.sin(sa) * r_rim)
            ctx.set_source_rgba(1, 1, 1, al * 0.38); ctx.set_line_width(1.6); ctx.stroke()
        ctx.restore()


def draw_running_human_60fps(
    cs, cg, cx: float, foot_y: float, scale: float, t: float, alpha: float = 1.0, facing_left: bool = True
):
    """60fps articulated running human figure (sine-coupled stride + arm swing + forward lean)."""
    if alpha <= 0.01:
        return
    sgn = -1.0 if facing_left else 1.0
    ph = t * 8.4  # Crisp athletic stride cadence

    hip_x = cx
    hip_y = foot_y - 68.0 * scale + abs(math.sin(ph)) * 7.0 * scale
    sh_x  = hip_x + sgn * 14.0 * scale
    sh_y  = hip_y - 54.0 * scale
    hd_x  = sh_x + sgn * 8.0 * scale
    hd_y  = sh_y - 24.0 * scale

    for ctx, lw, al in ((cs, 3.0, alpha * 0.96), (cg, 6.0, alpha * 0.45)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)

        # Head
        ctx.arc(hd_x, hd_y, 15.0 * scale, 0, 2 * math.pi); ctx.stroke()
        # Torso
        ctx.move_to(sh_x, sh_y); ctx.line_to(hip_x, hip_y); ctx.stroke()

        # Two legs in counter-phase
        for leg_off, op_mul in ((0.0, 1.0), (math.pi, 0.68)):
            sw = math.sin(ph + leg_off)
            lift = max(0.0, math.cos(ph + leg_off))
            kx = hip_x + sgn * (20.0 * sw + 8.0) * scale
            ky = hip_y + (34.0 - 10.0 * lift) * scale
            fx = kx + sgn * (16.0 * sw - 12.0 * lift) * scale
            fy = hip_y + (66.0 - 22.0 * lift) * scale
            ctx.set_source_rgba(1, 1, 1, al * op_mul)
            ctx.move_to(hip_x, hip_y); ctx.line_to(kx, ky); ctx.line_to(fx, fy); ctx.stroke()

        # Two arms in counter-phase (front arm reaching toward phone!)
        for arm_off, op_mul in ((math.pi, 1.0), (0.0, 0.65)):
            aw = math.sin(ph + arm_off)
            ex = sh_x + sgn * (18.0 * aw + 6.0) * scale
            ey = sh_y + 24.0 * scale
            hx = ex + sgn * (20.0 * max(-0.2, aw) + 12.0) * scale
            hy = ey - (10.0 + 12.0 * aw) * scale
            ctx.set_source_rgba(1, 1, 1, al * op_mul)
            ctx.move_to(sh_x, sh_y); ctx.line_to(ex, ey); ctx.line_to(hx, hy); ctx.stroke()
        ctx.restore()

    # Return leading wrist coordinate so clock-chains can attach cleanly!
    aw_front = math.sin(ph + math.pi)
    ex_f = sh_x + sgn * (18.0 * aw_front + 6.0) * scale
    ey_f = sh_y + 24.0 * scale
    wx = ex_f + sgn * (20.0 * max(-0.2, aw_front) + 12.0) * scale
    wy = ey_f - (10.0 + 12.0 * aw_front) * scale
    return wx, wy


def draw_mini_everyday_icon(cs, cg, kind: str, cx: float, cy: float, t: float, alpha: float = 1.0, active: float = 0.0):
    """Animated bespoke vector icons for Scene 4 rows: 'shoe', 'dinner', 'phone'."""
    if alpha <= 0.01:
        return
    bob = math.sin(t * 3.4) * 3.5 * (0.3 + 0.7 * active)
    cy = cy + bob
    for ctx, lw, al in ((cs, 2.3, alpha * 0.94), (cg, 4.8, alpha * (0.22 + 0.38 * active))):
        ctx.save()
        ctx.set_dash([])
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        if kind == "shoe":
            # Crisp minimalist sneaker silhouette
            ctx.move_to(cx - 42, cy + 20)
            ctx.line_to(cx + 42, cy + 20)
            ctx.curve_to(cx + 44, cy + 6, cx + 30, cy + 2, cx + 12, cy - 4)
            ctx.line_to(cx - 6, cy - 22)
            ctx.line_to(cx - 24, cy - 18)
            ctx.line_to(cx - 38, cy + 4)
            ctx.close_path(); ctx.stroke()
            # Sole line + laces
            ctx.move_to(cx - 42, cy + 13); ctx.line_to(cx + 41, cy + 13); ctx.stroke()
            ctx.move_to(cx + 2, cy - 14); ctx.line_to(cx + 10, cy - 8); ctx.stroke()
            ctx.move_to(cx + 8, cy - 9); ctx.line_to(cx + 16, cy - 3); ctx.stroke()
        elif kind == "dinner":
            # Fine-dining silver cloche platter + rising aroma wave
            ctx.move_to(cx - 46, cy + 18); ctx.line_to(cx + 46, cy + 18); ctx.stroke()
            lift = 6.0 * active
            ctx.arc(cx, cy + 14 - lift, 36.0, math.pi, 2 * math.pi); ctx.close_path(); ctx.stroke()
            ctx.arc(cx, cy - 25 - lift, 4.5, 0, 2 * math.pi); ctx.stroke()
            if ctx is cs:
                for si in (-14, 0, 14):
                    sw_s = math.sin(t * 4.0 + si) * 5.0
                    ctx.move_to(cx + si, cy - 32 - lift)
                    ctx.curve_to(cx + si + sw_s, cy - 38 - lift, cx + si - sw_s, cy - 44 - lift, cx + si, cy - 50 - lift)
                    ctx.set_source_rgba(1, 1, 1, al * 0.55); ctx.set_line_width(1.4); ctx.stroke()
        else:
            # Sleek mini smartphone + upgrade arrow
            rounded_rect_path(ctx, cx - 22, cy - 36, 44, 72, 9); ctx.stroke()
            ctx.move_to(cx - 7, cy - 28); ctx.line_to(cx + 7, cy - 28); ctx.stroke()
            ctx.move_to(cx, cy + 14); ctx.line_to(cx, cy - 12); ctx.stroke()
            ctx.move_to(cx - 9, cy - 3); ctx.line_to(cx, cy - 13); ctx.line_to(cx + 9, cy - 3); ctx.stroke()
        ctx.restore()


# =============================================================================
# Master 60fps Scene Choreography & Virtual Camera Renderer
# =============================================================================

def render_scene_frame(
    t: float, total_dur: float, t_cues: dict, sub_lines: list[dict],
    fonts: FontBank, surf_glow, ctx_glow, surf_sharp, ctx_sharp
) -> bytes:
    for ctx in (ctx_glow, ctx_sharp):
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.restore()

    cs, cg = ctx_sharp, ctx_glow
    txts = []

    t_s1_price  = t_cues["s1_price"]
    t_s1_sec    = t_cues["s1_secret"]
    t_s1_600    = t_cues["s1_600"]
    t_s2_paper  = t_cues["s2_paper"]
    t_s2_life   = t_cues["s2_life"]
    t_s3_calc   = t_cues["s3_calc"]
    t_s3_rate   = t_cues["s3_rate"]
    t_s3_75d    = t_cues["s3_75d"]
    t_s3_season = t_cues["s3_season"]
    t_s4_lens   = t_cues["s4_lens"]
    t_s4_shoe   = t_cues["s4_shoe"]
    t_s4_din    = t_cues["s4_din"]
    t_s5_wheel  = t_cues["s5_wheel"]
    t_s5_own    = t_cues["s5_own"]
    t_s6_rule   = t_cues["s6_rule"]
    t_s6_worth  = t_cues["s6_worth"]
    t_s7_cta    = t_cues["s7_cta"]
    outro_t0    = total_dur - 4.0

    chapters = [0.0, t_s2_paper, t_s3_calc, t_s4_lens, t_s5_wheel, t_s6_rule, t_s7_cta]
    draw_hud_chrome(cs, cg, txts, fonts, t, total_dur, EP_CODE, EP_TITLE, chapters)

    amb_alpha = clamp((outro_t0 - t) / 0.8)
    draw_ambient_particles(cs, t, alpha=0.92 * amb_alpha)

    # =========================================================================
    # SCENE 1 (0 .. t_s2_paper): HYPNOTIC X-RAY SMARTPHONE -> 600 LIFE-HOURS!
    # =========================================================================
    w1 = window_fade(t, -0.1, t_s2_paper + 0.02, fi=0.20, fo=0.28)
    if w1 > 0.01:
        stx = []
        u1 = clamp(t / max(1.0, t_s2_paper))
        whip_out1 = clamp((t - (t_s2_paper - 0.26)) / 0.28) ** 2 * 0.08
        cam_z = (0.95 + 0.08 * ease_out_cubic(min(1.0, t / 0.85))
                 + 0.032 * u1 + whip_out1
                 + impact_punch(t, t_s1_600, amp=0.038, dur=0.60))
        cam_dy = math.sin(t * 1.1) * 4.0
        push_camera(cs, cg, zoom=cam_z, dx=0.0, dy=cam_dy, px=540.0, py=805.0)

        p_in = ease_out_cubic(clamp(t / 0.85))
        xray_p = ease_in_out_cubic(clamp((t - (t_s1_sec - 0.15)) / 0.85))
        flip_raw = clamp((t - (t_s1_600 - 0.12)) / 0.58)
        shock_600 = clamp((t - t_s1_600) / 0.72)

        draw_pill_badge(cs, cg, stx, "پشتِ صحنه‌ی قیمتِ گوشیِ توی دستت", 540, 238, fonts.reg_26, w1 * p_in)

        # Perpetual counter-rotating Swiss chronograph halo around smartphone!
        draw_hypnotic_chronograph_ring(
            cs, cg, 540, 745, 305.0, t,
            alpha=w1 * (0.42 + 0.45 * xray_p), draw_p=p_in, speed=(1.0 + 1.4 * xray_p)
        )

        # Center Flagship Smartphone (540, 745)
        draw_flagship_phone(cs, cg, 540, 745, 256, 470, alpha=w1, draw_p=p_in, glow=True)

        # Before X-ray: clean retail screen UI inside phone; After X-ray: live draining Hourglass Monolith!
        pre_al = w1 * p_in * (1.0 - 0.88 * xray_p)
        if pre_al > 0.03:
            sp_scr1 = get_fitted_text_sprite("قیمت روی فاکتور", fonts.light_22, 200, (185, 185, 198, 255))
            sp_scr2 = get_fitted_text_sprite("۶۰ میلیون", fonts.bold_44, 210, (255, 255, 255, 255), glow=0.55)
            sp_scr3 = get_fitted_text_sprite("تومان", fonts.reg_26, 200, (215, 215, 228, 255))
            stx.append((sp_scr1, 540, 665, pre_al))
            stx.append((sp_scr2, 540, 738, pre_al))
            stx.append((sp_scr3, 540, 795, pre_al))

        if xray_p > 0.02:
            sand_left = clamp(0.82 - 0.52 * clamp((t - t_s1_sec) / max(1.2, t_s2_paper - t_s1_sec)))
            draw_hourglass_monolith(
                cs, cg, 540, 755, 148, 285,
                sand_top=sand_left, flowing=True, t=t, alpha=w1 * xray_p, draw_p=xray_p
            )
            # Sweeping X-ray horizontal laser beam inside phone glass
            scan_y = 535.0 + ((t * 175.0) % 420.0)
            draw_glow_line(cs, cg, 424, scan_y, 656, scan_y, w1 * xray_p * 0.72, lw_s=1.8, lw_g=5.0)

            # Human silhouette on right (895, 955) whose life-sparks stream into the phone!
            draw_human_figure(cs, 895, 955, scale=0.92, alpha=w1 * xray_p * 0.92, vortex=True, t=t)
            draw_human_figure(cg, 895, 955, scale=0.92, alpha=w1 * xray_p * 0.38, lw=4.5)
            for oi in range(10):
                ou = ((t * 0.95 + oi / 10.0) % 1.0)
                # Parabolic arc from human chest (875, 865) -> phone core (540, 755)
                ox = (1 - ou) ** 2 * 865 + 2 * (1 - ou) * ou * 725 + ou ** 2 * 565
                oy = (1 - ou) ** 2 * 865 + 2 * (1 - ou) * ou * 645 + ou ** 2 * 755
                oa = math.sin(math.pi * ou) * w1 * xray_p
                cs.arc(ox, oy, 3.6, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.95 * oa); cs.fill()
                cg.arc(ox, oy, 8.5, 0, 2 * 3.14159); cg.set_source_rgba(1, 1, 1, 0.65 * oa); cg.fill()

        # Shockwave burst at "۶۰۰ ساعت از عمرت!"
        if 0.01 < shock_600 < 0.99:
            draw_shockwave_ring(cs, cg, 540, 745, shock_600, max_r=410.0, alpha=w1)

        # Bottom 3D Perspective Flip Card (y = 1185): flips from "۶۰ میلیون تومان" -> "۶۰۰ ساعت از عمرت!"
        ang_f = math.pi * ease_in_out_cubic(flip_raw)
        sx_card = max(0.08, abs(math.cos(ang_f)))
        card_w_cur = 780.0 * sx_card
        is_revealed = (flip_raw >= 0.5)
        if not is_revealed:
            p_appear = ease_out_cubic(clamp((t - (t_s1_price - 0.15)) / 0.45))
            if p_appear > 0.02:
                draw_safe_card(
                    cs, cg, stx if sx_card > 0.35 else [], 540, 1185, card_w_cur, 150,
                    [
                        ("عددی که روی برچسب می‌بینی:", fonts.reg_26, -34, (190, 190, 202, 255), 0.0),
                        ("۵۰ تا ۶۰ میلیون تومان", fonts.bold_36, 26, (250, 250, 255, 255), 0.45),
                    ],
                    radius=18, pad_x=28, alpha=w1 * p_appear, allow_expand=False
                )
        else:
            draw_safe_card(
                cs, cg, stx if sx_card > 0.35 else [], 540, 1185, card_w_cur, 165,
                [
                    ("قیمتِ واقعی که از وجودت پرداخت کردی:", fonts.reg_26, -38, (220, 220, 232, 255), 0.25),
                    ("۶۰۰ ساعت از عمرت!", fonts.bold_44, 28, (255, 255, 255, 255), 0.85),
                ],
                radius=18, pad_x=28, alpha=w1, glow_border=True, allow_expand=False
            )
            draw_star4(cs, 175, 1125, 14.0, w1); draw_star4(cg, 175, 1125, 22.0, w1 * 0.8)
            draw_star4(cs, 905, 1125, 14.0, w1); draw_star4(cg, 905, 1125, 22.0, w1 * 0.8)

        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cam_z, dx=0.0, dy=cam_dy, px=540.0, py=805.0)

    # =========================================================================
    # SCENE 2 (t_s2_paper .. t_s3_calc): ASTRONOMICAL SCALE + ECG LIFELINE
    # =========================================================================
    w2 = window_fade(t, t_s2_paper - 0.04, t_s3_calc + 0.02, fi=0.26, fo=0.28)
    if w2 > 0.01:
        stx = []
        p2 = ease_out_cubic(clamp((t - t_s2_paper) / 0.55))
        tip_p = ease_in_out_cubic(clamp((t - (t_s2_life - 0.15)) / 0.90))
        whip_out2 = clamp((t - (t_s3_calc - 0.26)) / 0.28) ** 2 * 0.08
        cam_z2 = (0.93 + 0.07 * p2
                  + 0.028 * clamp((t - t_s2_paper) / max(1.0, t_s3_calc - t_s2_paper))
                  + whip_out2
                  + impact_punch(t, t_s2_life, amp=0.032, dur=0.60))
        push_camera(cs, cg, zoom=cam_z2, px=540.0, py=820.0)

        draw_pill_badge(cs, cg, stx, "واحدِ واقعیِ معامله: کاغذ یا زندگی؟", 540, 238, fonts.reg_26, w2 * p2)

        # Astronomical Fulcrum & Tilting Balance Beam at (540, 585)
        piv_x, piv_y = 540.0, 585.0
        tilt_deg = 13.5 * tip_p
        tilt_rad = math.radians(tilt_deg)
        arm_len = 280.0

        lx = piv_x - math.cos(tilt_rad) * arm_len
        ly = piv_y + math.sin(tilt_rad) * arm_len
        rx = piv_x + math.cos(tilt_rad) * arm_len
        ry = piv_y - math.sin(tilt_rad) * arm_len

        draw_hypnotic_chronograph_ring(cs, cg, piv_x, piv_y, 165.0, t, alpha=w2 * 0.28, draw_p=p2, speed=0.8)

        # Central fulcrum pillar + beam + generous suspension triangles
        pan_drop = 142.0
        for ctx, lw, al in ((cs, 2.8, w2 * 0.92), (cg, 5.5, w2 * 0.40)):
            ctx.save(); ctx.set_dash([])
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            ctx.move_to(piv_x - 62, 955); ctx.line_to(piv_x + 62, 955); ctx.stroke()
            ctx.move_to(piv_x, 955); ctx.line_to(piv_x, piv_y); ctx.stroke()
            ctx.arc(piv_x, piv_y, 9.0, 0, 2 * math.pi); ctx.stroke()
            ctx.move_to(lx, ly); ctx.line_to(rx, ry); ctx.stroke()
            # Wide suspension cords so hourglass sits 100% cleanly inside!
            ctx.set_line_width(1.5)
            ctx.move_to(lx, ly); ctx.line_to(lx - 86, ly + pan_drop)
            ctx.move_to(lx, ly); ctx.line_to(lx + 86, ly + pan_drop); ctx.stroke()
            ctx.move_to(rx, ry); ctx.line_to(rx - 86, ry + pan_drop)
            ctx.move_to(rx, ry); ctx.line_to(rx + 86, ry + pan_drop); ctx.stroke()
            # Pans
            ctx.set_line_width(lw)
            ctx.move_to(lx - 96, ly + pan_drop)
            ctx.curve_to(lx - 35, ly + pan_drop + 18, lx + 35, ly + pan_drop + 18, lx + 96, ly + pan_drop); ctx.stroke()
            ctx.move_to(rx - 96, ry + pan_drop)
            ctx.curve_to(rx - 35, ry + pan_drop + 18, rx + 35, ry + pan_drop + 18, rx + 96, ry + pan_drop); ctx.stroke()
            ctx.restore()

        # RIGHT PAN (Banknotes dissolving into floating smoke dots — "فقط یه کاغذ واسطه‌ست!")
        fade_note = 1.0 - 0.45 * tip_p
        for bi in range(3):
            bx_n = rx - 50 + bi * 5
            by_n = ry + pan_drop - 52 - bi * 12
            cs.save(); cs.set_dash([])
            rounded_rect_path(cs, bx_n, by_n, 96, 44, 6)
            cs.set_source_rgba(0.04, 0.04, 0.05, 0.9 * w2 * fade_note); cs.fill_preserve()
            cs.set_source_rgba(1, 1, 1, 0.65 * w2 * fade_note); cs.set_line_width(1.8); cs.stroke()
            cs.arc(bx_n + 48, by_n + 22, 10, 0, 2 * math.pi); cs.stroke()
            cs.restore()
        for gi in range(7):
            gu = ((t * 0.8 + gi / 7.0) % 1.0)
            gx = rx - 35 + (gi * 13) % 70 + math.sin(t * 3.0 + gi) * 8.0
            gy = ry + pan_drop - 65 - gu * 85.0
            cs.arc(gx, gy, 2.2, 0, 2 * math.pi)
            cs.set_source_rgba(1, 1, 1, (1.0 - gu) * 0.55 * w2); cs.fill()
        sp_r_lbl = get_fitted_text_sprite("پول (کاغذِ واسطه)", fonts.reg_26, 220, (185, 185, 198, 255))
        stx.append((sp_r_lbl, rx, ry + pan_drop + 46, w2 * p2))

        # LEFT PAN (Heavy Glowing Hourglass sitting cleanly on pan!)
        sand_s2 = clamp(0.75 - 0.45 * clamp((t - t_s2_paper) / max(1.0, t_s3_calc - t_s2_paper)))
        draw_hourglass_monolith(
            cs, cg, lx, ly + pan_drop - 58, 72, 106,
            sand_top=sand_s2, flowing=True, t=t, alpha=w2 * p2, draw_p=p2
        )
        sp_l_lbl = get_fitted_text_sprite("ساعت‌هایِ برنگشتنیِ عمر!", fonts.bold_30, 260, (255, 255, 255, 255), glow=0.6 * tip_p)
        stx.append((sp_l_lbl, lx, ly + pan_drop + 48, w2 * p2))

        if 0.02 < tip_p < 0.95:
            draw_shockwave_ring(cs, cg, lx, ly + pan_drop - 45, tip_p, max_r=180.0, alpha=w2 * 0.7)

        # Bottom Live Scrolling Human Heartbeat ECG Box (540, 1185, w=860, h=205)
        draw_safe_card(
            cs, cg, stx, 540, 1185, 860, 205,
            [
                ("ضربانِ عمر: تنها سرمایه‌ای که هیچ بانکی دوباره چاپش نمی‌کنه!", fonts.reg_26, 66, (235, 235, 245, 255), 0.35),
            ],
            radius=18, pad_x=30, alpha=w2 * p2, glow_border=(tip_p > 0.3), allow_expand=False
        )
        draw_ecg_waveform(cs, cg, 155, 925, 1152, t, amp=42.0, alpha=w2 * p2)

        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cam_z2, px=540.0, py=820.0)

    # =========================================================================
    # SCENE 3 (t_s3_calc .. t_s4_lens): HUD CALCULATOR + 75-DAY DOMINO MATRIX!
    # =========================================================================
    w3 = window_fade(t, t_s3_calc - 0.04, t_s4_lens + 0.02, fi=0.26, fo=0.28)
    if w3 > 0.01:
        stx = []
        p3 = ease_out_cubic(clamp((t - t_s3_calc) / 0.55))
        rate_p = ease_out_cubic(clamp((t - (t_s3_rate - 0.25)) / 0.65))
        dom_u = clamp((t - (t_s3_rate + 0.15)) / max(0.75, (t_s3_75d + 0.45) - (t_s3_rate + 0.15)))
        seas_p = ease_out_cubic(clamp((t - (t_s3_season - 0.15)) / 0.55))
        whip_out3 = clamp((t - (t_s4_lens - 0.26)) / 0.28) ** 2 * 0.08

        cam_z3 = (0.93 + 0.07 * p3
                  + 0.025 * dom_u + whip_out3
                  + impact_punch(t, t_s3_season, amp=0.036, dur=0.60))
        push_camera(cs, cg, zoom=cam_z3, px=540.0, py=835.0)

        draw_pill_badge(cs, cg, stx, "فرمولِ واقعی: تبدیلِ قیمت به روزهای زندگی", 540, 238, fonts.reg_26, w3 * p3)

        # Live rolling hours counter (0 -> 600)
        cur_hrs = int(round(600 * ease_out_cubic(clamp((t - t_s3_calc) / max(0.8, t_s3_75d - t_s3_calc)))))
        hrs_fa = str(cur_hrs).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

        draw_safe_card(
            cs, cg, stx, 540, 435, 860, 195,
            [
                ("گوشیِ ۶۰ میلیونی  ÷  ساعتی ۱۰۰ هزار تومن درآمدِ خالص", fonts.reg_26, -42, (205, 205, 218, 255), 0.15 * rate_p),
                (f"=  {hrs_fa} ساعت کارِ خالص از عمرت!", fonts.bold_44, 34, (255, 255, 255, 255), 0.75),
            ],
            radius=18, pad_x=30, alpha=w3 * p3, glow_border=True, allow_expand=False
        )

        # 75-DAY CALENDAR DOMINO MATRIX (15 cols x 5 rows = 75 full 8-hour workdays!)
        # Enclosed inside an architectural calendar frame (540, 865, w=860, h=520)
        draw_safe_card(
            cs, cg, stx, 540, 865, 860, 520,
            [
                ("تقویمِ عمرت: ۷۵ روزِ کاملِ کاری (هر خانه = ۱ روزِ زندگی)", fonts.reg_26, -212, (215, 215, 228, 255), 0.2),
                ("۷۵ روز کامل کاری  =  بیشتر از ۳ ماه زندگیت!", fonts.bold_30, 212, (255, 255, 255, 255), 0.65 * dom_u),
            ],
            radius=18, pad_x=30, alpha=w3 * p3, glow_border=(dom_u > 0.85), allow_expand=False
        )

        cols, rows = 15, 5
        cell_w, cell_h = 42.0, 52.0
        gap_x, gap_y = 11.0, 14.0
        grid_w = cols * cell_w + (cols - 1) * gap_x
        grid_h = rows * cell_h + (rows - 1) * gap_y
        gx0 = 540.0 - grid_w / 2.0
        gy0 = 865.0 - grid_h / 2.0 + 4.0

        lit_float = dom_u * 75.0
        cs.save(); cg.save()
        cs.set_dash([]); cg.set_dash([])
        for r_i in range(rows):
            for c_i in range(cols):
                # RTL progression (right-to-left across each week row!)
                idx_d = r_i * cols + (cols - 1 - c_i)
                cx_d = gx0 + c_i * (cell_w + gap_x)
                cy_d = gy0 + r_i * (cell_h + gap_y)
                cell_act = clamp(lit_float - idx_d)
                is_crest = (0.01 < cell_act < 0.99) or (0.0 <= (lit_float - idx_d) < 2.2 and dom_u < 0.99)

                rounded_rect_path(cs, cx_d, cy_d, cell_w, cell_h, 7.0)
                if cell_act > 0.02:
                    cs.set_source_rgba(1, 1, 1, (0.20 + 0.58 * cell_act) * w3)
                    cs.fill_preserve()
                    cs.set_source_rgba(1, 1, 1, 0.95 * w3)
                    cs.set_line_width(1.9)
                    cs.stroke()
                    if is_crest:
                        rounded_rect_path(cg, cx_d - 2, cy_d - 2, cell_w + 4, cell_h + 4, 8.0)
                        cg.set_source_rgba(1, 1, 1, 0.85 * w3)
                        cg.set_line_width(4.5)
                        cg.stroke()
                else:
                    cs.set_source_rgba(1, 1, 1, 0.16 * w3 * p3)
                    cs.set_line_width(1.2)
                    cs.stroke()
        cs.restore(); cg.restore()

        if seas_p > 0.04:
            if seas_p < 0.92:
                draw_shockwave_ring(cs, cg, 540, 1235, seas_p, max_r=280.0, alpha=w3 * 0.75)
            draw_pill_badge(
                cs, cg, stx, "یعنی کلِ یه فصل از جوونیت پایِ یه گوشی رفت!",
                540, 1235, fonts.bold_30, w3 * seas_p, glow=True
            )

        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cam_z3, px=540.0, py=835.0)

    # =========================================================================
    # SCENE 4 (t_s4_lens .. t_s5_wheel): EVERYDAY X-RAY LIFE-TAG SCANNER
    # =========================================================================
    w4 = window_fade(t, t_s4_lens - 0.04, t_s5_wheel + 0.02, fi=0.26, fo=0.28)
    if w4 > 0.01:
        stx = []
        p4 = ease_out_cubic(clamp((t - t_s4_lens) / 0.55))
        u4 = clamp((t - t_s4_lens) / max(1.2, t_s5_wheel - t_s4_lens))
        whip_out4 = clamp((t - (t_s5_wheel - 0.26)) / 0.28) ** 2 * 0.08
        cam_z4 = 0.93 + 0.07 * p4 + 0.025 * u4 + whip_out4
        push_camera(cs, cg, zoom=cam_z4, px=540.0, py=805.0)

        draw_pill_badge(cs, cg, stx, "عینکِ «ساعتِ عمر» روی خریدهای روزمره", 540, 238, fonts.reg_26, w4 * p4)

        rows_data = [
            ("shoe",   500.0, "کفشِ ۶ میلیونی",           "۶۰ ساعت کارِ خالص!",   clamp((t - (t_s4_shoe - 0.45)) / 0.50)),
            ("dinner", 755.0, "شامِ پرزرق‌وبرقِ ۲ میلیونی", "۲۰ ساعت از آزادیت!",   clamp((t - (t_s4_din - 0.45)) / 0.50)),
            ("phone", 1010.0, "ارتقای نمایشیِ گوشی",      "۷۵ روز حبسِ کاری!",    clamp((t - (t_s4_din + 0.15)) / 0.55)),
        ]

        # Smooth X-ray horizontal scanline sweeping down across the 3 everyday cards
        beam_y = 390.0 + ease_in_out_cubic(clamp(u4 * 1.12)) * 735.0

        for idx_r, (ic_kind, ry_c, title_r, real_tag, rev_u) in enumerate(rows_data):
            rp = ease_out_cubic(clamp((t - (t_s4_lens + idx_r * 0.22)) / 0.55))
            act_r = ease_out_cubic(max(rev_u, clamp((beam_y - (ry_c - 65.0)) / 120.0)))
            if rp <= 0.02:
                continue

            # Outer row card (w=860, h=195)
            cs.save(); cg.save(); cs.set_dash([]); cg.set_dash([])
            rounded_rect_path(cs, 540 - 430, ry_c - 96, 860, 192, 18)
            cs.set_source_rgba(0.035, 0.035, 0.048, 0.92 * w4 * rp); cs.fill_preserve()
            cs.set_source_rgba(1, 1, 1, (0.28 + 0.62 * act_r) * w4 * rp); cs.set_line_width(2.2); cs.stroke()
            if act_r > 0.25:
                rounded_rect_path(cg, 540 - 430, ry_c - 96, 860, 192, 18)
                cg.set_source_rgba(1, 1, 1, 0.36 * act_r * w4); cg.set_line_width(4.4); cg.stroke()
            cs.restore(); cg.restore()

            # Right side: bespoke animated icon (x=885) + title centered in right zone (x=665)
            draw_mini_everyday_icon(cs, cg, ic_kind, 888, ry_c, t, alpha=w4 * rp, active=act_r)
            sp_rt = get_fitted_text_sprite(title_r, fonts.bold_30, 310, (238, 238, 248, 255))
            stx.append((sp_rt, 655, ry_c, w4 * rp))

            # Left side (x=285): X-Ray revealed Life-Hours Pill Badge!
            draw_safe_card(
                cs, cg, stx, 285, ry_c, 310, 108,
                [
                    ("قیمت به عمر:", fonts.light_22, -24, (195, 195, 208, 255), 0.0),
                    (real_tag, fonts.bold_30, 22, (255, 255, 255, 255), 0.72 * act_r),
                ],
                radius=14, pad_x=22, alpha=w4 * rp * (0.28 + 0.72 * act_r),
                glow_border=(act_r > 0.35), allow_expand=False
            )

        # Glowing X-ray laser line + side reticles
        if 395.0 < beam_y < 1120.0:
            draw_glow_line(cs, cg, 92, beam_y, 988, beam_y, w4 * 0.82, lw_s=2.0, lw_g=5.8)
            cs.arc(92, beam_y, 4.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.95 * w4); cs.fill()
            cs.arc(988, beam_y, 4.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.95 * w4); cs.fill()

        draw_pill_badge(cs, cg, stx, "هر خرید = تکه‌ای از آزادیت که معامله می‌کنی!", 540, 1225, fonts.reg_26, w4 * p4, glow=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cam_z4, px=540.0, py=805.0)

    # =========================================================================
    # SCENE 5 (t_s5_wheel .. t_s6_rule): GIANT CLOCKWORK WHEEL + RUNNING HUMAN!
    # =========================================================================
    w5 = window_fade(t, t_s5_wheel - 0.04, t_s6_rule + 0.02, fi=0.26, fo=0.28)
    if w5 > 0.01:
        stx = []
        p5 = ease_out_cubic(clamp((t - t_s5_wheel) / 0.55))
        own_p = ease_out_cubic(clamp((t - (t_s5_own - 0.25)) / 0.65))
        u5 = clamp((t - t_s5_wheel) / max(1.2, t_s6_rule - t_s5_wheel))
        whip_out5 = clamp((t - (t_s6_rule - 0.26)) / 0.28) ** 2 * 0.08

        cam_z5 = (0.93 + 0.07 * p5 + 0.038 * u5 + whip_out5
                  + impact_punch(t, t_s5_own, amp=0.036, dur=0.65))
        push_camera(cs, cg, zoom=cam_z5, px=540.0, py=775.0)

        draw_pill_badge(cs, cg, stx, "تله‌ی چشم‌وهم‌چشمی: چرخ‌دنده‌ی بی‌پایان", 540, 238, fonts.reg_26, w5 * p5)

        # Giant Meshing Clockwork Wheel at (540, 725, r=265) + Secondary upper-right gear!
        w_cx, w_cy, w_r = 540.0, 725.0, 265.0
        rot_main = t * 0.62
        draw_clock_gear(cs, cg, 815, 495, 92.0, 12, -rot_main * (24.0 / 12.0) + 0.18, alpha=w5 * p5 * 0.48, glow=False)
        draw_clock_gear(cs, cg, w_cx, w_cy, w_r, 24, rot_main, alpha=w5 * p5, glow=True)
        draw_hypnotic_chronograph_ring(cs, cg, w_cx, w_cy, w_r * 0.78, t, alpha=w5 * p5 * 0.55, draw_p=p5, speed=2.2)

        # Articulated 60fps Human Running cleanly on the inner rim track of the spinning Clock-Wheel!
        wrist_pt = draw_running_human_60fps(cs, cg, 575, w_cy + w_r * 0.61, scale=1.08, t=t, alpha=w5 * p5, facing_left=True)

        # Dangling Glowing Smartphone ahead on left rim (325, 685) + Glowing Clock-Chain tether to wrist!
        ph_x, ph_y = 335.0, 675.0 + math.sin(t * 3.2) * 8.0
        draw_flagship_phone(cs, cg, ph_x, ph_y, 76, 138, alpha=w5 * p5, draw_p=p5, glow=True)

        if wrist_pt is not None:
            wx, wy = wrist_pt
            # Taut glowing chain of 9 oval links from smartphone to runner's wrist!
            n_links = 9
            cs.save(); cg.save(); cs.set_dash([]); cg.set_dash([])
            for li in range(n_links + 1):
                lu = li / n_links
                lx_c = ph_x + 36 + (wx - (ph_x + 36)) * lu
                ly_c = ph_y + 10 + (wy - (ph_y + 10)) * lu + math.sin(math.pi * lu) * 18.0
                cs.arc(lx_c, ly_c, 4.8, 0, 2 * math.pi)
                cs.set_source_rgba(1, 1, 1, (0.55 + 0.42 * own_p) * w5); cs.set_line_width(2.0); cs.stroke()
                if own_p > 0.1:
                    cg.arc(lx_c, ly_c, 7.5, 0, 2 * math.pi)
                    cg.set_source_rgba(1, 1, 1, 0.48 * own_p * w5); cg.fill()
            cs.restore(); cg.restore()

        # Peeling calendar pages flying off behind the runner into darkness!
        for pg_i in range(5):
            pu = ((t * 0.72 + pg_i / 5.0) % 1.0)
            px_p = 640.0 + pu * 240.0
            py_p = 835.0 - pu * 135.0 + math.sin(pu * 6.0 + pg_i) * 16.0
            pa = math.sin(math.pi * pu) * 0.75 * w5 * p5
            cs.save(); cs.set_dash([])
            cs.translate(px_p, py_p)
            cs.rotate(pu * 1.1 + pg_i * 0.4)
            rounded_rect_path(cs, -16, -20, 32, 40, 4)
            cs.set_source_rgba(1, 1, 1, pa); cs.set_line_width(1.6); cs.stroke()
            cs.move_to(-16, -10); cs.line_to(16, -10); cs.stroke()
            cs.restore()

        # Bottom punchline card (540, 1185, w=860, h=180)
        draw_safe_card(
            cs, cg, stx, 540, 1185, 860, 180,
            [
                ("دیگه تو صاحبِ وسایلت نیستی؛", fonts.reg_26, -38, (205, 205, 218, 255), 0.15),
                ("اون وسایل صاحبِ عمر و زندگیِ توئن!", fonts.bold_36, 30, (255, 255, 255, 255), 0.82 * max(0.35, own_p)),
            ],
            radius=18, pad_x=30, alpha=w5 * p5, glow_border=(own_p > 0.2), allow_expand=False
        )

        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cam_z5, px=540.0, py=775.0)

    # =========================================================================
    # SCENE 6 (t_s6_rule .. t_s7_cta): 3-SECOND LIBERATION FILTER & CHAIN BREAK!
    # =========================================================================
    w6 = window_fade(t, t_s6_rule - 0.04, t_s7_cta + 0.02, fi=0.26, fo=0.28)
    if w6 > 0.01:
        stx = []
        p6 = ease_out_cubic(clamp((t - t_s6_rule) / 0.55))
        free_p = ease_out_cubic(clamp((t - (t_s6_worth - 0.15)) / 0.65))
        shat_u = clamp((t - (t_s6_worth - 0.08)) / 0.85) if t >= (t_s6_worth - 0.08) else 0.0
        whip_out6 = clamp((t - (t_s7_cta - 0.26)) / 0.28) ** 2 * 0.08

        cam_z6 = (0.93 + 0.07 * p6 + whip_out6
                  + impact_punch(t, t_s6_worth, amp=0.036, dur=0.60))
        push_camera(cs, cg, zoom=cam_z6, px=540.0, py=805.0)

        draw_pill_badge(cs, cg, stx, "پادزهرِ ۳ ثانیه‌ای قبل از کشیدنِ کارت", 540, 238, fonts.reg_26, w6 * p6)

        draw_safe_card(
            cs, cg, stx, 540, 405, 860, 130,
            [
                ("قیمتِ جنس  ÷  درآمدِ ۱ ساعتت  =  چند ساعت از عمرم؟", fonts.bold_30, 0, (250, 250, 255, 255), 0.45),
            ],
            radius=16, pad_x=28, alpha=w6 * p6, glow_border=False, allow_expand=False
        )

        # Right Portal: Impulse Object (dims when chain shatters!)
        dim_imp = 1.0 - 0.58 * free_p
        draw_safe_card(
            cs, cg, stx, 765, 785, 345, 415,
            [
                ("گزینه‌ی اول", fonts.light_22, -145, (180, 180, 192, 255), 0.0),
                ("خریدِ هیجانی", fonts.bold_36, -60, (215, 215, 225, 255), 0.0),
                ("ذوقِ ۲ روزه", fonts.reg_26, 35, (175, 175, 188, 255), 0.0),
                ("و ماه‌ها اضافه‌کاری!", fonts.light_22, 120, (165, 165, 178, 255), 0.0),
            ],
            radius=18, pad_x=26, alpha=w6 * p6 * dim_imp, allow_expand=False
        )

        # Left Portal: Your Free Life-Days (illuminates with OLED halo + human standing free!)
        draw_safe_card(
            cs, cg, stx, 315, 785, 355, 415,
            [
                ("گزینه‌ی دوم", fonts.light_22, -145, (220, 220, 235, 255), 0.2 * free_p),
                ("نگه داشتنِ عمرت!", fonts.bold_36, -82, (255, 255, 255, 255), 0.8 * free_p),
                ("آرامش و آزادیِ واقعی", fonts.reg_26, 145, (245, 245, 252, 255), 0.45 * free_p),
            ],
            radius=18, pad_x=26, alpha=w6 * p6, glow_border=(free_p > 0.15), allow_expand=False
        )
        draw_human_figure(cs, 315, 868, scale=0.72, alpha=w6 * p6 * (0.45 + 0.55 * free_p), star_mind=(free_p > 0.2))
        draw_human_figure(cg, 315, 868, scale=0.72, alpha=w6 * p6 * 0.38 * free_p, lw=4.5, star_mind=(free_p > 0.2))
        if free_p > 0.15:
            draw_star4(cs, 180, 625, 14 * free_p, w6); draw_star4(cg, 180, 625, 22 * free_p, w6 * 0.8)
            draw_star4(cs, 450, 625, 14 * free_p, w6); draw_star4(cg, 450, 625, 22 * free_p, w6 * 0.8)

        # Center chain shatter + cursor click choosing Freedom!
        if 0.01 < shat_u < 0.99:
            draw_shockwave_ring(cs, cg, 540, 785, shat_u, max_r=260.0, alpha=w6)
            for bi in range(16):
                ang_b = bi * (2 * math.pi / 16.0) + 0.2
                rr_b = 18.0 + ease_out_cubic(shat_u) * 145.0
                bx_b = 540 + math.cos(ang_b) * rr_b
                by_b = 785 + math.sin(ang_b) * rr_b
                ba = (1.0 - shat_u) * w6
                cs.arc(bx_b, by_b, 3.4, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, ba); cs.fill()
                cg.arc(bx_b, by_b, 7.0, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, ba * 0.6); cg.fill()

        cur_u6 = ease_in_out_cubic(clamp((t - (t_s6_rule + 0.4)) / max(0.6, (t_s6_worth - t_s6_rule))))
        cx6 = 740.0 + (335.0 - 740.0) * cur_u6
        cy6 = 825.0 - math.sin(math.pi * cur_u6) * 48.0
        draw_cursor_pointer(cs, cg, cx6, cy6, click_p=shat_u, alpha=w6 * p6, scale=1.12)

        draw_pill_badge(
            cs, cg, stx, "اگه به اون‌همه زندگی نمی‌ارزه، نخر و آزاد بمون!",
            540, 1175, fonts.bold_30, w6 * max(0.35, free_p), glow=True
        )
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cam_z6, px=540.0, py=805.0)

    # =========================================================================
    # SCENE 7 (t_s7_cta .. outro_t0): INTERACTIVE 3-CHOICE COMMENT TRIGGER!
    # =========================================================================
    w7 = window_fade(t, t_s7_cta - 0.10, outro_t0 + 0.10, fi=0.35, fo=0.42)
    if w7 > 0.01:
        stx = []
        p7 = ease_out_cubic(clamp((t - t_s7_cta) / 0.55))
        cam_z7 = 0.98 + 0.025 * p7
        push_camera(cs, cg, zoom=cam_z7, px=540.0, py=805.0)

        draw_pill_badge(cs, cg, stx, "همین الان گوشیِ توی دستت رو حساب کن!", 540, 245, fonts.reg_26, w7 * p7)

        opts = [
            (495.0, "۱.  کمتر از ۱ ماه از عمرم پاش رفته"),
            (690.0, "۲.  بین ۱ تا ۳ ماهِ کامل براش کار کردم"),
            (885.0, "۳.  بیشتر از ۳ ماه از عمرم پاش رفته!"),
        ]
        cyc = ((t - t_s7_cta) * 1.45) % 3.0
        for oi, (oy, otxt) in enumerate(opts):
            op = ease_out_cubic(clamp((t - (t_s7_cta + oi * 0.16)) / 0.45))
            hi = math.exp(-((cyc - oi) ** 2) / 0.30)
            if op > 0.02:
                draw_safe_card(
                    cs, cg, stx, 540, oy, 850, 138,
                    [(otxt, fonts.bold_30, 0, (255, 255, 255, 255), 0.30 + 0.55 * hi)],
                    radius=18, pad_x=32, alpha=w7 * op, glow_border=(hi > 0.50), allow_expand=False
                )

        # Gliding cursor inviting viewer tap
        cur_y7 = 495.0 + ease_in_out_cubic(clamp(((t - t_s7_cta) % 2.4) / 2.0)) * 390.0
        draw_cursor_pointer(cs, cg, 175, cur_y7 + 18, click_p=0.0, alpha=w7 * p7 * 0.85, scale=1.05)

        draw_pill_badge(cs, cg, stx, "عددش رو توی کامنت بنویس: ۱، ۲ یا ۳؟", 540, 1145, fonts.bold_30, w7 * p7, glow=True)
        pop_camera_and_transform_texts(cs, cg, stx, txts, zoom=cam_z7, px=540.0, py=805.0)

    # =========================================================================
    # SCENE 8 (outro_t0 .. total_dur): SIGNATURE OLED ENDPLATE (@zavieh.penhann)
    # =========================================================================
    w9 = window_fade(t, outro_t0 - 0.15, total_dur + 0.5, fi=0.45, fo=0.55)
    if w9 > 0.01:
        lt = max(0.0, t - outro_t0)
        p_logo = ease_out_cubic(clamp(lt / 1.05))

        cx, cy = 540.0, 725.0
        # Hypnotic timepiece halo gently framing the signature Mind-Aperture!
        draw_hypnotic_chronograph_ring(cs, cg, cx, cy, 228.0, t, alpha=w9 * p_logo * 0.36, draw_p=p_logo, speed=0.65)

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
# Multiprocessing 60fps Cloud Renderer + Automated 12-Panel QA Sheets
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
    """Generates automated subtitle baseline QA strip + 12-panel full-episode storyboard."""
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    sg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cg = cairo.Context(sg)
    ss = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cs = cairo.Context(ss)

    # 1. Subtitle Baseline Stability & Liquid Wipe Strip (14 frames across 75-day reveal!)
    sub_strip = Image.new("RGB", (920, 14 * 105), (0, 0, 0))
    test_ln = meta["sub_lines"][min(15, len(meta["sub_lines"]) - 1)]
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

    # 2. 12-Scene Full Storyboard Sheet across all 8 scenes & transitions
    tc = meta["t_cues"]
    td = meta["total_dur"]
    sample_ts = [
        tc["s1_price"] + 0.35,                  # P1: Retail smartphone price screen + chronograph halo
        tc["s1_secret"] + 0.90,                 # P2: X-ray hourglass inside phone + human life-sparks!
        tc["s1_600"] + 0.55,                    # P3: 3D-flipped "۶۰۰ ساعت از عمرت!" + shockwave
        tc["s2_life"] + 0.95,                   # P4: Astronomical Balance Scale + live PQRST ECG lifeline
        tc["s3_rate"] + 0.65,                   # P5: HUD Calculator + Domino Calendar igniting mid-wave!
        tc["s3_season"] + 0.50,                 # P6: Full 75-day matrix lit + "کل یه فصل از جوونیت!"
        tc["s4_shoe"] + 0.25,                   # P7: X-ray laser sweeping mid-way across Everyday tags
        0.5 * (tc["s4_din"] + tc["s5_wheel"]),  # P8: All 3 Everyday Life-Tags illuminated cleanly!
        tc["s5_own"] + 0.55,                    # P9: Giant Clockwork Gear Wheel + Running Human + Tethered Phone!
        tc["s6_worth"] + 0.30,                  # P10: 3-Second Filter + Chain Shatter Burst + Freedom Portal!
        tc["s7_cta"] + 1.15,                    # P11: Interactive 1 / 2 / 3 Self-Calculation CTA
        td - 1.5,                               # P12: Signature OLED Endplate (@zavieh.penhann)
    ]
    pw, ph = 360, 640
    grid = Image.new("RGB", (pw * 4, ph * 3), (18, 18, 22))
    for idx_p, ts in enumerate(sample_ts):
        ts_c = max(0.05, min(td - 0.05, ts))
        raw = render_scene_frame(ts_c, td, tc, meta["sub_lines"], fonts, sg, cg, ss, cs)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw, ph), Image.Resampling.LANCZOS)
        r, c = divmod(idx_p, 4)
        grid.paste(im, (c * pw, r * ph))
    grid.save(os.path.join(qa_dir, "storyboard_12_scenes.png"))


def run_cloud_render(font_dir: str, work_dir: str, out_mp4: str, qa_dir: str, whisper_size: str = "medium"):
    import multiprocessing as mp
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(qa_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)

    print("=== [1/3] Building Studio v3.0 Master Audio (Locked Rasalgethi + Hypnotic D-Minor Horology Score) ===", flush=True)
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
    print(f"=== [2/3] Rendering {total_frames} frames @ {W}x{H} {FPS}fps on {workers} CPU cores (CRF 14) ===", flush=True)

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

    print("=== [3/3] Generating QA Verification Sheets & Alignment Report ===", flush=True)
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
