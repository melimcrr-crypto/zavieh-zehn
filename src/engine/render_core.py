import os, math, time, subprocess, multiprocessing as mp
import numpy as np
import cairocffi as cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 60

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

def window_fade(t: float, t0: float, t1: float, fi: float = 0.35, fo: float = 0.35) -> float:
    if t < t0 or t > t1:
        return 0.0
    a = clamp((t - t0) / fi) if fi > 0 else 1.0
    b = clamp((t1 - t) / fo) if fo > 0 else 1.0
    return ease_out_cubic(min(a, b))

class FontBank:
    def __init__(self, font_dir: str):
        self.light_24 = ImageFont.truetype(f"{font_dir}/Vazirmatn-Light.ttf", 24)
        self.light_26 = ImageFont.truetype(f"{font_dir}/Vazirmatn-Light.ttf", 26)
        self.reg_28   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Regular.ttf", 28)
        self.reg_32   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Regular.ttf", 32)
        self.med_34   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Medium.ttf", 34)
        self.med_38   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Medium.ttf", 38)
        self.med_42   = ImageFont.truetype(f"{font_dir}/Vazirmatn-Medium.ttf", 42)
        self.bold_36  = ImageFont.truetype(f"{font_dir}/Vazirmatn-Bold.ttf", 36)
        self.bold_44  = ImageFont.truetype(f"{font_dir}/Vazirmatn-Bold.ttf", 44)
        self.bold_52  = ImageFont.truetype(f"{font_dir}/Vazirmatn-Bold.ttf", 52)
        self.eb_68    = ImageFont.truetype(f"{font_dir}/Vazirmatn-ExtraBold.ttf", 68)
        self.eb_92    = ImageFont.truetype(f"{font_dir}/Vazirmatn-ExtraBold.ttf", 92)

_SPRITE_CACHE = {}

def get_text_sprite(text: str, font, color=(255, 255, 255, 255), glow: float = 0.0) -> Image.Image:
    key = (text, id(font), color, round(glow, 2))
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]
    if len(_SPRITE_CACHE) > 120:
        _SPRITE_CACHE.clear()

    t_dir = "ltr" if text.isascii() else "rtl"
    dummy = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font, direction=t_dir, language="fa")
    pad = 34
    tw = max(1, bbox[2] - bbox[0] + pad * 2)
    th = max(1, bbox[3] - bbox[1] + pad * 2)
    ox = pad - bbox[0]
    oy = pad - bbox[1]

    fg = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(fg).text((ox, oy), text, font=font, fill=color, direction=t_dir, language="fa")

    if glow > 0.01:
        ga = int(clamp(glow) * 215)
        g_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(g_img).text((ox, oy), text, font=font, fill=(255, 255, 255, ga), direction=t_dir, language="fa")
        g_blur = g_img.filter(ImageFilter.GaussianBlur(radius=14))
        out = Image.alpha_composite(g_blur, fg)
    else:
        out = fg

    _SPRITE_CACHE[key] = out
    return out

def paste_center(canvas: Image.Image, sprite: Image.Image, cx: float, cy: float, alpha: float = 1.0):
    if alpha <= 0.01:
        return
    if alpha < 0.995:
        r, g, b, a = sprite.split()
        a = a.point(lambda p: int(p * alpha))
        sprite = Image.merge("RGBA", (r, g, b, a))
    x = int(round(cx - sprite.width / 2.0))
    y = int(round(cy - sprite.height / 2.0))
    canvas.alpha_composite(sprite, (x, y))

def draw_star4(ctx, cx: float, cy: float, r: float, alpha: float = 1.0):
    if r <= 0.2 or alpha <= 0.01:
        return
    ctx.save()
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

def draw_stipple_line(ctx, x0, y0, x1, y1, count: int, r: float = 1.8, alpha: float = 0.8):
    if count <= 0 or alpha <= 0.01:
        return
    ctx.set_source_rgba(1, 1, 1, alpha)
    for i in range(count + 1):
        u = i / max(1, count)
        ctx.arc(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, r, 0, 2 * math.pi)
        ctx.fill()

