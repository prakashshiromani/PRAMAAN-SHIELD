"""
PRAMAAN-SHIELD — Voice Anti-Spoofing & Clone Detection
File: backend/app/services/voice_service.py

Uses AASIST (Graph Attention Network) + RawNet2 (Raw Waveform CNN) ensemble
for audio liveness and synthetic voice clone detection.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from loguru import logger

from app.ml.aasist.model import AASISTModel
from app.ml.rawnet2.model import RawNet2Model


@dataclass
class VoiceResult:
    liveness_score: int                   # 0 - 100
    is_synthetic: bool
    aasist_score: float                   # 0.0 - 1.0
    rawnet2_score: float                  # 0.0 - 1.0
    verdict: str


class VoiceAnalyzer:
    def __init__(self, aasist_path: Optional[str] = None, rawnet2_path: Optional[str] = None):
        self.aasist = AASISTModel(aasist_path or "app/ml/aasist/weights/aasist.pth")
        self.rawnet2 = RawNet2Model(rawnet2_path or "app/ml/rawnet2/weights/rawnet2.pth")
        logger.info("Initialized VoiceAnalyzer (AASIST + RawNet2 ensemble)")

    async def analyze(self, audio_path: str) -> VoiceResult:
        """
        Analyze audio file for synthetic voice clone markers using AASIST & RawNet2.
        Ensemble formula: 0.6 * AASIST + 0.4 * RawNet2
        """
        try:
            audio_bytes = b""
            path_obj = Path(audio_path)
            if path_obj.exists():
                audio_bytes = path_obj.read_bytes()

            aasist_score = self.aasist.predict(audio_bytes)
            rawnet2_score = self.rawnet2.predict(audio_bytes)

            combined = 0.6 * aasist_score + 0.4 * rawnet2_score
            is_synthetic = combined < 0.5

            liveness_score = round(combined * 100)
            verdict_text = (
                f"Voice Liveness: {liveness_score}% — "
                f"{'LIKELY SYNTHETIC / CLONED' if is_synthetic else 'LIKELY GENUINE'}"
            )

            return VoiceResult(
                liveness_score=liveness_score,
                is_synthetic=is_synthetic,
                aasist_score=aasist_score,
                rawnet2_score=rawnet2_score,
                verdict=verdict_text
            )
        except Exception as e:
            logger.error(f"Voice analysis failed: {e}")
            return VoiceResult(
                liveness_score=50,
                is_synthetic=False,
                aasist_score=0.5,
                rawnet2_score=0.5,
                verdict="Voice Analysis Skipped due to processing error"
            )
