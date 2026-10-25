import os, re, json, time, wave, base64, difflib, subprocess, urllib.request, urllib.error
import numpy as np
from scipy.signal import butter, lfilter, resample_poly
from faster_whisper import WhisperModel

SR = 48000

def synthesize_gemini_tts(text: str, out_raw_wav: str, voice: str = "Iapetus") -> dict:
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

    for attempt in range(3):
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
                body = e.read().decode("utf-8", errors="ignore")[:180]
                print(f"[TTS] {model} HTTP {e.code}: {body}", flush=True)
                if e.code == 429:
                    continue
        if pcm is not None:
            break
        print(f"[TTS] Rate limit hit across models; sleeping 22s before retry {attempt+1}...", flush=True)
        time.sleep(22)

    if pcm is None:
        raise RuntimeError("All Gemini TTS models failed or exceeded quota.")

    with wave.open(out_raw_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm)

    dur = len(pcm) / (24000 * 2)
    print(f"[TTS] Synthesized {dur:.2f}s via {used_model} ({voice})", flush=True)
    return {"model": used_model, "voice": voice, "raw_duration": dur}


def calibrate_baritone_and_tighten(raw_wav: str, tightened_wav: str, dramatic_frac_range=(0.10, 0.24)) -> dict:
    """
    1. Formant-preserving -0.95 semitone baritone calibration via rubberband CLI (if available) + 48kHz resample.
    2. @ensan.besham Silence Tightener:
       - Cold-open start at 0.04s
       - Ordinary inter-sentence pauses > 0.24s compressed to 0.19s (achieving ~92-94% VoicedTime!)
       - Preserves ONE intentional 0.72s dramatic pause inside dramatic_frac_range (after hook question).
    """
    cal_wav = raw_wav.replace(".wav", "_cal48.wav")
    has_rb = subprocess.call(["which", "rubberband"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    if has_rb:
        rb_tmp = raw_wav.replace(".wav", "_rb.wav")
        subprocess.check_call(["rubberband", "-q", "--pitch", "-0.90", "--formant", raw_wav, rb_tmp])
        subprocess.check_call(["ffmpeg", "-y", "-i", rb_tmp, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", cal_wav], stderr=subprocess.DEVNULL)
    else:
        subprocess.check_call(["ffmpeg", "-y", "-i", raw_wav, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", cal_wav], stderr=subprocess.DEVNULL)

    with wave.open(cal_wav, "rb") as wf:
        x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

    # High-pass at 72Hz to remove rumble
    b_hp, a_hp = butter(2, 72.0 / (SR / 2), btype="high")
    x = lfilter(b_hp, a_hp, x)

    # Frame RMS in 10ms hops
    hop = int(0.010 * SR) # 480 samples
    n_hops = len(x) // hop
    frames = x[:n_hops * hop].reshape(n_hops, hop)
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    peak_rms = np.percentile(rms, 95) + 1e-6
    sil_thr = max(0.008, peak_rms * 0.065)
    is_sil = rms < sil_thr

    # Trim leading & trailing silence first
    voiced_idxs = np.where(~is_sil)[0]
    first_v = max(0, int(voiced_idxs[0]) - 2)
    last_v  = min(n_hops, int(voiced_idxs[-1]) + 4)
    x = x[first_v * hop : last_v * hop]
    is_sil = is_sil[first_v : last_v]
    n_hops = len(is_sil)

    # Identify contiguous runs of silence / speech
    runs = []
    cur_state = bool(is_sil[0])
    run_start = 0
    for i in range(1, n_hops):
        if bool(is_sil[i]) != cur_state:
            runs.append((cur_state, run_start, i))
            cur_state = bool(is_sil[i])
            run_start = i
    runs.append((cur_state, run_start, n_hops))

    # Find the primary dramatic pause inside dramatic_frac_range
    best_dramatic_idx = -1
    best_len = 0
    for r_i, (st_sil, s0, s1) in enumerate(runs):
        if st_sil:
            frac = ((s0 + s1) * 0.5) / n_hops
            dur_s = (s1 - s0) * 0.010
            if dramatic_frac_range[0] <= frac <= dramatic_frac_range[1] and dur_s > best_len and dur_s >= 0.25:
                best_len = dur_s
                best_dramatic_idx = r_i

    # Reconstruct waveform with smooth 20ms crossfades on shortened silences
    pieces = [np.zeros(int(0.04 * SR), dtype=np.float32)] # Exact 0.04s Cold-Open!
    xfade = int(0.018 * SR)
    trimmed_count = 0

    for r_i, (st_sil, s0, s1) in enumerate(runs):
        seg = x[s0 * hop : s1 * hop]
        dur_s = len(seg) / SR
        if not st_sil:
            pieces.append(seg)
        else:
            if r_i == best_dramatic_idx:
                # Shape dramatic rhetorical pause to exact 0.72s
                target_n = int(0.72 * SR)
                if len(seg) >= target_n:
                    pieces.append(seg[:target_n])
                else:
                    pad_n = target_n - len(seg)
                    pieces.append(np.concatenate([seg, np.zeros(pad_n, dtype=np.float32)]))
            elif dur_s > 0.24:
                # Tighten dead air down to crisp 0.19s (@ensan.besham signature pacing!)
                target_n = int(0.19 * SR)
                half = target_n // 2
                left_s = seg[:half + xfade]
                right_s = seg[-(half + xfade):]
                w_fade = np.linspace(0.0, 1.0, 2 * xfade, dtype=np.float32)
                mid = left_s[-2*xfade:] * (1.0 - w_fade) + right_s[:2*xfade] * w_fade
                tight_seg = np.concatenate([left_s[:-2*xfade], mid, right_s[2*xfade:]])
                pieces.append(tight_seg)
                trimmed_count += 1
            else:
                pieces.append(seg)

    # Append 1.35s outro tail for brand lockup
    pieces.append(np.zeros(int(1.35 * SR), dtype=np.float32))
    out_x = np.concatenate(pieces)

    # Warm broadcast compressor + limiter
    env = lfilter(*butter(1, 14.0 / (SR / 2), btype="low"), np.abs(out_x)) + 1e-6
    gain = np.where(env > 0.15, (0.15 / env) ** 0.36, 1.0)
    out_x = np.tanh(out_x * gain * 1.48) * 0.84

    # Measure final VoicedTime ratio (excluding outro tail)
    active_part = out_x[:len(out_x) - int(1.30 * SR)]
    v_win = active_part[:len(active_part)//hop*hop].reshape(-1, hop)
    voiced_pct = float(np.mean(np.sqrt(np.mean(v_win**2, axis=1)) > sil_thr * 0.9) * 100.0)

    with wave.open(tightened_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(out_x, -0.98, 0.98) * 32767).astype(np.int16).tobytes())

    dur_final = len(out_x) / SR
    print(f"[Audio] Tightened {trimmed_count} pauses -> {dur_final:.2f}s | VoicedTime={voiced_pct:.1f}%", flush=True)
    return {"duration": dur_final, "voiced_pct": round(voiced_pct, 1), "trimmed_pauses": trimmed_count}


def _norm_fa(s: str) -> str:
    # Normalize Persian/Arabic characters and strip punctuation/ZWNJ/spaces for character alignment
    s = s.replace("ي", "ی").replace("ك", "ک").replace("ة", "ه").replace("ؤ", "و").replace("إ", "ا").replace("أ", "ا").replace("آ", "ا")
    # Convert digits just in case Whisper emits ASCII digits
    s = s.replace("99", "نودونه").replace("11", "یازده").replace("5", "پنج")
    s = re.sub(r"[^\u0621-\u06cc0-9۰-۹]", "", s)
    return s


def align_script_lines(tightened_wav: str, script_lines: list[str], whisper_size: str = "medium") -> dict:
    """
    Runs faster-whisper on tightened_wav and aligns every line & token in script_lines
    to exact millisecond start/end timestamps via character-level SequenceMatcher!
    """
    raw_16k = subprocess.check_output(
        ["ffmpeg", "-i", tightened_wav, "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "1", "-ar", "16000", "-"],
        stderr=subprocess.DEVNULL
    )
    audio_16k = np.frombuffer(raw_16k, dtype=np.float32)
    total_dur = len(audio_16k) / 16000.0

    print(f"[Whisper] Loading faster-whisper '{whisper_size}' for forced word alignment...", flush=True)
    wm = WhisperModel(whisper_size, device="cpu", compute_type="int8")
    segs, _ = wm.transcribe(audio_16k, language="fa", word_timestamps=True, vad_filter=False)
    w_words = [w for s in segs for w in s.words]

    # Build Whisper normalized char timeline: each char gets (t0, t1)
    w_chars = []
    w_t0 = []
    w_t1 = []
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

    # Build Script normalized char string & record token char spans
    s_chars = []
    line_meta = []
    for line in script_lines:
        tokens = [tk for tk in line.strip().split(" ") if tk]
        tok_spans = []
        for tk in tokens:
            nc = _norm_fa(tk)
            if not nc:
                nc = "ا"
            c0 = len(s_chars)
            s_chars.extend(list(nc))
            c1 = len(s_chars)
            tok_spans.append((tk, c0, c1))
        line_meta.append({"full": line.strip(), "tok_spans": tok_spans})

    s_str = "".join(s_chars)
    N_s = len(s_str)
    N_w = len(w_str)

    # Map every script char index -> whisper char index via SequenceMatcher anchor points + linear interp
    sm = difflib.SequenceMatcher(None, s_str, w_str, autojunk=False)
    anchors_s = [0]
    anchors_w = [0]
    for blk in sm.get_matching_blocks():
        if blk.size > 0:
            anchors_s.append(blk.a)
            anchors_w.append(blk.b)
            anchors_s.append(blk.a + blk.size - 1)
            anchors_w.append(blk.b + blk.size - 1)
    anchors_s.append(max(1, N_s - 1))
    anchors_w.append(max(1, N_w - 1))

    # Deduplicate monotonic anchors
    clean_s, clean_w = [], []
    for a_s, a_w in zip(anchors_s, anchors_w):
        if not clean_s or (a_s > clean_s[-1] and a_w >= clean_w[-1]):
            clean_s.append(a_s)
            clean_w.append(a_w)

    mapped_w = np.interp(np.arange(N_s), clean_s, clean_w)

    aligned_lines = []
    for lm in line_meta:
        tokens = []
        times = []
        t_ends = []
        for tk, c0, c1 in lm["tok_spans"]:
            wi0 = int(np.clip(round(mapped_w[c0]), 0, N_w - 1))
            wi1 = int(np.clip(round(mapped_w[max(c0, c1 - 1)]), 0, N_w - 1))
            tokens.append(tk)
            times.append(round(w_t0[wi0], 3))
            t_ends.append(round(w_t1[wi1], 3))
        aligned_lines.append({
            "full": lm["full"],
            "start": round(max(0.0, times[0] - 0.06), 3),
            "end": round(t_ends[-1] + 0.16, 3),
            "tokens": tokens,
            "times": times,
        })

    # Prevent tiny overlaps between consecutive subtitle lines
    for i in range(len(aligned_lines) - 1):
        gap_mid = 0.5 * (aligned_lines[i]["end"] + aligned_lines[i+1]["start"])
        if aligned_lines[i]["end"] > aligned_lines[i+1]["start"]:
            aligned_lines[i]["end"] = round(gap_mid - 0.01, 3)
            aligned_lines[i+1]["start"] = round(gap_mid + 0.01, 3)

    speech_span = max(0.1, w_words[-1].end - w_words[0].start)
    net_wpm = len(w_words) / (speech_span / 60.0)
    print(f"[Whisper] Aligned {len(aligned_lines)} lines ({len(w_words)} words, Net WPM={net_wpm:.1f})", flush=True)

    return {
        "total_duration": round(total_dur, 3),
        "net_wpm": round(net_wpm, 1),
        "word_count": len(w_words),
        "lines": aligned_lines,
    }


def build_master_stereo_mix(tightened_wav: str, out_master_wav: str, sfx_events: list[dict]) -> None:
    """
    Combines 48kHz tightened voiceover with:
    - -32 dBFS Dark C-minor9 Ambient Drone (sidechain-ducked under speech, @ensan.besham signature)
    - Event-locked stereo micro-SFX (radar pings, filter snap, sub-bass swells, crystalline brand chime)
    """
    with wave.open(tightened_wav, "rb") as wf:
        vo = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

    N = len(vo)
    dur = N / SR
    t = np.arange(N, dtype=np.float32) / SR

    # Sidechain ducking envelope
    duck_env = lfilter(*butter(1, 3.0 / (SR / 2), btype="low"), np.abs(vo))
    duck = np.clip(1.0 - 2.4 * duck_env, 0.36, 1.0)

    # Dark C-minor9 ambient drone (C2, G2, D3, Eb3, G3)
    pad_L = np.zeros(N, dtype=np.float32)
    pad_R = np.zeros(N, dtype=np.float32)
    for i, (f, a) in enumerate([(65.41, 0.32), (98.00, 0.24), (146.83, 0.14), (155.56, 0.13), (196.00, 0.09)]):
        l1 = 0.76 + 0.24 * np.sin(2 * np.pi * (0.065 + 0.015 * i) * t + i)
        l2 = 0.76 + 0.24 * np.cos(2 * np.pi * (0.058 + 0.018 * i) * t + i * 1.3)
        pad_L += a * l1 * np.sin(2 * np.pi * (f * 0.999) * t)
        pad_R += a * l2 * np.sin(2 * np.pi * (f * 1.001) * t + 0.6)

    b_lp, a_lp = butter(2, 440.0 / (SR / 2), btype="low")
    fade = np.clip(t / 1.2, 0, 1) * np.clip((dur - t) / 1.8, 0, 1)
    pad_L = lfilter(b_lp, a_lp, pad_L) * 0.115 * duck * fade
    pad_R = lfilter(b_lp, a_lp, pad_R) * 0.115 * duck * fade

    sfx_L = np.zeros(N, dtype=np.float32)
    sfx_R = np.zeros(N, dtype=np.float32)

    for ev in sfx_events:
        kind = ev["type"]
        ts = float(ev["t"])
        idx = int(ts * SR)
        if idx < 0 or idx >= N - 400:
            continue

        if kind == "ping":
            dn = min(int(0.22 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            f0 = float(ev.get("freq", 1046.5))
            pan = float(ev.get("pan", 0.5))
            sig = np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 22.0) * 0.042
            sfx_L[idx:idx+dn] += sig * (1.0 - 0.5 * pan)
            sfx_R[idx:idx+dn] += sig * (0.5 + 0.5 * pan)

        elif kind == "sub_swell":
            dn = min(int(1.15 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            env_s = np.sin(np.pi * tt / (dn / SR)) ** 1.4
            sig = np.sin(2 * np.pi * (58.0 - 13.0 * tt) * tt) * env_s * 0.078
            sfx_L[idx:idx+dn] += sig
            sfx_R[idx:idx+dn] += sig

        elif kind == "tick":
            dn = min(int(0.025 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            pan = float(ev.get("pan", 0.5))
            sig = np.sin(2 * np.pi * 2300.0 * tt) * np.exp(-tt * 240.0) * 0.036
            sfx_L[idx:idx+dn] += sig * (1.0 - 0.5 * pan)
            sfx_R[idx:idx+dn] += sig * (0.5 + 0.5 * pan)

        elif kind == "chime":
            dn = min(int(2.6 * SR), N - idx)
            tt = np.arange(dn, dtype=np.float32) / SR
            f0 = float(ev.get("freq", 523.25))
            att = np.clip(tt / 0.012, 0, 1)
            sig = att * (
                np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 2.4)
                + 0.45 * np.sin(2 * np.pi * f0 * 1.5 * tt) * np.exp(-tt * 3.3)
                + 0.25 * np.sin(2 * np.pi * f0 * 2.0 * tt) * np.exp(-tt * 4.5)
            ) * 0.062
            sfx_L[idx:idx+dn] += sig * 0.96
            sfx_R[idx:idx+dn] += sig * 1.04

    mix_L = np.clip(vo + pad_L + sfx_L, -0.97, 0.97)
    mix_R = np.clip(vo + pad_R + sfx_R, -0.97, 0.97)

    stereo = np.empty((N * 2,), dtype=np.int16)
    stereo[0::2] = (mix_L * 32767).astype(np.int16)
    stereo[1::2] = (mix_R * 32767).astype(np.int16)

    with wave.open(out_master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(stereo.tobytes())
    print(f"[Audio] Master 48kHz stereo mix saved -> {out_master_wav} ({dur:.2f}s)", flush=True)
