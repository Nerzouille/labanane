"""Shared in-memory stores.

_reports: keyed by run_id → rendered markdown string.
Populated by step 9 (ReportGenerationStep) and read by the export route.
Not deleted on WebSocket disconnect so the user can download after the run ends.
"""

_reports: dict[str, str] = {}
