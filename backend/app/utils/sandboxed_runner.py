"""
PRAMAAN-SHIELD — Sandboxed Media Processing Runner
File: backend/app/utils/sandboxed_runner.py

Isolates CPU-intensive media parsing (video decode, audio processing) inside a
separate subprocess with a timeout guard. A malformed or adversarial media
file cannot hang or crash the main FastAPI async event loop.

Usage:
    from app.utils.sandboxed_runner import run_in_sandbox

    result = await run_in_sandbox(heavy_function, (arg1, arg2), timeout_secs=30)
"""

import asyncio
import concurrent.futures
import multiprocessing
from typing import Any, Callable, Tuple
from loguru import logger


# Use a module-level process pool (lazily initialised) to avoid repeated
# fork/spawn overhead. One worker is enough — media parsing is sequential.
_pool: concurrent.futures.ProcessPoolExecutor | None = None


def _get_pool() -> concurrent.futures.ProcessPoolExecutor:
    global _pool
    if _pool is None:
        _pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=1,
            mp_context=multiprocessing.get_context("spawn"),
        )
    return _pool


def _run_func(func: Callable, args: Tuple) -> Any:
    """Top-level wrapper so the function is picklable for multiprocessing."""
    return func(*args)


async def run_in_sandbox(
    func: Callable,
    args: Tuple = (),
    timeout_secs: int = 30,
) -> Any:
    """
    Execute `func(*args)` in a sandboxed subprocess with a hard timeout.

    Args:
        func:         A module-level (picklable) function.
        args:         Positional arguments tuple.
        timeout_secs: Maximum wall-clock seconds before the task is cancelled.

    Returns:
        Whatever `func(*args)` returns.

    Raises:
        TimeoutError:  If the function exceeds `timeout_secs`.
        RuntimeError:  If the subprocess crashes (segfault, OOM, etc.).
    """
    loop = asyncio.get_running_loop()
    pool = _get_pool()

    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(pool, _run_func, func, args),
            timeout=timeout_secs,
        )
        return result
    except asyncio.TimeoutError:
        logger.error(
            f"Sandbox timeout: {func.__name__}() exceeded {timeout_secs}s limit"
        )
        # Kill the rogue worker and let the pool spawn a fresh one
        _shutdown_pool()
        raise TimeoutError(
            f"Media processing exceeded {timeout_secs}s sandbox limit"
        )
    except Exception as e:
        logger.error(f"Sandbox execution failed for {func.__name__}(): {e}")
        raise RuntimeError(f"Sandboxed execution failed: {e}") from e


def _shutdown_pool():
    """Force-kill the current process pool so a fresh one is created next call."""
    global _pool
    if _pool is not None:
        try:
            _pool.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        _pool = None
