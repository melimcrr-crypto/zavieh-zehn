import os, math
import numpy as np
import cairocffi as cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 60
SAFE_MARGIN_X = 64.0  # Strict horizontal screen safe-zone [64 .. 1016]

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
def fa(s) -> str:
    return str(s).translate(FA_DIGITS)

def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return a if x < a else (b if x > b else x)

def ease_out_cubic(x: float) -> float:
    x = clamp(x)
    return 1.0 - (1.0 - x) ** 3

def ease_in_out_cubic(x: float) -> float:
    x = clamp(x)
    return 4 * x * x * x if x < 0.5 else 1.0 - ((-2 * x + 2) ** 3) / 2.0

def spring_pop(x: float) -> float:
    """Remotion-style damped spring (damping=13, stiffness=150) for snappy badges & frames."""
    x = clamp(x)
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    return 1.0 - math.exp(-6.5 * x) * math.cos(9.5 * x)

def window_fade(t: float, t0: float, t1: float, fi: float = 0.32, fo: float = 0.32) -> float:
    if t < t0 or t > t1:
        return 0.0
    a = clamp((t - t0) / fi) if fi > 0 else 1.0
    b = clamp((t1 - t) / fo) if fo > 0 else 1.0
    return ease_out_cubic(min(a, b))


class FontBank:
    def __init__(self, font_dir: str):
        self.light_22 = ImageFont.truetype(f"{font_dir}/Vazirmatn-Light.ttf", 22)
        self.light_26 = ImageFont.truetype(f"{font_dir}/Vazirmatn-Light.ttf", 26)
        self.reg_26   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Regular.ttf", 26)
        self.reg_30   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Regular.ttf", 30)
        self.reg_34   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Regular.ttf", 34)
        self.med_32   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Medium.ttf", 32)
        self.med_36   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Medium.ttf", 36)
        self.sub_40   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Medium.ttf", 40) # Constant fixed subtitle font!
        self.bold_30  = ImageFont.truetype(f"{font_dir}/Vazirmatn-Bold.ttf", 30)
        self.bold_36  = ImageFont.truetype(f"{font_dir}/Vazirmatn-Bold.ttf", 36)
        self.bold_44  = ImageFont.truetype(f"{font_dir}/Vazirmatn-Bold.ttf", 44)
        self.bold_52  = ImageFont.truetype(f"{font_dir}/Vazirmatn-Bold.ttf", 52)
        self.eb_68    = ImageFont.truetype(f"{font_dir}/Vazirmatn-ExtraBold.ttf", 68)
        self.eb_84    = ImageFont.truetype(f"{font_dir}/Vazirmatn-ExtraBold.ttf", 84)
        self.eb_92    = ImageFont.truetype(f"{font_dir}/Vazirmatn-ExtraBold.ttf", 92)


_SPRITE_CACHE = {}
_SUB_PAIR_CACHE = {}

def get_text_sprite(text: str, font, color=(255, 255, 255, 255), glow: float = 0.0) -> Image.Image:
    """Metric-baseline-locked text sprite so typography never jitters vertically."""
    key = (text, id(font), color, round(glow, 2))
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]
    if len(_SPRITE_CACHE) > 140:
        _SPRITE_CACHE.clear()

    t_dir = "ltr" if text.isascii() else "rtl"
    ascent, descent = font.getmetrics()
    dummy = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font, direction=t_dir, language="fa")
    pad_x, pad_y = 32, 26
    tw = max(1, bbox[2] - bbox[0] + pad_x * 2)
    th = max(1, ascent + descent + pad_y * 2)
    ox = pad_x - bbox[0]
    oy = pad_y  # Pillow draws from top of ascent box -> constant baseline across all strings!

    fg = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(fg).text((ox, oy), text, font=font, fill=color, direction=t_dir, language="fa")

    if glow > 0.01:
        ga = int(clamp(glow) * 205)
        g_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(g_img).text((ox, oy), text, font=font, fill=(255, 255, 255, ga), direction=t_dir, language="fa")
        out = Image.alpha_composite(g_img.filter(ImageFilter.GaussianBlur(radius=13)), fg)
    else:
        out = fg

    _SPRITE_CACHE[key] = out
    return out



_FIT_FONT_CACHE = {}

def measure_text_width(text: str, font) -> float:
    t_dir = "ltr" if text.isascii() else "rtl"
    dummy = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    bb = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font, direction=t_dir, language="fa")
    return float(bb[2] - bb[0])

def fit_font_to_width(text: str, font, max_width: float, min_px: int = 16):
    """Automatically steps down font size if text exceeds max_width -> 0.0px overflow guaranteed!"""
    w = measure_text_width(text, font)
    if w <= max_width or not hasattr(font, "path"):
        return font
    cur_sz = getattr(font, "size", 28)
    est_sz = max(min_px, int(cur_sz * (max_width / max(1.0, w)) * 0.97))
    while est_sz > min_px:
        fkey = (font.path, est_sz)
        if fkey not in _FIT_FONT_CACHE:
            _FIT_FONT_CACHE[fkey] = ImageFont.truetype(font.path, est_sz)
        cand = _FIT_FONT_CACHE[fkey]
        if measure_text_width(text, cand) <= max_width:
            return cand
        est_sz -= 1
    fkey = (font.path, min_px)
    if fkey not in _FIT_FONT_CACHE:
        _FIT_FONT_CACHE[fkey] = ImageFont.truetype(font.path, min_px)
    return _FIT_FONT_CACHE[fkey]

def wrap_persian_lines(text: str, font, max_width: float) -> list[str]:
    """Splits a long Persian/LTR string into balanced lines that each fit inside max_width."""
    words = text.split()
    if len(words) <= 1 or measure_text_width(text, font) <= max_width:
        return [text]
    lines, cur = [], words[0]
    for w in words[1:]:
        cand = cur + " " + w
        if measure_text_width(cand, font) <= max_width:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines

