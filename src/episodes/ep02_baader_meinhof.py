import os, sys, json, math, time, subprocess, multiprocessing as mp
import numpy as np
import cairocffi as cairo
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.engine.audio_master import (
    synthesize_gemini_tts,
    calibrate_baritone_and_tighten,
    align_script_lines,
    build_master_stereo_mix,
)
from src.engine.render_core import (
    W, H, FPS, FontBank, fa, clamp, ease_out_cubic, ease_in_out_cubic,
    window_fade, get_text_sprite, draw_star4, draw_stipple_line,
    draw_hud_and_subtitles, composite_oled_frame,
)

EP_CODE = "پرونده‌ی ۰۲"
EP_TITLE = "توهمِ فرکانس"

# 18 crisp spoken-Tehrani Persian lines (zero foreign/ambiguous TTS loanwords)
SCRIPT_LINES = [
    "تاحالا شده اسمِ یه ماشینِ خاص رو تازه بشنوی،",
    "و دقیقاً از همون ظهر، توی هر خیابونی پشتِ سرِ هم ببینی‌ش؟",
    "انگار کلِ شهر همون صبح با هم هماهنگ کردن!",
    "واقعاً داستان چیه؟ دنیا عوض شده، یا مغزِ تو؟",
    "علم به این اتفاق می‌گه پدیده‌ی بادر ماینهوف، یا توهمِ فرکانس.",
    "مغزِ تو هر ثانیه با یازده میلیون بیت تصویر و صدا بمبارون می‌شه؛",
    "صدای بوق، تابلوهای مغازه، قیافه‌ی هزارتا رهگذر.",
    "اگه بخواد همه‌ش رو ببینه، تو پنج ثانیه قفل می‌کنه؛",
    "پس نود و نُه درصدِ دنیا رو سانسور می‌کنه!",
    "اما به محضِ اینکه یه چیزِ تازه توجه‌ت رو می‌گیره،",
    "رادارِ مغزت روش قفل می‌شه و می‌ره توی لیستِ ویژه.",
    "از فرداش، تعدادِ اون ماشین توی شهر بیشتر نشده؛",
    "فقط مغزِ تو دیگه حذفش نمی‌کنه!",
    "حالا بخشِ ترسناکِ ماجرا اینجاست: این رادار روی افکارت هم همین شکلی کار می‌کنه!",
    "اگه صبح با این فکر بیدار شی که دنیا جای بدیه و شانسی نداری،",
    "مغزت تا شب فقط شواهدِ بدبختی رو پررنگ می‌کنه و بقیه رو پاک می‌کنه.",
    "دنیا همون دنیاست؛ فقط بستگی داره رادارِ ذهنت رو، روی چی تنظیم کنی.",
    "این، زاویه‌ی ذهنِ توئه.",
]

# Precomputed deterministic ambient & data-stream particles
_RNG = np.random.default_rng(2026)
_DUST = [(_RNG.uniform(60, W - 60), _RNG.uniform(160, H - 380), _RNG.uniform(0.7, 1.8), _RNG.uniform(0, 6.28), _RNG.uniform(7, 19)) for _ in range(34)]
_STREAM = [(_RNG.uniform(0.0, 1.0), _RNG.uniform(-310, 310), _RNG.uniform(1.4, 3.2), _RNG.integers(0, 100)) for _ in range(135)]
# 5x5 Daily Events grid types: 0=neutral dot, 1=negative thorn (6 items), 2=positive star (7 items)
_GRID_25 = [
    0, 1, 0, 2, 0,
    2, 0, 1, 0, 2,
    0, 2, 0, 1, 0,
    1, 0, 2, 0, 1,
    2, 0, 1, 2, 0,
]

def draw_car_icon(ctx, cx: float, cy: float, scale: float = 1.0, alpha: float = 1.0, lw: float = 2.4):
    """Minimalist sleek side-profile sedan wireframe in @ensan.besham monoline style."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(scale, scale)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.set_line_width(lw / max(0.35, scale))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # Car body silhouette
    ctx.move_to(-92, 18)
    ctx.line_to(-92, -4)
    ctx.line_to(-56, -8)
    ctx.line_to(-28, -36)
    ctx.line_to(34, -36)
    ctx.line_to(64, -8)
    ctx.line_to(94, -2)
    ctx.line_to(94, 18)
    ctx.stroke()

    # Undercarriage segments between wheel arches
    ctx.move_to(-92, 18); ctx.line_to(-68, 18); ctx.stroke()
    ctx.move_to(-32, 18); ctx.line_to(32, 18); ctx.stroke()
    ctx.move_to(68, 18); ctx.line_to(94, 18); ctx.stroke()

    # Windows divider
    ctx.move_to(-48, -8); ctx.line_to(54, -8); ctx.stroke()
    ctx.move_to(4, -35); ctx.line_to(4, -8); ctx.stroke()

    # Wheels
    ctx.arc(-50, 18, 17, 0, 2 * math.pi); ctx.stroke()
    ctx.arc(50, 18, 17, 0, 2 * math.pi); ctx.stroke()
    ctx.restore()

def draw_head_profile(ctx, cx: float, cy: float, scale: float = 1.0, alpha: float = 1.0, lw: float = 2.6, facing_right: bool = True):
    """Minimalist architectural human head silhouette facing right (toward incoming sensory stream)."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(scale if facing_right else -scale, scale)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.set_line_width(lw / max(0.4, scale))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    ctx.move_to(-45, 155)
    ctx.line_to(-38, 95)
    ctx.curve_to(-115, 75, -135, -15, -120, -85)
    ctx.curve_to(-100, -155, -15, -175, 55, -145)
    ctx.curve_to(95, -125, 108, -85, 102, -48)
    ctx.line_to(128, -8)    # Nose bridge & tip
    ctx.line_to(106, 6)
    ctx.line_to(114, 24)    # Upper lip
    ctx.line_to(102, 36)
    ctx.line_to(108, 65)    # Chin
    ctx.curve_to(98, 92, 62, 95, 35, 92)
    ctx.line_to(38, 155)
    ctx.stroke()
    ctx.restore()


