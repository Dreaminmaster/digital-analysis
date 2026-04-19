from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class GatherError(RuntimeError):
    def __init__(self, message: str, results: dict[str, Any], errors: dict[str, BaseException]) -> None:
        super().__init__(message)
        self.results = results
        self.errors = errors


@dataclass(frozen=True)
class GatherResult:
    results: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, BaseException] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def get(self, key: str) -> Any:
        if key in self.errors:
            raise self.errors[key]
        return self.results[key]

    def get_or(self, key: str, default: T) -> Any:
        if key in self.errors:
            return default
        return self.results.get(key, default)


def gather(
    tasks: dict[str, Callable[[], Any]],
    *,
    max_workers: int | None = None,
    timeout_seconds: float | None = None,
    fail_fast: bool = False,
) -> GatherResult:
    if not tasks:
        return GatherResult()

    effective_workers = max_workers if max_workers is not None else len(tasks)
    results: dict[str, Any] = {}
    errors: dict[str, BaseException] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=effective_workers) as pool:
        future_to_label = {pool.submit(fn): label for label, fn in tasks.items()}
        done, not_done = concurrent.futures.wait(
            future_to_label,
            timeout=timeout_seconds,
            return_when=(
                concurrent.futures.FIRST_EXCEPTION if fail_fast else concurrent.futures.ALL_COMPLETED
            ),
        )
        for future in done:
            label = future_to_label[future]
            try:
                results[label] = future.result(timeout=0)
            except BaseException as exc:
                errors[label] = exc
        for future in not_done:
            label = future_to_label[future]
            future.cancel()
            errors[label] = TimeoutError(f"task {label!r} did not complete within {timeout_seconds}s")

    if fail_fast and errors:
        first_label = next(iter(errors))
        raise GatherError(
            f"task {first_label!r} failed: {errors[first_label]}",
            results=results,
            errors=errors,
        )

    return GatherResult(results=results, errors=errors)
