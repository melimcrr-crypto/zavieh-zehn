"""
Studio v7.0 Blogger Pro Motion-Edit Engine — Client Reel: DentEye (دنت‌آی) • Aidite Rapid 5
=============================================================================================
Host: Milad Keramatipour (میلاد کرامتی‌پور) | Brand: DentEye (دنت‌آی)
Product: Aidite Rapid 5 Intraoral 3D Dental Scanner (اورال اسکنر آیدایت مدل Rapid 5)

Key Blogger Retention-Editing Upgrades Applied:
1. Smart Studio Reframe & Seamless Softbox Removal on Talking-Head Shots (0..32.13s)
   + Dynamic Keyframed Blogger Camera Zooms & Authority Punch-Ins.
2. Automatic 90° CCW Widescreen Restoration (1428x804 upright!) for sideways laptop
   dental software & live 3D intraoral arch scan shots (74.47..88.27s & 94.27..122.43s)
   inside a sleek Dark-Glass Medical Studio Monitor Frame.
3. Clean Dark-Glass Showcase Framing for harsh white PDF spec pages (63.70..68.97s & 88.27..94.27s).
4. 14 Context-Synced Glassmorphic Blogger Motion Graphics Overlays (Host Lower-Third,
   Niche Hook Banner, Product Hero Card, DentEye QC Shield, Interactive 4-Item Unboxing
   Checklist, 100x Autoclave Badge, 162g & 25mm Spec Cards, Calibration-Free Card,
   25s/60s Scan Speed HUD, 10µm/20µm Precision HUD, Soft-Tissue AI Card, 3-Pillar Summary,
   and High-Converting Instagram Comment CTA Card: «آیدایت»).
5. CapCut Pro / Iman-Gadzhi-Style Word-by-Word Active Highlight Pill Subtitles in
   Instagram-Safe Zone (y=1495) powered by faster-whisper word timestamps + Domain Dictionary.
6. Studio Vocal Enhancement (-31.9dB raw phone mic -> -14.2dB warm broadcast master)
   + Subtle Sidechain-Ducked Tech-Minimal Beat + 20 Synchronized Foley SFX.
"""
import os, sys, re, math, json, wave, shutil, subprocess, urllib.request
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.signal import butter, filtfilt
import cairocffi as cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.engine.render_core import (
    W, H, FontBank, fa, clamp, ease_out_cubic, ease_in_out_cubic, spring_pop, window_fade
)

FPS_EDIT = 30
RAW_W, RAW_H = 804, 1428

RAW_PRIMARY_URL = "https://github.com/melimcrr-crypto/zavieh-zehn/releases/download/client-raw-denteye/raw_client_denteye.mp4"
RAW_FALLBACK_URL = "https://tempfile.org/JGCj2Vqc8kq/download"

# Exact frame-verified cut timestamps (30.00 fps)
F_TH_CUT     = 383   # 12.767s: Talking Head 1 -> Talking Head 2
F_UNBOX_1    = 964   # 32.133s: Talking Head 2 -> Open Case B-Roll
F_UNBOX_2    = 1097  # 36.567s: Stand Box
F_UNBOX_3    = 1224  # 40.800s: Scanner on Stand
F_UNBOX_4    = 1267  # 42.233s: USB Flash Drive
F_UNBOX_5    = 1350  # 45.000s: 4 Scan Tips in Hand
F_MACRO_HEAD = 1622  # 54.067s: Macro Scanner Optical Tip (100x Autoclave)
F_BODY_162G  = 1738  # 57.933s: Sleek Handheld Body (162g)
F_SPEC_TBL   = 1911  # 63.700s: White Spec Table Screenshot
F_SPEC_25MM  = 1980  # 66.000s: White 25mm DoF Brochure Page
F_CASE_CAL   = 2069  # 68.967s: Scanner in Case (Calibration-Free)
F_SW_ORDER   = 2234  # 74.467s: Sideways 90° Software Order Screen (Aidite | DENTEYE A)
F_SPEC_10UM  = 2648  # 88.267s: White 10µm Precision Brochure Page
F_SW_SCAN3D  = 2828  # 94.267s: Sideways 90° Real-Time 3D Intraoral Arch Scan -> End (3673)

# Palette
CYAN_RGB  = (46, 212, 255)
GREEN_RGB = (72, 250, 148)
AMBER_RGB = (255, 202, 68)
WHITE_RGB = (248, 252, 255)
DARK_TXT  = (7, 14, 26, 255)

POWER_KEYWORDS = {
    "دنت‌آی", "کرامتی‌پور", "میلاد", "آیدایت", "رپید", "فایو",
    "استوک", "فیلترهای", "سلامت", "کیفیت", "استند", "فلش", "چهار",
    "اتوکلاو", "۱۰۰", "سبک", "۱۶۲", "۲۵", "کالیبراسیون",
    "سرعت", "۶۰", "دقت", "۱۰", "۲۰", "میکرون", "بافت‌های", "کامنت", "قیمت"
}

# Domain dictionary post-normalizer for 100% typo-free Whisper Persian output
ORTHO_FIXES = [
    (r"دنت\s*آی\s*ای|دنت\s*آی\s*هست|دنت\s*آیه", lambda m: "دنت‌آی هست" if "هست" in m.group(0) else "دنت‌آیه"),
    (r"دنت\s*آی|دنتای|دنت‌آی‌ای", "دنت‌آی"),
    (r"کرامتی\s+پور", "کرامتی‌پور"),
    (r"آی\s*دایت|آی\s*دیت|آیدیت|ایدایت", "آیدایت"),
    (r"رپید\s*فایب|رپیدفایو|رپید\s*۵|رپید\s*5", "رپید فایو"),
    (r"فول\s*آرش|فول\s*ارچ", "فول‌آرچ"),
    (r"سینگل\s*کرون|سینگل\s*کراون", "سینگل‌کراون"),
    (r"اتو\s*کلاو", "اتوکلاو"),
    (r"میلی\s+متری", "میلی‌متری"),
    (r"میلی\s+متر", "میلی‌متر"),
    (r"۱۶۰\s*گرم|160\s*گرم", "۱۶۲ گرم"),
    (r"فیلتر\s+های", "فیلترهای"),
    (r"برخوردارره", "برخورداره"),
    (r"فلترهای", "فیلترهای"),
]


def normalize_persian_transcript_words(raw_words: list) -> list:
    """Applies domain orthography fixes while preserving exact acoustic word timestamps."""
    if not raw_words:
        return []
    # First normalize individual tokens
    cleaned = []
    i = 0
    n = len(raw_words)
    while i < n:
        w = raw_words[i]["word"].strip()
        s = raw_words[i]["start"]
        e = raw_words[i]["end"]
        # Check 2-word compound merges (e.g., "دنت" + "آی", "آی" + "دایت", "کرامتی" + "پور")
        if i + 1 < n:
            w2 = raw_words[i + 1]["word"].strip()
            pair = f"{w} {w2}"
            merged = None
            if re.fullmatch(r"دنت\s*(آی|ای|آیه|آی‌ای)", pair):
                merged = "دنت‌آیه" if pair.endswith("ه") else "دنت‌آی"
            elif re.fullmatch(r"(آی|ای)\s*(دایت|دیت)", pair):
                merged = "آیدایت"
            elif re.fullmatch(r"کرامتی\s*پور[\.،؟!]*", pair):
                merged = "کرامتی‌پور"
            elif re.fullmatch(r"اتو\s*کلاو[\.،؟!]*", pair):
                merged = "اتوکلاو"
            elif re.fullmatch(r"میلی\s*متری[\.،؟!]*", pair):
                merged = "میلی‌متری"
            if merged:
                cleaned.append({"word": fa(merged), "start": s, "end": raw_words[i + 1]["end"]})
                i += 2
                continue

        w = fa(w)
        for pat, rep in ORTHO_FIXES:
            w = re.sub(pat, rep, w)
        if w:
            cleaned.append({"word": w, "start": s, "end": e})
        i += 1

    # Fix "۱۶۰" -> "۱۶۲" if followed by "گرم"
    for k in range(len(cleaned) - 1):
        if cleaned[k]["word"] in ("۱۶۰", "160") and "گرم" in cleaned[k + 1]["word"]:
            cleaned[k]["word"] = "۱۶۲"
    return cleaned