# Worker global state for fast multi-core rendering
_G_STATE = {}

def _init_worker(font_dir: str, align_data: dict):
    _G_STATE["fonts"] = FontBank(font_dir)
    _G_STATE["align"] = align_data

def render_single_frame(frame_idx: int) -> bytes:
    fonts: FontBank = _G_STATE["fonts"]
    align = _G_STATE["align"]
    L = align["lines"]
    total_dur = align["total_duration"]
    t = frame_idx / FPS

    # Chapter boundaries anchored directly to spoken line starts!
    c0 = 0.0
    c1 = L[4]["start"]   # علم به این اتفاق می‌گه...
    c2 = L[9]["start"]   # اما به محض اینکه...
    c3 = L[13]["start"]  # حالا بخش ترسناک ماجرا...
    c4 = L[16]["start"]  # دنیا همون دنیاست...
    chapter_starts = [c0, c1, c2, c3, c4]

    surf_glow = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cg = cairo.Context(surf_glow)
    surf_sharp = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cs = cairo.Context(surf_sharp)
    text_overlays = []

    # Ambient OLED floating white dust motes
    for dx, dy, dr, ph, spd in _DUST:
        yy = (dy - t * spd) % (H - 420) + 150
        twk = 0.07 + 0.09 * (0.5 + 0.5 * math.sin(t * 1.6 + ph))
        cs.arc(dx, yy, dr, 0, 2 * math.pi)
        cs.set_source_rgba(1, 1, 1, twk)
        cs.fill()

    # =========================================================================
    # CHAPTER 0 (L[0]..L[3]): Hearing a New Car Name -> Seeing 5 in Every Street -> World vs Brain?
    # =========================================================================
    sa = window_fade(t, c0, c1, fi=0.25, fo=0.40)
    if sa > 0.005:
        t_b1 = L[1]["start"]
        t_b2 = L[3]["start"]

        if t < t_b2:
            # Sub-phase A & B: Single Car -> 5 Highlighted Cars in 3-Lane Street!
            p_zoom = ease_in_out_cubic((t - (t_b1 - 0.15)) / 0.85)
            sub_a = sa * clamp((t_b2 - t) / 0.35)

            if p_zoom < 0.99:
                # Beat 0A: Single sleek car inside acoustic target reticle
                fa_0 = sub_a * (1.0 - p_zoom)
                p_in = ease_out_cubic(t / 0.9)
                draw_car_icon(cs, 540, 790, scale=1.55 * (0.88 + 0.12 * p_in), alpha=fa_0 * 0.96, lw=2.8)
                draw_car_icon(cg, 540, 790, scale=1.55 * (0.88 + 0.12 * p_in), alpha=fa_0 * 0.65, lw=5.5)

                # Radiating soundwaves above car ("اسم یه ماشین خاص رو تازه بشنوی")
                for w_i in range(3):
                    prog = ((t * 1.15 - w_i * 0.33) % 1.0)
                    rad = 45 + 135 * prog
                    w_al = fa_0 * (1.0 - prog) * 0.65
                    cs.set_source_rgba(1, 1, 1, w_al)
                    cs.set_line_width(2.0)
                    cs.arc(540, 680, rad, -math.pi * 0.78, -math.pi * 0.22)
                    cs.stroke()

                sp0 = get_text_sprite(fa("شنیدنِ نام برای اولین بار"), fonts.reg_32, (225, 225, 232, 255), glow=0.35)
                text_overlays.append((sp0, 540, 955, fa_0 * p_in))

            if p_zoom > 0.02:
                # Beat 0B: 3-Lane City Intersection with 5 Identical Cars Snapping into Glowing Selector Frames!
                fa_1 = sub_a * p_zoom
                lane_ys = [560, 820, 1080]
                for ly in lane_ys:
                    cs.set_source_rgba(1, 1, 1, fa_1 * 0.12)
                    cs.set_line_width(1.2)
                    cs.move_to(110, ly + 52); cs.line_to(970, ly + 52); cs.stroke()
                    draw_stipple_line(cs, 130, ly - 75, 950, ly - 75, 28, r=1.2, alpha=fa_1 * 0.14)

                # 8 traffic cars; 5 of them are the TARGET car lighting up sequentially!
                cars = [
                    (310, 560, True,  0.00),
                    (740, 560, False, 0.00),
                    (540, 820, True,  0.42),
                    (220, 820, False, 0.00),
                    (835, 820, True,  0.84),
                    (370, 1080, True, 1.26),
                    (695, 1080, True, 1.68),
                    (175, 1080, False, 0.00),
                ]
                span_b = max(1.2, L[2]["end"] - t_b1)
                lit_count = 0
                for cx_c, cy_c, is_target, delay_u in cars:
                    drift = ((t - t_b1) * 26.0) if is_target else ((t - t_b1) * 18.0)
                    px = cx_c + drift * 0.35
                    if not is_target:
                        draw_car_icon(cs, px, cy_c, scale=0.82, alpha=fa_1 * 0.18, lw=1.8)
                    else:
                        t_trig = t_b1 + delay_u * (span_b * 0.38)
                        p_lock = ease_out_cubic((t - t_trig) / 0.38)
                        if p_lock > 0.05:
                            lit_count += 1
                        c_al = fa_1 * (0.25 + 0.75 * p_lock)
                        draw_car_icon(cs, px, cy_c, scale=0.88, alpha=c_al, lw=2.4)
                        if p_lock > 0.05:
                            draw_car_icon(cg, px, cy_c, scale=0.88, alpha=fa_1 * p_lock * 0.65, lw=5.0)
                            # Glowing @ensan.besham white selector box around spotted car!
                            bw, bh = 196, 108
                            for ctx, lw, al in ((cs, 2.6, fa_1 * p_lock * 0.95), (cg, 6.0, fa_1 * p_lock * 0.80)):
                                ctx.set_source_rgba(1, 1, 1, al)
                                ctx.set_line_width(lw)
                                ctx.rectangle(px - bw / 2, cy_c - bh / 2 - 6, bw, bh)
                                ctx.stroke()
                            draw_star4(cs, px + bw / 2, cy_c - bh / 2 - 6, 8 * p_lock, fa_1 * p_lock)

                sp_cnt = get_text_sprite(fa(f"مشاهده در همان روز:  ×{max(1, lit_count)}"), fonts.bold_44, (255, 255, 255, 255), glow=0.80)
                text_overlays.append((sp_cnt, 540, 360, fa_1))

        else:
            # Beat 0C (L[3] + 0.72s dramatic pause!): "دنیا عوض شده، یا مغزِ تو؟"
            p_q = ease_out_cubic((t - t_b2) / 0.55)
            t_brain_word = L[3]["times"][-2] if len(L[3]["times"]) >= 2 else (t_b2 + 1.4)
            p_br = ease_out_cubic((t - t_brain_word) / 0.45)

            # Right side: Wireframe Globe ("دنیا عوض شده؟")
            gx, gy, gr = 760, 790, 125
            w_al = sa * p_q * (0.80 - 0.42 * p_br)
            cs.set_source_rgba(1, 1, 1, w_al)
            cs.set_line_width(2.2)
            cs.arc(gx, gy, gr, 0, 2 * math.pi); cs.stroke()
            cs.save(); cs.translate(gx, gy); cs.scale(0.48, 1.0); cs.arc(0, 0, gr, 0, 2 * math.pi); cs.restore(); cs.stroke()
            cs.move_to(gx - gr, gy); cs.line_to(gx + gr, gy); cs.stroke()
            cs.move_to(gx - gr * 0.86, gy - gr * 0.5); cs.line_to(gx + gr * 0.86, gy - gr * 0.5); cs.stroke()
            cs.move_to(gx - gr * 0.86, gy + gr * 0.5); cs.line_to(gx + gr * 0.86, gy + gr * 0.5); cs.stroke()
            sp_w = get_text_sprite("دنیا عوض شده؟", fonts.med_38, (185, 185, 195, 255), glow=0.0)
            text_overlays.append((sp_w, gx, 995, sa * p_q * (0.9 - 0.35 * p_br)))

            # Left side: Glowing Constellation Mind ("یا مغزِ تو؟") — blazes bright during dramatic pause!
            bx, by = 320, 790
            b_al = sa * (0.28 * p_q + 0.72 * p_br)
            b_nodes = [(-95, 10), (-80, -55), (-30, -95), (35, -90), (90, -45), (98, 20), (55, 75), (-25, 78), (-10, -15), (35, -10)]
            b_edges = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(1,8),(3,9),(8,9),(7,8),(5,9),(2,8)]
            for i, j in b_edges:
                cs.set_source_rgba(1, 1, 1, b_al * 0.55)
                cs.set_line_width(1.8)
                cs.move_to(bx + b_nodes[i][0], by + b_nodes[i][1])
                cs.line_to(bx + b_nodes[j][0], by + b_nodes[j][1])
                cs.stroke()
            for ni, (nx, ny) in enumerate(b_nodes):
                pulse = 0.65 + 0.35 * math.sin(t * 4.5 + ni)
                cs.arc(bx + nx, by + ny, 4.2, 0, 2 * math.pi)
                cs.set_source_rgba(1, 1, 1, b_al); cs.fill()
                if p_br > 0.05:
                    cg.arc(bx + nx, by + ny, 10.5 * pulse, 0, 2 * math.pi)
                    cg.set_source_rgba(1, 1, 1, sa * p_br * 0.85); cg.fill()

            sp_m = get_text_sprite("یا مغزِ تو؟", fonts.bold_44, (255, 255, 255, 255), glow=0.95 * p_br)
            text_overlays.append((sp_m, bx, 995, b_al))

    # =========================================================================
    # CHAPTER 1 (L[4]..L[8]): 11,000,000 Bits/Sec Sensory Bombardment & 99% Brain Shield
    # =========================================================================
    sa = window_fade(t, c1, c2, fi=0.35, fo=0.40)
    if sa > 0.005:
        t_bomb = L[5]["start"]
        t_shield = L[7]["end"] - 0.25 # Right as "پس نود و نه درصد دنیا رو سانسور می‌کنه" begins!

        sp_bm = get_text_sprite("پدیده‌ی بادر-ماینهوف  •  توهمِ فرکانس", fonts.bold_44, (255, 255, 255, 255), glow=0.75)
        text_overlays.append((sp_bm, 540, 310, sa * ease_out_cubic((t - c1) / 0.65)))

        # Head profile on left facing incoming world data stream on right
        hx, hy = 275, 865
        p_hd = ease_out_cubic((t - c1) / 0.8)
        draw_head_profile(cs, hx, hy, scale=1.08, alpha=sa * p_hd * 0.92, lw=2.8, facing_right=True)
        draw_head_profile(cg, hx, hy, scale=1.08, alpha=sa * p_hd * 0.55, lw=5.5, facing_right=True)
        draw_star4(cs, hx - 10, hy - 35, 11 * p_hd, sa)
        draw_star4(cg, hx - 10, hy - 35, 18 * p_hd, sa * 0.85)

        if t >= t_bomb - 0.15:
            p_bm = ease_out_cubic((t - t_bomb) / 1.1)
            p_sh = ease_out_cubic((t - t_shield) / 0.55)
            shield_x = 495.0

            # Rolling 11,000,000 bits/sec counter -> switches to "۹۹٪ سانسورِ ورودی‌ها" when shield activates!
            if p_sh < 0.5:
                val = int(round(11_000_000 * ease_out_cubic((t - t_bomb) / 1.4)))
                txt_num = fa(f"{val:,} بیت در ثانیه".replace(",", "٬"))
                sp_n = get_text_sprite(txt_num, fonts.eb_68, (255, 255, 255, 255), glow=0.85)
                text_overlays.append((sp_n, 540, 445, sa * p_bm * (1.0 - p_sh * 2.0)))
            else:
                sp_s = get_text_sprite(fa("۹۹٪ حذف و سانسور توسطِ مغز"), fonts.bold_52, (255, 255, 255, 255), glow=0.90)
                text_overlays.append((sp_s, 540, 445, sa * clamp((p_sh - 0.5) * 2.0)))

            # Stream of 135 sensory particles flying from right (x=990) toward head (x=395)
            for idx_p, (u0, y_off, r_sz, kind_id) in enumerate(_STREAM):
                u = (u0 + (t - t_bomb) * 0.52) % 1.0
                px = 985.0 - u * 590.0
                py = hy + y_off

                is_chosen_one = (idx_p == 0)
                if is_chosen_one:
                    py = hy - 35
                    cs.arc(px, py, 5.2, 0, 2 * math.pi)
                    cs.set_source_rgba(1, 1, 1, sa * p_bm); cs.fill()
                    cg.arc(px, py, 11.0, 0, 2 * math.pi)
                    cg.set_source_rgba(1, 1, 1, sa * p_bm * 0.9); cg.fill()
                else:
                    # Blocked by firewall shield at x = shield_x when p_sh > 0!
                    if p_sh > 0.05 and px < shield_x:
                        fade_blk = max(0.03, (1.0 - p_sh) * 0.5)
                        py += (shield_x - px) * (0.45 if y_off >= 0 else -0.45) * p_sh
                        cs.arc(px, py, r_sz * 0.8, 0, 2 * math.pi)
                        cs.set_source_rgba(1, 1, 1, sa * fade_blk); cs.fill()
                    else:
                        cs.arc(px, py, r_sz, 0, 2 * math.pi)
                        cs.set_source_rgba(1, 1, 1, sa * p_bm * 0.58); cs.fill()

            # Glowing curved Brain Censorship Shield Arc at x = 495
            if p_sh > 0.01:
                for ctx, lw, al in ((cs, 3.6, sa * p_sh * 0.98), (cg, 8.5, sa * p_sh * 0.90)):
                    ctx.set_source_rgba(1, 1, 1, al)
                    ctx.set_line_width(lw)
                    ctx.arc(hx + 40, hy, 255, -0.92 * p_sh, 0.92 * p_sh)
                    ctx.stroke()

                # Single 1% laser ray piercing cleanly into the mind!
                for ctx, lw, al in ((cs, 2.8, sa * p_sh * 0.95), (cg, 6.5, sa * p_sh * 0.85)):
                    ctx.set_source_rgba(1, 1, 1, al)
                    ctx.set_line_width(lw)
                    ctx.move_to(hx + 295, hy - 35)
                    ctx.line_to(hx - 10, hy - 35)
                    ctx.stroke()

                sp_f = get_text_sprite(fa("عبور به آگاهی: فقط ۱٪"), fonts.reg_32, (230, 230, 238, 255), glow=0.45)
                text_overlays.append((sp_f, 540, 1275, sa * p_sh))

    # =========================================================================
    # CHAPTER 2 (L[9]..L[12]): Radar Lock (RAS) -> Yesterday vs Today 5x5 City Proof!
    # =========================================================================
    sa = window_fade(t, c2, c3, fi=0.35, fo=0.40)
    if sa > 0.005:
        t_grid = L[11]["start"] # "از فرداش، تعداد اون ماشین توی شهر بیشتر نشده..."

        if t < t_grid:
            # Beat 2A: Observatory Attention Radar locking onto Target Car ("ثبت در لیست ویژه")
            fa_r = sa * clamp((t_grid - t) / 0.35)
            p_r = ease_out_cubic((t - c2) / 0.75)
            rcx, rcy = 540, 815

            for rad, al_mul in ((230, 0.22), (165, 0.38), (105, 0.65)):
                cs.set_source_rgba(1, 1, 1, fa_r * p_r * al_mul)
                cs.set_line_width(1.6)
                cs.arc(rcx, rcy, rad * p_r, 0, 2 * math.pi)
                cs.stroke()

            # Rotating radar sweep arm
            ang_sw = t * 2.6
            cs.set_source_rgba(1, 1, 1, fa_r * p_r * 0.85)
            cs.set_line_width(2.4)
            cs.move_to(rcx, rcy)
            cs.line_to(rcx + math.cos(ang_sw) * 230 * p_r, rcy + math.sin(ang_sw) * 230 * p_r)
            cs.stroke()

            # Target car locked in glowing white brackets at center!
            p_lk = ease_out_cubic((t - L[10]["start"]) / 0.55)
            draw_car_icon(cs, rcx, rcy + 6, scale=1.05, alpha=fa_r * (0.45 + 0.55 * p_lk), lw=2.6)
            if p_lk > 0.05:
                draw_car_icon(cg, rcx, rcy + 6, scale=1.05, alpha=fa_r * p_lk * 0.80, lw=5.5)
                bw, bh = 235, 130
                for ctx, lw, al in ((cs, 3.0, fa_r * p_lk), (cg, 7.0, fa_r * p_lk * 0.85)):
                    ctx.set_source_rgba(1, 1, 1, al)
                    ctx.set_line_width(lw)
                    # Corner target brackets
                    for sx_s in (-1, 1):
                        for sy_s in (-1, 1):
                            cx0 = rcx + sx_s * bw / 2
                            cy0 = rcy + sy_s * bh / 2
                            ctx.move_to(cx0 - sx_s * 28, cy0); ctx.line_to(cx0, cy0); ctx.line_to(cx0, cy0 - sy_s * 28)
                            ctx.stroke()

            sp_rt = get_text_sprite("قفل شدنِ رادارِ توجه  •  ثبت در لیستِ ویژه", fonts.bold_44, (255, 255, 255, 255), glow=0.75 * p_lk)
            text_overlays.append((sp_rt, 540, 415, fa_r * p_r))
        else:
            # Beat 2B: Side-by-Side 5x5 City Proof (دیروز vs امروز — Exact same 4 targets!)
            p_g = ease_out_cubic((t - t_grid) / 0.65)
            p_hi = ease_out_cubic((t - L[12]["start"]) / 0.55)

            sp_hd = get_text_sprite(fa("تعدادِ واقعی در شهر: ثابت (۴ دستگاه)"), fonts.bold_44, (255, 255, 255, 255), glow=0.70)
            text_overlays.append((sp_hd, 540, 360, sa * p_g))

            target_cells = {(0, 1), (1, 3), (3, 0), (4, 2)}

            # Right Matrix = قبل از شنیدن (دیروز) | Left Matrix = بعد از شنیدن (امروز)
            for side, panel_cx, title_lbl, sub_lbl in (
                ("before", 785, "دیروز (قبل از شنیدن)", "هر ۴ ماشین سانسور شدن"),
                ("after",  295, "امروز (بعد از قفلِ رادار)", "دیگه حذف نمی‌شن!"),
            ):
                sp_tl = get_text_sprite(fa(title_lbl), fonts.bold_36, (240, 240, 246, 255), glow=0.55 if side == "after" else 0.0)
                text_overlays.append((sp_tl, panel_cx, 540, sa * p_g))

                step = 68.0
                for r in range(5):
                    for c in range(5):
                        px = panel_cx + (c - 2) * step
                        py = 825 + (r - 2) * step
                        is_t = (r, c) in target_cells

                        if side == "before":
                            # Target dots ARE physically there, just dim like everything else!
                            rad = 5.2 if is_t else 3.6
                            al = sa * p_g * (0.42 if is_t else 0.22)
                            cs.arc(px, py, rad, 0, 2 * math.pi)
                            cs.set_source_rgba(1, 1, 1, al); cs.fill()
                        else:
                            if is_t:
                                rad = 5.2 + 2.2 * p_hi
                                cs.arc(px, py, rad, 0, 2 * math.pi)
                                cs.set_source_rgba(1, 1, 1, sa * p_g * (0.35 + 0.65 * p_hi)); cs.fill()
                                if p_hi > 0.05:
                                    cg.arc(px, py, 13.0, 0, 2 * math.pi)
                                    cg.set_source_rgba(1, 1, 1, sa * p_hi * 0.90); cg.fill()
                                    for ctx, lw, al in ((cs, 2.4, sa * p_hi * 0.96), (cg, 5.5, sa * p_hi * 0.80)):
                                        ctx.set_source_rgba(1, 1, 1, al)
                                        ctx.set_line_width(lw)
                                        ctx.rectangle(px - 24, py - 24, 48, 48)
                                        ctx.stroke()
                            else:
                                cs.arc(px, py, 3.4, 0, 2 * math.pi)
                                cs.set_source_rgba(1, 1, 1, sa * p_g * 0.22); cs.fill()

                sp_sb = get_text_sprite(fa(sub_lbl), fonts.reg_28, (205, 205, 215, 255) if side == "after" else (140, 140, 150, 255), glow=0.35 if side == "after" else 0.0)
                text_overlays.append((sp_sb, panel_cx, 1125, sa * p_g))

            # Center vertical divider
            cs.set_source_rgba(1, 1, 1, sa * p_g * 0.14)
            cs.set_line_width(1.4)
            cs.move_to(540, 520); cs.line_to(540, 1150); cs.stroke()

    # =========================================================================
    # CHAPTER 3 & 4 (L[13]..End): Morning Thought Radar on 25 Daily Events -> Brand Lockup!
    # =========================================================================
    t_brand = L[17]["start"] - 0.15 # "این، زاویه‌ی ذهنِ توئه"
    sa_grid = window_fade(t, c3, t_brand + 0.15, fi=0.35, fo=0.45)
    if sa_grid > 0.005:
        p_in = ease_out_cubic((t - c3) / 0.70)
        p_neg = ease_in_out_cubic((t - L[14]["start"]) / 0.75)  # Negative morning filter locks on!
        p_pos = ease_in_out_cubic((t - c4) / 0.85)             # Radar retunes to positive opportunities!

        if p_neg < 0.35:
            top_lbl = "۲۵ اتفاقِ معمولیِ یک روزِ تو"
        elif p_pos < 0.35:
            top_lbl = "رادارِ صبحگاهی: «دنیا جایِ بدیه»"
        else:
            top_lbl = "تغییرِ زاویه‌ی رادار  •  همون دنیا، دیدِ تازه"

        sp_top = get_text_sprite(fa(top_lbl), fonts.bold_44, (255, 255, 255, 255), glow=0.80)
        text_overlays.append((sp_top, 540, 355, sa_grid * p_in))

        # 5x5 Matrix of Daily Life Events at center (540, 835)
        step = 122.0
        for idx_e, ev_type in enumerate(_GRID_25):
            r, c = idx_e // 5, idx_e % 5
            px = 540 + (c - 2) * step
            py = 835 + (r - 2) * step

            if ev_type == 0:
                # Neutral event dot
                al = sa_grid * p_in * (0.32 - 0.10 * max(p_neg, p_pos))
                cs.arc(px, py, 3.8, 0, 2 * math.pi)
                cs.set_source_rgba(1, 1, 1, al); cs.fill()

            elif ev_type == 1:
                # Negative event (X / sharp cross) — blazes during p_neg, fades during p_pos!
                neg_focus = p_neg * (1.0 - p_pos)
                al = sa_grid * p_in * (0.24 + 0.76 * neg_focus - 0.12 * p_pos)
                sz = 11.0 + 5.0 * neg_focus
                cs.set_source_rgba(1, 1, 1, al)
                cs.set_line_width(2.2 + 1.2 * neg_focus)
                cs.move_to(px - sz, py - sz); cs.line_to(px + sz, py + sz); cs.stroke()
                cs.move_to(px + sz, py - sz); cs.line_to(px - sz, py + sz); cs.stroke()
                if neg_focus > 0.1:
                    cg.set_source_rgba(1, 1, 1, sa_grid * neg_focus * 0.85)
                    cg.set_line_width(6.0)
                    cg.move_to(px - sz, py - sz); cg.line_to(px + sz, py + sz); cg.stroke()
                    cg.move_to(px + sz, py - sz); cg.line_to(px - sz, py + sz); cg.stroke()
                    cs.set_line_width(2.2)
                    cs.rectangle(px - 38, py - 38, 76, 76); cs.stroke()
                    cg.rectangle(px - 38, py - 38, 76, 76); cg.stroke()

            elif ev_type == 2:
                # Positive opportunity (4-point star) — suppressed during p_neg, blazes during p_pos!
                pos_focus = p_pos
                suppressed = p_neg * (1.0 - p_pos)
                al = sa_grid * p_in * max(0.08, 0.28 - 0.19 * suppressed + 0.72 * pos_focus)
                sz = 12.0 + 10.0 * pos_focus
                draw_star4(cs, px, py, sz, al)
                if pos_focus > 0.08:
                    draw_star4(cg, px, py, sz * 1.55, sa_grid * pos_focus * 0.95)
                    for ctx, lw, a_box in ((cs, 2.4, sa_grid * pos_focus * 0.95), (cg, 5.5, sa_grid * pos_focus * 0.80)):
                        ctx.set_source_rgba(1, 1, 1, a_box)
                        ctx.set_line_width(lw)
                        ctx.arc(px, py, 40, 0, 2 * math.pi)
                        ctx.stroke()

        if p_neg > 0.35 and p_pos < 0.35:
            sp_b = get_text_sprite(fa("فقط نشونه‌های بدبختی پررنگ می‌شن؛ فرصت‌ها نامرئی می‌شن!"), fonts.reg_32, (225, 225, 235, 255), glow=0.45)
            text_overlays.append((sp_b, 540, 1265, sa_grid * p_neg * (1.0 - p_pos * 2.5)))
        elif p_pos >= 0.35:
            sp_b2 = get_text_sprite(fa("دنیا عوض نشد؛ فقط فیلترِ رادارت رو چرخوندی"), fonts.bold_36, (255, 255, 255, 255), glow=0.75)
            text_overlays.append((sp_b2, 540, 1265, sa_grid * clamp((p_pos - 0.35) * 1.6)))

    # =========================================================================
    # FINALE BRAND LOCKUP (L[17]..End): زاویه ذهن | @zavieh.penhann
    # =========================================================================
    sa_br = window_fade(t, t_brand - 0.10, total_dur, fi=0.45, fo=0.55)
    if sa_br > 0.005:
        p_b = ease_out_cubic((t - t_brand) / 0.85)
        cy_em = 710

        # Observatory degree ring + upward perspective ray (signature of زاویه ذهن!)
        for ctx, lw, al in ((cs, 1.8, sa_br * 0.55), (cg, 4.5, sa_br * 0.45)):
            ctx.set_source_rgba(1, 1, 1, al * p_b)
            ctx.set_line_width(lw)
            ctx.arc(540, cy_em, 155 * p_b, 0, 2 * math.pi)
            ctx.stroke()

        for tk_i in range(24):
            ang = tk_i * (math.pi / 12.0) + t * 0.12
            r_in = 166 if tk_i % 2 == 0 else 170
            cs.set_source_rgba(1, 1, 1, sa_br * p_b * 0.35)
            cs.set_line_width(1.3)
            cs.move_to(540 + math.cos(ang) * r_in, cy_em + math.sin(ang) * r_in)
            cs.line_to(540 + math.cos(ang) * 176, cy_em + math.sin(ang) * 176)
            cs.stroke()

        ang_up = math.radians(215)   # Upward-left ray!
        ang_dn = math.radians(145)   # Lower reference ray
        r_len = 235 * p_b
        x_up, y_up = 540 + math.cos(ang_up) * r_len, cy_em + math.sin(ang_up) * r_len
        x_dn, y_dn = 540 + math.cos(ang_dn) * r_len, cy_em + math.sin(ang_dn) * r_len

        draw_stipple_line(cs, 540, cy_em, 830, cy_em, 20, r=1.6, alpha=sa_br * p_b * 0.35)

        for ctx, lw, al in ((cs, 3.4, sa_br * 0.98), (cg, 7.5, sa_br * 0.88)):
            ctx.set_source_rgba(1, 1, 1, al)
            ctx.set_line_width(lw)
            ctx.move_to(540, cy_em); ctx.line_to(x_up, y_up); ctx.stroke()
            ctx.set_line_width(lw * 0.55)
            ctx.set_source_rgba(1, 1, 1, al * 0.55)
            ctx.move_to(540, cy_em); ctx.line_to(x_dn, y_dn); ctx.stroke()
            ctx.set_line_width(2.2)
            ctx.set_source_rgba(1, 1, 1, al * 0.85)
            ctx.arc(540, cy_em, 82 * p_b, ang_dn, ang_up)
            ctx.stroke()

        draw_star4(cs, 540, cy_em, 19 * p_b, sa_br)
        draw_star4(cg, 540, cy_em, 30 * p_b, sa_br * 0.95)
        draw_star4(cs, x_up, y_up, 15 * p_b, sa_br)
        draw_star4(cg, x_up, y_up, 24 * p_b, sa_br * 0.90)

        sp_t1 = get_text_sprite("زاویه ذهن", fonts.eb_92, (255, 255, 255, 255), glow=0.95)
        sp_t2 = get_text_sprite("@zavieh.penhann", fonts.med_38, (220, 220, 230, 255), glow=0.45)
        sp_t3 = get_text_sprite("رادارِ ذهنت رو آگاهانه تنظیم کن", fonts.reg_28, (155, 155, 168, 255), glow=0.0)
        text_overlays.append((sp_t1, 540, 1005, sa_br * p_b))
        text_overlays.append((sp_t2, 540, 1115, sa_br * p_b))
        text_overlays.append((sp_t3, 540, 1195, sa_br * ease_out_cubic((t - t_brand - 0.25) / 0.8)))

    # Draw HUD + Chapter Progress Dots + Floating Karaoke Subtitles
    draw_hud_and_subtitles(
        cs, cg, text_overlays, fonts, t, total_dur,
        EP_CODE, EP_TITLE, chapter_starts, L
    )

    return composite_oled_frame(surf_glow, surf_sharp, text_overlays, fonts, t, L)


