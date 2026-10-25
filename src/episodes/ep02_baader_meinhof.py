"""
Episode 02 — Baader-Meinhof Phenomenon / Frequency Illusion (توهم فرکانس)
Page: زاویه ذهن (@zavieh.penhann)
Engine v2:
  - Voice: Gemini Rasalgethi + 129-tap @ensan.besham Spectral-Match FIR + -0.34st Formant Calibration (0.9433 MFCC match)
  - Subtitles: 26 short single-line RTL phrases @ constant 40px Vazirmatn-Medium + 64px-feathered 60fps gradient wipe
  - Visuals: 9 rich @ensan.besham-grade architectural/human/HUD scenes + progressive stroke-draw + 60fps camera motion
"""
import os, sys, json, math, time, subprocess
import cairocffi as cairo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.engine.audio_master import build_episode_audio, LOCKED_SIGNATURE_VOICE
from src.engine.render_core import (
    W, H, FPS, fa, clamp, ease_out_cubic, ease_in_out_cubic, spring_pop, window_fade,
    FontBank, get_text_sprite, get_fitted_text_sprite, set_stroke_draw, rounded_rect_path, draw_star4, draw_stipple_line,
    draw_human_figure, draw_pill_badge, draw_folder_window, draw_stamp_badge,
    draw_tehran_skyline, draw_spotlight_cone, draw_hud_chrome, composite_oled_frame
)

EP_CODE = "02"
EP_TITLE = "توهم فرکانس"

TTS_PROMPT = (
    "Read this Persian psychological reel script in a calm, warm, charismatic, intellectual Tehrani male voice, "
    "like a seasoned documentary storyteller speaking intimately late at night. Keep a natural, steady, engaging "
    "conversational flow (~142 words per minute) with subtle curiosity on the opening question and grounded authority "
    "on the scientific insights."
)

# 26 short (4-7 word) phrases so EVERY subtitle line renders at constant 40px on one exact baseline!
SCRIPT_SEGMENTS = [
    ("شده تا حالا یه کلمه‌ی جدید بشنوی،",              "شده تا حالا یه کلمه‌ی جدید بشنوی،"),
    ("یا چشمت به یه ماشینِ خاص بیفته،",                "یا چشمت به یه ماشین خاص بیفته،"),
    ("و دقیقاً از فرداش توی هر خیابون،",               "و دقیقاً از فرداش توی هر خیابون،"),
    ("و هر صفحه‌ای همون رو ببینی؟",                   "و هر صفحه‌ای همون رو ببینی؟"),
    ("خیلی‌ها می‌گن دنیا داره نشونه می‌فرسته؛",         "خیلی‌ها می‌گن دنیا داره نشونه می‌فرسته؛"),
    ("ولی مغزت داره سرت کلاه می‌ذاره!",                "ولی مغزت داره سرت کلاه می‌ذاره!"),
    ("اسمِ علمیِ این اتفاق،",                          "اسم علمی این اتفاق،"),
    ("پدیده‌ی بادر ماینهوف یا توهمِ فرکانسه.",          "پدیده‌ی بادر-ماینهوف یا توهم فرکانسه."),
    ("مغزِ ما توی هر ثانیه،",                          "مغز ما توی هر ثانیه،"),
    ("با یازده میلیون بیت اطلاعات بمباران می‌شه؛",      "با ۱۱ میلیون بیت اطلاعات بمباران می‌شه؛"),
    ("اما بخشِ خودآگاهِ ما فقط می‌تونه،",               "اما بخش خودآگاه ما فقط می‌تونه،"),
    ("چهل بیت از اون رو پردازش کنه!",                 "۴۰ بیت از اون رو پردازش کنه!"),
    ("پس یه فیلترِ عصبیِ هوشمند تو مغزمون،",            "پس یه فیلتر عصبی هوشمند تو مغزمون،"),
    ("نود و نه درصدِ چیزها رو سانسور می‌کنه؛",          "۹۹ درصد چیزها رو سانسور می‌کنه؛"),
    ("تا وقتی یه موضوع برات مهم بشه.",                 "تا وقتی یه موضوع برات مهم بشه."),
    ("همون لحظه سوژه می‌ره تو لیستِ ویژه!",             "همون لحظه سوژه می‌ره تو لیست ویژه!"),
    ("تعدادِ اون ماشین تو شهر زیاد نشده؛",             "تعداد اون ماشین تو شهر زیاد نشده؛"),
    ("فقط رادارِ پنهانِ مغزت روش قفل کرده.",            "فقط رادار پنهان مغزت روش قفل کرده."),
    ("بعدش هم سوگیریِ تأیید واردِ بازی می‌شه:",         "بعدش هم سوگیری تأیید وارد بازی می‌شه:"),
    ("هر بار می‌بینیش، مغزت امتیاز ثبت می‌کنه،",        "هر بار می‌بینیش، مغزت امتیاز ثبت می‌کنه،"),
    ("و هزار بار ندیدنش رو نادیده می‌گیره!",           "و هزار بار ندیدنش رو نادیده می‌گیره!"),
    ("حالا بخشِ ترسناکِ ماجرا کجاست؟",                 "حالا بخش ترسناک ماجرا کجاست؟"),
    ("اگه فکرت درگیرِ شک و ترس باشه،",                 "اگه فکرت درگیر شک و ترس باشه،"),
    ("مغزت همه‌جا دنبالِ اثباتِ همون ترس می‌گرده.",      "مغزت همه‌جا دنبال اثبات همون ترس می‌گرده."),
    ("دنیا همونه؛ زاویه‌ی ذهنت انتخابت می‌کنه.",        "دنیا همونه؛ زاویه‌ی ذهنت انتخابت می‌کنه."),
    ("رادارِ ذهنِ تو الان رو چی قفله؟",                "رادار ذهن تو الان رو چی قفله؟"),
]

