"""
PRAMAAN-SHIELD — RawNet2 Audio Anti-Spoofing Model
File: backend/app/ml/rawnet2/model.py

RawNet2 Raw Waveform CNN for audio liveness and deepfake detection.
Operates in PRODUCTION mode when weights exist, or HACKATHON fallback mode.
"""

import wave
from pathlib import Path
from loguru import logger
import torch


class RawNet2Model:
    """RawNet2 Raw Waveform CNN Model Wrapper."""

    def __init__(self, weights_path: str = "app/ml/rawnet2/weights/rawnet2.pth"):
        self.weights_path = Path(weights_path)
        self.mode = "HACKATHON"
        self.model = None

        if self.weights_path.exists() and self.weights_path.stat().st_size > 1024:
            try:
                import torch
                loaded = torch.load(self.weights_path, map_location="cpu")
                if isinstance(loaded, dict):
                    self.model = loaded
                else:
                    self.model = loaded
                    if hasattr(self.model, "eval"):
                        self.model.eval()
                self.mode = "PRODUCTION"
                logger.info(f"Loaded PyTorch RawNet2 model from {self.weights_path}")
            except Exception as e:
                logger.warning(f"Could not load RawNet2 PyTorch weights: {e}. Falling back to HACKATHON mode.")
        else:
            logger.info("RawNet2: Operating in HACKATHON deterministic fallback mode")

    def predict(self, audio_input) -> float:
        """
        Run inference on raw audio waveform bytes or file path.
        Returns bonafide probability score (0.0 - 1.0).

        SECURITY NOTE (A2): the weights on disk are a placeholder dict, NOT a
        trainable nn.Module. A constant "0.82" here would certify EVERY audio
        clip as genuine (+35 "Authentic Voice Confirmed"). The PRODUCTION path
        is taken only for a real nn.Module; otherwise the DSP forensics engine
        runs instead.
        """
        if self.mode == "PRODUCTION" and isinstance(self.model, torch.nn.Module):
            try:
                return self._real_inference(audio_input)
            except Exception as e:
                logger.error(f"Inference error in RawNet2 production mode: {e}")
                return self._envelope_forensics(audio_input)

        return self._envelope_forensics(audio_input)

    def _real_inference(self, audio_input) -> float:
        """Actual tensor evaluation against a genuine loaded RawNet2 module."""
        try:
            import torchaudio
        except ImportError:
            return self._envelope_forensics(audio_input)

        if isinstance(audio_input, (str, Path)) and Path(audio_input).exists():
            waveform, _ = torchaudio.load(str(audio_input))
        elif isinstance(audio_input, (bytes, bytearray)):
            import io
            waveform, _ = torchaudio.load(io.BytesIO(audio_input))
        else:
            return self._envelope_forensics(audio_input)

        if waveform.size(1) == 0:
            return 0.35
        waveform = waveform[:1]

        with torch.no_grad():
            self.model.eval()
            out = self.model(waveform)
            if isinstance(out, tuple):
                out = out[0]
            if isinstance(out, torch.Tensor):
                return float(torch.sigmoid(out.float()).mean().item())
        return self._envelope_forensics(audio_input)

    @staticmethod
    def _envelope_forensics(audio_input) -> float:
        """
        Complementary acoustic analysis for HACKATHON mode.
        Focuses on energy envelope periodicity and crest factor.

        Real speech: irregular energy envelope with natural pauses.
        TTS output:  uniform energy, missing micro-silences.
        """
        import numpy as np
        import io

        try:
            audio = None
            sample_rate = 16000

            # 1. Try decoding via torchaudio
            try:
                import torchaudio
                if isinstance(audio_input, (str, Path)) and Path(audio_input).exists():
                    waveform, sample_rate = torchaudio.load(str(audio_input))
                    audio = waveform.mean(dim=0).numpy().astype(np.float32)
                elif isinstance(audio_input, (bytes, bytearray)):
                    waveform, sample_rate = torchaudio.load(io.BytesIO(audio_input))
                    audio = waveform.mean(dim=0).numpy().astype(np.float32)
            except Exception:
                pass

            # 2. Try stdlib wave module
            if audio is None:
                try:
                    raw_bytes = audio_input if isinstance(audio_input, (bytes, bytearray)) else Path(audio_input).read_bytes()
                    with wave.open(io.BytesIO(raw_bytes)) as wf:
                        n_frames = wf.getnframes()
                        sample_rate = wf.getframerate()
                        raw = wf.readframes(n_frames)
                        sample_width = wf.getsampwidth()
                        n_channels = wf.getnchannels()

                    if sample_width == 2:
                        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                    else:
                        audio = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0

                    if n_channels > 1:
                        audio = audio[::n_channels]
                except Exception:
                    pass

            if audio is None or len(audio) < 1600:
                raw_bytes = audio_input if isinstance(audio_input, (bytes, bytearray)) else Path(audio_input).read_bytes()
                from app.ml.aasist.model import AASISTModel
                mp3_score = AASISTModel._analyze_mp3_bitstream_forensics(raw_bytes)
                if mp3_score is not None:
                    return mp3_score
                return 0.5

            max_samples = sample_rate * 5
            audio = audio[:max_samples]

            # 1. Short-Term RMS Energy Envelope Periodicity
            frame_len = sample_rate // 20  # 50ms
            envelope = np.array([
                float(np.sqrt(np.mean(audio[i:i + frame_len] ** 2)))
                for i in range(0, len(audio) - frame_len, frame_len)
            ])

            if len(envelope) < 4:
                return 0.35

            # 2. Dynamic Range Compression (Crest Factor)
            peak = float(np.max(np.abs(audio)))
            rms_global = float(np.sqrt(np.mean(audio ** 2)))
            crest = peak / (rms_global + 1e-10)

            # AI TTS audio is heavily compressed (crest < 3.5)
            crest_anomaly = max(0.0, min(1.0, (4.5 - crest) / 3.0))

            # 3. Envelope Autocorrelation Periodicity
            env_centered = envelope - np.mean(envelope)
            autocorr = np.correlate(env_centered, env_centered, mode='full')
            autocorr = autocorr[len(autocorr) // 2:]
            if autocorr[0] > 0:
                autocorr = autocorr / autocorr[0]
            periodicity = float(np.max(autocorr[2:min(len(autocorr), 20)])) if len(autocorr) > 20 else 0.5

            # AI vocoder synthesis exhibits high energy envelope periodicity (>0.45)
            period_anomaly = max(0.0, min(1.0, (periodicity - 0.30) / 0.40))

            # 4. Zero-Crossing Rate Jitter (micro-variations in pitch)
            zcr = [
                float(np.mean(np.abs(np.diff(np.sign(audio[i:i + frame_len]))) > 0))
                for i in range(0, len(audio) - frame_len, frame_len)
            ]
            zcr_std = float(np.std(zcr)) if len(zcr) > 2 else 0.1
            zcr_anomaly = max(0.0, min(1.0, (0.08 - zcr_std) / 0.06))

            synthetic_score = (
                0.35 * crest_anomaly
                + 0.35 * period_anomaly
                + 0.30 * zcr_anomaly
            )

            liveness = 1.0 - max(0.0, min(1.0, synthetic_score))
            logger.info(
                f"RawNet2 forensics: liveness={liveness:.2f}, crest={crest:.2f}, "
                f"periodicity={periodicity:.3f}, zcr_std={zcr_std:.4f}"
            )
            return round(max(0.05, min(0.95, liveness)), 3)

        except Exception as e:
            logger.warning(f"RawNet2 envelope forensics fallback failed: {e}")
            return 0.35
