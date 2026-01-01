import argparse
from pathlib import Path
from sql_connector import init_db
from lyrics_generator import LyricsGenerator
from common_constants.constants import MUSIC_ROOT_PATH


def main():
    """Main entry point for the LRC generator."""
    parser = argparse.ArgumentParser(
        description="Generate LRC files for audio files using Whisper"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=MUSIC_ROOT_PATH,
        help=f"Root directory containing audio files (default: {MUSIC_ROOT_PATH})",
    )

    args = parser.parse_args()

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        return

    if not directory.is_dir():
        print(f"Error: Path is not a directory: {directory}")
        return

    print("=" * 60)
    print("LRC File Generator - Using Whisper + Gemini")
    print("=" * 60)
    print(f"Processing directory: {directory}")
    print(f"This may take a while depending on the number of files...")
    print("=" * 60)

    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("Database initialized successfully")

    # Create lyrics generator and process directory
    generator = LyricsGenerator()
    generator.process_directory(directory)

    print("\n" + "=" * 60)
    print("All done! Check your audio file directories for .lrc files")
    print("=" * 60)


if __name__ == "__main__":
    main()
