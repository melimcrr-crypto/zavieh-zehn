"""
Studio v8.0 Ultra-Blogger VFX, AI Rotoscoping, Stroked Display Typography & 17 Topic Logos
==========================================================================================
Provides:
1. BloggerFontPack: Lalezar Display + Vazirmatn-Black (900) with crisp dark outline strokes
   for maximum mobile readability ("فونت خوانا").
2. HumanRotoscoper: Real deep-learning human segmentation via u2net_human_seg.onnx (ONNXRuntime)
   with temporal smoothing + optical edge light-wrap so giant 3D kinetic titles, radial neon
   auras, volumetric god-rays, and brand logos appear BEHIND the speaker ("افکت‌های پشت صحنه").
3. draw_behind_person_stage & draw_broll_ambient_vfx: Dynamic background motion effects.
4. draw_topic_logo: 17 bespoke vector logos & official brand emblems synced to every single
   product, part, specification, and call-to-action mentioned by the speaker.
"""
import os, math, subprocess
import numpy as np
import cairocffi as cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920

U2NET_HUMAN_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx"
U2NETP_FALLBACK_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx"


def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return a if x < a else (b if x > b else x)


class BloggerFontPack:
    """High-contrast, ultra-legible Persian display & UI typography pack (zero small thin text)."""
    def __init__(self, font_dir: str):
        blk = f"{font_dir}/Vazirmatn-Black.ttf"
        if not os.path.exists(blk):
            blk = f"{font_dir}/Vazirmatn-ExtraBold.ttf"
        lal = f"{font_dir}/Lalezar-Regular.ttf"
        if not os.path.exists(lal):
            lal = blk
        eb = f"{font_dir}/Vazirmatn-ExtraBold.ttf"
        bd = f"{font_dir}/Vazirmatn-Bold.ttf"

        # Behind-head giant 3D depth fonts
        self.hero_156   = ImageFont.truetype(blk, 156)
        self.hero_124   = ImageFont.truetype(lal, 128)
        # Display headlines (Lalezar & Black)
        self.lal_68     = ImageFont.truetype(lal, 68)
        self.lal_56     = ImageFont.truetype(lal, 56)
        self.lal_48     = ImageFont.truetype(lal, 48)
        self.black_72   = ImageFont.truetype(blk, 72)
        self.black_58   = ImageFont.truetype(blk, 58)
        self.black_50   = ImageFont.truetype(blk, 50)   # Primary Subtitle Font!
        self.black_42   = ImageFont.truetype(blk, 42)   # Auto-fit Subtitle Font!
        self.black_36   = ImageFont.truetype(blk, 36)
        # Crisp bold secondary labels (minimum 32-36px Bold!)
        self.eb_38      = ImageFont.truetype(eb, 38)
        self.bold_34    = ImageFont.truetype(bd, 34)
        self.bold_30    = ImageFont.truetype(bd, 30)


_STROKED_CACHE = {}

def get_stroked_text_sprite(text: str, font, fill=(255, 255, 255, 255),
                            stroke_fill=(5, 10, 20, 245), stroke_w: int = 3,
                            glow_rgb=None) -> tuple:
    """
    Renders razor-sharp Persian/ASCII text with thick dark outline stroke + drop shadow
    so every letter pops with 100% legibility on mobile screens.
    Returns (PIL.Image RGBA, logical_text_width, logical_text_height).
    """
    key = (text, id(font), fill, stroke_fill, stroke_w, glow_rgb)
    if key in _STROKED_CACHE:
        return _STROKED_CACHE[key]
    if len(_STROKED_CACHE) > 360:
        _STROKED_CACHE.clear()

    t_dir = "ltr" if text.isascii() else "rtl"
    asc, desc = font.getmetrics()
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dummy.textbbox((0, 0), text, font=font, direction=t_dir, language="fa", stroke_width=stroke_w)
    pad_x = 22 + (14 if glow_rgb else 0)
    pad_y = 16 + (12 if glow_rgb else 0)
    tw = max(1, bb[2] - bb[0] + pad_x * 2)
    th = max(1, asc + desc + pad_y * 2)
    ox = pad_x - bb[0]
    oy = pad_y

    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    if glow_rgb is not None:
        g_im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(g_im).text(
            (ox, oy), text, font=font, fill=(*glow_rgb, 210),
            direction=t_dir, language="fa", stroke_width=stroke_w + 3, stroke_fill=(*glow_rgb, 150)
        )
        canvas = Image.alpha_composite(canvas, g_im.filter(ImageFilter.GaussianBlur(radius=11)))

    d = ImageDraw.Draw(canvas)
    if stroke_w > 0:
        # Soft drop shadow + crisp outline stroke
        d.text((ox, oy + 4), text, font=font, fill=(0, 0, 0, 175),
               direction=t_dir, language="fa", stroke_width=stroke_w + 1, stroke_fill=(0, 0, 0, 175))
        d.text((ox, oy), text, font=font, fill=fill,
               direction=t_dir, language="fa", stroke_width=stroke_w, stroke_fill=stroke_fill)
    else:
        d.text((ox, oy), text, font=font, fill=fill, direction=t_dir, language="fa")

    res = (canvas, bb[2] - bb[0], asc + desc)
    _STROKED_CACHE[key] = res
    return res