def get_fitted_text_sprite(text: str, font, max_width: float, color=(255, 255, 255, 255), glow: float = 0.0, min_px: int = 18) -> Image.Image:
    """
    Bulletproof container text sprite:
    1) Steps font size down cleanly down to min_px.
    2) If still wider than max_width, auto-wraps into balanced multi-line RTL sprite!
    Guarantees visible ink width <= max_width in 100% of cases.
    """
    txt_fa = text if text.isascii() else fa(text)
    safe_font = fit_font_to_width(txt_fa, font, max_width, min_px=min_px)
    if measure_text_width(txt_fa, safe_font) <= max_width:
        return get_text_sprite(txt_fa, safe_font, color=color, glow=glow)

    # Multi-line RTL auto-wrap at readable min_px!
    wrapped = wrap_persian_lines(txt_fa, safe_font, max_width)
    line_sprites = []
    for ln in wrapped:
        ln_font = fit_font_to_width(ln, safe_font, max_width, min_px=12)
        sp_ln = get_text_sprite(ln, ln_font, color=color, glow=glow)
        if sp_ln.width > int(max_width + 64):
            ratio = (max_width + 48) / sp_ln.width
            sp_ln = sp_ln.resize((int(sp_ln.width * ratio), max(1, int(sp_ln.height * ratio))), Image.Resampling.LANCZOS)
        line_sprites.append(sp_ln)

    line_step = max(24, int(getattr(safe_font, "size", 20) * 1.42))
    out_w = max(sp.width for sp in line_sprites)
    out_h = line_sprites[0].height + line_step * (len(line_sprites) - 1)
    combo = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    for i, sp in enumerate(line_sprites):
        combo.alpha_composite(sp, ((out_w - sp.width) // 2, i * line_step))
    return combo

def paste_center(canvas: Image.Image, sprite: Image.Image, cx: float, cy: float, alpha: float = 1.0):
    if alpha <= 0.01:
        return
    if alpha < 0.995:
        r, g, b, a = sprite.split()
        a = a.point(lambda p: int(p * alpha))
        sprite = Image.merge("RGBA", (r, g, b, a))
    x = int(round(clamp(cx - sprite.width / 2.0, 16.0, W - sprite.width - 16.0)))
    y = int(round(cy - sprite.height / 2.0))
    canvas.alpha_composite(sprite, (x, y))


def _get_subtitle_bitmap_pair(sub: dict, font):
    """
    Builds ONE single shaped HarfBuzz/Raqm line in two identical-geometry RGBA arrays
    (dim gray & glowing white) + exact monotonic RTL wipe knot coordinates!
    Guarantees 0.000px vertical/horizontal jitter and silky @ensan.besham gradient wipe.
    """
    full_fa = fa(sub["full"])
    key = (full_fa, tuple(sub["times"]), tuple(sub.get("ends", [])))
    if key in _SUB_PAIR_CACHE:
        return _SUB_PAIR_CACHE[key]
    if len(_SUB_PAIR_CACHE) > 40:
        _SUB_PAIR_CACHE.clear()

    ascent, descent = font.getmetrics()
    dummy = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dummy)
    bbox = dd.textbbox((0, 0), full_fa, font=font, direction="rtl", language="fa")

    # Auto step-down only if an unusually wide phrase exceeds 940px
    use_font = font
    if (bbox[2] - bbox[0]) > 940:
        use_font = ImageFont.truetype(font.path, 35)
        ascent, descent = use_font.getmetrics()
        bbox = dd.textbbox((0, 0), full_fa, font=use_font, direction="rtl", language="fa")

    pad_x, pad_y = 44, 28
    txt_w = bbox[2] - bbox[0]
    tw = max(1, txt_w + pad_x * 2)
    th = max(1, ascent + descent + pad_y * 2)
    ox = pad_x - bbox[0]
    oy = pad_y

    # 1. Dim unspoken layer: exact @ensan.besham matte silver-charcoal rgba(255,255,255,0.26)
    dim_im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(dim_im).text((ox, oy), full_fa, font=use_font, fill=(70, 70, 76, 255), direction="rtl", language="fa")

    # 2. Lit spoken layer: crisp #FFFFFF + soft subtle @ensan.besham white bloom
    lit_fg = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(lit_fg).text((ox, oy), full_fa, font=use_font, fill=(252, 252, 255, 255), direction="rtl", language="fa")
    lit_gl = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(lit_gl).text((ox, oy), full_fa, font=use_font, fill=(255, 255, 255, 115), direction="rtl", language="fa")
    lit_im = Image.alpha_composite(lit_gl.filter(ImageFilter.GaussianBlur(radius=9)), lit_fg)

    # 3. Exact RTL cumulative word x-coordinates inside [pad_x .. pad_x + txt_w]
    tokens_fa = [fa(tk) for tk in sub["tokens"]]
    x_right = float(pad_x + txt_w)
    x_left  = float(pad_x)

    t_knots = [sub["times"][0] - 0.04]
    x_knots = [x_right + 28.0]

    ends = sub.get("ends") or [sub["times"][min(k+1, len(sub["times"])-1)] for k in range(len(tokens_fa))]
    for k in range(len(tokens_fa)):
        prefix_str = " ".join(tokens_fa[:k + 1])
        pw = dd.textlength(prefix_str, font=use_font, direction="rtl", language="fa")
        x_edge = max(x_left, x_right - pw)
        if k == len(tokens_fa) - 1:
            x_edge = x_left - 28.0
        t_end_k = max(t_knots[-1] + 0.03, float(ends[k]))
        t_knots.append(t_end_k)
        x_knots.append(x_edge)

    entry = {
        "dim_arr": np.array(dim_im, dtype=np.float32),
        "lit_arr": np.array(lit_im, dtype=np.float32),
        "tw": tw,
        "th": th,
        "baseline_offset": oy + ascent,
        "t_knots": np.array(t_knots, dtype=np.float64),
        "x_knots": np.array(x_knots, dtype=np.float64),
    }
    _SUB_PAIR_CACHE[key] = entry
    return entry


def render_liquid_rtl_subtitle(canvas: Image.Image, t: float, sub_lines: list[dict], font):
    """
    Renders @ensan.besham-identical baseline-locked, sub-pixel feathered RTL gradient wipe subtitle.
    """
    active_sub = None
    for sub in sub_lines:
        if sub["start"] <= t <= sub["end"]:
            active_sub = sub
            break
    if active_sub is None:
        return

    fi = clamp((t - active_sub["start"]) / 0.18)
    fo = clamp((active_sub["end"] - t) / 0.16)
    line_alpha = ease_out_cubic(min(fi, fo))
    if line_alpha <= 0.01:
        return

    entry = _get_subtitle_bitmap_pair(active_sub, font)
    # Smooth 5-point temporal micro-filter (+/- 35ms) so wipe velocity is pure liquid silk!
    ts_probe = np.array([t - 0.035, t - 0.017, t, t + 0.017, t + 0.035])
    wipe_x = float(np.mean(np.interp(ts_probe, entry["t_knots"], entry["x_knots"])))

    # 1D horizontal feathered ramp (feather = 64px across active Persian word, matching @ensan.besham!)
    feather = 64.0
    xs = np.arange(entry["tw"], dtype=np.float32)
    # Right of wipe_x => 1.0 (spoken white); Left of wipe_x => 0.0 (unspoken dim gray)
    mask_1d = np.clip((xs - (wipe_x - feather * 0.5)) / feather, 0.0, 1.0)[None, :, None]

    blended = entry["dim_arr"] * (1.0 - mask_1d) + entry["lit_arr"] * mask_1d
    if line_alpha < 0.998:
        blended[:, :, 3] *= line_alpha

    sub_im = Image.fromarray(blended.astype(np.uint8), mode="RGBA")

    # Constant fixed typographical baseline at y = 1642 (with subtle 4px upward float on entrance)
    y_glide = (1.0 - ease_out_cubic(fi)) * 4.5
    paste_x = int(round(W / 2.0 - entry["tw"] / 2.0))
    paste_y = int(round(1642.0 - entry["baseline_offset"] + y_glide))
    canvas.alpha_composite(sub_im, (paste_x, paste_y))


# =============================================================================
# @ensan.besham-GRADE VECTOR PRIMITIVES (Stroke-Draw, Camera, Humans, Pills, HUD)
# =============================================================================

def set_stroke_draw(ctx, progress: float, approx_len: float = 900.0):
    p = clamp(progress)
    if p >= 0.999:
        ctx.set_dash([])
    else:
        ctx.set_dash([max(0.1, approx_len * p), approx_len * 2.0], 0)

def rounded_rect_path(ctx, x: float, y: float, w: float, h: float, r: float):
    r = min(r, w / 2.0, h / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()

def draw_star4(ctx, cx: float, cy: float, r: float, alpha: float = 1.0):
    if r <= 0.2 or alpha <= 0.01:
        return
    ctx.save()
    ctx.set_dash([])
    ctx.translate(cx, cy)
    ctx.move_to(0, -r)
    ctx.curve_to(r * 0.16, -r * 0.16, r * 0.16, -r * 0.16, r, 0)
    ctx.curve_to(r * 0.16, r * 0.16, r * 0.16, r * 0.16, 0, r)
    ctx.curve_to(-r * 0.16, r * 0.16, -r * 0.16, r * 0.16, -r, 0)
    ctx.curve_to(-r * 0.16, -r * 0.16, -r * 0.16, -r * 0.16, 0, -r)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.fill()
    ctx.restore()

def draw_stipple_line(ctx, x0, y0, x1, y1, count: int, r: float = 1.7, alpha: float = 0.8):
    if count <= 0 or alpha <= 0.01:
        return
    ctx.save()
    ctx.set_dash([])
    ctx.set_source_rgba(1, 1, 1, alpha)
    for i in range(count + 1):
        u = i / max(1, count)
        ctx.arc(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, r, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()

def draw_human_figure(
    ctx, cx: float, cy: float, scale: float = 1.0, alpha: float = 1.0,
    draw_p: float = 1.0, lw: float = 2.2, vortex: bool = False, star_mind: bool = False, t: float = 0.0
):
    """
    Signature @ensan.besham geometric monoline human figure (Panels 1, 2, 3, 9, 10):
    Clean circular head + architectural rounded shoulder-arm-torso silhouette + legs.
    Origin (cx, cy) is at the feet (standing point on pedestal/ground)!
    """
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(scale, scale)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.set_line_width(lw / max(0.35, scale))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # Head circle (center at 0, -148, r=22)
    set_stroke_draw(ctx, draw_p, 160.0)
    ctx.arc(0, -148, 22, 0, 2 * math.pi)
    ctx.stroke()

    # Architectural rounded shoulders + outer arms + inner torso + legs (exact @ensan.besham silhouette!)
    set_stroke_draw(ctx, draw_p, 520.0)
    ctx.move_to(-18, -118)
    ctx.curve_to(-36, -118, -42, -104, -42, -86)
    ctx.line_to(-42, -46)
    ctx.line_to(-30, -46)
    ctx.line_to(-30, -84)
    ctx.move_to(-26, -84)
    ctx.line_to(-26, 0)
    ctx.line_to(-6, 0)
    ctx.line_to(-6, -52)
    ctx.line_to(6, -52)
    ctx.line_to(6, 0)
    ctx.line_to(26, 0)
    ctx.line_to(26, -84)
    ctx.move_to(30, -84)
    ctx.line_to(30, -46)
    ctx.line_to(42, -46)
    ctx.line_to(42, -86)
    ctx.curve_to(42, -104, 36, -118, 18, -118)
    ctx.close_path()
    ctx.stroke()

    ctx.set_dash([])
    if vortex:
        # Concentric spiral rings inside head (Panel 4 homage!)
        for ri in (6, 11, 16):
            ctx.arc(0, -148, ri, t * 2.5 + ri, t * 2.5 + ri + math.pi * 1.45)
            ctx.stroke()
    if star_mind:
        draw_star4(ctx, 0, -148, 10, alpha)

    ctx.restore()


def draw_pill_badge(
    cs, cg, text_overlays: list, text: str, cx: float, cy: float,
    font, alpha: float = 1.0, glow: bool = False, pad_x: float = 30.0, pad_y: float = 13.0, max_box_w: float = 920.0
):
    """Exact @ensan.besham bordered pill tag with automatic text-fit & screen-margin clamp (0px overflow!)."""
    if alpha <= 0.01:
        return
    disp_txt = text if text.isascii() else fa(text)
    pad_x = max(24.0, pad_x)
    safe_font = fit_font_to_width(disp_txt, font, max_box_w - pad_x * 2)
    sp = get_text_sprite(disp_txt, safe_font, (250, 250, 255, 255) if glow else (210, 210, 220, 255), glow=0.55 if glow else 0.0)
    dummy = Image.new("RGBA", (4, 4))
    t_dir = "ltr" if disp_txt.isascii() else "rtl"
    bb = ImageDraw.Draw(dummy).textbbox((0, 0), disp_txt, font=safe_font, direction=t_dir, language="fa")
    bw = (bb[2] - bb[0]) + pad_x * 2
    bh = (bb[3] - bb[1]) + pad_y * 2
    cx = clamp(cx, SAFE_MARGIN_X + bw / 2.0, W - SAFE_MARGIN_X - bw / 2.0)

    cs.save()
    cs.set_dash([])
    rounded_rect_path(cs, cx - bw / 2, cy - bh / 2, bw, bh, 9.0)
    cs.set_source_rgba(0.02, 0.02, 0.03, 0.92 * alpha)
    cs.fill_preserve()
    cs.set_source_rgba(1, 1, 1, (0.82 if glow else 0.34) * alpha)
    cs.set_line_width(2.0 if glow else 1.4)
    cs.stroke()
    cs.restore()

    if glow:
        cg.save()
        rounded_rect_path(cg, cx - bw / 2, cy - bh / 2, bw, bh, 9.0)
        cg.set_source_rgba(1, 1, 1, 0.55 * alpha)
        cg.set_line_width(4.5)
        cg.stroke()
        cg.restore()

    text_overlays.append((sp, cx, cy, alpha))


def draw_folder_window(
    cs, cg, text_overlays: list, cx: float, cy: float, w: float, h: float,
    tab_label: str, font_tab, alpha: float = 1.0, draw_p: float = 1.0
):
    """
    Signature @ensan.besham chamfered folder-tab HUD window (Panel 7 '[ انسان ]' card!).
    """
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    x0, y0 = cx - w / 2.0, cy - h / 2.0
    x1, y1 = cx + w / 2.0, cy + h / 2.0
    safe_tab_font = fit_font_to_width(fa(tab_label), font_tab, max(120.0, w - 120.0))
    dummy_tb = Image.new("RGBA", (4, 4))
    bb_tb = ImageDraw.Draw(dummy_tb).textbbox((0, 0), fa(tab_label), font=safe_tab_font, direction="rtl", language="fa")
    tab_w = clamp(float(bb_tb[2] - bb_tb[0]) + 68.0, 175.0, w - 70.0)
    tab_h = 44.0

    for ctx, lw, al in ((cs, 2.0, alpha * 0.78), (cg, 4.5, alpha * 0.32)):
        ctx.save()
        set_stroke_draw(ctx, draw_p, (w + h) * 2.2)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.move_to(x0, y0)
        ctx.line_to(x1 - tab_w - 22, y0)
        ctx.line_to(x1 - tab_w, y0 - tab_h)
        ctx.line_to(x1, y0 - tab_h)
        ctx.line_to(x1, y1)
        ctx.line_to(x0, y1)
        ctx.close_path()
        ctx.stroke()
        # Subtle inner top divider under tab
        ctx.set_dash([])
        ctx.set_source_rgba(1, 1, 1, al * 0.25)
        ctx.set_line_width(1.1)
        ctx.move_to(x0, y0 + 2); ctx.line_to(x1, y0 + 2); ctx.stroke()
        ctx.restore()

    if draw_p > 0.35:
        sp_tb = get_text_sprite(fa(tab_label), safe_tab_font, (235, 235, 242, 255), glow=0.25)
        text_overlays.append((sp_tb, x1 - tab_w / 2.0, y0 - tab_h / 2.0 + 2, alpha * clamp((draw_p - 0.35) / 0.4)))


def draw_stamp_badge(
    cs, cg, text_overlays: list, text: str, cx: float, cy: float,
    angle_deg: float, font, alpha: float = 1.0, pop_p: float = 1.0
):
    """Double-bordered angled stamp badge ('[ انجام دادید ]' from Panel 7!) with spring impact."""
    if alpha <= 0.01 or pop_p <= 0.01:
        return
    sc = 1.32 - 0.32 * spring_pop(pop_p)
    dummy = Image.new("RGBA", (4, 4))
    bb = ImageDraw.Draw(dummy).textbbox((0, 0), fa(text), font=font, direction="rtl", language="fa")
    bw = (bb[2] - bb[0]) + 62
    bh = (bb[3] - bb[1]) + 30

    for ctx, lw, al in ((cs, 2.4, alpha * 0.96), (cg, 5.5, alpha * 0.72)):
        ctx.save()
        ctx.set_dash([])
        ctx.translate(cx, cy)
        ctx.rotate(math.radians(angle_deg))
        ctx.scale(sc, sc)
        if ctx is cs:
            ctx.rectangle(-bw/2, -bh/2, bw, bh)
            ctx.set_source_rgba(0, 0, 0, 0.96 * alpha)
            ctx.fill()
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.rectangle(-bw/2, -bh/2, bw, bh)
        ctx.stroke()
        ctx.set_line_width(lw * 0.5)
        ctx.rectangle(-bw/2 + 6, -bh/2 + 6, bw - 12, bh - 12)
        ctx.stroke()
        ctx.restore()

    sp = get_text_sprite(fa(text), font, (255, 255, 255, 255), glow=0.65)
    sp_rot = sp.rotate(-angle_deg, resample=Image.Resampling.BICUBIC, expand=True)
    text_overlays.append((sp_rot, cx, cy, alpha * clamp(pop_p * 1.8)))




def draw_safe_card(
    cs, cg, text_overlays: list, cx: float, cy: float, w: float, h: float,
    lines_spec: list[tuple], radius: float = 12.0, pad_x: float = 28.0,
    alpha: float = 1.0, glow_border: bool = False, allow_expand: bool = True, max_w: float = 920.0
):
    """
    Universal overflow-proof card container for @zavieh.penhann scenes!
    lines_spec: list of (text, font, y_offset_from_cy, color_rgba, glow_float)
    Guarantees every line stays strictly inside [cx - w/2 + pad_x .. cx + w/2 - pad_x]
    and clamps card inside [SAFE_MARGIN_X .. W - SAFE_MARGIN_X].
    """
    if alpha <= 0.01:
        return
    pad_x = max(24.0, pad_x)
    req_w = w
    if allow_expand and lines_spec:
        widest = max(measure_text_width(t if t.isascii() else fa(t), fnt) for (t, fnt, _, _, _) in lines_spec)
        req_w = min(max_w, max(w, widest + pad_x * 2))
    cx = clamp(cx, SAFE_MARGIN_X + req_w / 2.0, W - SAFE_MARGIN_X - req_w / 2.0)

    cs.save()
    cs.set_dash([])
    rounded_rect_path(cs, cx - req_w / 2.0, cy - h / 2.0, req_w, h, radius)
    cs.set_source_rgba(0.03, 0.03, 0.04, 0.92 * alpha)
    cs.fill_preserve()
    cs.set_source_rgba(1, 1, 1, (0.84 if glow_border else 0.68) * alpha)
    cs.set_line_width(2.1 if glow_border else 1.7)
    cs.stroke()
    cs.restore()

    if glow_border:
        cg.save()
        rounded_rect_path(cg, cx - req_w / 2.0, cy - h / 2.0, req_w, h, radius)
        cg.set_source_rgba(1, 1, 1, 0.42 * alpha)
        cg.set_line_width(4.2)
        cg.stroke()
        cg.restore()

    inner_max_w = max(60.0, req_w - pad_x * 2)
    for (txt, fnt, dy, col, glw) in lines_spec:
        sp = get_fitted_text_sprite(txt, fnt, inner_max_w, color=col, glow=glw)
        text_overlays.append((sp, cx, cy + dy, alpha))


_AMBIENT_SEEDS = [
    ((i * 173 + 91) % 940 + 70, (i * 293 + 211) % 1220 + 210, 1.0 + (i % 3) * 0.55, 0.35 + (i % 5) * 0.14, i * 1.13)
    for i in range(28)
]

def draw_ambient_particles(cs, t: float, alpha: float = 1.0):
    """Subtle 60fps floating OLED micro-dust that gives continuous spatial depth across scenes."""
    if alpha <= 0.01:
        return
    cs.save()
    cs.set_dash([])
    for bx, by, rad, spd, ph in _AMBIENT_SEEDS:
        px = bx + math.sin(t * spd + ph) * 18.0
        py = 210 + ((by - 210 - t * (9.0 + spd * 14.0)) % 1220.0)
        twk = 0.05 + 0.09 * (0.5 + 0.5 * math.sin(t * 2.1 + ph * 2.0))
        cs.arc(px, py, rad, 0, 2 * math.pi)
        cs.set_source_rgba(1, 1, 1, twk * alpha)
        cs.fill()
    cs.restore()


def draw_curved_arrow(
    ctx, x0: float, y0: float, x1: float, y1: float, bend: float = -75.0,
    progress: float = 1.0, alpha: float = 1.0, lw: float = 2.4
):
    """Progressive quadratic Bézier arc + auto-oriented arrowhead at leading tip!"""
    p = clamp(progress)
    if p <= 0.01 or alpha <= 0.01:
        return
    mx = 0.5 * (x0 + x1)
    my = 0.5 * (y0 + y1) + bend
    # Sample N points up to parameter p for crisp partial drawing + exact tangent at tip
    N = 32
    ctx.save()
    ctx.set_dash([])
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.set_line_width(lw)
    pts = []
    for k in range(N + 1):
        u = (k / N) * p
        px = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u ** 2 * x1
        py = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u ** 2 * y1
        pts.append((px, py))
    ctx.move_to(*pts[0])
    for px, py in pts[1:]:
        ctx.line_to(px, py)
    ctx.stroke()

    if len(pts) >= 2:
        tx, ty = pts[-1]
        px_prev, py_prev = pts[-2]
        ang = math.atan2(ty - py_prev, tx - px_prev)
        ah = 13.0
        ctx.move_to(tx, ty)
        ctx.line_to(tx - ah * math.cos(ang - 0.48), ty - ah * math.sin(ang - 0.48))
        ctx.move_to(tx, ty)
        ctx.line_to(tx - ah * math.cos(ang + 0.48), ty - ah * math.sin(ang + 0.48))
        ctx.stroke()
    ctx.restore()


def draw_cursor_pointer(cs, cg, x: float, y: float, click_p: float = 0.0, alpha: float = 1.0, scale: float = 1.0):
    """Sleek vector arrow cursor + expanding concentric sonar click-ripples!"""
    if alpha <= 0.01:
        return
    press_sc = scale * (1.0 - 0.16 * math.sin(math.pi * clamp(click_p * 2.0)) if 0.0 < click_p < 0.5 else 1.0)
    for ctx, lw, al in ((cs, 2.3, alpha * 0.98), (cg, 5.0, alpha * 0.65)):
        ctx.save()
        ctx.set_dash([])
        ctx.translate(x, y)
        ctx.scale(press_sc, press_sc)
        if ctx is cs:
            ctx.move_to(0, 0); ctx.line_to(0, 38); ctx.line_to(11, 29); ctx.line_to(20, 46)
            ctx.line_to(27, 42); ctx.line_to(18, 25); ctx.line_to(31, 25); ctx.close_path()
            ctx.set_source_rgba(0.03, 0.03, 0.04, 0.95 * alpha); ctx.fill_preserve()
        else:
            ctx.move_to(0, 0); ctx.line_to(0, 38); ctx.line_to(11, 29); ctx.line_to(20, 46)
            ctx.line_to(27, 42); ctx.line_to(18, 25); ctx.line_to(31, 25); ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        ctx.restore()

    if 0.01 < click_p < 0.99:
        for mult in (1.0, 0.62):
            rp = clamp(click_p / mult)
            if rp < 1.0:
                rr = 10.0 + rp * 68.0
                ra = (1.0 - rp) * 0.78 * alpha
                cs.arc(x, y, rr, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, ra); cs.set_line_width(1.9); cs.stroke()
                cg.arc(x, y, rr, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, ra * 0.55); cg.set_line_width(4.0); cg.stroke()


# =============================================================================
# STUDIO v3.0 HYPNOTIC CINEMA CAMERA, EDITING SHOCKWAVES & HOROLOGY PRIMITIVES
# =============================================================================

def impact_punch(t: float, cue_t: float, amp: float = 0.032, dur: float = 0.55) -> float:
    """Damped editing beat-punch zoom delta triggered on reveal timestamps."""
    if t < cue_t or t > cue_t + dur:
        return 0.0
    u = (t - cue_t) / max(0.05, dur)
    return amp * math.sin(math.pi * min(1.0, u * 1.35)) * math.exp(-3.1 * u)


def push_camera(cs, cg, zoom: float = 1.0, dx: float = 0.0, dy: float = 0.0, px: float = 540.0, py: float = 860.0):
    """Pushes a synchronized 60fps virtual cinema camera onto sharp + bloom Cairo contexts."""
    for ctx in (cs, cg):
        ctx.save()
        ctx.translate(px + dx, py + dy)
        ctx.scale(zoom, zoom)
        ctx.translate(-px, -py)


def pop_camera_and_transform_texts(
    cs, cg, scene_txts: list, out_txts: list,
    zoom: float = 1.0, dx: float = 0.0, dy: float = 0.0, px: float = 540.0, py: float = 860.0
):
    """Restores Cairo camera state and locks scene text overlays to the exact camera motion."""
    cs.restore()
    cg.restore()
    for sp, tx, ty, al in scene_txts:
        nx = px + (tx - px) * zoom + dx
        ny = py + (ty - py) * zoom + dy
        out_txts.append((sp, nx, ny, al))


def draw_shockwave_ring(cs, cg, cx: float, cy: float, progress: float, max_r: float = 380.0, alpha: float = 1.0):
    """Kinetic editing impact ring + 12 radial light streaks on dramatic reveals."""
    p = clamp(progress)
    if p <= 0.01 or p >= 0.99 or alpha <= 0.01:
        return
    ep = ease_out_cubic(p)
    fade = (1.0 - p) ** 1.45 * alpha
    r1 = 28.0 + ep * max_r
    r2 = 16.0 + ep * (max_r * 0.68)
    cs.save(); cg.save()
    cs.set_dash([]); cg.set_dash([])
    cs.arc(cx, cy, r1, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.72 * fade); cs.set_line_width(2.0); cs.stroke()
    cg.arc(cx, cy, r1, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.50 * fade); cg.set_line_width(5.0); cg.stroke()
    cs.arc(cx, cy, r2, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.35 * fade); cs.set_line_width(1.2); cs.stroke()
    for k in range(12):
        ang = k * (math.pi / 6.0)
        ri = r2 + 12.0
        ro = r1 + 18.0
        cs.move_to(cx + math.cos(ang) * ri, cy + math.sin(ang) * ri)
        cs.line_to(cx + math.cos(ang) * ro, cy + math.sin(ang) * ro)
        cs.set_source_rgba(1, 1, 1, 0.44 * fade); cs.set_line_width(1.4); cs.stroke()
    cs.restore(); cg.restore()


def draw_hypnotic_chronograph_ring(
    cs, cg, cx: float, cy: float, radius: float, t: float,
    alpha: float = 1.0, draw_p: float = 1.0, speed: float = 1.0
):
    """
    Perpetual counter-rotating Swiss chronograph / astronomical dial:
    60 outer second ticks + 12 luminous hour batons + counter-rotating inner orbital + sweeping needle.
    """
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    dp = clamp(draw_p)
    cs.save(); cg.save()
    cs.set_dash([]); cg.set_dash([])

    # Outer soft halo circle
    cs.arc(cx, cy, radius, -math.pi / 2, -math.pi / 2 + 2 * math.pi * dp)
    cs.set_source_rgba(1, 1, 1, 0.24 * alpha); cs.set_line_width(1.3); cs.stroke()

    # 60 rotating horology ticks
    n_ticks = int(60 * dp)
    rot_outer = t * 0.22 * speed
    for k in range(n_ticks):
        ang = k * (2 * math.pi / 60.0) + rot_outer
        is_maj = (k % 5 == 0)
        r_in = radius - (16.0 if is_maj else 8.0)
        r_out = radius - 2.0
        x0, y0 = cx + math.cos(ang) * r_in, cy + math.sin(ang) * r_in
        x1, y1 = cx + math.cos(ang) * r_out, cy + math.sin(ang) * r_out
        cs.move_to(x0, y0); cs.line_to(x1, y1)
        cs.set_source_rgba(1, 1, 1, (0.72 if is_maj else 0.28) * alpha)
        cs.set_line_width(2.2 if is_maj else 1.1)
        cs.stroke()
        if is_maj:
            cg.move_to(x0, y0); cg.line_to(x1, y1)
            cg.set_source_rgba(1, 1, 1, 0.35 * alpha); cg.set_line_width(4.0); cg.stroke()

    # Counter-rotating inner segmented orbital ring
    r_orb = radius * 0.78
    rot_in = -t * 0.36 * speed
    for seg_i in range(4):
        a0 = rot_in + seg_i * (math.pi / 2.0) + 0.14
        a1 = a0 + (math.pi / 2.0 - 0.28) * dp
        if a1 > a0:
            cs.arc(cx, cy, r_orb, a0, a1)
            cs.set_source_rgba(1, 1, 1, 0.22 * alpha); cs.set_line_width(1.3); cs.stroke()

    # Sweeping precision chronograph needle (1 rev per 8s * speed)
    if dp > 0.5:
        na = -math.pi / 2.0 + t * (2 * math.pi / 8.0) * speed
        nx = cx + math.cos(na) * (radius - 20.0)
        ny = cy + math.sin(na) * (radius - 20.0)
        cs.move_to(cx - math.cos(na) * 18.0, cy - math.sin(na) * 18.0)
        cs.line_to(nx, ny)
        cs.set_source_rgba(1, 1, 1, 0.45 * alpha); cs.set_line_width(1.5); cs.stroke()
        cs.arc(nx, ny, 3.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.88 * alpha); cs.fill()
        cg.arc(nx, ny, 7.5, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.55 * alpha); cg.fill()

    cs.restore(); cg.restore()


def draw_hourglass_monolith(
    cs, cg, cx: float, cy: float, w: float, h: float,
    sand_top: float = 0.65, flowing: bool = True, t: float = 0.0,
    alpha: float = 1.0, draw_p: float = 1.0
):
    """Architectural OLED Hourglass with live draining upper dune, falling luminous stream & rising lower cone."""
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    dp = clamp(draw_p)
    hw, hh = w * 0.5, h * 0.5
    top_y, bot_y = cy - hh, cy + hh
    neck_w = max(7.0, w * 0.07)

    for ctx, lw, al in ((cs, 2.5, alpha * 0.95), (cg, 5.2, alpha * 0.42)):
        ctx.save()
        set_stroke_draw(ctx, dp, 900.0)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        # Top & Bottom brushed caps
        rounded_rect_path(ctx, cx - hw - 10, top_y - 12, w + 20, 12, 4); ctx.stroke()
        rounded_rect_path(ctx, cx - hw - 10, bot_y, w + 20, 12, 4); ctx.stroke()
        # Twin outer architectural pillars
        ctx.move_to(cx - hw - 4, top_y); ctx.line_to(cx - hw - 4, bot_y); ctx.stroke()
        ctx.move_to(cx + hw + 4, top_y); ctx.line_to(cx + hw + 4, bot_y); ctx.stroke()
        # Left & Right curved glass bulbs
        ctx.move_to(cx - hw + 8, top_y)
        ctx.curve_to(cx - hw + 8, cy - hh * 0.25, cx - neck_w, cy - hh * 0.14, cx - neck_w, cy)
        ctx.curve_to(cx - neck_w, cy + hh * 0.14, cx - hw + 8, cy + hh * 0.25, cx - hw + 8, bot_y)
        ctx.stroke()
        ctx.move_to(cx + hw - 8, top_y)
        ctx.curve_to(cx + hw - 8, cy - hh * 0.25, cx + neck_w, cy - hh * 0.14, cx + neck_w, cy)
        ctx.curve_to(cx + neck_w, cy + hh * 0.14, cx + hw - 8, cy + hh * 0.25, cx + hw - 8, bot_y)
        ctx.stroke()
        ctx.restore()

    if dp > 0.45:
        sf = clamp(sand_top)
        bf = clamp(1.0 - sf)
        cs.save(); cg.save()
        cs.set_dash([]); cg.set_dash([])
        # Upper sand pool (funneling into neck)
        if sf > 0.03:
            sh = (hh - 14.0) * (0.22 + 0.72 * sf)
            sw = (hw - 14.0) * (0.32 + 0.65 * sf)
            dip = 9.0 * (1.0 if flowing else 0.0)
            cs.move_to(cx - sw, cy - sh)
            cs.curve_to(cx - sw * 0.35, cy - sh + dip, cx + sw * 0.35, cy - sh + dip, cx + sw, cy - sh)
            cs.curve_to(cx + sw * 0.75, cy - sh * 0.35, cx + neck_w * 0.8, cy - 8, cx, cy - 2)
            cs.curve_to(cx - neck_w * 0.8, cy - 8, cx - sw * 0.75, cy - sh * 0.35, cx - sw, cy - sh)
            cs.close_path()
            cs.set_source_rgba(1, 1, 1, 0.26 * alpha); cs.fill_preserve()
            cs.set_source_rgba(1, 1, 1, 0.78 * alpha); cs.set_line_width(1.6); cs.stroke()

        # Lower sand mound (rising smoothly)
        if bf > 0.03:
            mh = (hh - 14.0) * (0.14 + 0.72 * bf)
            mw = hw - 14.0
            cs.move_to(cx - mw, bot_y - 3)
            cs.curve_to(cx - mw * 0.38, bot_y - 3 - mh * 1.35, cx + mw * 0.38, bot_y - 3 - mh * 1.35, cx + mw, bot_y - 3)
            cs.close_path()
            cs.set_source_rgba(1, 1, 1, 0.30 * alpha); cs.fill_preserve()
            cs.set_source_rgba(1, 1, 1, 0.82 * alpha); cs.set_line_width(1.6); cs.stroke()
            cg.arc(cx, bot_y - 3 - mh * 0.72, 10.0, 0, 2 * math.pi)
            cg.set_source_rgba(1, 1, 1, 0.35 * alpha); cg.fill()

        # Falling luminous sand grains through neck!
        if flowing:
            mound_tip_y = bot_y - 4 - (hh - 14.0) * (0.14 + 0.72 * bf) * 0.72
            cs.move_to(cx, cy); cs.line_to(cx, mound_tip_y)
            cs.set_source_rgba(1, 1, 1, 0.65 * alpha); cs.set_line_width(1.8); cs.stroke()
            cg.move_to(cx, cy); cg.line_to(cx, mound_tip_y)
            cg.set_source_rgba(1, 1, 1, 0.45 * alpha); cg.set_line_width(4.2); cg.stroke()
            for gi in range(9):
                gu = ((t * 2.6 + gi / 9.0) % 1.0)
                gy = cy + (mound_tip_y - cy) * gu
                gx = cx + math.sin(gi * 2.3 + t * 9.0) * 1.8
                cs.arc(gx, gy, 2.1, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.95 * alpha); cs.fill()
            # Micro-sparks bouncing off sand peak
            for si in range(4):
                su = ((t * 3.4 + si * 0.25) % 1.0)
                ang_s = -math.pi * (0.22 + 0.56 * ((si * 37) % 10) / 10.0)
                sx = cx + math.cos(ang_s) * su * 22.0 * (1 if si % 2 == 0 else -1)
                sy = mound_tip_y + math.sin(ang_s) * su * 16.0 + (su ** 2) * 18.0
                cs.arc(sx, sy, 1.6, 0, 2 * math.pi)
                cs.set_source_rgba(1, 1, 1, (1.0 - su) * 0.85 * alpha); cs.fill()
        cs.restore(); cg.restore()


def draw_ecg_waveform(cs, cg, x0: float, x1: float, y_mid: float, t: float, amp: float = 34.0, alpha: float = 1.0):
    """Live scrolling P-Q-R-S-T human heartbeat phosphor lifeline."""
    if alpha <= 0.01 or x1 <= x0 + 20:
        return
    span = x1 - x0
    head_u = (t * 0.48) % 1.0
    head_x = x0 + head_u * span

    def _pqrst(phase_01: float) -> float:
        # Sharp realistic P-Q-R-S-T pulse centered at phase 0.50
        d = phase_01 - 0.50
        p_wv = 0.18 * math.exp(-((d + 0.14) / 0.032) ** 2)
        q_wv = -0.22 * math.exp(-((d + 0.045) / 0.015) ** 2)
        r_wv = 1.00 * math.exp(-(d / 0.018) ** 2)
        s_wv = -0.34 * math.exp(-((d - 0.042) / 0.016) ** 2)
        t_wv = 0.26 * math.exp(-((d - 0.16) / 0.042) ** 2)
        return -(p_wv + q_wv + r_wv + s_wv + t_wv)

    cs.save(); cg.save()
    cs.set_dash([]); cg.set_dash([])
    N_pts = 150
    prev = None
    for i in range(N_pts + 1):
        u = i / N_pts
        px = x0 + u * span
        # 2.5 beats visible across width
        beat_ph = (u * 2.5) % 1.0
        py = y_mid + _pqrst(beat_ph) * amp
        # Phosphor trail brightness behind sweeping head_u
        age = (head_u - u) % 1.0
        inten = (1.0 - age) ** 1.8
        if prev is not None and abs(u - head_u) > 0.018:
            cs.move_to(prev[0], prev[1]); cs.line_to(px, py)
            cs.set_source_rgba(1, 1, 1, (0.14 + 0.80 * inten) * alpha)
            cs.set_line_width(2.2); cs.stroke()
            if inten > 0.55:
                cg.move_to(prev[0], prev[1]); cg.line_to(px, py)
                cg.set_source_rgba(1, 1, 1, 0.45 * inten * alpha)
                cg.set_line_width(4.6); cg.stroke()
        prev = (px, py)

    head_y = y_mid + _pqrst((head_u * 2.5) % 1.0) * amp
    cs.arc(head_x, head_y, 4.5, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.98 * alpha); cs.fill()
    cg.arc(head_x, head_y, 11.0, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.78 * alpha); cg.fill()
    cs.restore(); cg.restore()


# =============================================================================
# STUDIO v4.0 EXPRESSIVE HUMAN CHARACTER RIG & @ensan.besham HYPER-CUT PRIMITIVES
# =============================================================================

def draw_character_with_phone(
    cs, cg, cx: float, foot_y: float, scale: float = 1.0,
    raise_p: float = 1.0, screen_glow: float = 1.0,
    t: float = 0.0, alpha: float = 1.0, draw_p: float = 1.0,
    star_mind: bool = False, facing_right: bool = True
):
    """
    Signature @ensan.besham human protagonist holding their smartphone in hand!
    - Smoothly raises forearm + phone from side (raise_p=0) up to face level (raise_p=1)
    - Casts translucent volumetric screen light cone directly onto face!
    - Returns (phone_x, phone_y, chest_x, chest_y) in world coordinates.
    """
    if alpha <= 0.01 or draw_p <= 0.01:
        return (cx, foot_y - 100 * scale, cx, foot_y - 95 * scale)

    rp = clamp(raise_p)
    dp = clamp(draw_p)
    sgn = 1.0 if facing_right else -1.0
    breathe = math.sin(t * 2.4) * 1.8

    # Head tilts gently toward the raised phone
    hx_loc = sgn * (7.0 * rp)
    hy_loc = -148.0 + 5.0 * rp + breathe * 0.5

    # Shoulder -> Elbow -> Hand holding phone kinematics
    sh_x, sh_y = sgn * 24.0, -110.0 + breathe * 0.4
    el_x = sh_x + sgn * (12.0 + 14.0 * rp)
    el_y = sh_y + 34.0 * (1.0 - 0.35 * rp)
    hd_x = el_x + sgn * (-4.0 + 26.0 * rp)
    hd_y = el_y + (26.0 * (1.0 - rp) - 38.0 * rp)

    ph_loc_x = hd_x + sgn * 7.0
    ph_loc_y = hd_y - 12.0

    # Volumetric phone screen glow cone onto character's face!
    if screen_glow > 0.03 and rp > 0.25:
        ga = clamp(screen_glow) * clamp((rp - 0.2) / 0.8) * alpha
        cs.save()
        cs.translate(cx, foot_y)
        cs.scale(scale, scale)
        cs.set_dash([])
        p_grad = cairo.LinearGradient(ph_loc_x, ph_loc_y, hx_loc, hy_loc)
        p_grad.add_color_stop_rgba(0.0, 1, 1, 1, 0.36 * ga)
        p_grad.add_color_stop_rgba(0.7, 1, 1, 1, 0.10 * ga)
        p_grad.add_color_stop_rgba(1.0, 1, 1, 1, 0.00)
        cs.move_to(ph_loc_x - sgn * 3, ph_loc_y - 13)
        cs.line_to(hx_loc - sgn * 4, hy_loc - 25)
        cs.line_to(hx_loc + sgn * 16, hy_loc + 20)
        cs.line_to(ph_loc_x - sgn * 3, ph_loc_y + 13)
        cs.close_path()
        cs.set_source(p_grad)
        cs.fill()
        cs.restore()

    for ctx, lw, al in ((cs, 2.5, alpha * 0.96), (cg, 5.2, alpha * 0.38)):
        ctx.save()
        ctx.translate(cx, foot_y)
        ctx.scale(scale, scale)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw / max(0.35, scale))

        # Head
        set_stroke_draw(ctx, dp, 160.0)
        ctx.arc(hx_loc, hy_loc, 22.0, 0, 2 * math.pi)
        ctx.stroke()

        # Architectural torso + passive arm + legs
        set_stroke_draw(ctx, dp, 480.0)
        ctx.move_to(-sgn * 18, -118 + breathe * 0.4)
        ctx.curve_to(-sgn * 36, -118, -sgn * 40, -104, -sgn * 40, -86)
        ctx.line_to(-sgn * 40, -46)
        ctx.line_to(-sgn * 28, -46)
        ctx.line_to(-sgn * 28, -84)
        ctx.move_to(-24, -84)
        ctx.line_to(-24, 0); ctx.line_to(-6, 0); ctx.line_to(-6, -52)
        ctx.line_to(6, -52); ctx.line_to(6, 0); ctx.line_to(24, 0)
        ctx.line_to(24, -84)
        ctx.move_to(sgn * 18, -118 + breathe * 0.4)
        ctx.line_to(-sgn * 18, -118 + breathe * 0.4)
        ctx.stroke()

        # Articulated active arm holding smartphone!
        ctx.set_dash([])
        ctx.set_line_width((lw + 0.6) / max(0.35, scale))
        ctx.move_to(sh_x, sh_y)
        ctx.line_to(el_x, el_y)
        ctx.line_to(hd_x, hd_y)
        ctx.stroke()

        # Smartphone in hand (tilted slightly toward face)
        ctx.save()
        ctx.translate(ph_loc_x, ph_loc_y)
        ctx.rotate(-sgn * 0.24 * rp)
        rounded_rect_path(ctx, -9, -18, 18, 36, 4)
        if ctx is cs:
            ctx.set_source_rgba(1, 1, 1, (0.15 + 0.70 * screen_glow * rp) * alpha)
            ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, min(1.0, al * 1.15))
        ctx.set_line_width(lw / max(0.35, scale))
        ctx.stroke()
        ctx.restore()

        if star_mind:
            draw_star4(ctx, hx_loc, hy_loc, 11.0, al)
        ctx.restore()

    world_ph_x = cx + ph_loc_x * scale
    world_ph_y = foot_y + ph_loc_y * scale
    world_ch_x = cx
    world_ch_y = foot_y - 92.0 * scale
    return (world_ph_x, world_ph_y, world_ch_x, world_ch_y)


def draw_pov_phone_in_hand(
    cs, cg, cx: float, cy: float, w: float = 330.0, h: float = 610.0,
    thumb_swipe: float = 0.0, thumb_tap: float = 0.0,
    alpha: float = 1.0, draw_p: float = 1.0, bright_screen: bool = False
):
    """
    Exact @ensan.besham v04_11M POV Close-Up:
    Large smartphone gripped by anatomical monoline fingers (left bezel) + palm & articulated thumb (right side)!
    """
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    dp = clamp(draw_p)
    x0, y0 = cx - w / 2.0, cy - h / 2.0
    rad = 42.0

    # Screen fill (dark obsidian or @ensan.besham lit white glass!)
    cs.save(); cs.set_dash([])
    rounded_rect_path(cs, x0, y0, w, h, rad)
    if bright_screen:
        cs.set_source_rgba(0.92, 0.92, 0.95, 0.94 * alpha * dp)
    else:
        cs.set_source_rgba(0.035, 0.035, 0.05, 0.95 * alpha * dp)
    cs.fill()
    cs.restore()

    # Phone chassis & speaker island
    for ctx, lw, al in ((cs, 3.2, alpha * 0.98), (cg, 6.8, alpha * 0.52)):
        ctx.save()
        set_stroke_draw(ctx, dp, 2.2 * (w + h))
        rounded_rect_path(ctx, x0, y0, w, h, rad)
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
        rounded_rect_path(ctx, cx - 46, y0 + 22, 92, 14, 7)
        ctx.set_source_rgba(0.1, 0.1, 0.12, al) if bright_screen else ctx.set_source_rgba(1, 1, 1, al * 0.75)
        ctx.set_line_width(2.0); ctx.stroke()
        ctx.restore()

    if dp > 0.35:
        # 4 curved fingers gripping left edge of phone
        for ctx, lw, al in ((cs, 2.6, alpha * 0.92), (cg, 5.0, alpha * 0.32)):
            ctx.save(); ctx.set_dash([])
            for fi in range(4):
                fy = cy - 35.0 + fi * 48.0
                rounded_rect_path(ctx, x0 - 22, fy, 30, 34, 14)
                if ctx is cs:
                    ctx.set_source_rgba(0.03, 0.03, 0.04, 0.96 * alpha); ctx.fill_preserve()
                ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()

            # Right-side palm arch + wrist silhouette + articulated swiping thumb!
            sw_dy = -58.0 * math.sin(math.pi * clamp(thumb_swipe))
            press_dx = -8.0 * math.sin(math.pi * clamp(thumb_tap * 2.0)) if 0.0 < thumb_tap < 0.5 else 0.0
            th_tip_x = x0 + w - 88.0 + press_dx
            th_tip_y = cy + 72.0 + sw_dy

            ctx.new_path()
            ctx.move_to(x0 + w - 25, y0 + h + 95)
            ctx.curve_to(x0 + w + 52, y0 + h + 25, x0 + w + 58, cy + 120, x0 + w + 26, cy + 45)
            ctx.curve_to(x0 + w + 4, cy + 12, th_tip_x + 34, th_tip_y - 26, th_tip_x, th_tip_y - 16)
            ctx.curve_to(th_tip_x - 22, th_tip_y - 8, th_tip_x - 18, th_tip_y + 24, th_tip_x + 12, th_tip_y + 28)
            ctx.curve_to(x0 + w - 20, th_tip_y + 42, x0 + w - 8, y0 + h - 30, x0 + w - 85, y0 + h + 95)
            if ctx is cs:
                ctx.set_source_rgba(0.03, 0.03, 0.04, 0.96 * alpha); ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw); ctx.stroke()
            ctx.restore()

            if 0.02 < thumb_tap < 0.98 and ctx is cs:
                rr = 14.0 + ease_out_cubic(thumb_tap) * 58.0
                cs.arc(th_tip_x - 6, th_tip_y + 4, rr, 0, 2 * math.pi)
                cs.set_source_rgba(1, 1, 1, (1.0 - thumb_tap) * 0.85 * alpha)
                cs.set_line_width(2.0); cs.stroke()


