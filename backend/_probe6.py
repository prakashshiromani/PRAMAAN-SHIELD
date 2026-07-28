import asyncio, sys
from app.services.phishing_service import PhishingService
from app.services.trust_score_service import calculate_trust_score

CASES = [
 ("1 Zerodha genuine (official domains)",
  "Official Advisory from Zerodha Broking Limited (SEBI Reg: INZ000031633). Please never share your password, OTP, or PIN with anyone. Always verify trading activity directly on zerodha.com or kite.zerodha.com."),
 ("2 Groww typosquat phish",
  "URGENT NOTICE: Your Groww Account will be BLOCKED in 24 hours! Complete mandatory KYC re-verification immediately at http://app-groww.in/login or face legal penalties."),
 ("3 TATASTEEL pump-and-dump",
  "SURE SHOT CALL: Buy TATASTEEL now for target 2000%! 100% risk free guaranteed return. Join our private WhatsApp group for daily jackpot multibagger calls: chat.whatsapp.com/sample_scam_link"),
 ("4 Hindi KYC threat",
  "अंतिम चेतावनी: आपका SEBI डीमैट खाता 24 घंटे में ब्लॉक कर दिया जाएगा! तुरंत अपनी KYC री-वेरिफिकेशन पूरी करें वरना आपका खाता फ्रीज हो जाएगा।"),
 ("5 ATTACK: SEBI name + .xyz link",
  "Advisory from SEBI. Kindly complete your account update at https://sebi-kyc-portal.xyz/update at your convenience."),
 ("6 ATTACK: Zerodha name + .info link",
  "Zerodha Broking Limited notice. Please deposit funds via https://zerodha-secure-payments.info/pay"),
]

async def main():
    from app.services.gemini_service import GeminiService
    from app.services.registry_service import RegistryService
    svc = PhishingService(GeminiService(), RegistryService())
    print("="*100)
    for title, text in CASES:
        p = await svc.analyze_text(text)
        r = calculate_trust_score(hash_result=None, phishing_result=p, voice_result=None, video_result=None, registry_result=p.registry_match, seal_result=None)
        eb = p.entity_binding
        print(f"\n### {title}")
        print(f"    SCORE {r['trust_score']:>3}/100   VERDICT {r['verdict']}")
        print(f"    binding={eb.status!r} entity={eb.entity!r} offending={eb.offending_domains}")
        print(f"    registry: found={p.registry_match.found} matched={p.registry_match.matched_entity!r} basis={p.registry_match.match_basis!r}")
        print(f"    ai_degraded={p.ai_degraded}")
        for c in r["checks"]:
            print(f"      [{c.status.value if hasattr(c.status,'value') else c.status:<4}] {c.module:<9} {c.contribution:>+4}  {c.label}")
            print(f"             hi: {c.label_hi!r}")
    print("\n" + "="*100)

asyncio.run(main())
