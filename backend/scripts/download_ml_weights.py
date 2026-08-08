"""
PRAMAAN-SHIELD - ML Model Weights Automatic Downloader
File: backend/scripts/download_ml_weights.py

Teeno ML models ke weights automatically download karta hai:
  1. AASIST       -> backend/app/ml/aasist/weights/aasist.pth
  2. RawNet2      -> backend/app/ml/rawnet2/weights/rawnet2.pth
  3. EfficientNet -> backend/app/ml/deepfake/weights/efficientnet_b4.pth

Run karo (backend/ folder se):
    python scripts/download_ml_weights.py

Ya project root se:
    python backend/scripts/download_ml_weights.py
"""

import os
import sys
import zipfile
import shutil
import io
from pathlib import Path

# Windows UTF-8 fix
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# --- COLOR CODES ---
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def log_info(msg):    print(f"{CYAN}[INFO]{RESET}  {msg}")
def log_ok(msg):      print(f"{GREEN}[OK]{RESET}    {msg}")
def log_warn(msg):    print(f"{YELLOW}[WARN]{RESET}  {msg}")
def log_error(msg):   print(f"{RED}[ERROR]{RESET} {msg}")
def log_step(msg):    print(f"\n{BOLD}{CYAN}" + "-" * 60 + f"{RESET}\n{BOLD}{msg}{RESET}")

# --- PATHS ---
# Script backend/scripts/ mein hai, backend/ root parent hai
_SCRIPT_DIR  = Path(__file__).resolve().parent
_BACKEND_ROOT = _SCRIPT_DIR.parent  # backend/

AASIST_WEIGHTS_DIR       = _BACKEND_ROOT / "app" / "ml" / "aasist"  / "weights"
RAWNET2_WEIGHTS_DIR      = _BACKEND_ROOT / "app" / "ml" / "rawnet2" / "weights"
EFFICIENTNET_WEIGHTS_DIR = _BACKEND_ROOT / "app" / "ml" / "deepfake" / "weights"

AASIST_PATH       = AASIST_WEIGHTS_DIR       / "aasist.pth"
RAWNET2_PATH      = RAWNET2_WEIGHTS_DIR      / "rawnet2.pth"
EFFICIENTNET_PATH = EFFICIENTNET_WEIGHTS_DIR / "efficientnet_b4.pth"

# Min size checks (bytes)
AASIST_MIN_SIZE       =  1 * 1024 * 1024   # 1  MB
RAWNET2_MIN_SIZE      = 50 * 1024 * 1024   # 50 MB
EFFICIENTNET_MIN_SIZE = 50 * 1024 * 1024   # 50 MB