def build_sfx_schedule(align_data: dict) -> list[dict]:
    L = align_data["lines"]
    events = [
        {"type": "ping", "t": L[0]["start"] + 0.25, "freq": 880.0, "pan": 0.5},
        # 5 car lock-on pings in Beat 0B
        {"type": "ping", "t": L[1]["start"] + 0.15, "freq": 987.77, "pan": 0.25},
        {"type": "ping", "t": L[1]["start"] + 0.75, "freq": 1046.50, "pan": 0.50},
        {"type": "ping", "t": L[1]["start"] + 1.35, "freq": 1174.66, "pan": 0.78},
        {"type": "ping", "t": L[2]["start"] + 0.20, "freq": 1318.51, "pan": 0.35},
        {"type": "ping", "t": L[2]["start"] + 0.80, "freq": 1567.98, "pan": 0.68},
        # Dramatic pause sub-swell ("یا مغز تو؟")
        {"type": "sub_swell", "t": L[3]["end"] - 0.25},
        # Chapter 1 transition & 99% shield snap
        {"type": "sub_swell", "t": L[4]["start"]},
        {"type": "sub_swell", "t": L[8]["start"] - 0.10},
        {"type": "ping", "t": L[8]["start"] + 0.15, "freq": 783.99, "pan": 0.3},
        # Chapter 2 radar lock & city grid
        {"type": "ping", "t": L[10]["start"] + 0.15, "freq": 1046.50, "pan": 0.5},
        {"type": "tick", "t": L[12]["start"] + 0.10, "pan": 0.3},
        {"type": "tick", "t": L[12]["start"] + 0.28, "pan": 0.7},
        # Chapter 3 & 4 shift
        {"type": "sub_swell", "t": L[13]["start"]},
        {"type": "chime", "t": L[16]["start"] + 0.15, "freq": 659.25},
        # Final brand chime
        {"type": "chime", "t": L[17]["start"] + 0.05, "freq": 523.25},
    ]
    return events


