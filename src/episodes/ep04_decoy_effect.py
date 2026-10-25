"""
Episode 04 — The Decoy Effect / Middle-Number Trap (تله‌ی عددِ وسط / اثرِ طعمه در قیمت‌گذاری)
Page: زاویه ذهن (@zavieh.penhann)
Engine v2.3 (Elevated 60fps Kinetic Motion):
  - Locked Voice: Gemini 'Rasalgethi' + 129-tap @ensan.besham FIR + -0.34st Formant Calibration
  - Music: Dark-Cinematic Evolving Minor Score (Am9 -> Fmaj7 -> Dm9 -> Em7) + Felt Piano + Hall Reverb
  - Kinetic Upgrades: Animated rising cafe steam, pendulum fishing hook, Bezier cursor & sonar clicks,
    parabolic money-flight particles, live 32%->84% swarm migration, X-ray industry scanner & shattering decoy!
  - Subtitles & Boxes: 0.000px baseline-locked 64px-feathered RTL wipe + 100% Zero-Overflow containers.
"""
import os, sys, math, time, subprocess
import cairocffi as cairo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.engine.audio_master import build_episode_audio, LOCKED_SIGNATURE_VOICE
from src.engine.render_core import (
    W, H, FPS, fa, clamp, ease_out_cubic, ease_in_out_cubic, spring_pop, window_fade,
    FontBank, get_text_sprite, get_fitted_text_sprite, set_stroke_draw, rounded_rect_path,
    draw_star4, draw_stipple_line, draw_human_figure, draw_pill_badge, draw_folder_window,
    draw_stamp_badge, draw_safe_card, draw_spotlight_cone, draw_ambient_particles,
    draw_curved_arrow, draw_cursor_pointer, draw_hud_chrome, composite_oled_frame
)

EP_CODE = "04"
EP_TITLE = "تله‌ی عددِ وسط"

# 30 short, punchy, crystal-clear colloquial Tehrani phrases (4-7 words each)
SCRIPT_SEGMENTS = [
    ("تا حالا دقت کردی توی کافه‌ها،",                  "تا حالا دقت کردی توی کافه‌ها،"),
    ("چرا قهوه‌ی سایزِ متوسط،",                       "چرا قهوه‌ی سایز متوسط،"),
    ("فقط پونزده تومن با بزرگه فرق داره؟",             "فقط ۱۵ تومن با بزرگه فرق داره؟"),
    ("اون سایزِ متوسط برای فروش نیست؛",                "اون سایز متوسط برای فروش نیست؛"),
    ("فقط یه طعمه‌ست برای جیبِ تو!",                   "فقط یه طعمه‌ست برای جیب تو!"),
    ("بیا بدونِ طعمه امتحانش کنیم:",                  "بیا بدون طعمه امتحانش کنیم:"),
    ("اگه منو فقط دو تا سایز داشت،",                  "اگه منو فقط ۲ تا سایز داشت،"),
    ("کوچیک نود تومن و بزرگ صد و پنجاه،",             "کوچیک ۹۰ تومن و بزرگ ۱۵۰،"),
    ("اکثرِ ما همون نود تومنی رو می‌خریدیم!",          "اکثر ما همون ۹۰ تومنی رو می‌خریدیم!"),
    ("حالا کافه میاد وسطِ این دو تا،",                 "حالا کافه میاد وسط این ۲ تا،"),
    ("یه متوسطِ صد و سی و پنجی می‌ذاره!",              "یه متوسط ۱۳۵ تومنی می‌ذاره!"),
    ("مغزت فوری نود تومنی رو یادش می‌ره؛",             "مغزت فوری ۹۰ تومنی رو یادش می‌ره؛"),
    ("می‌گه پونزده تومن می‌ذارم بزرگش رو می‌خرم!",      "می‌گه ۱۵ تومن می‌ذارم بزرگش رو می‌خرم!"),
    ("تو حس می‌کنی زرنگ‌بازی درآوردی،",                "تو حس می‌کنی زرنگ‌بازی درآوردی،"),
    ("ولی شصت تومن بیشتر خرج کردی!",                  "ولی ۶۰ تومن بیشتر خرج کردی!"),
    ("توی اقتصاد به این حقه می‌گن:",                  "توی اقتصاد به این حقه می‌گن:"),
    ("اثرِ طعمه، یا تله‌ی عددِ وسط!",                   "اثر طعمه، یا تله‌ی عدد وسط!"),
    ("توی یه آزمایشِ معروفِ دانشگاهی،",                "توی یه آزمایش معروف دانشگاهی،"),
    ("وقتی فقط دو تا بسته جلوی مردم بود،",            "وقتی فقط ۲ تا بسته جلوی مردم بود،"),
    ("فقط سی و دو درصد گرونه رو خریدن؛",              "فقط ۳۲ درصد گرونه رو خریدن؛"),
    ("اما به محضِ ورودِ گزینه‌ی طعمه،",                 "اما به محض ورود گزینه‌ی طعمه،"),
    ("صفر درصد طعمه رو خریدن،",                       "۰ درصد طعمه رو خریدن،"),
    ("ولی خریدِ گرونه پرید روی هشتاد و چهار درصد!",    "ولی خرید گرونه پرید روی ۸۴ درصد!"),
    ("از پاپ‌کورنِ سینما و حافظه‌ی گوشی،",             "از پاپ‌کورن سینما و حافظه‌ی گوشی،"),
    ("تا بسته‌های اینترنت و اشتراکِ سایت‌ها،",          "تا بسته‌های اینترنت و اشتراک سایت‌ها،"),
    ("همه‌جا گزینه‌ی وسط فقط یه طعمه‌ست!",              "همه‌جا گزینه‌ی وسط فقط یه طعمه‌ست!"),
    ("راهِ فرارش خیلی ساده‌ست:",                       "راه فرارش خیلی ساده‌ست:"),
    ("هر وقت بینِ سه تا قیمت موندی،",                 "هر وقت بین ۳ تا قیمت موندی،"),
    ("انگشتت رو بذار روی وسطی و حذفش کن!",            "انگشتت رو بذار روی وسطی و حذفش کن!"),
    ("آخرین بار کجا تو این تله افتادی؟",              "آخرین بار کجا تو این تله افتادی؟"),
]

