"""
PRAMAAN-SHIELD — Social Media Coordination & Pump-and-Dump Scorer
File: backend/app/services/social_service.py

Module A5: Detects coordinated pump-and-dump networks across Telegram/WhatsApp channels.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any


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
            "100% risk free", "sure shot tip", "upper circuit"
        ]
        self.scam_group_patterns = [
            r"vip\s*(trading|calls?|tips?)",
            r"premium\s*stock",
            r"free\s*intraday",
            r"jackpot\s*(call|tip)",
            r"insider\s*(info|tips?|trading)",
            r"guaranteed\s*(profit|return)",
            r"(zerodha|groww|angel|upstox)\s*(official|premium|vip)\s*(group|channel)?",
            r"sebi\s*(approved|registered)\s*(group|channel|tips?)",
        ]
        self.official_channels = {
            "zerodha": ["t.me/zerodhaindia"],
            "groww": ["t.me/groww_official"],
            "sebi": []
        }

    async def analyze_coordination(self, text: str) -> SocialCoordinationResult:
        """
        Analyze message for pump-and-dump and channel impersonation patterns.
        """
        text_lower = text.lower()
        patterns_found = []
        score = 0

        for kw in self.scam_keywords:
            if kw in text_lower:
                score += 25
                patterns_found.append(f"Pump-and-dump phrase: '{kw}'")

        # Telegram & WhatsApp group link extraction and impersonation check
        telegram_links = re.findall(r't\.me/([a-zA-Z0-9_]+)', text)
        whatsapp_links = re.findall(r'chat\.whatsapp\.com/([a-zA-Z0-9]+)', text)

        if telegram_links or whatsapp_links:
            score += 20
            patterns_found.append("Unregulated social group invite link detected")

        for link in telegram_links:
            link_lower = link.lower()
            for entity in ["zerodha", "groww", "angel", "upstox", "sebi"]:
                if entity in link_lower:
                    official = self.official_channels.get(entity, [])
                    if f"t.me/{link}" not in official:
                        score += 30
                        patterns_found.append(
                            f"Telegram channel 't.me/{link}' claims connection to '{entity}' — unofficial channel"
                        )

        # Scam group pattern matching
        for pattern in self.scam_group_patterns:
            if re.search(pattern, text_lower):
                score += 15
                patterns_found.append(f"Suspicious social group pattern detected: '{pattern}'")

        # Stock ticker extraction (filtering noise words)
        noise_words = {
            "THE", "AND", "FOR", "THIS", "THAT", "WITH", "FROM", "YOUR",
            "SEBI", "PRAMAAN", "SHIELD", "VERIFIED", "CAUTION", "ALERT",
            "SCAN", "NOTE", "DATE", "TIME", "HTTP", "HTTPS", "WWW", "INFO"
        }
        raw_tickers = re.findall(r'\b[A-Z]{3,10}\b', text)
        stock_tickers = [t for t in raw_tickers if t not in noise_words]

        score = min(100, score)
        is_coordinated = score >= 50

        total_links = len(telegram_links) + len(whatsapp_links)
        virality_index = round(min(1.0, total_links * 0.3 + score / 100.0), 2)

        return SocialCoordinationResult(
            coordination_score=score,
            is_coordinated_scam=is_coordinated,
            detected_patterns=patterns_found,
            target_stocks=stock_tickers[:5],
            channel_virality_index=virality_index
        )
