"""
Instagram Reel Cover Generator — Episode 04 (تله‌ی عددِ وسط / اثرِ طعمه)
Page: زاویه ذهن (@zavieh.penhann)

Engineered simultaneously for all 3 Instagram aspect ratios:
  1. Full Reels Cover:       1080 x 1920 (9:16)
  2. Profile Main Grid:      1080 x 1440 (3:4 center crop -> y in [240 .. 1680])
  3. Legacy Square Preview:  1080 x 1080 (1:1 center crop -> y in [420 .. 1500])
"""
import os, sys, math
import cairocffi as cairo
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.engine.render_core import (
    W, H, FontBank, clamp, fa,
    get_text_sprite, get_fitted_text_sprite,
    rounded_rect_path, draw_star4, draw_pill_badge,
    draw_ambient_particles, draw_hypnotic_chronograph_ring,
    draw_cursor_pointer, composite_oled_frame,
)


def _draw_cafe_cup_cover(
    cs, cg, cx: float, base_y: float, top_w: float, h: float,
    alpha: float = 1.0, glow: bool = False, dashed: bool = False, steam: bool = False
):
    bot_w = top_w * 0.70
    y_top = base_y - h
    layers = [(cs, 3.0 if glow else 2.5, alpha * 0.96)]
    if glow:
        layers.append((cg, 7.2, alpha * 0.62))
    else:
        layers.append((cg, 4.8, alpha * 0.24))

    for ctx, lw, al in layers:
        ctx.save()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_dash([9.0, 7.0] if dashed else [])

        # Tapered cup body
        ctx.new_path()
        ctx.move_to(cx - top_w * 0.5, y_top)
        ctx.line_to(cx - bot_w * 0.5, base_y)
        ctx.line_to(cx + bot_w * 0.5, base_y)
        ctx.line_to(cx + top_w * 0.5, y_top)
        ctx.close_path()
        if ctx is cs:
            fill_a = 0.13 if glow else 0.04
            ctx.set_source_rgba(1, 1, 1, fill_a * alpha) if glow else ctx.set_source_rgba(0.03, 0.03, 0.05, 0.94 * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()

        # Barista cardboard heat sleeve
        ctx.set_dash([])
        sl_y0 = base_y - h * 0.65
        sl_y1 = base_y - h * 0.34
        w0 = bot_w + (top_w - bot_w) * 0.65
        w1 = bot_w + (top_w - bot_w) * 0.34
        ctx.move_to(cx - w0 * 0.5, sl_y0); ctx.line_to(cx + w0 * 0.5, sl_y0); ctx.stroke()
        ctx.move_to(cx - w1 * 0.5, sl_y1); ctx.line_to(cx + w1 * 0.5, sl_y1); ctx.stroke()

        # Raised barista lid rim + dome
        rim_w = top_w * 1.09
        rounded_rect_path(ctx, cx - rim_w * 0.5, y_top - 14, rim_w, 14, 4)
        ctx.stroke()
        ctx.move_to(cx - top_w * 0.44, y_top - 14)
        ctx.line_to(cx - top_w * 0.33, y_top - 30)
        ctx.line_to(cx + top_w * 0.33, y_top - 30)
        ctx.line_to(cx + top_w * 0.44, y_top - 14)
        ctx.stroke()
        ctx.restore()

    if steam:
        for ctx, lw, al in ((cs, 2.1, alpha * 0.62), (cg, 4.5, alpha * 0.28)):
            ctx.save()
            ctx.set_dash([])
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            for si, x_off in enumerate((-top_w * 0.22, 0.0, top_w * 0.22)):
                ctx.set_source_rgba(1, 1, 1, al * (0.85 if si == 1 else 0.65))
                ctx.set_line_width(lw)
                for step in range(16):
                    u = step / 15.0
                    sy = (y_top - 42) - u * 56.0
                    sx = cx + x_off + math.sin(u * 4.8 + si * 1.9) * 8.0
                    if step == 0:
                        ctx.move_to(sx, sy)
                    else:
                        ctx.line_to(sx, sy)
                ctx.stroke()
            ctx.restore()


def _draw_barbed_fishing_hook(cs, cg, anchor_x: float, top_y: float, tip_y: float):
    """Gleaming vertical fishing line & sharp J-hook catching the middle decoy cup!"""
    for ctx, lw, al in ((cs, 3.0, 0.96), (cg, 6.8, 0.54)):
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)

        # Vertical taut fishing line
        ctx.move_to(anchor_x, top_y)
        ctx.line_to(anchor_x, tip_y - 44)
        ctx.stroke()

        # Hook eyelet ring
        ctx.arc(anchor_x, tip_y - 36, 7.5, 0, 2 * math.pi)
        ctx.stroke()

        # Classic J-hook curve + sharp barb hooking right under lid center!
        ctx.move_to(anchor_x, tip_y - 28.5)
        ctx.line_to(anchor_x, tip_y - 4)
        ctx.arc(anchor_x - 20, tip_y - 4, 20, 0, math.pi)
        ctx.line_to(anchor_x - 40, tip_y - 21)
        ctx.stroke()
        # Sharp inner barb
        ctx.move_to(anchor_x - 40, tip_y - 21)
        ctx.line_to(anchor_x - 29, tip_y - 13)
        ctx.stroke()
        ctx.restore()


