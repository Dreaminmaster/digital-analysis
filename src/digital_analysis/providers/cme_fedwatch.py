from __future__ import annotations

from dataclasses import dataclass

from ..execution.http import JsonHttpClient, UrllibHttpClient
from .base import ProviderParseError, SignalProvider

_URL = "https://www.cmegroup.com/services/fed-funds-target/fed-funds-target.json"


def _coerce_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_target_range(raw: str) -> tuple[float, float] | None:
    parts = raw.split("-")
    if len(parts) != 2:
        return None
    low = _coerce_float(parts[0])
    high = _coerce_float(parts[1])
    if low is None or high is None:
        return None
    return low / 100.0, high / 100.0


@dataclass(frozen=True)
class FedRateProb:
    target_low: float
    target_high: float
    probability: float


@dataclass(frozen=True)
class FedMeetingProbability:
    meeting_date: str
    current_target_low: float
    current_target_high: float
    probabilities: tuple[FedRateProb, ...]


class CMEFedWatchProvider(SignalProvider):
    provider_id = "cme_fedwatch"
    display_name = "CME FedWatch"
    capabilities = ("rate_probabilities",)

    def __init__(self, http_client: JsonHttpClient | None = None) -> None:
        self.http_client = http_client or UrllibHttpClient()

    def get_probabilities(self) -> list[FedMeetingProbability]:
        data = self.http_client.get_json(_URL)
        meetings_raw = self._extract_meetings(data)
        if meetings_raw is None:
            raise ProviderParseError("cannot locate meetings data in CME FedWatch response")
        results: list[FedMeetingProbability] = []
        for item in meetings_raw:
            parsed = self._parse_meeting(item)
            if parsed is not None:
                results.append(parsed)
        return results

    @staticmethod
    def _extract_meetings(data: object) -> list[object] | None:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("meetings", "Meetings", "data"):
                val = data.get(key)
                if isinstance(val, list):
                    return val
            if "meetingDate" in data or "meeting_date" in data:
                return [data]
        return None

    @staticmethod
    def _parse_meeting(item: object) -> FedMeetingProbability | None:
        if not isinstance(item, dict):
            return None
        meeting_date = item.get("meetingDate") or item.get("meeting_date") or ""
        if not meeting_date:
            return None
        current_raw = item.get("currentTarget") or item.get("current_target") or ""
        current_range = _parse_target_range(str(current_raw))
        if current_range is None:
            return None
        probs_raw = item.get("probabilities") or item.get("Probabilities") or {}
        probs: list[FedRateProb] = []
        if isinstance(probs_raw, dict):
            for range_key, prob_val in probs_raw.items():
                rng = _parse_target_range(str(range_key))
                p = _coerce_float(prob_val)
                if rng is None or p is None or p == 0.0:
                    continue
                probs.append(FedRateProb(target_low=rng[0], target_high=rng[1], probability=p / 100.0))
        return FedMeetingProbability(
            meeting_date=str(meeting_date),
            current_target_low=current_range[0],
            current_target_high=current_range[1],
            probabilities=tuple(probs),
        )
