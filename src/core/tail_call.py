from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class TailCall:
    deferred_call: Callable[[], Any]


def tail_call_optimized(step: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(step)
    def driver(*args: Any, **kwargs: Any) -> Any:
        current = step(*args, **kwargs)
        while isinstance(current, TailCall):
            current = current.deferred_call()
        return current

    return driver


@dataclass(frozen=True)
class AsyncTailCall:
    deferred_call: Callable[[], Awaitable[Any]]


def async_tail_call_optimized(
    step: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    @wraps(step)
    async def driver(*args: Any, **kwargs: Any) -> Any:
        current = await step(*args, **kwargs)
        while isinstance(current, AsyncTailCall):
            current = await current.deferred_call()
        return current

    return driver


def depth_first_search(
    get_children: Callable[[T], list[T]], transform: Callable[[T], R]
) -> Callable[[list[T], list[R]], list[R]]:
    def _step(pending: list[T], done: list[R]) -> Any:
        if not pending:
            return done
        head, *rest = pending
        return TailCall(
            lambda: _step(
                [*get_children(head), *rest], [*done, transform(head)]
            )
        )

    return tail_call_optimized(_step)