def group_into_blogger_phrases(words: list) -> list:
    """Groups word-timed tokens into snappy 3..5-word blogger caption pills."""
    phrases = []
    cur = []
    for idx, wd in enumerate(words):
        cur.append(wd)
        wtxt = wd["word"]
        char_len = sum(len(x["word"]) for x in cur) + max(0, len(cur) - 1)
        next_gap = (words[idx + 1]["start"] - wd["end"]) if (idx + 1 < len(words)) else 9.0
        ends_punct = any(wtxt.endswith(p) for p in (".", "،", "؛", "؟", "!", ":"))

        if len(cur) >= 5 or char_len >= 27 or next_gap >= 0.34 or (ends_punct and len(cur) >= 2):
            phrases.append({
                "start": round(cur[0]["start"], 3),
                "end": round(max(cur[-1]["end"] + min(0.24, max(0.04, next_gap - 0.04)), cur[0]["start"] + 0.45), 3),
                "words": cur,
                "full": " ".join(x["word"] for x in cur),
            })
            cur = []
    if cur:
        phrases.append({
            "start": round(cur[0]["start"], 3),
            "end": round(cur[-1]["end"] + 0.30, 3),
            "words": cur,
            "full": " ".join(x["word"] for x in cur),
        })
    return phrases


# =============================================================================
# STUDIO AUDIO ENHANCEMENT + TECH-MINIMAL BEAT + BLOGGER FOLEY SFX
# =============================================================================
def _synth_blogger_music_and_sfx(dur_sec: float, voice_env_48k: np.ndarray, sr: int = 48000) -> np.ndarray:
    """
    Synthesizes a warm, modern tech-blogger minimal background groove (-24dB, sidechain ducked)
    plus 20 crisp glass/whoosh/pop/tick/chime Foley cues synced to cuts & UI pop-ups.
    """
    n = int(dur_sec * sr)
    t = np.arange(n, dtype=np.float64) / sr
    mix_l = np.zeros(n, dtype=np.float64)
    mix_r = np.zeros(n, dtype=np.float64)

    # 1. Warm Rhodes/Pad Chord Progression (Am9 -> Fmaj7 -> Cmaj9 -> G6, 8s per bar group)
    chords = [
        [110.0, 220.0, 261.63, 329.63, 392.00, 493.88],
        [87.31, 174.61, 220.00, 261.63, 329.63, 440.00],
        [130.81, 196.00, 246.94, 293.66, 392.00],
        [98.00, 196.00, 246.94, 293.66, 329.63],
    ]
    bar_len = 4.0
    total_bars = int(math.ceil(dur_sec / bar_len))
    for b in range(total_bars):
        i0 = int(b * bar_len * sr)
        i1 = min(n, int((b + 1.15) * bar_len * sr))
        if i0 >= n:
            break
        lt = np.arange(i1 - i0, dtype=np.float64) / sr
        env = np.clip(lt / 0.45, 0.0, 1.0) * np.exp(-lt * 0.42)
        notes = chords[b % len(chords)]
        ch_l = np.zeros_like(lt)
        ch_r = np.zeros_like(lt)
        for ni, f in enumerate(notes):
            s1 = np.sin(2 * np.pi * f * lt) + 0.22 * np.sin(2 * np.pi * f * 2.0 * lt) * np.exp(-lt * 1.8)
            pan = 0.35 + 0.30 * ((ni % 3) / 2.0)
            ch_l += s1 * (1.0 - pan * 0.45)
            ch_r += s1 * (0.55 + pan * 0.45)
        mix_l[i0:i1] += ch_l * env * 0.015
        mix_r[i0:i1] += ch_r * env * 0.015

    # Subtle 112-BPM soft muted pulse kick/tick for modern tech-review energy
    beat_dt = 60.0 / 112.0
    n_beats = int(dur_sec / beat_dt)
    for bi in range(n_beats):
        ib = int(bi * beat_dt * sr)
        ln = min(int(0.11 * sr), n - ib)
        if ln <= 64:
            continue
        bt = np.arange(ln, dtype=np.float64) / sr
        if bi % 2 == 0:
            f_sw = 52.0 + 68.0 * np.exp(-bt * 42.0)
            pulse = np.sin(2 * np.pi * np.cumsum(f_sw) / sr) * np.exp(-bt * 26.0) * 0.026
            mix_l[ib:ib + ln] += pulse
            mix_r[ib:ib + ln] += pulse
        else:
            hat = np.random.default_rng(bi + 77).normal(0, 1, ln) * np.exp(-bt * 95.0) * 0.0045
            mix_l[ib:ib + ln] += hat * 0.9
            mix_r[ib:ib + ln] += hat * 1.1

    # Sidechain duck music under Milad's voice
    duck = 1.0 - 0.58 * np.clip(voice_env_48k[:n] * 3.5, 0.0, 1.0)
    fade_out = np.clip((dur_sec - t) / 1.2, 0.0, 1.0)
    mix_l *= duck * fade_out
    mix_r *= duck * fade_out

    # 2. Blogger Foley SFX Cues (Whoosh, Glass Pop, Check Tick, Chime)
    def add_pop(ts: float, freq: float = 780.0, gain: float = 0.085):
        i0 = int(ts * sr)
        ln = min(int(0.085 * sr), n - i0)
        if i0 < 0 or ln <= 64:
            return
        pt = np.arange(ln, dtype=np.float64) / sr
        f_c = freq * (0.68 + 0.55 * (1.0 - np.exp(-pt * 55.0)))
        sig = np.sin(2 * np.pi * np.cumsum(f_c) / sr) * np.exp(-pt * 44.0) * gain
        mix_l[i0:i0 + ln] += sig
        mix_r[i0:i0 + ln] += sig * 0.96

    def add_whoosh(ts: float, dur_w: float = 0.28, gain: float = 0.070):
        i0 = max(0, int((ts - dur_w * 0.45) * sr))
        ln = min(int(dur_w * sr), n - i0)
        if ln <= 128:
            return
        wt = np.arange(ln, dtype=np.float64) / ln
        env = np.sin(np.pi * wt) ** 1.8
        noise = np.random.default_rng(int(ts * 100) + 13).normal(0, 1, ln)
        b_lp, a_lp = butter(2, [280 / (sr * 0.5), 2400 / (sr * 0.5)], btype="band")
        sw = filtfilt(b_lp, a_lp, noise) * env * gain
        mix_l[i0:i0 + ln] += sw * (1.1 - 0.4 * wt)
        mix_r[i0:i0 + ln] += sw * (0.7 + 0.4 * wt)

    def add_chime(ts: float, gain: float = 0.095):
        i0 = int(ts * sr)
        ln = min(int(0.65 * sr), n - i0)
        if i0 < 0 or ln <= 128:
            return
        ct = np.arange(ln, dtype=np.float64) / sr
        sig = (
            np.sin(2 * np.pi * 1046.5 * ct) * np.exp(-ct * 6.5)
            + 0.65 * np.sin(2 * np.pi * 1318.5 * ct) * np.exp(-ct * 5.2)
            + 0.45 * np.sin(2 * np.pi * 1568.0 * ct) * np.exp(-ct * 4.5)
        ) * gain
        mix_l[i0:i0 + ln] += sig * 0.95
        mix_r[i0:i0 + ln] += sig * 1.05

    # Timed UI & Cut SFX
    for w_ts in [0.08, 12.76, 32.13, 54.06, 63.70, 74.46, 88.26, 94.26, 115.2]:
        add_whoosh(w_ts)
    for p_ts in [0.45, 5.2, 13.4, 19.0, 36.6, 40.8, 42.3, 45.1, 58.1, 69.1, 78.0, 90.0, 96.5, 106.0]:
        add_pop(p_ts, 820.0, 0.075)
    add_chime(19.2, 0.070)   # Trust QC Shield chime
    add_chime(115.5, 0.105)  # Comment «آیدایت» CTA notification chime!

    return np.stack([mix_l, mix_r], axis=1)