def draw_character_at_desk(cs, cg, cx: float, ground_y: float, scale: float = 1.0, t: float = 0.0, alpha: float = 1.0):
    """60fps hunched office worker typing rapidly at glowing laptop desk."""
    if alpha <= 0.01:
        return
    typ = math.sin(t * 24.0) * 4.5
    # Laptop upward screen glow onto worker's face
    cs.save()
    cs.translate(cx, ground_y); cs.scale(scale, scale); cs.set_dash([])
    lg = cairo.LinearGradient(-48, -96, 22, -162)
    lg.add_color_stop_rgba(0.0, 1, 1, 1, 0.30 * alpha)
    lg.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)
    cs.move_to(-65, -92); cs.line_to(10, -172); cs.line_to(38, -132); cs.line_to(-32, -92)
    cs.close_path(); cs.set_source(lg); cs.fill()
    cs.restore()

    for ctx, lw, al in ((cs, 2.5, alpha * 0.94), (cg, 5.0, alpha * 0.36)):
        ctx.save()
        ctx.translate(cx, ground_y); ctx.scale(scale, scale)
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(1, 1, 1, al); ctx.set_line_width(lw / max(0.4, scale))

        # Ground + Desk table
        ctx.move_to(-185, 0); ctx.line_to(185, 0); ctx.stroke()
        ctx.move_to(-135, -88); ctx.line_to(15, -88); ctx.stroke()
        ctx.move_to(-120, -88); ctx.line_to(-120, 0); ctx.move_to(0, -88); ctx.line_to(0, 0); ctx.stroke()

        # Open glowing laptop on desk
        ctx.move_to(-92, -88); ctx.line_to(-32, -88); ctx.stroke()
        ctx.move_to(-92, -88); ctx.line_to(-108, -138); ctx.stroke()

        # Office chair
        ctx.move_to(42, -55); ctx.line_to(96, -55); ctx.line_to(106, -125); ctx.stroke()
        ctx.move_to(68, -55); ctx.line_to(68, 0); ctx.move_to(48, 0); ctx.line_to(88, 0); ctx.stroke()

        # Seated hunched human body + fast typing arms
        ctx.arc(24, -152, 20, 0, 2 * math.pi); ctx.stroke()
        ctx.move_to(34, -130); ctx.curve_to(56, -108, 66, -82, 62, -58) # curved back
        ctx.line_to(22, -56); ctx.line_to(18, 0); ctx.stroke()
        # Two typing forearms
        ctx.move_to(38, -120); ctx.line_to(-2, -98); ctx.line_to(-42, -94 + typ); ctx.stroke()
        ctx.move_to(34, -116); ctx.line_to(-8, -94); ctx.line_to(-52, -92 - typ); ctx.stroke()
        ctx.restore()


