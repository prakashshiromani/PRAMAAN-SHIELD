"""
PRAMAAN-SHIELD — Voice Anti-Spoofing & Clone Detection
File: backend/app/services/voice_service.py

Uses AASIST (Graph Attention Network) + RawNet2 (Raw Waveform CNN) ensemble
for audio liveness and synthetic voice clone detection.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import asyncio
from loguru import logger

from app.ml.aasist.model import AASISTModel
from app.ml.rawnet2.model import RawNet2Model


def _run_voice_analysis_sync(analyzer, audio_path: str) -> "VoiceResult":
    """Module-level entry for the sandboxed subprocess. Under fork the child
    inherits the parent's loaded VoiceAnalyzer copy-on-write; a plain string
    argument is accepted for the spawn/Windows path to rebuild inside the worker."""
    if isinstance(analyzer, str):
        analyzer = VoiceAnalyzer(aasist_path=None, rawnet2_path=None)
    return analyzer._analyze_sync(audio_path)


@dataclass
class VoiceResult:
    liveness_score: int                   # 0 - 100
    is_synthetic: bool
    aasist_score: float                   # 0.0 - 1.0
    rawnet2_score: float                  # 0.0 - 1.0
    verdict: str
    analysis_failed: bool = False         # True → ML error; must NOT be scored as genuine
    model_mode: str = "forensics"         # "production" if a loaded nn.Module ran, else "forensics"


class VoiceAnalyzer:
    def __init__(self, aasist_path: Optional[str] = None, rawnet2_path: Optional[str] = None):
        self.aasist_path = aasist_path or "app/ml/aasist/weights/aasist.pth"
        self.rawnet2_path = rawnet2_path or "app/ml/rawnet2/weights/rawnet2.pth"
        self.aasist = AASISTModel(self.aasist_path)
        self.rawnet2 = RawNet2Model(self.rawnet2_path)
        logger.info("Initialized VoiceAnalyzer (AASIST + RawNet2 ensemble)")

    async def analyze(self, audio_path: str) -> VoiceResult:
        """
        Analyze audio file for synthetic voice clone markers using AASIST & RawNet2.
        Offloaded to a sandbox subprocess (timeout-guarded); falls back to a worker
        thread if the subprocess layer is unavailable — never blocks the event loop.
        """
        from app.utils.sandboxed_runner import run_sandboxed_or_thread
        return await run_sandboxed_or_thread(
            _run_voice_analysis_sync,
            (self, audio_path),
            timeout_secs=45,
            fallback=lambda: self._analyze_sync(audio_path),
            task_label="voice analysis",
        )

    def _analyze_sync(self, audio_path: str) -> VoiceResult:
        try:
            path_obj = Path(audio_path)

            # Signal gate: never score an audio sample we cannot actually hear.
            # 0-byte/garbage uploads decode to None and get a 0.50 sentinel from
            # both predictors → combined 0.50 → "NOT synthetic" → +50 genuine
            # boost (forgery of a verdict). Real silence decodes but reads as
            # synthetic (hard-gate false positive). Both must be marked
            # analysis_failed and excluded from the trust score.
            signal_status = self._probe_signal(audio_path)
            if signal_status != "ok":
                reason = {
                    "empty": "file is missing/empty",
                    "undecodable": "audio could not be decoded",
                    "silent": "audio is silent or too short",
                }[signal_status]
                logger.warning(
                    f"Voice analysis marked analysis_failed ({reason}): {audio_path}"
                )
                return VoiceResult(
                    liveness_score=0,
                    is_synthetic=False,
                    aasist_score=0.0,
                    rawnet2_score=0.0,
                    verdict=f"Voice Analysis Failed: {reason}",
                    analysis_failed=True,
                )

            # Pass file path to model predictors for native MP3/WAV torchaudio decoding
            audio_target = str(path_obj) if path_obj.exists() else b""

            aasist_score = self.aasist.predict(audio_target)
            rawnet2_score = self.rawnet2.predict(audio_target)

            combined = 0.6 * aasist_score + 0.4 * rawnet2_score
            is_synthetic = combined < 0.50

            liveness_score = round(combined * 100)
            model_mode = (
                "production"
                if self.aasist.mode == "PRODUCTION" and self.rawnet2.mode == "PRODUCTION"
                else "forensics"
            )
            verdict_text = (
                f"Voice Liveness: {liveness_score}% — "
                f"{'LIKELY SYNTHETIC / CLONED' if is_synthetic else 'LIKELY GENUINE'}"
            )

            return VoiceResult(
                liveness_score=liveness_score,
                is_synthetic=is_synthetic,
                aasist_score=aasist_score,
                rawnet2_score=rawnet2_score,
                verdict=verdict_text,
                model_mode=model_mode
            )
        except Exception as e:
            logger.error(f"Voice analysis failed: {e}")
            return VoiceResult(
                liveness_score=0,
                is_synthetic=False,
                aasist_score=0.0,
                rawnet2_score=0.0,
                verdict="Voice Analysis Skipped due to processing error",
                analysis_failed=True
            )

    @staticmethod
    def _probe_signal(audio_path: str) -> str:
        """Decode the audio file and report whether it is analysable.

        Returns one of:
          "ok"           → decoded into a real, non-silent waveform
          "empty"        → file missing or 0-byte
          "undecodable"  → no decoder could extract any waveform
          "silent"       → decoded but too short (< 1600 samples) or near-silent

        Mirrors the decode strategy inside the AASIST/RawNet2 forensics paths
        (torchaudio first, stdlib wave fallback) so the gate and the models
        agree on what "unusable audio" means.
        """
        import numpy as np

        path_obj = Path(audio_path)
        try:
            if not path_obj.exists() or path_obj.stat().st_size == 0:
                return "empty"
        except OSError:
            return "empty"

        audio = None
        try:
            import torchaudio
            waveform, _ = torchaudio.load(str(path_obj))
            audio = waveform.mean(dim=0).numpy().astype(np.float32)
        except Exception:
            audio = None

        if audio is None:
            try:
                import wave
                import io
                raw_bytes = path_obj.read_bytes()
                with wave.open(io.BytesIO(raw_bytes)) as wf:
                    n_frames = wf.getnframes()
                    sample_width = wf.getsampwidth()
                    n_channels = wf.getnchannels()
                    raw = wf.readframes(n_frames)
                if sample_width == 2:
                    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                elif sample_width == 4:
                    audio = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
                else:
                    audio = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
                if n_channels > 1:
                    audio = audio[::n_channels]
            except Exception:
                audio = None

        if audio is None or len(audio) == 0:
            return "undecodable"
        if len(audio) < 1600:  # < 100 ms at 16 kHz — no analysable signal
            return "silent"

        rms = float(np.sqrt(np.mean(np.square(audio.astype(np.float64)))))
        if rms < 1e-4:
            return "silent"
        return "ok"
