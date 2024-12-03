import pytest

from s3_synchroniser.lib.files_manager.files_manager import get_local_files


@pytest.fixture
def test_directory(tmp_path):
    """Creates a temporary directory structure for testing."""
    # Create test directory structure
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Create some test files
    (test_dir / "file1.txt").touch()
    (test_dir / "file2.pdf").touch()
    (test_dir / "file3.PDF").touch()

    # Create a subdirectory with files
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file4.txt").touch()

    return test_dir


def test_get_local_files_all_files(test_directory):
    """Test getting all files without extension filtering."""
    files = get_local_files(str(test_directory))

    assert len(files) == 4
    assert "test_dir/file1.txt" in files
    assert "test_dir/file2.pdf" in files
    assert "test_dir/file3.PDF" in files
    assert "test_dir/subdir/file4.txt" in files


def test_get_local_files_with_extensions(test_directory):
    """Test getting files with specific extensions."""
    files = get_local_files(str(test_directory), extensions=[".txt"])

    assert len(files) == 2
    assert "test_dir/file1.txt" in files
    assert "test_dir/subdir/file4.txt" in files


def test_get_local_files_case_insensitive_extensions(test_directory):
    """Test that extension matching is case-insensitive."""
    files = get_local_files(str(test_directory), extensions=[".pdf"])

    assert len(files) == 2
    assert "test_dir/file2.pdf" in files
    assert "test_dir/file3.PDF" in files


def test_get_local_files_nonexistent_path():
    """Test that appropriate error is raised for non-existent paths."""
    with pytest.raises(FileNotFoundError):
        get_local_files("/nonexistent/path")


def test_get_local_files_file_path(test_directory):
    """Test that appropriate error is raised when path is a file."""
    test_file = test_directory / "file1.txt"

    with pytest.raises(NotADirectoryError):
        get_local_files(str(test_file))
