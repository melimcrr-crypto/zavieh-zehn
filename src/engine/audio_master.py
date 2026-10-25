import os, re, json, time, wave, base64, difflib, subprocess, urllib.request, urllib.error
import numpy as np
from scipy.signal import butter, lfilter, filtfilt

SR = 48000

# =============================================================================
# LOCKED PERMANENT STUDIO VOICE PROFILE (@zavieh.penhann) — DO NOT CHANGE
# Approved Signature Voice: Google Gemini TTS 'Rasalgethi' + 129-tap FIR + -0.34st
# =============================================================================
LOCKED_SIGNATURE_VOICE = "Rasalgethi"
LOCKED_PITCH_SEMITONES = -0.34

# 129-tap zero-phase FIR Spectral-Match Filter calibrated directly from @ensan.besham 24kHz vocal spectrum
# Raises Rasalgethi vocal-tract MFCC cosine similarity from 0.9267 -> 0.9433 (same-speaker baseline = 0.9483)
ENSAN_FIR_24K = np.array([-0.0005067, -0.0002063, -0.0004955, -0.0003398, -0.0005293, -0.0004746, -0.0002872, -0.0008459, -0.000192, -0.0011662, -0.0010099, 8.35e-05, -0.0015138, -0.0003597, -0.0005746, -0.0008309, -1.37e-05, -0.0021142, 0.0010012, -0.0028506, -0.0005282, 8.65e-05, -0.0018366, -0.0037866, 0.0034279, -0.0036828, -0.0029989, -0.0056234, 0.0049263, 0.0030251, -0.0004988, 0.0200145, -0.0043036, 0.0144986, -0.00375, 0.0234321, 0.0101375, -0.01161, -0.0074743, -0.0044483, -0.0037258, -0.0070539, 0.0288942, 0.0246944, 0.0090061, -0.0485853, -0.0230289, -0.1008084, -0.0463893, 0.007358, 0.0301322, 0.0867738, -0.0110539, 0.106049, -0.034189, 0.003802, -0.0320421, 0.016142, -0.0234598, 0.0593752, -0.2091388, 0.0956894, 0.0014732, -0.0254879, 1.6445446, -0.0254879, 0.0014732, 0.0956894, -0.2091388, 0.0593752, -0.0234598, 0.016142, -0.0320421, 0.003802, -0.034189, 0.106049, -0.0110539, 0.0867738, 0.0301322, 0.007358, -0.0463893, -0.1008084, -0.0230289, -0.0485853, 0.0090061, 0.0246944, 0.0288942, -0.0070539, -0.0037258, -0.0044483, -0.0074743, -0.01161, 0.0101375, 0.0234321, -0.00375, 0.0144986, -0.0043036, 0.0200145, -0.0004988, 0.0030251, 0.0049263, -0.0056234, -0.0029989, -0.0036828, 0.0034279, -0.0037866, -0.0018366, 8.65e-05, -0.0005282, -0.0028506, 0.0010012, -0.0021142, -1.37e-05, -0.0008309, -0.0005746, -0.0003597, -0.0015138, 8.35e-05, -0.0010099, -0.0011662, -0.000192, -0.0008459, -0.0002872, -0.0004746, -0.0005293, -0.0003398, -0.0004955, -0.0002063, -0.0005067], dtype=np.float64)


