import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.formulaire import show as show_formulaire
from pages.dashboard import show as show_dashboard

# ---- CONFIG PAGE ----
st.set_page_config(
    page_title="DigitalLife Campus",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: #7C3AED; font-size: 28px;'>📱 DigitalLife</h1>
            <h2 style='color: #A78BFA; font-size: 16px; font-weight: normal;'>Campus</h2>
            <hr style='border-color: #7C3AED; margin: 10px 0;'>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigation")

    page = st.radio(
        "",
        options=["Formulaire", "Dashboard"],
        format_func=lambda x: "📝 Formulaire de collecte" if x == "Formulaire"
                              else "📊 Dashboard analytique",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    st.markdown("""
        <div style='text-align: center; padding: 10px 0; color: #A78BFA; font-size: 12px;'>
            <p>Étude sur les comportements<br>numériques étudiants</p>
            <p style='color: #7C3AED;'>🌍 Multi-pays | Bilingue FR/EN</p>
        </div>
    """, unsafe_allow_html=True)

# ---- CONTENU PRINCIPAL ----
if page == "Formulaire":
    show_formulaire()
else:
    show_dashboard()