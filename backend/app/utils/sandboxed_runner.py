"""
PRAMAAN-SHIELD — Sandboxed Media Processing Runner
File: backend/app/utils/sandboxed_runner.py

Isolates CPU-intensive media parsing (video decode, audio processing) inside a
separate subprocess with a timeout guard. A malformed or adversarial media
file cannot hang or crash the main FastAPI async event loop.

Design: one short-lived process PER CALL (spawn context). Each call gets its
own subprocess so a timeout hard-terminates exactly the rogue worker — never a
sibling scan's future (a shared ProcessPoolExecutor + shutdown(cancel_futures)
would cancel the OTHER concurrent scan and orphan the timed-out worker).

Usage:
    from app.utils.sandboxed_runner import run_in_sandbox

    result = await run_in_sandbox(heavy_function, (arg1, arg2), timeout_secs=30)
"""

import asyncio
import multiprocessing as mp
import os
from typing import Any, Callable, Tuple
from loguru import logger

# Start method picker. On POSIX, "fork" inherits the parent's already-loaded ML
# models copy-on-write — a sandboxed worker then adds ~0 MB of model RAM and
# never re-downloads/re-loads weights (a fresh "spawn" child loads its own full
# ViT/AASIST stacks: 3x redundant model copies blew the Render 512MB box → OOM
# → proxy 502). Windows has no fork, so it keeps the picklable spawn path.
def _pick_context() -> str:
    if hasattr(os, "fork"):
        try:
            mp.get_context("fork")
            return "fork"
        except Exception:
            pass
    return "spawn"


def _run_func(func: Callable, args: Tuple, queue) -> None:
    """Top-level wrapper (picklable under spawn). Puts the result on the queue."""
    queue.put(func(*args))


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
        timeout_secs: Maximum wall-clock seconds before the process is killed.

    Returns:
        Whatever `func(*args)` returns.

    Raises:
        TimeoutError: If the function exceeds `timeout_secs`.
        RuntimeError: If the subprocess crashes (segfault, OOM, etc.).
    """
    ctx = mp.get_context(_pick_context())
    queue = ctx.SimpleQueue()
    proc = ctx.Process(target=_run_func, args=(func, args, queue), daemon=True)

    proc.start()
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(queue.get), timeout=timeout_secs
        )
        return result
    except (asyncio.TimeoutError, TimeoutError):
        logger.error(f"Sandbox timeout: {func.__name__}() exceeded {timeout_secs}s limit")
        _terminate(proc)
        raise TimeoutError(
            f"Media processing exceeded {timeout_secs}s sandbox limit"
        )
    except Exception as e:
        logger.error(f"Sandbox execution failed for {func.__name__}(): {e}")
        _terminate(proc)
        raise RuntimeError(f"Sandboxed execution failed: {e}") from e
    finally:
        # Close the queue on EVERY exit path, including timeouts. The worker
        # thread blocked inside `queue.get()` cannot be cancelled by asyncio —
        # without this, every sandbox timeout would permanently leak a
        # blocked worker thread until the thread pool is exhausted.
        try:
            queue.close()
        except Exception:
            pass


def _terminate(proc: mp.Process) -> None:
    """Hard-kill the rogue worker. Never touch anything else — each call owns
    its own process, so sibling scans are unaffected."""
    if proc.is_alive():
        try:
            proc.terminate()
            proc.join(timeout=5)
        except Exception:
            pass
    if proc.is_alive():
        try:
            proc.kill()
        except Exception:
            pass


async def run_sandboxed_or_thread(
    func: Callable,
    args: Tuple = (),
    *,
    timeout_secs: int,
    fallback: Callable,
    task_label: str,
) -> Any:
    """
    Run `func(*args)` sandboxed with a hard timeout; if the sandbox layer is
    unavailable (spawn errors, missing fork support, etc.), degrade gracefully
    to an in-process worker thread. The asyncio event loop is never blocked.

    Shared by VoiceAnalyzer.analyze / VideoAnalyzer.analyze — previously each
    duplicated this try/except fallback dance.
    """
    try:
        return await run_in_sandbox(func, args, timeout_secs=timeout_secs)
    except TimeoutError:
        # Wall-clock deadline exceeded. NEVER silently re-run the analysis
        # un-sandboxed: that would void the timeout exactly for the adversarial
        # file the sandbox exists to stop. The caller downgrades to SKIP.
        raise
    except Exception as e:
        logger.warning(
            f"Sandboxed {task_label} unavailable ({e}); using in-process worker thread"
        )
        # Sandbox machinery failure (spawn/pickle/stdio), not a timeout. A
        # worker thread can't be hard-killed, so at least bound the wait so a
        # failing analysis cannot hold the request (or the pool) indefinitely.
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(fallback), timeout=timeout_secs
            )
        except (asyncio.TimeoutError, TimeoutError):
            logger.error(f"Fallback {task_label} exceeded {timeout_secs}s; skipping analysis")
            raise TimeoutError(
                f"Media processing exceeded {timeout_secs}s processing limit"
            )
