"""
Episode 03 — The Invisible Tax & Money Illusion (مالیاتِ نامرئی و توهمِ پولیِ حقوق)
Page: زاویه ذهن (@zavieh.penhann)
Engine v2.2:
  - Locked Voice: Gemini 'Rasalgethi' + 129-tap @ensan.besham FIR + -0.34st Formant Calibration
  - Music: Evolving Dark-Cinematic Minor Progression (Am9 -> Fmaj7 -> Dm9 -> Em7) + Felt Piano + Hall Reverb
  - Subtitles: 29 short single-line RTL phrases @ constant 40px Vazirmatn-Medium + 64px-feathered 60fps wipe
  - Layout Safety: 100% Zero-Overflow containers via draw_safe_card & get_fitted_text_sprite
"""
import os, sys, math, time, subprocess
import cairocffi as cairo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.engine.audio_master import build_episode_audio, LOCKED_SIGNATURE_VOICE
from src.engine.render_core import (
    W, H, FPS, SAFE_MARGIN_X, fa, clamp, ease_out_cubic, ease_in_out_cubic, spring_pop, window_fade,
    FontBank, get_text_sprite, get_fitted_text_sprite, set_stroke_draw, rounded_rect_path,
    draw_star4, draw_stipple_line, draw_human_figure, draw_pill_badge, draw_folder_window,
    draw_stamp_badge, draw_safe_card, draw_spotlight_cone, draw_hud_chrome, composite_oled_frame
)

EP_CODE = "03"
EP_TITLE = "مالیاتِ نامرئی"

# 29 crisp, simple, street-smart 4-7 word phrases (0 jargon, instant comprehension!)
SCRIPT_SEGMENTS = [
    ("اگه پارسال حقوقت بیست میلیون بوده،",            "اگه پارسال حقوقت ۲۰ میلیون بوده،"),
    ("و امسال شده بیست و هشت میلیون،",               "و امسال شده ۲۸ میلیون،"),
    ("اصلاً به خودت تبریک نگو؛",                      "اصلاً به خودت تبریک نگو؛"),
    ("چون ماهی چهار میلیون فقیرتر شدی!",              "چون ماهی ۴ میلیون فقیرتر شدی!"),
    ("چرا هر چقدر بیشتر می‌دوی،",                     "چرا هر چقدر بیشتر می‌دوی،"),
    ("آخرِ ماه باز سرِ جات ثابتی؟",                   "آخر ماه باز سر جات ثابتی؟"),
    ("اقتصاددان‌ها به این تله‌ی عجیب می‌گن:",          "اقتصاددان‌ها به این تله‌ی عجیب می‌گن:"),
    ("توهمِ پولی و مالیاتِ نامرئی!",                   "توهم پولی و مالیات نامرئی!"),
    ("مغزِ ما عاشقِ عددهای درشته؛",                    "مغز ما عاشق عددهای درشته؛"),
    ("وقتی می‌بینه رقمِ حقوقت بالا رفته،",             "وقتی می‌بینه رقم حقوقت بالا رفته،"),
    ("فوری حسِ پیشرفت بهت می‌ده؛",                    "فوری حس پیشرفت بهت می‌ده؛"),
    ("ولی آب رفتنِ پول رو نمی‌بینه!",                  "ولی آب رفتن پول رو نمی‌بینه!"),
    ("بیا با یه حسابِ ساده ببینیمش:",                 "بیا با یه حساب ساده ببینیمش:"),
    ("وقتی حقوقت چهل درصد بیشتر بشه،",               "وقتی حقوقت ۴۰ درصد بیشتر بشه،"),
    ("ولی اجاره و خوراک شصت درصد گرون شن،",           "ولی اجاره و خوراک ۶۰ درصد گرون شن،"),
    ("سبدِ خریدت بیست درصد کوچیک‌تر شده!",             "سبد خریدت ۲۰ درصد کوچیک‌تر شده!"),
    ("حالا چرا اسمش مالیاتِ نامرئیه؟",                "حالا چرا اسمش مالیات نامرئیه؟"),
    ("چون هیچ پیامکی برات نمیاد،",                   "چون هیچ پیامکی برات نمیاد،"),
    ("و پولی از حسابت کم نمی‌شه؛",                    "و پولی از حسابت کم نمی‌شه؛"),
    ("ولی قدرتِ پولت بی‌صدا دزدیده می‌شه!",            "ولی قدرت پولت بی‌صدا دزدیده می‌شه!"),
    ("بدتر از همه پس‌اندازِ نقدیه:",                   "بدتر از همه پس‌انداز نقدیه:"),
    ("صد میلیون پولِ راکد توی بانک،",                 "۱۰۰ میلیون پول راکد توی بانک،"),
    ("بعدِ دو سال همون صد میلیونه؛",                  "بعد ۲ سال همون ۱۰۰ میلیونه؛"),
    ("ولی زورش نصفِ قبل هم نیست!",                    "ولی زورش نصف قبل هم نیست!"),
    ("ثروتمندها هیچ‌وقت به تومن فکر نمی‌کنن؛",         "ثروتمندها هیچ‌وقت به تومن فکر نمی‌کنن؛"),
    ("داراییِ واقعی و مهارت جمع می‌کنن،",              "دارایی واقعی و مهارت جمع می‌کنن،"),
    ("نه فقط عددِ بزرگ‌تر روی فیش!",                  "نه فقط عدد بزرگ‌تر روی فیش!"),
    ("امسال عددِ حقوقت جلوتر دویده،",                 "امسال عدد حقوقت جلوتر دویده،"),
    ("یا سرعتِ خرج‌های زندگیت؟",                      "یا سرعت خرج‌های زندگیت؟"),
]

