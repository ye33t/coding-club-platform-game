"""Input abstraction layer for key mappings."""

import pygame


class Input:
    """Abstraction layer for input handling.

    Maps physical keys to logical actions, making controls rebindable
    and state code cleaner.
    """

    # Key mappings (physical keys -> logical actions)
    # These could be loaded from config in the future
    KEY_LEFT = pygame.K_a
    KEY_RIGHT = pygame.K_d
    KEY_UP = pygame.K_w
    KEY_DOWN = pygame.K_s
    KEY_JUMP = pygame.K_k
    KEY_RUN = pygame.K_j

    @staticmethod
    def is_left(keys) -> bool:
        """Check if left action is pressed."""
        return bool(keys[Input.KEY_LEFT])

    @staticmethod
    def is_right(keys) -> bool:
        """Check if right action is pressed."""
        return bool(keys[Input.KEY_RIGHT])

    @staticmethod
    def is_up(keys) -> bool:
        """Check if up action is pressed."""
        return bool(keys[Input.KEY_UP])

    @staticmethod
    def is_down(keys) -> bool:
        """Check if down action is pressed."""
        return bool(keys[Input.KEY_DOWN])

    @staticmethod
    def is_jump(keys) -> bool:
        """Check if jump action is pressed."""
        return bool(keys[Input.KEY_JUMP])

    @staticmethod
    def is_run(keys) -> bool:
        """Check if run action is pressed."""
        return bool(keys[Input.KEY_RUN])