def prepare_blogger_audio_and_alignment(raw_mp4: str, work_dir: str, whisper_model_size: str = "medium") -> dict:
    """
    1. Enhances Milad's real vocal track from -31.9dB raw phone mic to studio clarity.
    2. Runs faster-whisper word-timestamp alignment + DentEye/Aidite orthographic dictionary.
    3. Mixes subtle sidechain-ducked blogger groove + 20 synced Foley cues -> master_audio.wav.
    """
    clean_vo_wav = os.path.join(work_dir, "clean_voice_48k.wav")
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", raw_mp4, "-vn",
        "-af", (
            "highpass=f=85,"
            "afftdn=nf=-26:nr=10,"
            "equalizer=f=185:t=q:w=1.2:g=2.4,"
            "equalizer=f=360:t=q:w=1.5:g=-2.0,"
            "equalizer=f=3600:t=q:w=1.1:g=3.2,"
            "equalizer=f=9200:t=h:w=2000:g=1.8,"
            "acompressor=threshold=-23dB:ratio=3.2:attack=8:release=140:makeup=11dB,"
            "alimiter=limit=0.86:attack=5:release=50:level=disabled"
        ),
        "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", clean_vo_wav
    ], check=True)

    # Read cleaned mono voice
    with wave.open(clean_vo_wav, "rb") as wf:
        n_frames = wf.getnframes()
        vo_mono = np.frombuffer(wf.readframes(n_frames), dtype=np.int16).astype(np.float64) / 32768.0
    dur_sec = len(vo_mono) / 48000.0

    # Normalize RMS cleanly to target ~ -15.2 dBFS before limiter so speech sits loud & clear
    rms = np.sqrt(np.mean(vo_mono ** 2) + 1e-12)
    target_rms = 0.172
    vo_gain = min(2.8, target_rms / rms)
    vo_mono = np.tanh(vo_mono * vo_gain * 1.06) / np.tanh(1.06) * 0.86

    # Envelope for sidechain music ducking
    win = 2400
    vo_abs = np.abs(vo_mono)
    kernel = np.ones(win, dtype=np.float64) / win
    vo_env = np.convolve(vo_abs, kernel, mode="same")

    # Run faster-whisper word-level transcription directly on 16kHz float32 ndarray (bypasses PyAV!)
    from faster_whisper import WhisperModel
    print(f"[Studio v7.0] Running faster-whisper ({whisper_model_size}) word-timestamp alignment...", flush=True)
    vo_16k = np.ascontiguousarray(vo_mono[::3], dtype=np.float32)
    wmodel = WhisperModel(whisper_model_size, device="cpu", compute_type="int8")
    segments, _ = wmodel.transcribe(
        vo_16k,
        language="fa",
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 260},
        initial_prompt=(
            "درود بر شما همراهان عزیز. بنده میلاد کرامتی‌پور هستم و اینجا دنت‌آی هست. "
            "تجهیزات دندانپزشکی استوک در حد نو، اورال اسکنر آیدایت مدل رپید فایو، استند، "
            "فلش حاوی نرم‌افزار، چهار عدد تیپ اسکنر، قابلیت اتوکلاو تا ۱۰۰ بار، وزن ۱۶۲ گرم، "
            "عمق اسکن ۲۵ میلی‌متری، کالیبراسیون دوره‌ای، یک آرچ ۲۵ ثانیه، فول‌آرچ ۶۰ ثانیه، "
            "دقت سینگل‌کراون ۱۰ میکرون، بافت‌های نرم، کلمه آیدایت رو کامنت کنید."
        ),
    )
    raw_words = []
    for seg in segments:
        if seg.words:
            for wd in seg.words:
                txt = wd.word.strip()
                if txt:
                    raw_words.append({"word": txt, "start": round(float(wd.start), 3), "end": round(float(wd.end), 3)})
    del wmodel

    norm_words = normalize_persian_transcript_words(raw_words)
    phrases = group_into_blogger_phrases(norm_words)

    # Synthesize background music + Foley SFX and mix with enhanced vocal
    bg_sfx_st = _synth_blogger_music_and_sfx(dur_sec, vo_env, 48000)
    master_st = np.zeros_like(bg_sfx_st)
    master_st[:, 0] = vo_mono + bg_sfx_st[:, 0]
    master_st[:, 1] = vo_mono + bg_sfx_st[:, 1]
    peak = np.max(np.abs(master_st)) + 1e-9
    if peak > 0.89:
        master_st = master_st * (0.89 / peak)

    master_wav = os.path.join(work_dir, "master_blogger_48k.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes((np.clip(master_st, -0.95, 0.95) * 32767.0).astype(np.int16).tobytes())

    meta = {
        "total_dur": round(dur_sec, 3),
        "word_count": len(norm_words),
        "phrase_count": len(phrases),
        "phrases": phrases,
        "master_wav": master_wav,
    }
    return meta


# =============================================================================
# STUDIO v7.0 VIDEO GRADING, SMART CROP & UPRIGHT 16:9 MONITOR RESTORATION
# =============================================================================
_VIG_MASK = None
_BG_DARK_CACHE = None

def _get_vignette_mask() -> np.ndarray:
    """Precomputes subtle top/bottom dark blogger gradient mask (1920, 1080, 1) float32."""
    global _VIG_MASK
    if _VIG_MASK is not None:
        return _VIG_MASK
    yy = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
    top_Shade = np.clip((0.18 - yy) / 0.18, 0.0, 1.0) * 0.34
    bot_Shade = np.clip((yy - 0.68) / 0.32, 0.0, 1.0) * 0.56
    rad_Shade = np.clip((xx ** 2 + ((yy - 0.45) * 1.15) ** 2 - 0.55) * 0.35, 0.0, 0.24)
    keep = np.clip(1.0 - np.maximum(np.maximum(top_Shade, bot_Shade), rad_Shade), 0.35, 1.0)
    _VIG_MASK = keep[:, :, None]
    return _VIG_MASK


def _get_studio_dark_backdrop() -> Image.Image:
    """Precomputes the deep Sapphire-Obsidian DentEye studio backdrop for software/spec scenes."""
    global _BG_DARK_CACHE
    if _BG_DARK_CACHE is not None:
        return _BG_DARK_CACHE
    arr = np.zeros((H, W, 3), dtype=np.float32)
    yy = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
    r2 = xx ** 2 + ((yy - 0.46) * 1.35) ** 2
    glow = np.exp(-r2 * 2.2)
    arr[:, :, 0] = 4.0 + 10.0 * glow
    arr[:, :, 1] = 10.0 + 28.0 * glow
    arr[:, :, 2] = 22.0 + 58.0 * glow
    # Subtle 72px medical grid
    g_col = np.array([3.0, 9.0, 16.0], dtype=np.float32)
    for gx in range(36, W, 72):
        arr[:, gx:gx + 1, :] += glow[:, gx:gx + 1, None] * g_col
    for gy in range(36, H, 72):
        arr[gy:gy + 1, :, :] += glow[gy:gy + 1, :, None] * g_col
    _BG_DARK_CACHE = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    return _BG_DARK_CACHE


def _patch_softbox_corner(crop_rgb: np.ndarray, patch_w: int = 58, patch_h: int = 235) -> np.ndarray:
    """Seamlessly clones the clean royal-blue studio wall over the tiny residual top-left softbox corner."""
    h, w, _ = crop_rgb.shape
    pw = min(patch_w, w // 4)
    ph = min(patch_h, h // 3)
    # Sample clean vertical gradient strip right beside the softbox (x = pw+12 .. pw+36)
    ref_strip = np.mean(crop_rgb[:ph, pw + 12:pw + 38, :].astype(np.float32), axis=1, keepdims=True)
    # Triangular feather mask (strongest in top-left corner, 0 at diagonal)
    yy = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None]
    xx = np.linspace(0.0, 1.0, pw, dtype=np.float32)[None, :]
    alpha = np.clip((1.0 - (xx * 0.92 + yy * 0.78)) * 2.4, 0.0, 1.0)[:, :, None]
    region = crop_rgb[:ph, :pw, :].astype(np.float32)
    crop_rgb[:ph, :pw, :] = np.clip(region * (1.0 - alpha) + ref_strip * alpha, 0, 255).astype(np.uint8)
    return crop_rgb


def _grade_camera_frame(im: Image.Image, contrast: float = 1.06, color: float = 1.08, bright: float = 1.02) -> Image.Image:
    im = ImageEnhance.Brightness(im).enhance(bright)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(color)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.15, percent=55, threshold=3))
    arr = np.asarray(im, dtype=np.float32) * _get_vignette_mask()
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def build_base_video_canvas(frame_idx: int, raw_rgb: np.ndarray, t: float) -> Image.Image:
    """Transforms raw 804x1428 phone footage into a graded 1080x1920 Studio v7.0 frame."""
    # -------------------------------------------------------------------------
    # A. Talking Head Shots (0 .. 32.133s) -> Smart Crop + Softbox Removal + Blogger Zooms
    # -------------------------------------------------------------------------
    if frame_idx < F_UNBOX_1:
        if frame_idx < F_TH_CUT:
            # Shot 01 (0..12.77s): Base crop (x=204..800, y=254..1314)
            cx0, cy0, bw0 = 502.0, 784.0, 596.0
            if t < 2.2:
                zm = 1.0 + 0.075 * (1.0 - ease_out_cubic(t / 2.2))
            elif t < 9.1:
                zm = 1.0 + 0.055 * ease_in_out_cubic((t - 2.2) / 6.9)
            else:
                zm = 1.022
        else:
            # Shot 02 (12.77..32.13s): Base crop (x=168..802, y=178..1305)
            cx0, cy0, bw0 = 485.0, 742.0, 634.0
            if t < 18.4:
                zm = 1.0 + 0.050 * ease_in_out_cubic((t - 12.77) / 5.63)
            elif t < 25.3:
                # Authority punch-in on "ما هر دستگاهی داخل دنت‌آی موجود نمی‌کنیم"!
                zm = 1.082
                cy0 -= 14.0
            elif t < 29.2:
                zm = 1.035 + 0.035 * ease_in_out_cubic((t - 25.3) / 3.9)
            else:
                zm = 1.07 + 0.055 * ease_in_out_cubic((t - 29.2) / 2.93)

        cw = bw0 / zm
        ch = cw * (16.0 / 9.0)
        x0 = int(round(clamp(cx0 - cw * 0.5, 0.0, RAW_W - cw)))
        y0 = int(round(clamp(cy0 - ch * 0.5, 0.0, RAW_H - ch)))
        x1 = min(RAW_W, x0 + int(round(cw)))
        y1 = min(RAW_H, y0 + int(round(ch)))
        sub = raw_rgb[y0:y1, x0:x1, :].copy()
        sub = _patch_softbox_corner(sub, patch_w=64, patch_h=250)
        im = Image.fromarray(sub, "RGB").resize((W, H), Image.Resampling.LANCZOS)
        return _grade_camera_frame(im, contrast=1.07, color=1.09, bright=1.03)

    # -------------------------------------------------------------------------
    # B. Sideways 90° Laptop Software & Live 3D Arch Scan (Shots 13 & 15)
    # -------------------------------------------------------------------------
    if (F_SW_ORDER <= frame_idx < F_SPEC_10UM) or (frame_idx >= F_SW_SCAN3D):
        base = _get_studio_dark_backdrop().copy()
        # Rotate 90° CCW -> 1428 x 804 upright 16:9 widescreen!
        rot_arr = np.rot90(raw_rgb, k=1)  # shape (804, 1428, 3)
        if frame_idx >= F_SW_SCAN3D:
            # Subtle focus push-in onto the 3D dental arch!
            tl = (frame_idx - F_SW_SCAN3D) / float(FPS_EDIT)
            zm = 1.04 + 0.05 * math.sin(min(1.0, tl / 26.0) * math.pi * 0.5)
            rw, rh = int(1428 / zm), int(804 / zm)
            rx0 = (1428 - rw) // 2 + 28
            ry0 = (804 - rh) // 2 + 12
            rx0 = max(0, min(1428 - rw, rx0))
            ry0 = max(0, min(804 - rh, ry0))
            rot_arr = rot_arr[ry0:ry0 + rh, rx0:rx0 + rw, :]

        mon_w, mon_h = 988, 556
        sw_im = Image.fromarray(rot_arr, "RGB").resize((mon_w, mon_h), Image.Resampling.LANCZOS)
        sw_im = ImageEnhance.Contrast(sw_im).enhance(1.05)

        # Paste inside rounded Dark-Glass Studio Monitor at (46, 616) below 48px window bar (46, 568)
        mask = Image.new("L", (mon_w, mon_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, mon_w - 1, mon_h - 1], radius=22, fill=255)
        base.paste(sw_im, (46, 616), mask)
        return base

    # -------------------------------------------------------------------------
    # C. White PDF Spec / Brochure Shots (Shots 10, 11, 14) -> Framed Showcase Card
    # -------------------------------------------------------------------------
    if (F_SPEC_TBL <= frame_idx < F_CASE_CAL) or (F_SPEC_10UM <= frame_idx < F_SW_SCAN3D):
        base = _get_studio_dark_backdrop().copy()
        tl_s = (frame_idx - (F_SPEC_TBL if frame_idx < F_CASE_CAL else F_SPEC_10UM)) / float(FPS_EDIT)
        zm = 1.0 + 0.035 * clamp(tl_s / 5.0)
        cw, ch = int(RAW_W / zm), int(920 / zm)
        x0 = (RAW_W - cw) // 2
        y0 = 260 + (920 - ch) // 2
        card_im = Image.fromarray(raw_rgb[y0:y0 + ch, x0:x0 + cw, :], "RGB").resize((944, 710), Image.Resampling.LANCZOS)
        card_im = ImageEnhance.Brightness(card_im).enhance(0.95)
        mask = Image.new("L", (944, 710), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 943, 709], radius=28, fill=255)
        base.paste(card_im, (68, 548), mask)
        return base

    # -------------------------------------------------------------------------
    # D. Hardware & Unboxing B-Roll Shots -> Full 1080x1920 Ken Burns + Grade
    # -------------------------------------------------------------------------
    cut_starts = [F_UNBOX_1, F_UNBOX_2, F_UNBOX_3, F_UNBOX_4, F_UNBOX_5, F_MACRO_HEAD, F_BODY_162G, F_CASE_CAL]
    f0 = max(cs for cs in cut_starts if cs <= frame_idx)
    tl_b = (frame_idx - f0) / float(FPS_EDIT)
    zm = 1.0 + 0.055 * clamp(tl_b / 5.5)
    cw, ch = int(RAW_W / zm), int(RAW_H / zm)
    x0, y0 = (RAW_W - cw) // 2, (RAW_H - ch) // 2
    im = Image.fromarray(raw_rgb[y0:y0 + ch, x0:x0 + cw, :], "RGB").resize((W, H), Image.Resampling.LANCZOS)
    return _grade_camera_frame(im, contrast=1.06, color=1.08, bright=1.01)


