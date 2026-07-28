"""
PRAMAAN-SHIELD — Video Deepfake Detection Module
File: backend/app/services/video_service.py

Extracts frames via OpenCV, crops faces, runs EfficientNet-B4 CNN,
and performs temporal consistency check.

Pipeline per TRD §8.4: sample every 10th frame (max 30) → detect the primary
face → 224x224 crop → per-frame manipulation score → temporal consistency
across the sampled frames → aggregate.

Every score comes from decoded pixels. The filename is logged for traceability
and never scored — a detector that reads "deepfake" out of the upload name
flags any honestly-named file and misses any renamed one.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from loguru import logger

from app.ml.deepfake.model import DeepfakeModel
from app.utils.frame_extract import (
    extract_frames, temporal_consistency, generate_manipulation_heatmap,
    calculate_blink_rate, rppg_pulse_score, FACE_CROP_SIZE
)


@dataclass
class VideoResult:
    deepfake_probability: int             # 0 - 100
    is_deepfake: bool
    frame_scores: List[float]
    temporal_score: float
    num_frames_analyzed: int
    heatmap_available: bool
    heatmap_b64: str = ""                 # base64-encoded manipulation heatmap PNG
    blink_rate: float = 0.0               # blinks per second (0 = suspicious)
    rppg_result: dict = None              # {pulse_detected, bpm_estimate, liveness_boost}
    frames_sampled: int = 0               # frames decoded before face detection
    detector: str = "none"                # MTCNN | HaarCascade | none
    mode: str = "HACKATHON"               # inference mode of the CNN wrapper


class FaceDetector:
    """
    Primary-face locator for frame crops.

    MTCNN (TRD §8.4) when facenet-pytorch is installed, otherwise OpenCV's
    Haar cascade, which ships with opencv-python and needs no extra download.
    """

    def __init__(self):
        self.backend = "none"
        self._mtcnn = None
        self._cascade = None

        try:
            from facenet_pytorch import MTCNN
            self._mtcnn = MTCNN(keep_all=False, post_process=False, device="cpu")
            self.backend = "MTCNN"
        except Exception:
            try:
                if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
                    cascade_path = f"{cv2.data.haarcascades}haarcascade_frontalface_default.xml"
                    cascade = cv2.CascadeClassifier(cascade_path)
                    if not cascade.empty():
                        self._cascade = cascade
                        self.backend = "HaarCascade"
            except Exception as e:
                logger.warning(f"CascadeClassifier initialization skipped: {e}")

        logger.info(f"FaceDetector backend: {self.backend}")

    def crop_face(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Return the largest face in the frame as a 224x224 BGR crop, or None."""
        box = self._detect_box(frame)
        if box is None:
            return None

        x, y, w, h = box
        height, width = frame.shape[:2]
        # Widen slightly — swap artefacts concentrate on the blend boundary.
        margin = int(0.1 * max(w, h))
        x1, y1 = max(0, x - margin), max(0, y - margin)
        x2, y2 = min(width, x + w + margin), min(height, y + h + margin)

        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return None
        return cv2.resize(crop, (FACE_CROP_SIZE, FACE_CROP_SIZE), interpolation=cv2.INTER_AREA)

    def _detect_box(self, frame: np.ndarray) -> Optional[tuple]:
        """Locate the largest face as (x, y, w, h). Downsampled for sub-second CPU speed."""
        try:
            h, w = frame.shape[:2]
            scale = 320.0 / float(max(h, w)) if max(h, w) > 320 else 1.0
            if scale != 1.0:
                small = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
            else:
                small = frame

            if self._cascade is not None:
                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                faces = self._cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=4, minSize=(24, 24)
                )
                if len(faces) > 0:
                    best = max(faces, key=lambda f: f[2] * f[3])
                    bx, by, bw, bh = best
                    return (int(bx / scale), int(by / scale), int(bw / scale), int(bh / scale))

            if self._mtcnn is not None:
                rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                boxes, _ = self._mtcnn.detect(rgb)
                if boxes is not None and len(boxes) > 0:
                    x1, y1, x2, y2 = [int(v / scale) for v in boxes[0]]
                    return (x1, y1, max(1, x2 - x1), max(1, y2 - y1))
        except Exception as e:
            logger.warning(f"Face detection failed on frame: {e}")

        return None


