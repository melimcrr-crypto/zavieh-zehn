"""
Studio v5.0 — Deep-Glow Continuous-Camera Motion Graphics Engine
Inspired by high-retention monochrome neon-bloom visual storytelling:
  - 4-Octave Optical Deep-Glow Halation (tight neon core + inner aura + mid mist + wide room halation)
    with filmic anti-banding micro-dither for H.264 8-bit perfection.
  - Foreground Depth-of-Field (DoF) Pass-Through Layer for 6X camera zoom-through transitions.
  - Pure Zero-Clutter Visual Storytelling (vast #000000 canvas, anatomical head/brain profiles,
    blinking spiral eye, volumetric light cones, isometric 3D cubes, Venn diagrams, circuit pulses).
  - Raised Instagram-Safe Minimalist Subtitle (y = 1510.0, 0.00px baseline lock).
"""
import math
import numpy as np
import cairocffi as cairo
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter, zoom

from src.engine.render_core import (
    W, H, FPS, FontBank, clamp, ease_out_cubic, ease_in_out_cubic,
    fa, _get_subtitle_bitmap_pair, paste_center, rounded_rect_path, draw_star4
)

DEEP_GLOW_SUB_Y = 1510.0  # Cleanly above Instagram's @username + Follow + caption UI!


def exp_in_out(x: float) -> float:
    """Snappy After-Effects Graph-Editor S-curve (85% influence) for whip-pans & morphs."""
    x = clamp(x)
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    if x < 0.5:
        return 0.5 * math.pow(2.0, 16.0 * x - 8.0)
    return 1.0 - 0.5 * math.pow(2.0, -16.0 * x + 8.0)


def set_trim_path(ctx, start_p: float, end_p: float, total_len: float = 1200.0):
    """After-Effects 'Trim Paths' equivalent (start_p..end_p along stroke)."""
    s = clamp(start_p)
    e = clamp(end_p)
    if e <= s + 0.001:
        ctx.set_dash([0.0, total_len * 3.0], 0.0)
    elif s <= 0.001 and e >= 0.999:
        ctx.set_dash([])
    else:
        seg = max(0.5, (e - s) * total_len)
        ctx.set_dash([seg, total_len * 3.0], -s * total_len)


def render_clean_deepglow_subtitle(canvas: Image.Image, t: float, sub_lines: list[dict], font):
    """
    Understated, ultra-clean minimalist cinema subtitle at y = 1510.0:
    Zero baseline jitter (0.00px), subtle 56px RTL feathered reveal so eyes stay glued to the center art.
    """
    active_sub = None
    for sub in sub_lines:
        if sub["start"] <= t <= sub["end"]:
            active_sub = sub
            break
    if active_sub is None:
        return

    fi = clamp((t - active_sub["start"]) / 0.20)
    fo = clamp((active_sub["end"] - t) / 0.18)
    line_alpha = ease_out_cubic(min(fi, fo))
    if line_alpha <= 0.01:
        return

    entry = _get_subtitle_bitmap_pair(active_sub, font)
    ts_probe = np.array([t - 0.035, t - 0.017, t, t + 0.017, t + 0.035])
    wipe_x = float(np.mean(np.interp(ts_probe, entry["t_knots"], entry["x_knots"])))

    feather = 56.0
    xs = np.arange(entry["tw"], dtype=np.float32)
    mask_1d = np.clip((xs - (wipe_x - feather * 0.5)) / feather, 0.0, 1.0)[None, :, None]

    # Soft understated dim (38%) -> clean crisp white (94%) matching minimalist reference
    blended = entry["dim_arr"] * 0.85 * (1.0 - mask_1d) + entry["lit_arr"] * 0.95 * mask_1d
    if line_alpha < 0.998:
        blended[:, :, 3] *= line_alpha

    sub_im = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), mode="RGBA")
    y_glide = (1.0 - ease_out_cubic(fi)) * 3.5
    paste_x = int(round(W / 2.0 - entry["tw"] / 2.0))
    paste_y = int(round(DEEP_GLOW_SUB_Y - entry["baseline_offset"] + y_glide))
    canvas.alpha_composite(sub_im, (paste_x, paste_y))


_DITHER_NOISE = np.random.default_rng(2026).uniform(-0.55, 0.55, (H, W, 1)).astype(np.float32)