def draw_hud_and_subtitles(
    cs, cg, text_overlays: list, fonts: FontBank, t: float, total_dur: float,
    ep_code: str, ep_title: str, chapter_starts: list[float], sub_lines: list[dict]
):
    """
    Renders:
    1. Minimalist @ensan.besham-inspired HUD header at top ('زاویه ذهن | پرونده ۰۲ • توهم فرکانس')
       + rotating astrolabe mind-angle mini-avatar at top-left!
    2. Subtle chapter progress dots at y=1515 ('• • ⚪ • •')
    3. Word-by-word RTL floating Karaoke subtitles at y=1615
    """
    hud_alpha = window_fade(t, 0.0, total_dur, fi=0.4, fo=0.8)
    # Hide top HUD during final 3.5s full-screen brand lockup for pure visual impact
    if len(chapter_starts) >= 2:
        brand_fade = clamp((total_dur - 4.2 - t) / 0.6)
        hud_alpha *= brand_fade

    if hud_alpha > 0.01:
        # Top hairline divider & angled پرونده tab (y=118)
        cs.set_source_rgba(1, 1, 1, 0.11 * hud_alpha)
        cs.set_line_width(1.2)
        cs.move_to(75, 134)
        cs.line_to(650, 134)
        cs.line_to(674, 110)
        cs.line_to(1005, 110)
        cs.stroke()

        sp_ep = get_text_sprite(fa(f"{ep_code}  •  {ep_title}"), fonts.reg_28, (225, 225, 232, 255), glow=0.25)
        text_overlays.append((sp_ep, 840, 84, hud_alpha * 0.92))

        # Top-left rotating Observatory Mind-Angle Mini-Avatar (cx=128, cy=96)
        ax, ay = 128, 96
        cs.set_source_rgba(1, 1, 1, 0.32 * hud_alpha)
        cs.set_line_width(1.3)
        cs.arc(ax, ay, 28, 0, 2 * math.pi)
        cs.stroke()
        # Counter-rotating tick ring
        for k in range(12):
            ang = k * (math.pi / 6.0) - t * 0.45
            cs.move_to(ax + math.cos(ang) * 33, ay + math.sin(ang) * 33)
            cs.line_to(ax + math.cos(ang) * 37, ay + math.sin(ang) * 37)
            cs.stroke()
        # Perspective angle rays inside mini-avatar
        cs.set_source_rgba(1, 1, 1, 0.90 * hud_alpha)
        cs.set_line_width(1.8)
        cs.move_to(ax + 8, ay + 4); cs.line_to(ax - 15, ay - 11); cs.stroke()
        cs.set_source_rgba(1, 1, 1, 0.50 * hud_alpha)
        cs.move_to(ax + 8, ay + 4); cs.line_to(ax - 15, ay + 12); cs.stroke()
        draw_star4(cs, ax + 8, ay + 4, 5.5, hud_alpha)
        draw_star4(cg, ax + 8, ay + 4, 8.5, hud_alpha * 0.75)

        # Chapter progress dots at y=1518 (RTL order: chapter 0 on right -> last on left)
        n_ch = len(chapter_starts)
        cur_ch = 0
        for ci, cs_t in enumerate(chapter_starts):
            if t >= cs_t:
                cur_ch = ci
        dot_gap = 24.0
        right_x = 540 + (n_ch - 1) * dot_gap / 2.0
        for ci in range(n_ch):
            dx = right_x - ci * dot_gap
            dy = 1520
            if ci == cur_ch:
                cs.arc(dx, dy, 4.8, 0, 2 * math.pi)
                cs.set_source_rgba(1, 1, 1, 0.96 * hud_alpha)
                cs.fill()
                cg.arc(dx, dy, 8.5, 0, 2 * math.pi)
                cg.set_source_rgba(1, 1, 1, 0.80 * hud_alpha)
                cg.fill()
            elif ci < cur_ch:
                cs.arc(dx, dy, 3.0, 0, 2 * math.pi)
                cs.set_source_rgba(1, 1, 1, 0.45 * hud_alpha)
                cs.fill()
            else:
                cs.arc(dx, dy, 2.6, 0, 2 * math.pi)
                cs.set_source_rgba(1, 1, 1, 0.16 * hud_alpha)
                cs.fill()

