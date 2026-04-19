from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..execution.http import JsonHttpClient, UrllibHttpClient
from .base import ProviderError, ProviderParseError, SignalProvider

EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions"
EDGAR_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


@dataclass(frozen=True)
class EdgarInsiderQuery:
    ticker: str
    limit: int = 20


@dataclass(frozen=True)
class EdgarFiling:
    accession_number: str
    form_type: str
    filing_date: str
    report_date: str
    primary_document: str
    description: str


@dataclass(frozen=True)
class EdgarInsiderSummary:
    ticker: str
    company_name: str
    cik: str
    recent_form4s: tuple[EdgarFiling, ...]
    total_form4_count: int


class EdgarProvider(SignalProvider):
    provider_id = "sec_edgar"
    display_name = "SEC EDGAR"
    capabilities = ("insider_transactions",)

    def __init__(self, http_client: JsonHttpClient | None = None, user_email: str | None = None):
        if http_client is None:
            ua = f"digital-analysis/0.1 ({user_email})" if user_email else "digital-analysis/0.1"
            http_client = UrllibHttpClient(headers={
                "Accept": "application/json",
                "User-Agent": ua,
            })
        self.http_client: JsonHttpClient = http_client
        self._ticker_map: dict[str, dict[str, Any]] | None = None

    def _resolve_cik(self, ticker: str) -> tuple[str, str]:
        if self._ticker_map is None:
            data = self.http_client.get_json(EDGAR_TICKERS_URL)
            if not isinstance(data, Mapping):
                raise ProviderParseError("expected company_tickers.json to be an object")
            self._ticker_map = {}
            for entry in data.values():
                if not isinstance(entry, Mapping):
                    continue
                t = str(entry.get("ticker", "")).upper()
                if t:
                    self._ticker_map[t] = dict(entry)
        ticker_upper = ticker.upper()
        entry = self._ticker_map.get(ticker_upper)
        if not entry:
            raise ProviderError(f"ticker not found: {ticker}")
        cik = str(entry["cik_str"]).zfill(10)
        return cik, str(entry.get("title", ""))

    def get_insider_transactions(self, query: EdgarInsiderQuery) -> EdgarInsiderSummary:
        cik, company_name = self._resolve_cik(query.ticker)
        submissions = self.http_client.get_json(f"{EDGAR_SUBMISSIONS_URL}/CIK{cik}.json")
        if not isinstance(submissions, Mapping):
            raise ProviderParseError("expected submissions response to be an object")
        filings_block = submissions.get("filings")
        if not isinstance(filings_block, Mapping):
            raise ProviderParseError("expected submissions.filings to be an object")
        recent = filings_block.get("recent")
        if not isinstance(recent, Mapping):
            raise ProviderParseError("expected submissions.filings.recent to be an object")

        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        primary_documents = recent.get("primaryDocument", [])
        primary_doc_descriptions = recent.get("primaryDocDescription", [])

        form4_filings: list[EdgarFiling] = []
        total_form4_count = 0
        for i in range(len(forms)):
            if str(forms[i]) != "4":
                continue
            total_form4_count += 1
            if len(form4_filings) < query.limit:
                form4_filings.append(
                    EdgarFiling(
                        accession_number=str(accession_numbers[i]) if i < len(accession_numbers) else "",
                        form_type="4",
                        filing_date=str(filing_dates[i]) if i < len(filing_dates) else "",
                        report_date=str(report_dates[i]) if i < len(report_dates) else "",
                        primary_document=str(primary_documents[i]) if i < len(primary_documents) else "",
                        description=str(primary_doc_descriptions[i]) if i < len(primary_doc_descriptions) else "",
                    )
                )
        return EdgarInsiderSummary(
            ticker=query.ticker.upper(),
            company_name=company_name,
            cik=cik,
            recent_form4s=tuple(form4_filings),
            total_form4_count=total_form4_count,
        )
