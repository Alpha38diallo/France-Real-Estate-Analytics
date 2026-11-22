import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw/dvf")
OUTPUT_FILE = Path("data/processed/france_real_estate.parquet")

COLUMNS = [
    "Date mutation",
    "Nature mutation",
    "Valeur fonciere",
    "Commune",
    "Code departement",
    "Type local",
    "Surface reelle bati",
    "Nombre pieces principales",
    "Surface terrain",
]

all_dfs = []

for file in sorted(RAW_DIR.glob("*.txt")):

    print(f"\n{'=' * 50}")
    print(f"Lecture : {file.name}")
    print(f"{'=' * 50}")

    df = pd.read_csv(
        file,
        sep="|",
        usecols=COLUMNS,
        low_memory=False
    )

    print(f"Lignes initiales : {len(df):,}")

    # Vente classique uniquement
    df = df[df["Nature mutation"] == "Vente"]

    # Logements résidentiels uniquement
    df = df[
        df["Type local"].isin(
            ["Appartement", "Maison"]
        )
    ]

    # Conversion prix
    df["Valeur fonciere"] = (
        df["Valeur fonciere"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    df["Valeur fonciere"] = pd.to_numeric(
        df["Valeur fonciere"],
        errors="coerce"
    )

    # Conversion surface
    df["Surface reelle bati"] = pd.to_numeric(
        df["Surface reelle bati"],
        errors="coerce"
    )

    # Suppression NA
    df = df.dropna(
        subset=[
            "Valeur fonciere",
            "Surface reelle bati"
        ]
    )

    # Surface réaliste
    df = df[
        df["Surface reelle bati"]
        .between(10, 500)
    ]

    # Dates
    df["Date mutation"] = pd.to_datetime(
        df["Date mutation"],
        dayfirst=True,
        errors="coerce"
    )

    # Année et mois
    df["annee"] = df["Date mutation"].dt.year
    df["mois"] = df["Date mutation"].dt.month

    # Prix au m²
    df["prix_m2"] = (
        df["Valeur fonciere"]
        / df["Surface reelle bati"]
    )

    # Suppression des anomalies
    df = df[
        df["prix_m2"]
        .between(100, 20000)
    ]

    # Renommage
    df = df.rename(
        columns={
            "Date mutation": "date_mutation",
            "Valeur fonciere": "valeur_fonciere",
            "Commune": "commune",
            "Code departement": "code_departement",
            "Type local": "type_local",
            "Surface reelle bati": "surface_reelle_bati",
            "Nombre pieces principales": "nombre_pieces_principales",
            "Surface terrain": "surface_terrain",
        }
    )

    # Colonnes finales
    df = df[
        [
            "date_mutation",
            "annee",
            "mois",
            "valeur_fonciere",
            "commune",
            "code_departement",
            "type_local",
            "surface_reelle_bati",
            "nombre_pieces_principales",
            "surface_terrain",
            "prix_m2",
        ]
    ]

    print(f"Lignes après nettoyage : {len(df):,}")

    all_dfs.append(df)

print(f"\n{'=' * 50}")
print("Fusion des fichiers")
print(f"{'=' * 50}")

final_df = pd.concat(
    all_dfs,
    ignore_index=True
)

print(f"Nombre total de lignes : {len(final_df):,}")

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

final_df.to_parquet(
    OUTPUT_FILE,
    index=False
)

print("\nDataset sauvegardé :")
print(OUTPUT_FILE)

print("\nRésumé final :")
print(final_df[["prix_m2", "surface_reelle_bati"]].describe())