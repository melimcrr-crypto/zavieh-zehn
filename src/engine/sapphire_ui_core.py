"""
Studio v6.0 — Sapphire Rim-Lit Glassmorphic UI & Volumetric 3D Character Engine
Modeled forensically on high-retention dark-glass SaaS/Finance motion graphics (https://pin.it/5EdbcB1Tn):
  1. Vignetted Architectural Cyan Blueprint Grid over pure #02050A obsidian.
  2. Dual-Surface Full-RGB Compositor (Base Glass/3D Volume + 32-Bit Float Multi-Octave RGB Emissive Bloom
     with Horizontal Anamorphic Optical Flare Streaks + Filmic Anti-Banding Micro-Dither).
  3. Saber / Travelling Laser-Edge Frosted Glass Cards, 3D Emerald Check / Crimson X Medallions,
     Cyan Sphere Checklist Badges, Multi-Curve Financial Charts, Split Probability Bars, & Dual Gauges.
  4. Volumetric 3D Fresnel Rim-Lit Faceless Blue Characters:
     - Side-view sitting at desk with glowing monitor, bokeh wall charts, floor reflection & neon '???'
     - Front-view thinking pose behind laptop & coffee mug with glowing dot-eyes & chin hand.
  5. Multi-Tone Highlighted Persian Typography (HarfBuzz-locked RTL word coloring) + Clean y=1515 Subtitle.
"""
import math
import numpy as np
import cairocffi as cairo
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, zoom

from src.engine.render_core import (
    W, H, FPS, FontBank, clamp, ease_out_cubic, ease_in_out_cubic,
    fa, fit_font_to_width, get_fitted_text_sprite, paste_center,
    _get_subtitle_bitmap_pair, rounded_rect_path
)

SAPPHIRE_SUB_Y = 1515.0  # Safely above Instagram's @username / Follow / caption UI!

# Signature Palette (normalized 0..1 floats for Cairo)
C_CYAN_CORE = (0.58, 0.91, 1.00)    # #94E8FF
C_CYAN_MID  = (0.16, 0.68, 0.98)    # #29ADFA
C_BLUE_DEEP = (0.04, 0.22, 0.48)    # #0A387A
C_GREEN     = (0.32, 1.00, 0.52)    # #52FF85
C_RED       = (1.00, 0.28, 0.30)    # #FF474D
C_AMBER     = (1.00, 0.76, 0.28)    # #FFC247
C_GLASS_BG  = (0.038, 0.058, 0.092) # #0A0F17


def exp_in_out(x: float) -> float:
    x = clamp(x)
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    if x < 0.5:
        return 0.5 * math.pow(2.0, 15.0 * x - 7.5)
    return 1.0 - 0.5 * math.pow(2.0, -15.0 * x + 7.5)


def set_trim_path(ctx, start_p: float, end_p: float, total_len: float = 1200.0):
    s = clamp(start_p)
    e = clamp(end_p)
    if e <= s + 0.001:
        ctx.set_dash([0.0, total_len * 3.0], 0.0)
    elif s <= 0.001 and e >= 0.999:
        ctx.set_dash([])
    else:
        seg = max(0.5, (e - s) * total_len)
        ctx.set_dash([seg, total_len * 3.0], -s * total_len)


# =============================================================================
# PRECOMPUTED VIGNETTED CYAN ARCHITECTURAL GRID + ANTI-BANDING DITHER
# =============================================================================
_BG_CACHE = None
_DITHER = np.random.default_rng(6060).uniform(-0.52, 0.52, (H, W, 1)).astype(np.float32)


def get_sapphire_grid_bg() -> np.ndarray:
    """Builds the signature radial-vignetted cyan blueprint grid over #02050A (cached once!)."""
    global _BG_CACHE
    if _BG_CACHE is not None:
        return _BG_CACHE

    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]

    # Elliptical radial vignette centered behind UI stage (540, 820)
    r2 = ((xx - 540.0) / 470.0) ** 2 + ((yy - 820.0) / 690.0) ** 2
    vig = np.exp(-r2 * 1.15)

    # Subtle ambient midnight-sapphire stage glow
    bg = np.zeros((H, W, 3), dtype=np.float32)
    bg[:, :, 0] = 1.5 + 4.5 * vig
    bg[:, :, 1] = 3.5 + 12.5 * vig
    bg[:, :, 2] = 6.5 + 24.0 * vig

    # Crisp 78px square architectural grid lines with anti-aliased 1.5px profile
    cell = 78.0
    gx = np.abs(((xx - 540.0 + cell * 0.5) % cell) - cell * 0.5)
    gy = np.abs(((yy - 820.0 + cell * 0.5) % cell) - cell * 0.5)
    line_mask = np.clip(1.35 - np.minimum(gx, gy), 0.0, 1.0) * vig

    bg[:, :, 0] += line_mask * 12.0
    bg[:, :, 1] += line_mask * 36.0
    bg[:, :, 2] += line_mask * 56.0

    _BG_CACHE = bg
    return _BG_CACHE


# =============================================================================
# CLEAN MINIMALIST SUBTITLE + HARFBUZZ MULTI-TONE COLORED PERSIAN LINES
# =============================================================================
def render_sapphire_subtitle(canvas: Image.Image, t: float, sub_lines: list[dict], font):
    """Understated, zero-jitter RTL feathered subtitle at y = 1515.0 (clears IG Reels UI!)."""
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
    ts_probe = np.array([t - 0.035, t - 0.017, t, t + 0.017, t + 0.035])
    wipe_x = float(np.mean(np.interp(ts_probe, entry["t_knots"], entry["x_knots"])))

    feather = 58.0
    xs = np.arange(entry["tw"], dtype=np.float32)
    mask_1d = np.clip((xs - (wipe_x - feather * 0.5)) / feather, 0.0, 1.0)[None, :, None]

    blended = entry["dim_arr"] * 0.85 * (1.0 - mask_1d) + entry["lit_arr"] * 0.96 * mask_1d
    if line_alpha < 0.998:
        blended[:, :, 3] *= line_alpha

    sub_im = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), mode="RGBA")
    y_glide = (1.0 - ease_out_cubic(fi)) * 3.5
    paste_x = int(round(W / 2.0 - entry["tw"] / 2.0))
    paste_y = int(round(SAPPHIRE_SUB_Y - entry["baseline_offset"] + y_glide))
    canvas.alpha_composite(sub_im, (paste_x, paste_y))


