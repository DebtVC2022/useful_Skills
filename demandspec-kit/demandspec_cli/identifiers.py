from __future__ import annotations

import hashlib
import re
import unicodedata


LEGACY_SLUGS = {
    "拜访单自动生成": "visit-form-auto-generation",
    "风控模型智能化升级": "risk-model-ai-upgrade",
    "逾期容忍度模型优化": "overdue-tolerance-model-optimization",
    "征信报告信息提取": "credit-report-extraction",
    "移动端贷审助手": "mobile-loan-review-assistant",
}


def stable_slug(text: str, fallback_prefix: str = "demand") -> str:
    normalized = text.strip().lower()
    if normalized in LEGACY_SLUGS:
        return LEGACY_SLUGS[normalized]

    ascii_text = (
        unicodedata.normalize("NFKD", normalized)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    readable = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    has_non_ascii = any(ord(char) > 127 for char in normalized)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8]

    if readable and not has_non_ascii:
        return readable
    if readable:
        return f"{readable}-{digest}"
    return f"{fallback_prefix}-{digest}"