def composite_deep_glow_frame(
    surf_core,
    text_overlays: list,
    fonts: FontBank,
    t: float,
    sub_lines: list[dict],
    surf_dof=None,
    dof_blur_px: float = 0.0,
    glow_gain: float = 1.0,
) -> bytes:
    """
    True 4-Octave Optical 'Deep Glow' Compositor:
      Octave 1 (r ~  4.5px): Tight electric neon core edge
      Octave 2 (r ~ 18.0px): Creamy inner aura
      Octave 3 (r ~ 56.0px): Atmospheric halo
      Octave 4 (r ~155.0px): Wide room-filling inverse-square halation
    Blended in optical screen space (1 - prod(1 - layer)) + filmic micro-dither.
    """
    buf = np.frombuffer(surf_core.get_data(), dtype=np.uint8).reshape((H, W, 4))
    lum_u8 = np.maximum(buf[:, :, 2], buf[:, :, 1]).copy()
    core_im = Image.fromarray(lum_u8, mode="L")

    # Pre-composite diagram text sprites onto core_im so labels share the exact 4-octave Deep Glow!
    sharp_overlays = []
    if text_overlays:
        core_rgba = Image.merge("RGBA", (core_im, core_im, core_im, Image.new("L", (W, H), 255)))
        has_pre = False
        for item in text_overlays:
            if len(item) == 5 and not item[4]:
                sharp_overlays.append(item[:4])
            else:
                sp, cx, cy, al = item[:4]
                paste_center(core_rgba, sp, cx, cy, al)
                has_pre = True
        if has_pre:
            core_im = core_rgba.convert("L")

    # Pure 32-bit float32 multi-scale Gaussian pyramid (0.000 uint8 truncation steps -> infinite smooth falloff!)
    h2, w2 = H // 2, W // 2
    h4, w4 = H // 4, W // 4

    im_half = core_im.resize((w2, h2), Image.Resampling.BILINEAR)
    o1 = im_half.filter(ImageFilter.GaussianBlur(radius=1.8)).resize((W, H), Image.Resampling.BILINEAR)
    o1_mid = im_half.filter(ImageFilter.GaussianBlur(radius=4.2)).resize((W, H), Image.Resampling.BILINEAR)

    # Quarter-res (270x480) & 1/12-res (90x160) in pure IEEE float32 (min nonzero ~ 1e-10 -> zero outer step rings!)
    a_qtr = np.asarray(im_half.resize((w4, h4), Image.Resampling.BILINEAR), dtype=np.float32) * (1.0 / 255.0)
    a_o2 = gaussian_filter(a_qtr, sigma=5.2)
    a_12 = a_qtr.reshape(H // 12, 3, W // 12, 3).mean(axis=(1, 3))
    a_o3 = gaussian_filter(a_12, sigma=4.8)
    a_o4 = gaussian_filter(a_12, sigma=15.0)

    wide_qtr_lin = a_o2 * 0.36 + zoom(a_o3 * 0.62 + a_o4 * 1.05, 3.0, order=1)
    cw_lin = np.maximum(0.0, zoom(wide_qtr_lin, 4.0, order=1))

    c0 = np.asarray(core_im, dtype=np.float32) * (1.0 / 255.0)
    c1 = np.asarray(o1, dtype=np.float32) * (1.0 / 255.0)
    c1m = np.asarray(o1_mid, dtype=np.float32) * (1.0 / 255.0)

    # Linear photon sum + Reinhard soft-knee prevents whiteout inside dense brain gyri while preserving wide atmospheric halo!
    glow_lin = (c1 * 1.65 + c1m * 0.28 + cw_lin) * float(glow_gain)
    glow_knee = glow_lin / (1.0 + glow_lin * 1.25)
    glow_srgb = np.sqrt(np.clip(glow_knee, 0.0, 1.0)) * 0.92
    lum = (1.0 - (1.0 - np.clip(c0, 0.0, 1.0)) * (1.0 - np.clip(glow_srgb, 0.0, 1.0))) * 255.0

    # Optional Depth-of-Field (DoF) blurred foreground pass-through layer (pure float32!)
    if surf_dof is not None and dof_blur_px > 0.2:
        dbuf = np.frombuffer(surf_dof.get_data(), dtype=np.uint8).reshape((H, W, 4))
        dlum = np.maximum(dbuf[:, :, 2], dbuf[:, :, 1])
        if dlum.max() > 1:
            dq = np.asarray(Image.fromarray(dlum, mode="L").resize((w4, h4), Image.Resampling.BILINEAR), dtype=np.float32) * (1.0 / 255.0)
            dblur_q = gaussian_filter(dq, sigma=max(0.8, dof_blur_px * 0.25))
            da = np.clip(zoom(dblur_q, 4.0, order=1) * 1.35, 0.0, 1.0)
            lum = (1.0 - (1.0 - lum * (1.0 / 255.0)) * (1.0 - da)) * 255.0

    # Subtle micro-dither eliminates 8-bit banding in wide dark glow gradients!
    mask_dither = (lum > 1.2)[:, :, None]
    rgb_f = lum[:, :, None] + _DITHER_NOISE * mask_dither
    rgb_u8 = np.clip(rgb_f, 0.0, 255.0).astype(np.uint8)
    rgb_3 = np.repeat(rgb_u8, 3, axis=2)

    if not sharp_overlays and not sub_lines:
        return rgb_3.tobytes()

    canvas = Image.fromarray(rgb_3, mode="RGB").convert("RGBA")
    for sp, cx, cy, al in sharp_overlays:
        paste_center(canvas, sp, cx, cy, al)

    sub_font = getattr(fonts, "med_36", fonts.sub_40)
    render_clean_deepglow_subtitle(canvas, t, sub_lines, sub_font)
    return canvas.convert("RGB").tobytes()


# =============================================================================
# SIGNATURE ANATOMICAL & ICONIC VECTOR ACTORS (Exact Reference Visual Language)
# =============================================================================
def draw_blinking_spiral_eye(
    ctx, cx: float, cy: float, scale: float = 1.0,
    open_p: float = 1.0, spiral_p: float = 0.0, t: float = 0.0,
    alpha: float = 1.0, trim_p: float = 1.0
):
    """
    Anatomical almond eye with upper/lower lid folds, smooth Bezier blink,
    and stippled iris morphing into a rotating Archimedean hypnotic spiral!
    """
    if alpha <= 0.01 or trim_p <= 0.01:
        return
    op = clamp(open_p)
    rx = 165.0 * scale
    ry_up = 92.0 * scale * (op * 1.18 - 0.18)
    ry_dn = 86.0 * scale * (0.22 + 0.78 * op)

    ctx.save()
    ctx.translate(cx, cy)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # Outer almond eye contour
    ctx.new_path()
    ctx.move_to(-rx, 0)
    ctx.curve_to(-rx * 0.48, -ry_up, rx * 0.48, -ry_up, rx, 0)
    ctx.curve_to(rx * 0.48, ry_dn, -rx * 0.48, ry_dn, -rx, 0)
    set_trim_path(ctx, 0.0, trim_p, rx * 4.6)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.98)
    ctx.set_line_width(5.0)
    ctx.stroke()

    # Upper & lower delicate eyelid crease arcs (signature detail from 0.2s..4.8s!)
    ctx.set_dash([])
    ctx.set_line_width(3.2)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.72 * trim_p)
    crease_up = ry_up + 26.0 * scale
    ctx.move_to(-rx * 0.56, -crease_up * 0.42)
    ctx.curve_to(-rx * 0.22, -crease_up, rx * 0.22, -crease_up, rx * 0.56, -crease_up * 0.42)
    ctx.stroke()

    crease_dn = ry_dn + 22.0 * scale
    ctx.move_to(-rx * 0.42, crease_dn * 0.52)
    ctx.curve_to(-rx * 0.16, crease_dn, rx * 0.16, crease_dn, rx * 0.42, crease_dn * 0.52)
    ctx.stroke()

    # Clip iris & spiral strictly inside the open almond eye!
    if op > 0.06 and trim_p > 0.35:
        ctx.save()
        ctx.new_path()
        ctx.move_to(-rx, 0)
        ctx.curve_to(-rx * 0.48, -ry_up, rx * 0.48, -ry_up, rx, 0)
        ctx.curve_to(rx * 0.48, ry_dn, -rx * 0.48, ry_dn, -rx, 0)
        ctx.clip()

        iris_r = 66.0 * scale
        ctx.arc(0, 0, iris_r, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, alpha * 0.95)
        ctx.set_line_width(4.2)
        ctx.stroke()

        # Stippled glowing pupil fading into spinning Archimedean spiral!
        sp_u = clamp(spiral_p)
        if sp_u < 0.98:
            ctx.arc(0, 0, iris_r * 0.88 * (1.0 - 0.65 * sp_u), 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, alpha * 0.88 * (1.0 - sp_u))
            ctx.fill()

        if sp_u > 0.02:
            ctx.new_path()
            turns = 3.3 * sp_u
            steps = 110
            rot = -t * 3.8
            for si in range(steps + 1):
                u = si / steps
                ang = u * turns * 2.0 * math.pi + rot
                rr = u * (iris_r * 0.86)
                px, py = math.cos(ang) * rr, math.sin(ang) * rr
                if si == 0:
                    ctx.move_to(px, py)
                else:
                    ctx.line_to(px, py)
            ctx.set_source_rgba(1, 1, 1, alpha * 0.96 * clamp(sp_u * 1.4))
            ctx.set_line_width(3.8)
            ctx.stroke()
        ctx.restore()

    ctx.restore()