_MTONE_CACHE = {}

def get_multitone_persian_sprite(
    full_text: str,
    highlights: list[tuple[str, tuple[int, int, int]]],
    font,
    max_width: float = 900.0,
    base_rgb: tuple[int, int, int] = (246, 250, 255),
) -> tuple[Image.Image, Image.Image]:
    """
    Renders a single HarfBuzz-shaped RTL Persian line where specific words/phrases
    light up in Electric Cyan (#45CAFF), Crimson Red (#FF474D), or Emerald Green (#52FF85)!
    Returns (sharp_rgba, emissive_rgba) with 0.00px kerning/ligature shift!
    """
    txt_fa = fa(full_text)
    hl_fa = tuple((fa(w), col) for w, col in highlights)
    key = (txt_fa, hl_fa, id(font), int(max_width), base_rgb)
    if key in _MTONE_CACHE:
        return _MTONE_CACHE[key]
    if len(_MTONE_CACHE) > 80:
        _MTONE_CACHE.clear()

    use_font = fit_font_to_width(txt_fa, font, max_width, min_px=20)
    ascent, descent = use_font.getmetrics()
    dummy = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dummy)
    bbox = dd.textbbox((0, 0), txt_fa, font=use_font, direction="rtl", language="fa")
    pad_x, pad_y = 32, 24
    txt_w = max(1, bbox[2] - bbox[0])
    tw = txt_w + pad_x * 2
    th = max(1, ascent + descent + pad_y * 2)
    ox = pad_x - bbox[0]
    oy = pad_y

    # Render sharp white/base mask once with full HarfBuzz RTL shaping
    mask_im = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask_im).text((ox, oy), txt_fa, font=use_font, fill=255, direction="rtl", language="fa")
    mask_f = np.asarray(mask_im, dtype=np.float32) * (1.0 / 255.0)

    # Color map across horizontal X coordinates using exact RTL prefix word widths!
    col_x = np.tile(np.array(base_rgb, dtype=np.float32), (tw, 1))
    em_x = np.zeros((tw, 3), dtype=np.float32)

    x_right = float(pad_x + txt_w)
    words = txt_fa.split()
    # Map each word index [x_w0 .. x_w1] in RTL order
    word_spans = []
    for k in range(len(words)):
        w_prev = dd.textlength(" ".join(words[:k]), font=use_font, direction="rtl", language="fa") if k > 0 else 0.0
        w_cur = dd.textlength(" ".join(words[:k + 1]), font=use_font, direction="rtl", language="fa")
        xa = int(max(0, math.floor(x_right - w_cur - 6)))
        xb = int(min(tw, math.ceil(x_right - w_prev + 6)))
        word_spans.append((words[k], xa, xb))

    for sub_phrase, rgb_c in hl_fa:
        sub_toks = sub_phrase.split()
        m = len(sub_toks)
        if m == 0:
            continue
        for i in range(len(words) - m + 1):
            if words[i:i + m] == sub_toks:
                xa = word_spans[i + m - 1][1]
                xb = word_spans[i][2]
                # Soft 6px feather at word boundaries
                for xx in range(xa, xb):
                    col_x[xx] = rgb_c
                    em_x[xx] = np.array(rgb_c, dtype=np.float32) * 0.42

    sharp_arr = np.zeros((th, tw, 4), dtype=np.uint8)
    for c_i in range(3):
        sharp_arr[:, :, c_i] = np.clip(col_x[None, :, c_i], 0, 255).astype(np.uint8)
    sharp_arr[:, :, 3] = np.clip(mask_f * 255.0, 0, 255).astype(np.uint8)

    em_arr = np.zeros((th, tw, 4), dtype=np.uint8)
    for c_i in range(3):
        em_arr[:, :, c_i] = np.clip(em_x[None, :, c_i] * mask_f, 0, 255).astype(np.uint8)
    em_arr[:, :, 3] = np.clip((em_x.max(axis=1)[None, :] > 1.0) * mask_f * 255.0, 0, 255).astype(np.uint8)

    res = (Image.fromarray(sharp_arr, mode="RGBA"), Image.fromarray(em_arr, mode="RGBA"))
    _MTONE_CACHE[key] = res
    return res


