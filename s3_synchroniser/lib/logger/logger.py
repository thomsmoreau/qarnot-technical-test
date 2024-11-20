import logging


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    return logging.getLogger(name)
