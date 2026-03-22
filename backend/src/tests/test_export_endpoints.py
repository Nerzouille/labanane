"""Tests for REST export endpoints: GET /api/export/{run_id}/markdown and /pdf."""
import pytest
from starlette.testclient import TestClient
from src.main import app
import src.store as store_mod

SAMPLE_MARKDOWN = """# Market Analysis: test product

**Date**: 2026-03-22
**Run ID**: test-run-123
**Verdict**: conditional

---

## Keywords Used

- desk mat

---

## Viability Score

Score: 74/100

Good viability.

---

## Go / No-Go: conditional

Moderate opportunity.

---

## Key Risks

- Competition

---

## Key Opportunities

- Eco angle

---

## Marketplace Products

| Product | Price | Rating | Reviews |
|---------|-------|--------|---------|
| Test Desk Mat | EUR 24.99 | 4.3/5 | 1247 |

---

## Market Trends (Google Trends)

*(Trend data is descriptive text — charts are browser-only)*

---

## Target Persona

Remote workers.

---

## Differentiation Angles

Bundle with cable tray.

---

## Competitive Overview

Logitech dominates.

---

## Scoring Criteria

| Criterion | Score |
|-----------|-------|
| Market size | 80/100 |
"""


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def seed_report():
    """Pre-populate _reports with a test markdown entry."""
    store_mod._reports["test-run-123"] = SAMPLE_MARKDOWN
    yield
    store_mod._reports.pop("test-run-123", None)


# ── Markdown export ───────────────────────────────────────────────────────


def test_markdown_export_returns_200(client):
    resp = client.get("/api/export/test-run-123/markdown")
    assert resp.status_code == 200


def test_markdown_export_content_type_is_text_markdown(client):
    resp = client.get("/api/export/test-run-123/markdown")
    assert "text/markdown" in resp.headers.get("content-type", "")


def test_markdown_export_content_disposition_is_attachment(client):
    resp = client.get("/api/export/test-run-123/markdown")
    cd = resp.headers.get("content-disposition", "")
    assert "attachment" in cd


def test_markdown_export_filename_contains_run_id(client):
    resp = client.get("/api/export/test-run-123/markdown")
    cd = resp.headers.get("content-disposition", "")
    assert "test-run-123" in cd


def test_markdown_export_body_contains_score_line(client):
    resp = client.get("/api/export/test-run-123/markdown")
    assert "Score: 74/100" in resp.text


def test_markdown_export_body_starts_with_h1(client):
    resp = client.get("/api/export/test-run-123/markdown")
    assert resp.text.startswith("# Market Analysis:")


# ── PDF export ────────────────────────────────────────────────────────────


def test_pdf_export_returns_200(client):
    resp = client.get("/api/export/test-run-123/pdf")
    assert resp.status_code == 200


def test_pdf_export_content_type_is_pdf(client):
    resp = client.get("/api/export/test-run-123/pdf")
    assert "application/pdf" in resp.headers.get("content-type", "")


def test_pdf_export_content_disposition_is_attachment(client):
    resp = client.get("/api/export/test-run-123/pdf")
    cd = resp.headers.get("content-disposition", "")
    assert "attachment" in cd


def test_pdf_export_body_starts_with_pdf_magic(client):
    resp = client.get("/api/export/test-run-123/pdf")
    assert resp.content[:4] == b"%PDF"


def test_pdf_export_body_is_non_empty(client):
    resp = client.get("/api/export/test-run-123/pdf")
    assert len(resp.content) > 100


# ── 404 cases ─────────────────────────────────────────────────────────────


def test_markdown_export_unknown_run_id_returns_404(client):
    resp = client.get("/api/export/nonexistent-run-id/markdown")
    assert resp.status_code == 404


def test_pdf_export_unknown_run_id_returns_404(client):
    resp = client.get("/api/export/nonexistent-run-id/pdf")
    assert resp.status_code == 404


def test_markdown_export_when_store_empty_returns_404(client):
    store_mod._reports.clear()
    resp = client.get("/api/export/test-run-123/markdown")
    assert resp.status_code == 404


def test_pdf_export_when_store_empty_returns_404(client):
    store_mod._reports.clear()
    resp = client.get("/api/export/test-run-123/pdf")
    assert resp.status_code == 404