# =============================================================================
# REAL AI HUMAN ROTOSCOPING (u2net_human_seg ONNX) FOR BEHIND-PERSON DEPTH VFX
# =============================================================================
def ensure_human_seg_model(work_dir: str) -> str:
    onnx_path = os.path.join(work_dir, "u2net_human_seg.onnx")
    if os.path.exists(onnx_path) and os.path.getsize(onnx_path) > 4_000_000:
        return onnx_path
    for url in (U2NET_HUMAN_URL, U2NETP_FALLBACK_URL):
        try:
            print(f"[Studio v8.0] Downloading AI Human Rotoscope model from {url} ...", flush=True)
            subprocess.run(["curl", "-fsSL", "-L", "--retry", "3", url, "-o", onnx_path], check=True)
            if os.path.getsize(onnx_path) > 4_000_000:
                return onnx_path
        except Exception as e:
            print(f"[Warn] Failed {url}: {e}", flush=True)
    raise RuntimeError("Could not download u2net_human_seg.onnx")


def precompute_talking_head_mattes(raw_mp4: str, work_dir: str, num_th_frames: int = 964) -> str:
    """
    Precomputes smooth 270x480 alpha mattes for all talking-head frames (0..963)
    evaluating u2net_human_seg every 2nd frame + temporal EMA smoothing (~16s total!).
    Saves compact uint8 array (964, 480, 270) to work_dir/th_mattes.npy (~120 MB on disk).
    """
    out_npy = os.path.join(work_dir, "th_mattes.npy")
    if os.path.exists(out_npy):
        return out_npy

    onnx_path = ensure_human_seg_model(work_dir)
    import onnxruntime as ort
    sess_opts = ort.SessionOptions()
    sess_opts.intra_op_num_threads = max(2, os.cpu_count() or 2)
    sess = ort.InferenceSession(onnx_path, sess_options=sess_opts, providers=["CPUExecutionProvider"])
    in_name = sess.get_inputs()[0].name

    # Decode first num_th_frames from raw_mp4 at 320x320 directly via FFmpeg!
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", raw_mp4, "-frames:v", str(num_th_frames),
        "-vf", "scale=320:320:flags=bilinear",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=320 * 320 * 3 * 8)

    mw, mh = 270, 480
    mattes = np.zeros((num_th_frames, mh, mw), dtype=np.uint8)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape((1, 1, 3))
    std  = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape((1, 1, 3))

    last_mask_f = None
    for idx in range(num_th_frames):
        buf = proc.stdout.read(320 * 320 * 3)
        if not buf or len(buf) < 320 * 320 * 3:
            if last_mask_f is not None:
                mattes[idx] = np.clip(last_mask_f * 255.0, 0, 255).astype(np.uint8)
            continue
        if idx % 2 == 0 or last_mask_f is None:
            arr = np.frombuffer(buf, dtype=np.uint8).reshape((320, 320, 3)).astype(np.float32) / 255.0
            norm = ((arr - mean) / std).transpose((2, 0, 1))[None, :, :, :]
            pred = sess.run(None, {in_name: norm})[0][0, 0]
            pmin, pmax = float(pred.min()), float(pred.max())
            pred = (pred - pmin) / (pmax - pmin + 1e-6)
            m_im = Image.fromarray(np.clip(pred * 255.0, 0, 255).astype(np.uint8), "L").resize((mw, mh), Image.Resampling.BILINEAR)
            cur_f = np.asarray(m_im, dtype=np.float32) / 255.0
            if last_mask_f is not None:
                cur_f = 0.68 * cur_f + 0.32 * last_mask_f
            last_mask_f = cur_f
        mattes[idx] = np.clip(last_mask_f * 255.0, 0, 255).astype(np.uint8)

    proc.stdout.close()
    proc.wait()
    # Smooth odd frames between idx-1 and idx+1
    for idx in range(1, num_th_frames - 1, 2):
        mattes[idx] = ((mattes[idx - 1].astype(np.uint16) + mattes[idx + 1].astype(np.uint16)) // 2).astype(np.uint8)

    np.save(out_npy, mattes)
    print(f"[Studio v8.0] AI Human Rotoscope mattes ready: {num_th_frames} frames!", flush=True)
    return out_npy


# =============================================================================
# BEHIND-THE-PERSON DEPTH STAGE ("افکت‌های پشت صحنه") + AMBIENT B-ROLL VFX
# =============================================================================
def _cairo_surface_to_pil_rgba(surf: cairo.ImageSurface) -> Image.Image:
    """Converts premultiplied Cairo ARGB32 surface to straight-alpha PIL RGBA with pure luminous glows."""
    buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((H, W, 4))
    b = buf[:, :, 0].astype(np.uint16)
    g = buf[:, :, 1].astype(np.uint16)
    r = buf[:, :, 2].astype(np.uint16)
    a = buf[:, :, 3].astype(np.uint16)
    a_safe = np.maximum(a, 1)
    r_u = np.minimum(255, (r * 255 + a_safe // 2) // a_safe).astype(np.uint8)
    g_u = np.minimum(255, (g * 255 + a_safe // 2) // a_safe).astype(np.uint8)
    b_u = np.minimum(255, (b * 255 + a_safe // 2) // a_safe).astype(np.uint8)
    out = np.stack([r_u, g_u, b_u, buf[:, :, 3]], axis=2)
    return Image.fromarray(out, "RGBA")


def render_behind_person_stage(t: float, fonts: BloggerFontPack,
                               surf: cairo.ImageSurface, ctx: cairo.Context) -> tuple:
    """
    Draws rich 3D studio depth VFX on the wall BEHIND Milad (0..32.13s):
    - Volumetric diagonal god-rays + floating luminous bokeh particles
    - Pulsing radial neon aura + rotating cyber-medical radar rings behind his shoulders
    - Floating Behind-Shoulder Holographic Brand/Topic Logos peeking out on Left & Right!
    - Giant 3D depth titles ('DENTEYE', 'GRADE A+', 'AIDITE', '100% QC') rising behind him!
    """
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    ctx.paint()
    ctx.restore()
    stage_texts = []

    if t < 5.1:
        acc = (0.16, 0.85, 1.0)    # Electric Cyan
        rgb_i = (40, 218, 255)
        hero_top, hero_sub = "DENTEYE", "تجهیزات تخصصی دندانپزشکی"
        logo_l, logo_r = "denteye", "verified_host"
    elif t < 12.8:
        acc = (0.24, 0.98, 0.60)   # Neon Emerald
        rgb_i = (62, 250, 152)
        hero_top, hero_sub = "GRADE A+", "استوک در حد نو"
        logo_l, logo_r = "dental_stock", "qc_shield"
    elif t < 19.1:
        acc = (0.22, 0.82, 1.0)    # Sapphire Blue
        rgb_i = (56, 210, 255)
        hero_top, hero_sub = "AIDITE", "RAPID 5  •  3D SCANNER"
        logo_l, logo_r = "aidite_brand", "rapid5_wand"
    else:
        acc = (0.28, 0.98, 0.56)   # QC Emerald
        rgb_i = (72, 250, 142)
        hero_top, hero_sub = "100% QC", "تایید کارشناسان فنی"
        logo_l, logo_r = "qc_shield", "micron_target"

    # 1. Volumetric Diagonal Studio God-Rays sweeping across back wall
    for ri in range(3):
        bx = 165 + ri * 320 + math.sin(t * 0.75 + ri * 1.4) * 60.0
        lg = cairo.LinearGradient(bx - 120, 0, bx + 160, 1180)
        lg.add_color_stop_rgba(0.0, acc[0], acc[1], acc[2], 0.28)
        lg.add_color_stop_rgba(0.55, acc[0], acc[1], acc[2], 0.11)
        lg.add_color_stop_rgba(1.0, acc[0], acc[1], acc[2], 0.0)
        ctx.move_to(bx - 105, 0)
        ctx.line_to(bx + 105, 0)
        ctx.line_to(bx + 300, 1180)
        ctx.line_to(bx + 35, 1180)
        ctx.close_path()
        ctx.set_source(lg)
        ctx.fill()

    # 2. Radial Neon Aura Halo right behind Milad's head & shoulders (cx=505, cy=560)
    pulse = 0.85 + 0.15 * math.sin(t * 3.4)
    rg = cairo.RadialGradient(505, 560, 40, 505, 560, 520)
    rg.add_color_stop_rgba(0.0, acc[0], acc[1], acc[2], 0.52 * pulse)
    rg.add_color_stop_rgba(0.50, acc[0], acc[1], acc[2], 0.22 * pulse)
    rg.add_color_stop_rgba(1.0, acc[0], acc[1], acc[2], 0.0)
    ctx.rectangle(0, 0, W, 1280)
    ctx.set_source(rg)
    ctx.fill()

    # 3. Rotating Segmented Tech-Medical HUD Rings behind Milad's shoulders!
    for rad, spd, lw, segs in [(355, 0.42, 4.2, 6), (455, -0.28, 2.8, 8)]:
        ang0 = t * spd
        for s in range(segs):
            a0 = ang0 + s * (2 * math.pi / segs)
            a1 = a0 + (2 * math.pi / segs) * 0.56
            ctx.arc(505, 560, rad, a0, a1)
            ctx.set_source_rgba(acc[0], acc[1], acc[2], 0.62)
            ctx.set_line_width(lw)
            ctx.stroke()

    # 4. Floating Behind-Shoulder 3D Hologram Topic Logos (Left & Right of Milad!)
    bob_l = math.sin(t * 2.1) * 14.0
    bob_r = math.cos(t * 1.9) * 14.0
    draw_topic_logo(ctx, stage_texts, fonts, logo_l, 152, 545 + bob_l, 138, t, 0.92)
    draw_topic_logo(ctx, stage_texts, fonts, logo_r, 895, 585 + bob_r, 138, t, 0.92)

    # 5. Horizontal Laser Scan-Wave on Product Reveal (12.8..19.1s)
    if 12.8 <= t < 19.1:
        sy = 200.0 + ((t - 12.8) * 195.0) % 790.0
        sg = cairo.LinearGradient(0, sy - 48, 0, sy + 48)
        sg.add_color_stop_rgba(0.0, 0.2, 0.85, 1.0, 0.0)
        sg.add_color_stop_rgba(0.5, 0.45, 0.96, 1.0, 0.48)
        sg.add_color_stop_rgba(1.0, 0.2, 0.85, 1.0, 0.0)
        ctx.rectangle(30, sy - 48, W - 60, 96)
        ctx.set_source(sg)
        ctx.fill()

    # 6. Floating Glowing Studio Bokeh Sparks
    for pi in range(26):
        px = (97 * pi + int(math.sin(t * 0.65 + pi) * 42)) % 980 + 50
        py = 1100 - ((int(t * (38 + (pi % 5) * 9)) + pi * 83) % 1020)
        pr = 2.6 + (pi % 4) * 1.8
        ctx.arc(px, py, pr * 2.6, 0, math.pi * 2)
        ctx.set_source_rgba(acc[0], acc[1], acc[2], 0.24)
        ctx.fill()
        ctx.arc(px, py, pr, 0, math.pi * 2)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.72)
        ctx.fill()

    stage_rgba = _cairo_surface_to_pil_rgba(surf)
    for sp_t, tx, ty, tal in stage_texts:
        if tal < 0.995:
            r, g, b, a = sp_t.split()
            sp_t = Image.merge("RGBA", (r, g, b, a.point(lambda p: int(p * tal))))
        stage_rgba.alpha_composite(sp_t, (int(round(tx - sp_t.width * 0.5)), int(round(ty - sp_t.height * 0.5))))

    # 7. Giant Glowing 3D Depth Title BEHIND Milad's Head!
    sp_big, _, _ = get_stroked_text_sprite(
        hero_top, fonts.hero_156,
        fill=(255, 255, 255, 232),
        stroke_fill=(rgb_i[0] // 3, rgb_i[1] // 3, rgb_i[2] // 3, 235),
        stroke_w=5, glow_rgb=rgb_i
    )
    sp_sub, _, _ = get_stroked_text_sprite(
        hero_sub, fonts.lal_48,
        fill=(*rgb_i, 242),
        stroke_fill=(5, 12, 24, 235),
        stroke_w=3
    )
    drift_y = math.sin(t * 1.8) * 8.0
    stage_rgba.alpha_composite(sp_big, (int(540 - sp_big.width * 0.5), int(228 + drift_y - sp_big.height * 0.5)))
    stage_rgba.alpha_composite(sp_sub, (int(540 - sp_sub.width * 0.5), int(352 + drift_y - sp_sub.height * 0.5)))
    return stage_rgba, rgb_i


def composite_talking_head_with_depth_vfx(graded_bg_im: Image.Image, raw_matte_270x480: np.ndarray,
                                          crop_box_raw: tuple, raw_size: tuple,
                                          t: float, fonts: BloggerFontPack,
                                          surf: cairo.ImageSurface, ctx: cairo.Context) -> Image.Image:
    """
    True 3-Layer Rotoscope Sandwich + Colored Studio Rim Light-Wrap:
      Layer 1: Graded Studio Camera Frame (Background Wall)
      Layer 2: Behind-Person Neon Stage (Giant 3D Text, Shoulder Holograms, Radar Rings, God-Rays)
      Layer 3: Rotoscoped Foreground Subject (100% solid interior + smooth colored rim light-wrap!)
    """
    rx0, ry0, rx1, ry1 = crop_box_raw
    rw, rh = raw_size
    mw, mh = raw_matte_270x480.shape[1], raw_matte_270x480.shape[0]
    mx0 = int(round(rx0 * mw / rw))
    my0 = int(round(ry0 * mh / rh))
    mx1 = max(mx0 + 4, int(round(rx1 * mw / rw)))
    my1 = max(my0 + 4, int(round(ry1 * mh / rh)))

    m_crop = Image.fromarray(raw_matte_270x480[my0:my1, mx0:mx1], "L").resize((W, H), Image.Resampling.BILINEAR)
    m_crop = m_crop.filter(ImageFilter.GaussianBlur(radius=2.0))
    fg_alpha = np.asarray(m_crop, dtype=np.float32) / 255.0

    # Anchor foreground suitcase at bottom (y >= 1255) & solidify interior subject (>= 0.62 -> 1.0)
    yy = np.arange(H, dtype=np.float32)[:, None]
    case_mask = np.clip((yy - 1255.0) / 55.0, 0.0, 1.0)
    fg_alpha = np.maximum(fg_alpha, case_mask)
    fg_alpha = np.clip((fg_alpha - 0.28) / 0.40, 0.0, 1.0)

    stage_rgba, rim_rgb_i = render_behind_person_stage(t, fonts, surf, ctx)

    bg_with_vfx = graded_bg_im.convert("RGBA")
    bg_with_vfx.alpha_composite(stage_rgba)

    fg_arr = np.asarray(graded_bg_im, dtype=np.float32)
    bg_vfx_arr = np.asarray(bg_with_vfx.convert("RGB"), dtype=np.float32)

    a3 = fg_alpha[:, :, None]
    comp = bg_vfx_arr * (1.0 - a3) + fg_arr * a3

    # Colored Optical Studio Rim Light-Wrap along hair/shoulder silhouette (no harsh white halo!)
    rim_band = np.clip(4.0 * fg_alpha * (1.0 - fg_alpha), 0.0, 1.0)[:, :, None]
    rim_col = np.array(rim_rgb_i, dtype=np.float32).reshape((1, 1, 3))
    comp = np.clip(comp + rim_col * rim_band * 0.30, 0, 255).astype(np.uint8)
    return Image.fromarray(comp, "RGB")


def draw_broll_ambient_vfx(ctx: cairo.Context, t: float, is_dark_stage: bool = False):
    """Adds energetic background motion particles, HUD corner brackets & subtle light leaks on B-roll."""
    acc = (0.18, 0.86, 1.0) if int(t / 8.0) % 2 == 0 else (0.26, 0.98, 0.58)
    if is_dark_stage:
        # Rotating cyber-medical rings + floating particles on dark showcase/monitor scenes!
        for rad, spd in [(460, 0.22), (560, -0.15)]:
            for k in range(6):
                a0 = t * spd + k * (math.pi / 3.0)
                ctx.arc(540, 860, rad, a0, a0 + 0.35)
                ctx.set_source_rgba(acc[0], acc[1], acc[2], 0.20)
                ctx.set_line_width(2.2)
                ctx.stroke()

    # Floating luminous dust particles across B-roll
    n_p = 22 if is_dark_stage else 14
    for pi in range(n_p):
        px = (131 * pi + int(math.sin(t * 0.8 + pi) * 35)) % 980 + 50
        py = 1820 - ((int(t * (42 + (pi % 4) * 11)) + pi * 137) % 1720)
        pr = 2.2 + (pi % 3) * 1.6
        ctx.arc(px, py, pr * 2.2, 0, math.pi * 2)
        ctx.set_source_rgba(acc[0], acc[1], acc[2], 0.18 if is_dark_stage else 0.12)
        ctx.fill()
        ctx.arc(px, py, pr, 0, math.pi * 2)
        ctx.set_source_rgba(1, 1, 1, 0.42 if is_dark_stage else 0.28)
        ctx.fill()


# =============================================================================
# 17 BESPOKE VECTOR TOPIC LOGOS & OFFICIAL BRAND EMBLEMS ("لوگوهای هرچیزی")
# =============================================================================
def _rrect(ctx, x, y, w, h, r):
    r = min(r, w * 0.5, h * 0.5)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
    ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
    ctx.close_path()


def _draw_tooth_silhouette(ctx, cx, cy, sc, rgba=(1, 1, 1, 0.96)):
    """Draws a crisp, unmistakable anatomical molar/crown vector icon."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(sc, sc)
    ctx.move_to(0, -24)
    ctx.curve_to(10, -30, 26, -28, 28, -12)
    ctx.curve_to(30, 2, 22, 12, 18, 28)
    ctx.curve_to(15, 36, 8, 34, 6, 20)
    ctx.curve_to(4, 12, -4, 12, -6, 20)
    ctx.curve_to(-8, 34, -15, 36, -18, 28)
    ctx.curve_to(-22, 12, -30, 2, -28, -12)
    ctx.curve_to(-26, -28, -10, -30, 0, -24)
    ctx.close_path()
    ctx.set_source_rgba(*rgba)
    ctx.fill()
    ctx.restore()


def draw_topic_logo(ctx: cairo.Context, texts_out: list, fonts: BloggerFontPack,
                    kind: str, cx: float, cy: float, size: float, t: float, alpha: float = 1.0):
    """
    Draws a high-impact animated badge/logo for every single brand, accessory, or spec
    mentioned by the speaker!
    """
    if alpha <= 0.01:
        return
    r = size * 0.5
    pulse = 0.85 + 0.15 * math.sin(t * 5.0)

    if kind == "instagram":
        # Official Instagram Multi-Stop Gradient Squircle Logo!
        _rrect(ctx, cx - r, cy - r, size, size, size * 0.26)
        ig = cairo.LinearGradient(cx - r, cy + r, cx + r, cy - r)
        ig.add_color_stop_rgba(0.00, 0.996, 0.855, 0.459, alpha)  # #FEDA75
        ig.add_color_stop_rgba(0.26, 0.980, 0.494, 0.118, alpha)  # #FA7E1E
        ig.add_color_stop_rgba(0.55, 0.839, 0.161, 0.463, alpha)  # #D62976
        ig.add_color_stop_rgba(0.80, 0.588, 0.184, 0.749, alpha)  # #962FBF
        ig.add_color_stop_rgba(1.00, 0.310, 0.357, 0.835, alpha)  # #4F5BD5
        ctx.set_source(ig)
        ctx.fill()
        # Inner white camera rounded square + lens circle + flash dot
        ir = size * 0.31
        _rrect(ctx, cx - ir, cy - ir, ir * 2, ir * 2, ir * 0.52)
        ctx.set_source_rgba(1, 1, 1, 0.98 * alpha)
        ctx.set_line_width(max(3.2, size * 0.068))
        ctx.stroke()
        ctx.arc(cx, cy, size * 0.155, 0, math.pi * 2)
        ctx.stroke()
        ctx.arc(cx + size * 0.185, cy - size * 0.185, size * 0.042, 0, math.pi * 2)
        ctx.fill()
        return

    if kind == "aidite_brand":
        # Official White-Pill Aidite Brand Logo Lockup (Navy 'Aidite' + Cyan Diamond over 'i'!)
        bw, bh = size * 1.85, size * 0.92
        _rrect(ctx, cx - bw * 0.5, cy - bh * 0.5, bw, bh, bh * 0.32)
        ctx.set_source_rgba(0.96, 0.98, 1.0, 0.97 * alpha)
        ctx.fill()
        _rrect(ctx, cx - bw * 0.5, cy - bh * 0.5, bw, bh, bh * 0.32)
        ctx.set_source_rgba(0.16, 0.82, 1.0, 0.95 * alpha)
        ctx.set_line_width(3.2)
        ctx.stroke()
        sp_a, _, _ = get_stroked_text_sprite("Aidite", fonts.black_50, fill=(11, 58, 118, 255), stroke_w=0)
        texts_out.append((sp_a, cx, cy + 3, alpha))
        # Iconic cyan rotated diamond accent above the first 'i'
        dx, dy = cx - bw * 0.14, cy - bh * 0.26
        ctx.move_to(dx, dy - 7); ctx.line_to(dx + 7, dy); ctx.line_to(dx, dy + 7); ctx.line_to(dx - 7, dy)
        ctx.close_path()
        ctx.set_source_rgba(0.05, 0.72, 0.98, alpha)
        ctx.fill()
        return

    if kind == "verified_host":
        # Official 12-Scallop Blue Creator Verified Badge!
        pts = 24
        for i in range(pts):
            ang = i * (2 * math.pi / pts) + t * 0.5
            rr = r * (1.0 if i % 2 == 0 else 0.83)
            px, py = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
            if i == 0:
                ctx.move_to(px, py)
            else:
                ctx.line_to(px, py)
        ctx.close_path()
        ctx.set_source_rgba(0.11, 0.63, 0.98, alpha)
        ctx.fill()
        ctx.move_to(cx - r * 0.34, cy + r * 0.02)
        ctx.line_to(cx - r * 0.08, cy + r * 0.28)
        ctx.line_to(cx + r * 0.38, cy - r * 0.24)
        ctx.set_source_rgba(1, 1, 1, alpha)
        ctx.set_line_width(max(4.0, size * 0.085))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
        return

    # Glowing Circular/Squircle Medallion Base for Technical & Dental Icons
    col_map = {
        "denteye":       (0.16, 0.84, 1.00),
        "dental_stock":  (0.24, 0.98, 0.60),
        "rapid5_wand":   (0.18, 0.84, 1.00),
        "qc_shield":     (0.24, 0.98, 0.56),
        "stand":         (0.22, 0.82, 1.00),
        "usb_flash":     (0.32, 0.78, 1.00),
        "scan_tips_4":   (0.26, 0.98, 0.62),
        "autoclave_100": (1.00, 0.78, 0.24),
        "feather_162g":  (0.18, 0.88, 1.00),
        "laser_25mm":    (0.26, 0.98, 0.60),
        "no_calibration":(0.26, 0.98, 0.56),
        "stopwatch":     (0.18, 0.86, 1.00),
        "micron_target": (1.00, 0.80, 0.25),
        "soft_tissue_ai":(0.98, 0.46, 0.68),
    }
    mc = col_map.get(kind, (0.18, 0.84, 1.0))

    # Outer halo + dark glass medallion
    ctx.arc(cx, cy, r * 1.12, 0, math.pi * 2)
    ctx.set_source_rgba(mc[0], mc[1], mc[2], 0.22 * alpha * pulse)
    ctx.fill()
    _rrect(ctx, cx - r, cy - r, size, size, size * 0.28)
    ctx.set_source_rgba(0.05, 0.11, 0.22, 0.94 * alpha)
    ctx.fill()
    _rrect(ctx, cx - r, cy - r, size, size, size * 0.28)
    ctx.set_source_rgba(mc[0], mc[1], mc[2], 0.95 * alpha)
    ctx.set_line_width(3.0)
    ctx.stroke()

    sc = size / 100.0
    if kind == "denteye":
        # Eye Almond + Molar Tooth Iris!
        ctx.move_to(cx - 34 * sc, cy)
        ctx.curve_to(cx - 16 * sc, cy - 24 * sc, cx + 16 * sc, cy - 24 * sc, cx + 34 * sc, cy)
        ctx.curve_to(cx + 16 * sc, cy + 24 * sc, cx - 16 * sc, cy + 24 * sc, cx - 34 * sc, cy)
        ctx.set_source_rgba(mc[0], mc[1], mc[2], 0.95 * alpha)
        ctx.set_line_width(3.2 * sc)
        ctx.stroke()
        _draw_tooth_silhouette(ctx, cx, cy + 2 * sc, 0.42 * sc, (1, 1, 1, 0.98 * alpha))

    elif kind == "dental_stock":
        _draw_tooth_silhouette(ctx, cx - 4 * sc, cy + 4 * sc, 0.82 * sc, (1, 1, 1, 0.98 * alpha))
        # Golden sparkle star top-right
        sx, sy = cx + 24 * sc, cy - 22 * sc
        for a_s in (0, math.pi * 0.5):
            ctx.move_to(sx - 11 * sc * math.cos(a_s), sy - 11 * sc * math.sin(a_s))
            ctx.line_to(sx + 11 * sc * math.cos(a_s), sy + 11 * sc * math.sin(a_s))
        ctx.set_source_rgba(1.0, 0.84, 0.25, alpha)
        ctx.set_line_width(3.2 * sc)
        ctx.stroke()

    elif kind == "rapid5_wand":
        # Sleek angled intraoral scanner wand + cyan laser fan!
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(-0.48)
        _rrect(ctx, -32 * sc, -10 * sc, 54 * sc, 20 * sc, 9 * sc)
        ctx.set_source_rgba(0.95, 0.98, 1.0, alpha)
        ctx.fill()
        # Optical nozzle tip
        ctx.move_to(20 * sc, -7 * sc); ctx.line_to(38 * sc, -5 * sc)
        ctx.line_to(38 * sc, 5 * sc); ctx.line_to(20 * sc, 7 * sc); ctx.close_path()
        ctx.set_source_rgba(0.75, 0.90, 1.0, alpha); ctx.fill()
        # Laser scan cone
        ctx.move_to(38 * sc, 0); ctx.line_to(52 * sc, -16 * sc); ctx.line_to(52 * sc, 16 * sc); ctx.close_path()
        ctx.set_source_rgba(0.18, 0.88, 1.0, 0.55 * alpha * pulse); ctx.fill()
        ctx.restore()

    elif kind == "qc_shield":
        # Classic Security Shield + Bold Checkmark
        ctx.move_to(cx, cy - 32 * sc)
        ctx.line_to(cx + 28 * sc, cy - 20 * sc)
        ctx.curve_to(cx + 28 * sc, cy + 8 * sc, cx + 14 * sc, cy + 24 * sc, cx, cy + 34 * sc)
        ctx.curve_to(cx - 14 * sc, cy + 24 * sc, cx - 28 * sc, cy + 8 * sc, cx - 28 * sc, cy - 20 * sc)
        ctx.close_path()
        ctx.set_source_rgba(0.24, 0.98, 0.56, 0.25 * alpha); ctx.fill_preserve()
        ctx.set_source_rgba(0.28, 0.98, 0.58, alpha); ctx.set_line_width(3.4 * sc); ctx.stroke()
        ctx.move_to(cx - 12 * sc, cy + 1 * sc); ctx.line_to(cx - 3 * sc, cy + 11 * sc); ctx.line_to(cx + 14 * sc, cy - 9 * sc)
        ctx.set_source_rgba(1, 1, 1, alpha); ctx.set_line_width(4.2 * sc); ctx.stroke()

    elif kind == "stand":
        # Desktop Cradle Base + Upright Wand Holder
        _rrect(ctx, cx - 28 * sc, cy + 16 * sc, 56 * sc, 12 * sc, 6 * sc)
        ctx.set_source_rgba(0.92, 0.97, 1.0, alpha); ctx.fill()
        ctx.move_to(cx - 14 * sc, cy + 16 * sc); ctx.line_to(cx - 6 * sc, cy - 22 * sc)
        ctx.line_to(cx + 12 * sc, cy - 22 * sc); ctx.line_to(cx + 16 * sc, cy + 16 * sc); ctx.close_path()
        ctx.set_source_rgba(0.22, 0.84, 1.0, 0.85 * alpha); ctx.fill()

    elif kind == "usb_flash":
        # USB Flash Drive Body + Metal Plug
        _rrect(ctx, cx - 15 * sc, cy - 10 * sc, 30 * sc, 40 * sc, 8 * sc)
        ctx.set_source_rgba(0.22, 0.80, 1.0, alpha); ctx.fill()
        _rrect(ctx, cx - 10 * sc, cy - 28 * sc, 20 * sc, 18 * sc, 3 * sc)
        ctx.set_source_rgba(0.88, 0.94, 1.0, alpha); ctx.fill()
        ctx.arc(cx, cy + 10 * sc, 5 * sc, 0, math.pi * 2)
        ctx.set_source_rgba(1, 1, 1, alpha); ctx.fill()

    elif kind == "scan_tips_4":
        # 3 Standard Tips (Cyan) + 1 Mini Tip (Gold)!
        for ti in range(4):
            tx = cx - 27 * sc + ti * 18 * sc
            th_t = 44 * sc if ti < 3 else 30 * sc
            ty = cy + 22 * sc - th_t
            _rrect(ctx, tx - 5.5 * sc, ty, 11 * sc, th_t, 4 * sc)
            if ti < 3:
                ctx.set_source_rgba(0.22, 0.88, 1.0, alpha)
            else:
                ctx.set_source_rgba(1.0, 0.80, 0.25, alpha)
            ctx.fill()

    elif kind == "autoclave_100":
        # Animated Rising Steam Waves + 134° Sterilization Ring!
        ctx.arc(cx, cy + 4 * sc, 26 * sc, 0, math.pi * 2)
        ctx.set_source_rgba(1.0, 0.78, 0.24, 0.92 * alpha); ctx.set_line_width(3.4 * sc); ctx.stroke()
        for wi in (-12, 0, 12):
            wx = cx + wi * sc
            ctx.move_to(wx, cy + 16 * sc)
            for sy in range(16, -24, -4):
                off = math.sin((sy * 0.25) + t * 6.0 + wi) * 4.2 * sc
                ctx.line_to(wx + off, cy + sy * sc)
            ctx.set_source_rgba(1.0, 0.92, 0.55, alpha); ctx.set_line_width(3.0 * sc); ctx.stroke()

    elif kind == "feather_162g":
        # Weightless Feather Quill
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(-0.55)
        ctx.move_to(0, 32 * sc)
        ctx.curve_to(-22 * sc, 10 * sc, -18 * sc, -24 * sc, 0, -34 * sc)
        ctx.curve_to(18 * sc, -24 * sc, 22 * sc, 10 * sc, 0, 32 * sc)
        ctx.set_source_rgba(0.20, 0.88, 1.0, 0.88 * alpha); ctx.fill()
        ctx.move_to(0, 36 * sc); ctx.line_to(0, -30 * sc)
        ctx.set_source_rgba(1, 1, 1, alpha); ctx.set_line_width(3.0 * sc); ctx.stroke()
        ctx.restore()

    elif kind == "laser_25mm":
        # Laser Depth Cone hitting Tooth Crown
        ctx.move_to(cx, cy - 32 * sc); ctx.line_to(cx - 24 * sc, cy + 6 * sc); ctx.line_to(cx + 24 * sc, cy + 6 * sc); ctx.close_path()
        ctx.set_source_rgba(0.24, 0.98, 0.60, 0.42 * alpha * pulse); ctx.fill()
        _draw_tooth_silhouette(ctx, cx, cy + 16 * sc, 0.52 * sc, (1, 1, 1, 0.96 * alpha))

    elif kind == "no_calibration":
        # Gear Circle + Bold Green Check & Slash-Free Lock
        ctx.arc(cx, cy, 24 * sc, 0, math.pi * 2)
        ctx.set_source_rgba(0.26, 0.98, 0.56, alpha); ctx.set_line_width(4.0 * sc); ctx.stroke()
        ctx.move_to(cx - 11 * sc, cy + 1 * sc); ctx.line_to(cx - 2 * sc, cy + 10 * sc); ctx.line_to(cx + 13 * sc, cy - 9 * sc)
        ctx.set_source_rgba(1, 1, 1, alpha); ctx.set_line_width(4.5 * sc); ctx.stroke()

    elif kind == "stopwatch":
        # Animated Stopwatch Sweeping Arc!
        ctx.arc(cx, cy + 3 * sc, 25 * sc, 0, math.pi * 2)
        ctx.set_source_rgba(1, 1, 1, 0.28 * alpha); ctx.set_line_width(3.5 * sc); ctx.stroke()
        sweep = -math.pi * 0.5 + ((t * 2.6) % (2 * math.pi))
        ctx.arc(cx, cy + 3 * sc, 25 * sc, -math.pi * 0.5, sweep)
        ctx.set_source_rgba(mc[0], mc[1], mc[2], alpha); ctx.set_line_width(4.5 * sc); ctx.stroke()
        ctx.move_to(cx, cy + 3 * sc)
        ctx.line_to(cx + 16 * sc * math.cos(sweep), cy + 3 * sc + 16 * sc * math.sin(sweep))
        ctx.set_source_rgba(1, 1, 1, alpha); ctx.set_line_width(3.2 * sc); ctx.stroke()

    elif kind == "micron_target":
        # Precision Crosshair Reticle over Tooth Crown
        _draw_tooth_silhouette(ctx, cx, cy + 2 * sc, 0.56 * sc, (1, 1, 1, 0.92 * alpha))
        ctx.arc(cx, cy, 28 * sc, 0, math.pi * 2)
        ctx.set_source_rgba(1.0, 0.80, 0.25, alpha); ctx.set_line_width(2.8 * sc); ctx.stroke()
        for dx, dy in [(-34, 0), (22, 0), (0, -34), (0, 22)]:
            ctx.move_to(cx + dx * sc, cy + dy * sc)
            ctx.line_to(cx + (dx + (12 if dx != 0 else 0)) * sc, cy + (dy + (12 if dy != 0 else 0)) * sc)
        ctx.stroke()

    elif kind == "soft_tissue_ai":
        # AI Neural Chip + Soft Wave!
        _rrect(ctx, cx - 22 * sc, cy - 22 * sc, 44 * sc, 44 * sc, 10 * sc)
        ctx.set_source_rgba(0.98, 0.46, 0.68, 0.30 * alpha); ctx.fill_preserve()
        ctx.set_source_rgba(0.98, 0.55, 0.75, alpha); ctx.set_line_width(3.0 * sc); ctx.stroke()
        sp_ai, _, _ = get_stroked_text_sprite("AI", fonts.bold_30, fill=(255, 255, 255, 255), stroke_w=0)
        texts_out.append((sp_ai, cx, cy, alpha))
