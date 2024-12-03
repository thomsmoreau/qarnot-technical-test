from pathlib import Path
from typing import List


def get_local_files(path: str, extensions: List[str] | None = None) -> List[str]:
    """Returns a list of all file paths in a given folder.

    Args:
        path (str): Path to explore
        extensions (List[str] | None, optional): List of file extensions to include (e.g. ['.txt', '.pdf']).
            If None, includes all files. Defaults to None.

    Returns:
        List[str]: Relative paths of all matching files in folder

    Raises:
        FileNotFoundError: If the provided path doesn't exist
        NotADirectoryError: If the provided path is not a directory
    """

    directory = Path(path).resolve()

    if not directory.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    base_directory = directory.parent

    return [
        file.relative_to(base_directory).as_posix()
        for file in directory.rglob("*")
        if file.is_file() and (extensions is None or file.suffix.lower() in extensions)
    ]
