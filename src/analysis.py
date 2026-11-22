import pandas as pd
from pathlib import Path

# ==========================
# Chargement des données
# ==========================

DATA_FILE = Path("data/processed/france_real_estate.parquet")

print("Chargement des données...")

df = pd.read_parquet(DATA_FILE)

print(f"Nombre de lignes : {len(df):,}")

# ==========================
# KPI Généraux
# ==========================

total_sales = len(df)

avg_price_m2 = df["prix_m2"].mean()

median_price_m2 = df["prix_m2"].median()

avg_property_value = df["valeur_fonciere"].mean()

print("\n" + "=" * 50)
print("KPI GÉNÉRAUX")
print("=" * 50)

print(f"Transactions : {total_sales:,}")
print(f"Prix moyen au m² : {avg_price_m2:,.2f} €")
print(f"Prix médian au m² : {median_price_m2:,.2f} €")
print(f"Valeur foncière moyenne : {avg_property_value:,.2f} €")

# ==========================
# Répartition des biens
# ==========================

property_distribution = (
    df["type_local"]
    .value_counts()
    .reset_index()
)

property_distribution.columns = [
    "type_local",
    "nombre_ventes"
]

print("\n" + "=" * 50)
print("RÉPARTITION DES BIENS")
print("=" * 50)

print(property_distribution)

# ==========================
# Top 10 communes les plus chères
# ==========================

top_expensive_cities = (
    df.groupby("commune")
    .agg(
        prix_m2_moyen=("prix_m2", "mean"),
        nombre_ventes=("prix_m2", "size")
    )
    .query("nombre_ventes >= 50")
    .sort_values(
        "prix_m2_moyen",
        ascending=False
    )
    .head(10)
    .reset_index()
)

print("\n" + "=" * 50)
print("TOP 10 COMMUNES LES PLUS CHÈRES")
print("=" * 50)

print(top_expensive_cities)

# ==========================
# Top 10 départements
# ==========================

top_departments = (
    df.groupby("code_departement")
    .size()
    .reset_index(name="nombre_ventes")
    .sort_values(
        "nombre_ventes",
        ascending=False
    )
    .head(10)
)

print("\n" + "=" * 50)
print("TOP 10 DÉPARTEMENTS PAR NOMBRE DE VENTES")
print("=" * 50)

print(top_departments)

# ==========================
# Evolution annuelle du prix au m²
# ==========================

yearly_price = (
    df.groupby("annee")
    .agg(
        prix_m2_moyen=("prix_m2", "mean"),
        prix_m2_median=("prix_m2", "median")
    )
    .reset_index()
)

print("\n" + "=" * 50)
print("EVOLUTION ANNUELLE DU PRIX AU M²")
print("=" * 50)

print(yearly_price)

# ==========================
# Evolution annuelle des ventes
# ==========================

yearly_sales = (
    df.groupby("annee")
    .size()
    .reset_index(name="nombre_ventes")
)

print("\n" + "=" * 50)
print("EVOLUTION ANNUELLE DES VENTES")
print("=" * 50)

print(yearly_sales)

# ==========================
# Top 10 communes les plus actives
# ==========================

top_sales_cities = (
    df.groupby("commune")
    .size()
    .reset_index(name="nombre_ventes")
    .sort_values(
        "nombre_ventes",
        ascending=False
    )
    .head(10)
)

print("\n" + "=" * 50)
print("TOP 10 COMMUNES PAR NOMBRE DE VENTES")
print("=" * 50)

print(top_sales_cities)

# ==========================
# Sauvegarde KPI
# ==========================

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(exist_ok=True)

property_distribution.to_csv(
    OUTPUT_DIR / "property_distribution.csv",
    index=False
)

top_expensive_cities.to_csv(
    OUTPUT_DIR / "top_expensive_cities.csv",
    index=False
)

top_departments.to_csv(
    OUTPUT_DIR / "top_departments.csv",
    index=False
)

yearly_price.to_csv(
    OUTPUT_DIR / "yearly_price.csv",
    index=False
)

yearly_sales.to_csv(
    OUTPUT_DIR / "yearly_sales.csv",
    index=False
)

top_sales_cities.to_csv(
    OUTPUT_DIR / "top_sales_cities.csv",
    index=False
)

print("\n✅ KPI exportés dans le dossier reports/")