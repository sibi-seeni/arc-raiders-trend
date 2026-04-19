import logging
import argparse
from src import init_db, search_new_videos, collect_comments

# Setting up Logging
logging.basicConfig(
    filename="collection_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")


def run_discovery():
    logging.info("Phase: Starting Video Discovery...")
    # Note: Each 'search.list' call costs 100 quota units
    search_new_videos()
    logging.info("Phase Complete: Video Discovery.")


def run_collection():
    logging.info("Phase: Starting Comment Collection...")
    # Note: Each 'commentThreads.list' call costs 1 API quota unit
    collect_comments()
    logging.info("Phase Complete: Comment Collection.")


def run_pipeline(mode):
    logging.info(f"--- Starting Run: mode='{mode}' ---")

    try:
        logging.info("Initializing Database...")
        init_db()
        logging.info("Database Ready.")

        if mode in ("discovery", "full"):
            run_discovery()

        if mode in ("comments", "full"):
            run_collection()

        logging.info(f"--- Run Successful: mode='{mode}' ---")
        print(f"Pipeline ({mode}) executed successfully. Check collection_log.txt for details.")

    except Exception as e:
        logging.error(f"Critical error during run: {e}")
        print(f"Pipeline failed. Error logged: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arc Raiders YouTube Data Pipeline")
    parser.add_argument(
        "mode",
        choices=["discovery", "comments", "full"],
        help="Which phase to run: 'discovery' (find videos), 'comments' (collect comments), or 'full' (both phases)"
    )
    args = parser.parse_args()
    run_pipeline(args.mode)