# =============================================================================
# FULL-RGB 32-BIT FLOAT SAPPHIRE + ANAMORPHIC BLOOM COMPOSITOR
# =============================================================================
def composite_sapphire_frame(
    surf_base,
    surf_emissive,
    sharp_texts: list,
    emissive_texts: list,
    fonts: FontBank,
    t: float,
    sub_lines: list[dict],
    grid_strength: float = 1.0,
) -> bytes:
    """
    Composites:
      1. Vignetted Cyan Blueprint Grid (#02050A + subtle slate-cyan grid)
      2. Base Glass / 3D Shaded Layer (surf_base, alpha-over)
      3. Multi-Octave 32-Bit Float RGB Optical Bloom + Horizontal Anamorphic Flare (surf_emissive)
      4. Crisp Typography + Minimalist y=1515 Subtitle + Filmic Anti-Banding Micro-Dither
    """
    bg = get_sapphire_grid_bg() * float(grid_strength)

    # Extract Cairo BGRA -> premultiplied float32 RGB + Alpha
    b_buf = np.frombuffer(surf_base.get_data(), dtype=np.uint8).reshape((H, W, 4))
    b_rgb = b_buf[:, :, [2, 1, 0]].astype(np.float32)
    b_a = b_buf[:, :, 3:4].astype(np.float32) * (1.0 / 255.0)

    # Alpha-over base glass & 3D shaded objects onto grid background
    comp = bg * (1.0 - b_a) + b_rgb

    # Extract emissive layer + pre-paste emissive colored text highlights
    e_buf = np.frombuffer(surf_emissive.get_data(), dtype=np.uint8).reshape((H, W, 4))
    e_rgb_u8 = e_buf[:, :, [2, 1, 0]].copy()
    if emissive_texts:
        em_im = Image.fromarray(e_rgb_u8, mode="RGB").convert("RGBA")
        for sp_em, cx, cy, al in emissive_texts:
            paste_center(em_im, sp_em, cx, cy, al)
        e_rgb_u8 = np.asarray(em_im.convert("RGB"), dtype=np.uint8)

    em_im_rgb = Image.fromarray(e_rgb_u8, mode="RGB")
    h2, w2 = H // 2, W // 2
    h4, w4 = H // 4, W // 4
    h8, w8 = H // 8, W // 8

    # Octave 1 (half-res) + Octave 2/3 & Horizontal Anamorphic Streak -> combined at half-res (3X faster!)
    im_h = em_im_rgb.resize((w2, h2), Image.Resampling.BILINEAR)
    o1_h = np.asarray(im_h.filter(ImageFilter.GaussianBlur(radius=2.0)), dtype=np.float32) * (1.0 / 255.0)

    a_qtr = np.asarray(im_h.resize((w4, h4), Image.Resampling.BILINEAR), dtype=np.float32) * (1.0 / 255.0)
    o2_q = gaussian_filter(a_qtr, sigma=(4.4, 4.4, 0.0))

    a_8 = np.asarray(im_h.resize((w8, h8), Image.Resampling.BILINEAR), dtype=np.float32) * (1.0 / 255.0)
    o3_8 = gaussian_filter(a_8, sigma=(7.2, 7.2, 0.0))
    # Signature Horizontal Anamorphic Cinema Flare on intense laser highlights!
    flare_src = np.maximum(0.0, a_8 - 0.24) * 1.40
    o_anam_8 = gaussian_filter(flare_src, sigma=(1.1, 10.5, 0.0))

    comb_8_srgb = np.sqrt(np.clip((o3_8 * 0.92 + o_anam_8 * 1.15) * 0.25, 0.0, 1.0)) * 255.0
    comb_q_im = Image.fromarray(comb_8_srgb.astype(np.uint8), mode="RGB").resize((w4, h4), Image.Resampling.BILINEAR)
    comb_q_f = np.asarray(comb_q_im, dtype=np.float32) * (2.0 / 255.0)
    wide_q = o2_q * 0.62 + comb_q_f * comb_q_f

    wide_q_srgb = np.sqrt(np.clip(wide_q * 0.25, 0.0, 1.0)) * 255.0
    wide_h_im = Image.fromarray(wide_q_srgb.astype(np.uint8), mode="RGB").resize((w2, h2), Image.Resampling.BILINEAR)
    wide_h_srgb = np.asarray(wide_h_im, dtype=np.float32) * (2.0 / 255.0)
    wide_h = wide_h_srgb * wide_h_srgb

    # Soft-knee RGB optical glow computed at half-res (540x960) -> single SIMD upsample to 1080x1920!
    glow_lin_h = o1_h * 1.10 + wide_h * 1.22
    glow_knee_h = glow_lin_h / (1.0 + glow_lin_h * 0.98)
    glow_srgb_h_u8 = np.clip(np.sqrt(np.clip(glow_knee_h, 0.0, 1.0)) * (0.90 * 255.0), 0.0, 255.0).astype(np.uint8)
    glow_srgb = np.asarray(Image.fromarray(glow_srgb_h_u8, mode="RGB").resize((W, H), Image.Resampling.BILINEAR), dtype=np.float32) * (1.0 / 255.0)

    e0 = e_rgb_u8.astype(np.float32) * (1.0 / 255.0)
    em_total = 1.0 - (1.0 - np.clip(e0, 0.0, 1.0)) * (1.0 - glow_srgb)

    # Optical screen blend emissive light over frosted glass scene!
    comp_norm = np.clip(comp * (1.0 / 255.0), 0.0, 1.0)
    out_f = (1.0 - (1.0 - comp_norm) * (1.0 - em_total)) * 255.0 + _DITHER
    out_u8 = np.clip(out_f, 0.0, 255.0).astype(np.uint8)

    if not sharp_texts and not sub_lines:
        return out_u8.tobytes()

    canvas = Image.fromarray(out_u8, mode="RGB").convert("RGBA")
    for sp, cx, cy, al in sharp_texts:
        paste_center(canvas, sp, cx, cy, al)

    sub_font = getattr(fonts, "med_36", fonts.sub_40)
    render_sapphire_subtitle(canvas, t, sub_lines, sub_font)
    return canvas.convert("RGB").tobytes()


# =============================================================================
# SIGNATURE GLASSMORPHIC UI PRIMITIVES WITH TRAVELLING LASER CORNERS
# =============================================================================
def draw_laser_glass_card(
    cb, ce, x: float, y: float, w: float, h: float, r: float = 18.0,
    alpha: float = 1.0, accent_rgb=C_CYAN_MID, core_rgb=C_CYAN_CORE,
    laser_phase: float = 0.18, dual_laser: bool = True, fill_alpha: float = 0.88
):
    """
    Signature frosted charcoal-glass card with subtle top-left inner sheen
    + travelling glowing Saber laser highlights along corners/edges!
    """
    if alpha <= 0.01 or w <= 2 or h <= 2:
        return

    # 1. Frosted dark-obsidian glass body + top-left inner specular gradient on cb
    cb.save()
    rounded_rect_path(cb, x, y, w, h, r)
    grad = cairo.LinearGradient(x, y, x + w * 0.4, y + h)
    grad.add_color_stop_rgba(0.0, 0.075, 0.115, 0.175, alpha * fill_alpha)
    grad.add_color_stop_rgba(0.35, C_GLASS_BG[0], C_GLASS_BG[1], C_GLASS_BG[2], alpha * fill_alpha)
    grad.add_color_stop_rgba(1.0, 0.024, 0.036, 0.058, alpha * (fill_alpha * 1.04))
    cb.set_source(grad)
    cb.fill_preserve()

    # Subtle 1.6px slate-cyan rim around full perimeter
    cb.set_source_rgba(accent_rgb[0], accent_rgb[1], accent_rgb[2], alpha * 0.34)
    cb.set_line_width(1.7)
    cb.stroke()
    cb.restore()

    # 2. Travelling intense Saber laser segments on BOTH cb and ce!
    perim = 2.0 * (w + h) - 8.0 * r + 2.0 * math.pi * r
    seg = perim * 0.21
    offsets = [laser_phase % 1.0]
    if dual_laser:
        offsets.append((laser_phase + 0.5) % 1.0)

    for off in offsets:
        for ctx_t, col, lw, al_m in (
            (ce, accent_rgb, 5.2, 0.92),
            (ce, core_rgb,   2.6, 0.98),
            (cb, (1.0, 1.0, 1.0), 2.0, 0.95),
        ):
            ctx_t.save()
            ctx_t.set_line_cap(cairo.LINE_CAP_ROUND)
            rounded_rect_path(ctx_t, x, y, w, h, r)
            ctx_t.set_dash([seg, perim * 2.0], -off * perim)
            ctx_t.set_source_rgba(col[0], col[1], col[2], alpha * al_m)
            ctx_t.set_line_width(lw)
            ctx_t.stroke()
            ctx_t.restore()


