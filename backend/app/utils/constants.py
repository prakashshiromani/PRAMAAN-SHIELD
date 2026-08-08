"""
PRAMAAN-SHIELD — Shared Constants
File: backend/app/utils/constants.py
"""

# SHA-256 of the empty string. Used as a placeholder before real content hashes
# are computed — shared so no copy can drift (previously hardcoded with two
# different spellings in four files).
EMPTY_SHA256 = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