def draw_observatory_eye(
    cs, cg, cx: float, cy: float, radius: float = 46.0, t: float = 0.0,
    alpha: float = 1.0, scan_targets: list = None
):
    """Exact @ensan.besham top AI Observatory Eye + optional geometric scan rays."""
    if alpha <= 0.01:
        return
    cs.save(); cg.save(); cs.set_dash([]); cg.set_dash([])
    # Outer counter-rotating dotted halo
    for k in range(24):
        ang = k * (math.pi / 12.0) + t * 0.65
        cs.arc(cx + math.cos(ang) * radius, cy + math.sin(ang) * radius, 1.7, 0, 2 * math.pi)
        cs.set_source_rgba(1, 1, 1, 0.55 * alpha); cs.fill()
    # Inner solid iris + glowing pupil
    cs.arc(cx, cy, radius * 0.66, 0, 2 * math.pi)
    cs.set_source_rgba(1, 1, 1, 0.85 * alpha); cs.set_line_width(2.0); cs.stroke()
    cg.arc(cx, cy, radius * 0.66, 0, 2 * math.pi)
    cg.set_source_rgba(1, 1, 1, 0.40 * alpha); cg.set_line_width(4.5); cg.stroke()

    look_x = math.sin(t * 1.6) * 5.0
    cs.arc(cx + look_x, cy + 3.0, radius * 0.24, 0, 2 * math.pi)
    cs.set_source_rgba(1, 1, 1, 0.96 * alpha); cs.set_line_width(2.2); cs.stroke()
    cs.arc(cx + look_x, cy + 3.0, 3.5, 0, 2 * math.pi); cs.fill()

    if scan_targets:
        cs.set_dash([7.0, 7.0], -t * 28.0)
        for tx_s, ty_s in scan_targets:
            cs.move_to(cx, cy + radius * 0.68); cs.line_to(tx_s, ty_s)
            cs.set_source_rgba(1, 1, 1, 0.34 * alpha); cs.set_line_width(1.5); cs.stroke()
    cs.restore(); cg.restore()


