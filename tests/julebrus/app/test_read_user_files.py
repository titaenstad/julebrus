import pandas as pd
from src.julebrus.app import read_user_files


def test_read_user_files(user_files):
    """Test reading multiple user TSV files into a combined DataFrame"""
    result_df = read_user_files(user_files)

    expected_df = pd.DataFrame(
        {"user1": [0, 1, 2], "user2": [1, 2, 0]}, index=["A", "B", "C"]
    )
    expected_df.index.name = "kodenavn"

    pd.testing.assert_frame_equal(result_df, expected_df)


def test_read_only_user_1(user_files):
    result_df = read_user_files([user_files[0]])

    expected_df = pd.DataFrame({"user1": [0, 1, 2]}, index=["A", "B", "C"])
    expected_df.index.name = "kodenavn"

    pd.testing.assert_frame_equal(result_df, expected_df)


def test_read_only_user_2(user_files):
    """User2 has C first, then A, then B"""
    result_df = read_user_files([user_files[1]])

    expected_df = pd.DataFrame(
        {"user2": [0, 1, 2]},
        index=[
            "C",
            "A",
            "B",
        ],
    )
    expected_df.index.name = "kodenavn"

    pd.testing.assert_frame_equal(result_df, expected_df)


def test_empty_user_file_list():
    result_df = read_user_files([])
    assert result_df.empty
