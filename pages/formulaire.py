import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import (
    init_db, get_all_pays, insert_universite,
    insert_etudiant, insert_reponse,
    insert_habitudes, insert_bien_etre
)

# ---- TEXTES BILINGUES ----
TEXTS = {
    "fr": {
        "titre": "📱 DigitalLife Campus",
        "sous_titre": "Comportements numériques & bien-être des étudiants",
        "section1": "👤 Informations personnelles",
        "age": "Âge",
        "genre": "Genre",
        "genres": ["Homme", "Femme", "Autre"],
        "filiere": "Filière d'études",
        "niveau": "Niveau d'études",
        "niveaux": ["L1", "L2", "L3", "M1", "M2", "Doctorat", "Autre"],
        "pays": "Pays",
        "universite": "Université / École",
        "ville": "Ville",
        "autre_pays": "Précisez votre pays",
        "autre_devise": "Devise utilisée (ex: USD, GBP...)",
        "noms_pays": {
            "Cameroun": "Cameroun",
            "Sénégal": "Sénégal",
            "Côte d'Ivoire": "Côte d'Ivoire",
            "Mali": "Mali",
            "France": "France",
            "Allemagne": "Allemagne",
            "Canada": "Canada",
            "Hong Kong": "Hong Kong",
            "Autre": "Autre"
        },
        "section2": "📱 Habitudes numériques",
        "temps_ecran": "Temps d'écran quotidien (heures)",
        "reseaux": "Réseaux sociaux utilisés",
        "connexion": "Type(s) de connexion utilisés",
        "depenses": "Dépenses internet mensuelles",
        "appareil": "Appareil principal",
        "appareils": ["Smartphone", "PC / Ordinateur", "Tablette", "Les deux (smartphone + PC)"],
        "section3": "🧠 Bien-être & vie académique",
        "qualite_sommeil": "Qualité du sommeil",
        "heures_sommeil": "Heures de sommeil par nuit",
        "niveau_stress": "Niveau de stress académique",
        "heures_revision": "Heures de révision par jour",
        "satisfaction": "Satisfaction académique générale",
        "echelle": "1 = Très faible | 5 = Très élevé",
        "soumettre": "Soumettre mes réponses",
        "succes": "Merci ! Vos réponses ont été enregistrées.",
        "erreur_reseaux": "Veuillez sélectionner au moins un réseau social.",
        "erreur_connexion": "Veuillez sélectionner au moins un type de connexion.",
        "erreur_age": "L'âge doit être entre 15 et 60 ans.",
    },
    "en": {
        "titre": "📱 DigitalLife Campus",
        "sous_titre": "Digital behavior & student well-being",
        "section1": "👤 Personal information",
        "age": "Age",
        "genre": "Gender",
        "genres": ["Male", "Female", "Other"],
        "filiere": "Field of study",
        "niveau": "Study level",
        "niveaux": ["L1", "L2", "L3", "M1", "M2", "PhD", "Other"],
        "pays": "Country",
        "universite": "University / School",
        "ville": "City",
        "autre_pays": "Specify your country",
        "autre_devise": "Currency used (e.g. USD, GBP...)",
        "noms_pays": {
            "Cameroun": "Cameroon",
            "Sénégal": "Senegal",
            "Côte d'Ivoire": "Ivory Coast",
            "Mali": "Mali",
            "France": "France",
            "Allemagne": "Germany",
            "Canada": "Canada",
            "Hong Kong": "Hong Kong",
            "Autre": "Other"
        },
        "section2": "📱 Digital habits",
        "temps_ecran": "Daily screen time (hours)",
        "reseaux": "Social media used",
        "connexion": "Type(s) of connection used",
        "depenses": "Monthly internet expenses",
        "appareil": "Main device",
        "appareils": ["Smartphone", "PC / Computer", "Tablet", "Both (smartphone + PC)"],
        "section3": "🧠 Well-being & academic life",
        "qualite_sommeil": "Sleep quality",
        "heures_sommeil": "Hours of sleep per night",
        "niveau_stress": "Academic stress level",
        "heures_revision": "Study hours per day",
        "satisfaction": "Overall academic satisfaction",
        "echelle": "1 = Very low | 5 = Very high",
        "soumettre": "Submit my answers",
        "succes": "Thank you! Your answers have been saved.",
        "erreur_reseaux": "Please select at least one social network.",
        "erreur_connexion": "Please select at least one connection type.",
        "erreur_age": "Age must be between 15 and 60.",
    }
}

RESEAUX_OPTIONS = {
    "fr": ["TikTok", "Instagram", "WhatsApp", "Facebook",
           "Twitter/X", "YouTube", "Snapchat", "LinkedIn", "Autre"],
    "en": ["TikTok", "Instagram", "WhatsApp", "Facebook",
           "Twitter/X", "YouTube", "Snapchat", "LinkedIn", "Other"]
}

CONNEXION_OPTIONS = {
    "fr": ["WiFi domicile", "WiFi campus", "Data mobile", "Box internet personnelle"],
    "en": ["Home WiFi", "Campus WiFi", "Mobile data", "Personal internet box"]
}