def draw_tehran_skyline(cs, cg, y_base: float, alpha: float = 1.0, draw_p: float = 1.0):
    """
    @ensan.besham Panel 4 homage: Alborz mountain ridge + Azadi Tower (left) + Milad Tower (right) + skyline blocks!
    """
    if alpha <= 0.01 or draw_p <= 0.01:
        return
    cs.save()
    # 1. Alborz mountain ridgeline in delicate ghost silver
    set_stroke_draw(cs, draw_p, 1100.0)
    cs.set_source_rgba(1, 1, 1, alpha * 0.28)
    cs.set_line_width(1.3)
    pts_mtn = [(60, y_base-35), (190, y_base-105), (310, y_base-68), (470, y_base-145),
               (620, y_base-85), (775, y_base-155), (915, y_base-95), (1020, y_base-40)]
    cs.move_to(*pts_mtn[0])
    for px, py in pts_mtn[1:]:
        cs.line_to(px, py)
    cs.stroke()

    # 2. Azadi Tower silhouette on left (cx=235)
    az_x = 235.0
    for ctx, lw, al in ((cs, 2.1, alpha * 0.80), (cg, 4.2, alpha * 0.34)):
        set_stroke_draw(ctx, draw_p, 420.0)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.move_to(az_x - 42, y_base)
        ctx.curve_to(az_x - 32, y_base - 55, az_x - 24, y_base - 92, az_x - 22, y_base - 115)
        ctx.line_to(az_x + 22, y_base - 115)
        ctx.curve_to(az_x + 24, y_base - 92, az_x + 32, y_base - 55, az_x + 42, y_base)
        ctx.stroke()
        # Inner Azadi arch
        ctx.move_to(az_x - 24, y_base)
        ctx.curve_to(az_x - 16, y_base - 56, az_x + 16, y_base - 56, az_x + 24, y_base)
        ctx.stroke()

    # 3. City apartment blocks across horizon
    cs.set_source_rgba(1, 1, 1, alpha * 0.46)
    cs.set_line_width(1.7)
    blocks = [(95, 52, 48), (310, 58, 64), (382, 48, 42), (455, 66, 78), (545, 54, 52), (620, 62, 70), (705, 50, 46), (900, 64, 62)]
    for bx, bw, bh in blocks:
        set_stroke_draw(cs, draw_p, 260.0)
        cs.rectangle(bx, y_base - bh, bw, bh)
        cs.stroke()

    # 4. Iconic Milad Tower on right (cx=825)
    mx = 825.0
    for ctx, lw, al in ((cs, 2.2, alpha * 0.90), (cg, 4.8, alpha * 0.42)):
        set_stroke_draw(ctx, draw_p, 520.0)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        # Tapered shaft
        ctx.move_to(mx - 14, y_base); ctx.line_to(mx - 5, y_base - 135)
        ctx.move_to(mx + 14, y_base); ctx.line_to(mx + 5, y_base - 135)
        ctx.stroke()
        # Gondola head pod
        ctx.move_to(mx - 22, y_base - 152)
        ctx.line_to(mx - 10, y_base - 135); ctx.line_to(mx + 10, y_base - 135); ctx.line_to(mx + 22, y_base - 152)
        ctx.line_to(mx + 12, y_base - 170); ctx.line_to(mx - 12, y_base - 170)
        ctx.close_path()
        ctx.stroke()
        # Antenna spire
        ctx.move_to(mx, y_base - 170); ctx.line_to(mx, y_base - 215); ctx.stroke()

    cs.set_dash([])
    cs.set_source_rgba(1, 1, 1, alpha * 0.48)
    cs.set_line_width(1.4)
    cs.move_to(60, y_base); cs.line_to(1020, y_base); cs.stroke()
    cs.restore()


