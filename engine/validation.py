# [`engine/validation.py`](engine/validation.py:1)
"""
Validation models and helpers for the HMLV simulator.

This module provides typed dataclasses for ValidationIssue and ValidationReport,
plus utilities to parse the phase-1 string-style issues emitted by validators.

Purpose:
- Centralize Validation types so other modules can import a stable API.
- Provide JSON-serializable dict views for reports.
- Offer a small parser for legacy string issue format used in Phase-1.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any


@dataclass
class ValidationIssue:
    file: Optional[str]
    row: Optional[int]
    column: Optional[str]
    message: str
    severity: str = "error"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    valid: bool
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "warnings": [w.to_dict() for w in self.warnings],
            "errors": [e.to_dict() for e in self.errors],
        }

    def extend_from_legacy_strings(self, warnings_strs: List[str], errors_strs: List[str]) -> None:
        """
        Parse legacy string-formatted issues and append them to this report.

        Legacy format:
          "file:{name},row:{row},column:{col},message:{text}"
        """
        for w in warnings_strs:
            issue = parse_legacy_issue(w, severity="warning")
            self.warnings.append(issue)
        for e in errors_strs:
            issue = parse_legacy_issue(e, severity="error")
            self.errors.append(issue)


def parse_legacy_issue(s: str, severity: str = "error") -> ValidationIssue:
    """
    Parse a legacy issue string into a ValidationIssue instance.

    Best-effort parsing; missing parts are set to None.
    """
    file = None
    row = None
    column = None
    message = s
    try:
        for part in s.split(","):
            if ":" not in part:
                continue
            k, v = part.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k == "file":
                file = v or None
            elif k == "row":
                try:
                    row = int(v)
                except Exception:
                    row = None
            elif k == "column":
                column = v or None
            elif k == "message":
                message = v or message
    except Exception:
        # fallback: store entire string as message
        message = s
    return ValidationIssue(file=file, row=row, column=column, message=message, severity=severity)