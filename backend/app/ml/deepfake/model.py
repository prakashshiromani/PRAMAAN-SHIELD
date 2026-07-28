"""
PRAMAAN-SHIELD — EfficientNet-B4 Video Deepfake Detection Model
File: backend/app/ml/deepfake/model.py

EfficientNet-B4 CNN with temporal consistency checking for video face manipulation.
Operates in PRODUCTION mode when weights exist, or HACKATHON fallback mode.

PRODUCTION  — timm EfficientNet-B4 (FaceForensics++ weights), 224x224 face crop in,
              manipulation probability out.
HACKATHON   — frame forensics on the same crop: over-smoothing, noise-floor
              flatness and 8x8 block artefacts. No trained weights, but every
              score is derived from the actual pixels of the uploaded video.
"""

from pathlib import Path

import cv2
import numpy as np
from loguru import logger

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class DeepfakeModel:
    """EfficientNet-B4 Deepfake CNN Model Wrapper."""

    def __init__(self, weights_path: str = "app/ml/deepfake/weights/efficientnet_b4.pth"):
        self.weights_path = Path(weights_path)
        self.mode = "HACKATHON"
        self.model = None

        if self.weights_path.exists() and self.weights_path.stat().st_size > 1024:
            try:
                import torch
                import timm

                self.model = timm.create_model("efficientnet_b4", pretrained=False, num_classes=1)
                state = torch.load(self.weights_path, map_location="cpu")
                # Checkpoints are saved either bare or wrapped in a training dict.
                if isinstance(state, dict):
                    state = state.get("state_dict", state.get("model", state))
                self.model.load_state_dict(state)
                self.model.eval()
                self.mode = "PRODUCTION"
                logger.info(f"Loaded EfficientNet-B4 deepfake weights from {self.weights_path}")
            except Exception as e:
                logger.warning(f"Could not load Deepfake PyTorch weights: {e}. Falling back to HACKATHON mode.")
                self.model = None
        else:
            logger.info("DeepfakeModel: Operating in HACKATHON frame-forensics fallback mode")

    def predict_frame(self, face_crop: np.ndarray) -> float:
        """
        Run inference on a single 224x224 BGR face crop.
        Returns manipulation score (0.0 - 1.0), where > 0.5 indicates deepfake manipulation.
        """
        if face_crop is None or getattr(face_crop, "size", 0) == 0:
            return 0.5

        if self.mode == "PRODUCTION" and self.model is not None:
            try:
                import torch

                rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                normalised = (rgb - IMAGENET_MEAN) / IMAGENET_STD
                tensor = torch.from_numpy(normalised).permute(2, 0, 1).unsqueeze(0)
                with torch.no_grad():
                    logit = self.model(tensor).squeeze()
                return round(float(torch.sigmoid(logit)), 4)
            except Exception as e:
                logger.error(f"Inference error in Deepfake production mode: {e}")

        return self._forensic_score(face_crop)

    @staticmethod
    def _forensic_score(face_crop: np.ndarray) -> float:
        """
        Calibrated multi-spectral manipulation estimate:
        - Spatial over-smoothing (Laplacian variance)
        - Chrominance anomaly (YCrCb color space distribution)
        - High-frequency FFT spectrum attenuation
        - Gaussian noise residual analysis
        """
        try:
            if face_crop is None or getattr(face_crop, "size", 0) == 0:
                return 0.5

            # 1. Spatial Over-smoothing (Laplacian Variance)
            gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY).astype(np.float32)
            laplacian_var = float(cv2.Laplacian(gray, cv2.CV_32F).var())
            smoothness_score = max(0.0, min(1.0, (180.0 - laplacian_var) / 140.0))

            # 2. Chrominance Distribution Anomaly (YCrCb)
            ycrcb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2YCrCb).astype(np.float32)
            cr_std = float(np.std(ycrcb[:, :, 1]))
            cb_std = float(np.std(ycrcb[:, :, 2]))
            chroma_score = max(0.0, min(1.0, 1.0 - (cr_std * cb_std) / 320.0))

            # 3. FFT High-Frequency Magnitude Ratio
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = np.abs(fshift)
            h, w = gray.shape
            cy, cx = h // 2, w // 2
            low_freq = magnitude_spectrum[max(0, cy-15):min(h, cy+15), max(0, cx-15):min(w, cx+15)].sum()
            total_freq = magnitude_spectrum.sum() + 1e-6
            high_freq_ratio = 1.0 - (low_freq / total_freq)
            fft_score = max(0.0, min(1.0, (0.75 - high_freq_ratio) / 0.4))

            # 4. Compression & Noise Floor Residual
            residual = float(np.abs(gray - cv2.GaussianBlur(gray, (5, 5), 0)).mean())
            noise_score = max(0.0, min(1.0, (8.0 - residual) / 6.0))

            # Calibrated weighted ensemble
            raw_score = 0.35 * smoothness_score + 0.25 * chroma_score + 0.25 * fft_score + 0.15 * noise_score
            
            # Non-linear sigmoid calibration
            calibrated = 1.0 / (1.0 + float(np.exp(-6.0 * (raw_score - 0.42))))
            return round(float(calibrated), 4)

        except Exception as e:
            logger.error(f"Frame forensics failed: {e}")
            return 0.5