def composite_oled_frame(surf_glow, surf_sharp, text_overlays: list, fonts: FontBank, t: float, sub_lines: list[dict]) -> bytes:
    buf_g = np.frombuffer(surf_glow.get_data(), dtype=np.uint8).reshape((H, W, 4))
    img_g = Image.fromarray(buf_g[:, :, [2, 1, 0, 3]], mode="RGBA")

    # Dual-pass After-Effects-style Deep Glow Halation
    small_g = img_g.resize((W // 4, H // 4), Image.Resampling.BILINEAR)
    bloom_wide = small_g.filter(ImageFilter.GaussianBlur(radius=7.8)).resize((W, H), Image.Resampling.BILINEAR)
    bloom_core = small_g.filter(ImageFilter.GaussianBlur(radius=2.3)).resize((W, H), Image.Resampling.BILINEAR)

    buf_s = np.frombuffer(surf_sharp.get_data(), dtype=np.uint8).reshape((H, W, 4))
    img_s = Image.fromarray(buf_s[:, :, [2, 1, 0, 3]], mode="RGBA")

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    canvas.alpha_composite(bloom_wide)
    canvas.alpha_composite(bloom_core)
    canvas.alpha_composite(img_s)

    for sp, cx, cy, al in text_overlays:
        paste_center(canvas, sp, cx, cy, al)

    # Floating RTL Karaoke Subtitles (y = 1618)
    active_sub = None
    for sub in sub_lines:
        if sub["start"] <= t <= sub["end"]:
            active_sub = sub
            break

    if active_sub is not None:
        sub_al = clamp(min((t - active_sub["start"]) / 0.12, (active_sub["end"] - t) / 0.16))
        tokens = active_sub["tokens"]
        times  = active_sub["times"]

        cur_k = 0
        for k, ts in enumerate(times):
            if t >= ts - 0.03:
                cur_k = k

        full_txt = fa(active_sub["full"])
        if len(full_txt) <= 36:
            f_sub = fonts.med_42
        elif len(full_txt) <= 46:
            f_sub = fonts.med_38
        else:
            f_sub = fonts.med_34

        dd = ImageDraw.Draw(canvas)
        sp_w = dd.textlength(" ", font=f_sub, direction="rtl", language="fa")
        tok_fa = [fa(tok) for tok in tokens]
        tok_w  = [dd.textlength(tok, font=f_sub, direction="rtl", language="fa") for tok in tok_fa]
        total_w = sum(tok_w) + sp_w * max(0, len(tok_fa) - 1)

        # Safety scale if line exceeds 940px
        if total_w > 940 and f_sub is not fonts.med_34:
            f_sub = fonts.med_34
            sp_w = dd.textlength(" ", font=f_sub, direction="rtl", language="fa")
            tok_w = [dd.textlength(tok, font=f_sub, direction="rtl", language="fa") for tok in tok_fa]
            total_w = sum(tok_w) + sp_w * max(0, len(tok_fa) - 1)

        cur_right = 540.0 + total_w / 2.0
        sub_y = 1618

        for k, (tk, tw) in enumerate(zip(tok_fa, tok_w)):
            cx_tok = cur_right - tw / 2.0
            if k < cur_k:
                col, glw = (242, 242, 246, 255), 0.0
            elif k == cur_k:
                col, glw = (255, 255, 255, 255), 0.70
            else:
                col, glw = (76, 76, 84, 255), 0.0
            sp_tk = get_text_sprite(tk, f_sub, col, glow=glw)
            paste_center(canvas, sp_tk, cx_tok, sub_y, sub_al)
            cur_right -= (tw + sp_w)

    return canvas.convert("RGB").tobytes()