def _draw_jump_arc_arrow(cs, cg, x0: float, y0: float, x1: float, y1: float, peak_dy: float = -88.0):
    """Smooth Bezier jump arrow from Decoy (135) -> Target Large (150)."""
    cx1 = x0 + (x1 - x0) * 0.30
    cy1 = min(y0, y1) + peak_dy
    cx2 = x0 + (x1 - x0) * 0.72
    cy2 = min(y0, y1) + peak_dy

    for ctx, lw, al in ((cs, 2.8, 0.94), (cg, 6.4, 0.48)):
        ctx.save()
        ctx.set_dash([9.0, 6.0])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(x0, y0)
        ctx.curve_to(cx1, cy1, cx2, cy2, x1, y1)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()

        # Solid crisp arrowhead at (x1, y1)
        ctx.set_dash([])
        ang = math.atan2(y1 - cy2, x1 - cx2)
        for da in (-2.55, 2.55):
            ctx.move_to(x1, y1)
            ctx.line_to(x1 + math.cos(ang + da) * 18.0, y1 + math.sin(ang + da) * 18.0)
            ctx.stroke()
        ctx.restore()


def build_ep04_cover(font_dir: str, out_png: str, qa_crops_png: str | None = None):
    fonts = FontBank(font_dir)
    eb_98 = ImageFont.truetype(f"{font_dir}/Vazirmatn-ExtraBold.ttf", 98)
    eb_62 = ImageFont.truetype(f"{font_dir}/Vazirmatn-ExtraBold.ttf", 62)
    bold_40 = ImageFont.truetype(f"{font_dir}/Vazirmatn-Bold.ttf", 40)

    sg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cg = cairo.Context(sg)
    ss = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cs = cairo.Context(ss)

    txts = []

    # 1. Pure #000000 OLED atmospheric stardust + subtle corner framing ticks
    draw_ambient_particles(cs, 4.2, alpha=0.80)
    for ctx, lw, al in ((cs, 1.8, 0.28), (cg, 4.0, 0.12)):
        ctx.save()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        for sx in (76, W - 76):
            dx = 26 if sx < 540 else -26
            for sy, dy in ((272, 26), (1648, -26)):
                ctx.move_to(sx, sy + dy); ctx.line_to(sx, sy); ctx.line_to(sx + dx, sy); ctx.stroke()
        ctx.restore()

    # 2. Top Dossier Pill (y = 335 — cleanly inside 3:4 Profile Grid [240..1680])
    draw_pill_badge(
        cs, cg, txts, "پرونده ۰۴  |  اقتصادِ پنهان",
        540, 335, fonts.bold_30, alpha=0.95, glow=True, pad_x=38, pad_y=13
    )

    # 3. Main Scroll-Stopping Headline & Sub-Hook (y = 508 & y = 612 — generous breathing room in 1:1, 3:4 & 9:16!)
    sp_title = get_fitted_text_sprite("تله‌ی عددِ وسط", eb_98, 900, (255, 255, 255, 255), glow=0.95)
    sp_sub   = get_fitted_text_sprite("چرا همیشه گرون‌ترین گزینه رو می‌خری؟", bold_40, 880, (214, 214, 232, 255), glow=0.35)
    txts.append((sp_title, 540, 508, 1.0))
    txts.append((sp_sub,   540, 612, 1.0))

    # 4. Hero @ensan.besham Metaphor: Fishing Hook + 3 Cafe Cups (90 -> 135 Decoy -> 150 Target!)
    base_y = 1152.0

    # Subtle hypnotic radar arc at top of fishing line (cx=540, cy=694)
    draw_hypnotic_chronograph_ring(cs, cg, 540, 694, 40.0, 2.4, alpha=0.68, draw_p=1.0, speed=1.0)
    cs.arc(540, 694, 6.5, 0, 2 * math.pi)
    cs.set_source_rgba(1, 1, 1, 0.95); cs.fill()

    # Barbed fishing hook dropping straight from radar node (y=734) into Middle Cup lid (y=926)!
    _draw_barbed_fishing_hook(cs, cg, 540, 734, 926)

    # Crisp "طعمه!" pill right beside the fishing line
    draw_pill_badge(cs, cg, txts, "طعمه!", 642, 818, fonts.bold_30, alpha=0.96, glow=True, pad_x=24, pad_y=8)

    # Glowing counter baseline
    for ctx, lw, al in ((cs, 2.6, 0.72), (cg, 6.0, 0.28)):
        ctx.save()
        ctx.move_to(108, base_y)
        ctx.line_to(972, base_y)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.stroke()
        ctx.restore()

    # RIGHT CUP (Small — 90): dimmed logical baseline
    cx_s, cx_m, cx_l = 825.0, 540.0, 248.0
    _draw_cafe_cup_cover(cs, cg, cx_s, base_y, top_w=108, h=152, alpha=0.55, glow=False, dashed=False, steam=False)

    # CENTER CUP (Medium — 135 Decoy!): dashed trap-cup hooked on the barbed fishing line!
    _draw_cafe_cup_cover(cs, cg, cx_m, base_y, top_w=138, h=198, alpha=0.88, glow=False, dashed=True, steam=False)
    # Subtle X-mark inside middle cup showing it's never meant to be bought ("۰٪ خرید")
    for ctx, lw, al in ((cs, 2.4, 0.58), (cg, 5.0, 0.22)):
        ctx.save(); ctx.set_dash([])
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw)
        ctx.move_to(cx_m - 24, base_y - 118); ctx.line_to(cx_m + 24, base_y - 70); ctx.stroke()
        ctx.move_to(cx_m + 24, base_y - 118); ctx.line_to(cx_m - 24, base_y - 70); ctx.stroke()
        ctx.restore()

    # LEFT CUP (Large — 150 Real Seller Target!): blazing hero cup + spotlight + steam + star!
    # Subtle glow frame around winner/target cup
    for ctx, lw, al in ((cs, 2.0, 0.42), (cg, 5.5, 0.24)):
        ctx.save(); ctx.set_dash([])
        rounded_rect_path(ctx, cx_l - 112, base_y - 318, 224, 336, 22)
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        ctx.restore()

    _draw_cafe_cup_cover(cs, cg, cx_l, base_y, top_w=166, h=248, alpha=1.0, glow=True, dashed=False, steam=True)
    draw_star4(cs, cx_l, base_y - 122, 22.0, 0.98)
    draw_star4(cg, cx_l, base_y - 122, 38.0, 0.78)
    draw_cursor_pointer(cs, cg, cx_l - 68, base_y - 62, scale=1.18, click_p=0.65, alpha=0.96)

    # Curved jump arrow from Middle (135) -> Large (150) + "فقط ۱۵ تومن بیشتر؟!" micro-hook!
    _draw_jump_arc_arrow(cs, cg, cx_m - 58, base_y - 235, cx_l + 78, base_y - 282, peak_dy=-68.0)
    sp_jump = get_fitted_text_sprite("فقط ۱۵ تومن بیشتر؟!", fonts.bold_30, 255, (255, 255, 255, 255), glow=0.65)
    txts.append((sp_jump, 398, 784, 0.98))

    # 5. Price & Role Pedestal Numbers Below Counter (y = 1212 .. 1310 — zero overlap!)
    # Small (90)
    sp_p90  = get_text_sprite(fa("90"), fonts.bold_52, (168, 168, 186, 255), glow=0.0)
    sp_l90  = get_fitted_text_sprite("کوچک", fonts.reg_26, 170, (150, 150, 168, 255))
    txts.append((sp_p90, cx_s, 1214, 0.92))
    txts.append((sp_l90, cx_s, 1282, 0.85))

    # Medium Decoy (135)
    sp_p135 = get_text_sprite(fa("135"), eb_62, (222, 222, 238, 255), glow=0.35)
    sp_l135 = get_fitted_text_sprite("متوسط (طعمه)", fonts.bold_30, 220, (205, 205, 224, 255))
    txts.append((sp_p135, cx_m, 1214, 0.96))
    txts.append((sp_l135, cx_m, 1284, 0.94))

    # Large Target (150)
    sp_p150 = get_text_sprite(fa("150"), fonts.eb_68, (255, 255, 255, 255), glow=0.92)
    sp_l150 = get_fitted_text_sprite("بزرگ (۸۴٪ خرید!)", fonts.bold_30, 240, (255, 255, 255, 255), glow=0.55)
    txts.append((sp_p150, cx_l, 1212, 1.0))
    txts.append((sp_l150, cx_l, 1284, 1.0))

    # 6. Bottom Signature @zavieh.penhann Brand Pill (y = 1422 — inside BOTH 1:1 [420..1500] & 3:4 [240..1680]!)
    draw_pill_badge(cs, cg, txts, "@zavieh.penhann", 540, 1422, fonts.med_32, alpha=0.92, glow=True, pad_x=38, pad_y=12)

    # Subtle bottom-most Reels 9:16 editorial footer (gracefully outside 1:1 crop, adds luxury depth in full 9:16 view)
    sp_foot = get_fitted_text_sprite("زاویه ذهن  •  کالبدشکافیِ تله‌های قیمت‌گذاری", fonts.light_22, 760, (135, 135, 152, 255))
    txts.append((sp_foot, 540, 1595, 0.78))

    raw_rgb = composite_oled_frame(sg, ss, txts, fonts, t=0.0, sub_lines=[])
    img_full = Image.frombytes("RGB", (W, H), raw_rgb)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    img_full.save(out_png, format="PNG", optimize=True)

    if qa_crops_png:
        # Build visual QA board verifying [1] Full 9:16, [2] 3:4 Profile Grid (1080x1440), [3] 1:1 Square (1080x1080)
        board = Image.new("RGB", (1420, 760), (18, 18, 24))
        d = ImageDraw.Draw(board)

        # Panel 1: Full 9:16 (360 x 640) with dashed green 3:4 & cyan 1:1 safe-zone overlays
        p916 = img_full.copy()
        d9 = ImageDraw.Draw(p916)
        d9.rectangle([4, 240, 1075, 1680], outline=(0, 230, 110), width=4)   # 3:4 Profile Grid
        d9.rectangle([8, 420, 1071, 1500], outline=(70, 195, 255), width=4)  # 1:1 Square Grid
        board.paste(p916.resize((360, 640), Image.Resampling.LANCZOS), (40, 60))

        # Panel 2: Exact 3:4 Instagram Profile Grid Crop (1080x1440 -> 450x600)
        crop_3x4 = img_full.crop((0, 240, 1080, 1680)).resize((450, 600), Image.Resampling.LANCZOS)
        board.paste(crop_3x4, (445, 80))
        d.rectangle([445, 80, 895, 680], outline=(0, 230, 110), width=2)

        # Panel 3: Exact 1:1 Legacy Square Crop (1080x1080 -> 440x440)
        crop_1x1 = img_full.crop((0, 420, 1080, 1500)).resize((440, 440), Image.Resampling.LANCZOS)
        board.paste(crop_1x1, (940, 160))
        d.rectangle([940, 160, 1380, 600], outline=(70, 195, 255), width=2)

        board.save(qa_crops_png, format="PNG")


if __name__ == "__main__":
    f_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/fonts_cover"
    o_png = sys.argv[2] if len(sys.argv) > 2 else "/home/user/zavieh_zehn_ep04_cover_ig.png"
    q_png = sys.argv[3] if len(sys.argv) > 3 else None
    build_ep04_cover(f_dir, o_png, q_png)
    print(f"Saved Episode 04 cover -> {o_png}")