def draw_spotlight_cone(cs, cg, ax: float, ay: float, x_left: float, x_right: float, y_target: float, alpha: float = 1.0):
    """@ensan.besham Panel 9 translucent spotlight beam + crisp edge rays."""
    if alpha <= 0.01:
        return
    cs.save()
    cs.set_dash([])
    pat = cairo.LinearGradient(ax, ay, 0.5 * (x_left + x_right), y_target)
    pat.add_color_stop_rgba(0.0, 1, 1, 1, 0.16 * alpha)
    pat.add_color_stop_rgba(0.7, 1, 1, 1, 0.05 * alpha)
    pat.add_color_stop_rgba(1.0, 1, 1, 1, 0.00)
    cs.move_to(ax, ay)
    cs.line_to(x_left, y_target)
    cs.line_to(x_right, y_target)
    cs.close_path()
    cs.set_source(pat)
    cs.fill()

    for ctx, lw, al in ((cs, 2.0, alpha * 0.78), (cg, 4.5, alpha * 0.45)):
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(lw)
        ctx.move_to(ax, ay); ctx.line_to(x_left, y_target); ctx.stroke()
        ctx.move_to(ax, ay); ctx.line_to(x_right, y_target); ctx.stroke()
    cs.restore()


def draw_hud_chrome(
    cs, cg, text_overlays: list, fonts: FontBank, t: float, total_dur: float,
    ep_code: str, ep_title: str, chapter_starts: list[float]
):
    hud_alpha = window_fade(t, 0.0, total_dur, fi=0.35, fo=0.6)
    brand_fade = clamp((total_dur - 4.0 - t) / 0.55)
    hud_alpha *= brand_fade
    if hud_alpha <= 0.01:
        return

    # Exact @ensan.besham angled پرونده tab at top right + rotating AI/Observatory eye at top left
    cs.save()
    cs.set_dash([])
    cs.set_source_rgba(1, 1, 1, 0.14 * hud_alpha)
    cs.set_line_width(1.2)
    cs.move_to(70, 128)
    cs.line_to(665, 128)
    cs.line_to(690, 102)
    cs.line_to(1010, 102)
    cs.stroke()
    cs.restore()

    sp_lbl = get_text_sprite("پرونده", fonts.light_22, (135, 135, 145, 255))
    sp_val = get_text_sprite(fa(ep_title), fonts.bold_30, (245, 245, 250, 255), glow=0.35)
    text_overlays.append((sp_lbl, 962, 76, hud_alpha * 0.85))
    text_overlays.append((sp_val, 805, 76, hud_alpha * 0.95))

    # Top-left Observatory Dual Counter-Rotating Dotted Rings + Mind Angle
    ax, ay = 128, 92
    cs.save()
    cs.set_dash([])
    for k in range(16):
        ang = k * (math.pi / 8.0) + t * 0.55
        cs.arc(ax + math.cos(ang) * 32, ay + math.sin(ang) * 32, 1.3, 0, 2 * math.pi)
        cs.set_source_rgba(1, 1, 1, 0.42 * hud_alpha); cs.fill()
    for k in range(12):
        ang = k * (math.pi / 6.0) - t * 0.75
        cs.move_to(ax + math.cos(ang) * 38, ay + math.sin(ang) * 38)
        cs.line_to(ax + math.cos(ang) * 43, ay + math.sin(ang) * 43)
        cs.set_source_rgba(1, 1, 1, 0.28 * hud_alpha); cs.set_line_width(1.2); cs.stroke()
    cs.set_source_rgba(1, 1, 1, 0.92 * hud_alpha); cs.set_line_width(1.9)
    cs.move_to(ax + 9, ay + 4); cs.line_to(ax - 15, ay - 11); cs.stroke()
    cs.set_source_rgba(1, 1, 1, 0.48 * hud_alpha)
    cs.move_to(ax + 9, ay + 4); cs.line_to(ax - 15, ay + 12); cs.stroke()
    draw_star4(cs, ax + 9, ay + 4, 5.5, hud_alpha)
    draw_star4(cg, ax + 9, ay + 4, 9.0, hud_alpha * 0.8)
    cs.restore()

    # Bottom Chapter Progress Dots at y = 1538 (exact @ensan.besham spacing!)
    n_ch = len(chapter_starts)
    cur_ch = 0
    for ci, cs_t in enumerate(chapter_starts):
        if t >= cs_t:
            cur_ch = ci
    dot_gap = 22.0
    right_x = 540.0 + (n_ch - 1) * dot_gap / 2.0
    for ci in range(n_ch):
        dx = right_x - ci * dot_gap
        dy = 1538.0
        if ci == cur_ch:
            cs.arc(dx, dy, 4.6, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.96 * hud_alpha); cs.fill()
            cg.arc(dx, dy, 8.5, 0, 2 * math.pi); cg.set_source_rgba(1, 1, 1, 0.80 * hud_alpha); cg.fill()
        elif ci < cur_ch:
            cs.arc(dx, dy, 2.8, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.42 * hud_alpha); cs.fill()
        else:
            cs.arc(dx, dy, 2.4, 0, 2 * math.pi); cs.set_source_rgba(1, 1, 1, 0.16 * hud_alpha); cs.fill()


