import pandas as pd

# Fichier de test
FILE_PATH = "data/raw/dvf/ValeursFoncieres-2025.txt"

# Colonnes utiles
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

print("Lecture du fichier...")

df = pd.read_csv(
    FILE_PATH,
    sep="|",
    usecols=COLUMNS,
    low_memory=False
)

print(f"Lignes initiales : {len(df):,}")

# Vente uniquement
df = df[df["Nature mutation"] == "Vente"]

# Maison et appartement uniquement
df = df[df["Type local"].isin(["Appartement", "Maison"])]

# Conversion du prix
df["Valeur fonciere"] = (
    df["Valeur fonciere"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)

df["Valeur fonciere"] = pd.to_numeric(
    df["Valeur fonciere"],
    errors="coerce"
)

# Surface
df["Surface reelle bati"] = pd.to_numeric(
    df["Surface reelle bati"],
    errors="coerce"
)

# Suppression des lignes invalides
df = df.dropna(
    subset=[
        "Valeur fonciere",
        "Surface reelle bati"
    ]
)

df = df[df["Surface reelle bati"] > 0]

# Date
df["Date mutation"] = pd.to_datetime(
    df["Date mutation"],
    dayfirst=True,
    errors="coerce"
)

# Année
df["annee"] = df["Date mutation"].dt.year

# prix au m²
df["prix_m2"] = (
    df["Valeur fonciere"]
    / df["Surface reelle bati"]
)

# filtre surface
df = df[
    df["Surface reelle bati"].between(10, 500)
]

# filtre prix au m²
df = df[
    df["prix_m2"].between(100, 20000)
]

print(f"Lignes après nettoyage : {len(df):,}")

print("\nTypes de biens :")
print(df["Type local"].value_counts())

print("\nAnnées :")
print(df["annee"].value_counts())

print("\nStatistiques prix/m² :")
print(df["prix_m2"].describe())

# Sauvegarde test
df.to_parquet(
    "data/processed/test_2025.parquet",
    index=False
)

print("\nFichier sauvegardé dans data/processed/test_2025.parquet")

print("\nTop 10 prix/m² les plus élevés :")

print(
    df[
        [
            "Commune",
            "Valeur fonciere",
            "Surface reelle bati",
            "prix_m2"
        ]
    ]
    .sort_values("prix_m2", ascending=False)
    .head(10)
)

print("\nTop 10 prix/m² les plus faibles :")

print(
    df[
        [
            "Commune",
            "Valeur fonciere",
            "Surface reelle bati",
            "prix_m2"
        ]
    ]
    .sort_values("prix_m2", ascending=True)
    .head(10)
)

print("\nStatistiques surfaces :")
print(df["Surface reelle bati"].describe())

print(df["Code departement"].nunique())
print(df["Commune"].nunique())
df["mois"] = df["Date mutation"].dt.month