import pandas as pd
import pytest


@pytest.fixture
def user_files(tmp_path):
    """Create temporary user TSV files for testing"""
    user1_df = pd.DataFrame({"kodenavn": ["A", "B", "C"]})
    user1_file = tmp_path / "user1.tsv"
    user1_df.to_csv(user1_file, sep="\t", index=False)

    user2_df = pd.DataFrame({"kodenavn": ["C", "A", "B"]})
    user2_file = tmp_path / "user2.tsv"
    user2_df.to_csv(user2_file, sep="\t", index=False)

    return [user1_file, user2_file]
