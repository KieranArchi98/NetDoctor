"""
QRunnable implementation for background task execution.

Workers accept cancellation flags and emit progress, error, and finished signals.
"""

import threading
from typing import Callable, Any, Optional
from PySide6.QtCore import QObject, QRunnable, Signal, QThreadPool


class WorkerSignals(QObject):
    """Signals that can be emitted by TaskWorker."""

    def __init__(self, parent=None):
        super().__init__(parent)

    progress = Signal(int)  # Progress percentage (0-100)
    row = Signal(dict)  # Emit a row of data (dict)
    log = Signal(str)  # Emit a log message
    error = Signal(str)  # Emit an error message
    finished = Signal(object)  # Emit final result object


class TaskWorker(QRunnable):
    """
    QRunnable worker that wraps a callable and supports cancellation.

    The worker executes a function in a background thread and emits signals
    for progress, results, errors, and completion. Supports graceful cancellation
    via a thread-safe Event flag.

    Usage example:
        ```python
        from PySide6.QtCore import QThreadPool

        def my_long_task(worker, cancel_flag):
            for i in range(100):
                if cancel_flag.is_set():
                    worker.log.emit("Task cancelled")
                    return None
                worker.progress.emit(i)
                worker.row.emit({"iteration": i, "value": i * 2})
                time.sleep(0.1)
            return {"total": 100}

        signals = WorkerSignals()
        worker = TaskWorker(my_long_task, signals)

        # Connect signals to UI slots
        signals.progress.connect(progress_bar.setValue)
        signals.row.connect(lambda row: table_model.add_row(row))
        signals.finished.connect(on_task_complete)
        signals.error.connect(show_error_message)

        # Start the worker
        QThreadPool.globalInstance().start(worker)

        # To cancel:
        # worker.cancel()
        ```
    """

    def __init__(
        self,
        func: Callable[[WorkerSignals, threading.Event], Any],
        signals: Optional[WorkerSignals] = None,
    ):
        """
        Initialize TaskWorker.

        Args:
            func: Callable that takes (signals, cancel_flag) as arguments.
                  The function should check cancel_flag.is_set() periodically
                  and return a result object when complete.
            signals: Optional WorkerSignals instance. If None, creates a new one.
        """
        super().__init__()
        self.func = func
        self.signals = signals if signals is not None else WorkerSignals()
        self._cancel = threading.Event()
        self._result = None
        self._error = None

    def run(self):
        """
        Execute the wrapped function in the worker thread.

        Catches exceptions and emits error signals. Emits finished signal
        with the function's return value (or None if cancelled/errored).
        """
        try:
            self.signals.log.emit("Task started")
            self._result = self.func(self.signals, self._cancel)
            if self._cancel.is_set():
                self.signals.log.emit("Task cancelled")
                self.signals.finished.emit(None)
            else:
                self.signals.log.emit("Task completed")
                self.signals.finished.emit(self._result)
        except Exception as e:
            error_msg = f"Task error: {str(e)}"
            self._error = error_msg
            self.signals.error.emit(error_msg)
            self.signals.finished.emit(None)

    def cancel(self):
        """
        Request cancellation of the running task.

        Sets the cancellation flag. The wrapped function should check
        cancel_flag.is_set() periodically and exit gracefully.
        """
        self._cancel.set()
        self.signals.log.emit("Cancellation requested")

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancel.is_set()