SFX_CUE_MAP = [
    ("s1_28m",    1, 2, "ping"),    # ۲۸ میلیون
    ("s1_shock",  3, 2, "stamp"),   # ۴ میلیون فقیرتر شدی
    ("s2_tread",  4, 0, "whoosh"),  # چرا هر چقدر بیشتر می‌دوی
    ("s2_term",   7, 0, "ping"),    # توهم پولی و مالیات نامرئی
    ("s3_brain",  8, 0, "whoosh"),  # مغز ما عاشق عددهای درشته
    ("s3_melt",  11, 1, "ping"),    # آب رفتن پول
    ("s4_math",  12, 0, "whoosh"),  # بیا با یه حساب ساده
    ("s4_shrink",15, 2, "stamp"),   # ۲۰ درصد کوچیک‌تر شده
    ("s5_silent",16, 0, "whoosh"),  # حالا چرا اسمش مالیات نامرئیه
    ("s5_steal", 19, 3, "ping"),    # بی‌صدا دزدیده می‌شه
    ("s6_cash",  20, 0, "whoosh"),  # بدتر از همه پس‌انداز نقدیه
    ("s6_half",  23, 2, "stamp"),   # نصف قبل هم نیست
    ("s7_rich",  24, 0, "whoosh"),  # ثروتمندها هیچ‌وقت
    ("s8_cta",   27, 0, "chime"),   # امسال عدد حقوقت جلوتر دویده
]


def apply_camera(ctx, zoom: float, pan_x: float = 0.0, pan_y: float = 0.0):
    ctx.translate(W * 0.5 + pan_x, H * 0.48 + pan_y)
    ctx.scale(zoom, zoom)
    ctx.translate(-W * 0.5, -H * 0.48)


def draw_running_human(ctx, cx: float, cy: float, scale: float, alpha: float, t: float, lw: float = 2.4):
    """
    60fps animated running geometric monoline human (facing RIGHT toward goal, running on treadmill!).
    Origin (cx, cy) is belt contact level.
    """
    if alpha <= 0.01:
        return
    stride = math.sin(t * 9.5)
    stride_cos = math.cos(t * 9.5)
    bob = abs(stride_cos) * 7.5

    ctx.save()
    ctx.set_dash([])
    ctx.translate(cx, cy - bob * scale)
    ctx.scale(scale, scale)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.set_line_width(lw / max(0.4, scale))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # Slight forward runner lean (+11 deg)
    # Head
    ctx.arc(14, -146, 21, 0, 2 * math.pi)
    ctx.stroke()

    # Spine / Torso (hip at -4, -64; shoulder at 10, -118)
    ctx.move_to(10, -118)
    ctx.line_to(-4, -64)
    ctx.stroke()
    # Rounded chest/torso frame
    ctx.move_to(-6, -116)
    ctx.line_to(22, -114)
    ctx.line_to(10, -64)
    ctx.line_to(-16, -66)
    ctx.close_path()
    ctx.stroke()

    # Pumping Arms (shoulder pivot at 8, -110)
    for sgn in (1.0, -1.0):
        ang_u = sgn * stride * 0.72
        el_x = 8 + math.sin(ang_u) * 32
        el_y = -110 + math.cos(ang_u) * 30
        ha_x = el_x + math.cos(ang_u * 0.6 - 0.35) * 26
        ha_y = el_y + math.sin(ang_u * 0.6 - 0.35) * 22 - 8
        ctx.move_to(8, -110)
        ctx.line_to(el_x, el_y)
        ctx.line_to(ha_x, ha_y)
        ctx.stroke()

    # Pumping Legs (hip pivot at -4, -64)
    for sgn in (1.0, -1.0):
        ang_l = -sgn * stride * 0.78
        kn_x = -4 + math.sin(ang_l) * 36
        kn_y = -64 + math.cos(ang_l) * 34
        bend = max(0.15, 0.55 + 0.45 * sgn * stride_cos)
        ft_x = kn_x + math.sin(ang_l - bend) * 34
        ft_y = min(2.0, kn_y + math.cos(ang_l - bend) * 34)
        ctx.move_to(-4, -64)
        ctx.line_to(kn_x, kn_y)
        ctx.line_to(ft_x, ft_y)
        ctx.stroke()

    ctx.restore()