SFX_CUE_MAP = [
    ("s1_diff",   2, 1, "ping"),    # ۱۵ تومن
    ("s1_hook",   4, 2, "stamp"),   # طعمه‌ست
    ("s2_two",    5, 0, "whoosh"),  # بیا بدون طعمه
    ("s2_pick90", 8, 3, "click"),   # ۹۰ تومنی رو می‌خریدیم
    ("s3_trap",   9, 0, "whoosh"),  # حالا کافه میاد وسط
    ("s3_drop135",10,2, "ping"),    # ۱۳۵ تومنی
    ("s3_pick150",12,4, "click"),   # بزرگش رو می‌خرم
    ("s4_wallet", 13,0, "whoosh"),  # تو حس می‌کنی
    ("s4_term",   16,0, "ping"),    # اثر طعمه
    ("s5_exp",    17,0, "whoosh"),  # توی یه آزمایش معروف
    ("s5_surge",  20,2, "ping"),    # ورود گزینه‌ی طعمه
    ("s5_84",     22,4, "stamp"),   # ۸۴ درصد
    ("s6_every",  23,0, "whoosh"),  # از پاپ‌کورن سینما
    ("s7_hack",   26,0, "whoosh"),  # راه فرارش
    ("s7_del",    28,5, "click"),   # حذفش کن
    ("s8_cta",    29,0, "chime"),   # آخرین بار کجا
]


def apply_camera(ctx, zoom: float, pan_x: float = 0.0, pan_y: float = 0.0):
    ctx.translate(W * 0.5 + pan_x, H * 0.48 + pan_y)
    ctx.scale(zoom, zoom)
    ctx.translate(-W * 0.5, -H * 0.48)


def draw_coffee_cup(
    cs, cg, cx: float, base_y: float, top_w: float, h: float,
    alpha: float = 1.0, draw_p: float = 1.0, t: float = 0.0, steam: bool = True, glow: bool = False
):
    """
    Architectural cafe cup with tapered body, ribbed heat-sleeve, dome lid, and 60fps rising S-curve steam!
    Origin (cx, base_y) is bottom center of cup on counter.
    """
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    bot_w = top_w * 0.70
    y_top = base_y - h

    layers = [(cs, 2.3, alpha * 0.94)]
    if glow:
        layers.append((cg, 5.2, alpha * 0.58))

    for ctx, lw, al in layers:
        ctx.save()
        set_stroke_draw(ctx, draw_p, (top_w + h) * 3.0)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)

        # Tapered cup walls
        ctx.move_to(cx - top_w * 0.5, y_top)
        ctx.line_to(cx - bot_w * 0.5, base_y)
        ctx.line_to(cx + bot_w * 0.5, base_y)
        ctx.line_to(cx + top_w * 0.5, y_top)
        ctx.close_path()
        if ctx is cs:
            ctx.set_source_rgba(0.03, 0.03, 0.04, 0.92 * alpha)
            ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al)
        ctx.stroke()

        # Cardboard grip sleeve (middle 38%..68% height)
        sl_y0 = base_y - h * 0.66
        sl_y1 = base_y - h * 0.34
        w0 = bot_w + (top_w - bot_w) * 0.66
        w1 = bot_w + (top_w - bot_w) * 0.34
        ctx.move_to(cx - w0 * 0.5, sl_y0); ctx.line_to(cx + w0 * 0.5, sl_y0); ctx.stroke()
        ctx.move_to(cx - w1 * 0.5, sl_y1); ctx.line_to(cx + w1 * 0.5, sl_y1); ctx.stroke()

        # Raised barista lid rim + dome
        rim_w = top_w * 1.08
        ctx.rectangle(cx - rim_w * 0.5, y_top - 12, rim_w, 12)
        ctx.stroke()
        ctx.move_to(cx - top_w * 0.44, y_top - 12)
        ctx.line_to(cx - top_w * 0.34, y_top - 26)
        ctx.line_to(cx + top_w * 0.34, y_top - 26)
        ctx.line_to(cx + top_w * 0.44, y_top - 12)
        ctx.stroke()
        ctx.set_dash([])
        ctx.restore()

    # 3 Animated 60fps rising sine-wave steam plumes!
    if steam and draw_p > 0.6:
        st_a = clamp((draw_p - 0.6) * 2.5) * alpha * 0.46
        cs.save()
        cs.set_dash([])
        cs.set_line_width(1.7)
        for si, x_off in enumerate((-top_w * 0.20, 0.0, top_w * 0.20)):
            cs.set_source_rgba(1, 1, 1, st_a * (0.7 + 0.3 * math.sin(t * 2.5 + si)))
            for step in range(15):
                u = step / 14.0
                sy = (y_top - 36) - u * 54.0
                sx = cx + x_off + math.sin(u * 5.2 - t * 4.6 + si * 2.1) * 7.5
                if step == 0:
                    cs.move_to(sx, sy)
                else:
                    cs.line_to(sx, sy)
            cs.stroke()
        cs.restore()


def draw_fishing_hook(cs, cg, anchor_x: float, top_y: float, tip_y: float, swing_rad: float, alpha: float = 1.0):
    """Animated pendulum fishing line & curved barbed hook catching the decoy!"""
    if alpha <= 0.01:
        return
    L = max(20.0, tip_y - top_y)
    for ctx, lw, al in ((cs, 2.5, alpha * 0.96), (cg, 5.2, alpha * 0.55)):
        ctx.save()
        ctx.set_dash([])
        ctx.translate(anchor_x, top_y)
        ctx.rotate(swing_rad)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        # Taut line
        ctx.move_to(0, 0); ctx.line_to(0, L - 36); ctx.stroke()
        # Hook eyelet
        ctx.arc(0, L - 30, 6, 0, 2 * math.pi); ctx.stroke()
        # J-Hook curve + sharp barb
        ctx.move_to(0, L - 24)
        ctx.line_to(0, L - 4)
        ctx.arc(-16, L - 4, 16, 0, math.pi)
        ctx.line_to(-32, L - 16)
        ctx.stroke()
        ctx.move_to(-32, L - 16); ctx.line_to(-24, L - 10); ctx.stroke()
        ctx.restore()