# =============================================================================
# STUDIO v7.0 BLOGGER GLASSMORPHIC UI CARDS & WORD-HIGHLIGHT SUBTITLES
# =============================================================================
_UI_TEXT_CACHE = {}

def _measure_and_sprite(text: str, font, color=(255, 255, 255, 255)):
    key = (text, id(font), color)
    if key in _UI_TEXT_CACHE:
        return _UI_TEXT_CACHE[key]
    if len(_UI_TEXT_CACHE) > 280:
        _UI_TEXT_CACHE.clear()
    t_dir = "ltr" if text.isascii() else "rtl"
    asc, desc = font.getmetrics()
    d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = d.textbbox((0, 0), text, font=font, direction=t_dir, language="fa")
    px, py = 14, 10
    tw = max(1, bb[2] - bb[0] + px * 2)
    th = max(1, asc + desc + py * 2)
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((px - bb[0], py), text, font=font, fill=color, direction=t_dir, language="fa")
    res = (im, bb[2] - bb[0], asc + desc)
    _UI_TEXT_CACHE[key] = res
    return res


def _paste_rgba(dst_rgba: Image.Image, src_rgba: Image.Image, cx: float, cy: float, alpha_mul: float = 1.0):
    if alpha_mul <= 0.01:
        return
    if alpha_mul < 0.995:
        r, g, b, a = src_rgba.split()
        a = a.point(lambda p: int(p * alpha_mul))
        src_rgba = Image.merge("RGBA", (r, g, b, a))
    x = int(round(cx - src_rgba.width * 0.5))
    y = int(round(cy - src_rgba.height * 0.5))
    dst_rgba.alpha_composite(src_rgba, (x, y))


def _draw_rounded_glass(ctx, x: float, y: float, w: float, h: float, r: float,
                        fill_rgba=(8/255, 16/255, 30/255, 0.84),
                        rim_rgb=(0.18, 0.83, 1.0), alpha: float = 1.0):
    if alpha <= 0.01:
        return
    # Soft drop shadow
    for si in range(3, 0, -1):
        pad = si * 5.0
        _cairo_rrect(ctx, x - pad * 0.4, y + si * 4.5, w + pad * 0.8, h + pad * 0.4, r + pad * 0.3)
        ctx.set_source_rgba(0, 0, 0, 0.14 * alpha)
        ctx.fill()

    # Frosted dark fill
    _cairo_rrect(ctx, x, y, w, h, r)
    lg = cairo.LinearGradient(x, y, x, y + h)
    lg.add_color_stop_rgba(0.0, fill_rgba[0] + 0.04, fill_rgba[1] + 0.05, fill_rgba[2] + 0.07, fill_rgba[3] * alpha)
    lg.add_color_stop_rgba(1.0, fill_rgba[0], fill_rgba[1], fill_rgba[2], (fill_rgba[3] + 0.06) * alpha)
    ctx.set_source(lg)
    ctx.fill()

    # Outer glowing rim
    _cairo_rrect(ctx, x, y, w, h, r)
    rg = cairo.LinearGradient(x, y, x + w, y + h)
    rg.add_color_stop_rgba(0.0, rim_rgb[0], rim_rgb[1], rim_rgb[2], 0.88 * alpha)
    rg.add_color_stop_rgba(0.5, rim_rgb[0] * 0.55, rim_rgb[1] * 0.55, rim_rgb[2] * 0.55, 0.32 * alpha)
    rg.add_color_stop_rgba(1.0, rim_rgb[0], rim_rgb[1], rim_rgb[2], 0.78 * alpha)
    ctx.set_source(rg)
    ctx.set_line_width(2.4)
    ctx.stroke()

    # Top specular highlight bar
    ctx.move_to(x + r + 14, y + 1.5)
    ctx.line_to(x + w - r - 14, y + 1.5)
    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.45 * alpha)
    ctx.set_line_width(1.6)
    ctx.stroke()


