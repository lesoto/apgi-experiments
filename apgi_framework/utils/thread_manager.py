"""Thread pool manager for APGI Framework to control resource usage."""

import concurrent.futures
import threading
import logging
from typing import Callable, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ThreadPoolManager:
    """Manages thread pools with resource limits and proper cleanup."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=8,  # Limit to 8 concurrent threads
                thread_name_prefix="apgi-worker",
            )
            self._active_futures = set()
            self._shutdown = False
            logger.info("ThreadPoolManager initialized with max_workers=8")

    def submit(self, fn: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Submit a task to the thread pool."""
        if self._shutdown:
            raise RuntimeError("ThreadPoolManager is shutting down")

        future = self._executor.submit(fn, *args, **kwargs)
        self._active_futures.add(future)
        future.add_done_callback(self._active_futures.discard)

        logger.debug(f"Submitted task {fn.__name__} to thread pool")
        return future

    def submit_with_timeout(
        self,
        fn: Callable,
        timeout: Optional[float] = None,
        *args,
        **kwargs,
    ) -> concurrent.futures.Future:
        """Submit a task with optional timeout."""
        if self._shutdown:
            raise RuntimeError("ThreadPoolManager is shutting down")

        future = self._executor.submit(fn, *args, **kwargs)
        self._active_futures.add(future)

        # Add timeout wrapper if specified
        if timeout:
            future = self._wrap_future_with_timeout(future, timeout)

        future.add_done_callback(self._active_futures.discard)

        logger.debug(f"Submitted task {fn.__name__} with timeout {timeout}s")
        return future

    def _wrap_future_with_timeout(
        self, future: concurrent.futures.Future, timeout: float
    ) -> concurrent.futures.Future:
        """Wrap a future with timeout functionality."""
        import threading
        import time

        timeout_event = threading.Event()
        timeout_future = concurrent.futures.Future()

        def timeout_monitor():
            if not timeout_event.wait(timeout):
                if not future.done():
                    future.cancel()
                    timeout_future.set_exception(
                        TimeoutError(f"Task timed out after {timeout}s")
                    )

        monitor_thread = threading.Thread(target=timeout_monitor, daemon=True)
        monitor_thread.start()

        def transfer_result(f):
            timeout_event.set()
            if f.cancelled():
                timeout_future.cancel()
            elif f.exception():
                timeout_future.set_exception(f.exception())
            else:
                timeout_future.set_result(f.result())

        future.add_done_callback(transfer_result)
        return timeout_future

    def submit_with_callback(
        self,
        fn: Callable,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        timeout: Optional[float] = None,
        *args,
        **kwargs,
    ) -> concurrent.futures.Future:
        """Submit a task with optional success/error callbacks and timeout."""
        future = self.submit_with_timeout(fn, timeout, *args, **kwargs)

        if callback or error_callback:

            def done_callback(fut: concurrent.futures.Future):
                try:
                    result = fut.result()
                    if callback:
                        callback(result)
                except Exception as e:
                    logger.error(f"Task {fn.__name__} failed: {e}")
                    if error_callback:
                        error_callback(e)

            future.add_done_callback(done_callback)

        return future

    def wait_for_completion(self, timeout: Optional[float] = None) -> None:
        """Wait for all active tasks to complete."""
        if not self._active_futures:
            return

        logger.info(f"Waiting for {len(self._active_futures)} tasks to complete")
        concurrent.futures.wait(self._active_futures, timeout=timeout)

    def cancel_all(self) -> None:
        """Cancel all pending tasks."""
        cancelled = 0
        for future in list(self._active_futures):
            if future.cancel():
                cancelled += 1

        logger.info(f"Cancelled {cancelled} pending tasks")

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool."""
        if self._shutdown:
            return

        self._shutdown = True
        logger.info("Shutting down ThreadPoolManager")

        self.cancel_all()
        self._executor.shutdown(wait=wait)

    @property
    def active_count(self) -> int:
        """Get the number of active tasks."""
        return len(self._active_futures)

    @property
    def is_shutdown(self) -> bool:
        """Check if the manager is shutting down."""
        return self._shutdown


# Global instance
thread_manager = ThreadPoolManager()


@contextmanager
def managed_thread_operation():
    """Context manager for thread-safe operations."""
    try:
        yield thread_manager
    except Exception as e:
        logger.error(f"Thread operation failed: {e}")
        raise
    finally:
        # Clean up completed futures
        pass


def run_in_thread(
    fn: Callable,
    callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
    timeout: Optional[float] = None,
    *args,
    **kwargs,
) -> concurrent.futures.Future:
    """Convenience function to run a function in a managed thread."""
    return thread_manager.submit_with_callback(
        fn, callback, error_callback, timeout, *args, **kwargs
    )


def get_thread_stats() -> dict:
    """Get current thread pool statistics."""
    return {
        "active_tasks": thread_manager.active_count,
        "max_workers": 8,
        "is_shutdown": thread_manager.is_shutdown,
        "thread_count": threading.active_count(),
    }