def draw_glass_status_medallion(cb, ce, cx: float, cy: float, r: float, is_check: bool = True, alpha: float = 1.0, pop_p: float = 1.0):
    """3D Glowing Glass Circular Checkmark (Emerald Green) or Cross (Crimson Red) — exact t=8.80s!"""
    if alpha <= 0.01 or pop_p <= 0.01:
        return
    col = C_GREEN if is_check else C_RED
    rr = r * pop_p

    # Dark tinted 3D glass sphere base
    cb.save()
    rg = cairo.RadialGradient(cx - rr * 0.3, cy - rr * 0.3, rr * 0.1, cx, cy, rr)
    rg.add_color_stop_rgba(0.0, col[0] * 0.28, col[1] * 0.28, col[2] * 0.28, alpha * 0.90)
    rg.add_color_stop_rgba(0.75, col[0] * 0.10, col[1] * 0.10, col[2] * 0.10, alpha * 0.92)
    rg.add_color_stop_rgba(1.0, col[0] * 0.45, col[1] * 0.45, col[2] * 0.45, alpha * 0.95)
    cb.arc(cx, cy, rr, 0, 2 * math.pi)
    cb.set_source(rg)
    cb.fill_preserve()
    cb.set_source_rgba(col[0], col[1], col[2], alpha * 0.65)
    cb.set_line_width(2.4)
    cb.stroke()
    cb.restore()

    # Outer ring + beveled 3D icon on ce & cb
    for ctx_t, lw, al_m, bright in ((ce, 4.4, 0.95, col), (cb, 2.8, 0.98, (0.85 + 0.15*col[0], 0.85 + 0.15*col[1], 0.85 + 0.15*col[2]))):
        ctx_t.save()
        ctx_t.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx_t.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx_t.arc(cx, cy, rr, 0, 2 * math.pi)
        ctx_t.set_source_rgba(col[0], col[1], col[2], alpha * 0.45)
        ctx_t.set_line_width(2.0)
        ctx_t.stroke()

        s = rr * 0.46
        if is_check:
            ctx_t.move_to(cx - s * 0.72, cy + s * 0.02)
            ctx_t.line_to(cx - s * 0.15, cy + s * 0.65)
            ctx_t.line_to(cx + s * 0.78, cy - s * 0.62)
        else:
            ctx_t.move_to(cx - s * 0.62, cy - s * 0.62); ctx_t.line_to(cx + s * 0.62, cy + s * 0.62)
            ctx_t.move_to(cx + s * 0.62, cy - s * 0.62); ctx_t.line_to(cx - s * 0.62, cy + s * 0.62)
        ctx_t.set_source_rgba(bright[0], bright[1], bright[2], alpha * al_m)
        ctx_t.set_line_width(lw * 1.45)
        ctx_t.stroke()
        ctx_t.restore()


def draw_cyan_sphere_check(cb, ce, cx: float, cy: float, r: float = 20.0, alpha: float = 1.0):
    """Glossy 3D sky-blue sphere checkmark icon inside checklist rows (exact t=17.50s!)."""
    if alpha <= 0.01:
        return
    cb.save()
    rg = cairo.RadialGradient(cx - r * 0.35, cy - r * 0.35, r * 0.1, cx, cy, r)
    rg.add_color_stop_rgba(0.0, 0.78, 0.96, 1.0, alpha * 0.98)
    rg.add_color_stop_rgba(0.55, 0.18, 0.65, 0.95, alpha * 0.96)
    rg.add_color_stop_rgba(1.0, 0.06, 0.32, 0.64, alpha * 0.98)
    cb.arc(cx, cy, r, 0, 2 * math.pi)
    cb.set_source(rg); cb.fill()
    # Crisp white check inside sphere
    cb.set_line_cap(cairo.LINE_CAP_ROUND); cb.set_line_join(cairo.LINE_JOIN_ROUND)
    cb.move_to(cx - r * 0.38, cy + r * 0.02)
    cb.line_to(cx - r * 0.08, cy + r * 0.32)
    cb.line_to(cx + r * 0.42, cy - r * 0.28)
    cb.set_source_rgba(1, 1, 1, alpha * 0.98)
    cb.set_line_width(r * 0.22); cb.stroke()
    cb.restore()

    ce.save()
    ce.arc(cx, cy, r * 0.92, 0, 2 * math.pi)
    ce.set_source_rgba(C_CYAN_MID[0], C_CYAN_MID[1], C_CYAN_MID[2], alpha * 0.55)
    ce.set_line_width(3.0); ce.stroke()
    ce.restore()


