import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db

# Chemin BDD
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "database", "digitallife.db")

# ---- TEXTES BILINGUES ----
TEXTS = {
    "fr": {
        "titre": "📊 Dashboard — Analyse des données",
        "sous_titre": "Analyse descriptive des comportements numériques étudiants",
        "aucune_donnee": "Aucune donnée disponible pour le moment.",
        "total": "Répondants total",
        "pays_rep": "Pays représentés",
        "age_moyen": "Âge moyen",
        "ans": "ans",
        "section1": "🌍 Vue générale",
        "repartition_pays": "Répartition par pays",
        "repartition_genre": "Répartition par genre",
        "repartition_niveau": "Répartition par niveau d'études",
        "section2": "📱 Habitudes numériques",
        "temps_ecran_moy": "Temps d'écran moyen (h/jour)",
        "reseaux_populaires": "Réseaux sociaux les plus utilisés",
        "connexion_types": "Types de connexion utilisés",
        "section3": "🧠 Bien-être académique",
        "stress_moyen": "Stress académique moyen",
        "sommeil_moyen": "Heures de sommeil moyennes",
        "satisfaction_moy": "Satisfaction académique moyenne",
        "correlation": "Corrélation : Temps d'écran vs Stress académique",
        "revision_satisfaction": "Corrélation : Heures de révision vs Satisfaction",
        "filtre_pays": "Filtrer par pays",
        "tous": "Tous les pays",
        "label_ecran": "Temps d'écran (h)",
        "label_stress": "Stress académique",
        "label_revision": "Heures de révision",
        "label_satisfaction": "Satisfaction académique",
        "label_pays": "Pays",
        "label_genre": "Genre",
        "label_niveau": "Niveau",
        "label_reseau": "Réseau social",
        "label_connexion": "Type de connexion",
        "label_count": "Nombre",
    },
    "en": {
        "titre": "📊 Dashboard — Data Analysis",
        "sous_titre": "Descriptive analysis of student digital behaviors",
        "aucune_donnee": "No data available yet.",
        "total": "Total respondents",
        "pays_rep": "Countries represented",
        "age_moyen": "Average age",
        "ans": "yrs",
        "section1": "🌍 General overview",
        "repartition_pays": "Distribution by country",
        "repartition_genre": "Distribution by gender",
        "repartition_niveau": "Distribution by study level",
        "section2": "📱 Digital habits",
        "temps_ecran_moy": "Average screen time (h/day)",
        "reseaux_populaires": "Most used social networks",
        "connexion_types": "Connection types used",
        "section3": "🧠 Academic well-being",
        "stress_moyen": "Average academic stress",
        "sommeil_moyen": "Average sleep hours",
        "satisfaction_moy": "Average academic satisfaction",
        "correlation": "Correlation: Screen time vs Academic stress",
        "revision_satisfaction": "Correlation: Study hours vs Satisfaction",
        "filtre_pays": "Filter by country",
        "tous": "All countries",
        "label_ecran": "Screen time (h)",
        "label_stress": "Academic stress",
        "label_revision": "Study hours",
        "label_satisfaction": "Academic satisfaction",
        "label_pays": "Country",
        "label_genre": "Gender",
        "label_niveau": "Level",
        "label_reseau": "Social network",
        "label_connexion": "Connection type",
        "label_count": "Count",
    }
}


def load_data():
    conn = sqlite3.connect(DB_PATH)

    df_main = pd.read_sql("""
        SELECT
            e.age, e.genre, e.filiere, e.niveau,
            p.nom_pays,
            h.temps_ecran_h, h.reseaux_sociaux,
            h.types_connexion, h.depenses_internet,
            h.appareil_principal,
            b.qualite_sommeil, b.heures_sommeil,
            b.niveau_stress, b.heures_revision,
            b.satisfaction_academique
        FROM etudiant e
        JOIN universite u ON e.id_universite = u.id_universite
        JOIN pays p ON u.id_pays = p.id_pays
        JOIN reponse r ON r.id_etudiant = e.id_etudiant
        JOIN habitudes_numeriques h ON h.id_reponse = r.id_reponse
        JOIN bien_etre b ON b.id_reponse = r.id_reponse
    """, conn)

    conn.close()
    return df_main


