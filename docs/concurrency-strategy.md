# Concurrency Strategy for APGI Framework

## Overview

This document defines the concurrency model and governance for the APGI Framework, ensuring consistent, safe, and performant concurrent operations across all components.

## Concurrency Patterns

### 1. Threading (ThreadPoolExecutor)

**Use Cases:**

- I/O-bound operations (file I/O, network requests)
- CPU-bound operations that can be parallelized with limited GIL impact
- Background tasks that don't require real-time responsiveness

**Guidelines:**

- Use `ThreadPoolExecutor` with bounded worker pools
- Default max workers: `min(32, os.cpu_count() + 4)`
- Always use context managers: `with ThreadPoolExecutor() as executor:`
- Implement proper shutdown in finally blocks

**Example:**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_data(items):
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_item, item) for item in items]
        for future in as_completed(futures):
            yield future.result()
```

### 2. Asyncio

**Use Cases:**

- High-concurrency network operations (websockets, HTTP clients)
- Real-time data streaming
- Event-driven architectures with many concurrent connections

**Guidelines:**

- Use async/await for I/O-bound operations
- Avoid blocking calls in async functions
- Use `asyncio.run()` for entry points
- Implement proper cancellation handling

**Example:**

```python
import asyncio

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 3. Web Sockets

**Use Cases:**

- Real-time bi-directional communication
- Live data streaming (EEG, physiological signals)
- Interactive GUI updates

**Guidelines:**

- Use connection pooling with limits
- Implement heartbeat/ping-pong for health checks
- Handle reconnection with exponential backoff
- Use message queues for backpressure

## Backpressure Controls

### 1. Bounded Queues

```python
from queue import Queue
import threading

# Bounded queue prevents unbounded memory growth
work_queue = Queue(maxsize=1000)

def producer():
    try:
        work_queue.put(item, block=True, timeout=1.0)
    except queue.Full:
        logger.warning("Queue full, dropping item")
```

### 2. Semaphore Limits

```python
from asyncio import Semaphore

# Limit concurrent operations
semaphore = Semaphore(max_concurrent=10)

async def process_with_limit(item):
    async with semaphore:
        return await process(item)
```

### 3. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second):
    min_interval = 1.0 / calls_per_second
    def decorator(func):
        last_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

## Lifecycle Governance

### 1. Graceful Shutdown

```python
import signal
import threading

class Service:
    def __init__(self):
        self._shutdown_event = threading.Event()
        self._threads = []
    
    def start(self):
        # Start background threads
        thread = threading.Thread(target=self._worker, daemon=True)
        thread.start()
        self._threads.append(thread)
    
    def stop(self):
        self._shutdown_event.set()
        for thread in self._threads:
            thread.join(timeout=5.0)
    
    def _worker(self):
        while not self._shutdown_event.is_set():
            # Do work
            pass
```

### 2. Cancellation Semantics

```python
import asyncio

class CancellableTask:
    def __init__(self):
        self._cancel_event = asyncio.Event()
    
    async def run(self):
        try:
            while not self._cancel_event.is_set():
                await self.do_work()
        except asyncio.CancelledError:
            logger.info("Task cancelled, cleaning up")
            raise
        finally:
            await self.cleanup()
    
    def cancel(self):
        self._cancel_event.set()
```

### 3. Resource Cleanup

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        cleanup_resource(resource)
```

## Component-Specific Guidelines

### Neural Simulators

- Use threading for parallel simulation runs
- Limit concurrent simulations to CPU count
- Implement result caching to avoid redundant computation

### Data Processing

- Use ThreadPoolExecutor for batch processing
- Implement chunk-based processing for large datasets
- Use progress callbacks for long-running operations

### GUI Components

- Use asyncio for event loop integration
- Keep UI thread responsive with background workers
- Implement debouncing for frequent updates

### Network Operations

- Use asyncio for HTTP/websocket clients
- Implement connection pooling with limits
- Use timeouts for all network calls
- Implement retry logic with exponential backoff

## Monitoring and Observability

### 1. Metrics Collection

```python
import time
from collections import defaultdict

class ConcurrencyMetrics:
    def __init__(self):
        self.active_threads = 0
        self.queue_sizes = defaultdict(int)
        self.execution_times = []
    
    def record_execution(self, duration):
        self.execution_times.append(duration)
        if len(self.execution_times) > 1000:
            self.execution_times = self.execution_times[-1000:]
```

### 2. Logging

```python
import logging

logger = logging.getLogger(__name__)

def log_concurrency_state():
    logger.info(
        f"Active threads: {threading.active_count()}, "
        f"Queue size: {work_queue.qsize()}"
    )
```

## Testing Guidelines

### 1. Thread Safety Testing

```python
import pytest
import threading

def test_thread_safety():
    shared_resource = []
    def append_value(value):
        shared_resource.append(value)
    
    threads = [threading.Thread(target=append_value, args=(i,)) for i in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(shared_resource) == 100
```

### 2. Deadlock Detection

```python
import pytest
import timeout_decorator

@timeout_decorator.timeout(5)
def test_no_deadlock():
    # Code that should not deadlock
    pass
```

## Decision Matrix

|Scenario|Recommended Pattern|Rationale|
|---|---|---|
|CPU-bound computation|ThreadPoolExecutor|Utilizes multiple cores|
|I/O-bound network calls|Asyncio|High concurrency, low overhead|
|File I/O operations|ThreadPoolExecutor|Simpler than async file I/O|
|Real-time streaming|Asyncio + WebSockets|Low latency, bidirectional|
|Batch data processing|ThreadPoolExecutor|Parallelizable chunks|
|GUI event handling|Main thread + background workers|UI responsiveness|

## Enforcement

### Code Review Checklist

- [ ] Thread pools have explicit max worker limits
- [ ] Queues are bounded to prevent memory leaks
- [ ] Async functions use proper error handling
- [ ] Resources are cleaned up in finally blocks
- [ ] Shutdown handlers are implemented
- [ ] Backpressure controls are in place

### Static Analysis

- Use `mypy` to detect async/await misuse
- Use `flake8` with `flake8-async` plugin
- Use `bandit` for security issues in concurrent code

## References

- Python Concurrency: <https://docs.python.org/3/library/concurrency.html>
- Asyncio Best Practices: <https://docs.python.org/3/library/asyncio-dev.html>
- Thread Safety: <https://docs.python.org/3/glossary.html#term-thread-safe>