def draw_chart_series(cb, ce, x: float, y: float, w: float, h: float, ys_norm: list[float], reveal_p: float = 1.0, col_rgb=(0.88, 0.95, 1.0), glow_rgb=C_CYAN_MID, alpha: float = 1.0, fill_under: bool = True):
    """Draws a crisp animated market/equity line series inside (x, y, w, h) with optional gradient fill."""
    n = len(ys_norm)
    if alpha <= 0.01 or n < 2 or reveal_p <= 0.01:
        return
    max_idx = max(1, int(round((n - 1) * clamp(reveal_p))))
    pts = []
    for i in range(max_idx + 1):
        px = x + (i / (n - 1)) * w
        py = y + h - clamp(ys_norm[i]) * h
        pts.append((px, py))

    if fill_under and len(pts) >= 2:
        cb.save()
        cb.new_path()
        cb.move_to(pts[0][0], y + h)
        for px, py in pts:
            cb.line_to(px, py)
        cb.line_to(pts[-1][0], y + h)
        cb.close_path()
        fg = cairo.LinearGradient(x, y, x, y + h)
        fg.add_color_stop_rgba(0.0, glow_rgb[0], glow_rgb[1], glow_rgb[2], alpha * 0.24)
        fg.add_color_stop_rgba(1.0, glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.0)
        cb.set_source(fg); cb.fill()
        cb.restore()

    for ctx_t, c, lw, al_m in ((ce, glow_rgb, 3.4, 0.72), (cb, col_rgb, 2.3, 0.96)):
        ctx_t.save()
        ctx_t.set_line_cap(cairo.LINE_CAP_ROUND); ctx_t.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx_t.new_path()
        for k, (px, py) in enumerate(pts):
            if k == 0:
                ctx_t.move_to(px, py)
            else:
                ctx_t.line_to(px, py)
        ctx_t.set_source_rgba(c[0], c[1], c[2], alpha * al_m)
        ctx_t.set_line_width(lw); ctx_t.stroke()
        ctx_t.restore()


# =============================================================================
# VOLUMETRIC 3D FRESNEL RIM-LIT SAPPHIRE CHARACTERS (t=2.23s & t=37.13s!)
# =============================================================================
def _draw_fresnel_tube(cb, ce, pts: list[tuple[float, float]], radius: float, alpha: float = 1.0):
    """
    Seamless jointless 3D volumetric tube along polyline `pts` with solid `ce` occlusion!
    Produces smooth rounded elbows/knees with ZERO X-ray joint circles and razor-crisp Fresnel cyan rim!
    """
    if alpha <= 0.01 or len(pts) < 2:
        return

    def _trace(c):
        c.new_path()
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.move_to(pts[0][0], pts[0][1])
        for px, py in pts[1:]:
            c.line_to(px, py)

    # 1. Occlude emissive layer behind solid 3D tube, then stroke ONLY outer silhouette rim on ce!
    ce.save()
    _trace(ce)
    ce.set_operator(cairo.OPERATOR_CLEAR)
    ce.set_line_width(radius * 2.0 + 1.0)
    ce.stroke()

    _trace(ce)
    ce.set_operator(cairo.OPERATOR_OVER)
    ce.set_source_rgba(C_CYAN_MID[0], C_CYAN_MID[1], C_CYAN_MID[2], alpha * 0.90)
    ce.set_line_width(radius * 2.0 + 4.5)
    ce.stroke()

    _trace(ce)
    ce.set_operator(cairo.OPERATOR_CLEAR)
    ce.set_line_width(max(1.0, radius * 2.0 - 4.5))
    ce.stroke()
    ce.restore()

    # 2. Concentric 3D cylindrical concentric tube shading on cb (outer bright rim -> mid sapphire -> deep navy core!)
    bands = [
        (radius * 2.0 + 2.0, (0.64, 0.93, 1.00), 0.96),
        (radius * 2.0 - 3.2, (0.16, 0.56, 0.92), 0.98),
        (radius * 2.0 - 9.0, (0.06, 0.24, 0.50), 0.99),
        (radius * 2.0 - 16.5, (0.025, 0.085, 0.20), 1.00),
        (radius * 2.0 - 25.0, (0.012, 0.042, 0.105), 1.00),
    ]
    cb.save()
    for lw_b, col_b, al_b in bands:
        if lw_b <= 1.0:
            continue
        _trace(cb)
        cb.set_source_rgba(col_b[0], col_b[1], col_b[2], alpha * al_b)
        cb.set_line_width(lw_b)
        cb.stroke()
    cb.restore()


def _draw_fresnel_capsule(cb, ce, x0: float, y0: float, x1: float, y1: float, radius: float, alpha: float = 1.0):
    _draw_fresnel_tube(cb, ce, [(x0, y0), (x1, y1)], radius, alpha)


def _draw_fresnel_sphere_head(cb, ce, cx: float, cy: float, r: float, alpha: float = 1.0, light_dx: float = -0.32):
    """Solid 3D sphere head that occludes background rims + razor-bright electric-cyan Fresnel rim!"""
    ce.save()
    ce.set_operator(cairo.OPERATOR_CLEAR)
    ce.arc(cx, cy, r - 1.5, 0, 2 * math.pi)
    ce.fill()
    ce.set_operator(cairo.OPERATOR_OVER)
    ce.arc(cx, cy, r, 0, 2 * math.pi)
    ce.set_source_rgba(C_CYAN_MID[0], C_CYAN_MID[1], C_CYAN_MID[2], alpha * 0.92)
    ce.set_line_width(5.2)
    ce.stroke()
    ce.restore()

    cb.save()
    cb.arc(cx, cy, r, 0, 2 * math.pi)
    rg = cairo.RadialGradient(cx - light_dx * r * 0.5, cy + r * 0.15, r * 0.12, cx, cy, r)
    rg.add_color_stop_rgba(0.0, 0.015, 0.045, 0.11, alpha * 1.00)
    rg.add_color_stop_rgba(0.62, 0.035, 0.12, 0.28, alpha * 1.00)
    rg.add_color_stop_rgba(0.88, 0.12, 0.46, 0.86, alpha * 1.00)
    rg.add_color_stop_rgba(1.0, 0.62, 0.93, 1.00, alpha * 0.99)
    cb.set_source(rg)
    cb.fill_preserve()
    cb.set_source_rgba(C_CYAN_CORE[0], C_CYAN_CORE[1], C_CYAN_CORE[2], alpha * 0.96)
    cb.set_line_width(3.4)
    cb.stroke()
    cb.restore()


