import argparse
import logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SzuruStash command-line interface.")
    parser.add_argument("--version", action="version", version="SzuruStash 0.1.0")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info("Welcome to SzuruStash!")