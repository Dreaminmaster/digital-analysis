from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Protocol

from ._coerce import _coerce_float, _coerce_int
from .base import ProviderParseError, SignalProvider


def _norm_cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def _norm_pdf(x: float) -> float:
    return math.exp(-x * x / 2.0) / math.sqrt(2.0 * math.pi)


@dataclass(frozen=True)
class OptionGreeks:
    delta: float
    gamma: float
    theta: float
    vega: float


def black_scholes_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> OptionGreeks | None:
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return None
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + sigma * sigma / 2.0) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    pdf_d1 = _norm_pdf(d1)
    gamma = pdf_d1 / (S * sigma * sqrt_T)
    vega = S * pdf_d1 * sqrt_T / 100.0
    if option_type == "call":
        delta = _norm_cdf(d1)
        theta = (-S * pdf_d1 * sigma / (2.0 * sqrt_T) - r * K * math.exp(-r * T) * _norm_cdf(d2)) / 365.0
    else:
        delta = _norm_cdf(d1) - 1.0
        theta = (-S * pdf_d1 * sigma / (2.0 * sqrt_T) + r * K * math.exp(-r * T) * _norm_cdf(-d2)) / 365.0
    return OptionGreeks(delta=delta, gamma=gamma, theta=theta, vega=vega)


@dataclass(frozen=True)
class OptionsChainQuery:
    ticker: str
    expiration: str | None = None
    risk_free_rate: float = 0.045
    compute_greeks: bool = True


@dataclass(frozen=True)
class OptionContract:
    contract_symbol: str
    option_type: str
    expiration: str
    strike: float
    last_price: float | None = None
    bid: float | None = None
    ask: float | None = None
    mid: float | None = None
    volume: int | None = None
    open_interest: int | None = None
    implied_volatility: float | None = None
    in_the_money: bool | None = None
    greeks: OptionGreeks | None = None


@dataclass(frozen=True)
class OptionsExpirations:
    ticker: str
    expirations: tuple[str, ...]


@dataclass
class OptionsChain:
    ticker: str
    expiration: str
    underlying_price: float | None
    calls: tuple[OptionContract, ...]
    puts: tuple[OptionContract, ...]

    @property
    def atm_strike(self) -> float | None:
        if self.underlying_price is None:
            return None
        strikes = [c.strike for c in self.calls] or [p.strike for p in self.puts]
        if not strikes:
            return None
        return min(strikes, key=lambda s: abs(s - self.underlying_price))

    @property
    def atm_call(self) -> OptionContract | None:
        strike = self.atm_strike
        return next((c for c in self.calls if c.strike == strike), None) if strike is not None else None

    @property
    def atm_put(self) -> OptionContract | None:
        strike = self.atm_strike
        return next((p for p in self.puts if p.strike == strike), None) if strike is not None else None

    @property
    def atm_iv(self) -> float | None:
        ivs = [x.implied_volatility for x in (self.atm_call, self.atm_put) if x is not None and x.implied_volatility is not None]
        return sum(ivs) / len(ivs) if ivs else None

    def implied_move(self) -> float | None:
        call = self.atm_call
        put = self.atm_put
        if call is None or put is None or self.underlying_price is None:
            return None
        call_mid = call.mid if call.mid is not None else call.last_price
        put_mid = put.mid if put.mid is not None else put.last_price
        if call_mid is None or put_mid is None or self.underlying_price <= 0:
            return None
        return (call_mid + put_mid) / self.underlying_price


@dataclass(frozen=True)
class _ChainRows:
    calls: list[dict[str, Any]]
    puts: list[dict[str, Any]]


class OptionsFetcher(Protocol):
    def fetch_expirations(self, ticker: str) -> tuple[str, ...]: ...
    def fetch_chain(self, ticker: str, expiration: str) -> _ChainRows: ...
    def fetch_underlying_price(self, ticker: str) -> float | None: ...


