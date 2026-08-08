"""
PRAMAAN-SHIELD — OpenCV Frame Sampler
File: backend/app/utils/frame_extract.py

Shared frame sampling for the perceptual hash engine (TRD §8.1) and the
video deepfake detector (TRD §8.4). Uses the decoder bundled with
opencv-python, so it works without a system `ffmpeg` binary on PATH.
"""

import math

from typing import List

import cv2
import numpy as np
from loguru import logger

FRAME_INTERVAL = 10   # TRD §8.4 — sample every 10th frame
MAX_FRAMES = 12       # Fast video scanning (up to 12 frames per video for sub-20s analysis)
FACE_CROP_SIZE = 224  # TRD §8.4 — 224x224 model input


def extract_frames(
    video_path: str,
    every_n: int = FRAME_INTERVAL,
    max_frames: int = MAX_FRAMES,
    max_dim: int = 0
) -> List[np.ndarray]:
    """
    Sample up to `max_frames` BGR frames, taking every `every_n`th frame.

    Skipped frames are consumed with grab() rather than decoded, so the cost
    scales with the sampled count and not the full video length.

    If `max_dim` > 0, decoded frames wider/taller than that are downscaled
    (keeping aspect ratio) before being retained — a 1080p frame is ~6 MB RAM;
    capping at 960 px cuts retained-frame memory ~4-6x with no visible impact
    on the 224x224 model crop or histogram forensics.
    Returns an empty list if the container cannot be opened or decoded.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.warning(f"OpenCV could not open video container: {video_path}")
        return []

    frames: List[np.ndarray] = []
    position = 0

    try:
        while len(frames) < max_frames:
            if not cap.grab():
                break
            if position % every_n == 0:
                ok, frame = cap.retrieve()
                if ok and frame is not None:
                    if max_dim > 0:
                        h, w = frame.shape[:2]
                        scale = max_dim / float(max(h, w)) if max(h, w) > max_dim else 1.0
                        if scale < 1.0:
                            frame = cv2.resize(
                                frame, (int(w * scale), int(h * scale)),
                                interpolation=cv2.INTER_AREA
                            )
                    frames.append(frame)
            position += 1
    except Exception as e:
        logger.error(f"Frame extraction aborted at position {position}: {e}")
    finally:
        cap.release()

    logger.info(
        f"Sampled {len(frames)} frames (every {every_n}th of {position} decoded) from {video_path}"
    )
    return frames


def temporal_consistency(frames: List[np.ndarray]) -> float:
    """
    Frame-to-frame stability score in [0.0, 1.0]; 1.0 is perfectly consistent.

    Compares normalised grayscale histograms of consecutive sampled frames.
    Face-swap pipelines re-render each frame independently, so the boundary
    between the swapped region and the source flickers — that shows up as
    lower correlation than an untouched capture of the same scene.

    Constant/near-flat frames (fade-to-black, solid colour screens) carry no
    temporal signal at all: their histogram degenerates to a single dominant
    bin, and OpenCV's HISTCMP_CORREL then reports ~1.0 for ANY two such
    frames — even two completely different scenes. Those frames are excluded
    from the comparison so a degenerate clip can neither certify a video as
    authentic nor incriminate it.
    """
    if len(frames) < 2:
        return 1.0

    # Neutral value inside the "no gate fires" band (0.90–0.95): used when
    # there is not enough structured signal to compare at all.
    NO_SIGNAL = 0.92

    histograms = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Near-zero pixel variance => constant frame => no temporal signal.
        if float(gray.std()) < 6.0:
            continue
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        histograms.append(hist)

    if len(histograms) < 2:
        return NO_SIGNAL

    correlations = []
    for i in range(len(histograms) - 1):
        corr = cv2.compareHist(histograms[i], histograms[i + 1], cv2.HISTCMP_CORREL)
        if math.isnan(corr):
            continue
        correlations.append(corr)

    if not correlations:
        return NO_SIGNAL

    return round(max(0.0, min(1.0, float(np.mean(correlations)))), 3)


def generate_manipulation_heatmap(face_crop: np.ndarray) -> str:
    """
    Produce a base64-encoded PNG manipulation-likelihood heatmap overlay
    from a 224×224 BGR face crop.

    Method: Laplacian gradient magnitude → normalise → JET colormap.
    Over-smoothed deepfake regions show up as cooler (blue/cyan) zones while
    authentic high-texture skin (pores, stubble) lights up hot (red/yellow).
    """
    import base64
    try:
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY).astype(np.float32)
        laplacian = np.abs(cv2.Laplacian(gray, cv2.CV_32F))

        # Normalise to 0-255 range
        lap_max = laplacian.max()
        if lap_max > 0:
            normed = (laplacian / lap_max * 255).astype(np.uint8)
        else:
            normed = np.zeros_like(gray, dtype=np.uint8)

        # Invert: low-texture (suspicious) = high heat
        inverted = 255 - normed

        heatmap = cv2.applyColorMap(inverted, cv2.COLORMAP_JET)

        # Blend with original face for context
        blended = cv2.addWeighted(face_crop, 0.4, heatmap, 0.6, 0)

        _, buffer = cv2.imencode(".png", blended)
        b64 = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        logger.error(f"Heatmap generation failed: {e}")
        return ""


def calculate_blink_rate(frames: List[np.ndarray]) -> float:
    """
    Estimate blink rate (blinks per second) across sampled video frames.

    Uses OpenCV Haar cascade for eye detection. A "blink" is registered when
    eyes are detected in one frame but absent in the next.

    Real humans: ~0.25–0.33 blinks/sec (15-20/min).
    Deepfakes:   typically 0 or near-zero (no real eyelid movement).

    Returns 0.0 if no reliable detection can be performed.
    """
    try:
        from pathlib import Path
        from cv2 import CascadeClassifier
        local_path = Path(__file__).parent.parent / "ml" / "deepfake" / "weights" / "haarcascade_eye.xml"
        eye_cascade = None
        if local_path.exists():
            eye_cascade = CascadeClassifier(str(local_path))

        if (eye_cascade is None or eye_cascade.empty()) and hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
            sys_path = Path(cv2.data.haarcascades) / "haarcascade_eye.xml"
            if sys_path.exists():
                eye_cascade = CascadeClassifier(str(sys_path))

        if eye_cascade is None or eye_cascade.empty():
            logger.warning("Eye HaarCascade classifier not found")
            return 0.0

        prev_eyes_detected = True
        blink_count = 0
        valid_frames = 0

        for frame in frames:
            h, w = frame.shape[:2]
            scale = 320.0 / max(h, w) if max(h, w) > 320 else 1.0
            if scale != 1.0:
                small = cv2.resize(frame, (int(w * scale), int(h * scale)),
                                   interpolation=cv2.INTER_AREA)
            else:
                small = frame

            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            eyes = eye_cascade.detectMultiScale(
                gray, scaleFactor=1.15, minNeighbors=4, minSize=(12, 12)
            )
            eyes_detected = len(eyes) >= 2  # Both eyes visible

            if valid_frames > 0 and prev_eyes_detected and not eyes_detected:
                blink_count += 1

            prev_eyes_detected = eyes_detected
            valid_frames += 1

        if valid_frames < 3:
            return 0.0

        # Assume FRAME_INTERVAL frames skipped between samples, ~30fps source
        fps_estimate = 30.0 / FRAME_INTERVAL  # effective sampled fps
        duration_secs = valid_frames / fps_estimate
        return round(blink_count / max(1.0, duration_secs), 3)

    except Exception as e:
        logger.warning(f"Blink rate calculation failed: {e}")
        return 0.0


def rppg_pulse_score(face_crops: List[np.ndarray], sampled_fps: float = 3.0) -> dict:
    """
    Remote Photoplethysmography (rPPG) — detect biological heartbeat from
    subtle green-channel fluctuations in the forehead region of face crops.

    Real person: pulsatile signal at 48–120 BPM (0.8–2.0 Hz).
    Deepfake:    flat or random signal, no cardiac periodicity.

    Args:
        face_crops: list of 224×224 BGR face crops (from consecutive sampled frames).
        sampled_fps: effective sampling rate (30fps source / every_10th = 3.0 fps).

    Returns:
        dict with keys:
          pulse_detected (bool), bpm_estimate (float), liveness_boost (int)
    """
    default = {"pulse_detected": False, "bpm_estimate": 0.0, "liveness_boost": 0}

    try:
        if len(face_crops) < 12:
            return default

        green_means: List[float] = []
        for crop in face_crops:
            h, w = crop.shape[:2]
            # Forehead ROI: top 1/3, center 50% width
            roi = crop[:h // 3, w // 4: 3 * w // 4]
            green_means.append(float(np.mean(roi[:, :, 1])))  # Green channel

        signal = np.array(green_means, dtype=np.float64)
        signal = signal - np.mean(signal)  # Remove DC offset

        # Apply Hanning window to reduce spectral leakage
        window = np.hanning(len(signal))
        windowed = signal * window

        fft_mag = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(len(windowed), d=1.0 / sampled_fps)

        # Cardiac band: 0.8–2.0 Hz (48–120 BPM)
        cardiac_mask = (freqs >= 0.8) & (freqs <= 2.0)
        if not np.any(cardiac_mask):
            return default

        cardiac_power = fft_mag[cardiac_mask]
        total_power = np.sum(fft_mag[1:]) + 1e-10  # Exclude DC
        cardiac_ratio = float(np.sum(cardiac_power) / total_power)

        peak_idx_cardiac = np.argmax(cardiac_power)
        peak_freq = freqs[cardiac_mask][peak_idx_cardiac]
        bpm = float(peak_freq * 60.0)

        # Get global index of the peak frequency
        peak_global_idx = np.where(freqs == peak_freq)[0][0]
        # Calculate SNR: peak power divided by mean power of other non-DC frequencies
        non_peak_mask = np.ones_like(fft_mag, dtype=bool)
        non_peak_mask[0] = False # Exclude DC
        non_peak_mask[peak_global_idx] = False
        mean_noise_power = np.mean(fft_mag[non_peak_mask]) if np.any(non_peak_mask) else 1e-10
        peak_power = fft_mag[peak_global_idx]
        snr = peak_power / (mean_noise_power + 1e-10)

        # For a genuine heartbeat, we expect:
        # - Sufficient number of frames (at least 12)
        # - The cardiac band contains a meaningful portion of the power (cardiac_ratio > 0.30)
        # - The peak is sharp and dominant (snr > 2.2)
        # - BPM is within normal human resting range (48 to 120 BPM)
        pulse_detected = len(face_crops) >= 12 and snr > 2.2 and cardiac_ratio > 0.30 and 48.0 <= bpm <= 120.0

        liveness_boost = 10 if pulse_detected else -5

        logger.info(
            f"rPPG analysis: pulse={'yes' if pulse_detected else 'no'}, "
            f"BPM≈{bpm:.1f}, cardiac_ratio={cardiac_ratio:.3f}, snr={snr:.3f}"
        )

        return {
            "pulse_detected": pulse_detected,
            "bpm_estimate": round(bpm, 1),
            "liveness_boost": liveness_boost
        }

    except Exception as e:
        logger.warning(f"rPPG pulse analysis failed: {e}")
        return default