class VideoAnalyzer:
    def __init__(self, model_path: Optional[str] = None):
        self.model = DeepfakeModel(model_path or "app/ml/deepfake/weights/efficientnet_b4.pth")
        self.face_detector = FaceDetector()
        logger.info(
            f"Initialized VideoAnalyzer (EfficientNet-B4 [{self.model.mode}] + {self.face_detector.backend})"
        )

    async def analyze(self, video_path: str, original_filename: Optional[str] = None) -> VideoResult:
        """
        Analyze video strictly from decoded frame pixels per TRD §8.4 specification.
        No filename bias or metadata rules.
        """
        try:
            frames = extract_frames(video_path, every_n=10, max_frames=30)
            if not frames:
                logger.warning(f"No decodable frames in '{original_filename or video_path}'; analysis skipped")
                return self._empty_result()

            frame_scores: List[float] = []
            face_crops: List[np.ndarray] = []
            for frame in frames:
                face = self.face_detector.crop_face(frame)
                if face is not None:
                    score = self.model.predict_frame(face)
                    frame_scores.append(score)
                    face_crops.append(face)

            temporal_score = temporal_consistency(frames)
            blink_rate = calculate_blink_rate(frames)

            # Generate manipulation heatmap from the most suspicious face crop
            heatmap_b64 = ""
            if face_crops:
                # Pick the crop with the highest manipulation score
                worst_idx = int(np.argmax(frame_scores)) if frame_scores else 0
                heatmap_b64 = generate_manipulation_heatmap(face_crops[worst_idx])

            # rPPG biological pulse analysis
            rppg = rppg_pulse_score(face_crops, sampled_fps=3.0)

            if frame_scores:
                avg_score = float(np.mean(frame_scores))
                avg_score = min(1.0, avg_score + max(0.0, 1.0 - temporal_score) * 0.15)
                # Blink rate penalty: near-zero blinks slightly increases suspicion
                if blink_rate < 0.05 and len(frames) >= 10:
                    avg_score = min(1.0, avg_score + 0.05)
                # rPPG adjustment: detected pulse slightly lowers suspicion
                if rppg.get("liveness_boost", 0) != 0:
                    boost = rppg["liveness_boost"] / 100.0  # ±0.05 to ±0.10
                    avg_score = max(0.0, min(1.0, avg_score - boost))
            else:
                logger.info(f"No face detected across {len(frames)} sampled frames in {video_path}")
                avg_score = 0.15

            is_deepfake = avg_score > 0.5

            logger.info(
                f"Video analysis '{original_filename or video_path}': "
                f"{len(frame_scores)}/{len(frames)} frames evaluated, "
                f"probability={round(avg_score * 100)}%, temporal={temporal_score}, "
                f"blink_rate={blink_rate}, rPPG={rppg}, mode={self.model.mode}"
            )

            return VideoResult(
                deepfake_probability=round(avg_score * 100),
                is_deepfake=is_deepfake,
                frame_scores=[round(s, 4) for s in frame_scores],
                temporal_score=temporal_score,
                num_frames_analyzed=len(frame_scores),
                heatmap_available=bool(heatmap_b64),
                heatmap_b64=heatmap_b64,
                blink_rate=blink_rate,
                rppg_result=rppg,
                frames_sampled=len(frames),
                detector=self.face_detector.backend,
                mode=self.model.mode
            )
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return self._empty_result()

    def _empty_result(self) -> VideoResult:
        return VideoResult(
            deepfake_probability=0,
            is_deepfake=False,
            frame_scores=[],
            temporal_score=0.0,
            num_frames_analyzed=0,
            heatmap_available=False,
            heatmap_b64="",
            blink_rate=0.0,
            rppg_result={"pulse_detected": False, "bpm_estimate": 0.0, "liveness_boost": 0},
            frames_sampled=0,
            detector=self.face_detector.backend,
            mode=self.model.mode
        )
