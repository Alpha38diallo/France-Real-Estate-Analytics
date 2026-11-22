from pathlib import Path

import pandas as pd
import plotly.express as px

# ==================================================
# Configuration
# ==================================================

DATA_FILE = "data/processed/france_real_estate.parquet"

FIGURES_DIR = Path("reports/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# Chargement des données
# ==================================================

print("Chargement des données...")

df = pd.read_parquet(DATA_FILE)

print(f"Lignes : {len(df):,}")

# ==================================================
# 1. Evolution du prix moyen au m²
# ==================================================

yearly_price = (
    df.groupby("annee")
    .agg(prix_m2_moyen=("prix_m2", "mean"))
    .reset_index()
)

yearly_price["prix_m2_moyen"] = (
    yearly_price["prix_m2_moyen"]
    .round(0)
)

fig1 = px.line(
    yearly_price,
    x="annee",
    y="prix_m2_moyen",
    markers=True,
    title="Average Price per Square Meter by Year"
)

fig1.update_layout(
    xaxis_title="Year",
    yaxis_title="Average Price per m² (€)",
    template="plotly_white"
)

fig1.write_image(
    FIGURES_DIR / "yearly_price.png",
    width=1200,
    height=700
)

print("✅ yearly_price.png")

# ==================================================
# 2. Evolution du nombre de ventes
# ==================================================

yearly_sales = (
    df.groupby("annee")
    .size()
    .reset_index(name="nombre_ventes")
)

fig2 = px.bar(
    yearly_sales,
    x="annee",
    y="nombre_ventes",
    text_auto=",",
    title="Number of Transactions by Year"
)

fig2.update_layout(
    xaxis_title="Year",
    yaxis_title="Transactions",
    template="plotly_white",
    showlegend=False
)

fig2.write_image(
    FIGURES_DIR / "yearly_sales.png",
    width=1200,
    height=700
)

print("✅ yearly_sales.png")

# ==================================================
# 3. Répartition Maison / Appartement
# ==================================================

property_distribution = (
    df["type_local"]
    .value_counts()
    .reset_index()
)

property_distribution.columns = [
    "type_local",
    "nombre_ventes"
]

fig3 = px.bar(
    property_distribution,
    x="type_local",
    y="nombre_ventes",
    text_auto=",",
    title="Property Type Distribution"
)

fig3.update_layout(
    xaxis_title="Property Type",
    yaxis_title="Transactions",
    template="plotly_white",
    showlegend=False
)

fig3.write_image(
    FIGURES_DIR / "property_distribution.png",
    width=1200,
    height=700
)

print("✅ property_distribution.png")

# ==================================================
# 4. Top 10 villes les plus chères
# ==================================================

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

top_expensive_cities["prix_m2_moyen"] = (
    top_expensive_cities["prix_m2_moyen"]
    .round(0)
)

fig4 = px.bar(
    top_expensive_cities.sort_values(
        "prix_m2_moyen"
    ),
    x="prix_m2_moyen",
    y="commune",
    orientation="h",
    text_auto=",",
    title="Top 10 Most Expensive Cities"
)

fig4.update_layout(
    xaxis_title="Average Price per m² (€)",
    yaxis_title="City",
    template="plotly_white",
    showlegend=False
)

fig4.write_image(
    FIGURES_DIR / "top_expensive_cities.png",
    width=1200,
    height=700
)

print("✅ top_expensive_cities.png")

# ==================================================
# 5. Top départements
# ==================================================

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

fig5 = px.bar(
    top_departments,
    x="code_departement",
    y="nombre_ventes",
    text_auto=",",
    title="Top 10 Departments by Transactions"
)

fig5.update_layout(
    xaxis_title="Department",
    yaxis_title="Transactions",
    template="plotly_white",
    showlegend=False
)

fig5.write_image(
    FIGURES_DIR / "top_departments.png",
    width=1200,
    height=700
)

print("✅ top_departments.png")

# ==================================================
# 6. Top villes par nombre de ventes
# ==================================================

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

fig6 = px.bar(
    top_sales_cities.sort_values(
        "nombre_ventes"
    ),
    x="nombre_ventes",
    y="commune",
    orientation="h",
    text_auto=",",
    title="Top 10 Cities by Transactions"
)

fig6.update_layout(
    xaxis_title="Transactions",
    yaxis_title="City",
    template="plotly_white",
    showlegend=False
)

fig6.write_image(
    FIGURES_DIR / "top_sales_cities.png",
    width=1200,
    height=700
)

print("✅ top_sales_cities.png")

# ==================================================
# Fin
# ==================================================

print("\n🎉 All visualizations generated successfully!")
print(f"📁 Output folder: {FIGURES_DIR}")