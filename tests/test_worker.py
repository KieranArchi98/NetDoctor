"""
Unit tests for TaskWorker and WorkerSignals.
"""

import time
import threading
from PySide6.QtCore import QCoreApplication, QThreadPool, QTimer
from PySide6.QtTest import QSignalSpy
import pytest

from netdoctor.workers.task_worker import TaskWorker, WorkerSignals


@pytest.fixture
def app():
    """Create QCoreApplication for testing Qt signals."""
    if not QCoreApplication.instance():
        app = QCoreApplication([])
    else:
        app = QCoreApplication.instance()
    return app


def test_worker_signals_creation():
    """Test that WorkerSignals can be instantiated."""
    signals = WorkerSignals()
    assert signals is not None
    assert hasattr(signals, "progress")
    assert hasattr(signals, "row")
    assert hasattr(signals, "log")
    assert hasattr(signals, "error")
    assert hasattr(signals, "finished")


def test_worker_basic_execution(app):
    """Test that a simple task executes and emits finished signal."""
    result_container = {"value": None}

    def simple_task(signals, cancel_flag):
        """Simple task that returns a result."""
        signals.log.emit("Running simple task")
        return {"status": "success", "value": 42}

    signals = WorkerSignals()
    worker = TaskWorker(simple_task, signals)

    # Spy on signals
    finished_spy = QSignalSpy(signals.finished)
    log_spy = QSignalSpy(signals.log)

    def on_finished(result):
        result_container["value"] = result

    signals.finished.connect(on_finished)

    # Start worker
    QThreadPool.globalInstance().start(worker)

    # Wait for thread pool to finish and process events
    thread_pool = QThreadPool.globalInstance()
    timeout = 5.0
    start_time = time.time()
    while finished_spy.count() == 0 and (time.time() - start_time) < timeout:
        thread_pool.waitForDone(100)  # Wait up to 100ms
        app.processEvents()
        time.sleep(0.01)

    # Verify signals were emitted
    assert finished_spy.count() > 0
    assert result_container["value"] == {"status": "success", "value": 42}
    assert log_spy.count() >= 2  # "Task started" and "Task completed"


def test_worker_progress_emission(app):
    """Test that progress signals are emitted correctly."""
    progress_values = []

    def progress_task(signals, cancel_flag):
        """Task that emits progress."""
        for i in range(0, 101, 25):
            if cancel_flag.is_set():
                return None
            signals.progress.emit(i)
            time.sleep(0.01)
        return {"progress": 100}

    signals = WorkerSignals()
    worker = TaskWorker(progress_task, signals)

    def on_progress(value):
        progress_values.append(value)

    signals.progress.connect(on_progress)
    finished_spy = QSignalSpy(signals.finished)

    thread_pool = QThreadPool.globalInstance()
    thread_pool.start(worker)

    # Wait for completion
    timeout = 5.0
    start_time = time.time()
    while finished_spy.count() == 0 and (time.time() - start_time) < timeout:
        thread_pool.waitForDone(100)  # Wait up to 100ms
        app.processEvents()
        time.sleep(0.01)

    # Verify progress was emitted
    assert len(progress_values) >= 4  # At least 0, 25, 50, 75, 100
    assert 0 in progress_values
    assert 100 in progress_values


def test_worker_row_emission(app):
    """Test that row signals are emitted correctly."""
    rows_received = []

    def row_task(signals, cancel_flag):
        """Task that emits rows."""
        for i in range(5):
            if cancel_flag.is_set():
                return None
            signals.row.emit({"id": i, "data": f"item_{i}"})
            time.sleep(0.01)
        return {"rows": 5}

    signals = WorkerSignals()
    worker = TaskWorker(row_task, signals)

    def on_row(row):
        rows_received.append(row)

    signals.row.connect(on_row)
    finished_spy = QSignalSpy(signals.finished)

    thread_pool = QThreadPool.globalInstance()
    thread_pool.start(worker)

    # Wait for completion
    timeout = 5.0
    start_time = time.time()
    while finished_spy.count() == 0 and (time.time() - start_time) < timeout:
        thread_pool.waitForDone(100)  # Wait up to 100ms
        app.processEvents()
        time.sleep(0.01)

    # Verify rows were emitted
    assert len(rows_received) == 5
    assert rows_received[0] == {"id": 0, "data": "item_0"}
    assert rows_received[4] == {"id": 4, "data": "item_4"}


def test_worker_cancellation(app):
    """Test that cancellation works correctly."""
    cancelled = {"value": False}

    def long_running_task(signals, cancel_flag):
        """Long-running task that checks for cancellation."""
        for i in range(100):
            if cancel_flag.is_set():
                cancelled["value"] = True
                signals.log.emit("Cancelled in task")
                return None
            signals.progress.emit(i)
            time.sleep(0.05)  # Simulate work
        return {"completed": True}

    signals = WorkerSignals()
    worker = TaskWorker(long_running_task, signals)

    finished_spy = QSignalSpy(signals.finished)
    log_spy = QSignalSpy(signals.log)

    thread_pool = QThreadPool.globalInstance()
    thread_pool.start(worker)

    # Wait a bit for task to start running, then cancel
    time.sleep(0.15)
    worker.cancel()
    # Give a moment for cancellation to propagate
    time.sleep(0.05)

    # Wait for cancellation to complete
    timeout = 5.0
    start_time = time.time()
    while finished_spy.count() == 0 and (time.time() - start_time) < timeout:
        thread_pool.waitForDone(100)  # Wait up to 100ms
        app.processEvents()
        time.sleep(0.01)

    # Verify cancellation
    assert worker.is_cancelled()
    assert cancelled["value"] is True
    assert finished_spy.count() > 0
    # Check that log signals were emitted (including cancellation messages)
    assert log_spy.count() > 0


def test_worker_error_handling(app):
    """Test that exceptions are caught and error signals are emitted."""
    error_received = {"value": None}

    def failing_task(signals, cancel_flag):
        """Task that raises an exception."""
        raise ValueError("Test error message")

    signals = WorkerSignals()
    worker = TaskWorker(failing_task, signals)

    def on_error(error_msg):
        error_received["value"] = error_msg

    signals.error.connect(on_error)
    finished_spy = QSignalSpy(signals.finished)
    error_spy = QSignalSpy(signals.error)

    thread_pool = QThreadPool.globalInstance()
    thread_pool.start(worker)

    # Wait for error
    timeout = 5.0
    start_time = time.time()
    while finished_spy.count() == 0 and (time.time() - start_time) < timeout:
        thread_pool.waitForDone(100)  # Wait up to 100ms
        app.processEvents()
        # Process more events to ensure signals are delivered
        for _ in range(10):
            app.processEvents()
        time.sleep(0.01)

    # Verify error was handled
    assert error_spy.count() > 0
    # Process events one more time to ensure callback is called
    for _ in range(10):
        app.processEvents()
    assert error_received["value"] is not None
    assert "Test error message" in error_received["value"]
    assert finished_spy.count() > 0


def test_worker_cancel_before_start():
    """Test that cancel() can be called before the worker starts."""
    signals = WorkerSignals()
    worker = TaskWorker(lambda s, c: None, signals)

    # Cancel before starting
    worker.cancel()
    assert worker.is_cancelled()

    # Worker should still run but return None immediately
    def quick_task(signals, cancel_flag):
        if cancel_flag.is_set():
            return None
        return {"done": True}

    signals2 = WorkerSignals()
    worker2 = TaskWorker(quick_task, signals2)
    worker2.cancel()

    # The task should see the cancellation flag
    assert worker2.is_cancelled()
