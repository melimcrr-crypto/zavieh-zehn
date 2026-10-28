"""
Episode 08 — Studio v5.0 Deep-Glow Continuous-Camera Motion Test
Reference Style: Monochrome 4-Octave Optical Deep-Glow Minimalist Motion Graphics (https://pin.it/60JaKrUmI)
Topic: «آمپولِ بی‌حسیِ پرداخت» (Payment Anesthesia — Cash Pain vs. Installment Numbness)
Page: زاویه ذهن (@zavieh.penhann)

Key Studio v5.0 Architectural Features:
  1. Pure Zero-Clutter Canvas (#000000): Zero top/bottom HUD chrome, zero text-box walls —
     only luminous central monoline visual metaphors breathing in vast black space.
  2. True 32-Bit Float 4-Octave 'Deep Glow' Optical Halation + Reinhard Soft-Knee + Micro-Dither:
     Calibrated directly against the reference radial luminance curve (255 -> 129 -> 72 -> 45 -> 37).
  3. Continuous-Camera Transitions:
     - Blinking anatomical almond eye -> hypnotic spiral pupil zoom-in
     - Exponential S-curve horizontal & vertical whip-pans
     - Trim-Path stroke-draw & retract morphs
     - 6X Foreground Depth-of-Field (DoF) blurred zoom-through into 5x3 head grid + sniper reticle
     - Anatomical side-profile heads + interconnected cortical gyri + volumetric eye-beams + soundwaves
     - Orthogonal glowing circuit flowchart + 3D isometric cubes
  4. Raised Instagram-Safe Understated Subtitle (y = 1510.0, 0.00px baseline jitter, RTL feathered wipe)
     + Locked Signature Voice (Rasalgethi + 129-tap FIR + -0.34st) + High-Loudness Broadcast Master.
"""
import os, sys, math, time, subprocess
import cairocffi as cairo
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.engine.audio_master import build_episode_audio, LOCKED_SIGNATURE_VOICE
from src.engine.render_core import (
    W, H, FPS, FontBank, clamp, ease_out_cubic, ease_in_out_cubic,
    fa, get_fitted_text_sprite, rounded_rect_path, draw_star4
)
from src.engine.deep_glow_core import (
    DEEP_GLOW_SUB_Y, exp_in_out, set_trim_path, composite_deep_glow_frame,
    draw_blinking_spiral_eye, draw_anatomical_head_profile,
    draw_volumetric_beam, draw_mouth_soundwaves, draw_isometric_cube,
    draw_sniper_reticle, draw_neon_checkmark, draw_cursor_arrow_neon
)

from src.episodes.ep08_payment_anesthesia import SCRIPT_SEGMENTS, SFX_CUE_MAP


# =============================================================================
# HELPER VECTOR PRIMITIVES FOR PAYMENT ANESTHESIA DEEP-GLOW METAPHORS
# =============================================================================
def _draw_neon_banknote(ctx, cx: float, cy: float, w: float, h: float, angle: float = 0.0, alpha: float = 1.0, trim_p: float = 1.0):
    if alpha <= 0.01 or trim_p <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(angle)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    set_trim_path(ctx, 0.0, trim_p, (w + h) * 2.2)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.96)
    ctx.set_line_width(4.4)
    rounded_rect_path(ctx, -w * 0.5, -h * 0.5, w, h, 14.0)
    ctx.stroke()

    if trim_p > 0.45:
        ia = alpha * clamp((trim_p - 0.45) / 0.45)
        ctx.set_dash([])
        ctx.set_line_width(2.8)
        ctx.set_source_rgba(1, 1, 1, ia * 0.78)
        ctx.arc(0, 0, min(w, h) * 0.25, 0, 2 * math.pi)
        ctx.stroke()
        for sx in (-1, 1):
            ctx.move_to(sx * w * 0.36, -h * 0.24)
            ctx.line_to(sx * w * 0.36, h * 0.24)
            ctx.stroke()
    ctx.restore()


def _draw_neon_bank_card(ctx, cx: float, cy: float, w: float, h: float, angle: float = 0.0, alpha: float = 1.0, trim_p: float = 1.0):
    if alpha <= 0.01 or trim_p <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(angle)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    set_trim_path(ctx, 0.0, trim_p, (w + h) * 2.2)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.98)
    ctx.set_line_width(4.8)
    rounded_rect_path(ctx, -w * 0.5, -h * 0.5, w, h, 18.0)
    ctx.stroke()

    if trim_p > 0.4:
        ia = alpha * clamp((trim_p - 0.4) / 0.45)
        ctx.set_dash([])
        ctx.set_line_width(3.0)
        ctx.set_source_rgba(1, 1, 1, ia * 0.85)
        # EMV chip
        rounded_rect_path(ctx, -w * 0.36, -h * 0.14, w * 0.18, h * 0.26, 6.0)
        ctx.stroke()
        # Minimalist card number bars
        for k in range(4):
            bx = -w * 0.36 + k * (w * 0.19)
            ctx.move_to(bx, h * 0.26)
            ctx.line_to(bx + w * 0.13, h * 0.26)
            ctx.stroke()
    ctx.restore()


def _draw_neon_syringe(ctx, cx: float, cy: float, scale: float = 1.0, angle: float = -0.65, plunge_p: float = 0.4, alpha: float = 1.0, trim_p: float = 1.0):
    """Sleek architectural monoline anesthesia syringe along local +x axis (needle at +x)."""
    if alpha <= 0.01 or trim_p <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(angle)
    ctx.scale(scale, scale)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    set_trim_path(ctx, 0.0, trim_p, 920.0)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.98)
    ctx.set_line_width(4.6)

    # Barrel (-110 .. +80)
    rounded_rect_path(ctx, -110, -34, 190, 68, 10)
    ctx.stroke()
    # Finger flange at -110
    ctx.move_to(-110, -56); ctx.line_to(-110, 56); ctx.stroke()
    # Hub & needle (+80 .. +195)
    rounded_rect_path(ctx, 80, -14, 24, 28, 5); ctx.stroke()
    ctx.move_to(104, 0); ctx.line_to(195, 0); ctx.stroke()

    if trim_p > 0.45:
        ia = alpha * clamp((trim_p - 0.45) / 0.45)
        ctx.set_dash([])
        # Plunger rod pushing inward with plunge_p
        px = -185 + 68.0 * clamp(plunge_p)
        ctx.set_line_width(4.2)
        ctx.set_source_rgba(1, 1, 1, ia * 0.92)
        ctx.move_to(px, 0); ctx.line_to(px + 95, 0); ctx.stroke()
        ctx.move_to(px, -38); ctx.line_to(px, 38); ctx.stroke()
        ctx.move_to(px + 95, -28); ctx.line_to(px + 95, 28); ctx.stroke()

        # Measurement ticks on barrel
        ctx.set_line_width(2.4)
        ctx.set_source_rgba(1, 1, 1, ia * 0.72)
        for tx in (-70, -40, -10, 20, 50):
            ctx.move_to(tx, -34); ctx.line_to(tx, -16); ctx.stroke()
    ctx.restore()


def _draw_ecg_trace(ctx, cx: float, cy: float, w: float, amp: float, phase: float, alpha: float = 1.0):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.set_dash([])
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    steps = 120
    x0 = cx - w * 0.5
    ctx.new_path()
    for i in range(steps + 1):
        u = i / steps
        x = x0 + u * w
        # Travelling QRS heartbeat spike
        du = ((u - phase) % 1.0)
        if du > 0.5:
            du -= 1.0
        spike = 0.0
        if abs(du) < 0.08:
            s = du / 0.08
            spike = -math.sin(s * math.pi * 1.5) * math.exp(-s * s * 4.5) * amp
        y = cy + spike
        if i == 0:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.92)
    ctx.set_line_width(3.8)
    ctx.stroke()
    ctx.restore()