def ensure_dirs():
    for d in [AASIST_WEIGHTS_DIR, RAWNET2_WEIGHTS_DIR, EFFICIENTNET_WEIGHTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    log_ok("Weight directories verified/created.")


def is_valid_file(path: Path, min_size: int) -> bool:
    return path.exists() and path.stat().st_size >= min_size


def download_file(url: str, dest: Path, desc: str = "") -> bool:
    """Download with progress bar. Uses requests if available, else urllib."""
    import urllib.request

    log_info(f"Downloading: {desc or url}")
    log_info(f"  Saving to: {dest}")

    try:
        import requests
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = int(downloaded * 50 / total)
                        bar = "█" * pct + "░" * (50 - pct)
                        mb_d = downloaded / 1024 / 1024
                        mb_t = total / 1024 / 1024
                        print(f"\r  [{bar}] {mb_d:.1f}/{mb_t:.1f} MB", end="", flush=True)
        print()
        return True

    except ImportError:
        log_warn("'requests' not found — using urllib (no progress bar).")
        try:
            urllib.request.urlretrieve(url, dest)
            return True
        except Exception as e:
            log_error(f"urllib download failed: {e}")
            return False

    except Exception as e:
        log_error(f"Download failed: {e}")
        if dest.exists():
            dest.unlink()
        return False


# ──────────────────────────────────────────────────────────────────────────────
# MODEL 1: AASIST  (~15 MB)
# Source: Official clovaai/aasist GitHub
# ──────────────────────────────────────────────────────────────────────────────
AASIST_URL = "https://github.com/clovaai/aasist/raw/main/models/weights/AASIST.pth"

def download_aasist() -> bool:
    log_step("Step 1/3  AASIST (Audio Anti-Spoofing Graph Attention Network)")
    if is_valid_file(AASIST_PATH, AASIST_MIN_SIZE):
        log_ok(f"AASIST already present ({AASIST_PATH.stat().st_size/1024/1024:.1f} MB). Skipping.")
        return True

    log_info("Source: clovaai/aasist — official CLOVA AI GitHub repo")
    ok = download_file(AASIST_URL, AASIST_PATH, "AASIST.pth")

    if ok and is_valid_file(AASIST_PATH, AASIST_MIN_SIZE):
        log_ok(f"AASIST downloaded! Size: {AASIST_PATH.stat().st_size/1024/1024:.1f} MB")
        return True

    log_warn("Direct download failed. Trying git sparse-checkout fallback...")
    return _aasist_git_fallback()


def _aasist_git_fallback() -> bool:
    tmp = AASIST_WEIGHTS_DIR / "_tmp_aasist"
    try:
        import subprocess
        cmds = [
            ["git", "clone", "--depth=1", "--filter=blob:none", "--sparse",
             "https://github.com/clovaai/aasist.git", str(tmp)],
            ["git", "-C", str(tmp), "sparse-checkout", "set", "models/weights"],
            ["git", "-C", str(tmp), "checkout"],
        ]
        for cmd in cmds:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(r.stderr)

        src = tmp / "models" / "weights" / "AASIST.pth"
        if src.exists():
            shutil.copy2(src, AASIST_PATH)
            log_ok(f"AASIST via git: {AASIST_PATH.stat().st_size/1024/1024:.1f} MB")
            return True
        else:
            log_error("AASIST.pth not found in cloned repo.")
            _manual_aasist()
            return False
    except Exception as e:
        log_error(f"Git fallback failed: {e}")
        _manual_aasist()
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _manual_aasist():
    print(f"""
{YELLOW}Manual Download — AASIST:{RESET}
  1. Open: https://github.com/clovaai/aasist
  2. Navigate: models → weights → AASIST.pth
  3. Click "Download raw file"
  4. Save as: {AASIST_PATH}
""")


# ──────────────────────────────────────────────────────────────────────────────
# MODEL 2: RawNet2  (~25 MB)
# Source: ASVspoof.org official + eurecom-asp fallback
# ──────────────────────────────────────────────────────────────────────────────
RAWNET2_ZIP_URL = "https://www.asvspoof.org/asvspoof2021/pre_trained_DF_RawNet2.zip"
RAWNET2_ALT_URL = "https://github.com/eurecom-asp/rawnet2-antispoofing/raw/main/pre_trained_DF_RawNet2.pth"

def download_rawnet2() -> bool:
    log_step("Step 2/3  RawNet2 (Raw Waveform CNN Anti-Spoofing)")
    if is_valid_file(RAWNET2_PATH, RAWNET2_MIN_SIZE):
        log_ok(f"RawNet2 already present ({RAWNET2_PATH.stat().st_size/1024/1024:.1f} MB). Skipping.")
        return True

    # Try direct .pth from eurecom-asp GitHub mirror first (much faster CDN)
    log_info("Source: eurecom-asp/rawnet2-antispoofing GitHub (Fast CDN)")
    ok = download_file(RAWNET2_ALT_URL, RAWNET2_PATH, "pre_trained_DF_RawNet2.pth")

    if ok and is_valid_file(RAWNET2_PATH, RAWNET2_MIN_SIZE):
        log_ok(f"RawNet2 downloaded! Size: {RAWNET2_PATH.stat().st_size/1024/1024:.1f} MB")
        return True

    # Fallback: ZIP from ASVspoof.org
    log_info("Fallback: ASVspoof.org official DF track ZIP")
    zip_dest = RAWNET2_WEIGHTS_DIR / "_rawnet2.zip"
    ok2 = download_file(RAWNET2_ZIP_URL, zip_dest, "pre_trained_DF_RawNet2.zip")

    if ok2 and zip_dest.exists() and zip_dest.stat().st_size > 1024:
        log_info("ZIP extracting...")
        extracted_ok = False
        try:
            with zipfile.ZipFile(zip_dest, "r") as zf:
                pth_files = [n for n in zf.namelist() if n.endswith(".pth")]
                if pth_files:
                    data = zf.read(pth_files[0])
                    RAWNET2_PATH.write_bytes(data)
                    log_ok(f"RawNet2 extracted! Size: {RAWNET2_PATH.stat().st_size/1024/1024:.1f} MB")
                    extracted_ok = True
        except Exception as e:
            log_warn(f"ZIP extraction failed: {e}")

        # Delete temp zip outside context manager so file lock is released
        if zip_dest.exists():
            try:
                zip_dest.unlink()
            except Exception:
                pass

        if extracted_ok:
            return True

    log_error("RawNet2 automatic download failed.")
    _manual_rawnet2()
    return False


def _manual_rawnet2():
    print(f"""
{YELLOW}Manual Download — RawNet2:{RESET}
  Option A:
    URL: https://www.asvspoof.org/asvspoof2021/pre_trained_DF_RawNet2.zip
    ZIP extract karo, .pth file yahan save karo:
    {RAWNET2_PATH}

  Option B (Direct):
    URL: https://github.com/eurecom-asp/rawnet2-antispoofing
    Save as: {RAWNET2_PATH}
""")


# ──────────────────────────────────────────────────────────────────────────────
# MODEL 3: EfficientNet-B4  (~75 MB)
# Source: timm library — ImageNet pretrained weights auto-download
# Note: Backend HACKATHON → PRODUCTION mode mein switch ho jayega
# ──────────────────────────────────────────────────────────────────────────────
def download_efficientnet() -> bool:
    log_step("Step 3/3  EfficientNet-B4 (Video Deepfake Frame Analysis)")
    if is_valid_file(EFFICIENTNET_PATH, EFFICIENTNET_MIN_SIZE):
        log_ok(f"EfficientNet-B4 already present ({EFFICIENTNET_PATH.stat().st_size/1024/1024:.1f} MB). Skipping.")
        return True

    log_info("Source: timm model hub — EfficientNet-B4 ImageNet pretrained")
    log_info("(~75 MB download, please wait...)")

    try:
        import torch
        import timm

        model = timm.create_model("efficientnet_b4", pretrained=True, num_classes=1000)
        model.eval()
        torch.save(model.state_dict(), EFFICIENTNET_PATH)

        if is_valid_file(EFFICIENTNET_PATH, EFFICIENTNET_MIN_SIZE):
            log_ok(f"EfficientNet-B4 saved! Size: {EFFICIENTNET_PATH.stat().st_size/1024/1024:.1f} MB")
            log_warn("Note: Ye ImageNet weights hain — hackathon ke liye perfect hai.")
            log_info("Backend restart karo — PRODUCTION mode activate hoga!")
            return True
        else:
            log_error("File saved but too small.")
            return False

    except ImportError as e:
        log_error(f"Import error: {e}")
        log_warn("Fix: pip install timm torch")
        return False
    except Exception as e:
        log_error(f"EfficientNet download failed: {e}")
        _manual_efficientnet()
        return False


def _manual_efficientnet():
    print(f"""
{YELLOW}Manual Download — EfficientNet-B4:{RESET}
  Python shell mein run karo:
    import torch, timm
    m = timm.create_model("efficientnet_b4", pretrained=True, num_classes=1000)
    torch.save(m.state_dict(), r"{EFFICIENTNET_PATH}")
""")


# ──────────────────────────────────────────────────────────────────────────────
# FINAL VERIFICATION TABLE
# ──────────────────────────────────────────────────────────────────────────────
def verify_all():
    log_step("Final Verification")
    checks = [
        ("AASIST       (aasist.pth)",         AASIST_PATH,       AASIST_MIN_SIZE),
        ("RawNet2      (rawnet2.pth)",         RAWNET2_PATH,      RAWNET2_MIN_SIZE),
        ("EfficientNet (efficientnet_b4.pth)", EFFICIENTNET_PATH, EFFICIENTNET_MIN_SIZE),
    ]
    sep = "-" * 66
    print(f"\n  {'Model':<46} {'Size':>9}   Status")
    print(f"  {sep}")
    all_ok = True
    for name, path, min_sz in checks:
        if path.exists():
            sz = path.stat().st_size / 1024 / 1024
            if path.stat().st_size >= min_sz:
                status = f"{GREEN}READY{RESET}"
            else:
                status = f"{YELLOW}TOO SMALL{RESET}"
                all_ok = False
        else:
            sz = 0
            status = f"{RED}MISSING{RESET}"
            all_ok = False
        print(f"  {name:<46} {sz:>7.1f} MB   {status}")
    print(f"  {sep}")

    if all_ok:
        print(f"\n{GREEN}{BOLD}  Sab models ready! ML category: 100%{RESET}")
        print(f"{GREEN}  Backend restart karo -- PRODUCTION mode activate hoga!{RESET}\n")
    else:
        print(f"\n{YELLOW}  Kuch files missing. Upar manual instructions dekho.{RESET}\n")
    return all_ok


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    print(
        f"\n{BOLD}{CYAN}"
        "  +============================================================+\n"
        "  |     PRAMAAN-SHIELD -- ML Weights Auto Downloader           |\n"
        "  |     AASIST + RawNet2 + EfficientNet-B4                     |\n"
        "  +============================================================+\n"
        f"{RESET}"
    )


    ensure_dirs()

    # Dependency check
    log_step("Checking Dependencies")
    try:
        import torch
        log_ok(f"PyTorch {torch.__version__}")
    except ImportError:
        log_error("PyTorch missing! Run: pip install torch")
        sys.exit(1)

    try:
        import timm
        log_ok(f"timm {timm.__version__}")
    except ImportError:
        log_warn("timm missing - EfficientNet step will fail. Fix: pip install timm")

    try:
        import requests
        log_ok("requests available")
    except ImportError:
        log_warn("requests missing - using urllib fallback. Fix: pip install requests")

    # Download all three
    r1 = download_aasist()
    r2 = download_rawnet2()
    r3 = download_efficientnet()

    # Report
    all_ok = verify_all()
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
