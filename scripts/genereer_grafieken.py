from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch


PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_DIR / "data" / "raw" / "Schoolverlaters dataset.csv"
FIGURES_DIR = PROJECT_DIR / "figuren"
RESULTS_DIR = PROJECT_DIR / "resultaten"

GROUP_COLUMN = "Vragenlijstnummer"
RATING_COLUMN = "Oordeel aansluiting"
GROUPS = ["vmbo", "havo of vwo"]
GROUP_LABELS = {"vmbo": "vmbo", "havo of vwo": "havo/vwo"}
RATINGS = ["slecht", "matig", "redelijk", "goed"]
RATING_LABELS = {
    "slecht": "Slecht",
    "matig": "Matig",
    "redelijk": "Redelijk",
    "goed": "Goed",
}
RATING_CODES = {rating: code for code, rating in enumerate(RATINGS, start=1)}
MISSING_MARKERS = {"", "*"}
COLORS = {
    "slecht": "#C8102E",  # Hogeschool Rotterdam red
    "matig": "#0072B2",
    "redelijk": "#E69F00",
    "goed": "#009E73",
}


def load_analysis_data():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Dataset niet gevonden: {SOURCE_FILE}")

    source = pd.read_csv(
        SOURCE_FILE,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )
    required_columns = {GROUP_COLUMN, RATING_COLUMN}
    missing_columns = required_columns.difference(source.columns)
    if missing_columns:
        raise ValueError(f"Verwachte kolommen ontbreken: {sorted(missing_columns)}")

    group_values = source[GROUP_COLUMN].str.strip().str.lower()
    rating_values = source[RATING_COLUMN].str.strip().str.lower()
    group_missing = group_values.isin(MISSING_MARKERS)
    rating_missing = rating_values.isin(MISSING_MARKERS)
    group_valid = group_values.isin(GROUPS)
    rating_valid = rating_values.isin(RATINGS)

    group_invalid = ~group_missing & ~group_valid
    rating_invalid = ~rating_missing & ~rating_valid
    valid_rows = group_valid & rating_valid

    analysis = pd.DataFrame(
        {
            "group": group_values[valid_rows],
            "rating": rating_values[valid_rows],
        }
    )
    diagnostics = {
        "n_rows": len(source),
        "n_valid": int(valid_rows.sum()),
        "n_excluded": int((~valid_rows).sum()),
        "group_missing": int(group_missing.sum()),
        "rating_missing": int(rating_missing.sum()),
        "group_invalid": int(group_invalid.sum()),
        "rating_invalid": int(rating_invalid.sum()),
        "group_values": group_values.value_counts(dropna=False).to_dict(),
        "rating_values": rating_values.value_counts(dropna=False).to_dict(),
    }

    if analysis.empty:
        raise ValueError("Geen geldige waarnemingen voor de gevraagde variabelen.")

    return analysis, diagnostics


def calculate_results(analysis):
    frequencies = pd.crosstab(analysis["group"], analysis["rating"])
    frequencies = frequencies.reindex(index=GROUPS, columns=RATINGS, fill_value=0)
    frequencies = frequencies.astype(int)

    group_sizes = frequencies.sum(axis=1)
    group_percentages = frequencies.div(group_sizes, axis=0) * 100
    total_frequencies = frequencies.sum(axis=0)
    total_n = int(total_frequencies.sum())
    total_percentages = total_frequencies / total_n * 100

    if not np.allclose(group_percentages.sum(axis=1).to_numpy(), 100):
        raise ValueError("Percentages binnen een onderwijsgroep tellen niet op tot 100%.")
    if not np.isclose(total_percentages.sum(), 100):
        raise ValueError("Totale percentages tellen niet op tot 100%.")

    group_stats = {}
    for group in GROUPS:
        rows = analysis.loc[analysis["group"] == group, "rating"]
        ordinal_ratings = rows.map(RATING_CODES)
        positive_percentage = rows.isin(["redelijk", "goed"]).mean() * 100
        group_stats[group] = {
            "n": int(len(rows)),
            "median": float(ordinal_ratings.median()),
            "positive_percentage": float(positive_percentage),
        }

    difference = (
        group_stats["havo of vwo"]["positive_percentage"]
        - group_stats["vmbo"]["positive_percentage"]
    )

    result_rows = []
    distributions = [(None, "Totaal", total_frequencies, total_percentages, total_n)]
    distributions.extend(
        (
            group,
            GROUP_LABELS[group],
            frequencies.loc[group],
            group_percentages.loc[group],
            int(group_sizes.loc[group]),
        )
        for group in GROUPS
    )
    for group_key, group_label, counts, percentages, n in distributions:
        for rating in RATINGS:
            stats = group_stats.get(group_key, {})
            result_rows.append(
                {
                    "onderwijsgroep": group_label,
                    "oordeel": RATING_LABELS[rating],
                    "frequentie": int(counts[rating]),
                    "percentage_binnen_groep": float(percentages[rating]),
                    "n_geldig_groep": n,
                    "mediaan_ordinaal": stats.get("median", np.nan),
                    "percentage_redelijk_goed": stats.get(
                        "positive_percentage", np.nan
                    ),
                    "verschil_pp_havo_vwo_min_vmbo": difference,
                }
            )

    return frequencies, group_percentages, total_frequencies, total_percentages, group_stats, difference, pd.DataFrame(result_rows)


