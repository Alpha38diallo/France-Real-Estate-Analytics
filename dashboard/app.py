from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ==================================================
# Configuration de la page
# ==================================================

st.set_page_config(
    page_title="France Real Estate Analytics",
    page_icon="🏠",
    layout="wide"
)

# ==================================================
# Chargement des données
# ==================================================

@st.cache_data
def load_data():

    root_dir = Path(__file__).resolve().parent.parent

    file_path = (
        root_dir
        / "data"
        / "processed"
        / "france_real_estate.parquet"
    )

    df = pd.read_parquet(file_path)

    return df


df = load_data()

# ==================================================
# Normalisation des villes
# ==================================================

df["ville"] = df["commune"]

df.loc[
    df["ville"].str.startswith("PARIS"),
    "ville"
] = "PARIS"

# ==================================================
# Sidebar
# ==================================================

st.sidebar.header("Filtres")

annees = sorted(df["annee"].unique())

types_biens = sorted(
    df["type_local"].dropna().unique()
)

departements = sorted(
    df["code_departement"].astype(str).unique()
)

selected_years = st.sidebar.multiselect(
    "Années",
    annees,
    default=annees
)

selected_types = st.sidebar.multiselect(
    "Types de bien",
    types_biens,
    default=types_biens
)

selected_departements = st.sidebar.multiselect(
    "Départements",
    departements,
    default=departements
)

# ==================================================
# Filtrage
# ==================================================

filtered_df = df[
    (df["annee"].isin(selected_years))
    &
    (df["type_local"].isin(selected_types))
    &
    (
        df["code_departement"]
        .astype(str)
        .isin(selected_departements)
    )
]

# ==================================================
# Titre
# ==================================================

st.title("🏠 Analyse du marché immobilier français")

st.markdown(
    """
    Analyse de plus de 5,5 millions de transactions immobilières françaises
    issues de la base DVF sur la période 2021-2026.
    """
)

# ==================================================
# KPI
# ==================================================

total_transactions = len(filtered_df)

prix_m2_median = int(
    filtered_df["prix_m2"].median()
)

nombre_villes = (
    filtered_df["ville"].nunique()
)

valeur_mediane = int(
    filtered_df["valeur_fonciere"].median()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Transactions analysées",
    f"{total_transactions:,}".replace(",", " ")
)

col2.metric(
    "Prix médian au m²",
    f"{prix_m2_median:,} €".replace(",", " ")
)

col3.metric(
    "Villes analysées",
    f"{nombre_villes:,}".replace(",", " ")
)

col4.metric(
    "Valeur foncière médiane",
    f"{valeur_mediane:,} €".replace(",", " ")
)

st.divider()

# ==================================================
# Evolution du marché
# ==================================================

st.subheader("📈 Évolution du marché immobilier")

yearly_stats = (
    filtered_df
    .groupby("annee")
    .agg(
        prix_m2_moyen=("prix_m2", "mean"),
        nombre_transactions=("prix_m2", "count")
    )
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:

    fig_price = px.line(
        yearly_stats,
        x="annee",
        y="prix_m2_moyen",
        markers=True,
        title="Évolution du prix moyen au m²"
    )

    fig_price.update_layout(
        xaxis_title="Année",
        yaxis_title="Prix moyen au m² (€)"
    )

    st.plotly_chart(
        fig_price,
        use_container_width=True
    )

with col2:

    fig_sales = px.bar(
        yearly_stats,
        x="annee",
        y="nombre_transactions",
        title="Nombre de transactions par année"
    )

    fig_sales.update_layout(
        xaxis_title="Année",
        yaxis_title="Transactions"
    )

    st.plotly_chart(
        fig_sales,
        use_container_width=True
    )

# ==================================================
# Analyse des types de biens
# ==================================================

st.subheader("🏠 Analyse par type de bien")

col1, col2 = st.columns(2)

type_distribution = (
    filtered_df["type_local"]
    .value_counts()
    .reset_index()
)

type_distribution.columns = [
    "type_local",
    "nombre"
]

with col1:

    fig_pie = px.pie(
        type_distribution,
        names="type_local",
        values="nombre",
        title="Répartition des transactions"
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

with col2:

    avg_price_type = (
        filtered_df
        .groupby("type_local")["prix_m2"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_bar_type = px.bar(
        avg_price_type,
        x="type_local",
        y="prix_m2",
        color="prix_m2",
        title="Prix moyen au m² selon le type de bien"
    )

    fig_bar_type.update_layout(
        xaxis_title="Type de bien",
        yaxis_title="Prix moyen au m² (€)"
    )

    st.plotly_chart(
        fig_bar_type,
        use_container_width=True
    )

# ==================================================
# Marchés immobiliers les plus chers
# ==================================================

st.subheader("💎 Les marchés immobiliers les plus chers")

top_price = (
    filtered_df
    .groupby("ville")
    .agg(
        prix_m2_moyen=("prix_m2", "mean"),
        nombre_transactions=("prix_m2", "count")
    )
    .query("nombre_transactions >= 50")
    .sort_values(
        "prix_m2_moyen",
        ascending=False
    )
    .head(10)
    .reset_index()
)

fig_top_price = px.bar(
    top_price,
    x="ville",
    y="prix_m2_moyen",
    color="prix_m2_moyen"
)

fig_top_price.update_layout(
    xaxis_title="Ville",
    yaxis_title="Prix moyen au m² (€)"
)

st.plotly_chart(
    fig_top_price,
    use_container_width=True
)

# ==================================================
# Villes les plus dynamiques
# ==================================================

st.subheader(
    "🏙️ Les villes les plus dynamiques en nombre de transactions"
)

top_transactions = (
    filtered_df["ville"]
    .value_counts()
    .head(10)
    .reset_index()
)

top_transactions.columns = [
    "ville",
    "transactions"
]

fig_top_transactions = px.bar(
    top_transactions,
    x="ville",
    y="transactions",
    color="transactions"
)

fig_top_transactions.update_layout(
    xaxis_title="Ville",
    yaxis_title="Nombre de transactions"
)

st.plotly_chart(
    fig_top_transactions,
    use_container_width=True
)

# ==================================================
# Footer
# ==================================================

st.markdown("---")

st.markdown(
    """
    **France Real Estate Analytics**

    Analyse exploratoire des transactions immobilières françaises à partir des données
    DVF (Demandes de Valeurs Foncières).

    **Période étudiée : 2021 à 2026**  
    **Volume analysé : plus de 5,5 millions de transactions**
    """
)