def run_dry_preview(font_dir: str, out_dir: str):
    """Generates 8 instant QA frames on synthetic timing to verify layout before cloud run."""
    os.makedirs(out_dir, exist_ok=True)
    lines = []
    cur = 0.04
    for s in SCRIPT_LINES:
        toks = s.split(" ")
        dur = len(toks) * 0.40
        times = [round(cur + k * 0.40, 3) for k in range(len(toks))]
        lines.append({"full": s, "start": round(cur, 3), "end": round(cur + dur, 3), "tokens": toks, "times": times})
        cur += dur + 0.19
    align_mock = {"total_duration": round(cur + 1.2, 3), "lines": lines}
    _init_worker(font_dir, align_mock)

    probe_lines = [0, 1, 3, 5, 8, 10, 12, 15, 16, 17]
    for k, li in enumerate(probe_lines):
        t_mid = 0.5 * (lines[li]["start"] + lines[li]["end"])
        raw_rgb = render_single_frame(int(round(t_mid * FPS)))
        im = Image.frombytes("RGB", (W, H), raw_rgb)
        im.save(os.path.join(out_dir, f"dry_{k:02d}_L{li:02d}.png"))
    print(f"[DryPreview] Saved {len(probe_lines)} frames to {out_dir}")


def run_full_cloud_pipeline(font_dir: str, work_dir: str, out_mp4: str, qa_dir: str, whisper_size: str = "medium"):
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(qa_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)

    full_tts_text = " ".join(SCRIPT_LINES)
    raw_wav = os.path.join(work_dir, "raw_tts.wav")
    tight_wav = os.path.join(work_dir, "tightened_vo.wav")
    master_wav = os.path.join(work_dir, "master_48k.wav")
    align_json = os.path.join(work_dir, "alignment.json")

    tts_info = synthesize_gemini_tts(full_tts_text, raw_wav, voice="Iapetus")
    aud_info = calibrate_baritone_and_tighten(raw_wav, tight_wav, dramatic_frac_range=(0.12, 0.25))
    align_data = align_script_lines(tight_wav, SCRIPT_LINES, whisper_size=whisper_size)
    align_data["tts"] = tts_info
    align_data["audio_master"] = aud_info

    with open(align_json, "w", encoding="utf-8") as f:
        json.dump(align_data, f, ensure_ascii=False, indent=2)

    sfx_events = build_sfx_schedule(align_data)
    build_master_stereo_mix(tight_wav, master_wav, sfx_events)

    total_frames = int(round(align_data["total_duration"] * FPS))
    workers = max(1, mp.cpu_count())
    print(f"[Render] Starting 60fps Studio Render: {total_frames} frames ({align_data['total_duration']:.2f}s) on {workers} CPU cores...", flush=True)

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", master_wav,
        "-c:v", "libx264", "-preset", "slow", "-crf", "14",
        "-profile:v", "high", "-level:v", "4.2", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest", out_mp4
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()

    with mp.Pool(processes=workers, initializer=_init_worker, initargs=(font_dir, align_data), maxtasksperchild=450) as pool:
        for f_idx, rgb_bytes in enumerate(pool.imap(render_single_frame, range(total_frames), chunksize=10)):
            proc.stdin.write(rgb_bytes)
            if f_idx % 360 == 0 or f_idx == total_frames - 1:
                el = time.time() - t0
                fps_eff = (f_idx + 1) / max(0.001, el)
                print(f"[Render] Frame {f_idx+1}/{total_frames} ({(f_idx+1)/total_frames*100:.1f}%) | {fps_eff:.1f} fps", flush=True)

    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg exited with code {rc}")

    # Extract 6 QA frames + copy alignment metadata into qa_dir
    for qi, frac in enumerate([0.08, 0.22, 0.36, 0.56, 0.80, 0.96]):
        ts = round(align_data["total_duration"] * frac, 2)
        subprocess.check_call([
            "ffmpeg", "-y", "-ss", str(ts), "-i", out_mp4,
            "-vframes", "1", os.path.join(qa_dir, f"qa_{qi:02d}_{ts}s.png")
        ], stderr=subprocess.DEVNULL)
    subprocess.check_call(["cp", align_json, os.path.join(qa_dir, "alignment.json")])
    print(f"[Done] High-Quality 60fps Reel saved -> {out_mp4} ({os.path.getsize(out_mp4)/1e6:.2f} MB) in {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "--dry-preview":
        run_dry_preview(sys.argv[2], sys.argv[3])
    elif mode == "--cloud-render":
        run_full_cloud_pipeline(
            font_dir=sys.argv[2],
            work_dir=sys.argv[3],
            out_mp4=sys.argv[4],
            qa_dir=sys.argv[5],
            whisper_size=sys.argv[6] if len(sys.argv) > 6 else "medium",
        )