def configure_axes(ax):
    ax.set_facecolor("white")
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#666666")
    ax.spines["bottom"].set_color("#666666")
    ax.tick_params(axis="both", labelsize=13, colors="#222222")


def make_total_chart(total_frequencies, total_percentages, total_n):
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")
    configure_axes(ax)

    positions = np.arange(len(RATINGS))
    values = [total_percentages[rating] for rating in RATINGS]
    bars = ax.bar(
        positions,
        values,
        width=0.66,
        color=[COLORS[rating] for rating in RATINGS],
        edgecolor="white",
        linewidth=1.2,
    )

    for bar, rating in zip(bars, RATINGS):
        percentage = total_percentages[rating]
        count = total_frequencies[rating]
        ax.annotate(
            f"{percentage:.1f}%  (n={count})",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            color="#222222",
        )

    ax.set_xticks(positions, [RATING_LABELS[rating] for rating in RATINGS])
    ax.set_ylabel("Percentage van geldige antwoorden", fontsize=15, labelpad=10)
    ax.set_ylim(0, 55)
    ax.set_yticks(np.arange(0, 51, 10), [f"{value}%" for value in range(0, 51, 10)])
    fig.suptitle("Aansluiting tussen opleidingen", fontsize=22, weight="bold", y=0.99)
    fig.text(
        0.5,
        0.875,
        f"Totale verdeling | geldige antwoorden n={total_n}",
        ha="center",
        va="bottom",
        fontsize=14,
        color="#444444",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.82))
    fig.savefig(FIGURES_DIR / "aansluiting_totaal.png", dpi=300, facecolor="white")
    plt.close(fig)


def make_group_chart(frequencies, group_percentages, group_stats):
    fig, ax = plt.subplots(figsize=(11, 6.5), facecolor="white")
    configure_axes(ax)

    positions = np.arange(len(GROUPS))
    bottoms = np.zeros(len(GROUPS))
    bar_width = 0.58

    for rating in RATINGS:
        values = np.array([group_percentages.loc[group, rating] for group in GROUPS])
        ax.bar(
            positions,
            values,
            width=bar_width,
            bottom=bottoms,
            color=COLORS[rating],
            edgecolor="white",
            linewidth=1.2,
        )

        for index, group in enumerate(GROUPS):
            percentage = values[index]
            if percentage < 7:
                continue
            center = bottoms[index] + percentage / 2
            label_color = "white" if rating in {"slecht", "matig"} else "#202020"
            ax.text(
                positions[index],
                center,
                f"{RATING_LABELS[rating]}\n{percentage:.1f}%",
                ha="center",
                va="center",
                fontsize=11,
                color=label_color,
                weight="bold",
            )
        bottoms += values

    # Keep the smallest category readable without squeezing labels into thin segments.
    for index, group in enumerate(GROUPS):
        rating = "slecht"
        percentage = group_percentages.loc[group, rating]
        if percentage >= 7:
            continue
        center = percentage / 2
        direction = -1 if index == 0 else 1
        ax.annotate(
            f"Slecht {percentage:.1f}%",
            xy=(positions[index] + direction * bar_width / 2, center),
            xytext=(positions[index] + direction * 0.54, center),
            ha="right" if direction < 0 else "left",
            va="center",
            fontsize=10,
            color="#222222",
            arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.9},
        )

    ax.set_xlim(-0.85, 1.85)
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 20), [f"{value}%" for value in range(0, 101, 20)])
    ax.set_xticks(
        positions,
        [
            f"{GROUP_LABELS[group]}\nn={group_stats[group]['n']:,}".replace(",", ".")
            for group in GROUPS
        ],
    )
    ax.set_ylabel("Percentage binnen onderwijsgroep", fontsize=15, labelpad=10)
    fig.suptitle(
        "Oordeel over aansluiting per onderwijsgroep",
        fontsize=21,
        weight="bold",
        y=0.99,
    )
    fig.text(
        0.5,
        0.875,
        "100%-gestapeld | percentages binnen elke groep",
        ha="center",
        va="bottom",
        fontsize=14,
        color="#444444",
    )

    legend_handles = [
        Patch(facecolor=COLORS[rating], edgecolor="none", label=RATING_LABELS[rating])
        for rating in RATINGS
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=4,
        frameon=False,
        fontsize=13,
        columnspacing=1.8,
    )
    fig.subplots_adjust(left=0.12, right=0.96, top=0.80, bottom=0.23)
    fig.savefig(
        FIGURES_DIR / "aansluiting_onderwijsniveau.png",
        dpi=300,
        facecolor="white",
        bbox_inches="tight",
    )
    plt.close(fig)


