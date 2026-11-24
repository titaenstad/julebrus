import pandas as pd

from src.julebrus.app import calculate_ranks


def test_single_user():
    """Test rank calculation with a single user"""
    combined_df = pd.DataFrame(
        {"user1": [0, 1, 2], "kodenavn": ["A", "B", "C"]},
    )
    combined_df = combined_df.set_index("kodenavn")
    rank_df = calculate_ranks(combined_df)

    expected_rank_order = [1, 2, 3]
    expected_kodenavn_order = ["A", "B", "C"]

    assert expected_rank_order == rank_df["rank"].to_list()
    assert expected_kodenavn_order == rank_df.kodenavn.to_list()


def test_two_users_same_rank():
    """Test rank calculation with two users with the same ranking"""
    combined_df = pd.DataFrame(
        {"user1": [0, 1, 2], "user2": [0, 1, 2], "kodenavn": ["A", "B", "C"]},
    )
    combined_df = combined_df.set_index("kodenavn")
    rank_df = calculate_ranks(combined_df)

    expected_rank_order = [1, 2, 3]
    expected_kodenavn_order = ["A", "B", "C"]

    assert expected_rank_order == rank_df["rank"].to_list()
    assert expected_kodenavn_order == rank_df.kodenavn.to_list()


def test_two_users_opposite_ranks_tie():
    """Test rank calculation with two users with opposite rankings"""
    combined_df = pd.DataFrame(
        {"user1": [0, 1, 2], "user2": [2, 1, 0], "kodenavn": ["A", "B", "C"]},
    )
    combined_df = combined_df.set_index("kodenavn")
    rank_df = calculate_ranks(combined_df)

    expected_rank_order = [1, 1, 1]
    expected_kodenavn_order = ["A", "B", "C"]

    assert expected_rank_order == rank_df["rank"].to_list()
    assert expected_kodenavn_order == rank_df.kodenavn.to_list()


def test_three_users_tied_ranks():
    """Test rank calculation with three users resulting in tied ranks"""
    combined_df = pd.DataFrame(
        {
            "user1": [0, 2, 1],
            "user2": [1, 0, 2],
            "user3": [2, 1, 0],
            "kodenavn": ["A", "B", "C"],
        },
    )
    combined_df = combined_df.set_index("kodenavn")
    rank_df = calculate_ranks(combined_df)

    expected_rank_order = [1, 1, 1]
    expected_kodenavn_order = ["A", "B", "C"]

    assert expected_rank_order == rank_df["rank"].to_list()
    assert expected_kodenavn_order == rank_df.kodenavn.to_list()


def test_four_users_C_best():
    """Test rank calculation with four users where C is the clear winner"""
    combined_df = pd.DataFrame(
        {
            "user1": [2, 1, 0],
            "user2": [2, 1, 0],
            "user3": [1, 2, 0],
            "user4": [2, 1, 0],
            "kodenavn": ["A", "B", "C"],
        },
    )
    combined_df = combined_df.set_index("kodenavn")
    rank_df = calculate_ranks(combined_df)

    expected_rank_order = [1, 2, 3]
    expected_kodenavn_order = ["C", "B", "A"]

    assert expected_rank_order == rank_df["rank"].to_list()
    assert expected_kodenavn_order == rank_df.kodenavn.to_list()


def test_rank_with_tie_for_second():
    """Test rank calculation resulting in [1, 2, 2]"""
    combined_df = pd.DataFrame(
        {
            "user1": [
                1,
                0,
                2,
            ],
            "user2": [
                2,
                0,
                1,
            ],
            "kodenavn": ["A", "B", "C"],
        },
    )
    combined_df = combined_df.set_index("kodenavn")
    rank_df = calculate_ranks(combined_df)

    expected_rank_order = [1, 2, 2]
    expected_kodenavn_order = [
        "B",
        "A",
        "C",
    ]

    assert expected_rank_order == rank_df["rank"].to_list()
    assert expected_kodenavn_order == rank_df.kodenavn.to_list()
