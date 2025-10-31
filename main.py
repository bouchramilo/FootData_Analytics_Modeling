import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# ⚙️ Configuration de la page
# ============================================================
st.set_page_config(
    page_title="DataFooT",
    page_icon="⚽",
    layout="wide"
)

# ============================================================
# 🏆 Titre principal
# ============================================================
st.title("⚽ DataFooT — Modélisation et Analyse de Données Footballistiques")
st.markdown("---")

# ============================================================
# 🧩 Description du projet
# ============================================================
st.header("🏆 Description du projet")

st.write("""
Ce projet a pour objectif de **créer une application complète d’analyse et de prédiction pour le football professionnel**.  
En s’appuyant sur les données collectées depuis le site **FBref**, l’application permet d’explorer, d’analyser et de visualiser 
les performances des équipes et des joueurs de la **Premier League (saison 2024–2025)**.

L’idée principale est de construire une solution **data-driven** (pilotée par les données) capable d’aider à :
- 📊 Comprendre les performances globales des équipes  
- ⚽ Identifier les meilleurs buteurs et passeurs  
- 🟥 Évaluer la discipline et l’efficacité défensive des joueurs  
- 🔮 Fournir des indicateurs pour anticiper les tendances des matchs à venir
""")

st.markdown("---")

# ============================================================
# ⚙️ Les grandes étapes du projet
# ============================================================
st.header("⚙️ Les grandes étapes du projet")

# --- Étape 1 : Web Scraping
st.subheader("1️⃣ Web Scraping")
st.write("""
- Collecte automatique des données depuis **FBref** à l’aide de **Selenium**  
- Extraction des informations sur les **équipes**, **joueurs** et **matchs** de la saison  
- Sauvegarde des données au format **CSV** pour un traitement ultérieur
""")

# --- Étape 2 : Transformation et nettoyage
st.subheader("2️⃣ Transformation et nettoyage des données")
st.write("""
- 🧹 Suppression des valeurs manquantes et incohérentes  
- 🧭 Uniformisation des formats (dates, unités, noms de colonnes)  
- 📦 Préparation des jeux de données prêts à être exploités
""")

# --- Étape 3 : Stockage et modélisation
st.subheader("3️⃣ Stockage et modélisation")
st.write("""
- Création d’une **base de données relationnelle PostgreSQL**  
- Conception d’un **modèle UML** structurant les relations entre saisons, équipes, joueurs, matchs, résultats et statistiques
""")

# --- Étape 4 : Analyse des données
st.subheader("4️⃣ Analyse des données")
st.write("""
- Calcul des **classements**, **moyennes** et **statistiques clés** (buts, passes, discipline…)  
- Identification des **tendances** à partir des performances individuelles et collectives
""")

# --- Étape 5 : Visualisation avec Streamlit
st.subheader("5️⃣ Visualisation avec Streamlit")
st.write("""
- Création d’un **Dashboard interactif** pour explorer les résultats  
- Intégration de **graphiques dynamiques**, **filtres** et **tableaux interactifs**  
- Option de **téléchargement des données filtrées** au format CSV
""")

st.markdown("---")

# ============================================================
# 🎯 Objectif final
# ============================================================
st.header("🎯 Objectif final")
st.write("""
L’objectif est de fournir un **outil simple, intuitif et interactif** permettant aux utilisateurs — 
**analystes**, **entraîneurs** ou **passionnés** — de **mieux comprendre le football à travers les données**
et de **prendre des décisions plus éclairées**.
""")