def draw_anatomical_head_profile(
    ctx, cx: float, cy: float, scale: float = 1.0, facing: int = -1,
    alpha: float = 1.0, trim_p: float = 1.0,
    brain_alpha: float = 1.0, brain_stars: int = 0, t: float = 0.0
):
    """
    Sleek anatomical side-profile human head + intricate cerebral cortex gyri folds!
    facing = -1 faces LEFT (like t=41.42s); facing = +1 faces RIGHT (like left speaker at t=52.7s).
    """
    if alpha <= 0.01 or trim_p <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(-facing * scale, scale)  # Canonical coordinates below face LEFT (+x is back of skull, -x is nose)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # Smooth continuous anatomical side-profile path (modeled directly on reference t=41.42s!)
    ctx.new_path()
    ctx.move_to(58, 175)  # Back base of neck
    ctx.line_to(-52, 175) # Front base of neck
    ctx.curve_to(-50, 145, -48, 128, -56, 118)   # Throat -> under-chin
    ctx.curve_to(-82, 118, -104, 114, -106, 96)  # Chin tip
    ctx.curve_to(-108, 84, -98, 76, -102, 68)    # Lower lip indent
    ctx.curve_to(-110, 62, -108, 54, -99, 50)    # Lower lip
    ctx.curve_to(-110, 46, -110, 38, -100, 33)   # Upper lip
    ctx.curve_to(-102, 24, -104, 18, -124, 12)   # Philtrum -> underside of nose
    ctx.curve_to(-134, 8, -132, -2, -122, -14)   # Nose tip
    ctx.curve_to(-110, -28, -98, -42, -98, -54)  # Nose bridge -> nasion
    ctx.curve_to(-98, -66, -106, -78, -102, -98) # Brow ridge -> forehead
    ctx.curve_to(-94, -148, -42, -186, 22, -184) # Frontal -> parietal dome
    ctx.curve_to(96, -182, 142, -128, 138, -48)  # Crown -> occipital curve
    ctx.curve_to(135, 16, 98, 62, 72, 104)       # Occiput -> nape of neck
    ctx.curve_to(60, 126, 56, 152, 58, 175)      # Down back of neck
    ctx.close_path()

    set_trim_path(ctx, 0.0, trim_p, 1150.0)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.98)
    ctx.set_line_width(4.8 / max(0.55, scale ** 0.35))
    ctx.stroke()

    # Side-profile anatomical almond eye behind nasal bridge (signature detail from t=41.42s & t=60.23s!)
    if trim_p > 0.28:
        ea = alpha * clamp((trim_p - 0.28) / 0.35)
        ctx.set_dash([])
        ctx.set_line_width(2.6 / max(0.6, scale ** 0.35))
        ctx.set_source_rgba(1, 1, 1, ea * 0.90)
        ctx.new_path()
        ctx.move_to(-88, -50)
        ctx.curve_to(-78, -60, -64, -58, -56, -50)
        ctx.curve_to(-65, -42, -79, -43, -88, -50)
        ctx.stroke()
        ctx.arc(-76, -50, 4.2, 0, 2 * math.pi)
        ctx.fill()

    # Intricate Cerebral Cortex Brain Outline + Interconnected Organic Gyri Loops + Cerebellum!
    if brain_alpha > 0.02 and trim_p > 0.35:
        ba = alpha * brain_alpha * clamp((trim_p - 0.35) / 0.55)
        ctx.set_dash([])
        lw_b = 2.05 / max(0.6, scale ** 0.35)
        ctx.set_line_width(lw_b)
        ctx.set_source_rgba(1, 1, 1, ba * 0.86)

        # Outer multi-lobed cerebral cortex contour
        ctx.new_path()
        ctx.move_to(-66, -68)
        ctx.curve_to(-78, -108, -54, -148, -8, -156)
        ctx.curve_to(38, -164, 92, -144, 108, -98)
        ctx.curve_to(120, -62, 106, -18, 76, -4)
        ctx.curve_to(48, 8, 18, -2, -2, 8)
        ctx.curve_to(-28, 18, -52, 4, -54, -22)
        ctx.curve_to(-70, -30, -74, -50, -66, -68)
        ctx.stroke()

        # Cerebellum + brainstem tucked under occipital lobe (exact match to t=41.42s!)
        ctx.new_path()
        ctx.move_to(36, 4)
        ctx.curve_to(54, 28, 88, 24, 92, 0)
        ctx.curve_to(94, -12, 80, -14, 68, -6)
        ctx.stroke()
        ctx.move_to(46, 12); ctx.curve_to(64, 16, 78, 12, 86, 4); ctx.stroke()
        ctx.move_to(22, 6); ctx.curve_to(20, 28, 24, 48, 30, 62); ctx.stroke()

        # Interconnected curly cortical sulci loops (modeled directly on reference t=41.42s!)
        loops = [
            ((-56, -86), (-36, -116), (-6, -96), (-18, -72)),
            ((-18, -72), (-34, -52), (-8, -42), (10, -64)),
            ((-26, -132), (-2, -146), (26, -122), (8, -98)),
            ((8, -98), (-8, -82), (24, -72), (38, -96)),
            ((28, -144), (62, -142), (76, -112), (48, -104)),
            ((48, -104), (32, -98), (52, -74), (82, -84)),
            ((68, -116), (98, -106), (102, -70), (74, -62)),
            ((12, -58), (34, -72), (56, -46), (34, -28)),
            ((-44, -46), (-24, -62), (-12, -28), (14, -22)),
            ((42, -48), (72, -56), (94, -34), (66, -18)),
            ((-38, -16), (-18, -4), (8, -14), (24, -4)),
        ]
        for p0, p1, p2, p3 in loops:
            ctx.move_to(*p0)
            ctx.curve_to(*p1, *p2, *p3)
            ctx.stroke()

        # Twinkling 4-point neural star sparks inside brain!
        star_pts = [(-36, -86), (16, -118), (62, -82), (-6, -48), (48, -36)]
        for si in range(min(brain_stars, len(star_pts))):
            sx, sy = star_pts[si]
            pulse = 0.68 + 0.32 * math.sin(t * 6.5 + si * 1.7)
            draw_star4(ctx, sx, sy, 14.0 * pulse, ba * 0.98)

    ctx.restore()


