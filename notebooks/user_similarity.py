import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import numpy as np
    import pandas as pd

    from julebrus.app import read_user_files

    return Path, mo, np, pd, read_user_files


@app.cell
def _(mo):
    mo.md(r"""
    # Hvem har lik julebrussmak?
    """)
    return


@app.cell
def _(Path, mo, read_user_files):
    data_dir = Path(__file__).resolve().parent.parent / "data" / "2025"

    user_files = sorted((data_dir / "user_data").glob("*.tsv"))
    mo.stop(len(user_files) < 2, mo.md("Trenger minst to rangeringer for å sammenligne."))
    ranks = read_user_files(user_files)
    ranks
    return (ranks,)


@app.cell
def _(mo, ranks):
    def heat(value: float) -> str:
        if value >= 0:
            r, g, b = (int(255 - (255 - c) * value) for c in (63, 107, 58))
        else:
            r, g, b = (int(255 - (255 - c) * -value) for c in (168, 52, 42))
        text = "white" if abs(value) > 0.6 else "black"
        return f"background-color: rgb({r},{g},{b}); color: {text}"


    correlation = ranks.corr(method="spearman")

    equal_columns = [
        {"selector": "", "props": "table-layout: fixed; border-collapse: collapse"},
        {"selector": "th.col_heading, td", "props": "width: 6em; text-align: center"},
        {
            "selector": "th.col_heading",
            "props": "overflow: hidden; text-overflow: ellipsis",
        },
        {
            "selector": "th.row_heading",
            "props": "text-align: right; padding-right: 0.5em",
        },
    ]
    heatmap = correlation.style.map(heat).format("{:.2f}").set_table_styles(equal_columns)

    mo.vstack(
        [
            mo.md("## Korrelasjonsmatrise"),
            mo.md(
                "Tabellen viser Spearman korrelasjonskoeffsient mellom alle par av brussmakere"
            ),
            mo.md("1 betyr at man har rangert brusene helt likt."),
            mo.md("-1 betyr at man har rangert brusene helt motsatt (best=verst osv)."),
            mo.md(
                "0 betyr at det ikke er noen sammenheng mellom hvordan de rangerte brusen"
            ),
            mo.Html(heatmap.to_html()),
        ]
    )
    return (correlation,)


@app.cell
def _(correlation, mo, pd):
    pair_index = [
        (a, b)
        for i, a in enumerate(correlation.columns)
        for b in correlation.columns[i + 1 :]
    ]
    pairs = (
        pd.DataFrame(
            [(a, b, correlation.loc[a, b]) for a, b in pair_index],
            columns=["bruker_a", "bruker_b", "spearman"],
        )
        .sort_values("spearman", ascending=False)
        .reset_index(drop=True)
    )
    mo.vstack(
        [
            mo.md("## Mest lik rangering"),
            mo.ui.table(pairs.head(7).round(2), selection=None),
            mo.md("## Minst lik rangering"),
            mo.ui.table(pairs.tail(7).iloc[::-1].round(2), selection=None),
        ]
    )
    return


@app.cell
def _(correlation, mo, pd):
    others = correlation.mask(
        pd.DataFrame(
            [[a == b for b in correlation.columns] for a in correlation.index],
            index=correlation.index,
            columns=correlation.columns,
        )
    )
    per_user = pd.DataFrame(
        {
            "snitt_mot_andre": others.mean(),
        }
    ).sort_values("snitt_mot_andre", ascending=False)

    mo.vstack(
        [
            mo.md('## Mest lik "resten"'),
            mo.md("Snitt-korrelasjon med resten av brussmakerne"),
            mo.ui.table(per_user.round(2).T, selection=None),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Dendrogram av folks liknende smak
    """)
    return


@app.cell
def _(correlation, np):
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter, MultipleLocator
    from scipy.cluster.hierarchy import dendrogram, linkage
    from scipy.spatial.distance import squareform

    distance = (1 - correlation).to_numpy()
    np.fill_diagonal(distance, 0)
    linkage_tree = linkage(squareform(distance, checks=False), method="average")

    fig, ax = plt.subplots(figsize=(10, 0.35 * len(correlation) + 1))
    dendrogram(
        linkage_tree,
        labels=correlation.index.to_list(),
        orientation="left",
        color_threshold=0,
        above_threshold_color="#4b423a",
        ax=ax,
    )
    ax.set_xlabel("Spearman")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{round(1 - x, 1) + 0.0:.1f}"))
    ax.xaxis.set_major_locator(MultipleLocator(0.1))
    ax.grid(axis="x", color="#c9bca6", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout()
    fig
    return


if __name__ == "__main__":
    app.run()