class _YFinanceFetcher:
    def __init__(self) -> None:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise ProviderParseError("yfinance is required for YFinanceProvider") from exc
        self.yf = yf

    def fetch_expirations(self, ticker: str) -> tuple[str, ...]:
        stock = self.yf.Ticker(ticker)
        return tuple(stock.options)

    def fetch_chain(self, ticker: str, expiration: str) -> _ChainRows:
        stock = self.yf.Ticker(ticker)
        chain = stock.option_chain(expiration)
        calls = chain.calls.to_dict("records")
        puts = chain.puts.to_dict("records")
        return _ChainRows(calls=calls, puts=puts)

    def fetch_underlying_price(self, ticker: str) -> float | None:
        stock = self.yf.Ticker(ticker)
        info = getattr(stock, "fast_info", None)
        if info is not None:
            try:
                value = info.get("lastPrice")
            except AttributeError:
                value = None
            v = _coerce_float(value)
            if v is not None:
                return v
        hist = stock.history(period="5d")
        if hist is None or hist.empty:
            return None
        return _coerce_float(hist["Close"].iloc[-1])


class YFinanceProvider(SignalProvider):
    provider_id = "yfinance"
    display_name = "Yahoo Finance Options"
    capabilities = ("options_chain", "options_expirations", "greeks")

    def __init__(self, *, fetcher: OptionsFetcher | None = None) -> None:
        self._fetcher: OptionsFetcher = fetcher or _YFinanceFetcher()

    def get_expirations(self, ticker: str) -> OptionsExpirations:
        exps = self._fetcher.fetch_expirations(ticker.upper())
        return OptionsExpirations(ticker=ticker.upper(), expirations=exps)

    def get_chain(self, query: OptionsChainQuery) -> OptionsChain:
        ticker = query.ticker.upper()
        expiration = query.expiration
        if expiration is None:
            exps = self._fetcher.fetch_expirations(ticker)
            if not exps:
                raise ProviderParseError(f"no options expirations found for {ticker}")
            expiration = exps[0]
        raw = self._fetcher.fetch_chain(ticker, expiration)
        underlying = self._fetcher.fetch_underlying_price(ticker)
        try:
            exp_date = datetime.strptime(expiration, "%Y-%m-%d").date()
            days_to_exp = (exp_date - date.today()).days
            T = max(days_to_exp, 0) / 365.0
        except ValueError:
            T = 0.0
        calls = self._parse_contracts(raw.calls, "call", expiration, underlying, T, query.risk_free_rate, query.compute_greeks)
        puts = self._parse_contracts(raw.puts, "put", expiration, underlying, T, query.risk_free_rate, query.compute_greeks)
        return OptionsChain(ticker=ticker, expiration=expiration, underlying_price=underlying, calls=tuple(calls), puts=tuple(puts))

    def _parse_contracts(self, rows: list[dict[str, Any]], option_type: str, expiration: str, underlying: float | None, T: float, risk_free_rate: float, compute_greeks: bool) -> list[OptionContract]:
        contracts: list[OptionContract] = []
        for row in rows:
            strike = _coerce_float(row.get("strike"))
            if strike is None:
                continue
            bid = _coerce_float(row.get("bid"))
            ask = _coerce_float(row.get("ask"))
            mid = (bid + ask) / 2.0 if bid is not None and ask is not None else None
            iv = _coerce_float(row.get("impliedVolatility"))
            greeks = None
            if compute_greeks and iv is not None and underlying is not None and T > 0:
                greeks = black_scholes_greeks(underlying, strike, T, risk_free_rate, iv, option_type)
            in_the_money = row.get("inTheMoney")
            contracts.append(
                OptionContract(
                    contract_symbol=str(row.get("contractSymbol", "")),
                    option_type=option_type,
                    expiration=expiration,
                    strike=strike,
                    last_price=_coerce_float(row.get("lastPrice")),
                    bid=bid,
                    ask=ask,
                    mid=mid,
                    volume=_coerce_int(row.get("volume")),
                    open_interest=_coerce_int(row.get("openInterest")),
                    implied_volatility=iv,
                    in_the_money=bool(in_the_money) if in_the_money is not None else None,
                    greeks=greeks,
                )
            )
        return contracts