def draw_volumetric_beam(ctx, x0: float, y0: float, angle: float, length: float, spread_rad: float = 0.24, alpha: float = 0.55):
    """Feathered volumetric light cone (soft lateral mist + bright axis, matching t=45.17s & t=60.23s)."""
    if alpha <= 0.01 or length <= 2.0:
        return
    ctx.save()
    ctx.translate(x0, y0)
    ctx.rotate(angle)

    # 6 nested cones from wide misty penumbra to focused inner core -> zero hard triangle edge!
    layers = [
        (1.18, 0.10),
        (0.98, 0.14),
        (0.80, 0.18),
        (0.62, 0.22),
        (0.44, 0.26),
        (0.24, 0.30),
    ]
    for sp_mul, w_al in layers:
        y_end = math.tan(spread_rad * sp_mul) * length
        y0_w = 5.0 * sp_mul
        grad = cairo.LinearGradient(0, 0, length, 0)
        grad.add_color_stop_rgba(0.0, 1, 1, 1, alpha * w_al * 1.35)
        grad.add_color_stop_rgba(0.45, 1, 1, 1, alpha * w_al * 0.68)
        grad.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)

        ctx.new_path()
        ctx.move_to(0, -y0_w)
        ctx.line_to(length, -y_end)
        ctx.line_to(length, y_end)
        ctx.line_to(0, y0_w)
        ctx.close_path()
        ctx.set_source(grad)
        ctx.fill()
    ctx.restore()