SFX_CUE_MAP = [
    ("s1_lock",   1, 3, "ping"),    # ماشین خاص
    ("s2_start",  2, 0, "whoosh"),  # و دقیقاً از فرداش
    ("s3_myth",   4, 0, "whoosh"),  # خیلی‌ها می‌گن
    ("s3_title",  7, 1, "ping"),    # بادر-ماینهوف
    ("s4_flood",  8, 0, "whoosh"),  # مغز ما توی هر ثانیه
    ("s4_40bit", 11, 0, "ping"),    # ۴۰ بیت
    ("s5_filter",12, 0, "whoosh"),  # پس یه فیلتر عصبی
    ("s5_stamp", 13, 3, "stamp"),   # سانسور می‌کنه
    ("s6_vip",   15, 4, "ping"),    # لیست ویژه
    ("s7_scale", 18, 0, "whoosh"),  # سوگیری تأیید
    ("s7_point", 19, 3, "ping"),    # امتیاز
    ("s8_dark",  21, 0, "whoosh"),  # بخش ترسناک
    ("s9_angle", 24, 0, "chime"),   # زاویه‌ی ذهنت
]


def draw_car_icon(ctx, cx: float, cy: float, sc: float = 1.0, alpha: float = 1.0, lw: float = 2.0):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(sc, sc)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.set_line_width(lw / max(0.4, sc))
    # Sleek minimalist coupe silhouette
    ctx.move_to(-46, 10)
    ctx.line_to(-42, -3)
    ctx.line_to(-22, -5)
    ctx.line_to(-10, -18)
    ctx.line_to(18, -18)
    ctx.line_to(30, -5)
    ctx.line_to(46, -2)
    ctx.line_to(46, 10)
    ctx.close_path()
    ctx.stroke()
    # Window cabin divider
    ctx.move_to(3, -18); ctx.line_to(3, -5); ctx.stroke()
    # Wheels
    ctx.arc(-25, 11, 8.5, 0, 2 * math.pi); ctx.stroke()
    ctx.arc(25, 11, 8.5, 0, 2 * math.pi); ctx.stroke()
    ctx.restore()


