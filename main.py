import argparse
import time
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.common_constants.constants import MUSIC_ROOT_PATH
from core.src.LyricsGenerator import LyricsGenerator
from core.utils.sql_connector import init_db
from core.utils.llm_utils import RateLimitError
from core.utils.logging_utils import get_logger

logger = get_logger(__name__)


def process_directory_scheduled(directory):
    """
    Process a directory and handle rate limit errors gracefully.

    Args:
        directory: Path to the directory to process
    """
    try:
        logger.info("=" * 60)
        logger.info("Starting scheduled LRC generation run")
        logger.info("=" * 60)

        # Create lyrics generator and process directory
        generator = LyricsGenerator()
        generator.process_directory(directory)

        logger.info("=" * 60)
        logger.info("Scheduled run completed successfully")
        logger.info("=" * 60)

    except RateLimitError as e:
        logger.error("=" * 60)
        logger.error(f"RATE LIMIT ENCOUNTERED: {e}")
        logger.error("Will retry in 24 hours...")
        logger.error("=" * 60)
        # The scheduler will automatically retry in 24 hours

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Unexpected error during processing: {e}", exc_info=True)
        logger.error("Will retry in 24 hours...")
        logger.error("=" * 60)


def main():
    """Main entry point for the LRC generator with 24-hour scheduling."""
    parser = argparse.ArgumentParser(
        description="Generate LRC files for audio files using Whisper (runs every 24 hours)"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=MUSIC_ROOT_PATH,
        help=f"Root directory containing audio files (default: {MUSIC_ROOT_PATH})",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit instead of scheduling every 24 hours",
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

    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("Database initialized successfully\n")

    # If --once flag is set, run once and exit
    if args.once:
        logger.info("Running in single-run mode (--once)")
        process_directory_scheduled(directory)
        return

    # Otherwise, schedule to run every 24 hours
    logger.info("Starting scheduler - will run immediately and every 24 hours")
    
    # Run immediately first
    process_directory_scheduled(directory)
    
    scheduler = BlockingScheduler()

    # Schedule the job to run every 24 hours after the initial run
    scheduler.add_job(
        process_directory_scheduled,
        IntervalTrigger(hours=24),
        args=[directory],
        id="lrc_generation",
        name="LRC Generation Job",
        replace_existing=True,
    )

    print("=" * 60)
    print("Scheduler started - running again in 24 hours")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    try:
        # Run the scheduler (blocking - continues indefinitely)
        scheduler.start()
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Scheduler stopped by user")
        print("=" * 60)
        scheduler.shutdown()


def main_legacy():
    """Legacy entry point for single run (deprecated - use --once flag instead)."""
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