def draw_sapphire_desk_scene_side(cb, ce, t: float, alpha: float = 1.0, q_pop: float = 1.0):
    """
    Exact Scene 01 Hero (modeled on ref t=2.23s!):
    - Blurred sapphire bokeh trading charts in background
    - Glossy dark floor with glowing blue mirror reflections
    - Sleek desk + glowing cyan monitor + small potted plant
    - Volumetric 3D Fresnel Rim-Lit Character sitting in chair, scratching head with glowing '???' above!
    """
    if alpha <= 0.01:
        return

    # 1. Background ambient bokeh wall charts (drawn softly onto ce so bloom blurs them into bokeh!)
    ce.save()
    # Left candlestick bars
    for k in range(8):
        bx = 42 + k * 28
        bh = 35 + 24 * math.sin(k * 1.4 + 0.5)
        by = 650 - k * 14
        ce.move_to(bx, by - bh * 0.7); ce.line_to(bx, by + bh * 0.7)
        ce.set_source_rgba(0.10, 0.52, 0.88, alpha * 0.35); ce.set_line_width(2.5); ce.stroke()
        ce.rectangle(bx - 6, by - bh * 0.38, 12, bh * 0.76)
        ce.set_source_rgba(0.14, 0.65, 0.98, alpha * 0.42); ce.fill()
    # Right ambient monitor dashboard panel
    rounded_rect_path(ce, 815, 515, 235, 250, 14)
    ce.set_source_rgba(0.08, 0.36, 0.72, alpha * 0.25); ce.set_line_width(3.5); ce.stroke()
    ce.move_to(830, 705)
    for k in range(12):
        ce.line_to(830 + k * 19, 705 - k * 5 - math.sin(k * 1.3 + t * 2.0) * 14)
    ce.set_source_rgba(0.22, 0.76, 1.0, alpha * 0.55); ce.set_line_width(4.5); ce.stroke()
    ce.restore()

    floor_y = 1155.0
    desk_y = 905.0

    # 2. Glossy Blue Floor Reflection Pools (exact t=2.23s polished dark floor!)
    ce.save()
    for rx, rw, ri in ((320, 180, 0.48), (585, 220, 0.65), (760, 130, 0.35)):
        rg = cairo.RadialGradient(rx, floor_y + 55, 8, rx, floor_y + 55, rw)
        rg.add_color_stop_rgba(0.0, 0.14, 0.58, 0.98, alpha * ri)
        rg.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        ce.save()
        ce.translate(rx, floor_y + 55); ce.scale(1.0, 0.38); ce.translate(-rx, -(floor_y + 55))
        ce.arc(rx, floor_y + 55, rw, 0, 2 * math.pi)
        ce.set_source(rg); ce.fill()
        ce.restore()
    ce.restore()

    # 3. Desk + Glowing Rim-Lit Monitor + Small Plant on Left
    for ctx_t, col, lw in ((ce, C_CYAN_MID, 4.2), (cb, (0.55, 0.85, 1.0), 2.6)):
        ctx_t.save()
        # Desk tabletop & angled legs
        rounded_rect_path(ctx_t, 125, desk_y, 505, 18, 6)
        ctx_t.set_source_rgba(col[0], col[1], col[2], alpha * 0.85); ctx_t.set_line_width(lw); ctx_t.stroke()
        for lx0, lx1 in ((185, 145), (235, 195), (545, 575)):
            ctx_t.move_to(lx0, desk_y + 18); ctx_t.line_to(lx1, floor_y); ctx_t.stroke()
        ctx_t.restore()

    # Monitor screen (245..515, 680..872)
    draw_laser_glass_card(cb, ce, 245, 678, 272, 194, 14, alpha, C_CYAN_MID, C_CYAN_CORE, t * 0.18, True, 0.94)
    # Monitor stand
    cb.save()
    cb.move_to(365, 872); cb.line_to(355, desk_y); cb.line_to(408, desk_y); cb.line_to(398, 872)
    cb.set_source_rgba(0.35, 0.72, 0.98, alpha * 0.85); cb.set_line_width(3.0); cb.stroke()
    cb.restore()
    # Live jagged loss chart inside monitor
    ys_m = [0.68, 0.72, 0.65, 0.74, 0.62, 0.54, 0.58, 0.42, 0.46, 0.28, 0.22]
    draw_chart_series(cb, ce, 268, 715, 224, 122, ys_m, clamp(t / 0.9), (0.85, 0.95, 1.0), C_CYAN_MID, alpha, True)

    # Small minimal potted plant on left edge of desk (155, desk_y)
    cb.save()
    cb.move_to(146, desk_y); cb.line_to(138, desk_y - 42); cb.line_to(182, desk_y - 42); cb.line_to(174, desk_y); cb.close_path()
    cb.set_source_rgba(0.28, 0.65, 0.92, alpha * 0.75); cb.set_line_width(2.4); cb.stroke()
    for ang_l in (-0.5, -0.15, 0.2, 0.52):
        cb.move_to(160, desk_y - 42)
        cb.curve_to(160 + math.sin(ang_l) * 24, desk_y - 72, 160 + math.sin(ang_l) * 34, desk_y - 88, 160 + math.sin(ang_l) * 18, desk_y - 98)
        cb.stroke()
    cb.restore()

    # 4. Sleek Modern Chair on Right (behind & under character)
    for ctx_t, col, lw in ((ce, C_CYAN_MID, 4.0), (cb, (0.52, 0.84, 1.0), 2.5)):
        ctx_t.save()
        # Chair legs
        for cx0, cx1 in ((665, 635), (710, 695), (765, 785), (805, 835)):
            ctx_t.move_to(cx0, 1005); ctx_t.line_to(cx1, floor_y)
            ctx_t.set_source_rgba(col[0], col[1], col[2], alpha * 0.78); ctx_t.set_line_width(lw); ctx_t.stroke()
        # Curved seat + backrest shell
        ctx_t.move_to(625, 998)
        ctx_t.curve_to(715, 1008, 795, 1005, 818, 975)
        ctx_t.curve_to(842, 935, 858, 845, 852, 815)
        ctx_t.curve_to(835, 812, 808, 825, 795, 945)
        ctx_t.stroke()
        ctx_t.restore()

    # 5. Volumetric 3D Fresnel Rim-Lit Character sitting at desk, scratching head (jointless 3D tubes!)
    bob = math.sin(t * 2.8) * 3.5
    scratch = math.sin(t * 6.5) * 4.5
    # Back leg + shoe (single jointless 3D polyline!)
    _draw_fresnel_tube(cb, ce, [(718, 972), (606, 982), (566, 1122), (532, 1124)], 22, alpha * 0.86)
    # Front leg + shoe (single jointless 3D polyline!)
    _draw_fresnel_tube(cb, ce, [(744, 976), (634, 992), (598, 1134), (558, 1136)], 24, alpha)
    # Left arm resting toward desk mouse/keyboard
    _draw_fresnel_tube(cb, ce, [(698, 822 + bob), (622, 886), (554, 888)], 17, alpha * 0.88)
    # Torso leaning slightly forward in thought
    _draw_fresnel_tube(cb, ce, [(748, 962), (716, 808 + bob)], 44, alpha)
    # Sphere 3D Head
    hx, hy = 696, 712 + bob
    _draw_fresnel_sphere_head(cb, ce, hx, hy, 58, alpha, light_dx=-0.4)
    # Right arm raised with elbow bent, hand scratching side/top of head (single jointless 3D tube!)
    _draw_fresnel_tube(cb, ce, [(712, 824 + bob), (610, 842 + bob), (642, 726 + bob + scratch)], 18, alpha)

    # 6. Three Glowing Neon '???' Floating Above Head (exact t=2.23s!)
    if q_pop > 0.02:
        q_specs = [(628, 608, -0.32, 0.88), (694, 576, 0.02, 1.08), (764, 602, 0.34, 0.92)]
        for qi, (qx, qy, qang, qsc) in enumerate(q_specs):
            qu = ease_out_cubic(clamp(q_pop * 1.35 - qi * 0.18))
            if qu <= 0.02:
                continue
            qy_b = qy + math.sin(t * 4.2 + qi * 1.6) * 5.5
            for ctx_t, col, lw in ((ce, C_CYAN_MID, 11.0), (ce, C_CYAN_CORE, 5.5), (cb, (0.92, 0.99, 1.0), 4.2)):
                ctx_t.save()
                ctx_t.translate(qx, qy_b)
                ctx_t.rotate(qang)
                ctx_t.scale(qsc * qu, qsc * qu)
                ctx_t.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx_t.new_path()
                ctx.arc if False else None
                ctx_t.arc(0, -18, 16, math.pi * 1.12, math.pi * 0.22)
                ctx_t.curve_to(12, -2, 0, 2, 0, 14)
                ctx_t.set_source_rgba(col[0], col[1], col[2], alpha * 0.96)
                ctx_t.set_line_width(lw); ctx_t.stroke()
                ctx_t.arc(0, 30, lw * 0.65, 0, 2 * math.pi); ctx_t.fill()
                ctx_t.restore()