def write_results(analysis, diagnostics, total_frequencies, total_percentages, group_stats, difference, results_table):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_table.to_csv(
        RESULTS_DIR / "aansluiting_frequenties_percentages.csv",
        sep=";",
        decimal=",",
        index=False,
        encoding="utf-8-sig",
        float_format="%.4f",
    )

    report = [
        "Schoolverlaters: oordeel over aansluiting",
        "Bron: data/raw/Schoolverlaters dataset.csv (ruwe bron ongewijzigd)",
        "Kolommen: Vragenlijstnummer en Oordeel aansluiting",
        "",
        f"Totaal aantal rijen: {diagnostics['n_rows']}",
        f"Geldige waarnemingen: {diagnostics['n_valid']}",
        f"Uitgesloten rijen (minstens een ongeldig/ontbrekend analyseveld): {diagnostics['n_excluded']}",
        f"Ontbrekend onderwijsniveau ('*' of leeg): {diagnostics['group_missing']}",
        f"Ontbrekend oordeel ('*' of leeg): {diagnostics['rating_missing']}",
        f"Onbekende onderwijsniveau-labels: {diagnostics['group_invalid']}",
        f"Onbekende oordeel-labels: {diagnostics['rating_invalid']}",
        "Opmerking: de bron bevat tekstlabels; '*' is als ontbrekend behandeld.",
        "Onderwijsniveau-labels vmbo en havo of vwo volgen de betekenis uit de vraag.",
        "Oordelen zijn geordend als slecht=1, matig=2, redelijk=3, goed=4.",
        "",
        "Totale verdeling:",
    ]
    total_n = int(total_frequencies.sum())
    for rating in RATINGS:
        report.append(
            f"  {RATING_LABELS[rating]}: {int(total_frequencies[rating])} "
            f"({total_percentages[rating]:.2f}%)"
        )

    report.extend(["", "Uitkomsten per onderwijsgroep:"])
    for group in GROUPS:
        stats = group_stats[group]
        report.append(
            f"  {GROUP_LABELS[group]} (n={stats['n']}): mediaan="
            f"{stats['median']:.1f}; redelijk/goed="
            f"{stats['positive_percentage']:.2f}%"
        )
        for rating in RATINGS:
            count = int(((analysis["group"] == group) & (analysis["rating"] == rating)).sum())
            percentage = count / stats["n"] * 100
            report.append(f"    {RATING_LABELS[rating]}: {count} ({percentage:.2f}%)")

    report.extend(
        [
            "",
            "Verschil redelijk/goed (havo/vwo minus vmbo): "
            f"{difference:+.2f} procentpunt",
            "Percentages zijn berekend op geldige antwoorden; groepspercentages "
            "tellen op tot 100%.",
            f"Totaal n voor de verdeling: {total_n}",
        ]
    )
    (RESULTS_DIR / "aansluiting_samenvatting.txt").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    analysis, diagnostics = load_analysis_data()
    (
        frequencies,
        group_percentages,
        total_frequencies,
        total_percentages,
        group_stats,
        difference,
        results_table,
    ) = calculate_results(analysis)

    make_total_chart(total_frequencies, total_percentages, diagnostics["n_valid"])
    make_group_chart(frequencies, group_percentages, group_stats)
    write_results(
        analysis,
        diagnostics,
        total_frequencies,
        total_percentages,
        group_stats,
        difference,
        results_table,
    )

    print(f"Grafieken opgeslagen in: {FIGURES_DIR}")
    print(f"Resultaten opgeslagen in: {RESULTS_DIR}")
    print(f"Geldige waarnemingen: {diagnostics['n_valid']} / {diagnostics['n_rows']}")
    print(f"Uitgesloten rijen: {diagnostics['n_excluded']}")
    print(f"Verschil redelijk/goed (havo/vwo - vmbo): {difference:+.2f} procentpunt")


if __name__ == "__main__":
    main()