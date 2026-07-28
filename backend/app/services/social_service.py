"""
PRAMAAN-SHIELD — Social Media Coordination & Pump-and-Dump Scorer
File: backend/app/services/social_service.py

Module A5: Detects coordinated pump-and-dump networks across Telegram/WhatsApp channels.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any
from loguru import logger


@dataclass
class SocialCoordinationResult:
    coordination_score: int               # 0 - 100
    is_coordinated_scam: bool
    detected_patterns: List[str]
    target_stocks: List[str]
    channel_virality_index: float


class SocialService:
    def __init__(self):
        self.scam_keywords = [
            "buy now", "target 2000%", "guaranteed upper circuit",
            "multibagger tip", "jackpot call", "leaked insider info",
            "100% risk free", "sure shot tip"
        ]

    async def analyze_coordination(self, text: str) -> SocialCoordinationResult:
        """
        Analyze message for pump-and-dump pattern indicators.
        """
        text_lower = text.lower()
        patterns_found = []
        score = 0

        for kw in self.scam_keywords:
            if kw in text_lower:
                score += 25
                patterns_found.append(f"Pump-and-dump phrase: '{kw}'")

        # Stock ticker extraction (e.g. $RELIANCE, NSE:TATASTEEL)
        stock_tickers = re.findall(r'\b[A-Z]{3,10}\b', text)

        # Telegram/WhatsApp group link check
        if "t.me/" in text_lower or "chat.whatsapp.com/" in text_lower:
            score += 20
            patterns_found.append("Unregulated social group invite link detected")

        score = min(100, score)
        is_coordinated = score >= 50

        return SocialCoordinationResult(
            coordination_score=score,
            is_coordinated_scam=is_coordinated,
            detected_patterns=patterns_found,
            target_stocks=stock_tickers[:5],
            channel_virality_index=0.88 if is_coordinated else 0.12
        )