def draw_sapphire_thinking_character_front(cb, ce, cx: float, cy: float, t: float, alpha: float = 1.0):
    """
    Exact Scene 07 Hero (modeled on ref t=37.13s!):
    Front-facing 3D Fresnel Rim-Lit Blue Character with 2 glowing white dot-eyes,
    hand on chin holding a pen, sleek dark-metallic laptop with glowing dot logo, and coffee mug on desk!
    """
    if alpha <= 0.01:
        return
    bob = math.sin(t * 2.4) * 3.0
    desk_y = cy + 165

    # Torso & shoulders behind laptop
    _draw_fresnel_tube(cb, ce, [(cx - 24, cy + 56 + bob), (cx + 24, cy + 56 + bob)], 52, alpha)
    _draw_fresnel_tube(cb, ce, [(cx, cy + 52 + bob), (cx, cy + 148)], 58, alpha)
    # Right arm resting toward laptop
    _draw_fresnel_tube(cb, ce, [(cx + 52, cy + 54 + bob), (cx + 96, cy + 134)], 21, alpha * 0.94)

    # 3D Sphere Head + 2 Expressive Glowing White Dot-Eyes (blinking smoothly!)
    hx, hy = cx - 4, cy - 58 + bob
    _draw_fresnel_sphere_head(cb, ce, hx, hy, 64, alpha, light_dx=0.0)

    blink = 1.0 - 0.88 * math.exp(-(((t % 3.6) - 1.8) / 0.09) ** 2)
    for ex_off in (-16, 14):
        for ctx_t, r_e in ((ce, 6.2), (cb, 4.6)):
            ctx_t.save()
            ctx_t.translate(hx + ex_off, hy - 6)
            ctx_t.scale(1.0, max(0.15, blink))
            ctx_t.arc(0, 0, r_e, 0, 2 * math.pi)
            ctx_t.set_source_rgba(1, 1, 1, alpha * 0.98)
            ctx_t.fill()
            ctx_t.restore()

    # Left arm bent up in classic thinking pose (hand on chin — single jointless 3D tube in front!)
    _draw_fresnel_tube(cb, ce, [(cx - 56, cy + 58 + bob), (cx - 94, cy + 124), (cx - 18, cy + 6 + bob)], 19, alpha)
    cb.save()
    cb.move_to(cx - 34, cy - 8 + bob); cb.line_to(cx + 8, cy + 16 + bob)
    cb.set_source_rgba(0.70, 0.92, 1.0, alpha * 0.95); cb.set_line_width(3.6); cb.stroke()
    cb.restore()

    # Occlude ce behind Desk + Laptop + Mug so foreground props are 100% solid opaque!
    ce.save()
    ce.set_operator(cairo.OPERATOR_CLEAR)
    ce.rectangle(cx - 290, desk_y, 580, 95); ce.fill()
    ce.new_path()
    ce.move_to(cx - 55, desk_y - 96); ce.line_to(cx + 128, desk_y - 96)
    ce.line_to(cx + 108, desk_y + 8); ce.line_to(cx - 75, desk_y + 8); ce.close_path(); ce.fill()
    rounded_rect_path(ce, cx - 198, desk_y - 52, 52, 58, 7); ce.fill()
    ce.restore()

    # Sleek Dark Desk Surface + Coffee Mug on Left + Laptop in Front!
    cb.save()
    lg_d = cairo.LinearGradient(cx - 280, desk_y - 10, cx - 280, desk_y + 90)
    lg_d.add_color_stop_rgba(0.0, 0.05, 0.11, 0.20, alpha * 0.95)
    lg_d.add_color_stop_rgba(1.0, 0.01, 0.02, 0.04, alpha * 0.98)
    cb.rectangle(cx - 290, desk_y, 580, 95)
    cb.set_source(lg_d); cb.fill()
    cb.restore()

    # Laptop lid (tilted trapezoid) + glowing emblem dot
    cb.save()
    cb.new_path()
    cb.move_to(cx - 55, desk_y - 96)
    cb.line_to(cx + 128, desk_y - 96)
    cb.line_to(cx + 108, desk_y + 8)
    cb.line_to(cx - 75, desk_y + 8)
    cb.close_path()
    lg_l = cairo.LinearGradient(cx - 60, desk_y - 96, cx + 120, desk_y + 8)
    lg_l.add_color_stop_rgba(0.0, 0.12, 0.24, 0.40, alpha * 0.98)
    lg_l.add_color_stop_rgba(1.0, 0.04, 0.08, 0.15, alpha * 0.99)
    cb.set_source(lg_l); cb.fill_preserve()
    cb.set_source_rgba(0.38, 0.78, 1.0, alpha * 0.72); cb.set_line_width(2.2); cb.stroke()
    # Base keyboard lip
    rounded_rect_path(cb, cx - 102, desk_y + 4, 212, 10, 4)
    cb.set_source_rgba(0.20, 0.45, 0.72, alpha * 0.88); cb.fill()
    # Glowing emblem on laptop back
    cb.arc(cx + 28, desk_y - 44, 7.5, 0, 2 * math.pi)
    cb.set_source_rgba(0.55, 0.88, 1.0, alpha * 0.85); cb.fill()
    cb.restore()

    # Dark Ceramic Coffee Mug on Left (cx - 178, desk_y - 54)
    cb.save()
    rounded_rect_path(cb, cx - 198, desk_y - 52, 52, 58, 7)
    lg_m = cairo.LinearGradient(cx - 198, desk_y - 52, cx - 146, desk_y - 52)
    lg_m.add_color_stop_rgba(0.0, 0.16, 0.34, 0.56, alpha * 0.96)
    lg_m.add_color_stop_rgba(0.5, 0.04, 0.09, 0.18, alpha * 0.98)
    lg_m.add_color_stop_rgba(1.0, 0.10, 0.24, 0.42, alpha * 0.96)
    cb.set_source(lg_m); cb.fill_preserve()
    cb.set_source_rgba(0.35, 0.72, 0.98, alpha * 0.55); cb.set_line_width(1.8); cb.stroke()
    # Mug handle
    cb.arc(cx - 198, desk_y - 23, 15, math.pi * 0.5, math.pi * 1.5)
    cb.set_line_width(4.2); cb.stroke()
    cb.restore()