def composite_oled_frame(surf_glow, surf_sharp, text_overlays: list, fonts: FontBank, t: float, sub_lines: list[dict]) -> bytes:
    buf_g = np.frombuffer(surf_glow.get_data(), dtype=np.uint8).reshape((H, W, 4))
    img_g = Image.fromarray(buf_g[:, :, [2, 1, 0, 3]], mode="RGBA")

    small_g = img_g.resize((W // 4, H // 4), Image.Resampling.BILINEAR)
    bloom_wide = small_g.filter(ImageFilter.GaussianBlur(radius=8.0)).resize((W, H), Image.Resampling.BILINEAR)
    bloom_core = small_g.filter(ImageFilter.GaussianBlur(radius=2.3)).resize((W, H), Image.Resampling.BILINEAR)

    buf_s = np.frombuffer(surf_sharp.get_data(), dtype=np.uint8).reshape((H, W, 4))
    img_s = Image.fromarray(buf_s[:, :, [2, 1, 0, 3]], mode="RGBA")

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    canvas.alpha_composite(bloom_wide)
    canvas.alpha_composite(bloom_core)
    canvas.alpha_composite(img_s)

    for sp, cx, cy, al in text_overlays:
        paste_center(canvas, sp, cx, cy, al)

    render_liquid_rtl_subtitle(canvas, t, sub_lines, fonts.sub_40)

    return canvas.convert("RGB").tobytes()
