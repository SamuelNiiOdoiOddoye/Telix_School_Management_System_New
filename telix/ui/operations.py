"""Runs a data operation and reports the outcome to the user."""

from __future__ import annotations

import logging
from typing import Any, Callable

from telix.core.errors import StorageError, ValidationError
from telix.ui.feedback import Feedback

LOGGER = logging.getLogger("telix.ui.operations")


class OperationRunner:
    def __init__(self, feedback: Feedback) -> None:
        self._feedback = feedback

    def run(
        self,
        operation: Callable[[], Any],
        success_message: str,
        on_success: Callable[[], None],
    ) -> None:
        """Run ``operation``; show an error on failure, or refresh and confirm on success."""
        try:
            operation()
        except (ValidationError, StorageError) as error:
            LOGGER.warning("UI operation rejected or storage failed (%s)", type(error).__name__)
            self._feedback.error(str(error))
            return
        except Exception as error:  # last-resort guard so the UI never crashes
            LOGGER.error("Unexpected UI operation failure (%s)", type(error).__name__)
            self._feedback.error(f"The operation could not be completed: {error}")
            return
        on_success()
        self._feedback.success(success_message)