def draw_popcorn_bucket(cs, cg, cx: float, base_y: float, w: float, h: float, alpha: float, t: float):
    """Animated cinema popcorn bucket with 60fps bobbing kernels & vertical stripes!"""
    if alpha <= 0.01:
        return
    y_top = base_y - h
    bw = w * 0.72
    cs.save(); cs.set_dash([])
    # Popping kernels along rim
    for ki in range(6):
        kx = cx - w * 0.36 + ki * (w * 0.145)
        ky = y_top - 6 - abs(math.sin(t * 5.2 + ki * 1.1)) * 11.0
        cs.arc(kx, ky, 11.0, 0, 2 * math.pi)
        cs.set_source_rgba(0.03, 0.03, 0.04, 0.95 * alpha); cs.fill_preserve()
        cs.set_source_rgba(1, 1, 1, 0.88 * alpha); cs.set_line_width(1.9); cs.stroke()

    # Tapered bucket + vertical stripes
    cs.move_to(cx - w * 0.5, y_top); cs.line_to(cx - bw * 0.5, base_y)
    cs.line_to(cx + bw * 0.5, base_y); cs.line_to(cx + w * 0.5, y_top); cs.close_path()
    cs.set_source_rgba(0.03, 0.03, 0.04, 0.94 * alpha); cs.fill_preserve()
    cs.set_source_rgba(1, 1, 1, 0.92 * alpha); cs.set_line_width(2.2); cs.stroke()
    for s_frac in (-0.22, 0.0, 0.22):
        cs.move_to(cx + w * s_frac, y_top); cs.line_to(cx + bw * s_frac, base_y)
        cs.set_source_rgba(1, 1, 1, 0.38 * alpha); cs.set_line_width(1.4); cs.stroke()
    cs.restore()


