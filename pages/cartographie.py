# ============================================================
# 🎯 IMPORTS
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, ForeignKey,
    Date, Time, Enum
)
from sqlalchemy.orm import declarative_base, relationship


# ============================================================
# ⚙️ CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="Cartographie de la base de données",
    page_icon="⚽",
    layout="wide"
)

# ============================================================
# 🧭 TITRE PRINCIPAL
# ============================================================
st.title("⚽ Cartographie de la base de données")
st.markdown("***")

# ============================================================
# 🔹 SECTION 1 — DESCRIPTION GÉNÉRALE
# ============================================================
st.header("1️⃣ Description générale de la base de données")
st.write(
    "Cette base de données contient l’ensemble des informations "
    "relatives aux compétitions de football : saisons, équipes, joueurs, "
    "matches, résultats et statistiques des joueurs."
)

st.markdown("***")

# ============================================================
# 🔹 SECTION 2 — DESCRIPTION DES TABLES
# ============================================================
st.header("2️⃣ Description des tables de la base de données")

# --- TABLE SAISONS
st.subheader("🟢 Table `saisons`")
st.write("""
- **id** : Integer (PK) — Identifiant unique de la saison  
- **annees** : String — Période de la saison (ex: '2024-2025')
""")

# --- TABLE COMPETITIONS
st.subheader("🟢 Table `competitions`")
st.write("""
- **id** : Integer (PK) — Identifiant unique de la compétition  
- **nom_competition** : String — Nom de la compétition
""")

# --- TABLE EQUIPES
st.subheader("🟢 Table `equipes`")
st.write("""
- **id** : Integer (PK) — Identifiant unique de l’équipe  
- **equipe** : String — Nom de l’équipe  
- **saison_id** : Integer (FK) — Référence à la saison
""")

# --- TABLE JOUEURS
st.subheader("🟢 Table `joueurs`")
st.write("""
- **id** : Integer (PK) — Identifiant unique du joueur  
- **nom_joueur** : String — Nom du joueur  
- **position** : String — Poste du joueur (FW, MF, DF, etc.)  
- **nationalite** : String — Nationalité du joueur  
- **equipe_id** : Integer (FK) — Équipe du joueur
""")

# --- TABLE MATCHES
st.subheader("🟢 Table `matches`")
st.write("""
- **id** : Integer (PK) — Identifiant unique du match  
- **date_match** : Date — Date du match  
- **heure** : Time — Heure du match  
- **round** : String — Tour/Phase de la compétition  
- **venue** : Enum — Lieu du match ('Home', 'Away', 'Neutral')  
- **team_home_id** : Integer (FK) — Équipe à domicile  
- **team_away_id** : Integer (FK) — Équipe à l’extérieur  
- **competition_id** : Integer (FK) — Compétition du match  
- **saison_id** : Integer (FK) — Saison du match
""")

# --- TABLE RESULTAT_MATCHS
st.subheader("🟢 Table `resultat_matchs`")
st.write("""
- **id** : Integer (PK) — Identifiant unique du résultat  
- **matche_id** : Integer (FK) — Référence au match  
- **equipe_id** : Integer (FK) — Équipe concernée  
- **buts_marques** : Integer — Nombre de buts marqués  
- **buts_concedes** : Integer — Nombre de buts concédés  
- **resultat** : Enum — Résultat du match ('Victoire', 'Défaite', 'Nul')
""")

# --- TABLE STATISTIQUES_JOUEURS
st.subheader("🟢 Table `statistiques_joueurs`")
st.write("""
- **id** : Integer (PK) — Identifiant unique de la statistique  
- **joueur_id** : Integer (FK) — Joueur concerné  
- **buts** : Integer — Nombre de buts marqués  
- **passes_decisives** : Integer — Nombre de passes décisives  
- **nb_matches_played** : Integer — Nombre de matchs joués  
- **cartons_jaunes** : Integer — Nombre de cartons jaunes  
- **cartons_rouges** : Integer — Nombre de cartons rouges
""")

st.markdown("***")

# ============================================================
# 🔹 SECTION 3 — RELATIONS ENTRE LES TABLES
# ============================================================
st.header("3️⃣ Relations entre les tables")

st.subheader("🔸 Relations One-to-Many")
st.write("""
- Une **saison** → plusieurs **équipes** (`saisons.id` → `equipes.saison_id`)  
- Une **saison** → plusieurs **matches** (`saisons.id` → `matches.saison_id`)  
- Une **compétition** → plusieurs **matches** (`competitions.id` → `matches.competition_id`)  
- Une **équipe** → plusieurs **joueurs** (`equipes.id` → `joueurs.equipe_id`)  
- Un **match** → plusieurs **résultats** (`matches.id` → `resultat_matchs.matche_id`)  
- Une **équipe** → plusieurs **résultats** (`equipes.id` → `resultat_matchs.equipe_id`)  
- Un **joueur** → une **statistique** (`joueurs.id` → `statistiques_joueurs.joueur_id`)
""")

st.subheader("🔸 Relations Many-to-Many implicites")
st.write("""
- **Équipes ↔ Matches** (via `team_home_id` et `team_away_id` dans `matches`)  
- **Équipes ↔ Compétitions** (via `matches`)
""")

st.markdown("***")

# ============================================================
# 🔹 SECTION 4 — DIAGRAMME UML
# ============================================================
st.header("4️⃣ Diagramme de classes (UML)")
st.image("Conception/Class_diagram.png", caption="Diagramme UML de la base de données", width=800)