def _cairo_rrect(ctx, x: float, y: float, w: float, h: float, r: float):
    r = min(r, w * 0.5, h * 0.5)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0.0)
    ctx.arc(x + w - r, y + h - r, r, 0.0, math.pi * 0.5)
    ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
    ctx.close_path()


def _draw_check_circle(ctx, cx: float, cy: float, rad: float, rgb=(0.28, 0.98, 0.58), alpha: float = 1.0):
    if alpha <= 0.01:
        return
    ctx.arc(cx, cy, rad, 0, math.pi * 2)
    ctx.set_source_rgba(rgb[0] * 0.22, rgb[1] * 0.22, rgb[2] * 0.22, 0.92 * alpha)
    ctx.fill()
    ctx.arc(cx, cy, rad, 0, math.pi * 2)
    ctx.set_source_rgba(rgb[0], rgb[1], rgb[2], 0.95 * alpha)
    ctx.set_line_width(2.4)
    ctx.stroke()
    ctx.move_to(cx - rad * 0.42, cy + rad * 0.02)
    ctx.line_to(cx - rad * 0.10, cy + rad * 0.34)
    ctx.line_to(cx + rad * 0.46, cy - rad * 0.30)
    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.98 * alpha)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(3.2)
    ctx.stroke()


def render_blogger_overlays_and_subtitles(base_img: Image.Image, frame_idx: int, t: float,
                                          phrases: list, fonts: FontBank,
                                          surf: cairo.ImageSurface, ctx: cairo.Context) -> bytes:
    """Renders all Studio v7.0 Glassmorphic Motion Overlays + Active-Word Pill Subtitles."""
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    ctx.paint()
    ctx.restore()

    texts = []  # (rgba_sprite, cx, cy, alpha)

    # -------------------------------------------------------------------------
    # 0. Persistent Subtle Top-Right Brand Pill: DENTEYE | دنت‌آی
    # -------------------------------------------------------------------------
    al_brand = clamp((t - 0.5) / 0.5)
    if al_brand > 0.01:
        _draw_rounded_glass(ctx, 696, 58, 326, 58, 29, (6/255, 13/255, 25/255, 0.80), (0.18, 0.83, 1.0), al_brand * 0.92)
        ctx.arc(994, 87, 7.0, 0, math.pi * 2)
        ctx.set_source_rgba(0.28, 0.98, 0.58, al_brand * (0.65 + 0.35 * math.sin(t * 4.0)))
        ctx.fill()
        # Divider line between LTR 'DENTEYE' and RTL 'دنت‌آی'
        ctx.move_to(866, 72)
        ctx.line_to(866, 102)
        ctx.set_source_rgba(0.45, 0.82, 1.0, 0.45 * al_brand)
        ctx.set_line_width(1.8)
        ctx.stroke()
        sp_en, _, _ = _measure_and_sprite("DENTEYE", fonts.bold_30, (*CYAN_RGB, 255))
        sp_fa, _, _ = _measure_and_sprite("دنت‌آی", fonts.bold_30, (245, 252, 255, 255))
        texts.extend([
            (sp_en, 784, 87, al_brand * 0.96),
            (sp_fa, 928, 87, al_brand * 0.96),
        ])

    # -------------------------------------------------------------------------
    # 1. Monitor Window Frame Chrome on Upright 16:9 Software Shots (Shots 13 & 15)
    # -------------------------------------------------------------------------
    if (F_SW_ORDER <= frame_idx < F_SPEC_10UM) or (frame_idx >= F_SW_SCAN3D):
        # Outer glass monitor shell (42, 564, 996, 612)
        _cairo_rrect(ctx, 42, 564, 996, 52, 20)
        ctx.set_source_rgba(0.05, 0.10, 0.20, 0.96)
        ctx.fill()
        _cairo_rrect(ctx, 42, 564, 996, 612, 24)
        ctx.set_source_rgba(0.18, 0.83, 1.0, 0.85)
        ctx.set_line_width(3.0)
        ctx.stroke()
        # macOS window dots
        for di, dcol in enumerate([(1.0, 0.35, 0.36), (1.0, 0.76, 0.24), (0.25, 0.90, 0.48)]):
            ctx.arc(76 + di * 26, 590, 7.0, 0, math.pi * 2)
            ctx.set_source_rgba(*dcol, 0.95)
            ctx.fill()
        sp_m, _, _ = _measure_and_sprite("DENTEYE LAB  •  Aidite Rapid 5 Live Scan", fonts.reg_26, (210, 232, 255, 245))
        texts.append((sp_m, 540, 590, 1.0))
        # Pulsing LIVE indicator
        pulse = 0.55 + 0.45 * math.sin(t * 5.5)
        ctx.arc(934, 590, 7.0, 0, math.pi * 2)
        ctx.set_source_rgba(0.28, 0.98, 0.58, pulse)
        ctx.fill()
        sp_lv, _, _ = _measure_and_sprite("LIVE", fonts.bold_30, (*GREEN_RGB, 255))
        texts.append((sp_lv, 982, 590, 0.95))

    # Showcase border on White PDF Spec Shots (Shots 10, 11, 14)
    if (F_SPEC_TBL <= frame_idx < F_CASE_CAL) or (F_SPEC_10UM <= frame_idx < F_SW_SCAN3D):
        _cairo_rrect(ctx, 66, 546, 948, 714, 28)
        ctx.set_source_rgba(0.18, 0.83, 1.0, 0.82)
        ctx.set_line_width(3.0)
        ctx.stroke()

    # -------------------------------------------------------------------------
    # 2. Context-Timed Blogger Motion-Graphics Cards (14 Cards!)
    # -------------------------------------------------------------------------
    # Card 01 (0.45..4.8s): Host Lower-Third Identity Card (below hands, y=1165..1330)
    a1 = window_fade(t, 0.45, 4.85, 0.32, 0.35)
    if a1 > 0.01:
        dy = (1.0 - spring_pop(clamp((t - 0.45) / 0.45))) * 36.0
        _draw_rounded_glass(ctx, 110, 1165 + dy, 860, 158, 28, (6/255, 13/255, 26/255, 0.86), (0.18, 0.83, 1.0), a1)
        _draw_check_circle(ctx, 905, 1222 + dy, 22, (0.18, 0.83, 1.0), a1)
        s_n1, _, _ = _measure_and_sprite("میلاد کرامتی‌پور", fonts.bold_44, (255, 255, 255, 255))
        s_n2, _, _ = _measure_and_sprite("کارشناس و بررسی‌کننده‌ی تجهیزات دندانپزشکی  •  دنت‌آی", fonts.reg_26, (*CYAN_RGB, 255))
        texts.extend([(s_n1, 510, 1216 + dy, a1), (s_n2, 510, 1280 + dy, a1)])

    # Card 02 (5.1..11.6s): Niche Hook Lower-Third Card (y=1160..1325 — never crowds Milad's head!)
    a2 = window_fade(t, 5.1, 11.6, 0.32, 0.35)
    if a2 > 0.01:
        dy = (1.0 - spring_pop(clamp((t - 5.1) / 0.45))) * 34.0
        _draw_rounded_glass(ctx, 84, 1160 + dy, 912, 162, 28, (7/255, 16/255, 30/255, 0.88), (0.28, 0.98, 0.58), a2)
        s_h1, _, _ = _measure_and_sprite("تجهیزات دندانپزشکی استوک در حد نو", fonts.bold_36, (*GREEN_RGB, 255))
        s_h2, _, _ = _measure_and_sprite("معرفی، تست عملی و بررسی تخصصی در دنت‌آی", fonts.reg_26, (235, 246, 255, 245))
        texts.extend([(s_h1, 540, 1214 + dy, a2), (s_h2, 540, 1278 + dy, a2)])

    # Card 03 (13.3..19.0s): Product Hero Reveal Card — Aidite Rapid 5 (y=1155..1330)
    a3 = window_fade(t, 13.3, 19.0, 0.32, 0.35)
    if a3 > 0.01:
        dy = (1.0 - spring_pop(clamp((t - 13.3) / 0.45))) * 36.0
        _draw_rounded_glass(ctx, 96, 1155 + dy, 888, 170, 28, (6/255, 14/255, 28/255, 0.88), (0.18, 0.83, 1.0), a3)
        s_p1, _, _ = _measure_and_sprite("Aidite Rapid 5", fonts.bold_52, (*CYAN_RGB, 255))
        s_p2, _, _ = _measure_and_sprite("اورال اسکنر دیجیتال سه‌بعدی داخل دهانی", fonts.bold_30, (255, 255, 255, 250))
        texts.extend([(s_p1, 540, 1212 + dy, a3), (s_p2, 540, 1280 + dy, a3)])

    # Card 04 (19.2..29.2s): DentEye Technical QC Guarantee Shield (y=1155..1330)
    a4 = window_fade(t, 19.2, 29.2, 0.32, 0.35)
    if a4 > 0.01:
        dy = (1.0 - spring_pop(clamp((t - 19.2) / 0.45))) * 32.0
        _draw_rounded_glass(ctx, 82, 1155 + dy, 916, 170, 28, (6/255, 18/255, 24/255, 0.88), (0.28, 0.98, 0.58), a4)
        _draw_check_circle(ctx, 932, 1240 + dy, 28, (0.28, 0.98, 0.58), a4)
        s_q1, _, _ = _measure_and_sprite("تاییدشده توسط کارشناسان فنی دنت‌آی", fonts.bold_36, (*GREEN_RGB, 255))
        s_q2, _, _ = _measure_and_sprite("عبور از فیلترهای تخصصی سلامت و بالاترین کیفیت", fonts.reg_26, (235, 248, 255, 245))
        texts.extend([(s_q1, 498, 1212 + dy, a4), (s_q2, 498, 1278 + dy, a4)])

    # Card 05 (32.3..53.9s): Interactive 4-Item Unboxing Checklist (Top Card y=140..475)
    a5 = window_fade(t, 32.3, 53.9, 0.30, 0.35)
    if a5 > 0.01:
        _draw_rounded_glass(ctx, 68, 140, 944, 338, 28, (6/255, 13/255, 26/255, 0.84), (0.18, 0.83, 1.0), a5)
        st_u, _, _ = _measure_and_sprite("اقلام همراه اورال اسکنر Aidite Rapid 5", fonts.bold_36, (*CYAN_RGB, 255))
        texts.append((st_u, 540, 188, a5))
        items = [
            (35.2, "۱. استند نگهدارنده‌ی رومیزی",       545, 265),
            (39.8, "۲. هندپیس اسکنر سه‌بعدی",           92,  265),
            (42.0, "۳. فلش اختصاصی نرم‌افزار",         545, 368),
            (45.0, "۴. چهار سری (۳ استاندارد + ۱ مینی)", 92,  368),
        ]
        for t_on, itxt, ix, iy in items:
            active = clamp((t - t_on) / 0.35)
            col_rim = (0.28, 0.98, 0.58) if active > 0.5 else (0.25, 0.40, 0.58)
            _draw_rounded_glass(ctx, ix, iy, 442, 82, 18, (10/255, 20/255, 36/255, 0.86), col_rim, a5 * (0.45 + 0.55 * active))
            if active > 0.2:
                _draw_check_circle(ctx, ix + 408, iy + 41, 16, (0.28, 0.98, 0.58), a5 * active)
            tcol = (*GREEN_RGB, 255) if active > 0.5 else (200, 218, 238, 210)
            sp_i, _, _ = _measure_and_sprite(itxt, fonts.reg_26, tcol)
            texts.append((sp_i, ix + 196, iy + 41, a5 * (0.55 + 0.45 * active)))

    # Card 06 (54.1..57.9s): 100x Autoclave Sterilization Badge (y=158..330)
    a6 = window_fade(t, 54.1, 57.9, 0.25, 0.28)
    if a6 > 0.01:
        dy = -(1.0 - spring_pop(clamp((t - 54.1) / 0.40))) * 28.0
        _draw_rounded_glass(ctx, 84, 158 + dy, 912, 168, 28, (8/255, 16/255, 28/255, 0.88), (1.0, 0.78, 0.26), a6)
        s6_1, _, _ = _measure_and_sprite("قابلیت اتوکلاو سری‌ها: تا ۱۰۰ بار استریل!", fonts.bold_36, (*AMBER_RGB, 255))
        s6_2, _, _ = _measure_and_sprite("دوام بالا و بهداشت کامل کلینیکی در مطب", fonts.reg_30, (240, 248, 255, 245))
        texts.extend([(s6_1, 540, 214 + dy, a6), (s6_2, 540, 278 + dy, a6)])

    # Card 07 (58.0..68.95s): Dual Ergonomic Spec Cards (162g Weight + 25mm Depth of Field)
    a7 = window_fade(t, 58.0, 68.95, 0.30, 0.30)
    if a7 > 0.01:
        _draw_rounded_glass(ctx, 68, 175, 456, 260, 26, (7/255, 15/255, 28/255, 0.88), (0.18, 0.83, 1.0), a7)
        s7_a1, _, _ = _measure_and_sprite("۱۶۲ گرم", fonts.eb_68, (*CYAN_RGB, 255))
        s7_a2, _, _ = _measure_and_sprite("طراحی فوق‌سبک و خوش‌دست", fonts.bold_30, (255, 255, 255, 250))
        texts.extend([(s7_a1, 296, 265, a7), (s7_a2, 296, 368, a7)])

        a7b = a7 * clamp((t - 60.8) / 0.45)
        if a7b > 0.01:
            _draw_rounded_glass(ctx, 556, 175, 456, 260, 26, (7/255, 18/255, 26/255, 0.88), (0.28, 0.98, 0.58), a7b)
            s7_b1, _, _ = _measure_and_sprite("۲۵ میلی‌متر", fonts.bold_52, (*GREEN_RGB, 255))
            s7_b2, _, _ = _measure_and_sprite("عمق اسکن بالا (25mm DoF)", fonts.bold_30, (255, 255, 255, 250))
            texts.extend([(s7_b1, 784, 265, a7b), (s7_b2, 784, 368, a7b)])

    # Card 08 (69.0..74.45s): Calibration-Free Highlight Card (y=165..345)
    a8 = window_fade(t, 69.0, 74.45, 0.28, 0.28)
    if a8 > 0.01:
        _draw_rounded_glass(ctx, 76, 165, 928, 174, 28, (6/255, 18/255, 24/255, 0.88), (0.28, 0.98, 0.58), a8)
        _draw_check_circle(ctx, 936, 252, 28, (0.28, 0.98, 0.58), a8)
        s8_1, _, _ = _measure_and_sprite("بدون نیاز به کالیبراسیون دوره‌ای!", fonts.bold_44, (*GREEN_RGB, 255))
        s8_2, _, _ = _measure_and_sprite("آماده‌به‌کار همیشگی و حذف دردسر کالیبره کردن", fonts.reg_26, (238, 248, 255, 245))
        texts.extend([(s8_1, 496, 222, a8), (s8_2, 496, 288, a8)])

    # Card 09 (74.5..88.25s): Scan Speed Stopwatch Cards above Upright Monitor (y=185..495)
    a9 = window_fade(t, 74.5, 88.25, 0.30, 0.30)
    if a9 > 0.01:
        _draw_rounded_glass(ctx, 560, 195, 464, 290, 26, (7/255, 16/255, 30/255, 0.90), (0.18, 0.83, 1.0), a9)
        s9_a1, _, _ = _measure_and_sprite("۲۵ ثانیه", fonts.eb_68, (*CYAN_RGB, 255))
        s9_a2, _, _ = _measure_and_sprite("اسکن کامل یک فک (Single Arch)", fonts.bold_30, (255, 255, 255, 250))
        texts.extend([(s9_a1, 792, 295, a9), (s9_a2, 792, 405, a9)])

        a9b = a9 * clamp((t - 78.2) / 0.45)
        if a9b > 0.01:
            _draw_rounded_glass(ctx, 56, 195, 464, 290, 26, (7/255, 18/255, 26/255, 0.90), (0.28, 0.98, 0.58), a9b)
            s9_b1, _, _ = _measure_and_sprite("۶۰ ثانیه", fonts.eb_68, (*GREEN_RGB, 255))
            s9_b2, _, _ = _measure_and_sprite("اسکن فول‌آرچ دو فک (Full Arch)", fonts.bold_30, (255, 255, 255, 250))
            texts.extend([(s9_b1, 288, 295, a9b), (s9_b2, 288, 405, a9b)])

    # Card 10 (88.3..94.25s): Micron Precision Cards above 10µm Showcase (y=185..485)
    a10 = window_fade(t, 88.3, 94.25, 0.28, 0.28)
    if a10 > 0.01:
        _draw_rounded_glass(ctx, 560, 195, 464, 285, 26, (7/255, 16/255, 30/255, 0.90), (0.18, 0.83, 1.0), a10)
        s10_a1, _, _ = _measure_and_sprite("۱۰ میکرون", fonts.eb_68, (*CYAN_RGB, 255))
        s10_a2, _, _ = _measure_and_sprite("دقت تک‌واحد (Single Crown)", fonts.bold_30, (255, 255, 255, 250))
        texts.extend([(s10_a1, 792, 292, a10), (s10_a2, 792, 402, a10)])

        _draw_rounded_glass(ctx, 56, 195, 464, 285, 26, (8/255, 17/255, 26/255, 0.90), (1.0, 0.78, 0.26), a10)
        s10_b1, _, _ = _measure_and_sprite("۲۰ میکرون", fonts.eb_68, (*AMBER_RGB, 255))
        s10_b2, _, _ = _measure_and_sprite("دقت فک کامل (Full Arch)", fonts.bold_30, (255, 255, 255, 250))
        texts.extend([(s10_b1, 288, 292, a10), (s10_b2, 288, 402, a10)])

    # Card 11 (94.3..103.5s): Soft-Tissue Image Recovery Card above Live 3D Arch Scan
    a11 = window_fade(t, 94.3, 103.5, 0.30, 0.32)
    if a11 > 0.01:
        _draw_rounded_glass(ctx, 64, 225, 952, 250, 28, (7/255, 16/255, 30/255, 0.90), (0.18, 0.83, 1.0), a11)
        s11_1, _, _ = _measure_and_sprite("بازیابی سریع تصویر و تشخیص بافت‌های نرم", fonts.bold_44, (*CYAN_RGB, 255))
        s11_2, _, _ = _measure_and_sprite("ثبت پیوسته و دقیق جزئیات دهان حین اسکن واقعی", fonts.bold_30, (240, 248, 255, 248))
        texts.extend([(s11_1, 540, 312, a11), (s11_2, 540, 402, a11)])

    # Card 12 (103.6..115.0s): 3-Pillar Clinic Summary Checklist above Live 3D Arch Model
    a12 = window_fade(t, 103.6, 115.0, 0.32, 0.32)
    if a12 > 0.01:
        _draw_rounded_glass(ctx, 64, 195, 952, 305, 28, (6/255, 16/255, 28/255, 0.90), (0.28, 0.98, 0.58), a12)
        s12_t, _, _ = _measure_and_sprite("چرا Aidite Rapid 5 انتخاب ایده‌آل مطب شماست؟", fonts.bold_36, (*GREEN_RGB, 255))
        texts.append((s12_t, 540, 252, a12))
        pills = [
            ("فوق‌سبک (۱۶۲ گرم)", 704, CYAN_RGB),
            ("فوق‌سریع (۲۵ ثانیه)", 384, GREEN_RGB),
            ("دقت ۱۰ میکرون",      84,  AMBER_RGB),
        ]
        for ptxt, px, prgb in pills:
            _draw_rounded_glass(ctx, px, 332, 290, 118, 22, (10/255, 22/255, 38/255, 0.92), (prgb[0]/255, prgb[1]/255, prgb[2]/255), a12)
            sp_p, _, _ = _measure_and_sprite(ptxt, fonts.bold_30, (*prgb, 255))
            texts.append((sp_p, px + 145, 391, a12))

    # Card 13 (115.1..122.43s): FLAGSHIP INSTAGRAM COMMENT CTA («آیدایت»)
    a13 = clamp((t - 115.1) / 0.38)
    if a13 > 0.01:
        dy = (1.0 - spring_pop(clamp((t - 115.1) / 0.48))) * 40.0
        pulse = 0.72 + 0.28 * math.sin(t * 6.0)
        _draw_rounded_glass(ctx, 56, 185 + dy, 968, 326, 32, (6/255, 15/255, 28/255, 0.94), (0.28, 0.98, 0.58), a13)
        s13_1, _, _ = _measure_and_sprite("جهت استعلام قیمت ویژه و دریافت مشاوره‌ی تخصصی:", fonts.bold_30, (235, 246, 255, 250))
        texts.append((s13_1, 540, 252 + dy, a13))

        # Glowing Comment Input Box Pill
        _draw_rounded_glass(ctx, 116, 318 + dy, 848, 142, 71, (14/255, 38/255, 32/255, 0.96), (0.28 * pulse + 0.2, 0.98, 0.58), a13)
        _draw_check_circle(ctx, 892, 389 + dy, 34, (0.28, 0.98, 0.58), a13)
        s13_2, _, _ = _measure_and_sprite("کلمه‌ی  « آیدایت »  رو کامنت کنید!", fonts.bold_44, (*GREEN_RGB, 255))
        texts.append((s13_2, 492, 389 + dy, a13))

    # -------------------------------------------------------------------------
    # 3. BLOGGER DYNAMIC WORD-BY-WORD ACTIVE-HIGHLIGHT PILL SUBTITLES (y=1495)
    # -------------------------------------------------------------------------
    active_phrase = None
    for ph in phrases:
        if ph["start"] - 0.06 <= t <= ph["end"]:
            active_phrase = ph
            break

    if active_phrase is not None:
        p_al = clamp((t - (active_phrase["start"] - 0.06)) / 0.14) * clamp((active_phrase["end"] - t) / 0.14)
        if p_al > 0.02:
            w_list = active_phrase["words"]
            # Choose active word index
            act_idx = 0
            for wi, wd in enumerate(w_list):
                if t >= wd["start"] - 0.04:
                    act_idx = wi

            # Measure each word individually so RTL order & per-word pill bounds are 100% exact!
            font_sub = fonts.bold_44
            gap = 16
            measured = []
            total_w = 0
            for wi, wd in enumerate(w_list):
                sp_w, ww, wh = _measure_and_sprite(wd["word"], font_sub, (255, 255, 255, 255))
                measured.append((wd["word"], ww, wh))
                total_w += ww
            total_w += gap * max(0, len(measured) - 1)

            # Auto-downscale font if phrase exceeds safe width 900px
            if total_w > 890:
                font_sub = fonts.bold_36
                gap = 13
                measured = []
                total_w = 0
                for wi, wd in enumerate(w_list):
                    sp_w, ww, wh = _measure_and_sprite(wd["word"], font_sub, (255, 255, 255, 255))
                    measured.append((wd["word"], ww, wh))
                    total_w += ww
                total_w += gap * max(0, len(measured) - 1)

            sub_cy = 1495.0 + (1.0 - spring_pop(clamp((t - active_phrase["start"] + 0.06) / 0.22))) * 16.0
            box_pad_x, box_pad_y = 38.0, 24.0
            box_w = min(984.0, total_w + box_pad_x * 2)
            box_h = 108.0
            box_x = 540.0 - box_w * 0.5
            box_y = sub_cy - box_h * 0.5

            # Frosted dark backdrop pill behind full phrase
            _draw_rounded_glass(ctx, box_x, box_y, box_w, box_h, 30,
                                (5/255, 11/255, 22/255, 0.88), (0.20, 0.78, 1.0), p_al)

            # Lay out words strictly Right-to-Left!
            cur_right = 540.0 + total_w * 0.5
            for wi, (w_str, ww, wh) in enumerate(measured):
                w_cx = cur_right - ww * 0.5
                is_act = (wi == act_idx)
                clean_tok = re.sub(r"[\.،؛؟!:«»]", "", w_str)
                is_kw = any(kw in clean_tok for kw in POWER_KEYWORDS)

                if is_act:
                    # Active word highlight pill!
                    pill_col = (1.0, 0.79, 0.24) if is_kw else (0.16, 0.84, 1.0)
                    pw = ww + 24.0
                    ph_h = 74.0
                    _cairo_rrect(ctx, w_cx - pw * 0.5, sub_cy - ph_h * 0.5, pw, ph_h, 18.0)
                    ctx.set_source_rgba(pill_col[0], pill_col[1], pill_col[2], 0.96 * p_al)
                    ctx.fill()
                    sp_dark, _, _ = _measure_and_sprite(w_str, font_sub, DARK_TXT)
                    texts.append((sp_dark, w_cx, sub_cy, p_al))
                elif wi < act_idx:
                    # Spoken word -> crisp white (or gold/cyan tint if keyword)
                    c_spoken = (*AMBER_RGB, 255) if is_kw else (255, 255, 255, 255)
                    sp_wh, _, _ = _measure_and_sprite(w_str, font_sub, c_spoken)
                    texts.append((sp_wh, w_cx, sub_cy, p_al))
                else:
                    # Upcoming word -> soft silver
                    sp_dim, _, _ = _measure_and_sprite(w_str, font_sub, (210, 226, 245, 175))
                    texts.append((sp_dim, w_cx, sub_cy, p_al))

                cur_right -= (ww + gap)

    # -------------------------------------------------------------------------
    # 4. Subtle Optical Sapphire Cut-Flash on Key Scene Transitions
    # -------------------------------------------------------------------------
    flash = 0.0
    for tc_cut in (0.0, 12.767, 32.133, 74.467, 94.267):
        dt_c = abs(t - tc_cut)
        if dt_c < 0.16:
            flash = max(flash, (1.0 - dt_c / 0.16) * 0.18)
    if flash > 0.01:
        rg = cairo.RadialGradient(540, 760, 40, 540, 760, 920)
        rg.add_color_stop_rgba(0.0, 0.55, 0.90, 1.0, flash)
        rg.add_color_stop_rgba(1.0, 0.10, 0.45, 0.95, 0.0)
        ctx.rectangle(0, 0, W, H)
        ctx.set_source(rg)
        ctx.fill()

    # Composite Cairo RGBA overlay + crisp Pillow typography onto graded base video frame
    buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((H, W, 4))
    ov_rgba = Image.fromarray(buf[:, :, [2, 1, 0, 3]], "RGBA")
    for sp, cx, cy, al in texts:
        _paste_rgba(ov_rgba, sp, cx, cy, al)

    out_rgba = base_img.convert("RGBA")
    out_rgba.alpha_composite(ov_rgba)
    return out_rgba.convert("RGB").tobytes()


