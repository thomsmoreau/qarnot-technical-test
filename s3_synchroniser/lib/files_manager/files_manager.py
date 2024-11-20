from pathlib import Path
from typing import List


def get_local_files(path: str) -> List[str]:
    """Returns the list of all files path in a given folder

    Args:
        path (str): Path to explore

    Returns:
        List[str]: All path of files in folder
    """
    directory = Path(path).resolve()
    file_list = []

    base_directory = directory.parent

    # Iterate through all files recursively
    for file in directory.rglob("*"):
        # Skip directories, only consider files
        if file.is_file():
            # Compute the relative path including 'data_to_sync'
            relative_path = file.relative_to(base_directory).as_posix()
            file_list.append(relative_path)

    return file_list
