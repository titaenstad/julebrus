from pathlib import Path
import pandas as pd
from flask import Flask, render_template, request, jsonify

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
TABLE_DATA_DIR = DATA_DIR / "table_data"
USER_DATA_DIR = DATA_DIR / "user_data"

flask_app = Flask(__name__)


def load_kodenavn() -> list[str]:
    """Load kodenavn from the julebrus.tsv file using pandas."""
    tsv_file = TABLE_DATA_DIR / "julebrus.tsv"
    df = pd.read_csv(tsv_file, sep="\t")
    return df["kodenavn"].tolist()


def load_brusnavn_mapping() -> dict[str, str]:
    """Load mapping of kodenavn to brusnavn."""
    tsv_file = TABLE_DATA_DIR / "julebrus.tsv"
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


def read_user_files_and_rank() -> tuple[list[dict], int]:
    """Calculate overall rankings based on all user files using pandas."""

    user_files = list(USER_DATA_DIR.glob("*.tsv"))
    number_of_users = len(user_files)
    user_df = read_user_files(user_files=user_files)
    summary = calculate_ranks(user_df)

    brusnavn_mapping = load_brusnavn_mapping()
    summary["brusnavn"] = summary["kodenavn"].map(brusnavn_mapping)
    return summary.to_dict("records"), number_of_users


@flask_app.route("/")
def index() -> str:
    """Render the main page."""
    kodenavn = load_kodenavn()
    return render_template("index.html", kodenavn=kodenavn)


@flask_app.route("/save", methods=["POST"])
def save_order():
    """Save the user's ordering to a TSV file using pandas."""
    data = request.json
    navn = data.get("navn", "").strip()
    order = data.get("order", [])

    if not navn:
        return jsonify({"success": False, "error": "Name is required"}), 400

    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = USER_DATA_DIR / f"{navn}.tsv"

    file_existed = output_file.exists()

    df = pd.DataFrame({"kodenavn": order})
    df.to_csv(output_file, sep="\t", index=False)

    response = {"success": True, "file": str(output_file)}
    if file_existed:
        response["warning"] = "Eksisterende rangering ble overskrevet"

    return jsonify(response)


@flask_app.route("/results")
def results() -> str:
    """Display the overall rankings based on all user submissions."""
    rankings, num_users = read_user_files_and_rank()
    return render_template("results.html", rankings=rankings, num_users=num_users)


def app() -> None:
    """Run the Flask app."""
    print("Starting Julebrus app...")
    print(f"Data directory: {DATA_DIR}")
    flask_app.run(debug=True, host="0.0.0.0", port=5000)