# =============================================================================
# MULTIPROCESS WORKER & STREAMING CLOUD RENDERER
# =============================================================================
_W_FONTS = None
_W_PHRASES = None
_W_SURF = None
_W_CTX = None

def _init_blogger_worker(font_dir: str, phrases: list):
    global _W_FONTS, _W_PHRASES, _W_SURF, _W_CTX
    _W_FONTS = FontBank(font_dir)
    _W_PHRASES = phrases
    _W_SURF = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    _W_CTX = cairo.Context(_W_SURF)


def _render_blogger_batch(batch_items: list) -> list:
    out = []
    for frame_idx, raw_bytes in batch_items:
        raw_arr = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((RAW_H, RAW_W, 3))
        t = frame_idx / float(FPS_EDIT)
        base_im = build_base_video_canvas(frame_idx, raw_arr, t)
        rgb_bytes = render_blogger_overlays_and_subtitles(
            base_im, frame_idx, t, _W_PHRASES, _W_FONTS, _W_SURF, _W_CTX
        )
        out.append((frame_idx, rgb_bytes))
    return out


def fetch_raw_client_video(work_dir: str) -> str:
    raw_mp4 = os.path.join(work_dir, "raw_client_denteye.mp4")
    if os.path.exists(raw_mp4) and os.path.getsize(raw_mp4) > 50_000_000:
        return raw_mp4
    for url in (RAW_PRIMARY_URL, RAW_FALLBACK_URL):
        try:
            print(f"[Studio v7.0] Fetching raw client video from {url} ...", flush=True)
            subprocess.run([
                "curl", "-fSL", "-L", "--retry", "3",
                "-A", "Mozilla/5.0",
                url, "-o", raw_mp4
            ], check=True)
            if os.path.getsize(raw_mp4) > 50_000_000:
                return raw_mp4
        except Exception as e:
            print(f"[Warn] Download failed from {url}: {e}", flush=True)
    raise RuntimeError("Could not download raw_client_denteye.mp4 from primary or fallback URL.")