def draw_mouth_soundwaves(ctx, mx: float, my: float, facing: int, t: float, alpha: float = 1.0):
    """Concentric acoustic speech arcs radiating smoothly from a speaking profile."""
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.set_dash([])
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    base_ang = 0.0 if facing > 0 else math.pi
    phase = (t * 2.4) % 1.0
    for wi in range(4):
        u = (wi + phase) / 4.0
        r = 18.0 + u * 78.0
        al = alpha * math.sin(u * math.pi) * 0.78
        ctx.arc(mx, my, r, base_ang - 0.62, base_ang + 0.62)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.set_line_width(2.6)
        ctx.stroke()
    ctx.restore()


def draw_isometric_cube(ctx, cx: float, cy: float, size: float, alpha: float = 1.0, trim_p: float = 1.0, tape: bool = False):
    """Crisp 3D isometric cube (30-deg projection, modeled on t=75.28s)."""
    if alpha <= 0.01 or trim_p <= 0.01:
        return
    dx = size * math.cos(math.radians(30))
    dy = size * math.sin(math.radians(30))
    ctx.save()
    ctx.translate(cx, cy)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    set_trim_path(ctx, 0.0, trim_p, size * 9.5)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.96)
    ctx.set_line_width(3.8)

    # Outer hexagon
    ctx.new_path()
    ctx.move_to(0, -size)
    ctx.line_to(dx, -dy)
    ctx.line_to(dx, dy)
    ctx.line_to(0, size)
    ctx.line_to(-dx, dy)
    ctx.line_to(-dx, -dy)
    ctx.close_path()
    ctx.stroke()

    # Inner Y-edges meeting at center (0, 0)
    ctx.move_to(-dx, -dy); ctx.line_to(0, 0); ctx.line_to(dx, -dy); ctx.stroke()
    ctx.move_to(0, 0); ctx.line_to(0, size); ctx.stroke()

    if tape and trim_p > 0.7:
        ctx.set_dash([])
        ctx.set_line_width(2.4)
        ctx.set_source_rgba(1, 1, 1, alpha * 0.72)
        ctx.move_to(-dx * 0.48, -dy - (size - dy) * 0.48)
        ctx.line_to(dx * 0.48, -dy + (size - dy) * 0.48)
        ctx.line_to(dx * 0.48, -dy + (size - dy) * 0.48 + size * 0.26)
        ctx.stroke()
    ctx.restore()


