"""Main entry point for the game."""

from game.game import Game


def main():
    """Main function."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()