def draw_speedometer_gauge_card(
    cb, ce, x: float, y: float, size: float,
    needle_p: float, active_cyan: bool, alpha: float = 1.0, laser_phase: float = 0.2
):
    """
    Square frosted-glass gauge card (exact ref t=45.83s!):
    - Left gauge (active_cyan=False): muted dark slate dial with erratic uncontrolled needle
    - Right gauge (active_cyan=True): glowing electric-cyan arc + crisp white needle!
    """
    if alpha <= 0.01:
        return
    draw_laser_glass_card(
        cb, ce, x, y, size, size, 22, alpha,
        C_CYAN_MID if active_cyan else (0.18, 0.36, 0.54),
        C_CYAN_CORE if active_cyan else (0.45, 0.70, 0.90),
        laser_phase, dual_laser=active_cyan, fill_alpha=0.90
    )

    cx = x + size * 0.5
    cy = y + size * 0.58
    r = size * 0.33
    ang_start = math.pi * 0.82
    ang_span = math.pi * 1.36
    ang_cur = ang_start + clamp(needle_p) * ang_span

    # Background dial track
    cb.save()
    cb.set_line_cap(cairo.LINE_CAP_ROUND)
    cb.arc(cx, cy, r, ang_start, ang_start + ang_span)
    cb.set_source_rgba(0.16, 0.24, 0.34, alpha * 0.75)
    cb.set_line_width(size * 0.075)
    cb.stroke()
    cb.restore()

    if active_cyan and needle_p > 0.02:
        for ctx_t, col, lw in ((ce, C_CYAN_MID, size * 0.095), (cb, (0.42, 0.84, 1.0), size * 0.072)):
            ctx_t.save()
            ctx_t.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx_t.arc(cx, cy, r, ang_start, ang_cur)
            ctx_t.set_source_rgba(col[0], col[1], col[2], alpha * 0.95)
            ctx_t.set_line_width(lw)
            ctx_t.stroke()
            ctx_t.restore()

    # Crisp tapered needle
    nx = cx + math.cos(ang_cur) * (r * 0.86)
    ny = cy + math.sin(ang_cur) * (r * 0.86)
    bx = cx + math.cos(ang_cur) * (r * 0.18)
    by = cy + math.sin(ang_cur) * (r * 0.18)
    cb.save()
    cb.set_line_cap(cairo.LINE_CAP_ROUND)
    cb.move_to(bx, by); cb.line_to(nx, ny)
    cb.set_source_rgba(0.95, 0.98, 1.0, alpha * (0.98 if active_cyan else 0.65))
    cb.set_line_width(4.8); cb.stroke()
    cb.restore()
