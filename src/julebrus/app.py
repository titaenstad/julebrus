import argparse
import json
import string
from pathlib import Path

import pandas as pd
from flask import Flask, abort, jsonify, render_template, request, send_from_directory


def load_brusnavn(data_dir: Path) -> dict[str, str]:
    """Load the mapping of short brusnavn (picture file stem) to full name."""
    json_file = data_dir / "brusnavn.json"
    brusnavn = json.loads(json_file.read_text(encoding="utf-8"))
    return {short: full.strip() for short, full in brusnavn.items()}


def check_pictures(pictures_dir: Path, brusnavn: dict[str, str]) -> None:
    missing = [short for short in brusnavn if not (pictures_dir / f"{short}.jpg").is_file()]
    if missing:
        raise FileNotFoundError(
            f"Missing pictures in {pictures_dir}: {', '.join(f'{m}.jpg' for m in missing)}"
        )


def create_julebrus_table(brusnavn: list[str]) -> pd.DataFrame:
    """Assign a kodenavn (A, B, C, ...) to each brusnavn, in sorted order."""
    if len(brusnavn) > len(string.ascii_uppercase):
        raise ValueError(
            f"Got {len(brusnavn)} brus, but at most {len(string.ascii_uppercase)} are supported"
        )
    return pd.DataFrame(
        {
            "brusnavn": sorted(brusnavn),
            "kodenavn": list(string.ascii_uppercase[: len(brusnavn)]),
        }
    )


def load_or_create_julebrus_table(
    data_dir: Path, brusnavn: dict[str, str]
) -> pd.DataFrame:
    """Read julebrus.tsv, or create it from brusnavn if it does not exist yet.

    An existing table is never regenerated, since saved user rankings refer to its kodenavn.
    """
    tsv_file = data_dir / "julebrus.tsv"
    if tsv_file.exists():
        df = pd.read_csv(tsv_file, sep="\t")
        if set(df["brusnavn"]) != set(brusnavn):
            raise ValueError(
                f"{tsv_file} does not match brusnavn.json. "
                f"Only in julebrus.tsv: {sorted(set(df['brusnavn']) - set(brusnavn))}. "
                f"Only in brusnavn.json: {sorted(set(brusnavn) - set(df['brusnavn']))}."
            )
        return df

    df = create_julebrus_table(list(brusnavn))
    df.to_csv(tsv_file, sep="\t", index=False)
    print(f"Created {tsv_file} with {len(df)} brus")
    return df


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
    julebrus_table: pd.DataFrame, user_data_dir: Path
) -> tuple[list[dict], int]:

    user_files = list(user_data_dir.glob("*.tsv"))
    number_of_users = len(user_files)
    user_df = read_user_files(user_files=user_files)
    summary = calculate_ranks(user_df)

    brusnavn_mapping = dict(zip(julebrus_table["kodenavn"], julebrus_table["brusnavn"]))
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


def create_app(data_dir: Path) -> Flask:
    user_data_dir = data_dir / "user_data"
    pictures_dir = (data_dir / "bilder").resolve()

    brusnavn = load_brusnavn(data_dir)
    check_pictures(pictures_dir, brusnavn)
    julebrus_table = load_or_create_julebrus_table(data_dir, brusnavn)
    kodenavn = julebrus_table["kodenavn"].tolist()

    flask_app = Flask(__name__)

    @flask_app.route("/")
    def index() -> str:
        """Render the main page."""
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
        rankings, num_users = read_user_files_and_rank(julebrus_table, user_data_dir)
        for item in rankings:
            item["symbol"] = kodenavn.index(item["kodenavn"]) + 1
            item["picture"] = f"{item['brusnavn']}.jpg"
            item["fullt_navn"] = brusnavn[item["brusnavn"]]
        return render_template("results.html", rankings=rankings, num_users=num_users)

    @flask_app.route("/bilder/<path:filename>")
    def picture(filename: str):
        if not pictures_dir.is_dir():
            abort(404)
        return send_from_directory(pictures_dir, filename)

    return flask_app


def app() -> None:
    default_data_dir = Path(__file__).resolve().parent.parent.parent / "data"

    parser = argparse.ArgumentParser(description="Run the Julebrus app.")
    parser.add_argument(
        "data_dir",
        nargs="?",
        type=Path,
        default=default_data_dir,
        help=(
            "Directory containing brusnavn.json and bilder/; julebrus.tsv and user_data/ "
            f"are created as needed (default: {default_data_dir})"
        ),
    )
    args = parser.parse_args()

    data_dir = args.data_dir.resolve()

    print("Starting Julebrus app...")
    print(f"Data directory: {data_dir}")
    flask_app = create_app(data_dir)
    flask_app.run(debug=True, host="0.0.0.0", port=5000)