def show():
    init_db()

    # ---- LANGUE ----
    col1, col2 = st.columns([4, 1])
    with col2:
        langue = st.selectbox("🌐", ["Français", "English"],
                              label_visibility="collapsed")
    lang = "fr" if langue == "Français" else "en"
    t = TEXTS[lang]

    # ---- HEADER ----
    st.title(t["titre"])
    st.markdown(f"*{t['sous_titre']}*")
    st.divider()

    # ---- CHARGEMENT DONNÉES ----
    df = load_data()

    if df.empty:
        st.warning(t["aucune_donnee"])
        return

    # ---- FILTRE PAR PAYS ----
    pays_liste = [t["tous"]] + sorted(df["nom_pays"].unique().tolist())
    pays_filtre = st.selectbox(t["filtre_pays"], pays_liste)

    if pays_filtre != t["tous"]:
        df = df[df["nom_pays"] == pays_filtre]

    # ---- MÉTRIQUES GLOBALES ----
    st.subheader(t["section1"])
    col1, col2, col3 = st.columns(3)
    col1.metric(t["total"], len(df))
    col2.metric(t["pays_rep"], df["nom_pays"].nunique())
    col3.metric(t["age_moyen"], f"{df['age'].mean():.1f} {t['ans']}")

    # Répartition par pays
    fig_pays = px.pie(df, names="nom_pays", title=t["repartition_pays"],
                      hole=0.3,
                      labels={"nom_pays": t["label_pays"]})
    st.plotly_chart(fig_pays, use_container_width=True)

    # Répartition par genre
    genre_counts = df["genre"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]
    fig_genre = px.bar(genre_counts, x="genre", y="count",
                       title=t["repartition_genre"],
                       color="genre",
                       labels={"genre": t["label_genre"], "count": t["label_count"]})
    st.plotly_chart(fig_genre, use_container_width=True)

    # Répartition par niveau
    niveau_counts = df["niveau"].value_counts().reset_index()
    niveau_counts.columns = ["niveau", "count"]
    fig_niveau = px.bar(niveau_counts, x="niveau", y="count",
                        title=t["repartition_niveau"],
                        color="niveau",
                        labels={"niveau": t["label_niveau"], "count": t["label_count"]})
    st.plotly_chart(fig_niveau, use_container_width=True)

    st.divider()

    # ---- SECTION 2 : HABITUDES NUMÉRIQUES ----
    st.subheader(t["section2"])

    col1, col2 = st.columns(2)
    col1.metric(t["temps_ecran_moy"], f"{df['temps_ecran_h'].mean():.1f}h")
    col2.metric(t["stress_moyen"], f"{df['niveau_stress'].mean():.1f}/5")

    # Réseaux sociaux
    reseaux_all = []
    for r in df["reseaux_sociaux"]:
        try:
            reseaux_all.extend(json.loads(r))
        except:
            pass

    if reseaux_all:
        reseaux_df = pd.Series(reseaux_all).value_counts().reset_index()
        reseaux_df.columns = ["reseau", "count"]
        fig_reseaux = px.bar(reseaux_df, x="reseau", y="count",
                             title=t["reseaux_populaires"],
                             color="reseau",
                             labels={"reseau": t["label_reseau"],
                                     "count": t["label_count"]})
        st.plotly_chart(fig_reseaux, use_container_width=True)

    # Types de connexion
    connexions_all = []
    for c in df["types_connexion"]:
        try:
            connexions_all.extend(json.loads(c))
        except:
            pass

    if connexions_all:
        conn_df = pd.Series(connexions_all).value_counts().reset_index()
        conn_df.columns = ["connexion", "count"]
        fig_conn = px.bar(conn_df, x="connexion", y="count",
                          title=t["connexion_types"],
                          color="connexion",
                          labels={"connexion": t["label_connexion"],
                                  "count": t["label_count"]})
        st.plotly_chart(fig_conn, use_container_width=True)

    st.divider()

    # ---- SECTION 3 : BIEN-ÊTRE ----
    st.subheader(t["section3"])

    col1, col2, col3 = st.columns(3)
    col1.metric(t["stress_moyen"], f"{df['niveau_stress'].mean():.1f}/5")
    col2.metric(t["sommeil_moyen"], f"{df['heures_sommeil'].mean():.1f}h")
    col3.metric(t["satisfaction_moy"], f"{df['satisfaction_academique'].mean():.1f}/5")

    # Corrélation temps d'écran vs stress
    fig_corr1 = px.scatter(df, x="temps_ecran_h", y="niveau_stress",
                           title=t["correlation"],
                           trendline="ols",
                           color="nom_pays",
                           labels={
                               "temps_ecran_h": t["label_ecran"],
                               "niveau_stress": t["label_stress"],
                               "nom_pays": t["label_pays"]
                           })
    st.plotly_chart(fig_corr1, use_container_width=True)

    # Corrélation révision vs satisfaction
    fig_corr2 = px.scatter(df, x="heures_revision", y="satisfaction_academique",
                           title=t["revision_satisfaction"],
                           trendline="ols",
                           color="nom_pays",
                           labels={
                               "heures_revision": t["label_revision"],
                               "satisfaction_academique": t["label_satisfaction"],
                               "nom_pays": t["label_pays"]
                           })
    st.plotly_chart(fig_corr2, use_container_width=True)


if __name__ == "__main__":
    show()