def render_scene_frame(
    t: float, total_dur: float, t_cues: dict, sub_lines: list[dict],
    fonts: FontBank, surf_glow, ctx_glow, surf_sharp, ctx_sharp
) -> bytes:
    for c in (ctx_glow, ctx_sharp):
        c.set_operator(cairo.OPERATOR_SOURCE)
        c.set_source_rgba(0, 0, 0, 0)
        c.paint()
        c.set_operator(cairo.OPERATOR_OVER)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)

    cs, cg = ctx_sharp, ctx_glow
    txts = []

    t_s2 = t_cues["s2_two"]
    t_s3 = t_cues["s3_trap"]
    t_s4 = t_cues["s4_wallet"]
    t_s5 = t_cues["s5_exp"]
    t_s6 = t_cues["s6_every"]
    t_s7 = t_cues["s7_hack"]
    t_s8 = t_cues["s8_cta"]
    t_endplate = total_dur - 3.9

    chapters = [0.0, t_s2, t_s3, t_s4, t_s5, t_s6, t_s7, t_s8]
    draw_ambient_particles(cs, t, alpha=0.85)
    draw_hud_chrome(cs, cg, txts, fonts, t, total_dur, EP_CODE, EP_TITLE, chapters)

    # =========================================================================
    # SCENE 1: Cafe Menu 3 Cups (۹۰ / ۱۳۵ / ۱۵۰) + Caliper Arc + Fishing Hook!
    # =========================================================================
    w1 = window_fade(t, 0.0, t_s2 + 0.22, fi=0.22, fo=0.35)
    if w1 > 0.01:
        u1 = clamp(t / max(0.1, t_s2))
        cs.save(); cg.save()
        apply_camera(cs, 1.0 + 0.045 * u1)
        apply_camera(cg, 1.0 + 0.045 * u1)

        draw_pill_badge(cs, cg, txts, "منویِ کافه — یک چیزِ عجیب بینِ قیمت‌ها!", 540, 365, fonts.bold_30, w1 * ease_out_cubic(t / 0.6), glow=True)

        counter_y = 1045.0
        cs.move_to(95, counter_y); cs.line_to(985, counter_y)
        cs.set_source_rgba(1, 1, 1, 0.42 * w1); cs.set_line_width(2.2); cs.stroke()

        # Hook animation at "فقط یه طعمه‌ست برای جیب تو!"
        t_hk = t_cues["s1_hook"]
        hk_p = spring_pop((t - (t_hk - 0.55)) / 0.65) if t >= (t_hk - 0.55) else 0.0
        mid_lift = 36.0 * hk_p

        # 3 Cups (RTL order: Right=Small 90, Center=Medium 135 Decoy, Left=Large 150)
        cups_s1 = [
            (825.0, 108.0, 155.0, "کوچیک", "۹۰ تومن", 0.0, False),
            (540.0, 134.0, 205.0, "متوسط", "۱۳۵ تومن", mid_lift, True),
            (255.0, 158.0, 255.0, "بزرگ",  "۱۵۰ تومن", 0.0, True),
        ]
        for ci, (cx_c, cw_c, ch_c, sz_lbl, pr_lbl, lift_y, gl_c) in enumerate(cups_s1):
            dp_c = ease_out_cubic((t - 0.14 * ci) / 0.65)
            draw_coffee_cup(cs, cg, cx_c, counter_y - lift_y, cw_c, ch_c, alpha=w1, draw_p=dp_c, t=t, steam=(lift_y < 5), glow=gl_c)
            draw_safe_card(
                cs, cg, txts, cx_c, 1155, 245, 132,
                [
                    (sz_lbl, fonts.reg_26, -28, (195, 195, 208, 255), 0.0),
                    (pr_lbl, fonts.bold_36, 28, (255, 255, 255, 255), 0.55 if gl_c else 0.0),
                ],
                radius=14, pad_x=24, alpha=w1 * dp_c, glow_border=gl_c, allow_expand=False
            )

        # Caliper comparison arc between 135 (540) and 150 (255) at s1_diff
        t_df = t_cues["s1_diff"]
        if t >= t_df - 0.45:
            ap = ease_out_cubic((t - (t_df - 0.45)) / 0.55)
            draw_curved_arrow(cs, 515, 765 - mid_lift, 280, 725, bend=-95, progress=ap, alpha=w1 * 0.92, lw=2.4)
            draw_curved_arrow(cg, 515, 765 - mid_lift, 280, 725, bend=-95, progress=ap, alpha=w1 * 0.55, lw=5.0)
            draw_pill_badge(cs, cg, txts, "فقط ۱۵ تومن فرق!", 385, 625, fonts.bold_30, w1 * ap, glow=True)

        # Pendulum Fishing Hook catching the middle cup!
        if hk_p > 0.02:
            dt_hk = max(0.0, t - (t_hk - 0.55))
            swing = math.sin(dt_hk * 5.5) * math.exp(-dt_hk * 1.8) * 0.08
            tip_y = (counter_y - 205.0 - 26.0 - mid_lift)
            draw_fishing_hook(cs, cg, 540.0, 415.0, tip_y, swing, alpha=w1 * clamp(hk_p * 1.5))
            draw_stamp_badge(cs, cg, txts, "طعمه‌ی منو!", 540, 925 - mid_lift, -9.0, fonts.bold_36, w1, hk_p)

        cs.restore(); cg.restore()

    # =========================================================================
    # SCENE 2: Without the Decoy — Honest 2-Cup Choice (۹۰ vs ۱۵۰ -> ۹۰ Wins!)
    # =========================================================================
    w2 = window_fade(t, t_s2 - 0.15, t_s3 + 0.22, fi=0.32, fo=0.35)
    if w2 > 0.01:
        lt = max(0.0, t - t_s2)
        p2 = ease_out_cubic(lt / 0.75)
        draw_pill_badge(cs, cg, txts, "آزمایشِ اول: منویِ صادقانه‌ی دوگزینه‌ای", 540, 380, fonts.bold_30, w2 * p2, glow=True)

        t_p90 = t_cues["s2_pick90"]
        sel90 = clamp((t - (t_p90 - 0.35)) / 0.55) if t >= (t_p90 - 0.35) else 0.0

        # Right Card: Small 90 Toman (Winner when no decoy!)
        draw_safe_card(
            cs, cg, txts, 765, 865, 380, 620,
            [
                ("سایزِ کوچیک", fonts.bold_36, -235, (255, 255, 255, 255), 0.5 * sel90),
                ("۹۰ هزار تومن", fonts.bold_44, 175, (255, 255, 255, 255), 0.75 * sel90),
                ("انتخابِ اکثرِ مردم", fonts.reg_26, 245, (215, 215, 228, 255), 0.3 * sel90),
            ],
            radius=20, pad_x=28, alpha=w2 * p2, glow_border=(sel90 > 0.2), allow_expand=False
        )
        draw_coffee_cup(cs, cg, 765, 965, 118, 175, alpha=w2 * p2, draw_p=p2, t=t, glow=(sel90 > 0.2))

        # Left Card: Large 150 Toman (Feels way too expensive: +60k jump!)
        dim150 = 1.0 - 0.45 * sel90
        draw_safe_card(
            cs, cg, txts, 315, 865, 380, 620,
            [
                ("سایزِ بزرگ", fonts.bold_36, -235, (210, 210, 220, 255), 0.0),
                ("۱۵۰ هزار تومن", fonts.bold_44, 175, (210, 210, 220, 255), 0.0),
                ("۶۰ تومن گرون‌تره!", fonts.reg_26, 245, (175, 175, 185, 255), 0.0),
            ],
            radius=20, pad_x=28, alpha=w2 * p2 * dim150, allow_expand=False
        )
        draw_coffee_cup(cs, cg, 315, 965, 158, 255, alpha=w2 * p2 * dim150, draw_p=p2, t=t, glow=False)

        # Animated Vector Cursor: inspects Left (315) -> glides smoothly to Right (765) & clicks!
        cur_u = ease_in_out_cubic(clamp((t - (t_s2 + 1.1)) / max(0.8, (t_p90 - t_s2 - 0.9))))
        cur_x = 335.0 + (785.0 - 335.0) * cur_u
        cur_y = 1045.0 - math.sin(math.pi * cur_u) * 85.0
        click_90 = clamp((t - (t_p90 - 0.15)) / 0.75) if t >= (t_p90 - 0.15) else 0.0
        draw_cursor_pointer(cs, cg, cur_x, cur_y, click_p=click_90, alpha=w2 * p2, scale=1.15)

        if sel90 > 0.15:
            draw_pill_badge(cs, cg, txts, "تصمیمِ منطقی: ۶۰ تومن تو جیبت موند!", 540, 1295, fonts.bold_30, w2 * sel90, glow=True)

    # =========================================================================
    # SCENE 3: Enter the ۱۳۵ Decoy — Brain Spotlight Shift & Snap to ۱۵۰!
    # =========================================================================
    w3 = window_fade(t, t_s3 - 0.15, t_s4 + 0.22, fi=0.32, fo=0.35)
    if w3 > 0.01:
        lt = max(0.0, t - t_s3)
        p3 = ease_out_cubic(lt / 0.65)

        t_d135 = t_cues["s3_drop135"]
        dec_p  = spring_pop((t - (t_d135 - 0.45)) / 0.55) if t >= (t_d135 - 0.45) else 0.0
        t_p150 = t_cues["s3_pick150"]
        win150 = clamp((t - (t_p150 - 0.35)) / 0.55) if t >= (t_p150 - 0.35) else 0.0

        # Observer Human Brain at top projecting narrow Spotlight Cone onto [135 & 150] ONLY!
        draw_human_figure(cs, 540, 560, scale=0.82, alpha=w3 * 0.95, draw_p=p3, star_mind=(win150 > 0.1), t=t)
        if dec_p > 0.2:
            draw_spotlight_cone(cs, cg, 540, 438, 115, 675, 1185, alpha=w3 * clamp(dec_p) * 0.95)

        # Right Card (90 Toman) — Fades into dark shadow once 135 drops! ("مغزت ۹۰ تومنی رو یادش می‌ره")
        dim_90 = 1.0 - 0.72 * clamp(dec_p)
        draw_safe_card(
            cs, cg, txts, 855, 945, 255, 510,
            [
                ("کوچیک", fonts.reg_26, -205, (185, 185, 195, 255), 0.0),
                ("۹۰ تومن", fonts.bold_36, 128, (195, 195, 205, 255), 0.0),
                ("فراموش شد!", fonts.light_22, 195, (160, 160, 170, 255), 0.0),
            ],
            radius=16, pad_x=24, alpha=w3 * p3 * dim_90, allow_expand=False
        )
        draw_coffee_cup(cs, cg, 855, 1005, 88, 125, alpha=w3 * p3 * dim_90, draw_p=p3, t=t, steam=False)

        # Center Card (135 Toman DECOY) — Slams down from above!
        if dec_p > 0.02:
            dy_drop = (1.0 - dec_p) * -180.0
            draw_safe_card(
                cs, cg, txts, 540, 945 + dy_drop, 275, 510,
                [
                    ("متوسط (طعمه)", fonts.bold_30, -205, (235, 235, 245, 255), 0.3),
                    ("۱۳۵ تومن", fonts.bold_36, 128, (245, 245, 252, 255), 0.4),
                    ("فقط برای مقایسه!", fonts.light_22, 195, (195, 195, 208, 255), 0.0),
                ],
                radius=16, pad_x=24, alpha=w3 * clamp(dec_p), glow_border=(win150 < 0.2), allow_expand=False
            )
            draw_coffee_cup(cs, cg, 540, 1005 + dy_drop, 110, 155, alpha=w3 * clamp(dec_p), draw_p=1.0, t=t, steam=False)

        # Left Card (150 Toman TARGET) — Lights up with victory stars at s3_pick150!
        draw_safe_card(
            cs, cg, txts, 225, 945, 275, 510,
            [
                ("بزرگ (هدفِ فروش)", fonts.bold_30, -205, (255, 255, 255, 255), 0.7 * win150),
                ("۱۵۰ تومن!", fonts.bold_44, 128, (255, 255, 255, 255), 0.85 * win150),
                ("فقط +۱۵ تومن!", fonts.reg_26, 198, (255, 255, 255, 255), 0.5 * win150),
            ],
            radius=16, pad_x=24, alpha=w3 * p3, glow_border=(win150 > 0.1), allow_expand=False
        )
        draw_coffee_cup(cs, cg, 225, 1005, 128, 182, alpha=w3 * p3, draw_p=p3, t=t, steam=False, glow=(win150 > 0.1))

        # Magnetic cursor glide from 540 (Decoy) -> 225 (Large 150 cup body) + Click!
        if dec_p > 0.4:
            mag_u = ease_in_out_cubic(clamp((t - (t_d135 + 0.35)) / max(0.6, (t_p150 - t_d135 - 0.2))))
            cx_m = 545.0 + (245.0 - 545.0) * mag_u
            cy_m = 935.0 - math.sin(math.pi * mag_u) * 55.0
            ck_150 = clamp((t - (t_p150 - 0.12)) / 0.75) if t >= (t_p150 - 0.12) else 0.0
            draw_cursor_pointer(cs, cg, cx_m, cy_m, click_p=ck_150, alpha=w3, scale=1.15)

        if win150 > 0.1:
            draw_star4(cs, 120, 715, 15 * win150, w3); draw_star4(cg, 120, 715, 24 * win150, w3 * 0.8)
            draw_star4(cs, 330, 715, 12 * win150, w3); draw_star4(cg, 330, 715, 20 * win150, w3 * 0.8)
            draw_pill_badge(cs, cg, txts, "مغزت گولِ «۱۵ تومن فاصله» رو خورد!", 540, 1305, fonts.bold_30, w3 * win150, glow=True)

    # =========================================================================
    # SCENE 4: Parabolic Money Flight (+۶۰ تومن) + Scientific Dossier Reveal
    # =========================================================================
    w4 = window_fade(t, t_s4 - 0.15, t_s5 + 0.22, fi=0.32, fo=0.35)
    if w4 > 0.01:
        lt = max(0.0, t - t_s4)
        p4 = ease_out_cubic(lt / 0.75)
        draw_pill_badge(cs, cg, txts, "پشتِ صحنه‌ی معامله: کی برنده شد؟", 540, 385, fonts.bold_30, w4 * p4, glow=True)

        # Right Box: Your Pocket (جیب تو) -> Left Box: Cafe Register (صندوق کافه)
        draw_safe_card(
            cs, cg, txts, 805, 685, 310, 230,
            [
                ("جیبِ تو", fonts.bold_36, -52, (215, 215, 225, 255), 0.0),
                ("-۶۰ هزار تومن", fonts.bold_36, 18, (255, 255, 255, 255), 0.35),
                ("خرجِ اضافه نسبت به ۹۰!", fonts.light_22, 74, (175, 175, 188, 255), 0.0),
            ],
            radius=16, pad_x=24, alpha=w4 * p4, allow_expand=False
        )
        draw_safe_card(
            cs, cg, txts, 275, 685, 310, 230,
            [
                ("صندوقِ فروشنده", fonts.bold_36, -52, (255, 255, 255, 255), 0.55),
                ("+۶۰ هزار تومن!", fonts.bold_36, 18, (255, 255, 255, 255), 0.8),
                ("سودِ خالص با یک عدد!", fonts.light_22, 74, (215, 215, 228, 255), 0.0),
            ],
            radius=16, pad_x=24, alpha=w4 * p4, glow_border=True, allow_expand=False
        )

        # 8 Parabolic 60fps glowing money orbs flying from Your Pocket (650, 650) -> Seller (430, 650)!
        draw_curved_arrow(cs, 645, 585, 435, 585, bend=-85, progress=p4, alpha=w4 * 0.65, lw=2.0)
        for oi in range(8):
            u_m = ((lt * 0.78 + oi / 8.0) % 1.0)
            mx = 650.0 + (430.0 - 650.0) * u_m
            my = 655.0 - math.sin(math.pi * u_m) * (115.0 + (oi % 3) * 18.0)
            ma = math.sin(math.pi * u_m) * w4
            cs.arc(mx, my, 6.0, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.95 * ma); cs.fill()
            cg.arc(mx, my, 12.0, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.80 * ma); cg.fill()

        # Bottom Hero Folder Window: Scientific Name "اثر طعمه / تله‌ی عدد وسط"
        t_tm4 = t_cues["s4_term"]
        if t >= t_tm4 - 1.1:
            dp4 = ease_out_cubic((t - (t_tm4 - 1.1)) / 0.8)
            draw_folder_window(cs, cg, txts, 540, 1135, 860, 355, "نامِ علمیِ این تکنیک", fonts.bold_30, w4, dp4)
            sp_d1 = get_fitted_text_sprite("اثرِ طعمه (تله‌ی عددِ وسط)", fonts.bold_52, 780, (255, 255, 255, 255), glow=0.85)
            sp_d2 = get_fitted_text_sprite("اضافه کردنِ یک گزینه‌ی بی‌مصرف، فقط برای هدایتِ مغز به گرون‌ترین انتخاب!", fonts.reg_26, 780, (200, 200, 212, 255))
            txts.append((sp_d1, 540, 1082, w4 * dp4))
            txts.append((sp_d2, 540, 1195, w4 * dp4))

    # =========================================================================
    # SCENE 5: Famous University Experiment — Live 32% -> 84% Swarm Migration!
    # =========================================================================
    w5 = window_fade(t, t_s5 - 0.15, t_s6 + 0.22, fi=0.32, fo=0.35)
    if w5 > 0.01:
        lt = max(0.0, t - t_s5)
        p5 = ease_out_cubic(lt / 0.8)

        t_srg = t_cues["s5_surge"]
        mig_u = ease_in_out_cubic(clamp((t - t_srg) / max(1.1, (t_cues["s5_84"] - t_srg + 0.5)))) if t >= t_srg else 0.0
        decoy_in = spring_pop((t - (t_srg - 0.35)) / 0.55) if t >= (t_srg - 0.35) else 0.0

        hdr_txt = "آزمایشِ دانشگاهی — مرحله ۱: بدونِ طعمه" if mig_u < 0.05 else "مرحله ۲: ورودِ طعمه و هجومِ ۸۴ درصدی!"
        draw_pill_badge(cs, cg, txts, hdr_txt, 540, 385, fonts.bold_30, w5 * p5, glow=True)

        floor_b = 1195.0
        max_bh  = 540.0
        cs.move_to(105, floor_b); cs.line_to(975, floor_b)
        cs.set_source_rgba(1, 1, 1, 0.45 * w5); cs.set_line_width(2.2); cs.stroke()

        # Live interpolated percentages: Cheap (68% -> 16%), Decoy (0%), Expensive (32% -> 84%!)
        pct_cheap = 68.0 - 52.0 * mig_u
        pct_exp   = 32.0 + 52.0 * mig_u

        # 1. Right Bar: Cheap Package (68% -> 16%)
        rx_b, bw_b = 815.0, 215.0
        h_ch = max_bh * (pct_cheap / 100.0) * p5
        rounded_rect_path(cs, rx_b - bw_b / 2, floor_b - h_ch, bw_b, max(12.0, h_ch), 12)
        cs.set_source_rgba(1, 1, 1, 0.12 * w5); cs.fill_preserve()
        cs.set_source_rgba(1, 1, 1, 0.55 * w5); cs.set_line_width(2.0); cs.stroke()
        sp_ch_p = get_fitted_text_sprite(f"{int(round(pct_cheap))}٪", fonts.bold_44, 190, (220, 220, 232, 255))
        sp_ch_l = get_fitted_text_sprite("بسته‌ی ارزون", fonts.reg_26, 210, (185, 185, 198, 255))
        txts.append((sp_ch_p, rx_b, floor_b - h_ch - 44, w5 * p5))
        txts.append((sp_ch_l, rx_b, floor_b + 44, w5 * p5))

        # 2. Center Bar: Decoy Package (0% bought!)
        if decoy_in > 0.02:
            mx_b = 540.0
            cs.set_dash([8, 7])
            rounded_rect_path(cs, mx_b - bw_b / 2, floor_b - 95 * decoy_in, bw_b, 95 * decoy_in, 12)
            cs.set_source_rgba(1, 1, 1, 0.48 * w5 * clamp(decoy_in)); cs.set_line_width(1.9); cs.stroke()
            cs.set_dash([])
            sp_dc_p = get_fitted_text_sprite("۰٪ خرید!", fonts.bold_36, 195, (235, 235, 245, 255), glow=0.35)
            sp_dc_l = get_fitted_text_sprite("گزینه‌ی طعمه", fonts.bold_30, 210, (220, 220, 232, 255))
            txts.append((sp_dc_p, mx_b, floor_b - 95 * decoy_in - 42, w5 * clamp(decoy_in)))
            txts.append((sp_dc_l, mx_b, floor_b + 44, w5 * clamp(decoy_in)))

        # 3. Left Bar: Expensive Package (32% -> 84% SKYROCKET!)
        lx_b = 265.0
        h_ex = max_bh * (pct_exp / 100.0) * p5
        for ctx, lw, al in ((cs, 2.8, w5 * 0.98), (cg, 6.0, w5 * (0.35 + 0.45 * mig_u))):
            rounded_rect_path(ctx, lx_b - bw_b / 2, floor_b - h_ex, bw_b, max(16.0, h_ex), 12)
            if ctx is cs:
                ctx.set_source_rgba(1, 1, 1, (0.14 + 0.14 * mig_u) * w5); ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        sp_ex_p = get_fitted_text_sprite(f"{int(round(pct_exp))}٪", fonts.eb_68, 200, (255, 255, 255, 255), glow=0.85 * mig_u)
        sp_ex_l = get_fitted_text_sprite("بسته‌ی گرون!", fonts.bold_30, 210, (255, 255, 255, 255), glow=0.45 * mig_u)
        txts.append((sp_ex_p, lx_b, floor_b - h_ex - 52, w5 * p5))
        txts.append((sp_ex_l, lx_b, floor_b + 44, w5 * p5))

        # 16 Parabolic Voter Orbs migrating live from Cheap (815) -> Expensive (265) over the Decoy!
        if 0.01 < mig_u < 0.99:
            for vi in range(16):
                delay = (vi / 16.0) * 0.55
                vu = clamp((mig_u - delay) / 0.45)
                if 0.01 < vu < 0.99:
                    vx = rx_b + (lx_b - rx_b) * vu
                    vy = (floor_b - 220) - math.sin(math.pi * vu) * (240.0 + (vi % 4) * 28.0)
                    va = math.sin(math.pi * vu) * w5
                    cs.arc(vx, vy, 6.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.96 * va); cs.fill()
                    cg.arc(vx, vy, 13.0, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.82 * va); cg.fill()

        if mig_u > 0.72:
            draw_pill_badge(cs, cg, txts, "فروشِ گرون‌ترین بسته تقریباً ۳ برابر شد!", 540, 1335, fonts.bold_30, w5 * clamp((mig_u - 0.72) * 3.5), glow=True)

    # =========================================================================
    # SCENE 6: Everywhere Around You — Popcorn, Phone Storage & Subscriptions!
    # =========================================================================
    w6 = window_fade(t, t_s6 - 0.15, t_s7 + 0.22, fi=0.32, fo=0.35)
    if w6 > 0.01:
        lt = max(0.0, t - t_s6)
        p6 = ease_out_cubic(lt / 0.75)
        draw_pill_badge(cs, cg, txts, "ردپایِ «تله‌ی عددِ وسط» توی زندگیِ روزمره", 540, 375, fonts.bold_30, w6 * p6, glow=True)

        rows_s6 = [
            (595,  "۱. پاپ‌کورنِ سینما",       "کوچیک  |  متوسط (طعمه)  |  بزرگ ✓"),
            (875,  "۲. حافظه‌ی گوشی‌های هوشمند", "۱۲۸ گیگ  |  ۲۵۶ (طعمه)  |  ۵۱۲ گیگ ✓"),
            (1155, "۳. اشتراکِ سایت‌ها و اپ‌ها", "یک‌ماهه  |  سه‌ماهه (طعمه)  |  یک‌ساله ✓"),
        ]
        for ri, (ry, r_ttl, r_opts) in enumerate(rows_s6):
            rp = spring_pop((lt - 0.22 * ri) / 0.55)
            if rp <= 0.02:
                continue
            # strip unsupported ✓ before rendering in Vazirmatn!
            clean_opts = r_opts.replace(" ✓", "")
            draw_safe_card(
                cs, cg, txts, 540, ry, 860, 205,
                [
                    (r_ttl, fonts.bold_36, -42, (255, 255, 255, 255), 0.55),
                    (clean_opts, fonts.med_32, 36, (215, 215, 228, 255), 0.2),
                ],
                radius=18, pad_x=34, alpha=w6 * clamp(rp), glow_border=True, allow_expand=False
            )
            if ri == 0:
                draw_popcorn_bucket(cs, cg, 195, ry + 68, 76, 96, alpha=w6 * clamp(rp), t=t)

        # Sweeping vertical X-ray scanner highlighting the middle decoy column!
        scan_x = 540.0 + math.sin(lt * 2.6) * 85.0
        for ctx, lw, al in ((cs, 2.2, w6 * 0.65), (cg, 6.5, w6 * 0.45)):
            ctx.move_to(scan_x, 465); ctx.line_to(scan_x, 1285)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        draw_pill_badge(cs, cg, txts, "هدفِ همه‌شون یکیه: هل دادنِ تو به گرون‌ترین گزینه!", 540, 1355, fonts.bold_30, w6 * p6, glow=True)

    # =========================================================================
    # SCENE 7: The 3-Second Antidote — Cover & Shatter the Middle Option!
    # =========================================================================
    w7 = window_fade(t, t_s7 - 0.15, t_s8 + 0.20, fi=0.32, fo=0.32)
    if w7 > 0.01:
        lt = max(0.0, t - t_s7)
        p7 = ease_out_cubic(lt / 0.7)
        draw_pill_badge(cs, cg, txts, "پادزهرِ ۳ ثانیه‌ای: چطور هیچ‌وقت گول نخوریم؟", 540, 390, fonts.bold_30, w7 * p7, glow=True)

        t_dl = t_cues["s7_del"]
        del_p = ease_out_cubic((t - (t_dl - 0.45)) / 0.6) if t >= (t_dl - 0.45) else 0.0

        # Outer 2 real options remain crisp & calm
        draw_safe_card(cs, cg, txts, 835, 825, 265, 360,
                       [("گزینه‌ی اول", fonts.reg_26, -85, (215, 215, 225, 255), 0.0),
                        ("ارزون و پایه", fonts.bold_36, 10, (255, 255, 255, 255), 0.45),
                        ("نیازِ واقعیت همینه؟", fonts.light_22, 95, (195, 195, 208, 255), 0.0)],
                       radius=18, pad_x=24, alpha=w7 * p7, glow_border=(del_p > 0.5), allow_expand=False)

        draw_safe_card(cs, cg, txts, 245, 825, 265, 360,
                       [("گزینه‌ی سوم", fonts.reg_26, -85, (215, 215, 225, 255), 0.0),
                        ("بزرگ و گرون", fonts.bold_36, 10, (240, 240, 250, 255), 0.25),
                        ("واقعاً می‌ارزه؟", fonts.light_22, 95, (195, 195, 208, 255), 0.0)],
                       radius=18, pad_x=24, alpha=w7 * p7, allow_expand=False)

        # Middle Decoy Card -> Covered by cursor & shatters/dissolves at s7_del!
        mid_alive = 1.0 - del_p
        if mid_alive > 0.03:
            sc_m = 1.0 - 0.22 * del_p
            cs.save(); apply_camera(cs, sc_m, pan_y=0); cs.restore()
            draw_safe_card(cs, cg, txts, 540, 825, 265 * sc_m, 360 * sc_m,
                           [("عددِ وسط", fonts.bold_30, -70 * sc_m, (220, 220, 230, 255), 0.0),
                            ("طعمه!", fonts.bold_44, 15 * sc_m, (255, 255, 255, 255), 0.3)],
                           radius=18, pad_x=24, alpha=w7 * p7 * mid_alive, allow_expand=False)

        # Shatter burst fragments & crisp X when deleted!
        if del_p > 0.02:
            for fi in range(12):
                ang = fi * (math.pi / 6.0) + 0.25
                rad_f = 35.0 + del_p * 145.0
                fx = 540.0 + math.cos(ang) * rad_f
                fy = 825.0 + math.sin(ang) * rad_f
                fa_p = (1.0 - del_p) * w7 * 0.9
                cs.arc(fx, fy, 4.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, fa_p); cs.fill()
            # Glowing X over deleted decoy slot
            for ctx, lw, al in ((cs, 3.4, w7 * 0.92), (cg, 6.5, w7 * 0.65)):
                ctx.set_source_rgba(1, 1, 1, al * clamp(del_p * 1.6)); ctx.set_line_width(lw)
                ctx.move_to(475, 760); ctx.line_to(605, 890); ctx.stroke()
                ctx.move_to(605, 760); ctx.line_to(475, 890); ctx.stroke()
            draw_pill_badge(cs, cg, txts, "عددِ وسط رو نادیده بگیر؛ جادو باطل می‌شه!", 540, 1215, fonts.bold_30, w7 * del_p, glow=True)

        draw_cursor_pointer(cs, cg, 548, 845, click_p=del_p, alpha=w7 * p7, scale=1.25)

    # =========================================================================
    # SCENE 8: Viral Interactive Comment Question (کجا تو این تله افتادی؟)
    # =========================================================================
    w8 = window_fade(t, t_s8 - 0.15, t_endplate + 0.22, fi=0.28, fo=0.42)
    if w8 > 0.01:
        lt = max(0.0, t - t_s8)
        p8 = spring_pop(lt / 0.6)
        draw_pill_badge(cs, cg, txts, "نوبتِ تو؛ آخرین بار کجا توی این تله افتادی؟", 540, 425, fonts.bold_30, w8 * clamp(p8), glow=True)

        cta_items = [
            (635,  "۱. منویِ کافه، فست‌فود یا سینما"),
            (835,  "۲. خریدِ گوشی و حافظه‌ی بالاتر"),
            (1035, "۳. بسته‌های اینترنت و اشتراکِ سایت‌ها"),
        ]
        active_hi = int(t * 2.2) % 3
        for ci, (cy_i, c_txt) in enumerate(cta_items):
            is_hi = (ci == active_hi)
            draw_safe_card(
                cs, cg, txts, 540, cy_i, 760, 142,
                [(c_txt, fonts.bold_36, 0, (255, 255, 255, 255), 0.7 if is_hi else 0.2)],
                radius=18, pad_x=34, alpha=w8 * clamp(p8), glow_border=is_hi, allow_expand=False
            )
        draw_pill_badge(cs, cg, txts, "عددش رو توی کامنت بنویس: ۱ ، ۲ یا ۳ ؟", 540, 1245, fonts.bold_30, w8 * clamp(p8), glow=True)

    # =========================================================================
    # SCENE 9: Signature OLED Endplate — زاویه ذهن (@zavieh.penhann)
    # =========================================================================
    w9 = window_fade(t, t_endplate - 0.1, total_dur + 0.5, fi=0.50, fo=0.1)
    if w9 > 0.01:
        lt = max(0.0, t - t_endplate)
        p_logo = ease_out_cubic(lt / 1.05)

        cx, cy = 540.0, 745.0
        cs.save(); cs.set_dash([])
        for k in range(36):
            ang = k * (math.pi / 18.0) + t * 0.22
            r0 = 188.0
            cs.arc(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0, 1.8, 0, 2 * math.pi)
            cs.set_source_rgba(1, 1, 1, 0.36 * w9 * p_logo); cs.fill()
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

        sp_brand = get_text_sprite("زاویه ذهن", fonts.eb_84, (255, 255, 255, 255), glow=0.82)
        sp_tag   = get_fitted_text_sprite("زوایایِ پنهانِ اقتصاد، ذهن و زندگی", fonts.reg_34, 880, (198, 198, 210, 255))
        txts.append((sp_brand, 540, 1065, w9 * ease_out_cubic((lt - 0.15) / 0.7)))
        txts.append((sp_tag,   540, 1168, w9 * ease_out_cubic((lt - 0.30) / 0.7)))

        pill_a = w9 * ease_out_cubic((lt - 0.45) / 0.7)
        draw_pill_badge(cs, cg, txts, "@zavieh.penhann", 540, 1290, fonts.med_36, pill_a, glow=True, pad_x=44, pad_y=15)

    return composite_oled_frame(surf_glow, surf_sharp, txts, fonts, t, sub_lines)