# =============================================================================
# CONTINUOUS TIMELINE BOUNDARIES (14 Deep-Glow Sequences + Smooth Whip/Morphs)
# =============================================================================
def _get_seq_bounds(tc: dict, total_dur: float) -> list[float]:
    outro_t0 = max(tc.get("c23_cta", total_dur - 6.0) + 2.2, total_dur - 4.0)
    raw = [
        0.0,
        tc["c02_pos"],       # S01: Blinking Spiral Eye -> Zoom into Trembling Cash + ECG
        tc["c03_scale"],     # S02: Whip-pan -> Contactless Card + 4 Floating Cubes
        tc["c04_scan"],      # S03: Two Overlapping Venn Circles (180-deg flip!)
        tc["c06_brake"],     # S04: Anatomical Head + Cortical Brain + Insula Pain Starburst
        tc["c07_brands"],    # S05: Neural Circuit Brake Clamping Runaway Coin
        tc["c08_syringe"],   # S06: Storefront Click -> 6X Foreground DoF Blur -> 15-Head Grid + Sniper Reticle
        tc["c09_oneclick"],  # S07: Giant Anesthesia Syringe Numbing Brain Pain Node
        tc["c10_split"],     # S08: Orthogonal 3-Branch Circuit Flowchart + 3D Isometric Cube
        tc["c11_four"],      # S09: Two Facing Anatomical Heads + Volumetric Beam + Soundwaves
        tc["c12_2x"],        # S10: 1M Isometric Cube Sliced by Laser into 4x 250 Cubes
        tc["c13_eat"],       # S11: Minimalist Neon Analytics Surge (1X vs 2X Spending)
        tc["c14_bnpl"],      # S12: 10 Orbiting Installment Cubes Draining Monthly Paycheck Orb
        tc["c16_anti1"],     # S13: "Buy Now Pay in 4 Months" Banner Sliced by Laser Cut
        tc["c18_anti2"],     # S14: Antidote 1 — 20s Manual Card Typing Waking Brain (5 Neural Stars)
        tc["c21_free"],      # S15: Antidote 2 — Head Vision Beam onto Cash Stack -> Syringe Crossed Out
        tc["c22_ask"],       # S16: Shattered Chains Around Tomorrow's Freedom Orb
        outro_t0,            # S17: Interactive Choice Orbs (1: Mindful vs 2: Installment Trap)
        total_dur,           # S18: Seamless Loop Outro — Blinking Spiral Eye + @zavieh.penhann
    ]
    # Enforce monotonic bounds
    out = [raw[0]]
    for v in raw[1:]:
        out.append(max(out[-1] + 0.4, float(v)))
    out[-1] = float(total_dur)
    return out


