import argparse
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request


def load_kodenavn(table_data_dir: Path) -> list[str]:
    """Load kodenavn from the julebrus.tsv file using pandas."""
    tsv_file = table_data_dir / "julebrus.tsv"
    df = pd.read_csv(tsv_file, sep="\t")
    return df["kodenavn"].tolist()


def load_brusnavn_mapping(table_data_dir: Path) -> dict[str, str]:
    """Load mapping of kodenavn to brusnavn."""
    tsv_file = table_data_dir / "julebrus.tsv"
    df = pd.read_csv(tsv_file, sep="\t")
    return dict(zip(df["kodenavn"], df["brusnavn"]))


def read_user_files(user_files: list[str]) -> pd.DataFrame:
    user_rankings = {}
    for user_file in user_files:
        df = pd.read_csv(user_file, sep="\t")
        user_rankings[user_file.stem] = pd.Series(df.index.values, index=df["kodenavn"])

    return pd.DataFrame(user_rankings)


def calculate_ranks(combined_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate ranks from combined user rankings DataFrame.

    Args:
        combined_df: DataFrame with kodenavn as index and user columns containing positions.
        Example:
            user1  user2  user3
        A      0      1      0
        B      1      0      2
        C      2      2      1

    Returns:
        DataFrame with columns: kodenavn, rank
        sorted by rank (ascending)
    """
    # Higher position = lower ranked. Minimal sum of positions means the item was highly ranked
    position_sums = combined_df.sum(axis=1)
    ranks = position_sums.rank(method="min").astype(int)

    return pd.DataFrame(
        {"kodenavn": combined_df.index, "rank": ranks.to_list()}
    ).sort_values("rank")


def read_user_files_and_rank(
    table_data_dir: Path, user_data_dir: Path
) -> tuple[list[dict], int]:

    user_files = list(user_data_dir.glob("*.tsv"))
    number_of_users = len(user_files)
    user_df = read_user_files(user_files=user_files)
    summary = calculate_ranks(user_df)

    brusnavn_mapping = load_brusnavn_mapping(table_data_dir)
    summary["brusnavn"] = summary["kodenavn"].map(brusnavn_mapping)
    return summary.to_dict("records"), number_of_users


def save_user_order(
    user_data_dir: Path, navn: str, order: list[str]
) -> tuple[Path, bool]:
    user_data_dir.mkdir(parents=True, exist_ok=True)
    output_file = user_data_dir / f"{navn}.tsv"

    file_existed = output_file.exists()

    df = pd.DataFrame({"kodenavn": order})
    df.to_csv(output_file, sep="\t", index=False)

    return output_file, file_existed


def create_app(table_data_dir: Path, user_data_dir: Path) -> Flask:
    flask_app = Flask(__name__)

    @flask_app.route("/")
    def index() -> str:
        """Render the main page."""
        kodenavn = load_kodenavn(table_data_dir)
        return render_template("index.html", kodenavn=kodenavn)

    @flask_app.route("/save", methods=["POST"])
    def save_order():
        """Save the user's ordering to a TSV file using pandas."""
        data = request.json
        navn = data.get("navn", "").strip()
        order = data.get("order", [])

        if not navn:
            return jsonify({"success": False, "error": "Name is required"}), 400

        output_file, file_existed = save_user_order(user_data_dir, navn, order)

        response = {"success": True, "file": str(output_file)}
        if file_existed:
            response["warning"] = "Eksisterende rangering ble overskrevet"

        return jsonify(response)

    @flask_app.route("/results")
    def results() -> str:
        rankings, num_users = read_user_files_and_rank(table_data_dir, user_data_dir)
        return render_template("results.html", rankings=rankings, num_users=num_users)

    return flask_app


def app() -> None:
    default_data_dir = Path(__file__).resolve().parent.parent.parent / "data"

    parser = argparse.ArgumentParser(description="Run the Julebrus app.")
    parser.add_argument(
        "data_dir",
        nargs="?",
        type=Path,
        default=default_data_dir,
        help=f"Directory containing table_data/ and user_data/ (default: {default_data_dir})",
    )
    args = parser.parse_args()

    data_dir = args.data_dir.resolve()
    table_data_dir = data_dir / "table_data"
    user_data_dir = data_dir / "user_data"

    print("Starting Julebrus app...")
    print(f"Data directory: {data_dir}")
    flask_app = create_app(table_data_dir, user_data_dir)
    flask_app.run(debug=True, host="0.0.0.0", port=5000)