# =============================================================================
# MULTICORE CLOUD RENDERER + AUTOMATIC VISUAL QA SHEET GENERATOR
# =============================================================================
_W_FONTS = None
_W_SURF_G = None
_W_CTX_G = None
_W_SURF_S = None
_W_CTX_S = None
_W_META = None

def _worker_init(font_dir: str, meta: dict):
    global _W_FONTS, _W_SURF_G, _W_CTX_G, _W_SURF_S, _W_CTX_S, _W_META
    _W_FONTS  = FontBank(font_dir)
    _W_SURF_G = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CTX_G  = cairo.Context(_W_SURF_G)
    _W_SURF_S = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CTX_S  = cairo.Context(_W_SURF_S)
    _W_META   = meta

def _worker_render_frame(fn: int) -> bytes:
    t = fn / float(FPS)
    return render_scene_frame(
        t, _W_META["total_dur"], _W_META["t_cues"], _W_META["sub_lines"],
        _W_FONTS, _W_SURF_G, _W_CTX_G, _W_SURF_S, _W_CTX_S
    )

def save_qa_sheets(font_dir: str, meta: dict, qa_dir: str):
    from PIL import Image, ImageDraw
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    sg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cg = cairo.Context(sg)
    ss = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cs = cairo.Context(ss)

    # 1. 14-frame subtitle wipe & baseline verification strip
    sub_idx = min(22, len(meta["sub_lines"]) - 2)
    t0_s = meta["sub_lines"][sub_idx]["start"] + 0.08
    strip = Image.new("RGB", (920, 14 * 96), (12, 12, 14))
    for i in range(14):
        tf = t0_s + i * (1.0 / 30.0) * 3.5
        raw = render_scene_frame(tf, meta["total_dur"], meta["t_cues"], meta["sub_lines"], fonts, sg, cg, ss, cs)
        crop = Image.frombytes("RGB", (W, H), raw).crop((80, 1580, 1000, 1676))
        d = ImageDraw.Draw(crop)
        d.line([(0, 62), (28, 62)], fill=(90, 220, 130), width=1)
        d.line([(892, 62), (920, 62)], fill=(90, 220, 130), width=1)
        strip.paste(crop, (0, i * 96))
    strip.save(os.path.join(qa_dir, "subtitle_strip_verify.png"))

    # 2. 12-panel full episode storyboard contact sheet
    tc = meta["t_cues"]
    td = meta["total_dur"]
    sample_ts = [
        tc["s1_diff"] + 0.35,       # P1: 3 Cafe Cups + 15k caliper arc + steam
        tc["s1_hook"] + 0.55,       # P2: Pendulum fishing hook lifting 135 Decoy cup!
        tc["s2_pick90"] + 0.35,     # P3: 2-Cup honest menu -> Cursor sonar-clicking 90!
        tc["s3_pick150"] + 0.35,    # P4: Brain spotlight cone on [135 & 150] -> Cursor clicking 150!
        tc["s4_term"] + 0.75,       # P5: Parabolic money orbs + Dossier "اثر طعمه"
        tc["s5_exp"] + 1.6,         # P6: University experiment Phase A (68% vs 32%)
        0.5 * (tc["s5_surge"] + tc["s5_84"]), # P7: Mid-migration parabolic voter swarm flying across!
        tc["s5_84"] + 0.55,         # P8: Final 84% surge vs 0% decoy!
        tc["s6_every"] + 2.2,       # P9: Popcorn bucket + Phone storage + Subscriptions X-ray
        tc["s7_del"] + 0.35,        # P10: Cursor shattering the middle decoy option!
        tc["s8_cta"] + 1.2,         # P11: Interactive 1 / 2 / 3 comment cards
        td - 1.5,                   # P12: Signature OLED Endplate (@zavieh.penhann)
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

    print("=== [1/3] Building Master Audio (Locked Rasalgethi + 129-tap FIR + Cinematic Minor Score) ===", flush=True)
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
        raise SystemExit("Usage: python ep04_decoy_effect.py --cloud-render <font_dir> <work_dir> <out_mp4> <qa_dir> [whisper_size]")