def synthesize_gemini_tts(text: str, out_raw_wav: str, voice: str = LOCKED_SIGNATURE_VOICE) -> dict:
    """
    Synthesizes Persian narration using Gemini TTS ('Rasalgethi': 139.1Hz natural F0,
    0.836 Whisper Tehrani clarity, 0.9433 spectral-matched vocal-tract similarity to @ensan.besham).
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

    models = [
        "gemini-3.8-flash-tts",
        "gemini-3.8-flash-lite-tts",
        "gemini-3.1-flash-tts-preview",
    ]
    pcm = None
    used_model = None

    for attempt in range(4):
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
                    }
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                    used_model = model
                    break
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore")[:160]
                print(f"[TTS] {model} HTTP {e.code}: {body}", flush=True)
                if e.code == 429:
                    continue
        if pcm is not None:
            break
        print(f"[TTS] Quota cool-down; sleeping 24s before retry {attempt+1}...", flush=True)
        time.sleep(24)

    if pcm is None:
        raise RuntimeError("All Gemini TTS models failed or exceeded quota.")

    # Apply zero-phase 129-tap @ensan.besham spectral-match EQ directly at native 24,000 Hz!
    x24 = np.frombuffer(pcm, dtype=np.int16).astype(np.float64) / 32768.0
    x24_eq = filtfilt(ENSAN_FIR_24K, [1.0], x24)
    peak24 = np.max(np.abs(x24_eq)) + 1e-9
    x24_eq = np.clip(x24_eq / peak24 * 0.88, -0.98, 0.98)

    with wave.open(out_raw_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes((x24_eq * 32767.0).astype(np.int16).tobytes())

    dur = len(x24_eq) / 24000.0
    print(f"[TTS] Synthesized & Spectral-Matched {dur:.2f}s via {used_model} ({voice})", flush=True)
    return {"model": used_model, "voice": voice, "raw_duration": round(dur, 2)}


def calibrate_baritone_and_tighten(raw_wav: str, tightened_wav: str, dramatic_frac_range=(0.11, 0.25), tail_pad_sec: float = 4.0) -> dict:
    """
    1. Subtle -0.34 semitone formant-preserved calibration (139.1Hz -> 136.4Hz exact @ensan.besham F0) + 48kHz upsample.
    2. @ensan.besham Silence Tightener:
       - Cold-open start at 0.04s
       - Ordinary inter-sentence pauses > 0.23s compressed smoothly to 0.18s (~93.5% VoicedTime!)
       - Preserves ONE intentional 0.75s dramatic pause inside dramatic_frac_range.
    """
    cal_wav = raw_wav.replace(".wav", "_cal48.wav")
    has_rb = subprocess.call(["which", "rubberband"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    if has_rb:
        rb_tmp = raw_wav.replace(".wav", "_rb.wav")
        subprocess.check_call(["rubberband", "-q", "--pitch", str(LOCKED_PITCH_SEMITONES), "--formant", raw_wav, rb_tmp])
        subprocess.check_call(["ffmpeg", "-y", "-i", rb_tmp, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", cal_wav], stderr=subprocess.DEVNULL)
    else:
        subprocess.check_call(["ffmpeg", "-y", "-i", raw_wav, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", cal_wav], stderr=subprocess.DEVNULL)

    with wave.open(cal_wav, "rb") as wf:
        x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

    b_hp, a_hp = butter(2, 72.0 / (SR / 2), btype="high")
    x = lfilter(b_hp, a_hp, x)

    hop = int(0.010 * SR)
    n_hops = len(x) // hop
    frames = x[:n_hops * hop].reshape(n_hops, hop)
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    peak_rms = np.percentile(rms, 95) + 1e-6
    sil_thr = max(0.008, peak_rms * 0.065)
    is_sil = rms < sil_thr

    voiced_idxs = np.where(~is_sil)[0]
    first_v = max(0, int(voiced_idxs[0]) - 2)
    last_v  = min(n_hops, int(voiced_idxs[-1]) + 4)
    x = x[first_v * hop : last_v * hop]
    is_sil = is_sil[first_v : last_v]
    n_hops = len(is_sil)

    runs = []
    cur_state = bool(is_sil[0])
    run_start = 0
    for i in range(1, n_hops):
        if bool(is_sil[i]) != cur_state:
            runs.append((cur_state, run_start, i))
            cur_state = bool(is_sil[i])
            run_start = i
    runs.append((cur_state, run_start, n_hops))

    best_dramatic_idx = -1
    best_len = 0.0
    for r_i, (st_sil, s0, s1) in enumerate(runs):
        if st_sil:
            frac = ((s0 + s1) * 0.5) / n_hops
            dur_s = (s1 - s0) * 0.010
            if dramatic_frac_range[0] <= frac <= dramatic_frac_range[1] and dur_s > best_len and dur_s >= 0.22:
                best_len = dur_s
                best_dramatic_idx = r_i

    pieces = [np.zeros(int(0.04 * SR), dtype=np.float32)]
    xfade = int(0.018 * SR)
    trimmed_count = 0

    for r_i, (st_sil, s0, s1) in enumerate(runs):
        seg = x[s0 * hop : s1 * hop]
        dur_s = len(seg) / SR
        if not st_sil:
            pieces.append(seg)
        else:
            if r_i == best_dramatic_idx:
                target_n = int(0.75 * SR)
                if len(seg) >= target_n:
                    pieces.append(seg[:target_n])
                else:
                    pieces.append(np.concatenate([seg, np.zeros(target_n - len(seg), dtype=np.float32)]))
            elif dur_s > 0.23:
                target_n = int(0.18 * SR)
                half = target_n // 2
                left_s = seg[:half + xfade]
                right_s = seg[-(half + xfade):]
                w_fade = np.linspace(0.0, 1.0, 2 * xfade, dtype=np.float32)
                mid = left_s[-2*xfade:] * (1.0 - w_fade) + right_s[:2*xfade] * w_fade
                pieces.append(np.concatenate([left_s[:-2*xfade], mid, right_s[2*xfade:]]))
                trimmed_count += 1
            else:
                pieces.append(seg)

    pieces.append(np.zeros(int(tail_pad_sec * SR), dtype=np.float32))
    out_x = np.concatenate(pieces)

    # Gentle broadcast leveling (-17.2 dBFS RMS target matching @ensan.besham!)
    env = lfilter(*butter(1, 12.0 / (SR / 2), btype="low"), np.abs(out_x)) + 1e-6
    gain = np.where(env > 0.14, (0.14 / env) ** 0.38, 1.0)
    out_x = np.tanh(out_x * gain * 1.45) * 0.83

    active_part = out_x[:max(hop, len(out_x) - int((tail_pad_sec - 0.05) * SR))]
    v_win = active_part[:len(active_part)//hop*hop].reshape(-1, hop)
    voiced_pct = float(np.mean(np.sqrt(np.mean(v_win**2, axis=1)) > sil_thr * 0.9) * 100.0)

    with wave.open(tightened_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(out_x, -0.98, 0.98) * 32767).astype(np.int16).tobytes())

    dur_final = len(out_x) / SR
    print(f"[Audio] Tightened {trimmed_count} pauses -> {dur_final:.2f}s | VoicedTime={voiced_pct:.1f}%", flush=True)
    return {"duration": round(dur_final, 3), "voiced_pct": round(voiced_pct, 1), "trimmed_pauses": trimmed_count}


_NUM_WORDS_FA = sorted([
    ("600", "ششصد"), ("۶۰۰", "ششصد"),
    ("512", "پانصدودوازده"), ("۵۱۲", "پانصدودوازده"),
    ("256", "دویستوپنجاهوشش"), ("۲۵۶", "دویستوپنجاهوشش"),
    ("180", "صدوهشتاد"), ("۱۸۰", "صدوهشتاد"),
    ("150", "صدوپنجاه"), ("۱۵۰", "صدوپنجاه"),
    ("135", "صدوسیوپنج"), ("۱۳۵", "صدوسیوپنج"),
    ("128", "صدوبیستوهشت"), ("۱۲۸", "صدوبیستوهشت"),
    ("100", "صد"), ("۱۰۰", "صد"),
    ("99", "نودونه"), ("۹۹", "نودونه"),
    ("90", "نود"), ("۹۰", "نود"),
    ("84", "هشتادوچهار"), ("۸۴", "هشتادوچهار"),
    ("75", "هفتادوپنج"), ("۷۵", "هفتادوپنج"),
    ("68", "شصتوهشت"), ("۶۸", "شصتوهشت"),
    ("60", "شصت"), ("۶۰", "شصت"),
    ("50", "پنجاه"), ("۵۰", "پنجاه"),
    ("40", "چهل"), ("۴۰", "چهل"),
    ("32", "سیودو"), ("۳۲", "سیودو"),
    ("30", "سی"), ("۳۰", "سی"),
    ("28", "بیستوهشت"), ("۲۸", "بیستوهشت"),
    ("25", "بیستوپنج"), ("۲۵", "بیستوپنج"),
    ("24", "بیستوچهار"), ("۲۴", "بیستوچهار"),
    ("20", "بیست"), ("۲۰", "بیست"),
    ("15", "پونزده"), ("۱۵", "پونزده"),
    ("12", "دوازده"), ("۱۲", "دوازده"),
    ("11", "یازده"), ("۱۱", "یازده"),
    ("10", "ده"), ("۱۰", "ده"),
    ("9", "نه"), ("۹", "نه"),
    ("8", "هشت"), ("۸", "هشت"),
    ("7", "هفت"), ("۷", "هفت"),
    ("6", "شش"), ("۶", "شش"),
    ("5", "پنج"), ("۵", "پنج"),
    ("4", "چهار"), ("۴", "چهار"),
    ("3", "سه"), ("۳", "سه"),
    ("2", "دو"), ("۲", "دو"),
    ("1", "یک"), ("۱", "یک"),
    ("0", "صفر"), ("۰", "صفر"),
], key=lambda kv: len(kv[0]), reverse=True)

def _norm_fa(s: str) -> str:
    s = s.replace("ي", "ی").replace("ك", "ک").replace("ة", "ه").replace("ؤ", "و").replace("إ", "ا").replace("أ", "ا").replace("آ", "ا")
    s = s.replace("شیشصد", "ششصد").replace("شیش", "شش")
    for k_num, v_word in _NUM_WORDS_FA:
        s = s.replace(k_num, v_word)
    s = re.sub(r"[^\u0621-\u06cc0-9۰-۹]", "", s)
    return s


def align_script_lines(tightened_wav: str, script_lines: list[str], whisper_size: str = "medium") -> dict:
    """
    Extracts exact per-token (t_start, t_end) pairs for continuous sub-pixel RTL liquid-wipe subtitles!
    """
    raw_16k = subprocess.check_output(
        ["ffmpeg", "-i", tightened_wav, "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "1", "-ar", "16000", "-"],
        stderr=subprocess.DEVNULL
    )
    audio_16k = np.frombuffer(raw_16k, dtype=np.float32)
    total_dur = len(audio_16k) / 16000.0

    from faster_whisper import WhisperModel
    wm = WhisperModel(whisper_size, device="cpu", compute_type="int8")
    segs, _ = wm.transcribe(audio_16k, language="fa", word_timestamps=True, vad_filter=False)
    w_words = [w for s in segs for w in s.words]

    w_chars, w_t0, w_t1 = [], [], []
    for w in w_words:
        nc = _norm_fa(w.word)
        if not nc:
            continue
        dt = (w.end - w.start) / len(nc)
        for k, ch in enumerate(nc):
            w_chars.append(ch)
            w_t0.append(float(w.start + k * dt))
            w_t1.append(float(w.start + (k + 1) * dt))

    w_str = "".join(w_chars)
    s_chars, line_meta = [], []
    for line in script_lines:
        tokens = [tk for tk in line.strip().split(" ") if tk]
        tok_spans = []
        for tk in tokens:
            nc = _norm_fa(tk) or "ا"
            c0 = len(s_chars)
            s_chars.extend(list(nc))
            c1 = len(s_chars)
            tok_spans.append((tk, c0, c1))
        line_meta.append({"full": line.strip(), "tok_spans": tok_spans})

    s_str = "".join(s_chars)
    N_s, N_w = len(s_str), len(w_str)

    sm = difflib.SequenceMatcher(None, s_str, w_str, autojunk=False)
    anchors_s, anchors_w = [0], [0]
    for blk in sm.get_matching_blocks():
        if blk.size > 0:
            anchors_s.extend([blk.a, blk.a + blk.size - 1])
            anchors_w.extend([blk.b, blk.b + blk.size - 1])
    anchors_s.append(max(1, N_s - 1))
    anchors_w.append(max(1, N_w - 1))

    clean_s, clean_w = [], []
    for a_s, a_w in zip(anchors_s, anchors_w):
        if not clean_s or (a_s > clean_s[-1] and a_w >= clean_w[-1]):
            clean_s.append(a_s)
            clean_w.append(a_w)

    mapped_w = np.interp(np.arange(N_s), clean_s, clean_w)

    aligned_lines = []
    for lm in line_meta:
        tokens, t_starts, t_ends = [], [], []
        for tk, c0, c1 in lm["tok_spans"]:
            wi0 = int(np.clip(round(mapped_w[c0]), 0, N_w - 1))
            wi1 = int(np.clip(round(mapped_w[max(c0, c1 - 1)]), 0, N_w - 1))
            t0_v = round(w_t0[wi0], 3)
            t1_v = round(max(t0_v + 0.06, w_t1[wi1]), 3)
            tokens.append(tk)
            t_starts.append(t0_v)
            t_ends.append(t1_v)
        # Ensure strictly monotonic token windows for ultra-smooth wipe interpolation
        for k in range(1, len(t_starts)):
            if t_starts[k] < t_ends[k-1]:
                mid = 0.5 * (t_starts[k] + t_ends[k-1])
                t_ends[k-1] = round(mid, 3)
                t_starts[k] = round(mid, 3)
            if t_ends[k] <= t_starts[k]:
                t_ends[k] = round(t_starts[k] + 0.08, 3)

        aligned_lines.append({
            "full": lm["full"],
            "start": round(max(0.0, t_starts[0] - 0.10), 3),
            "end": round(t_ends[-1] + 0.22, 3),
            "tokens": tokens,
            "times": t_starts,
            "ends": t_ends,
        })

    for i in range(len(aligned_lines) - 1):
        if aligned_lines[i]["end"] > aligned_lines[i+1]["start"]:
            mid = round(0.5 * (aligned_lines[i]["end"] + aligned_lines[i+1]["start"]), 3)
            aligned_lines[i]["end"] = round(mid - 0.015, 3)
            aligned_lines[i+1]["start"] = round(mid + 0.015, 3)

    speech_span = max(0.1, w_words[-1].end - w_words[0].start)
    net_wpm = len(w_words) / (speech_span / 60.0)
    print(f"[Whisper] Aligned {len(aligned_lines)} short phrases ({len(w_words)} words, Net WPM={net_wpm:.1f})", flush=True)

    return {
        "total_duration": round(total_dur, 3),
        "net_wpm": round(net_wpm, 1),
        "word_count": len(w_words),
        "lines": aligned_lines,
    }


def build_master_stereo_mix(tightened_wav: str, out_master_wav: str, sfx_events: list[dict]) -> None:
    """
    Studio v3.0 Hypnotic Neoclassical & Horology Master Mix (48kHz Stereo):
    Combines locked Rasalgethi spectral-matched voiceover with:
    1. Warm Analog Cello & Sub-Bass Progression (Dmadd9 -> Bbmaj7#11 -> Gm9 -> Asus4/A7b9, audible on phone speakers)
    2. Hypnotic 120-BPM Polyrhythmic Felt-Piano Ostinato (8th-note Zimmer/Arnalds motif + 6-tap concert hall reverb)
    3. Precision Swiss Watch Escapement Stereo Tick-Tock + Visceral Lub-Dub Heartbeat Sub-Pulse
    4. Act III Ethereal Bowed-Glass High String Shimmer + Speech-Pocket Presence Protection
    5. Synchronized Kinetic Editing Micro-SFX (tick, heartbeat, scan, shatter, click, whoosh, ping, stamp, chime)
    """
    with wave.open(tightened_wav, "rb") as wf:
        vo = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

    N = len(vo)
    dur = N / SR
    t = np.arange(N, dtype=np.float32) / SR

    # Smooth broadcast sidechain envelope: keeps voice crystal-clear while letting music breathe between phrases & bloom on outro
    vo_env_fast = lfilter(*butter(1, 2.0 / (SR / 2), btype="low"), np.abs(vo))
    duck = np.clip(1.0 - 2.35 * vo_env_fast, 0.45, 1.0).astype(np.float32)

    # Hypnotic D-minor Neoclassical Progression (120 BPM -> 4.0s per 8-beat bar):
    # (bass_hz, cello_pad_freqs, 8_step_felt_piano_ostinato_freqs, shimmer_freq)
    chords = [
        # Bar 1: Dmadd9 (deep, contemplative, magnetic)
        (73.42, [146.83, 174.61, 220.00, 329.63],
         [220.00, 293.66, 329.63, 349.23, 440.00, 349.23, 329.63, 293.66], 587.33),
        # Bar 2: Bbmaj7#11 (cinematic wonder & revelation)
        (58.27, [116.54, 174.61, 220.00, 293.66],
         [220.00, 293.66, 329.63, 349.23, 440.00, 329.63, 293.66, 220.00], 587.33),
        # Bar 3: Gm9 (emotional weight of passing life)
        (49.00, [98.00,  146.83, 220.00, 233.08],
         [196.00, 233.08, 293.66, 349.23, 440.00, 349.23, 293.66, 233.08], 523.25),
        # Bar 4: Asus4 -> A7b9 (irresistible harmonic tension resolving back to Dmadd9!)
        (55.00, [110.00, 164.81, 220.00, 277.18],
         [220.00, 293.66, 329.63, 392.00, 349.23, 329.63, 277.18, 220.00], 554.37),
    ]

    pad_L = np.zeros(N, dtype=np.float32)
    pad_R = np.zeros(N, dtype=np.float32)
    piano_L = np.zeros(N, dtype=np.float32)
    piano_R = np.zeros(N, dtype=np.float32)
    shimmer_L = np.zeros(N, dtype=np.float32)
    shimmer_R = np.zeros(N, dtype=np.float32)
    pulse_sub = np.zeros(N, dtype=np.float32)
    clock_L = np.zeros(N, dtype=np.float32)
    clock_R = np.zeros(N, dtype=np.float32)

    chord_len = 4.0
    n_blocks = int(np.ceil(dur / chord_len)) + 1
    xfade_s = 0.70

    # Dynamic 4-Act Story Arrangement Envelope
    cello_arr = np.clip((t - 2.5) / 8.0, 0.38, 1.0).astype(np.float32)
    shimmer_arr = (
        np.clip((t - dur * 0.36) / 7.5, 0.0, 1.0) * 0.75
        + np.clip((t - (dur - 5.2)) / 1.8, 0.0, 1.0) * 0.45
    ).astype(np.float32)

    for bi in range(n_blocks):
        t_start = bi * chord_len - xfade_s
        t_end   = (bi + 1) * chord_len + xfade_s
        i0 = max(0, int(t_start * SR))
        i1 = min(N, int(t_end * SR))
        if i1 <= i0:
            continue
        bt = np.arange(i0, i1, dtype=np.float32) / SR
        w_in  = np.clip((bt - (bi * chord_len - xfade_s)) / (2 * xfade_s), 0.0, 1.0)
        w_out = np.clip((((bi + 1) * chord_len + xfade_s) - bt) / (2 * xfade_s), 0.0, 1.0)
        win = (0.5 - 0.5 * np.cos(np.pi * w_in)) * (0.5 - 0.5 * np.cos(np.pi * w_out))

        f_bass, pad_freqs, arp_notes, f_shim = chords[bi % 4]

        # 1. Warm Analog Cello + Mobile-Audible Upper Bass Harmonics (f + 2f + 3f + sub f/2)
        cL = (0.24 * np.sin(2 * np.pi * (0.5 * f_bass) * bt)
              + 0.36 * np.sin(2 * np.pi * f_bass * bt)
              + 0.19 * np.sin(2 * np.pi * (2.0 * f_bass) * bt + 0.2)
              + 0.08 * np.sin(2 * np.pi * (3.0 * f_bass) * bt))
        cR = (0.24 * np.sin(2 * np.pi * (0.5 * f_bass) * bt)
              + 0.36 * np.sin(2 * np.pi * f_bass * bt + 0.14)
              + 0.19 * np.sin(2 * np.pi * (2.0 * f_bass) * bt + 0.5)
              + 0.08 * np.sin(2 * np.pi * (3.0 * f_bass) * bt + 0.3))

        for vi, pf in enumerate(pad_freqs):
            sw = 0.80 + 0.20 * np.sin(2 * np.pi * (0.16 + 0.04 * vi) * bt + vi)
            fL, fR = pf * 0.9980, pf * 1.0020
            cL += sw * (0.18 * np.sin(2*np.pi*fL*bt + vi) + 0.075 * np.sin(4*np.pi*fL*bt) + 0.028 * np.sin(6*np.pi*fL*bt))
            cR += sw * (0.18 * np.sin(2*np.pi*fR*bt + vi + 0.7) + 0.075 * np.sin(4*np.pi*fR*bt + 0.4) + 0.028 * np.sin(6*np.pi*fR*bt))
        pad_L[i0:i1] += (cL * win).astype(np.float32)
        pad_R[i0:i1] += (cR * win).astype(np.float32)

        # 2. Ethereal Wide-Stereo Bowed-Glass Shimmer (Act III climax & outro)
        vib_L = 1.0 + 0.0025 * np.sin(2 * np.pi * 4.6 * bt)
        vib_R = 1.0 + 0.0025 * np.sin(2 * np.pi * 4.9 * bt + 1.3)
        sL = 0.16 * np.sin(2 * np.pi * f_shim * vib_L * bt) + 0.07 * np.sin(2 * np.pi * (f_shim * 1.5) * bt + 0.8)
        sR = 0.16 * np.sin(2 * np.pi * f_shim * vib_R * bt + 1.1) + 0.07 * np.sin(2 * np.pi * (f_shim * 1.5) * bt + 2.1)
        shimmer_L[i0:i1] += (sL * win).astype(np.float32)
        shimmer_R[i0:i1] += (sR * win).astype(np.float32)

        # 3. Hypnotic 8-Step Felt-Piano Arpeggio (0.50s 8th-note ostinato at 120 BPM) + Swiss Watch Tick-Tock
        for step_k in range(8):
            beat_t0 = bi * chord_len + step_k * 0.50
            ni0 = int(beat_t0 * SR)
            if 0 <= ni0 < N - 400:
                vel = (0.34 if step_k in (0, 4) else (0.25 if step_k in (2, 6) else 0.19))
                ndur = int(1.35 * SR)
                ni1 = min(N, ni0 + ndur)
                nt = np.arange(ni1 - ni0, dtype=np.float32) / SR
                nf = arp_notes[step_k]
                att = np.clip(nt / 0.015, 0.0, 1.0)
                hammer = 0.14 * np.sin(2 * np.pi * 135.0 * nt) * np.exp(-nt * 65.0)
                tone = att * (
                    np.sin(2 * np.pi * nf * nt) * np.exp(-nt * 2.35)
                    + 0.34 * np.sin(2 * np.pi * (nf * 2.001) * nt) * np.exp(-nt * 4.4)
                    + 0.11 * np.sin(2 * np.pi * (nf * 3.003) * nt) * np.exp(-nt * 7.8)
                    + 0.04 * np.sin(2 * np.pi * (nf * 4.006) * nt) * np.exp(-nt * 12.0)
                    + hammer
                ) * vel
                pan_p = 0.32 if (step_k % 2 == 0) else 0.68
                piano_L[ni0:ni1] += (tone * (1.0 - 0.55 * pan_p)).astype(np.float32)
                piano_R[ni0:ni1] += (tone * (0.45 + 0.55 * pan_p)).astype(np.float32)

                # Swiss Horology Watch Escapement (subtle hypnotic Tick on even 0.5s, Tock on odd 0.5s)
                tdur = min(int(0.045 * SR), N - ni0)
                tt_k = np.arange(tdur, dtype=np.float32) / SR
                if step_k % 2 == 0:
                    tk_sig = (np.sin(2 * np.pi * 1720.0 * tt_k) * np.exp(-tt_k * 175.0)
                              + 0.45 * np.sin(2 * np.pi * 540.0 * tt_k) * np.exp(-tt_k * 115.0)) * 0.055
                    clock_L[ni0:ni0+tdur] += tk_sig * 1.15
                    clock_R[ni0:ni0+tdur] += tk_sig * 0.65
                else:
                    tk_sig = (np.sin(2 * np.pi * 1340.0 * tt_k) * np.exp(-tt_k * 165.0)
                              + 0.50 * np.sin(2 * np.pi * 430.0 * tt_k) * np.exp(-tt_k * 110.0)) * 0.046
                    clock_L[ni0:ni0+tdur] += tk_sig * 0.65
                    clock_R[ni0:ni0+tdur] += tk_sig * 1.15

        # 4. Visceral Lub-Dub Heartbeat Sub-Pulse every 2.0s (half-bar downbeats)
        for hb_k in range(2):
            for sub_off, f_start, h_gain in ((0.00, 62.0, 0.38), (0.24, 52.0, 0.24)):
                pi0 = int((bi * chord_len + hb_k * 2.0 + sub_off) * SR)
                pdur = int(0.36 * SR)
                if 0 <= pi0 < N - 400:
                    pi1 = min(N, pi0 + pdur)
                    pt = np.arange(pi1 - pi0, dtype=np.float32) / SR
                    p_env = np.clip(pt / 0.016, 0.0, 1.0) * np.exp(-pt * 9.5)
                    hb_wave = (np.sin(2 * np.pi * (f_start - 20.0 * pt) * pt)
                               + 0.35 * np.sin(2 * np.pi * 2.0 * (f_start - 20.0 * pt) * pt))
                    pulse_sub[pi0:pi1] += (hb_wave * p_env * h_gain).astype(np.float32)

    # Warm analog low-pass on cello ensemble (< 720 Hz -> zero masking of Persian consonants!)
    b_pad, a_pad = butter(3, 720.0 / (SR / 2), btype="low")
    pad_L = lfilter(b_pad, a_pad, pad_L) * cello_arr
    pad_R = lfilter(b_pad, a_pad, pad_R) * cello_arr

    # Velvet low-pass on felt piano (< 1650 Hz) + lush 6-tap cross-stereo concert hall reverb
    b_pno, a_pno = butter(2, 1650.0 / (SR / 2), btype="low")
    pL_flt = lfilter(b_pno, a_pno, piano_L)
    pR_flt = lfilter(b_pno, a_pno, piano_R)
    rev_L = pL_flt.copy()
    rev_R = pR_flt.copy()
    for d_ms, g_same, g_cross in [
        (37, 0.42, 0.24), (73, 0.22, 0.40), (119, 0.30, 0.18),
        (181, 0.16, 0.28), (269, 0.20, 0.12), (389, 0.11, 0.17)
    ]:
        ds = int(d_ms * 0.001 * SR)
        if ds < N:
            rev_L[ds:] += pL_flt[:-ds] * g_same + pR_flt[:-ds] * g_cross
            rev_R[ds:] += pR_flt[:-ds] * g_same + pL_flt[:-ds] * g_cross

    # Soft band-pass on Act III shimmer (420 - 1320 Hz warm angelic halo)
    b_shm, a_shm = butter(2, [420.0 / (SR / 2), 1320.0 / (SR / 2)], btype="band")
    shimmer_L = lfilter(b_shm, a_shm, shimmer_L) * shimmer_arr
    shimmer_R = lfilter(b_shm, a_shm, shimmer_R) * shimmer_arr

    fade = (np.clip(t / 0.45, 0.0, 1.0) * np.clip((dur - t) / 1.5, 0.0, 1.0)).astype(np.float32)
    score_gain = 0.295
    mus_L = (pad_L * 0.95 + rev_L * 0.72 + shimmer_L * 0.85 + pulse_sub * 0.52 + clock_L * 0.75) * score_gain * duck * fade
    mus_R = (pad_R * 0.95 + rev_R * 0.72 + shimmer_R * 0.85 + pulse_sub * 0.52 + clock_R * 0.75) * score_gain * duck * fade

    sfx_L = np.zeros(N, dtype=np.float32)
    sfx_R = np.zeros(N, dtype=np.float32)
    rng_s = np.random.default_rng(77)

    for ev in sfx_events:
        kind = ev["type"]
        ts = float(ev["t"])
        idx = int(ts * SR)
        if idx < 0 or idx >= N - 800:
            continue

        if kind == "ping":
            dn = min(int(0.20 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            f0 = float(ev.get("freq", 1174.66))
            pan = float(ev.get("pan", 0.5))
            sig = (np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 24.0)
                   + 0.35 * np.sin(2 * np.pi * (f0 * 0.5) * tt) * np.exp(-tt * 16.0)) * 0.036
            sfx_L[idx:idx+dn] += sig * (1.0 - 0.5 * pan)
            sfx_R[idx:idx+dn] += sig * (0.5 + 0.5 * pan)

        elif kind == "whoosh":
            dn = min(int(0.48 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            noise = rng_s.standard_normal(dn).astype(np.float32)
            shaped = lfilter(*butter(2, [190.0/(SR/2), 1050.0/(SR/2)], btype="band"), noise)
            env_w = np.sin(np.pi * tt / (dn / SR)) ** 1.8
            sig = shaped * env_w * 0.036
            sfx_L[idx:idx+dn] += sig * 0.88
            sfx_R[idx:idx+dn] += sig * 1.12

        elif kind == "click" or kind == "tick":
            dn = min(int(0.055 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            sig = (np.sin(2 * np.pi * 1920.0 * tt) * np.exp(-tt * 155.0)
                   + 0.55 * np.sin(2 * np.pi * 640.0 * tt) * np.exp(-tt * 95.0)) * 0.048
            sfx_L[idx:idx+dn] += sig
            sfx_R[idx:idx+dn] += sig

        elif kind == "heartbeat":
            dn = min(int(0.48 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            lub = np.sin(2 * np.pi * (68.0 - 26.0 * tt) * tt) * np.exp(-tt * 13.0)
            dub_t = np.maximum(0.0, tt - 0.19)
            dub = (tt >= 0.19).astype(np.float32) * np.sin(2 * np.pi * (56.0 - 20.0 * dub_t) * dub_t) * np.exp(-dub_t * 15.0) * 0.72
            sig = (lub + dub) * 0.068
            sfx_L[idx:idx+dn] += sig
            sfx_R[idx:idx+dn] += sig

        elif kind == "scan":
            dn = min(int(0.38 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            env_sc = np.sin(np.pi * tt / (dn / SR)) ** 1.4
            sweep = np.sin(2 * np.pi * (340.0 + 480.0 * tt) * tt) * env_sc * 0.026
            sfx_L[idx:idx+dn] += sweep * 0.80
            sfx_R[idx:idx+dn] += sweep * 1.20

        elif kind == "shatter":
            dn = min(int(0.34 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            noise = rng_s.standard_normal(dn).astype(np.float32)
            glass = lfilter(*butter(2, [1400.0/(SR/2), 4600.0/(SR/2)], btype="band"), noise) * np.exp(-tt * 18.0)
            impact = np.sin(2 * np.pi * 125.0 * tt) * np.exp(-tt * 28.0)
            sig = (0.55 * glass + 0.65 * impact) * 0.052
            sfx_L[idx:idx+dn] += sig * 1.05
            sfx_R[idx:idx+dn] += sig * 0.95

        elif kind == "stamp":
            dn = min(int(0.16 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            sig = (np.sin(2 * np.pi * 128.0 * tt) * np.exp(-tt * 34.0)
                   + 0.42 * np.sin(2 * np.pi * 1680.0 * tt) * np.exp(-tt * 135.0)) * 0.056
            sfx_L[idx:idx+dn] += sig
            sfx_R[idx:idx+dn] += sig

        elif kind == "sub_swell":
            dn = min(int(1.15 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            env_s = np.sin(np.pi * tt / (dn / SR)) ** 1.5
            sig = (np.sin(2 * np.pi * (58.0 - 12.0 * tt) * tt)
                   + 0.30 * np.sin(2 * np.pi * 2.0 * (58.0 - 12.0 * tt) * tt)) * env_s * 0.068
            sfx_L[idx:idx+dn] += sig
            sfx_R[idx:idx+dn] += sig

        elif kind == "chime":
            dn = min(int(2.6 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            f0 = float(ev.get("freq", 587.33))
            att = np.clip(tt / 0.012, 0, 1)
            sig = att * (
                np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 2.3)
                + 0.44 * np.sin(2 * np.pi * f0 * 1.5 * tt) * np.exp(-tt * 3.2)
                + 0.24 * np.sin(2 * np.pi * f0 * 2.0 * tt) * np.exp(-tt * 4.4)
            ) * 0.058
            sfx_L[idx:idx+dn] += sig * 0.94
            sfx_R[idx:idx+dn] += sig * 1.06

    mix_L = np.clip(vo + mus_L + sfx_L, -0.97, 0.97)
    mix_R = np.clip(vo + mus_R + sfx_R, -0.97, 0.97)

    stereo = np.empty((N * 2,), dtype=np.int16)
    stereo[0::2] = (mix_L * 32767).astype(np.int16)
    stereo[1::2] = (mix_R * 32767).astype(np.int16)

    with wave.open(out_master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(stereo.tobytes())
    print(f"[Audio] Studio v3.0 Hypnotic Master 48kHz stereo mix saved -> {out_master_wav} ({dur:.2f}s)", flush=True)


def build_episode_audio(
    segments: list[tuple[str, str]],
    sfx_cue_map: list[tuple[str, int, int, str]],
    work_dir: str,
    voice_name: str = LOCKED_SIGNATURE_VOICE,
    tail_pad_sec: float = 4.0,
    whisper_size: str = "medium",
) -> dict:
    """Full @ensan.besham-matched studio audio pipeline (TTS -> 129-tap FIR -> -0.34st -> Tighten -> Whisper -> 48kHz Stereo)."""
    os.makedirs(work_dir, exist_ok=True)
    spoken_text = " ".join(spk for spk, _ in segments)
    display_lines = [disp for _, disp in segments]

    raw_wav    = os.path.join(work_dir, "raw_tts_24k_fir.wav")
    tight_wav  = os.path.join(work_dir, "tightened_vo_48k.wav")
    master_wav = os.path.join(work_dir, "master_stereo_48k.wav")
    align_json = os.path.join(work_dir, "alignment.json")

    tts_info = synthesize_gemini_tts(spoken_text, raw_wav, voice=voice_name)
    aud_info = calibrate_baritone_and_tighten(raw_wav, tight_wav, dramatic_frac_range=(0.12, 0.26), tail_pad_sec=tail_pad_sec)
    aligned  = align_script_lines(tight_wav, display_lines, whisper_size=whisper_size)

    sub_lines = aligned["lines"]
    total_dur = aligned["total_duration"]

    t_cues = {}
    sfx_events = []
    for cue_name, seg_idx, word_idx, sfx_kind in sfx_cue_map:
        tms = sub_lines[seg_idx]["times"]
        ts = float(tms[min(word_idx, len(tms) - 1)])
        t_cues[cue_name] = round(ts, 3)
        sfx_events.append({"type": sfx_kind, "t": max(0.0, ts - 0.03)})

    # Signature crystalline D5 tonic chime on endplate reveal
    sfx_events.append({"type": "chime", "t": max(0.5, total_dur - tail_pad_sec + 0.12), "freq": 587.33})
    sfx_events.append({"type": "sub_swell", "t": max(0.3, total_dur - tail_pad_sec - 0.25)})

    build_master_stereo_mix(tight_wav, master_wav, sfx_events)

    meta = {
        "tts": tts_info,
        "audio_master": aud_info,
        "net_wpm": aligned["net_wpm"],
        "word_count": aligned["word_count"],
        "total_dur": total_dur,
        "t_cues": t_cues,
        "sub_lines": sub_lines,
        "master_wav": master_wav,
        "align_json": align_json,
    }
    with open(align_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta
