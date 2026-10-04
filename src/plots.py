import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def normalize_col(name):
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")

def find_column(df, candidates):
    norm_map = {normalize_col(col): col for col in df.columns}
    for cand in candidates:
        key = normalize_col(cand)
        if key in norm_map:
            return norm_map[key]
    return None

def safe_plot_path(output_dir, name):
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, name)

def uses_kde(series):
    values = series.dropna()
    return not values.empty and not np.all(np.isclose(values, np.round(values)))

def plot_correlation_matrix(df, output_path):
    plt.figure(figsize=(14, 12))  # Verander de figuurgrootte indien nodig
    
    # One-hot encoding voor categorische variabelen
    df_encoded = pd.get_dummies(df, drop_first=True)
    
    # Bereken de correlatie
    corr = df_encoded.corr()
    
    # Maak de heatmap
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', square=True, 
                cbar_kws={"shrink": .8}, annot_kws={"size": 8})  # Verklein de annotatietekst
    
    plt.title("Correlatiematrix", fontsize=16)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_income_distribution(df, output_path):
    income_col = find_column(df, [
        "bruto maandinkomen in euro",
        "maandinkomen",
        "inkomen",
        "income",
        "salary"
    ])
    
    if income_col is None:
        raise ValueError(f"Kan inkomen niet vinden in kolommen: {list(df.columns)}")

    plt.figure(figsize=(10, 6))
    income = df[income_col].dropna()
    sns.histplot(income, bins=30, kde=uses_kde(income))
    plt.title(f"Verdeling van {income_col}")
    plt.xlabel(income_col)
    plt.ylabel("Aantal")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_age_distribution(df, output_path):
    age_col = find_column(df, ["leeftijd", "age", "ouderdom"])
    
    if age_col is None:
        raise ValueError(f"Kan leeftijd niet vinden in kolommen: {list(df.columns)}")

    plt.figure(figsize=(10, 6))
    age = df[age_col].dropna()
    sns.histplot(age, bins=30, kde=uses_kde(age))
    plt.title(f"Verdeling van {age_col}")
    plt.xlabel(age_col)
    plt.ylabel("Aantal")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_income_vs_age(df, output_path):
    age_col = find_column(df, ["leeftijd", "age", "ouderdom"])
    income_col = find_column(df, [
        "bruto maandinkomen in euro",
        "maandinkomen",
        "inkomen",
        "income",
        "salary"
    ])

    if age_col is None or income_col is None:
        raise ValueError(f"Kan leeftijd/inkomen niet vinden in kolommen: {list(df.columns)}")

    df_plot = df[[age_col, income_col]].dropna()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_plot, x=age_col, y=income_col, alpha=0.7)
    plt.xlabel(age_col)
    plt.ylabel(income_col)
    plt.title(f"{income_col} vs {age_col}")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_working_hours_vs_income(df, output_path):
    hours_col = find_column(df, [
        "aantal arbeidsuren per week",
        "arbeidsuren",
        "werkuren",
        "hours_per_week",
        "weekly_hours"
    ])
    income_col = find_column(df, [
        "bruto maandinkomen in euro",
        "maandinkomen",
        "inkomen",
        "income",
        "salary"
    ])

    if hours_col is None or income_col is None:
        raise ValueError(f"Kan arbeidsuren/inkomen niet vinden in kolommen: {list(df.columns)}")

    df_plot = df[[hours_col, income_col]].dropna()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_plot, x=hours_col, y=income_col, alpha=0.7)
    plt.xlabel(hours_col)
    plt.ylabel(income_col)
    plt.title(f"{income_col} vs {hours_col}")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_histogram_numeric(df, output_dir):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols[:10]:
        plt.figure(figsize=(8, 5))
        values = df[col].dropna()
        sns.histplot(values, bins=20, kde=uses_kde(values), edgecolor="black")
        plt.xlabel(col)
        plt.ylabel("Aantal")
        plt.title(f"Histogram: {col}")
        plt.tight_layout()
        plt.savefig(safe_plot_path(output_dir, f"hist_{normalize_col(col)}.png"), dpi=200)
        plt.close()

def plot_bar_categories(df, output_dir, max_unique=12):
    for col in df.columns:
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            counts = df[col].dropna().astype(str).value_counts().head(max_unique)
            if len(counts) == 0:
                continue
            plt.figure(figsize=(10, 5))
            sns.barplot(x=counts.index, y=counts.values)
            plt.title(f"Verdeling: {col}")
            plt.ylabel("Aantal")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(safe_plot_path(output_dir, f"bar_{normalize_col(col)}.png"), dpi=200)
            plt.close()

def plot_boxplots_by_category(df, output_dir):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [
        c for c in df.columns
        if df[c].dtype == object or pd.api.types.is_string_dtype(df[c])
    ]

    for num in numeric_cols[:5]:
        for cat in cat_cols[:3]:
            plt.figure(figsize=(10, 5))
            sns.boxplot(data=df, x=cat, y=num, showfliers=False)  # Uitschieters niet tonen
            plt.title(f"{num} per {cat}")
            plt.xlabel(cat)
            plt.ylabel(num)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(safe_plot_path(output_dir, f"box_{normalize_col(num)}_by_{normalize_col(cat)}.png"), dpi=200)
            plt.close()

def generate_all_plots(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Correlatiematrix
    try:
        plot_correlation_matrix(df, safe_plot_path(output_dir, "correlatiematrix.png"))
    except Exception as e:
        print(f"Skip correlatiematrix: {e}")

    # 2. Verdelen van inkomen
    try:
        plot_income_distribution(df, safe_plot_path(output_dir, "inkomen_verdeling.png"))
    except Exception as e:
        print(f"Skip inkomen_verdeling: {e}")

    # 3. Verdelen van leeftijd
    try:
        plot_age_distribution(df, safe_plot_path(output_dir, "leeftijd_verdeling.png"))
    except Exception as e:
        print(f"Skip leeftijd_verdeling: {e}")

    # 4. bestaande plots
    try:
        plot_income_vs_age(df, safe_plot_path(output_dir, "inkomen_leeftijd.png"))
    except Exception as e:
        print(f"Skip inkomen_leeftijd: {e}")

    try:
        plot_working_hours_vs_income(df, safe_plot_path(output_dir, "arbeidsuren_inkomen.png"))
    except Exception as e:
        print(f"Skip arbeidsuren_inkomen: {e}")

    # 5. algemene plots
    plot_histogram_numeric(df, output_dir)
    plot_bar_categories(df, output_dir)
    plot_boxplots_by_category(df, output_dir)

    print(f"Alle plots opgeslagen in: {output_dir}")
    print(f"Alle plots opgeslagen in: {output_dir}")