def save_blogger_qa_sheets(raw_mp4: str, font_dir: str, meta: dict, qa_dir: str):
    """Generates a 12-panel full-edit QA storyboard + subtitle alignment strip."""
    os.makedirs(qa_dir, exist_ok=True)
    fonts = FontBank(font_dir)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    phrases = meta["phrases"]

    sample_ts = [2.2, 7.5, 15.5, 22.0, 38.5, 48.0, 56.0, 65.0, 71.5, 81.5, 99.0, 118.5]
    cols, rows = 4, 3
    tw, th = 360, 640
    grid = Image.new("RGB", (cols * tw, rows * th), (0, 0, 0))

    for i, tm in enumerate(sample_ts):
        f_idx = int(round(tm * FPS_EDIT))
        p = subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", f"{tm:.3f}", "-i", raw_mp4,
            "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ], capture_output=True, check=True)
        raw_arr = np.frombuffer(p.stdout, dtype=np.uint8).reshape((RAW_H, RAW_W, 3))
        base_im = build_base_video_canvas(f_idx, raw_arr, tm)
        rgb = render_blogger_overlays_and_subtitles(base_im, f_idx, tm, phrases, fonts, surf, ctx)
        im_out = Image.frombytes("RGB", (W, H), rgb).resize((tw, th), Image.Resampling.LANCZOS)
        grid.paste(im_out, ((i % cols) * tw, (i // cols) * th))

    grid.save(os.path.join(qa_dir, "storyboard_12_blogger_denteye.png"))

    # Subtitle strip across 8 phrases
    strip = Image.new("RGB", (W, 8 * 150), (6, 12, 22))
    for k in range(min(8, len(phrases))):
        ph = phrases[min(len(phrases) - 1, k * max(1, len(phrases) // 8))]
        tm = 0.5 * (ph["start"] + ph["end"])
        f_idx = int(round(tm * FPS_EDIT))
        raw_arr = np.zeros((RAW_H, RAW_W, 3), dtype=np.uint8)
        base_im = Image.new("RGB", (W, H), (10, 18, 32))
        rgb = render_blogger_overlays_and_subtitles(base_im, f_idx, tm, phrases, fonts, surf, ctx)
        crop = Image.frombytes("RGB", (W, H), rgb).crop((0, 1420, W, 1570))
        strip.paste(crop, (0, k * 150))
    strip.save(os.path.join(qa_dir, "subtitle_strip_blogger_denteye.png"))


def run_cloud_pipeline(font_dir: str, work_dir: str, out_mp4: str, qa_dir: str, whisper_sz: str = "medium"):
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
    os.makedirs(qa_dir, exist_ok=True)

    raw_mp4 = fetch_raw_client_video(work_dir)
    meta = prepare_blogger_audio_and_alignment(raw_mp4, work_dir, whisper_sz)
    with open(os.path.join(qa_dir, "alignment.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[Studio v7.0] Aligned {meta['word_count']} words into {meta['phrase_count']} blogger caption pills ({meta['total_dur']}s).", flush=True)
    save_blogger_qa_sheets(raw_mp4, font_dir, meta, qa_dir)

    # Stream-decode raw_client.mp4 -> 4-core worker pool -> x264 Full HD encoder!
    frame_bytes_len = RAW_W * RAW_H * 3
    dec_proc = subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", raw_mp4,
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ], stdout=subprocess.PIPE, bufsize=frame_bytes_len * 4)

    enc_cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS_EDIT),
        "-i", "-",
        "-i", meta["master_wav"],
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-profile:v", "high", "-level:v", "4.2", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-af", "volume=-0.8dB,alimiter=limit=0.895:attack=5:release=50:level=disabled",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-shortest",
        out_mp4
    ]
    enc_proc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE, bufsize=W * H * 3 * 4)

    workers = max(2, min(4, os.cpu_count() or 2))
    print(f"[Studio v7.0] Rendering 1080x1920 @ {FPS_EDIT}fps on {workers} cores...", flush=True)

    def _batch_reader(batch_sz: int = 8):
        f_idx = 0
        batch = []
        while True:
            buf = dec_proc.stdout.read(frame_bytes_len)
            if not buf or len(buf) < frame_bytes_len:
                break
            batch.append((f_idx, buf))
            f_idx += 1
            if len(batch) >= batch_sz:
                yield batch
                batch = []
        if batch:
            yield batch

    rendered = 0
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_blogger_worker, initargs=(font_dir, meta["phrases"])) as pool:
        for batch_out in pool.map(_render_blogger_batch, _batch_reader(8), chunksize=1):
            for _, out_bytes in batch_out:
                enc_proc.stdin.write(out_bytes)
                rendered += 1
            if rendered % 480 == 0:
                print(f"  -> {rendered} frames ({rendered / FPS_EDIT:.1f}s) composited...", flush=True)

    dec_proc.stdout.close()
    dec_proc.wait()
    enc_proc.stdin.close()
    rc = enc_proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg encode failed with code {rc}")
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"[Studio v7.0] MASTER READY: {out_mp4} ({rendered} frames, {sz_mb:.2f} MB)", flush=True)


if __name__ == "__main__":
    if len(sys.argv) >= 6 and sys.argv[1] == "--cloud-render":
        run_cloud_pipeline(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else "medium")
    else:
        print("Usage: python -m src.episodes.ep12_denteye_aidite_blogger_edit --cloud-render <fonts> <work> <out.mp4> <qa_dir> [whisper_model]")