def apply_camera(ctx, zoom: float, pan_x: float = 0.0, pan_y: float = 0.0):
    ctx.translate(W * 0.5 + pan_x, H * 0.48 + pan_y)
    ctx.scale(zoom, zoom)
    ctx.translate(-W * 0.5, -H * 0.48)


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

    t_s2 = t_cues["s2_start"]
    t_s3 = t_cues["s3_myth"]
    t_s4 = t_cues["s4_flood"]
    t_s5 = t_cues["s5_filter"]
    t_s6 = t_cues["s6_vip"] - 0.7
    t_s7 = t_cues["s7_scale"]
    t_s8 = t_cues["s8_dark"]
    t_s9 = t_cues["s9_angle"] - 0.25
    t_endplate = total_dur - 3.9

    chapters = [0.0, t_s2, t_s3, t_s4, t_s5, t_s6, t_s7, t_s8, t_s9]
    draw_hud_chrome(cs, cg, txts, fonts, t, total_dur, EP_CODE, EP_TITLE, chapters)

    # =========================================================================
    # SCENE 1: Tehran Skyline (Milad + Azadi) + Human Observer + Target Lock
    # =========================================================================
    w1 = window_fade(t, 0.0, t_s2 + 0.25, fi=0.25, fo=0.35)
    if w1 > 0.01:
        u1 = clamp(t / max(0.1, t_s2))
        zoom1 = 1.0 + 0.055 * u1
        draw_p1 = ease_out_cubic(t / 1.6)
        cs.save(); cg.save()
        apply_camera(cs, zoom1, pan_y=-12 * u1)
        apply_camera(cg, zoom1, pan_y=-12 * u1)

        # Architectural Tehran skyline at horizon y=760
        draw_tehran_skyline(cs, cg, 760.0, alpha=w1, draw_p=draw_p1)
        draw_pill_badge(cs, cg, txts, "تهران — مشاهده‌ی روزمره", 540, 465, fonts.reg_26, w1 * ease_out_cubic(t / 0.9))

        # Foreground multi-lane boulevard
        for ly in (915, 1045, 1175):
            cs.set_source_rgba(1, 1, 1, 0.14 * w1); cs.set_line_width(1.2)
            cs.move_to(75, ly); cs.line_to(1005, ly); cs.stroke()
            draw_stipple_line(cs, 95, ly + 65, 985, ly + 65, 22, r=1.2, alpha=0.14 * w1)

        # Observer human figure standing on sidewalk pedestal watching traffic
        draw_human_figure(cs, 195, 910, scale=0.92, alpha=w1 * 0.92, draw_p=ease_out_cubic(t / 1.1), star_mind=(t >= t_cues["s1_lock"]), t=t)
        if t >= t_cues["s1_lock"]:
            draw_human_figure(cg, 195, 910, scale=0.92, alpha=w1 * 0.45, draw_p=1.0, star_mind=True, t=t)

        # Passing muted cars + 1 locked target car
        t_lock = t_cues["s1_lock"]
        lock_p = spring_pop((t - t_lock) / 0.55) if t >= t_lock else 0.0
        cars = [
            (0, 980,  135, 0.0, False),
            (1, 980,  135, 0.48, False),
            (2, 1110, -145, 0.22, True),   # HERO TARGET CAR!
            (3, 1110, -145, 0.72, False),
            (4, 1240, 125, 0.35, False),
        ]
        for idx, cy, spd, ph, is_hero in cars:
            cx = 90 + ((t * spd + ph * 880) % 900)
            if is_hero and t >= t_lock - 0.4:
                # Smoothly arrest/center hero car near x=630 for dramatic radar lock
                freeze = ease_out_cubic((t - (t_lock - 0.4)) / 0.8)
                cx = cx * (1.0 - freeze) + 635.0 * freeze
                al = (0.28 + 0.72 * clamp((t - t_lock + 0.2) / 0.35)) * w1
                draw_car_icon(cs, cx, cy, sc=1.18, alpha=al, lw=2.5)
                if lock_p > 0.02:
                    draw_car_icon(cg, cx, cy, sc=1.18, alpha=w1 * 0.85 * lock_p, lw=4.8)
                    # Precision corner-bracket reticle + radar pulse
                    bw, bh = 84 * (1.28 - 0.28 * lock_p), 44 * (1.28 - 0.28 * lock_p)
                    for ctx, lw, a2 in ((cs, 2.2, w1 * 0.95), (cg, 4.5, w1 * 0.65)):
                        ctx.set_source_rgba(1, 1, 1, a2); ctx.set_line_width(lw)
                        for sx in (-1, 1):
                            for sy in (-1, 1):
                                ctx.move_to(cx + sx * bw, cy + sy * (bh - 15))
                                ctx.line_to(cx + sx * bw, cy + sy * bh)
                                ctx.line_to(cx + sx * (bw - 20), cy + sy * bh)
                                ctx.stroke()
                    # Dotted sightline from human head to locked car!
                    draw_stipple_line(cs, 195, 774, cx - bw, cy - 10, 18, r=1.8, alpha=w1 * 0.65 * lock_p)
                    rp = (t - t_lock) % 1.25
                    cs.arc(cx, cy, 34 + rp * 95, 0, 2 * math.pi)
                    cs.set_source_rgba(1, 1, 1, w1 * (1.0 - rp / 1.25) * 0.55); cs.set_line_width(1.5); cs.stroke()
                    draw_pill_badge(cs, cg, txts, "سوژه‌ی خاص: ثبت در حافظه", cx, cy - 84, fonts.bold_30, w1 * clamp(lock_p), glow=True)
            else:
                draw_car_icon(cs, cx, cy, sc=0.92, alpha=0.20 * w1, lw=1.6)

        cs.restore(); cg.restore()

    # =========================================================================
    # SCENE 2: Omnipresence Overload — 8 City/Screen Cards Surrounding Vortex Human
    # =========================================================================
    w2 = window_fade(t, t_s2 - 0.15, t_s3 + 0.22, fi=0.32, fo=0.35)
    if w2 > 0.01:
        lt = max(0.0, t - t_s2)
        u2 = clamp(lt / max(0.1, t_s3 - t_s2))
        cs.save(); cg.save()
        apply_camera(cs, 1.05 - 0.04 * u2)
        apply_camera(cg, 1.05 - 0.04 * u2)

        draw_pill_badge(cs, cg, txts, "فردایِ همان روز: تکرار در همه‌جا!", 540, 390, fonts.bold_30, w2, glow=True)

        # Central human figure with spinning head vortex!
        hx, hy = 540.0, 1035.0
        draw_human_figure(cs, hx, hy, scale=1.18, alpha=w2 * 0.96, draw_p=ease_out_cubic(lt / 0.7), vortex=True, t=t)
        draw_human_figure(cg, hx, hy, scale=1.18, alpha=w2 * 0.55, draw_p=1.0, vortex=True, t=t)
        # Pedestal ring under figure
        cs.save(); cs.translate(hx, hy + 6); cs.scale(1.0, 0.26)
        cs.arc(0, 0, 74, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.45 * w2); cs.set_line_width(2.0); cs.stroke()
        cs.restore()

        # 8 Surrounding urban/digital nodes (street, mobile feed, billboard, podcast, shop, taxi, news, chat)
        ring_nodes = [
            (235, 595, "بیلبوردِ اتوبان"),
            (540, 535, "استوریِ اینستاگرام"),
            (845, 595, "سرِ چهارراه"),
            (195, 885, "پادکستِ صبحگاهی"),
            (885, 885, "ویترینِ مغازه"),
            (235, 1210, "تاکسیِ عبوری"),
            (540, 1285, "تیترِ خبرها"),
            (845, 1210, "گفتگویِ جمع"),
        ]
        for i, (nx, ny, lbl) in enumerate(ring_nodes):
            act = spring_pop((lt - 0.22 * i) / 0.48)
            if act <= 0.02:
                continue
            al = w2 * clamp(act)
            cw, ch = 210 * act, 118 * act
            rounded_rect_path(cs, nx - cw / 2, ny - ch / 2, cw, ch, 12)
            cs.set_source_rgba(0.03, 0.03, 0.04, 0.90 * al); cs.fill_preserve()
            cs.set_source_rgba(1, 1, 1, 0.72 * al); cs.set_line_width(1.9); cs.stroke()

            rounded_rect_path(cg, nx - cw / 2, ny - ch / 2, cw, ch, 12)
            cg.set_source_rgba(1, 1, 1, 0.35 * al); cg.set_line_width(4.0); cg.stroke()

            draw_car_icon(cs, nx, ny - 12, sc=0.68 * act, alpha=0.92 * al, lw=2.0)
            sp_n = get_fitted_text_sprite(lbl, fonts.light_22, max(80.0, cw - 34.0), color=(205, 205, 215, 255))
            txts.append((sp_n, nx, ny + 34, al))

            # Dotted ray converging straight into observer's mind!
            draw_stipple_line(cs, nx, ny, hx, hy - 175, 11, r=1.5, alpha=0.38 * al)

        cs.restore(); cg.restore()

    # =========================================================================
    # SCENE 3: Cosmic Sign Myth [✕] -> Baader-Meinhof Scientific Folder Dossier
    # =========================================================================
    w3 = window_fade(t, t_s3 - 0.15, t_s4 + 0.22, fi=0.32, fo=0.35)
    if w3 > 0.01:
        lt = max(0.0, t - t_s3)
        t_ttl = t_cues["s3_title"]

        # Top Card: "نشانه‌ی کائنات؟" Mystical Eye Pyramid -> Struck out when science arrives!
        top_p = ease_out_cubic(lt / 0.85)
        strike_p = ease_out_cubic((t - (t_ttl - 1.5)) / 0.45) if t >= (t_ttl - 1.5) else 0.0
        dim_myth = 1.0 - 0.45 * strike_p

        draw_folder_window(cs, cg, txts, 540, 625, 760, 290, "باورِ رایج", fonts.reg_26, w3 * dim_myth, top_p)
        # Mystical All-Seeing Eye inside triangle on right side of top card
        ex, ey = 740, 625
        set_stroke_draw(cs, top_p, 420.0)
        cs.set_source_rgba(1, 1, 1, 0.78 * w3 * dim_myth); cs.set_line_width(2.0)
        cs.move_to(ex, ey - 82); cs.line_to(ex - 92, ey + 68); cs.line_to(ex + 92, ey + 68); cs.close_path(); cs.stroke()
        cs.set_dash([])
        cs.move_to(ex - 48, ey + 15)
        cs.curve_to(ex - 20, ey - 18, ex + 20, ey - 18, ex + 48, ey + 15)
        cs.curve_to(ex + 20, ey + 48, ex - 20, ey + 48, ex - 48, ey + 15); cs.stroke()
        cs.arc(ex, ey + 15, 12, 0, 2 * math.pi); cs.fill()

        dim_myth_txt = 1.0 - 0.80 * strike_p
        sp_m1 = get_text_sprite("«دنیا داره بهم نشونه می‌ده!»", fonts.bold_36, (235, 235, 242, 255))
        txts.append((sp_m1, 395, 608, w3 * top_p * dim_myth_txt))
        sp_m2 = get_text_sprite("تعبیرِ خرافی از یک خطایِ توجه", fonts.light_26, (165, 165, 175, 255))
        txts.append((sp_m2, 395, 668, w3 * top_p * dim_myth_txt))

        if strike_p > 0.02:
            # Crisp X strike over pyramid + angled stamp!
            for ctx, lw, al in ((cs, 3.2, w3 * 0.92), (cg, 6.0, w3 * 0.65)):
                ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
                ctx.move_to(ex - 85, ey - 65); ctx.line_to(ex - 85 + 170 * strike_p, ey - 65 + 145 * strike_p); ctx.stroke()
                ctx.move_to(ex + 85, ey - 65); ctx.line_to(ex + 85 - 170 * strike_p, ey - 65 + 145 * strike_p); ctx.stroke()
            draw_stamp_badge(cs, cg, txts, "خطایِ شناختی", 355, 625, -9.0, fonts.bold_36, w3, strike_p)

        # Bottom Hero Folder Window: Scientific Diagnosis "پدیده‌ی بادر-ماینهوف"
        if t >= t_ttl - 0.7:
            sci_p = ease_out_cubic((t - (t_ttl - 0.7)) / 0.85)
            draw_folder_window(cs, cg, txts, 540, 1115, 860, 410, "تشخیصِ عصب‌شناسی", fonts.bold_30, w3, sci_p)
            sp_b1 = get_text_sprite("پدیده‌ی بادر-ماینهوف", fonts.bold_52, (255, 255, 255, 255), glow=0.85)
            txts.append((sp_b1, 540, 1045, w3 * sci_p))
            draw_pill_badge(cs, cg, txts, "نامِ دیگر: توهمِ فرکانس", 540, 1145, fonts.med_32, w3 * sci_p, glow=True)

            # Live frequency pulse wave along bottom of dossier card
            cs.set_source_rgba(1, 1, 1, 0.55 * w3 * sci_p); cs.set_line_width(1.8)
            for ix in range(180, 901, 6):
                env = math.exp(-((ix - 540) / 170.0) ** 2)
                wy = 1248 + math.sin(ix * 0.065 - t * 9.0) * 28.0 * env * sci_p
                if ix == 180:
                    cs.move_to(ix, wy)
                else:
                    cs.line_to(ix, wy)
            cs.stroke()

    # =========================================================================
    # SCENE 4: 11,000,000 Bits Sensory Deluge -> 40-Bit Conscious Bottleneck
    # =========================================================================
    w4 = window_fade(t, t_s4 - 0.15, t_s5 + 0.22, fi=0.32, fo=0.35)
    if w4 > 0.01:
        lt = max(0.0, t - t_s4)
        cnt_p = ease_out_cubic(lt / 1.2)
        val_m = int(round(11_000_000 * cnt_p))
        sp_11m = get_text_sprite(fa(f"{val_m:,}"), fonts.eb_84, (255, 255, 255, 255), glow=0.75)
        txts.append((sp_11m, 540, 395, w4))
        draw_pill_badge(cs, cg, txts, "بیت اطلاعاتِ محیطی در هر ثانیه", 540, 488, fonts.reg_26, w4)

        # Architectural Sensory Funnel (y: 620 -> 960 -> neck 1070)
        fn_p = ease_out_cubic(lt / 0.9)
        for ctx, lw, al in ((cs, 2.3, w4 * 0.88), (cg, 5.0, w4 * 0.42)):
            set_stroke_draw(ctx, fn_p, 800.0)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            ctx.move_to(130, 610); ctx.line_to(496, 945); ctx.line_to(496, 1095); ctx.stroke()
            ctx.move_to(950, 610); ctx.line_to(584, 945); ctx.line_to(584, 1095); ctx.stroke()
            ctx.set_dash([])

        # 56 Cascading vertical sensory streams pouring into funnel; 98% deflect off walls!
        for i in range(56):
            sx = 155 + (i * 14.1)
            spd = 340 + (i % 5) * 65
            sy = 545 + ((lt * spd + i * 47) % 390)
            # Funnel wall y at this x
            dist_c = abs(sx - 540.0)
            wall_y = 945.0 - max(0.0, (dist_c - 44.0)) * (335.0 / 366.0)
            if dist_c > 36.0 and sy > wall_y:
                # Deflected sideways spark!
                over = sy - wall_y
                dx = sx + (1 if sx > 540 else -1) * over * 0.85
                dy = wall_y - over * 0.22
                al_p = clamp(1.0 - over / 130.0) * 0.35 * w4
                cs.arc(dx, dy, 2.0, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, al_p); cs.fill()
            else:
                cs.move_to(sx, sy); cs.line_to(sx, sy + 18)
                cs.set_source_rgba(1, 1, 1, 0.32 * w4); cs.set_line_width(1.5); cs.stroke()

        # Pure 40-bit conscious pearl stream emerging through narrow neck (x=540)
        t_40 = t_cues["s4_40bit"]
        p40 = ease_out_cubic((t - (t_40 - 0.8)) / 0.7) if t >= (t_40 - 0.8) else 0.25
        for k in range(6):
            py = 965 + ((lt * 210 + k * 42) % 245)
            for ctx, r, al in ((cs, 4.8, w4 * 0.96), (cg, 9.5, w4 * 0.78)):
                ctx.arc(540, py, r, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, al * p40); ctx.fill()

        # Human conscious observer at bottom receiving the 40-bit stream + [ ۴۰ بیت ] card!
        draw_human_figure(cs, 265, 1385, scale=0.88, alpha=w4 * p40, draw_p=p40, star_mind=True, t=t)
        rounded_rect_path(cs, 365, 1225, 450, 155, 16)
        cs.set_source_rgba(0.03, 0.03, 0.04, 0.94 * w4 * p40); cs.fill_preserve()
        cs.set_source_rgba(1, 1, 1, 0.88 * w4 * p40); cs.set_line_width(2.2); cs.stroke()
        rounded_rect_path(cg, 365, 1225, 450, 155, 16)
        cg.set_source_rgba(1, 1, 1, 0.50 * w4 * p40); cg.set_line_width(4.5); cg.stroke()

        sp_40 = get_text_sprite(fa("فقط ۴۰ بیت!"), fonts.eb_68, (255, 255, 255, 255), glow=0.85)
        sp_40s = get_text_sprite("ظرفیتِ پردازشِ بخشِ خودآگاه", fonts.reg_26, (200, 200, 212, 255))
        txts.append((sp_40, 590, 1280, w4 * p40))
        txts.append((sp_40s, 590, 1345, w4 * p40))

    # =========================================================================
    # SCENE 5: Neural Gatekeeper (فیلتر فعال‌ساز شبکه‌ای) + 99% Censorship Stamp
    # =========================================================================
    w5 = window_fade(t, t_s5 - 0.15, t_s6 + 0.22, fi=0.32, fo=0.35)
    if w5 > 0.01:
        lt = max(0.0, t - t_s5)
        bp = ease_out_cubic(lt / 1.0)
        draw_folder_window(cs, cg, txts, 540, 865, 900, 860, "فیلترِ فعال‌سازِ شبکه‌ای", fonts.bold_30, w5, bp)

        # Geometric Brain Silhouette + Glowing Brainstem Filter Core on left half (cx=340, cy=775)
        bx, by = 335.0, 775.0
        for ctx, lw, al in ((cs, 2.3, w5 * 0.90), (cg, 4.8, w5 * 0.40)):
            set_stroke_draw(ctx, bp, 900.0)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            # Cerebral cortex lobes
            ctx.move_to(bx - 95, by + 35)
            ctx.curve_to(bx - 135, by - 25, bx - 105, by - 115, bx - 25, by - 125)
            ctx.curve_to(bx + 55, by - 140, bx + 135, by - 85, bx + 125, by + 5)
            ctx.curve_to(bx + 120, by + 65, bx + 65, by + 90, bx + 15, by + 82)
            ctx.close_path(); ctx.stroke()
            # Internal neural circuit folds
            ctx.move_to(bx - 65, by - 45); ctx.line_to(bx - 10, by - 45); ctx.line_to(bx + 20, by - 75); ctx.stroke()
            ctx.move_to(bx - 45, by + 10); ctx.line_to(bx + 35, by + 10); ctx.line_to(bx + 65, by - 25); ctx.stroke()
            # Brainstem RAS Gate column
            ctx.move_to(bx - 12, by + 82); ctx.line_to(bx - 22, by + 185)
            ctx.move_to(bx + 24, by + 82); ctx.line_to(bx + 16, by + 185); ctx.stroke()
            ctx.set_dash([])

        # Pulsing RAS Filter Beacon at brainstem!
        pulse_r = 16 + 7 * math.sin(t * 6.5)
        cs.arc(bx + 2, by + 118, 9, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, w5); cs.fill()
        cg.arc(bx + 2, by + 118, pulse_r, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.75 * w5); cg.fill()
        draw_pill_badge(cs, cg, txts, "نگهبانِ ورودیِ ذهن", bx, by + 238, fonts.reg_26, w5 * bp)

        # Right side: 4 Routine Stimuli Rows Rejected + 1 Important Subject Unlocked!
        rows = [
            (635, "چهره‌ی عابرانِ پیاده", False),
            (735, "صدایِ ممتدِ خیابان", False),
            (835, "تابلوها و رنگ‌هایِ تکراری", False),
            (935, "هزاران ماشینِ معمولی", False),
            (1135, "سوژه‌ی جدید و مهمِ تو!", True),
        ]
        t_st = t_cues["s5_stamp"]
        st_p = clamp((t - t_st) / 0.42) if t >= t_st else 0.0
        vip_early = clamp((t - (t_s6 - 1.5)) / 0.55) if t >= (t_s6 - 1.5) else 0.0

        for ri, (ry, rtxt, is_vip) in enumerate(rows):
            rp = ease_out_cubic((lt - 0.15 * ri) / 0.5)
            if rp <= 0.02:
                continue
            if not is_vip:
                dim_r = 1.0 - 0.52 * st_p
                rounded_rect_path(cs, 520, ry - 34, 415, 68, 10)
                cs.set_source_rgba(1, 1, 1, 0.28 * w5 * rp * dim_r); cs.set_line_width(1.4); cs.stroke()
                sp_r = get_text_sprite(rtxt, fonts.reg_26, (185, 185, 195, 255))
                txts.append((sp_r, 728, ry, w5 * rp * dim_r))
            else:
                if vip_early > 0.02:
                    draw_pill_badge(cs, cg, txts, rtxt, 695, ry, fonts.bold_30, w5 * vip_early, glow=True, pad_x=38, pad_y=16)
                    draw_stipple_line(cs, 495, ry, bx + 12, by + 118, 14, r=2.2, alpha=w5 * vip_early * 0.9)

        if st_p > 0.02:
            draw_stamp_badge(cs, cg, txts, "۹۹٪ سانسور شد", 725, 785, -11.0, fonts.bold_44, w5, st_p)

    # =========================================================================
    # SCENE 6: VIP Priority Watchlist (لیست ویژه) + Spotlight Cone + Reality vs Radar
    # =========================================================================
    w6 = window_fade(t, t_s6 - 0.15, t_s7 + 0.22, fi=0.32, fo=0.35)
    if w6 > 0.01:
        lt = max(0.0, t - t_s6)
        p6 = ease_out_cubic(lt / 0.85)

        # Top Section: Observer Figure on Right Projecting Sweeping Spotlight onto Target Car on Left!
        sweep = math.sin(lt * 2.1) * 32.0
        draw_human_figure(cs, 855, 765, scale=1.05, alpha=w6 * 0.96, draw_p=p6, star_mind=True, t=t)
        draw_human_figure(cg, 855, 765, scale=1.05, alpha=w6 * 0.45, draw_p=1.0, star_mind=True, t=t)
        # Spotlight cone from human's head (855, 610) onto target car at (295, 725)
        draw_spotlight_cone(cs, cg, 832, 610, 175, 415, 775 + sweep * 0.3, alpha=w6 * p6)
        draw_car_icon(cs, 295, 730, sc=1.35, alpha=w6 * p6, lw=2.5)
        draw_car_icon(cg, 295, 730, sc=1.35, alpha=w6 * p6 * 0.8, lw=4.8)
        draw_pill_badge(cs, cg, txts, "قفلِ رادارِ پنهانِ مغز", 295, 635, fonts.bold_30, w6 * p6, glow=True)

        # Bottom Section: Folder Window comparing [ تعداد واقعی در شهر: ثابت ] vs [ حساسیت رادار مغز: ۱۰۰٪ ]
        draw_folder_window(cs, cg, txts, 540, 1145, 880, 460, "لیستِ ویژه‌ی ذهن", fonts.bold_30, w6, p6)

        # Dual telemetry graph inside folder window!
        gx0, gx1 = 165.0, 915.0
        # 1. Flat dashed line: Real count in city (unchanged!)
        cs.set_dash([10, 8])
        cs.set_source_rgba(1, 1, 1, 0.38 * w6 * p6); cs.set_line_width(2.0)
        cs.move_to(gx0, 1255); cs.line_to(gx0 + (gx1 - gx0) * p6, 1255); cs.stroke()
        cs.set_dash([])
        sp_flat = get_text_sprite("تعدادِ واقعی در شهر: کاملاً ثابت", fonts.reg_26, (165, 165, 175, 255))
        txts.append((sp_flat, 360, 1295, w6 * p6))

        # 2. Glowing step-surge curve: Brain Radar Sensitivity leaping to 100%!
        surge_p = ease_out_cubic((lt - 0.55) / 1.1)
        for ctx, lw, al in ((cs, 3.0, w6 * 0.96), (cg, 6.5, w6 * 0.72)):
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            N = 70
            for k in range(int(N * surge_p) + 1):
                u = k / N
                px = gx0 + (gx1 - gx0) * u
                step = 1.0 / (1.0 + math.exp(-(u - 0.42) * 18.0))
                py = 1235 - step * 205.0
                if k == 0:
                    ctx.move_to(px, py)
                else:
                    ctx.line_to(px, py)
            ctx.stroke()

        if surge_p > 0.45:
            draw_pill_badge(cs, cg, txts, "حساسیتِ رادارِ مغز: ۱۰۰٪", 725, 995, fonts.bold_30, w6 * clamp((surge_p - 0.45) * 2.0), glow=True)

    # =========================================================================
    # SCENE 7: Confirmation Bias Precision Balance Scale (سوگیری تأیید)
    # =========================================================================
    w7 = window_fade(t, t_s7 - 0.15, t_s8 + 0.22, fi=0.32, fo=0.35)
    if w7 > 0.01:
        lt = max(0.0, t - t_s7)
        p7 = ease_out_cubic(lt / 0.85)
        draw_pill_badge(cs, cg, txts, "مکانیزمِ دوم: سوگیریِ تأیید", 540, 415, fonts.bold_36, w7 * p7, glow=True)

        # Impact when "+1 امتیاز" hits!
        t_pt = t_cues["s7_point"]
        tilt_p = spring_pop((t - t_pt) / 0.65) if t >= t_pt else 0.0
        tilt_rad = math.radians(17.5 * tilt_p)  # Right side (1 sighting) slams heavily down!

        # Central architectural fulcrum pillar (x=540, y_pivot=790, base=1290)
        px, py = 540.0, 815.0
        for ctx, lw, al in ((cs, 2.4, w7 * 0.88), (cg, 4.8, w7 * 0.35)):
            set_stroke_draw(ctx, p7, 700.0)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            ctx.move_to(px, py); ctx.line_to(px - 36, 1285); ctx.line_to(px + 36, 1285); ctx.close_path(); ctx.stroke()
            ctx.move_to(px - 135, 1285); ctx.line_to(px + 135, 1285); ctx.stroke()
            ctx.set_dash([])

        # Rotating balance beam (length 680: -340 to +340)
        arm = 330.0
        lx = px - math.cos(tilt_rad) * arm
        ly = py - math.sin(tilt_rad) * arm
        rx = px + math.cos(tilt_rad) * arm
        ry = py + math.sin(tilt_rad) * arm

        for ctx, lw, al in ((cs, 3.0, w7 * 0.95), (cg, 5.5, w7 * 0.48)):
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            ctx.move_to(lx, ly); ctx.line_to(rx, ry); ctx.stroke()
            ctx.arc(px, py, 11, 0, 2 * math.pi); ctx.fill()

        # LEFT PAN: "۱,۰۰۰ بار ندیدن" — permeable ghost pan where hollow circles fall straight through!
        cs.set_source_rgba(1, 1, 1, 0.32 * w7); cs.set_line_width(1.6)
        cs.move_to(lx, ly); cs.line_to(lx - 75, ly + 135); cs.move_to(lx, ly); cs.line_to(lx + 75, ly + 135); cs.stroke()
        cs.set_dash([8, 7])
        cs.move_to(lx - 95, ly + 135); cs.line_to(lx + 95, ly + 135); cs.stroke()
        cs.set_dash([])
        # Ghosted missed sightings falling right through the left pan with zero weight!
        for k in range(14):
            gx = lx - 68 + (k % 5) * 34
            gy = (ly + 20) + ((lt * 145 + k * 39) % 290)
            ga = (1.0 - ((gy - ly) / 310.0)) * 0.30 * w7
            cs.arc(gx, gy, 8.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, max(0.0, ga)); cs.set_line_width(1.3); cs.stroke()
        sp_l1 = get_text_sprite(fa("۱,۰۰۰ بار ندیدن"), fonts.bold_30, (165, 165, 175, 255))
        sp_l2 = get_text_sprite("فراموشیِ کامل (وزن = صفر)", fonts.light_22, (130, 130, 140, 255))
        txts.append((sp_l1, lx, ly - 58, w7 * p7))
        txts.append((sp_l2, lx, ly + 335, w7 * p7))

        # RIGHT PAN: "فقط ۱ بار دیدن!" — solid glowing pan holding a heavy radiant orb!
        for ctx, lw, al in ((cs, 2.4, w7 * 0.95), (cg, 5.0, w7 * 0.65)):
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            ctx.move_to(rx, ry); ctx.line_to(rx - 75, ry + 135); ctx.stroke()
            ctx.move_to(rx, ry); ctx.line_to(rx + 75, ry + 135); ctx.stroke()
            ctx.move_to(rx - 100, ry + 135); ctx.line_to(rx + 100, ry + 135); ctx.stroke()

        if tilt_p > 0.02:
            orb_y = ry + 95
            cs.arc(rx, orb_y, 36 * clamp(tilt_p), 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, w7 * 0.96); cs.fill()
            cg.arc(rx, orb_y, 52 * clamp(tilt_p), 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, w7 * 0.85); cg.fill()
            draw_pill_badge(cs, cg, txts, "+۱ امتیازِ تأیید!", rx, ry - 64, fonts.bold_30, w7 * clamp(tilt_p), glow=True)
            sp_r2 = get_text_sprite("ثبتِ پررنگ در حافظه!", fonts.med_32, (250, 250, 255, 255), glow=0.45)
            txts.append((sp_r2, rx, ry + 205, w7 * clamp(tilt_p)))

    # =========================================================================
    # SCENE 8: The Dark Mirror — Fear / Doubt / Scarcity Radar Loop
    # =========================================================================
    w8 = window_fade(t, t_s8 - 0.15, t_s9 + 0.22, fi=0.32, fo=0.35)
    if w8 > 0.01:
        lt = max(0.0, t - t_s8)
        u8 = clamp(lt / max(0.1, t_s9 - t_s8))
        cs.save(); cg.save()
        apply_camera(cs, 1.0 + 0.07 * u8)  # Claustrophobic push-in!
        apply_camera(cg, 1.0 + 0.07 * u8)

        draw_pill_badge(cs, cg, txts, "هشدار: وقتی رادار رویِ ترس قفل شود", 540, 405, fonts.bold_30, w8, glow=True)

        # Central human figure trapped inside tightening dashed mental prison box!
        hx, hy = 540.0, 1085.0
        draw_human_figure(cs, hx, hy, scale=1.15, alpha=w8 * 0.95, draw_p=ease_out_cubic(lt / 0.6), vortex=True, t=-t * 1.4)
        box_pad = 165.0 - 42.0 * u8
        cs.set_dash([12, 8])
        cs.set_source_rgba(1, 1, 1, 0.52 * w8); cs.set_line_width(2.0)
        cs.rectangle(hx - box_pad, hy - 235, box_pad * 2, 265); cs.stroke()
        cs.set_dash([])

        # Three Towering Dark Monolith Mirrors reflecting proof of Fear, Doubt, Scarcity!
        monoliths = [
            (225, 655, "شک و بدبینی", "«همه غیرقابلِ اعتمادن»"),
            (540, 560, "ترس از شکست", "«حتماً یه جایِ کار می‌لنگه»"),
            (855, 655, "احساسِ کمبود", "«هیچ فرصتی برایِ من نیست»"),
        ]
        for mi, (mx, my, m_title, m_sub) in enumerate(monoliths):
            mp = spring_pop((lt - 0.25 * mi) / 0.55)
            if mp <= 0.02:
                continue
            mw, mh = 250 * mp, 165 * mp
            rounded_rect_path(cs, mx - mw / 2, my - mh / 2, mw, mh, 10)
            cs.set_source_rgba(0.03, 0.03, 0.04, 0.92 * w8 * mp); cs.fill_preserve()
            cs.set_source_rgba(1, 1, 1, 0.80 * w8 * mp); cs.set_line_width(2.1); cs.stroke()
            rounded_rect_path(cg, mx - mw / 2, my - mh / 2, mw, mh, 10)
            cg.set_source_rgba(1, 1, 1, 0.38 * w8 * mp); cg.set_line_width(4.2); cg.stroke()

            sp_mt = get_fitted_text_sprite(m_title, fonts.bold_30, max(90.0, mw - 38.0), color=(255, 255, 255, 255), glow=0.45)
            sp_ms = get_fitted_text_sprite(m_sub, fonts.light_22, max(90.0, mw - 38.0), color=(190, 190, 200, 255))
            txts.append((sp_mt, mx, my - 24, w8 * mp))
            txts.append((sp_ms, mx, my + 32, w8 * mp))

            # Scanning radar lock line between human's vortex head and each mirror!
            draw_stipple_line(cs, hx, hy - 175, mx, my + mh / 2, 14, r=1.9, alpha=0.65 * w8 * mp)

        cs.restore(); cg.restore()

    # =========================================================================
    # SCENE 9A: Reclaiming the Angle of Mind (Dual Perspective Spotlight!)
    # =========================================================================
    w9a = window_fade(t, t_s9 - 0.15, t_endplate + 0.25, fi=0.32, fo=0.45)
    if w9a > 0.01:
        lt = max(0.0, t - t_s9)
        p9 = ease_out_cubic(lt / 0.75)

        draw_pill_badge(cs, cg, txts, "انتخابِ زاویه‌ی ذهن با توست", 540, 395, fonts.bold_36, w9a * p9, glow=True)

        # Shared starry reality field across middle sky (same world, two angles!)
        stars = [(210, 560, False), (320, 650, False), (260, 745, False),
                 (675, 545, True), (790, 625, True), (885, 560, True), (745, 725, True)]
        for sx, sy, is_bright in stars:
            if is_bright:
                draw_star4(cs, sx, sy, 14 * p9, w9a * 0.95)
                draw_star4(cg, sx, sy, 22 * p9, w9a * 0.80)
            else:
                cs.arc(sx, sy, 4.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.28 * w9a); cs.fill()

        # Left Human: Narrow downward tunnel vision ("تهدید و بن‌بست")
        draw_human_figure(cs, 285, 1185, scale=1.05, alpha=w9a * 0.45, draw_p=p9, vortex=True, t=t)
        draw_spotlight_cone(cs, cg, 285, 1025, 185, 365, 625, alpha=w9a * 0.35 * p9)
        sp_neg = get_text_sprite("رادارِ ترس", fonts.reg_30, (165, 165, 175, 255))
        txts.append((sp_neg, 285, 1265, w9a * p9))

        # Center vertical divider
        cs.set_dash([8, 8]); cs.set_source_rgba(1, 1, 1, 0.22 * w9a); cs.set_line_width(1.4)
        cs.move_to(540, 500); cs.line_to(540, 1310); cs.stroke(); cs.set_dash([])

        # Right Human: Wide glowing upward 42° Angle of Mind beam ("فرصت و معنا ★")!
        draw_human_figure(cs, 795, 1185, scale=1.12, alpha=w9a * 0.98, draw_p=p9, star_mind=True, t=t)
        draw_human_figure(cg, 795, 1185, scale=1.12, alpha=w9a * 0.55, draw_p=1.0, star_mind=True, t=t)
        draw_spotlight_cone(cs, cg, 795, 1020, 625, 955, 515, alpha=w9a * 0.95 * p9)
        draw_pill_badge(cs, cg, txts, "زاویه‌ی ذهنِ آگاه", 795, 1268, fonts.bold_30, w9a * p9, glow=True)

    # =========================================================================
    # SCENE 9B: Signature OLED Endplate — زاویه ذهن (@zavieh.penhann)
    # =========================================================================
    w9b = window_fade(t, t_endplate - 0.1, total_dur + 0.5, fi=0.50, fo=0.1)
    if w9b > 0.01:
        lt = max(0.0, t - t_endplate)
        p_logo = ease_out_cubic(lt / 1.05)

        cx, cy = 540.0, 745.0
        # Counter-rotating observatory precision rings
        cs.save(); cs.set_dash([])
        for k in range(36):
            ang = k * (math.pi / 18.0) + t * 0.22
            r0 = 188.0
            cs.arc(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0, 1.8, 0, 2 * math.pi)
            cs.set_source_rgba(1, 1, 1, 0.36 * w9b * p_logo); cs.fill()
        cs.arc(cx, cy, 152, 0, 2 * math.pi * p_logo)
        cs.set_source_rgba(1, 1, 1, 0.22 * w9b); cs.set_line_width(1.4); cs.stroke()
        cs.restore()

        # Iconic 42° Geometric Aperture of Mind
        vx, vy = cx + 62, cy + 16
        for ctx, lw, al in ((cs, 5.2, w9b * 0.98), (cg, 11.5, w9b * 0.82)):
            set_stroke_draw(ctx, p_logo, 360.0)
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
            ctx.move_to(vx, vy); ctx.line_to(cx - 102, cy - 84); ctx.stroke()
            ctx.set_source_rgba(1, 1, 1, al * 0.52); ctx.set_line_width(lw * 0.72)
            ctx.move_to(vx, vy); ctx.line_to(cx - 102, cy + 90); ctx.stroke()
            ctx.set_dash([])

        cs.arc(cx - 24, cy + 6, 94, math.radians(142), math.radians(218))
        cs.set_source_rgba(1, 1, 1, 0.45 * w9b * p_logo); cs.set_line_width(1.8); cs.stroke()
        draw_star4(cs, vx, vy, 16 * p_logo, w9b)
        draw_star4(cg, vx, vy, 28 * p_logo, w9b * 0.92)

        sp_brand = get_text_sprite("زاویه ذهن", fonts.eb_84, (255, 255, 255, 255), glow=0.82)
        sp_tag   = get_text_sprite("جایی که ذهن، خودش را تماشا می‌کند", fonts.reg_34, (198, 198, 210, 255))
        txts.append((sp_brand, 540, 1065, w9b * ease_out_cubic((lt - 0.15) / 0.7)))
        txts.append((sp_tag,   540, 1168, w9b * ease_out_cubic((lt - 0.30) / 0.7)))

        pill_a = w9b * ease_out_cubic((lt - 0.45) / 0.7)
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

    # 1. 14-frame subtitle wipe & baseline verification strip (33.3ms intervals = 30fps step)
    sub_idx = min(13, len(meta["sub_lines"]) - 2)
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
        tc["s1_lock"] + 0.65,
        tc["s2_start"] + 2.0,
        tc["s3_myth"] + 1.1,
        tc["s3_title"] + 1.0,
        tc["s4_40bit"] + 0.7,
        tc["s5_filter"] + 1.0,
        tc["s5_stamp"] + 0.55,
        tc["s6_vip"] + 1.3,
        tc["s7_point"] + 0.85,
        tc["s8_dark"] + 2.0,
        tc["s9_angle"] + 1.2,
        td - 1.5,
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

    print("=== [1/3] Building @ensan.besham-Calibrated Master Audio (Rasalgethi + 129-tap FIR) ===", flush=True)
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
        raise SystemExit("Usage: python ep02_baader_meinhof.py --cloud-render <font_dir> <work_dir> <out_mp4> <qa_dir> [whisper_size]")