def draw_sniper_reticle(ctx, cx: float, cy: float, r: float, rot: float = 0.0, alpha: float = 1.0):
    """Spinning double-ring crosshair reticle (exact match to t=33.88s!)."""
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.set_dash([])
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.98)
    ctx.set_line_width(4.2)
    ctx.arc(0, 0, r, 0, 2 * math.pi); ctx.stroke()
    ctx.set_line_width(2.8)
    ctx.arc(0, 0, r * 0.62, 0, 2 * math.pi); ctx.stroke()
    for k in range(4):
        ang = k * (math.pi * 0.5)
        ctx.move_to(math.cos(ang) * r * 0.35, math.sin(ang) * r * 0.35)
        ctx.line_to(math.cos(ang) * r * 1.24, math.sin(ang) * r * 1.24)
        ctx.stroke()
    ctx.restore()


def draw_neon_checkmark(ctx, cx: float, cy: float, size: float = 34.0, alpha: float = 1.0, pop_p: float = 1.0):
    """Chunky double-outline glowing checkmark badge (exact match to t=37.65s!)."""
    if alpha <= 0.01 or pop_p <= 0.01:
        return
    ctx.save()
    ctx.set_dash([])
    ctx.translate(cx, cy)
    ctx.scale(pop_p, pop_p)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(-size * 0.55, 0)
    ctx.line_to(-size * 0.14, size * 0.42)
    ctx.line_to(size * 0.62, -size * 0.44)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.98)
    ctx.set_line_width(size * 0.34)
    ctx.stroke()
    ctx.restore()


def draw_cursor_arrow_neon(ctx, x: float, y: float, scale: float = 1.0, alpha: float = 1.0):
    """Crisp filled glowing pointer cursor (exact match to t=28.03s..29.98s!)."""
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.set_dash([])
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    ctx.new_path()
    ctx.move_to(0, 0)
    ctx.line_to(0, 48)
    ctx.line_to(13, 37)
    ctx.line_to(23, 56)
    ctx.line_to(31, 52)
    ctx.line_to(21, 33)
    ctx.line_to(36, 33)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, alpha * 0.98)
    ctx.fill()
    ctx.restore()
