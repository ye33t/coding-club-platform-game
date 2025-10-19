"""Score tracking helpers for enemy defeats and combo chains."""

from __future__ import annotations

from enum import Enum, auto
from weakref import WeakKeyDictionary


class ScoreType(Enum):
    """Categories of scoring actions that have combo behavior."""

    STOMP = auto()
    SHELL_CHAIN = auto()
    SHELL_KICK = auto()


class ScoreTracker:
    """Manage combo counters and compute awarded points."""

    _STOMP_SEQUENCE = [
        100,
        200,
        400,
        500,
        800,
        1000,
        2000,
        4000,
        5000,
        8000,
    ]

    _SHELL_SEQUENCE = [
        500,
        800,
        1000,
        2000,
        4000,
        5000,
        8000,
    ]

    _SHELL_KICK_SCORE = 400

    def __init__(self) -> None:
        self._stomp_index = 0
        self._shell_indices: "WeakKeyDictionary[object, int]" = WeakKeyDictionary()

    def reset_all(self) -> None:
        """Reset all combo tracking."""
        self._stomp_index = 0
        self._shell_indices.clear()

    def reset_stomp_chain(self) -> None:
        """Reset the stomp combo counter."""
        self._stomp_index = 0

    def reset_shell_combo(self, shell: object | None = None) -> None:
        """Reset the combo counter for a shell, or all shells if None."""
        if shell is None:
            self._shell_indices.clear()
            return
        self._shell_indices.pop(shell, None)

    def record(
        self,
        score_type: ScoreType,
        *,
        source: object | None = None,
    ) -> int:
        """Record a scoring event and return the awarded points."""
        if score_type is ScoreType.STOMP:
            index = min(self._stomp_index, len(self._STOMP_SEQUENCE) - 1)
            value = self._STOMP_SEQUENCE[index]
            if self._stomp_index < len(self._STOMP_SEQUENCE) - 1:
                self._stomp_index += 1
            return value

        if score_type is ScoreType.SHELL_CHAIN:
            if source is None:
                return self._SHELL_SEQUENCE[0]
            shell = source
            index = self._shell_indices.get(shell, 0)
            value = self._SHELL_SEQUENCE[min(index, len(self._SHELL_SEQUENCE) - 1)]
            if index < len(self._SHELL_SEQUENCE) - 1:
                self._shell_indices[shell] = index + 1
            else:
                self._shell_indices[shell] = index
            return value

        if score_type is ScoreType.SHELL_KICK:
            if source is not None:
                self._shell_indices.pop(source, None)
            return self._SHELL_KICK_SCORE

        return 0
