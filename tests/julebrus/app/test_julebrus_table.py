import pandas as pd
import pytest

from julebrus.app import load_or_create_julebrus_table

BRUSNAVN = {"unil": "Julebrus", "aass": "Aass julebrus", "roma_brun": "Romas brune julebrus"}


def test_creates_table_with_sorted_brusnavn(tmp_path):
    df = load_or_create_julebrus_table(tmp_path, BRUSNAVN)

    assert df["brusnavn"].tolist() == ["aass", "roma_brun", "unil"]
    assert df["kodenavn"].tolist() == ["A", "B", "C"]
    assert (tmp_path / "julebrus.tsv").is_file()


def test_reuses_existing_table(tmp_path):
    existing = pd.DataFrame({"brusnavn": ["unil", "aass", "roma_brun"], "kodenavn": ["A", "B", "C"]})
    existing.to_csv(tmp_path / "julebrus.tsv", sep="\t", index=False)

    df = load_or_create_julebrus_table(tmp_path, BRUSNAVN)

    assert df["brusnavn"].tolist() == ["unil", "aass", "roma_brun"]


def test_raises_when_existing_table_does_not_match(tmp_path):
    existing = pd.DataFrame({"brusnavn": ["unil", "aass"], "kodenavn": ["A", "B"]})
    existing.to_csv(tmp_path / "julebrus.tsv", sep="\t", index=False)

    with pytest.raises(ValueError, match="roma_brun"):
        load_or_create_julebrus_table(tmp_path, BRUSNAVN)