def show():
    init_db()

    # Bloquer double soumission
    if st.session_state.get("soumis"):
        st.success("Vos réponses ont déjà été enregistrées.")
        st.info("Merci pour votre participation !")
        if st.button("Soumettre une nouvelle réponse / Submit new response"):
            st.session_state["soumis"] = False
            st.rerun()
        return

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

    # ---- SECTION 1 : INFOS PERSO ----
    st.subheader(t["section1"])

    age = st.number_input(t["age"], min_value=15, max_value=60, value=20)
    genre = st.selectbox(t["genre"], t["genres"])
    filiere = st.text_input(
        t["filiere"],
        placeholder="ex: Computer Science, Medicine..." if lang == "en"
        else "ex: Informatique, Médecine..."
    )
    niveau = st.selectbox(t["niveau"], t["niveaux"])

    # Pays
    pays_data = get_all_pays()
    pays_noms = [t["noms_pays"].get(p[1], p[1]) for p in pays_data]
    pays_choisi = st.selectbox(t["pays"], pays_noms)

    # Retrouver le nom original du pays pour la BDD
    pays_nom_original = next(
        (p[1] for p in pays_data if t["noms_pays"].get(p[1], p[1]) == pays_choisi),
        pays_choisi
    )
    pays_info = next((p for p in pays_data if p[1] == pays_nom_original), None)

    # Devise automatique ou manuelle
    if pays_nom_original == "Autre":
        autre_pays = st.text_input(t["autre_pays"])
        autre_devise = st.text_input(t["autre_devise"])
        nom_pays_final = autre_pays
        devise_finale = autre_devise
    else:
        nom_pays_final = pays_nom_original
        devise_finale = f"{pays_info[2]} ({pays_info[3]})"
        st.info(f"💱 Devise : {devise_finale}")

    universite = st.text_input(
        t["universite"],
        placeholder="ex: University of Yaoundé I" if lang == "en"
        else "ex: Université de Yaoundé I"
    )
    ville = st.text_input(t["ville"], placeholder="ex: Yaoundé")

    st.divider()

    # ---- SECTION 2 : HABITUDES NUMÉRIQUES ----
    st.subheader(t["section2"])

    temps_ecran = st.slider(t["temps_ecran"], 0.0, 16.0, 4.0, step=0.5)
    reseaux = st.multiselect(t["reseaux"], RESEAUX_OPTIONS[lang])
    connexions = st.multiselect(t["connexion"], CONNEXION_OPTIONS[lang])
    depenses = st.number_input(
        f"{t['depenses']} ({devise_finale})",
        min_value=0.0, step=100.0 if "FCFA" in devise_finale else 1.0
    )
    appareil = st.selectbox(t["appareil"], t["appareils"])

    st.divider()

    # ---- SECTION 3 : BIEN-ÊTRE ----
    st.subheader(t["section3"])
    st.caption(t["echelle"])

    qualite_sommeil = st.slider(t["qualite_sommeil"], 1, 5, 3)
    heures_sommeil = st.slider(t["heures_sommeil"], 0.0, 12.0, 7.0, step=0.5)
    niveau_stress = st.slider(t["niveau_stress"], 1, 5, 3)
    heures_revision = st.slider(t["heures_revision"], 0.0, 12.0, 2.0, step=0.5)
    satisfaction = st.slider(t["satisfaction"], 1, 5, 3)

    st.divider()

    # ---- SOUMISSION ----
    if st.button(t["soumettre"], type="primary", use_container_width=True):

        # Validations
        if not reseaux:
            st.error(t["erreur_reseaux"])
            return
        if not connexions:
            st.error(t["erreur_connexion"])
            return
        if pays_nom_original == "Autre" and (not autre_pays or not autre_devise):
            st.error("Veuillez remplir le pays et la devise." if lang == "fr"
                     else "Please fill in the country and currency.")
            return

        # Normaliser les connexions en français
        connexions_norm = {
            "Home WiFi": "WiFi domicile",
            "Campus WiFi": "WiFi campus",
            "Mobile data": "Data mobile",
            "Personal internet box": "Box internet personnelle",
            "Other": "Autre"
        }
        connexions = [connexions_norm.get(c, c) for c in connexions]

        # Normaliser les réseaux
        reseaux_norm = {"Other": "Autre"}
        reseaux = [reseaux_norm.get(r, r) for r in reseaux]

        # Insertion BDD
        id_pays = pays_info[0] if pays_nom_original != "Autre" else get_all_pays()[-1][0]
        id_univ = insert_universite(universite, ville, id_pays)
        id_etu = insert_etudiant(age, genre, filiere, niveau, id_univ)
        id_rep = insert_reponse(id_etu)
        insert_habitudes(id_rep, temps_ecran, reseaux, connexions, depenses, appareil)
        insert_bien_etre(id_rep, qualite_sommeil, heures_sommeil,
                         niveau_stress, heures_revision, satisfaction)

        st.success(t["succes"])
        st.balloons()
        st.session_state["soumis"] = True


if __name__ == "__main__":
    show()