def draw_gear(ctx, cx: float, cy: float, r: float, angle: float, alpha: float, teeth: int = 8):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.set_dash([])
    ctx.translate(cx, cy)
    ctx.rotate(angle)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.set_line_width(2.0)
    ctx.arc(0, 0, r * 0.72, 0, 2 * math.pi)
    ctx.stroke()
    ctx.arc(0, 0, r * 0.24, 0, 2 * math.pi)
    ctx.stroke()
    for i in range(teeth):
        a = i * (2 * math.pi / teeth)
        ctx.move_to(math.cos(a) * r * 0.72, math.sin(a) * r * 0.72)
        ctx.line_to(math.cos(a) * r, math.sin(a) * r)
        ctx.stroke()
    ctx.restore()


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

    t_s2 = t_cues["s2_tread"]
    t_s3 = t_cues["s3_brain"]
    t_s4 = t_cues["s4_math"]
    t_s5 = t_cues["s5_silent"]
    t_s6 = t_cues["s6_cash"]
    t_s7 = t_cues["s7_rich"]
    t_s8 = t_cues["s8_cta"]
    t_endplate = total_dur - 3.9

    chapters = [0.0, t_s2, t_s3, t_s4, t_s5, t_s6, t_s7, t_s8]
    draw_hud_chrome(cs, cg, txts, fonts, t, total_dur, EP_CODE, EP_TITLE, chapters)

    # =========================================================================
    # SCENE 1: Paycheck Illusion (۲۰ میلیون -> ۲۸ میلیون) + [-۴ میلیون فقیرتر!] Stamp
    # =========================================================================
    w1 = window_fade(t, 0.0, t_s2 + 0.22, fi=0.22, fo=0.35)
    if w1 > 0.01:
        u1 = clamp(t / max(0.1, t_s2))
        cs.save(); cg.save()
        apply_camera(cs, 1.0 + 0.045 * u1)
        apply_camera(cg, 1.0 + 0.045 * u1)

        p_top = ease_out_cubic(t / 0.75)
        draw_folder_window(cs, cg, txts, 540, 560, 820, 235, "فیشِ حقوقِ پارسال", fonts.reg_26, w1, p_top)
        sp_20 = get_fitted_text_sprite("۲۰,۰۰۰,۰۰۰ تومان", fonts.bold_52, 740, (215, 215, 225, 255))
        sp_20s = get_fitted_text_sprite("قدرتِ خریدِ کاملِ سبدِ زندگی", fonts.light_26, 740, (155, 155, 165, 255))
        txts.append((sp_20, 540, 535, w1 * p_top))
        txts.append((sp_20s, 540, 608, w1 * p_top))

        # Downward transition connector
        t_28 = t_cues["s1_28m"]
        p_bot = ease_out_cubic((t - (t_28 - 0.55)) / 0.75) if t >= (t_28 - 0.55) else 0.0
        if p_bot > 0.02:
            draw_stipple_line(cs, 540, 690, 540, 790, 8, r=2.0, alpha=w1 * p_bot * 0.65)
            t_sh = t_cues["s1_shock"]
            sh_p = clamp((t - t_sh) / 0.42) if t >= t_sh else 0.0
            dim_28 = 1.0 - 0.88 * sh_p

            draw_folder_window(cs, cg, txts, 540, 965, 840, 290, "فیشِ حقوقِ امسال", fonts.bold_30, w1, p_bot)
            val_num = int(round(20 + 8 * p_bot))
            sp_28 = get_fitted_text_sprite(f"{val_num:,},۰۰۰,۰۰۰ تومان", fonts.eb_68, 760, (255, 255, 255, 255), glow=0.75 * dim_28)
            txts.append((sp_28, 540, 925, w1 * p_bot * dim_28))
            draw_pill_badge(cs, cg, txts, "ظاهرِ فیش: ۴۰٪ افزایشِ حقوق", 540, 1032, fonts.reg_26, w1 * p_bot * dim_28, glow=(sh_p < 0.1))

            # Reality Shock Stamp at "چون ماهی ۴ میلیون فقیرتر شدی!"
            if sh_p > 0.02:
                draw_stamp_badge(cs, cg, txts, "واقعیت: ۴ میلیون فقیرتر!", 540, 960, -8.5, fonts.bold_44, w1, sh_p)
                draw_safe_card(
                    cs, cg, txts, 540, 1265, 760, 118,
                    [("قدرتِ واقعیِ ۲۸ میلیونِ امسال = فقط ۱۶ میلیونِ پارسال!", fonts.med_32, 0, (245, 245, 252, 255), 0.45)],
                    radius=14, pad_x=32, alpha=w1 * ease_out_cubic(sh_p), glow_border=True
                )

        cs.restore(); cg.restore()

    # =========================================================================
    # SCENE 2: Mechanical Inflation Treadmill + Running Human + Dossier Reveal
    # =========================================================================
    w2 = window_fade(t, t_s2 - 0.15, t_s3 + 0.22, fi=0.32, fo=0.35)
    if w2 > 0.01:
        lt = max(0.0, t - t_s2)
        p2 = ease_out_cubic(lt / 0.8)
        draw_pill_badge(cs, cg, txts, "تردمیلِ پنهانِ اقتصاد: دویدن درجا!", 540, 385, fonts.bold_30, w2 * p2, glow=True)

        # Goal flag on far right (x=885, unreachable!)
        gx, gy = 875.0, 825.0
        cs.set_source_rgba(1, 1, 1, 0.78 * w2 * p2); cs.set_line_width(2.2)
        cs.move_to(gx, gy); cs.line_to(gx, gy - 175); cs.stroke()
        draw_star4(cs, gx, gy - 192, 13 * p2, w2)
        draw_star4(cg, gx, gy - 192, 22 * p2, w2 * 0.85)
        sp_goal = get_fitted_text_sprite("آرامشِ مالی", fonts.light_22, 160, (200, 200, 212, 255))
        txts.append((sp_goal, gx, gy - 232, w2 * p2))

        # Animated Running Human on Treadmill Belt (stays trapped around x=475!)
        runner_x = 475.0 + math.sin(lt * 2.2) * 14.0
        belt_y = 825.0
        draw_running_human(cs, runner_x, belt_y, scale=1.18, alpha=w2 * 0.98, t=t, lw=2.6)
        draw_running_human(cg, runner_x, belt_y, scale=1.18, alpha=w2 * 0.52, t=t, lw=5.0)

        # Mechanical Treadmill Deck & Spinning Gears (x: 195 .. 795, r_roller=42)
        tx0, tx1, r_rol = 215.0, 775.0, 42.0
        for ctx, lw, al in ((cs, 2.5, w2 * 0.92), (cg, 5.0, w2 * 0.42)):
            rounded_rect_path(ctx, tx0 - r_rol, belt_y, (tx1 - tx0) + 2 * r_rol, r_rol * 2, r_rol)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()

        # Spinning rollers (counter-clockwise = pushing runner LEFT!)
        draw_gear(cs, tx0, belt_y + r_rol, 30, -t * 5.2, w2 * 0.85)
        draw_gear(cs, tx1, belt_y + r_rol, 30, -t * 5.2, w2 * 0.85)
        # Moving belt chevrons sliding rapidly RIGHT-TO-LEFT!
        for k in range(11):
            bx = tx1 - ((t * 240.0 + k * 52.0) % (tx1 - tx0))
            cs.set_source_rgba(1, 1, 1, 0.55 * w2); cs.set_line_width(1.9)
            cs.move_to(bx + 8, belt_y - 6); cs.line_to(bx, belt_y); cs.line_to(bx + 8, belt_y + 6); cs.stroke()

        # Speed comparison pills (strictly fitted via draw_safe_card!)
        draw_safe_card(cs, cg, txts, 315, 978, 330, 82,
                       [("سرعتِ رشدِ حقوق: +۴۰٪", fonts.reg_26, 0, (210, 210, 220, 255), 0.0)],
                       radius=10, pad_x=26, alpha=w2 * p2, allow_expand=False)
        draw_safe_card(cs, cg, txts, 735, 978, 370, 82,
                       [("سرعتِ عقب‌گردِ قیمت‌ها: -۶۰٪", fonts.bold_30, 0, (255, 255, 255, 255), 0.45)],
                       radius=10, pad_x=26, alpha=w2 * p2, glow_border=True, allow_expand=False)

        # Scientific/Economic Dossier Reveal at "توهم پولی و مالیات نامرئی!"
        t_tm = t_cues["s2_term"]
        if t >= t_tm - 0.85:
            dp = ease_out_cubic((t - (t_tm - 0.85)) / 0.75)
            draw_folder_window(cs, cg, txts, 540, 1245, 860, 275, "نامِ علمیِ این تله", fonts.bold_30, w2, dp)
            sp_t1 = get_fitted_text_sprite("توهمِ پولی و مالیاتِ نامرئی", fonts.bold_52, 780, (255, 255, 255, 255), glow=0.82)
            sp_t2 = get_fitted_text_sprite("وقتی عددِ پول بزرگ می‌شه، ولی قدرتش آب می‌ره!", fonts.reg_26, 780, (195, 195, 208, 255))
            txts.append((sp_t1, 540, 1212, w2 * dp))
            txts.append((sp_t2, 540, 1295, w2 * dp))

    # =========================================================================
    # SCENE 3: Brain Loves Big Numbers vs Melting Purchasing-Power Ice Pillar
    # =========================================================================
    w3 = window_fade(t, t_s3 - 0.15, t_s4 + 0.22, fi=0.32, fo=0.35)
    if w3 > 0.01:
        lt = max(0.0, t - t_s3)
        p3 = ease_out_cubic(lt / 0.8)

        # Top Section: Observer Brain dazzled by big nominal Bank Card number
        draw_human_figure(cs, 215, 735, scale=1.02, alpha=w3 * 0.95, draw_p=p3, star_mind=True, t=t)
        draw_human_figure(cg, 215, 735, scale=1.02, alpha=w3 * 0.45, draw_p=1.0, star_mind=True, t=t)
        draw_stipple_line(cs, 245, 585, 415, 565, 10, r=1.9, alpha=w3 * p3 * 0.7)

        draw_safe_card(
            cs, cg, txts, 665, 585, 530, 215,
            [
                ("موجودیِ اسمیِ کارتِ بانکی", fonts.light_26, -54, (185, 185, 198, 255), 0.0),
                ("۲۸,۰۰۰,۰۰۰", fonts.eb_68, 8, (255, 255, 255, 255), 0.75),
                ("حسِ فریبنده‌ی پیشرفت در مغز!", fonts.reg_26, 68, (220, 220, 232, 255), 0.25),
            ],
            radius=16, pad_x=32, alpha=w3 * p3, glow_border=True, allow_expand=False
        )

        # Bottom Section: Melting Purchasing-Power Block ("ولی آب رفتن پول رو نمی‌بینه!")
        t_mlt = t_cues["s3_melt"]
        melt_u = clamp((t - (t_s3 + 1.0)) / max(1.2, (t_s4 - t_s3 - 1.2)))
        full_h = 330.0
        cur_h  = full_h * (1.0 - 0.52 * ease_in_out_cubic(melt_u))
        base_y = 1285.0
        bx0, bw_ice = 355.0, 370.0

        # Original ghosted height outline (dashed)
        cs.set_dash([9, 8]); cs.set_source_rgba(1, 1, 1, 0.26 * w3); cs.set_line_width(1.6)
        cs.rectangle(bx0, base_y - full_h, bw_ice, full_h); cs.stroke(); cs.set_dash([])

        # Shrinking luminous real-value block
        for ctx, lw, al in ((cs, 2.5, w3 * 0.95), (cg, 5.2, w3 * 0.52)):
            rounded_rect_path(ctx, bx0, base_y - cur_h, bw_ice, cur_h, 10)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()

        # Falling melt droplets & puddle ripples at base_y!
        for di in range(7):
            dx = bx0 + 38 + di * 49
            dy = (base_y - cur_h) + ((t * 175 + di * 43) % max(24.0, cur_h))
            cs.arc(dx, dy, 3.0, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.52 * w3); cs.fill()
        cs.move_to(240, base_y + 4); cs.line_to(840, base_y + 4)
        cs.set_source_rgba(1, 1, 1, 0.45 * w3); cs.set_line_width(2.0); cs.stroke()

        pct_left = int(round(100 - 52 * ease_in_out_cubic(melt_u)))
        sp_ice1 = get_fitted_text_sprite(f"قدرتِ واقعی: {pct_left}٪", fonts.bold_36, bw_ice - 40, (255, 255, 255, 255), glow=0.5)
        txts.append((sp_ice1, 540, base_y - cur_h * 0.5, w3))
        draw_pill_badge(cs, cg, txts, "ذوب شدنِ بی‌صدایِ ارزشِ پول", 540, 1365, fonts.bold_30, w3 * p3)

    # =========================================================================
    # SCENE 4: Side-by-Side Shopping Basket Math (۱۰ کالا -> ۸ کالا = -۲۰٪!)
    # =========================================================================
    w4 = window_fade(t, t_s4 - 0.15, t_s5 + 0.22, fi=0.32, fo=0.35)
    if w4 > 0.01:
        lt = max(0.0, t - t_s4)
        p4 = ease_out_cubic(lt / 0.85)
        draw_pill_badge(cs, cg, txts, "محاسبه‌ی واقعی: حقوق +۴۰٪  |  گرانیِ زندگی +۶۰٪", 540, 385, fonts.bold_30, w4 * p4, glow=True)

        # Two tall @ensan.besham comparison frames (Right: پارسال, Left: امسال)
        # Right Panel (cx=770, w=410, h=760)
        rx_c, lx_c, cy_p, pw_p, ph_p = 770.0, 310.0, 865.0, 410.0, 740.0
        draw_safe_card(
            cs, cg, txts, rx_c, cy_p, pw_p, ph_p,
            [
                ("پارسال", fonts.bold_36, -310, (240, 240, 248, 255), 0.3),
                ("حقوق: ۲۰ میلیون", fonts.reg_26, -252, (175, 175, 188, 255), 0.0),
                ("۱۰ واحد خریدِ کامل", fonts.bold_30, 305, (225, 225, 235, 255), 0.2),
            ],
            radius=18, pad_x=28, alpha=w4 * p4, allow_expand=False
        )
        # 10 solid glowing commodity blocks inside Right Basket (2 cols x 5 rows)
        for bi in range(10):
            r_i, c_i = divmod(bi, 2)
            bx = rx_c - 118 + c_i * 132
            by = cy_p + 185 - r_i * 82
            rounded_rect_path(cs, bx, by, 104, 62, 8)
            cs.set_source_rgba(1, 1, 1, 0.16 * w4 * p4); cs.fill_preserve()
            cs.set_source_rgba(1, 1, 1, 0.82 * w4 * p4); cs.set_line_width(1.9); cs.stroke()

        # Left Panel (cx=310, w=410, h=740) — امسال!
        t_shk = t_cues["s4_shrink"]
        shk_p = spring_pop((t - (t_shk - 0.5)) / 0.65) if t >= (t_shk - 0.5) else 0.0
        draw_safe_card(
            cs, cg, txts, lx_c, cy_p, pw_p, ph_p,
            [
                ("امسال", fonts.bold_36, -310, (255, 255, 255, 255), 0.6),
                ("حقوق: ۲۸ میلیون (+۴۰٪)", fonts.reg_26, -252, (205, 205, 218, 255), 0.0),
                ("فقط ۸ واحد خرید! (-۲۰٪)", fonts.bold_30, 305, (255, 255, 255, 255), 0.65),
            ],
            radius=18, pad_x=28, alpha=w4 * p4, glow_border=True, allow_expand=False
        )
        for bi in range(10):
            r_i, c_i = divmod(bi, 2)
            bx = lx_c - 118 + c_i * 132
            by = cy_p + 185 - r_i * 82
            if bi < 8:
                rounded_rect_path(cs, bx, by, 104, 62, 8)
                cs.set_source_rgba(1, 1, 1, 0.22 * w4 * p4); cs.fill_preserve()
                cs.set_source_rgba(1, 1, 1, 0.92 * w4 * p4); cs.set_line_width(2.1); cs.stroke()
            else:
                # Top 2 items evaporate upward & get crossed out!
                float_up = shk_p * 34.0
                cs.set_dash([6, 6])
                rounded_rect_path(cs, bx, by - float_up, 104, 62, 8)
                cs.set_source_rgba(1, 1, 1, (0.55 - 0.35 * clamp(shk_p)) * w4); cs.set_line_width(1.6); cs.stroke()
                cs.set_dash([])
                if shk_p > 0.1:
                    cs.move_to(bx + 18, by - float_up + 14); cs.line_to(bx + 86, by - float_up + 48); cs.stroke()
                    cs.move_to(bx + 86, by - float_up + 14); cs.line_to(bx + 18, by - float_up + 48); cs.stroke()

        if shk_p > 0.05:
            draw_pill_badge(cs, cg, txts, "نتیجه: سبدِ خریدت ۲۰٪ آب رفت!", 540, 1345, fonts.bold_36, w4 * clamp(shk_p), glow=True)

    # =========================================================================
    # SCENE 5: Why "Invisible Tax"? Zero Bank SMS vs Silent Purchasing-Power Siphon
    # =========================================================================
    w5 = window_fade(t, t_s5 - 0.15, t_s6 + 0.22, fi=0.32, fo=0.35)
    if w5 > 0.01:
        lt = max(0.0, t - t_s5)
        p5 = ease_out_cubic(lt / 0.85)
        draw_pill_badge(cs, cg, txts, "چرا بهش می‌گن «مالیاتِ نامرئی»؟", 540, 385, fonts.bold_36, w5 * p5, glow=True)

        # Top Smartphone Notification Window: "برداشت از حساب: ۰ تومان!"
        draw_folder_window(cs, cg, txts, 540, 625, 840, 250, "پیامک‌هایِ بانکِ تو", fonts.bold_30, w5, p5)
        sp_sms1 = get_fitted_text_sprite("برداشت از حساب: ۰ تومان", fonts.bold_44, 740, (255, 255, 255, 255), glow=0.55)
        sp_sms2 = get_fitted_text_sprite("هیچ پیامکِ هشداری ارسال نمی‌شود؛ موجودیِ عددی دست‌نخورده است!", fonts.light_26, 760, (185, 185, 198, 255))
        txts.append((sp_sms1, 540, 598, w5 * p5))
        txts.append((sp_sms2, 540, 675, w5 * p5))

        # Bottom Scene: Vault on Right + Invisible Siphon Beam pulling glowing orbs to Left!
        vx_c, vy_c = 775.0, 1105.0
        draw_safe_card(
            cs, cg, txts, vx_c, vy_c, 330, 320,
            [
                ("حسابِ بانکیِ تو", fonts.bold_30, -105, (240, 240, 250, 255), 0.3),
                ("عدد: ثابت", fonts.reg_26, 108, (175, 175, 188, 255), 0.0),
            ],
            radius=18, pad_x=26, alpha=w5 * p5, glow_border=True, allow_expand=False
        )
        # Vault dial wheel
        draw_gear(cs, vx_c, vy_c + 4, 56, t * 0.8, w5 * p5 * 0.85, teeth=6)

        # Siphon Spotlight Cone draining purchasing power from vault (610, 1105) to collector (225, 1105)
        t_stl = t_cues["s5_steal"]
        stl_p = ease_out_cubic((t - (t_s5 + 0.9)) / 0.9)
        if stl_p > 0.02:
            draw_spotlight_cone(cs, cg, 225, 1105, 610, 610, 995, alpha=0.0) # helper warm-up
            # Custom horizontal translucent siphon cone from Vault (610) -> Siphon Vortex (225)
            cs.save()
            pat = cairo.LinearGradient(610, vy_c, 225, vy_c)
            pat.add_color_stop_rgba(0.0, 1, 1, 1, 0.18 * w5 * stl_p)
            pat.add_color_stop_rgba(1.0, 1, 1, 1, 0.03 * w5 * stl_p)
            cs.move_to(610, vy_c - 95); cs.line_to(225, vy_c - 24); cs.line_to(225, vy_c + 24); cs.line_to(610, vy_c + 95); cs.close_path()
            cs.set_source(pat); cs.fill()
            cs.set_dash([10, 8]); cs.set_source_rgba(1, 1, 1, 0.55 * w5 * stl_p); cs.set_line_width(1.8)
            cs.move_to(610, vy_c - 95); cs.line_to(225, vy_c - 24); cs.stroke()
            cs.move_to(610, vy_c + 95); cs.line_to(225, vy_c + 24); cs.stroke()
            cs.set_dash([]); cs.restore()

            # Glowing purchasing-power orbs silently sucked leftward out of vault!
            for oi in range(7):
                u_o = ((t * 0.65 + oi / 7.0) % 1.0)
                ox = 600.0 - u_o * 365.0
                oy = vy_c + math.sin(u_o * 8.0 + oi) * (55.0 * (1.0 - u_o))
                oa = math.sin(math.pi * u_o) * w5 * stl_p
                cs.arc(ox, oy, 5.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.92 * oa); cs.fill()
                cg.arc(ox, oy, 11.0, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.75 * oa); cg.fill()

            # Siphon vortex ring at x=215
            draw_gear(cs, 215, vy_c, 44, -t * 3.8, w5 * stl_p * 0.92, teeth=10)
            draw_gear(cg, 215, vy_c, 44, -t * 3.8, w5 * stl_p * 0.55, teeth=10)
            draw_pill_badge(cs, cg, txts, "دزدیِ بی‌صدا از قدرتِ خرید", 255, vy_c + 125, fonts.bold_30, w5 * stl_p, glow=True)

    # =========================================================================
    # SCENE 6: The Idle Cash Trap — ۱۰۰ میلیون پولِ راکد در بانک بعد از ۲ سال!
    # =========================================================================
    w6 = window_fade(t, t_s6 - 0.15, t_s7 + 0.22, fi=0.32, fo=0.35)
    if w6 > 0.01:
        lt = max(0.0, t - t_s6)
        p6 = ease_out_cubic(lt / 0.8)
        draw_pill_badge(cs, cg, txts, "تله‌ی مرگبار: پس‌اندازِ نقدیِ راکد در بانک", 540, 390, fonts.bold_30, w6 * p6, glow=True)

        floor_y = 1285.0
        cs.move_to(110, floor_y); cs.line_to(970, floor_y)
        cs.set_source_rgba(1, 1, 1, 0.45 * w6); cs.set_line_width(2.0); cs.stroke()

        # RIGHT PEDESTAL: Nominal Number (۱۰۰ میلیون ثابت — height stays 460px!)
        r_px, col_w, full_col_h = 745.0, 250.0, 450.0
        h_nom = full_col_h * p6
        rounded_rect_path(cs, r_px - col_w / 2, floor_y - h_nom, col_w, h_nom, 10)
        cs.set_source_rgba(1, 1, 1, 0.42 * w6); cs.set_line_width(2.0); cs.stroke()
        sp_n1 = get_fitted_text_sprite("۱۰۰ میلیون", fonts.bold_44, col_w - 36, (220, 220, 232, 255))
        sp_n2 = get_fitted_text_sprite("عددِ روی دفترچه", fonts.reg_26, col_w - 36, (170, 170, 182, 255))
        sp_n3 = get_fitted_text_sprite("بعد از ۲ سال: ثابت", fonts.light_22, col_w - 36, (155, 155, 168, 255))
        txts.append((sp_n1, r_px, floor_y - h_nom * 0.62, w6 * p6))
        txts.append((sp_n2, r_px, floor_y - h_nom * 0.42, w6 * p6))
        txts.append((sp_n3, r_px, floor_y + 44, w6 * p6))

        # LEFT PEDESTAL + HUMAN FIGURE: Real Purchasing Power sinking below 50%!
        l_px = 335.0
        t_hlf = t_cues["s6_half"]
        drop_u = ease_in_out_cubic(clamp((t - (t_s6 + 0.9)) / max(1.0, (t_hlf - t_s6 + 0.3))))
        h_real = full_col_h * p6 * (1.0 - 0.58 * drop_u)

        # Ghost outline of original 100% height
        cs.set_dash([8, 8]); cs.set_source_rgba(1, 1, 1, 0.25 * w6); cs.set_line_width(1.5)
        cs.rectangle(l_px - col_w / 2, floor_y - full_col_h, col_w, full_col_h); cs.stroke(); cs.set_dash([])

        # Solid glowing shrunken real-power pedestal + Human standing on top!
        for ctx, lw, al in ((cs, 2.6, w6 * 0.96), (cg, 5.4, w6 * 0.55)):
            rounded_rect_path(ctx, l_px - col_w / 2, floor_y - h_real, col_w, h_real, 10)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()

        draw_human_figure(cs, l_px, floor_y - h_real, scale=0.98, alpha=w6 * 0.96, draw_p=p6, vortex=(drop_u > 0.45), t=t)
        real_val = int(round(100 - 58 * drop_u))
        sp_rv = get_fitted_text_sprite(f"زورِ واقعی: {real_val}", fonts.bold_36, col_w - 32, (255, 255, 255, 255), glow=0.65)
        sp_rl = get_fitted_text_sprite("قدرتِ خریدِ همان پول!", fonts.bold_30, 310, (250, 250, 255, 255), glow=0.35)
        txts.append((sp_rv, l_px, floor_y - h_real * 0.5, w6 * p6))
        txts.append((sp_rl, l_px, floor_y + 44, w6 * p6))

        if drop_u > 0.55:
            draw_stamp_badge(cs, cg, txts, "نصفِ زورش پرید!", 540, 745, -9.0, fonts.bold_44, w6, clamp((drop_u - 0.55) * 2.2))

    # =========================================================================
    # SCENE 7: Wealthy Mindset Shift — Banknotes vs Real Assets & Rare Skills
    # =========================================================================
    w7 = window_fade(t, t_s7 - 0.15, t_s8 + 0.20, fi=0.32, fo=0.32)
    if w7 > 0.01:
        lt = max(0.0, t - t_s7)
        p7 = ease_out_cubic(lt / 0.8)
        draw_pill_badge(cs, cg, txts, "قانونِ ثروتمندها: تغییرِ واحدِ اندازه‌گیریِ ذهن", 540, 385, fonts.bold_30, w7 * p7, glow=True)

        # Left Half: Counting Shrinking Toman Bills (faded)
        draw_human_figure(cs, 265, 1195, scale=1.0, alpha=w7 * 0.42, draw_p=p7, vortex=True, t=t)
        draw_safe_card(
            cs, cg, txts, 265, 765, 340, 220,
            [
                ("نگاهِ تله‌خورده", fonts.bold_30, -56, (175, 175, 185, 255), 0.0),
                ("شمارشِ عددِ تومن", fonts.reg_26, 8, (155, 155, 165, 255), 0.0),
                ("و دلخوشی به فیشِ حقوق", fonts.light_22, 62, (140, 140, 150, 255), 0.0),
            ],
            radius=14, pad_x=26, alpha=w7 * p7 * 0.65, allow_expand=False
        )

        # Center vertical divider
        cs.set_dash([8, 8]); cs.set_source_rgba(1, 1, 1, 0.24 * w7); cs.set_line_width(1.5)
        cs.move_to(500, 485); cs.line_to(500, 1295); cs.stroke(); cs.set_dash([])

        # Right Half: Conscious Wealth Builder + Upward Spotlight + 3 Asset Shields!
        draw_human_figure(cs, 770, 1195, scale=1.12, alpha=w7 * 0.98, draw_p=p7, star_mind=True, t=t)
        draw_human_figure(cg, 770, 1195, scale=1.12, alpha=w7 * 0.55, draw_p=1.0, star_mind=True, t=t)
        draw_spotlight_cone(cs, cg, 770, 1025, 535, 1005, 505, alpha=w7 * p7 * 0.85)

        shields = [
            (770, 575, "۱. داراییِ واقعی و ضدتورم"),
            (770, 705, "۲. مهارتِ کمیاب و ارزشمند"),
            (770, 835, "۳. سرمایه‌ی مولد به جای پولِ نقد"),
        ]
        for si, (sx, sy, stxt) in enumerate(shields):
            sp_s = spring_pop((lt - 0.18 * si) / 0.5)
            if sp_s > 0.02:
                draw_safe_card(
                    cs, cg, txts, sx, sy, 415, 96,
                    [(stxt, fonts.bold_30, 0, (255, 255, 255, 255), 0.55)],
                    radius=12, pad_x=28, alpha=w7 * clamp(sp_s), glow_border=True, allow_expand=False
                )
        draw_pill_badge(cs, cg, txts, "سپرِ حفظِ ارزشِ عمر", 770, 1275, fonts.bold_30, w7 * p7, glow=True)

    # =========================================================================
    # SCENE 8: Viral Interactive Comment Question (کدوم جلوتر دویده؟)
    # =========================================================================
    w8 = window_fade(t, t_s8 - 0.15, t_endplate + 0.22, fi=0.28, fo=0.42)
    if w8 > 0.01:
        lt = max(0.0, t - t_s8)
        p8 = spring_pop(lt / 0.65)
        draw_pill_badge(cs, cg, txts, "نوبتِ تو؛ توی کامنت بنویس کدوم جلوتره؟", 540, 445, fonts.bold_30, w8 * clamp(p8), glow=True)

        # Option 1 (Right Card): عدد حقوقم
        draw_safe_card(
            cs, cg, txts, 765, 845, 390, 360,
            [
                ("گزینه‌ی اول", fonts.light_26, -105, (185, 185, 198, 255), 0.0),
                ("عددِ حقوق و درآمدم", fonts.bold_36, -10, (245, 245, 252, 255), 0.4),
                ("جلوتر از تورم دویده!", fonts.reg_26, 75, (195, 195, 208, 255), 0.0),
            ],
            radius=20, pad_x=30, alpha=w8 * clamp(p8), allow_expand=False
        )

        # Option 2 (Left Card — Glowing pulse!): سرعت خرج‌هام!
        pulse_g = 0.65 + 0.35 * math.sin(t * 6.0)
        draw_safe_card(
            cs, cg, txts, 315, 845, 390, 360,
            [
                ("گزینه‌ی دوم", fonts.light_26, -105, (220, 220, 235, 255), 0.0),
                ("سرعتِ خرج‌های زندگیم", fonts.bold_36, -10, (255, 255, 255, 255), 0.75 * pulse_g),
                ("خیلی جلوتر دویده!", fonts.bold_30, 75, (255, 255, 255, 255), 0.45),
            ],
            radius=20, pad_x=30, alpha=w8 * clamp(p8), glow_border=True, allow_expand=False
        )

        draw_pill_badge(cs, cg, txts, "۱ یا ۲ ؟", 540, 1185, fonts.bold_44, w8 * clamp(p8), glow=True, pad_x=44, pad_y=16)

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
    sub_idx = min(15, len(meta["sub_lines"]) - 2)
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
        tc["s1_28m"] + 0.35,        # P1: Paycheck 20M -> 28M
        tc["s1_shock"] + 0.65,      # P2: Stamp [-۴ میلیون فقیرتر!]
        tc["s2_tread"] + 1.5,       # P3: Running human on mechanical treadmill
        tc["s2_term"] + 0.85,       # P4: Dossier "توهم پولی و مالیات نامرئی"
        tc["s3_melt"] + 0.75,       # P5: Brain card vs Melting ice pillar
        tc["s4_math"] + 1.4,        # P6: Dual baskets before shrink
        tc["s4_shrink"] + 0.85,     # P7: Dual baskets 10 vs 8 (-20%)
        tc["s5_steal"] + 0.75,      # P8: Zero bank SMS vs silent purchasing-power siphon
        tc["s6_half"] + 0.75,       # P9: 100M idle cash pedestal sinking <50%
        tc["s7_rich"] + 2.4,        # P10: Wealthy 3 asset shields
        tc["s8_cta"] + 1.4,         # P11: Binary interactive CTA (1 or 2?)
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
        raise SystemExit("Usage: python ep03_invisible_tax.py --cloud-render <font_dir> <work_dir> <out_mp4> <qa_dir> [whisper_size]")
