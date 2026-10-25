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
