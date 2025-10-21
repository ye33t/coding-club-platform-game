"""Heads-up display state management."""

from __future__ import annotations

from dataclasses import dataclass

from ..constants import COIN_LIFE_THRESHOLD


@dataclass(frozen=True, slots=True)
class HudDimensions:
    """Fixed display widths for HUD numeric values."""

    score_digits: int
    coin_digits: int
    timer_digits: int


class HudState:
    """Track score, coins, timer, and level label for the HUD."""

    def __init__(self, dimensions: HudDimensions) -> None:
        self._dimensions = dimensions
        self.score: int = 0
        self.coins: int = 0
        self.timer_value: int = 0
        self.level_label: str = ""
        self._timer_frames_per_decrement: int = 0
        self._timer_frame_accumulator: int = 0
        self.lives: int = 0

    @property
    def score_digits(self) -> int:
        return self._dimensions.score_digits

    @property
    def coin_digits(self) -> int:
        return self._dimensions.coin_digits

    @property
    def timer_digits(self) -> int:
        return self._dimensions.timer_digits

    def reset(
        self,
        *,
        display_label: str,
        timer_start: int,
        frames_per_decrement: int,
    ) -> None:
        """Reset HUD values for a new level or restart."""
        self.score = 0
        self.coins = 0
        self._apply_level_settings(display_label, timer_start, frames_per_decrement)

    def reset_for_new_game(
        self,
        *,
        initial_lives: int,
        display_label: str,
        timer_start: int,
        frames_per_decrement: int,
    ) -> None:
        """Reset all HUD values, including lives, for a new run."""
        self.set_lives(initial_lives)
        self.reset(
            display_label=display_label,
            timer_start=timer_start,
            frames_per_decrement=frames_per_decrement,
        )

    def _apply_level_settings(
        self,
        display_label: str,
        timer_start: int,
        frames_per_decrement: int,
    ) -> None:
        self.level_label = display_label.upper()
        self.timer_value = max(0, int(timer_start))
        self._timer_frames_per_decrement = max(1, int(frames_per_decrement))
        self._timer_frame_accumulator = 0

    def add_score(self, amount: int) -> None:
        """Increase the score by the provided amount."""
        if amount <= 0:
            return
        self.score = min(self.score + amount, self._max_value(self.score_digits))

    def add_coins(self, amount: int) -> int:
        """Increase the coin counter, returning the number of rollovers."""
        if amount <= 0:
            return 0
        threshold = COIN_LIFE_THRESHOLD
        total = self.coins + amount
        rollovers = total // threshold
        self.coins = total % threshold
        return rollovers

    def set_lives(self, lives: int) -> None:
        """Directly assign the life counter."""
        self.lives = max(0, lives)

    def gain_life(self, count: int = 1) -> None:
        """Increment lives by the provided count."""
        if count <= 0:
            return
        self.lives = max(0, self.lives + count)

    def lose_life(self, count: int = 1) -> int:
        """Decrement lives and return the remaining count."""
        if count <= 0:
            return self.lives
        self.lives = max(0, self.lives - count)
        return self.lives

    def has_lives_remaining(self) -> bool:
        """Whether Mario still has lives left."""
        return self.lives > 0

    def tick_timer(self, frames: int = 1) -> None:
        """Advance the level timer using frame-based cadence."""
        if self.timer_value <= 0:
            return

        self._timer_frame_accumulator += max(0, frames)
        while (
            self.timer_value > 0
            and self._timer_frame_accumulator >= self._timer_frames_per_decrement
        ):
            self._timer_frame_accumulator -= self._timer_frames_per_decrement
            self.timer_value = max(0, self.timer_value - 1)

    def configure_for_level(
        self,
        *,
        display_label: str,
        timer_start: int,
        frames_per_decrement: int,
        preserve_progress: bool = False,
    ) -> None:
        """Apply level metadata, optionally preserving score/coin totals."""
        if preserve_progress:
            saved_score = self.score
            saved_coins = self.coins
            self._apply_level_settings(display_label, timer_start, frames_per_decrement)
            self.score = saved_score
            self.coins = saved_coins
        else:
            self.reset(
                display_label=display_label,
                timer_start=timer_start,
                frames_per_decrement=frames_per_decrement,
            )

    def formatted_score(self) -> str:
        """Score padded to configured width."""
        return f"{self.score:0{self.score_digits}d}"

    def formatted_coins(self) -> str:
        """Coin total padded to configured width."""
        mod_value = self._max_value(self.coin_digits) + 1
        display_value = self.coins % mod_value
        return f"{display_value:0{self.coin_digits}d}"

    def formatted_timer(self) -> str:
        """Timer value padded to configured width."""
        capped = min(self.timer_value, self._max_value(self.timer_digits))
        return f"{capped:0{self.timer_digits}d}"

    @staticmethod
    def _max_value(digits: int) -> int:
        return int(pow(10, digits) - 1)