# =============================================================================
# MASTER CONTINUOUS-CAMERA SCENE RENDERER (Zero Clutter, Pure Deep-Glow Motion)
# =============================================================================
def render_deepglow_scene(
    t: float,
    total_dur: float,
    tc: dict,
    sub_lines: list[dict],
    fonts: FontBank,
    surf_core,
    ctx,
    surf_dof,
    ctx_dof,
) -> bytes:
    # Clear both surfaces to pure transparent black
    for c_clear in (ctx, ctx_dof):
        c_clear.save()
        c_clear.set_operator(cairo.OPERATOR_CLEAR)
        c_clear.paint()
        c_clear.restore()

    texts = []
    use_dof = False
    dof_blur = 0.0
    glow_gain = 1.0

    B = _get_seq_bounds(tc, total_dur)
    CY = 840.0  # Visual optical center safely above y=1510 subtitle!

    def _whip_x(t_now: float, t0: float, t1: float, w_dur: float = 0.38) -> tuple[float, float]:
        """Returns (dx_offset, alpha) for snappy horizontal S-curve whip-pan."""
        if t_now < t0 - w_dur or t_now > t1 + w_dur:
            return 0.0, 0.0
        dx = 0.0
        al = 1.0
        if t_now < t0 + w_dur * 0.5:
            u = clamp((t_now - (t0 - w_dur * 0.5)) / w_dur)
            e = exp_in_out(u)
            dx += (1.0 - e) * 980.0
            al *= clamp(u * 1.6)
        if t_now > t1 - w_dur * 0.5:
            u = clamp((t_now - (t1 - w_dur * 0.5)) / w_dur)
            e = exp_in_out(u)
            dx -= e * 980.0
            al *= clamp((1.0 - u) * 1.6)
        return dx, al

    # -------------------------------------------------------------------------
    # S01 (B[0]..B[1]): Blinking Almond Eye -> Spiral Pupil -> Zoom into Trembling Cash
    # -------------------------------------------------------------------------
    if t <= B[1] + 0.35:
        dur = B[1] - B[0]
        u = clamp((t - B[0]) / max(0.2, dur))
        _, al_exit = _whip_x(t, B[0] - 1.0, B[1], 0.40)
        dx_out = -exp_in_out(clamp((t - (B[1] - 0.20)) / 0.40)) * 980.0 if t > B[1] - 0.20 else 0.0

        # Phase A (0 .. 52% of S01): Blinking Spiral Eye (exact reference opening!)
        zoom_u = exp_in_out(clamp((u - 0.44) / 0.24))
        if zoom_u < 0.99:
            trim_eye = ease_out_cubic(clamp(t / 0.65))
            # Natural smooth blink at t = 0.95s
            blink = 1.0 - 0.92 * math.exp(-((t - 0.98) / 0.11) ** 2)
            spiral_p = ease_in_out_cubic(clamp((t - 0.85) / 0.95))
            eye_sc = 1.52 * (1.0 + 3.2 * zoom_u)
            eye_al = al_exit * (1.0 - clamp((zoom_u - 0.55) / 0.42))
            draw_blinking_spiral_eye(ctx, 540 + dx_out, CY, eye_sc, blink, spiral_p, t, eye_al, trim_eye)

        # Phase B (46% .. 100% of S01): Inside the pupil -> 3 Trembling Banknotes + Heartbeat ECG
        if zoom_u > 0.04:
            cash_al = al_exit * clamp((zoom_u - 0.04) / 0.45)
            tremor_x = math.sin(t * 46.0) * 5.5 * clamp((u - 0.55) * 3.0)
            tremor_y = math.cos(t * 39.0) * 3.5 * clamp((u - 0.55) * 3.0)
            sc_in = 0.45 + 0.55 * ease_out_cubic(zoom_u)
            for k, ang in enumerate((-0.18, 0.0, 0.18)):
                _draw_neon_banknote(
                    ctx,
                    540 + dx_out + tremor_x + (k - 1) * 34 * sc_in,
                    CY - 45 + tremor_y + abs(k - 1) * 14,
                    310 * sc_in, 155 * sc_in,
                    ang * sc_in,
                    cash_al * (0.65 if k != 1 else 0.98),
                    clamp(zoom_u * 1.4),
                )
            _draw_ecg_trace(ctx, 540 + dx_out, CY + 165, 420 * sc_in, 68.0, (t * 1.35) % 1.0, cash_al)
            sp = get_fitted_text_sprite("۱,۰۰۰,۰۰۰", fonts.bold_44, 320)
            texts.append((sp, 540 + dx_out + tremor_x, CY - 195, cash_al * 0.95))

    # -------------------------------------------------------------------------
    # S02 (B[1]..B[2]): Horizontal Whip-Pan -> Contactless Card + 4 Floating Cubes
    # -------------------------------------------------------------------------
    if B[1] - 0.35 <= t <= B[2] + 0.35:
        dx, al = _whip_x(t, B[1], B[2], 0.40)
        tl = max(0.0, t - B[1])
        dur = B[2] - B[1]
        u = clamp(tl / max(0.2, dur))
        trim_c = ease_out_cubic(clamp(tl / 0.55))

        # Sleek angled bank card on lower-left + radiating NFC waves
        card_x = 370 + dx
        card_y = CY + 65 + math.sin(t * 2.6) * 8.0
        _draw_neon_bank_card(ctx, card_x, card_y, 290, 182, -0.16, al, trim_c)

        # Concentric NFC contactless waves
        if tl > 0.35:
            wa = al * clamp((tl - 0.35) / 0.35)
            draw_mouth_soundwaves(ctx, card_x + 155, card_y - 45, +1, t * 1.15, wa)

        # 4 Weightless Isometric Installment Cubes drifting effortlessly up-right!
        for k in range(4):
            cu = ease_out_cubic(clamp((tl - 0.45 - k * 0.16) / 0.55))
            if cu > 0.02:
                cx_k = 640 + (k % 2) * 145 + dx
                cy_k = CY - 95 + (k // 2) * 145 - math.sin(t * 2.8 + k) * 9.0
                draw_isometric_cube(ctx, cx_k, cy_k, 48 * cu, al * cu, cu, False)

    # -------------------------------------------------------------------------
    # S03 (B[2]..B[3]): Overlapping Venn Circles + 180-Deg Orbital Flip (Ref t=11.3s!)
    # -------------------------------------------------------------------------
    if B[2] - 0.35 <= t <= B[3] + 0.25:
        tl = max(0.0, t - B[2])
        dur = B[3] - B[2]
        dx_in = (1.0 - exp_in_out(clamp((t - (B[2] - 0.20)) / 0.40))) * 980.0 if t < B[2] + 0.20 else 0.0
        # Exit via Trim-Path retraction (exact reference morph into Anatomical Head!)
        retract = exp_in_out(clamp((t - (B[3] - 0.38)) / 0.38))
        al = clamp((t - (B[2] - 0.20)) / 0.25) * (1.0 - retract * 0.95)
        trim_v = ease_out_cubic(clamp(tl / 0.65)) * (1.0 - retract)

        # 180-degree orbital rotation on segment 5 ("صد و هشتاد درجه فرق داره")
        flip_ang = exp_in_out(clamp((tl - dur * 0.46) / 0.85)) * math.pi
        sep = 132.0 * ease_out_cubic(clamp(tl / 0.70))
        vx1 = 540 + dx_in - math.cos(flip_ang) * sep
        vy1 = CY - math.sin(flip_ang) * sep * 0.52
        vx2 = 540 + dx_in + math.cos(flip_ang) * sep
        vy2 = CY + math.sin(flip_ang) * sep * 0.52

        ctx.save()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        set_trim_path(ctx, 0.0, trim_v, 2 * math.pi * 215)
        ctx.set_source_rgba(1, 1, 1, al * 0.98)
        ctx.set_line_width(6.2)
        ctx.arc(vx1, vy1, 215, 0, 2 * math.pi); ctx.stroke()
        ctx.arc(vx2, vy2, 215, 0, 2 * math.pi); ctx.stroke()
        ctx.restore()

        lbl_al = al * clamp((tl - 0.45) / 0.35) * (1.0 - retract * 1.4)
        if lbl_al > 0.02:
            texts.append((get_fitted_text_sprite("کارت و قسط", fonts.bold_36, 200), vx1 - math.cos(flip_ang) * 68, vy1, lbl_al))
            texts.append((get_fitted_text_sprite("پولِ نقد", fonts.bold_36, 200), vx2 + math.cos(flip_ang) * 68, vy2, lbl_al))
            texts.append((get_fitted_text_sprite("۱۸۰°", fonts.med_32, 120), 540 + dx_in, CY, lbl_al * clamp((tl - dur * 0.42) / 0.3)))

    # -------------------------------------------------------------------------
    # S04 (B[3]..B[4]): Large Anatomical Head + fMRI Scan + Insula Pain Starburst (Ref t=41.4s!)
    # -------------------------------------------------------------------------
    if B[3] - 0.15 <= t <= B[4] + 0.10:
        tl = max(0.0, t - B[3])
        retract = clamp((t - (B[4] - 0.25)) / 0.30)
        al = clamp(tl / 0.25) * (1.0 - retract)
        trim_h = ease_out_cubic(clamp(tl / 0.85))
        pain_t0 = tc.get("c05_pain", B[3] + (B[4] - B[3]) * 0.55)
        pain_u = clamp((t - pain_t0) / 0.32)

        draw_anatomical_head_profile(ctx, 540, CY, 1.58, -1, al, trim_h, 1.0, 2, t)

        # Horizontal fMRI scan line sweeping across cranium before pain ignition
        if 0.30 < tl < (pain_t0 - B[3] + 0.25):
            scan_u = ((tl - 0.30) / max(0.5, (pain_t0 - B[3] - 0.15))) % 1.0
            sy = CY - 265 + scan_u * 420.0
            ctx.save()
            ctx.set_dash([14.0, 10.0])
            ctx.move_to(260, sy); ctx.line_to(820, sy)
            ctx.set_source_rgba(1, 1, 1, al * 0.72 * math.sin(scan_u * math.pi))
            ctx.set_line_width(3.2); ctx.stroke()
            ctx.restore()

        # Anterior Insula Physical Pain Center Starburst + Shockwave Rings!
        if pain_u > 0.01:
            px, py = 540 - 18, CY - 118
            pulse = 1.0 + 0.22 * math.sin(t * 11.0)
            draw_star4(ctx, px, py, 44.0 * ease_out_cubic(pain_u) * pulse, al * 0.99)
            ctx.save()
            ctx.set_dash([])
            for ri in range(3):
                rp = ((t - pain_t0) * 1.45 + ri * 0.33) % 1.0
                ctx.arc(px, py, 24.0 + rp * 155.0, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 1, 1, al * (1.0 - rp) * 0.78 * pain_u)
                ctx.set_line_width(3.4); ctx.stroke()
            ctx.restore()
            texts.append((get_fitted_text_sprite("مرکزِ دردِ مغز", fonts.bold_36, 280), 540, CY + 335, al * pain_u * 0.95))

    # -------------------------------------------------------------------------
    # S05 (B[4]..B[5]): Neural Circuit Extending to Natural Brake Caliper Clamping Coin
    # -------------------------------------------------------------------------
    if B[4] - 0.15 <= t <= B[5] + 0.30:
        tl = max(0.0, t - B[4])
        _, al = _whip_x(t, B[4] - 0.6, B[5], 0.38)
        al *= clamp(tl / 0.25)
        dx_out = -exp_in_out(clamp((t - (B[5] - 0.19)) / 0.38)) * 980.0 if t > B[5] - 0.19 else 0.0

        # Upper mini anatomical head sending orthogonal brake signal downward
        draw_anatomical_head_profile(ctx, 540 + dx_out, CY - 230, 0.92, -1, al, 1.0, 0.95, 2, t)
        line_u = ease_out_cubic(clamp(tl / 0.55))
        ctx.save()
        set_trim_path(ctx, 0.0, line_u, 260.0)
        ctx.move_to(540 + dx_out, CY - 62); ctx.line_to(540 + dx_out, CY + 115)
        ctx.set_source_rgba(1, 1, 1, al * 0.94); ctx.set_line_width(4.8); ctx.stroke()
        ctx.restore()

        # Glowing coin at (540, CY + 210) clamped by twin symmetric brake jaws!
        clamp_u = exp_in_out(clamp((tl - 0.45) / 0.45))
        jaw_gap = 155.0 - 52.0 * clamp_u
        cx_b, cy_b = 540 + dx_out, CY + 215
        ctx.save()
        ctx.set_dash([])
        ctx.set_line_width(5.2)
        ctx.set_source_rgba(1, 1, 1, al * 0.98)
        ctx.arc(cx_b, cy_b, 74, 0, 2 * math.pi); ctx.stroke()
        # Left & right curved brake pads clamping inward
        ctx.set_line_width(8.5)
        ctx.arc(cx_b - (jaw_gap - 98), cy_b, 98, math.pi * 0.72, math.pi * 1.28); ctx.stroke()
        ctx.arc(cx_b + (jaw_gap - 98), cy_b, 98, -math.pi * 0.28, math.pi * 0.28); ctx.stroke()
        ctx.restore()
        texts.append((get_fitted_text_sprite("ترمزِ طبیعی", fonts.bold_36, 260), cx_b, cy_b + 148, al * clamp_u * 0.95))

    # -------------------------------------------------------------------------
    # S06 (B[5]..B[6]): Cursor Click + 6X FOREGROUND DOF ZOOM-THROUGH -> 15-Head Grid + Sniper Reticle!
    # -------------------------------------------------------------------------
    if B[5] - 0.30 <= t <= B[6] + 0.30:
        tl = max(0.0, t - B[5])
        dur = B[6] - B[5]
        dx_in = (1.0 - exp_in_out(clamp((t - (B[5] - 0.19)) / 0.38))) * 980.0 if t < B[5] + 0.19 else 0.0
        retract = clamp((t - (B[6] - 0.28)) / 0.30)
        al = clamp((t - (B[5] - 0.18)) / 0.22) * (1.0 - retract)

        # Transition trigger at 38% of S06: 6X Foreground DoF Pass-Through Zoom!
        zoom_u = exp_in_out(clamp((tl - dur * 0.34) / 0.68))

        # Foreground Brand Buy-Box + Neon Cursor Arrow -> switches to surf_dof as it zooms 8.5X past camera!
        if zoom_u < 0.96:
            fg_sc = 1.0 + 8.5 * zoom_u
            fg_al = al * (1.0 - clamp((zoom_u - 0.42) / 0.50))
            target_c = ctx_dof if zoom_u > 0.14 else ctx
            if zoom_u > 0.14:
                use_dof = True
                dof_blur = 6.0 + 38.0 * zoom_u

            target_c.save()
            target_c.translate(540 + dx_in, CY)
            target_c.scale(fg_sc, fg_sc)
            rounded_rect_path(target_c, -210, -135, 420, 270, 22)
            target_c.set_source_rgba(1, 1, 1, fg_al * 0.96)
            target_c.set_line_width(5.0 / max(1.0, fg_sc ** 0.55))
            target_c.stroke()
            rounded_rect_path(target_c, -125, 25, 250, 68, 34)
            target_c.stroke()
            cur_u = ease_out_cubic(clamp(tl / max(0.25, dur * 0.28)))
            draw_cursor_arrow_neon(target_c, 155 - 125 * cur_u, 145 - 88 * cur_u, 1.15, fg_al)
            target_c.restore()
            if zoom_u <= 0.14:
                texts.append((get_fitted_text_sprite("خریدِ هیجانی", fonts.bold_36, 230), 540 + dx_in, CY - 42, fg_al))

        # Background revealed through DoF blur: 5x3 Consumer Head Grid + Sniper Reticle + Checkmarks!
        if zoom_u > 0.10:
            grid_al = al * clamp((zoom_u - 0.10) / 0.45)
            grid_sc = 0.55 + 0.45 * ease_out_cubic(zoom_u)
            ctx.save()
            ctx.translate(540, CY)
            ctx.scale(grid_sc, grid_sc)
            ctx.translate(-540, -CY)
            for r in range(3):
                for col in range(5):
                    hx = 210 + col * 165
                    hy = CY - 220 + r * 220
                    idx = r * 5 + col
                    chk_t = dur * 0.62 + (idx % 4) * 0.11
                    if idx in (2, 6, 8, 12) and tl > chk_t:
                        pop = ease_out_cubic(clamp((tl - chk_t) / 0.24))
                        draw_neon_checkmark(ctx, hx, hy, 40, grid_al, pop)
                    else:
                        draw_anatomical_head_profile(ctx, hx, hy, 0.29, -1, grid_al * 0.88, 1.0, 0.55, 0, t)
                        if idx == 7:
                            ret_u = ease_out_cubic(clamp((tl - dur * 0.45) / 0.35))
                            draw_sniper_reticle(ctx, hx, hy, 70 * (1.35 - 0.35 * ret_u), t * 1.4, grid_al * ret_u)
            ctx.restore()

    # -------------------------------------------------------------------------
    # S07 (B[6]..B[7]): Giant Neon Anesthesia Syringe Injecting & Numbing Brain Pain Node!
    # -------------------------------------------------------------------------
    if B[6] - 0.25 <= t <= B[7] + 0.25:
        tl = max(0.0, t - B[6])
        dur = B[7] - B[6]
        u = clamp(tl / max(0.2, dur))
        al = clamp(tl / 0.25) * clamp((B[7] + 0.22 - t) / 0.26)
        trim_s = ease_out_cubic(clamp(tl / 0.60))
        plunge = ease_in_out_cubic(clamp((tl - 0.45) / max(0.4, dur * 0.55)))

        # Anatomical head on lower-left whose pain spark gets numbed from 1.0 -> 0.0!
        pain_fade = 1.0 - plunge
        draw_anatomical_head_profile(ctx, 430, CY + 95, 1.28, -1, al, trim_s, 0.95, int(round(3 * pain_fade)), t)
        if pain_fade > 0.05:
            draw_star4(ctx, 415, CY - 8, 34.0 * pain_fade, al * pain_fade)

        # Sleek diagonal anesthesia syringe injecting from upper-right directly into cranium!
        _draw_neon_syringe(ctx, 705 - 24 * plunge, CY - 165 + 20 * plunge, 1.12, math.pi * 0.76, plunge, al, trim_s)

        # Numbing mist rings expanding calmly inside cranium
        if plunge > 0.08:
            ctx.save()
            ctx.set_dash([10.0, 12.0])
            for k in range(2):
                mr = 35.0 + ((tl * 1.1 + k * 0.5) % 1.0) * 115.0
                ctx.arc(445, CY - 2, mr, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 1, 1, al * 0.55 * (1.0 - mr / 160.0))
                ctx.set_line_width(2.6); ctx.stroke()
            ctx.restore()

    # -------------------------------------------------------------------------
    # S08 (B[7]..B[8]): Orthogonal 3-Branch Circuit Flowchart + 3D Isometric Cube (Ref t=75.3s!)
    # -------------------------------------------------------------------------
    if B[7] - 0.20 <= t <= B[8] + 0.30:
        tl = max(0.0, t - B[7])
        dur = B[8] - B[7]
        dx_out = -exp_in_out(clamp((t - (B[8] - 0.19)) / 0.38)) * 980.0 if t > B[8] - 0.19 else 0.0
        al = clamp(tl / 0.26) * clamp((B[8] + 0.20 - t) / 0.25)
        trim_f = ease_out_cubic(clamp(tl / 0.75))

        ctx.save()
        ctx.translate(dx_out, 0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        set_trim_path(ctx, 0.0, trim_f, 1600.0)
        ctx.set_source_rgba(1, 1, 1, al * 0.96)
        ctx.set_line_width(5.0)

        # Top root box: آمپولِ بی‌حسی
        ctx.rectangle(340, 455, 400, 92); ctx.stroke()
        ctx.move_to(540, 547); ctx.line_to(540, 645); ctx.stroke()
        ctx.move_to(235, 645); ctx.line_to(845, 645); ctx.stroke()

        xs_b = [235, 540, 845]
        labels_b = ["کارتِ پلاستیکی", "تک‌کلیکی", "قسطِ بی‌کارمزد"]
        for i, bx in enumerate(xs_b):
            bu = ease_out_cubic(clamp((tl - 0.22 - i * 0.22) / 0.45))
            if bu > 0.02:
                ctx.set_dash([])
                ctx.set_source_rgba(1, 1, 1, al * bu * 0.96)
                ctx.move_to(bx, 645); ctx.line_to(bx, 720); ctx.stroke()
                ctx.rectangle(bx - 118, 720, 236, 86); ctx.stroke()
                ctx.move_to(bx, 806); ctx.line_to(bx, 885); ctx.stroke()
                texts.append((get_fitted_text_sprite(labels_b[i], fonts.reg_26, 206), bx + dx_out, 763, al * bu * 0.95))

        cube_u = ease_out_cubic(clamp((tl - 0.65) / 0.55))
        if cube_u > 0.02:
            ctx.move_to(235, 885); ctx.line_to(845, 885); ctx.stroke()
            ctx.move_to(540, 885); ctx.line_to(540, 975); ctx.stroke()
            draw_isometric_cube(ctx, 540, 1115, 108 * cube_u, al * cube_u, cube_u, True)
        ctx.restore()
        texts.append((get_fitted_text_sprite("آمپولِ بی‌حسی", fonts.med_36, 350), 540 + dx_out, 501, al * trim_f * 0.96))

    # -------------------------------------------------------------------------
    # S09 (B[8]..B[9]): Two Facing Anatomical Heads + Volumetric Beam + Soundwaves (Ref t=60.2s!)
    # -------------------------------------------------------------------------
    if B[8] - 0.30 <= t <= B[9] + 0.25:
        tl = max(0.0, t - B[8])
        dx_in = (1.0 - exp_in_out(clamp((t - (B[8] - 0.19)) / 0.38))) * 980.0 if t < B[8] + 0.19 else 0.0
        al = clamp((t - (B[8] - 0.18)) / 0.22) * clamp((B[9] + 0.18 - t) / 0.24)
        trim_p = ease_out_cubic(clamp(tl / 0.65))

        # Left head (Marketer speaking) + Mouth Soundwaves
        draw_anatomical_head_profile(ctx, 245 + dx_in, CY + 25, 1.04, +1, al * 0.95, trim_p, 0.85, 0, t)
        draw_mouth_soundwaves(ctx, 245 + dx_in + 112, CY + 68, +1, t, al * trim_p)

        # Right head (Buyer receiving instant dopamine spark + projecting volumetric vision beam!)
        draw_anatomical_head_profile(ctx, 835 + dx_in, CY + 25, 1.04, -1, al, trim_p, 0.98, 4, t)
        beam_u = ease_out_cubic(clamp((tl - 0.30) / 0.45))
        draw_volumetric_beam(ctx, 835 + dx_in - 79, CY - 27, math.pi - 0.48, 335 * beam_u, 0.22, al * 0.95 * beam_u)

        # Glowing Isometric Gift Cube illuminated inside the eye-beam!
        draw_isometric_cube(ctx, 540 + dx_in, CY + 135, 62 * beam_u, al * beam_u, beam_u, True)
        texts.append((get_fitted_text_sprite("لذتِ الان", fonts.bold_30, 180), 540 + dx_in, CY + 235, al * beam_u * 0.92))

        # Dotted timeline arc carrying the pain spark away to future months
        fut_u = ease_out_cubic(clamp((tl - 1.1) / 0.65))
        if fut_u > 0.02:
            ctx.save()
            ctx.set_dash([9.0, 9.0])
            ctx.move_to(540 + dx_in, CY - 165); ctx.line_to(540 + dx_in, CY - 275)
            ctx.set_source_rgba(1, 1, 1, al * fut_u * 0.72); ctx.set_line_width(3.0); ctx.stroke()
            ctx.restore()
            texts.append((get_fitted_text_sprite("دردِ ماه‌های بعد...", fonts.reg_26, 260), 540 + dx_in, CY - 310, al * fut_u * 0.85))

    # -------------------------------------------------------------------------
    # S10 (B[9]..B[10]): 1M Isometric Cube Sliced by Laser into 4x 250 Cubes!
    # -------------------------------------------------------------------------
    if B[9] - 0.20 <= t <= B[10] + 0.30:
        tl = max(0.0, t - B[9])
        dur = B[10] - B[9]
        dx_out = -exp_in_out(clamp((t - (B[10] - 0.19)) / 0.38)) * 980.0 if t > B[10] - 0.19 else 0.0
        al = clamp(tl / 0.22) * clamp((B[10] + 0.20 - t) / 0.24)
        split_u = exp_in_out(clamp((tl - 0.55) / 0.65))

        if split_u < 0.35:
            b_al = al * (1.0 - split_u / 0.35)
            draw_isometric_cube(ctx, 540 + dx_out, CY, 155, b_al, 1.0, False)
            texts.append((get_fitted_text_sprite("۱ میلیون", fonts.bold_44, 240), 540 + dx_out, CY + 215, b_al))

        # Diagonal laser slash flash at split moment
        if 0.42 < tl < 0.92:
            su = (tl - 0.42) / 0.50
            ctx.save()
            ctx.set_dash([])
            ctx.move_to(260 + dx_out, CY - 190); ctx.line_to(820 + dx_out, CY + 190)
            ctx.move_to(820 + dx_out, CY - 190); ctx.line_to(260 + dx_out, CY + 190)
            ctx.set_source_rgba(1, 1, 1, al * math.sin(su * math.pi) * 0.98)
            ctx.set_line_width(5.5); ctx.stroke()
            ctx.restore()

        if split_u > 0.15:
            s_al = al * clamp((split_u - 0.15) / 0.45)
            spread = 148.0 * split_u
            offsets = [(-spread, -spread), (spread, -spread), (-spread, spread), (spread, spread)]
            for idx_c, (ox, oy) in enumerate(offsets):
                bob = math.sin(t * 3.0 + idx_c * 1.4) * 7.0
                draw_isometric_cube(ctx, 540 + dx_out + ox, CY + oy + bob, 66, s_al, 1.0, False)
                texts.append((get_fitted_text_sprite("۲۵۰", fonts.bold_30, 110), 540 + dx_out + ox, CY + oy + bob + 94, s_al * 0.92))

    # -------------------------------------------------------------------------
    # S11 (B[10]..B[11]): Minimalist Neon Analytics Surge — 1X Cash vs 2X Numb Spending (Ref t=18.8s!)
    # -------------------------------------------------------------------------
    if B[10] - 0.30 <= t <= B[11] + 0.30:
        tl = max(0.0, t - B[10])
        dx, al = _whip_x(t, B[10], B[11], 0.38)
        boom_t = min(tc.get("c12_boom", B[10] + 1.2), B[10] + (B[11] - B[10]) * 0.35)
        u1 = ease_out_cubic(clamp(tl / 0.55))
        u2 = exp_in_out(clamp((t - (boom_t - 0.15)) / 0.55))

        base_y = CY + 235
        ctx.save()
        ctx.translate(dx, 0)
        ctx.set_dash([])
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgba(1, 1, 1, al * 0.95)
        ctx.set_line_width(5.0)
        # Clean horizontal axis
        ctx.move_to(210, base_y); ctx.line_to(870, base_y); ctx.stroke()

        # Bar 1: Cash (1X = 210px)
        h1 = 210.0 * u1
        rounded_rect_path(ctx, 305, base_y - h1, 140, max(6.0, h1), 12)
        ctx.stroke()

        # Bar 2: Numb Card/Installment (2X = 460px!) + Rising Trend Line & Arrow
        h2 = max(12.0, 210.0 * u1 + 260.0 * u2)
        rounded_rect_path(ctx, 635, base_y - h2, 140, h2, 12)
        ctx.stroke()

        if u2 > 0.08:
            ctx.set_line_width(4.4)
            ctx.move_to(260, base_y - 120)
            ctx.line_to(480, base_y - 220)
            ctx.line_to(705, base_y - h2 - 58)
            ctx.stroke()
            draw_star4(ctx, 705, base_y - h2 - 58, 26.0 * u2, al * 0.98)
        ctx.restore()

        texts.append((get_fitted_text_sprite("نقد (۱ برابر)", fonts.reg_26, 200), 375 + dx, base_y + 46, al * u1 * 0.92))
        texts.append((get_fitted_text_sprite("بی‌حس (۲ برابر)", fonts.bold_30, 230), 705 + dx, base_y + 46, al * max(0.3, u2) * 0.96))
        if u2 > 0.2:
            texts.append((get_fitted_text_sprite("۲ برابر خرج!", fonts.bold_44, 300), 705 + dx, base_y - h2 - 115, al * u2 * 0.98))

    # -------------------------------------------------------------------------
    # S12 (B[11]..B[12]): 10 Orbiting Installment Cubes Draining Monthly Paycheck Orb!
    # -------------------------------------------------------------------------
    if B[11] - 0.30 <= t <= B[12] + 0.25:
        tl = max(0.0, t - B[11])
        dur = B[12] - B[11]
        dx_in = (1.0 - exp_in_out(clamp((t - (B[11] - 0.19)) / 0.38))) * 980.0 if t < B[11] + 0.19 else 0.0
        al = clamp((t - (B[11] - 0.18)) / 0.22) * clamp((B[12] + 0.18 - t) / 0.24)
        drain_u = ease_in_out_cubic(clamp((tl - 0.45) / max(0.5, dur * 0.68)))

        # Center Paycheck Circle shrinking & draining as 10 installment nodes siphon it!
        orb_r = 128.0 * (1.0 - 0.62 * drain_u)
        ctx.save()
        ctx.translate(540 + dx_in, CY)
        set_trim_path(ctx, 0.0, max(0.08, 1.0 - 0.85 * drain_u), 2 * math.pi * orb_r)
        ctx.set_source_rgba(1, 1, 1, al * 0.96)
        ctx.set_line_width(6.0)
        ctx.arc(0, 0, orb_r, -math.pi * 0.5, 1.5 * math.pi); ctx.stroke()

        # 10 Orbiting Installment Mini-Cubes pulling inward with dashed siphon rays
        for k in range(10):
            ku = ease_out_cubic(clamp((tl - k * 0.07) / 0.35))
            if ku > 0.02:
                ang = k * (2.0 * math.pi / 10.0) + t * 0.55
                rad = 285.0 - 55.0 * drain_u
                kx, ky = math.cos(ang) * rad, math.sin(ang) * rad
                ctx.set_dash([6.0, 8.0])
                ctx.set_line_width(2.2)
                ctx.set_source_rgba(1, 1, 1, al * ku * 0.55)
                ctx.move_to(math.cos(ang) * (orb_r + 12), math.sin(ang) * (orb_r + 12))
                ctx.line_to(kx * 0.84, ky * 0.84); ctx.stroke()
                draw_isometric_cube(ctx, kx, ky, 26 * ku, al * ku * 0.94, 1.0, False)
        ctx.restore()
        texts.append((get_fitted_text_sprite("حقوقِ ماه", fonts.bold_30, 190), 540 + dx_in, CY, al * (1.0 - 0.55 * drain_u)))

    # -------------------------------------------------------------------------
    # S13 (B[12]..B[13]): "Buy Now, Pay in 4 Months" Neon Banner Sliced by Diagonal Laser!
    # -------------------------------------------------------------------------
    if B[12] - 0.20 <= t <= B[13] + 0.30:
        tl = max(0.0, t - B[12])
        cut_t = tc.get("c15_cut", B[12] + (B[13] - B[12]) * 0.52)
        cut_u = exp_in_out(clamp((t - cut_t) / 0.48))
        dx_out = -exp_in_out(clamp((t - (B[13] - 0.19)) / 0.38)) * 980.0 if t > B[13] - 0.19 else 0.0
        al = clamp(tl / 0.24) * clamp((B[13] + 0.20 - t) / 0.24)
        trim_b = ease_out_cubic(clamp(tl / 0.50))

        # Split offset along diagonal when cut_u > 0!
        sep = 42.0 * cut_u
        ctx.save()
        ctx.translate(540 + dx_out, CY - sep * 0.4)
        set_trim_path(ctx, 0.0, trim_b, 1400.0)
        rounded_rect_path(ctx, -310, -110, 620, 220, 24)
        ctx.set_source_rgba(1, 1, 1, al * (1.0 - 0.45 * cut_u))
        ctx.set_line_width(5.0); ctx.stroke()
        draw_cursor_arrow_neon(ctx, 235, 75 + sep, 1.1, al * (1.0 - cut_u))
        ctx.restore()

        texts.append((get_fitted_text_sprite("الان بخر، ۴ ماه دیگه بده!", fonts.bold_36, 540), 540 + dx_out, CY - sep * 0.4, al * (1.0 - 0.55 * cut_u)))

        # Razor-sharp diagonal laser slash neutralizing the trap!
        if t >= cut_t - 0.04:
            lu = ease_out_cubic(clamp((t - cut_t + 0.04) / 0.32))
            ctx.save()
            ctx.set_dash([])
            ctx.move_to(160 + dx_out, CY + 195)
            ctx.line_to(160 + dx_out + 760 * lu, CY + 195 - 390 * lu)
            ctx.set_source_rgba(1, 1, 1, al * 0.99)
            ctx.set_line_width(6.5); ctx.stroke()
            ctx.restore()

    # -------------------------------------------------------------------------
    # S14 (B[13]..B[14]): Antidote #1 — 20s Manual Card Typing Waking Up Cortical Brain!
    # -------------------------------------------------------------------------
    if B[13] - 0.30 <= t <= B[14] + 0.30:
        tl = max(0.0, t - B[13])
        dur = B[14] - B[13]
        dx, al = _whip_x(t, B[13], B[14], 0.38)
        u = clamp(tl / max(0.3, dur * 0.85))
        n_typed = int(round(u * 16))
        stars_awake = int(round(u * 5))

        # Top card slot box with 16 manual digits typing in one-by-one
        ctx.save()
        ctx.translate(dx, 0)
        ctx.set_dash([])
        rounded_rect_path(ctx, 210, CY - 305, 660, 120, 18)
        ctx.set_source_rgba(1, 1, 1, al * 0.95); ctx.set_line_width(4.6); ctx.stroke()
        for d in range(16):
            gx = 252 + d * 36 + (d // 4) * 14
            gy = CY - 245
            if d < n_typed:
                ctx.arc(gx, gy, 7.5, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 1, 1, al * 0.98); ctx.fill()
            else:
                ctx.move_to(gx - 8, gy + 12); ctx.line_to(gx + 8, gy + 12)
                ctx.set_source_rgba(1, 1, 1, al * 0.42); ctx.set_line_width(3.0); ctx.stroke()
        ctx.restore()

        # Anatomical head below waking up with all 5 twinkling cortical stars!
        draw_anatomical_head_profile(ctx, 540 + dx, CY + 105, 1.32, -1, al, 1.0, 1.0, stars_awake, t)
        sec_num = fa(min(20, max(1, int(round(u * 20)))))
        texts.append((get_fitted_text_sprite(f"{sec_num} ثانیه تایپ", fonts.bold_36, 280), 540 + dx, CY - 365, al * 0.96))

    # -------------------------------------------------------------------------
    # S15 (B[14]..B[15]): Antidote #2 — Vision Beam onto Cash Stack -> Syringe Crossed Out!
    # -------------------------------------------------------------------------
    if B[14] - 0.30 <= t <= B[15] + 0.25:
        tl = max(0.0, t - B[14])
        dx_in = (1.0 - exp_in_out(clamp((t - (B[14] - 0.19)) / 0.38))) * 980.0 if t < B[14] + 0.19 else 0.0
        al = clamp((t - (B[14] - 0.18)) / 0.22) * clamp((B[15] + 0.18 - t) / 0.24)
        stamp_t = tc.get("c20_stamp", B[14] + (B[15] - B[14]) * 0.62)
        stamp_u = exp_in_out(clamp((t - stamp_t) / 0.38))

        # Right anatomical head examining real cash stack with volumetric eye-beam!
        draw_anatomical_head_profile(ctx, 795 + dx_in, CY + 30, 1.18, -1, al, 1.0, 0.96, 3, t)
        beam_u = ease_out_cubic(clamp(tl / 0.45))
        draw_volumetric_beam(ctx, 795 + dx_in - 90, CY - 28, math.pi - 0.36, 390 * beam_u, 0.23, al * 0.92 * beam_u)

        if stamp_u < 0.85:
            c_al = al * (1.0 - stamp_u * 0.95)
            for k in range(3):
                _draw_neon_banknote(ctx, 315 + dx_in + (k - 1) * 18, CY + 115 - k * 16, 250, 126, -0.08 + k * 0.06, c_al, beam_u)
            texts.append((get_fitted_text_sprite("نقد می‌خریدی؟", fonts.bold_36, 280), 315 + dx_in, CY + 245, c_al * beam_u))

        if stamp_u > 0.08:
            s_al = al * clamp((stamp_u - 0.08) / 0.35)
            sx_c, sy_c = 325 + dx_in, CY + 95
            _draw_neon_syringe(ctx, sx_c, sy_c, 0.72, -0.55, 0.5, s_al * 0.85, 1.0)
            ctx.save()
            ctx.set_dash([])
            ctx.set_source_rgba(1, 1, 1, s_al * 0.98); ctx.set_line_width(6.2)
            ctx.arc(sx_c, sy_c, 138, 0, 2 * math.pi); ctx.stroke()
            ctx.move_to(sx_c - 96, sy_c + 96); ctx.line_to(sx_c + 96, sy_c - 96); ctx.stroke()
            ctx.restore()
            texts.append((get_fitted_text_sprite("اثرِ بی‌حسی!", fonts.bold_36, 260), sx_c, sy_c + 195, s_al))

    # -------------------------------------------------------------------------
    # S16 (B[15]..B[16]): Shattered Installment Chains Freeing Tomorrow's Luminous Orb!
    # -------------------------------------------------------------------------
    if B[15] - 0.20 <= t <= B[16] + 0.22:
        tl = max(0.0, t - B[15])
        al = clamp(tl / 0.22) * clamp((B[16] + 0.18 - t) / 0.22)
        burst = ease_out_cubic(clamp(tl / 0.75))

        ctx.save()
        ctx.translate(540, CY)
        ctx.set_dash([])
        ctx.set_source_rgba(1, 1, 1, al * 0.98); ctx.set_line_width(6.0)
        ctx.arc(0, 0, 135 * (0.82 + 0.18 * burst), 0, 2 * math.pi); ctx.stroke()
        draw_star4(ctx, 0, 0, 42 * burst, al * 0.96)

        # Shattered chain links flying outward radially!
        for k in range(6):
            ang = k * (math.pi / 3.0) + 0.25
            dist = 155.0 + 185.0 * burst
            lx, ly = math.cos(ang) * dist, math.sin(ang) * dist
            ctx.save()
            ctx.translate(lx, ly); ctx.rotate(ang + burst * 1.2)
            rounded_rect_path(ctx, -32, -16, 64, 32, 16)
            ctx.set_source_rgba(1, 1, 1, al * (1.0 - 0.65 * burst))
            ctx.set_line_width(4.2); ctx.stroke()
            ctx.restore()
        ctx.restore()
        texts.append((get_fitted_text_sprite("آزادیِ فردا", fonts.bold_36, 240), 540, CY + 215, al * burst * 0.95))

    # -------------------------------------------------------------------------
    # S17 (B[16]..B[17]): Interactive Choice Orbs — ۱ (Mindful) vs ۲ (Installment Trap)
    # -------------------------------------------------------------------------
    if B[16] - 0.20 <= t <= B[17] + 0.25:
        tl = max(0.0, t - B[16])
        al = clamp(tl / 0.24) * clamp((B[17] + 0.18 - t) / 0.26)
        u1 = ease_out_cubic(clamp(tl / 0.50))
        u2 = ease_out_cubic(clamp((tl - 0.35) / 0.50))

        ctx.save()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        # Right choice (RTL #1): حساب‌شده + Neon Checkmark
        set_trim_path(ctx, 0.0, u1, 2 * math.pi * 155)
        ctx.set_source_rgba(1, 1, 1, al * 0.98); ctx.set_line_width(5.8)
        ctx.arc(745, CY - 25, 155, 0, 2 * math.pi); ctx.stroke()
        draw_neon_checkmark(ctx, 745, CY - 75, 42, al * u1, u1)

        # Left choice (RTL #2): اسیرِ قسط + Hypnotic Spiral
        set_trim_path(ctx, 0.0, u2, 2 * math.pi * 155)
        ctx.set_source_rgba(1, 1, 1, al * 0.98); ctx.set_line_width(5.8)
        ctx.arc(335, CY - 25, 155, 0, 2 * math.pi); ctx.stroke()
        if u2 > 0.2:
            ctx.set_dash([])
            ctx.new_path()
            for si in range(75):
                su = si / 74.0
                ang = su * 2.8 * 2 * math.pi - t * 4.0
                rr = su * 44.0
                px, py = 335 + math.cos(ang) * rr, (CY - 75) + math.sin(ang) * rr
                if si == 0:
                    ctx.move_to(px, py)
                else:
                    ctx.line_to(px, py)
            ctx.set_source_rgba(1, 1, 1, al * u2 * 0.92); ctx.set_line_width(3.4); ctx.stroke()
        ctx.restore()

        if u1 > 0.2:
            texts.append((get_fitted_text_sprite("۱", fonts.eb_68, 120), 745, CY + 38, al * u1))
            texts.append((get_fitted_text_sprite("حساب‌شده", fonts.bold_36, 240), 745, CY + 195, al * u1 * 0.95))
        if u2 > 0.2:
            texts.append((get_fitted_text_sprite("۲", fonts.eb_68, 120), 335, CY + 38, al * u2))
            texts.append((get_fitted_text_sprite("اسیرِ قسط", fonts.bold_36, 240), 335, CY + 195, al * u2 * 0.95))

    # -------------------------------------------------------------------------
    # S18 (B[17]..total_dur): Seamless Loop Outro — Blinking Spiral Eye + @zavieh.penhann
    # -------------------------------------------------------------------------
    if t >= B[17] - 0.15:
        tl = max(0.0, t - B[17])
        dur = max(0.5, total_dur - B[17])
        al = clamp(tl / 0.35) * clamp((total_dur - t + 0.08) / 0.35)
        trim_o = ease_out_cubic(clamp(tl / 0.65))
        blink = 1.0 - 0.90 * math.exp(-((tl - dur * 0.58) / 0.12) ** 2)

        draw_blinking_spiral_eye(ctx, 540, CY - 55, 1.48, blink, 0.95, t, al, trim_o)
        brand_al = al * ease_out_cubic(clamp((tl - 0.25) / 0.45))
        texts.append((get_fitted_text_sprite("زاویه ذهن", fonts.bold_52, 420), 540, CY + 165, brand_al * 0.98))
        texts.append((get_fitted_text_sprite("@zavieh.penhann", fonts.med_32, 420), 540, CY + 235, brand_al * 0.85))

    return composite_deep_glow_frame(
        surf_core=surf_core,
        text_overlays=texts,
        fonts=fonts,
        t=t,
        sub_lines=sub_lines,
        surf_dof=(surf_dof if use_dof else None),
        dof_blur_px=dof_blur,
        glow_gain=glow_gain,
    )


# =============================================================================
# MULTIPROCESSING CLOUD WORKER + QA VERIFICATION SHEETS
# =============================================================================
_W_FONTS = None
_W_META = None
_W_SC = None
_W_CC = None
_W_SD = None
_W_CD = None


def _worker_init(font_dir: str, meta: dict):
    global _W_FONTS, _W_META, _W_SC, _W_CC, _W_SD, _W_CD
    _W_FONTS = FontBank(font_dir)
    _W_META = meta
    _W_SC = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CC = cairo.Context(_W_SC)
    _W_SD = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CD = cairo.Context(_W_SD)


def _worker_render_frame(fn: int) -> bytes:
    t = fn / float(FPS)
    return render_deepglow_scene(
        t, _W_META["total_dur"], _W_META["t_cues"], _W_META["sub_lines"],
        _W_FONTS, _W_SC, _W_CC, _W_SD, _W_CD
    )


def save_qa_sheets(font_dir: str, meta: dict, qa_dir: str):
    """Generates 18-sequence storyboard grid, 6X DoF transition strip, and y=1510 subtitle strip."""
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    sc = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cc = cairo.Context(sc)
    sd = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cd = cairo.Context(sd)

    tc = meta["t_cues"]
    td = meta["total_dur"]
    B = _get_seq_bounds(tc, td)

    # 1. 18-Sequence Storyboard Contact Sheet (6x3)
    pw, ph = 300, 533
    grid18 = Image.new("RGB", (pw * 6, ph * 3), (0, 0, 0))
    for i in range(18):
        ts = 0.5 * (B[i] + B[i + 1])
        if i == 0:
            ts = B[0] + (B[1] - B[0]) * 0.28  # Spiral Eye hero
        elif i == 3:
            ts = tc.get("c05_pain", ts) + 0.35
        elif i == 5:
            ts = B[5] + (B[6] - B[5]) * 0.78  # 15-Head Grid + Sniper Reticle
        raw = render_deepglow_scene(ts, td, tc, meta["sub_lines"], fonts, sc, cc, sd, cd)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw, ph), Image.Resampling.LANCZOS)
        r, c = divmod(i, 6)
        grid18.paste(im, (c * pw, r * ph))
    grid18.save(os.path.join(qa_dir, "storyboard_18_deepglow.png"))

    # 2. 6-Frame 6X Foreground DoF Zoom-Through Strip (S06 transition!)
    dof_strip = Image.new("RGB", (pw * 6, ph), (0, 0, 0))
    t_dof_start = B[5] + (B[6] - B[5]) * 0.30
    for k in range(6):
        tk = t_dof_start + k * 0.16
        raw = render_deepglow_scene(tk, td, tc, meta["sub_lines"], fonts, sc, cc, sd, cd)
        im = Image.frombytes("RGB", (W, H), raw).resize((pw, ph), Image.Resampling.LANCZOS)
        dof_strip.paste(im, (k * pw, 0))
    dof_strip.save(os.path.join(qa_dir, "dof_zoom_transition_strip.png"))

    # 3. Raised Minimalist Subtitle Baseline Strip (y = 1510.0)
    sub_strip = Image.new("RGB", (920, 12 * 100), (0, 0, 0))
    test_ln = meta["sub_lines"][min(4, len(meta["sub_lines"]) - 1)]
    t0_s = test_ln["times"][0]
    crop_y0 = int(round(DEEP_GLOW_SUB_Y - 58))
    for k in range(12):
        tk = t0_s + k * 0.09
        raw = render_deepglow_scene(tk, td, tc, meta["sub_lines"], fonts, sc, cc, sd, cd)
        im = Image.frombytes("RGB", (W, H), raw)
        crop = im.crop((80, crop_y0, 1000, crop_y0 + 100))
        for x in range(36):
            crop.putpixel((x, 58), (0, 220, 90))
            crop.putpixel((919 - x, 58), (0, 220, 90))
        sub_strip.paste(crop, (0, k * 100))
    sub_strip.save(os.path.join(qa_dir, "subtitle_strip_deepglow.png"))


def run_cloud_render(font_dir: str, work_dir: str, out_mp4: str, qa_dir: str, whisper_size: str = "medium"):
    import multiprocessing as mp
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(qa_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)

    print("=== [1/3] Building Studio v5.0 Master Audio (Locked Rasalgethi + Velvet Score + Foley) ===", flush=True)
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
    print(f"=== [2/3] Rendering {total_frames} Deep-Glow frames @ {W}x{H} {FPS}fps on {workers} CPU cores (CRF 14) ===", flush=True)

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

    with mp.Pool(processes=workers, initializer=_worker_init, initargs=(font_dir, meta), maxtasksperchild=400) as pool:
        for fn, rgb_bytes in enumerate(pool.imap(_worker_render_frame, range(total_frames), chunksize=10)):
            proc.stdin.write(rgb_bytes)
            if fn % 360 == 0 or fn == total_frames - 1:
                el = time.time() - t0
                print(f"  Frame {fn+1:4d}/{total_frames} ({(fn+1)/total_frames*100:5.1f}%) | {(fn+1)/max(0.01,el):5.1f} fps", flush=True)

    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg exited with code {rc}")

    print("=== [3/3] Generating Deep-Glow 18-Sequence & DoF Transition QA Sheets ===", flush=True)
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
            whisper_size=(sys.argv[6] if len(sys.argv) > 6 else "medium"),
        )
    else:
        print("Usage: python src/episodes/ep08_deepglow_test.py --cloud-render <fonts> <work> <out.mp4> <qa_dir> [whisper_size]")
