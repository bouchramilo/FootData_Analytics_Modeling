# ============================================================
# 🎯 IMPORTS
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy import create_engine, MetaData,Table, Column, Integer, String, ForeignKey, DateTime, Date, Time, Numeric, Text, insert, Float, Enum, case, select, desc, asc, func
from sqlalchemy.orm import declarative_base, relationship




# ============================================================
# ⚙️ Configuration de la page
# ============================================================
st.set_page_config(
    page_title="Analyse des données - DataFooT",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analyse des données footballistiques")
st.markdown("---")

# ============================================================
# 🔌 Connexion à la base de données PostgreSQL
# ============================================================
Base = declarative_base()
metadata = MetaData()
engine = create_engine("postgresql://postgres:bouchra@localhost:5432/FootData_db")

# ============================================================
# Fonction d'execution
# ============================================================
def run_query(query):
    """Exécute une requête SQL et renvoie un DataFrame pandas."""
    with engine.connect() as conn:
        return pd.read_sql(query, conn)
    
    

# ============================================================
# 🔍 Les Tables :
# ============================================================
Saison = Table(
    'saisons',
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("annees", String, unique=True, index=True, nullable=False)
)


Competition = Table(
    'competitions',
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("nom_competition", String, unique=True, index=True, nullable=False)
)


Equipe = Table(
    'equipes', 
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("equipe", String, index=True, nullable=False),
    Column("saison_id", Integer, ForeignKey("saisons.id", ondelete="CASCADE"))
)



Joueur = Table(
    'joueurs', 
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("nom_joueur", String, index=True, nullable=False),
    Column("position", String, index=True, nullable=False),
    Column("nationalite", String, index=True, nullable=False),
    Column("equipe_id", Integer, ForeignKey("equipes.id", ondelete="CASCADE"))
)

Matche = Table(
    'matches', 
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("date_match", Date, nullable=False),
    Column("heure", Time, nullable=False),
    Column("round", String, index=True, nullable=False),
    Column("venue", Enum('Home', 'Away', 'Neutral', name='venue_enum'), nullable=False),
    Column("team_home_id", Integer, ForeignKey("equipes.id", ondelete="CASCADE")),
    Column("team_away_id", Integer, ForeignKey("equipes.id", ondelete="CASCADE")),
    Column("competition_id", Integer, ForeignKey("competitions.id", ondelete="CASCADE")),
    Column("saison_id", Integer, ForeignKey("saisons.id", ondelete="CASCADE")),
)



Resultat_Match = Table(
    'resultat_matchs', 
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("matche_id", Integer, ForeignKey("matches.id", ondelete="CASCADE")),
    Column("equipe_id", Integer, ForeignKey("equipes.id", ondelete="CASCADE")),
    Column("buts_marques", Integer, nullable=False),
    Column("buts_concedes", Integer, nullable=False),
    Column("resultat", Enum('Victoire', 'Défaite', 'Nul', name='resultat_enum'), nullable=False),
)



Stat_joueur = Table(
    'statistiques_joueurs', 
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("joueur_id", Integer, ForeignKey("joueurs.id", ondelete="CASCADE")),
    Column("buts", Float, nullable=False),  # Changé en Float pour accepter 29.0
    Column("passes_decisives", Float, nullable=False),  # Changé en Float
    Column("nb_matches_played", Integer, nullable=False),
    Column("cartons_jaunes", Float, nullable=False),  # Changé en Float
    Column("cartons_rouges", Float, nullable=False),  # Changé en Float
)


# ============================================================
# 🔍 Analyses principales : des tables et des histograms
# ============================================================
# ! ========================================================================================================================


st.header("1️⃣ Top 10 des meilleurs buteurs")

query_equipes = select(Equipe.c.equipe).distinct().order_by(Equipe.c.equipe)
df_equipes = run_query(query_equipes)


selected_team_1 = st.selectbox(
    "🔍 Filtrer par équipe :", 
    options=["Toutes"] + df_equipes["equipe"].tolist(),
    key="select_team_1"
)

query_buteurs = (
    select(
        Joueur.c.nom_joueur.label("Nom_Joueur"), 
        Equipe.c.equipe.label("Nom_Equipe"),
        Stat_joueur.c.buts.label("nb_Buts")
    )
    .select_from(
        Stat_joueur
        .join(Joueur, Stat_joueur.c.joueur_id == Joueur.c.id)
        .join(Equipe, Joueur.c.equipe_id == Equipe.c.id)
    )
)

if selected_team_1 != "Toutes":
    query_buteurs = query_buteurs.where(Equipe.c.equipe == selected_team_1)

query_buteurs = query_buteurs.order_by(desc(Stat_joueur.c.buts)).limit(10)

df_buteurs = run_query(query_buteurs)

st.bar_chart(df_buteurs.set_index("Nom_Joueur")["nb_Buts"])
st.dataframe(df_buteurs, use_container_width=True)

st.download_button(
    "📥 Télécharger les données (CSV)", 
    df_buteurs.to_csv(index=False), 
    "top_buteurs.csv"
)

st.markdown("---")

# ! ========================================================================================================================


st.header("2️⃣ Joueurs les plus décisifs (buts + passes)")

query_equipes = select(Equipe.c.equipe).distinct().order_by(Equipe.c.equipe)
df_equipes = run_query(query_equipes)

selected_team_2 = st.selectbox(
    "🔍 Filtrer par équipe :", 
    options=["Toutes"] + df_equipes["equipe"].tolist(),
    key="select_team_2"
)

total_buts_passes = (Stat_joueur.c.buts + Stat_joueur.c.passes_decisives).label("Total_Buts_Passes")

query_decisifs = (
    select(
        Joueur.c.nom_joueur.label("Nom_Joueur"), 
        Equipe.c.equipe.label("Equipe"), 
        Stat_joueur.c.buts.label("Buts"), 
        Stat_joueur.c.passes_decisives.label("Passes_decisives"), 
        total_buts_passes
    )
    .select_from(
        Stat_joueur
        .join(Joueur, Stat_joueur.c.joueur_id == Joueur.c.id)
        .join(Equipe, Joueur.c.equipe_id == Equipe.c.id)
    )
)


if selected_team_2 != "Toutes":
    query_decisifs = query_decisifs.where(Equipe.c.equipe == selected_team_2)


query_decisifs = query_decisifs.order_by(desc(total_buts_passes)).limit(10)

df_decisifs = run_query(query_decisifs)

st.bar_chart(df_decisifs.set_index("Nom_Joueur")["Total_Buts_Passes"])
st.dataframe(df_decisifs, use_container_width=True)

st.download_button(
    "📥 Télécharger les données (CSV)", 
    df_decisifs.to_csv(index=False), 
    "joueurs_decisifs.csv"
)

st.markdown("---")

# ! ========================================================================================================================
st.header("3️⃣ Joueurs les plus disciplinés (cartons)")

query_equipes = select(Equipe.c.equipe).distinct().order_by(Equipe.c.equipe)
df_equipes = run_query(query_equipes)

selected_team_3 = st.selectbox(
    "🔍 Filtrer par équipe :", 
    options=["Toutes"] + df_equipes["equipe"].tolist(),
    key="select_team_3"
)

# ***
score_discipline = (Stat_joueur.c.cartons_jaunes + Stat_joueur.c.cartons_rouges).label('Score_discipline')

query_discipline = (
    select(
        Joueur.c.nom_joueur.label("Nom_Joueur"), 
        Equipe.c.equipe.label("Equipe"), 
        Stat_joueur.c.cartons_jaunes.label("Cartons_jaunes"), 
        Stat_joueur.c.cartons_rouges.label("Cartons_rouges"), 
        score_discipline
    )
    .select_from(
        Stat_joueur
        .join(Joueur, Stat_joueur.c.joueur_id == Joueur.c.id)
        .join(Equipe, Joueur.c.equipe_id == Equipe.c.id)
    )
)
# ***

if selected_team_3 != "Toutes":
    query_discipline = query_discipline.where(Equipe.c.equipe == selected_team_3)

query_discipline = query_discipline.order_by(desc(score_discipline)).limit(10)

df_discipline = run_query(query_discipline)

st.bar_chart(df_discipline.set_index("Nom_Joueur")["Score_discipline"])
st.dataframe(df_discipline, use_container_width=True)

st.download_button(
    "📥 Télécharger les données (CSV)", 
    df_discipline.to_csv(index=False), 
    "joueurs_disciplinés.csv"
)

st.markdown("---")



# ! ========================================================================================================================
st.header("4️⃣ Répartition des nationalités par équipe")

query_nat = (
    select(
        Equipe.c.equipe.label("Equipe"), 
        Joueur.c.nationalite.label("Nationalite"), 
        func.count().label('nombre_joueurs')
    )
    .select_from(
        Joueur
        .join(Equipe, Joueur.c.equipe_id == Equipe.c.id))
    .group_by(Equipe.c.equipe, Joueur.c.nationalite)
    .order_by(Equipe.c.equipe, desc('nombre_joueurs')))
df_nat = run_query(query_nat)

selected_team_4 = st.selectbox("Sélectionnez une équipe :", sorted(df_nat['Equipe'].unique()))
filtered_nat = df_nat[df_nat['Equipe'] == selected_team_4]

st.dataframe(filtered_nat, use_container_width=True)

fig, ax = plt.subplots(figsize=(6,6))
wedges, texts, autotexts = ax.pie(
    filtered_nat['nombre_joueurs'],
    labels=filtered_nat['Nationalite'],
    autopct='%1.1f%%',
    textprops={'fontsize': 5} 
)
for t in autotexts:
    t.set_fontsize(5)
ax.set_title(f"Répartition des nationalités — {selected_team_4}", fontsize=11)
st.pyplot(fig)

st.download_button("📥 Télécharger les données (CSV)", df_nat.to_csv(index=False), "repartition_nationalites.csv")

st.markdown("---")


# ! ========================================================================================================================
st.header("5️⃣ Nombre total de buts par équipe")

query_buts_equipe = (
    select(
        Equipe.c.equipe.label("Equipe"), 
        func.sum(Resultat_Match.c.buts_marques).label('total_buts_marques')
    )
    .select_from(
        Resultat_Match
        .join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id)
    )
    .group_by(Equipe.c.equipe)
    .order_by(desc('total_buts_marques'))
)

# query_buts_equipe = build_filters(query_buts_equipe, table_matches=Matche, table_equipes=Equipe)
df_buts_equipe = run_query(query_buts_equipe)

if not df_buts_equipe.empty:
    total_equipes = len(df_buts_equipe)
    items_per_page = 10

    total_pages = (total_equipes - 1) // items_per_page + 1

    selected_page = st.number_input(
        "📄 Sélectionner la page :", 
        min_value=1, 
        max_value=total_pages, 
        value=1, 
        step=1
    )

    start_idx = (selected_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    df_page = df_buts_equipe.iloc[start_idx:end_idx]

    st.dataframe(df_page, use_container_width=True)
    st.bar_chart(df_page.set_index("Equipe"))


    st.caption(f"📊 Page {selected_page}/{total_pages} – Affichage de {len(df_page)} équipes sur {total_equipes}")
else:
    st.warning("Aucune donnée ne correspond aux critères sélectionnés.")

st.download_button(
    "📥 Télécharger les données (CSV)", 
    df_buts_equipe.to_csv(index=False), 
    "buts_par_equipe.csv"
)

st.markdown("---")



import streamlit as st
from sqlalchemy import select, func, desc

# ! ========================================================================================================================
st.header("6️⃣ Moyenne de buts marqués et encaissés par match — Mesurer l’efficacité et la défense moyenne des équipes.")

query_classement = (
    select(
        Equipe.c.equipe.label("Equipe"), 
        func.round(func.avg(Resultat_Match.c.buts_marques), 2).label('moyenne_buts_marques'),
        func.round(func.avg(Resultat_Match.c.buts_concedes), 2).label('moyenne_buts_concedes'),
        func.count(Resultat_Match.c.id).label('nombre_matches')
    )
    .select_from(
        Resultat_Match
        .join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id)
    )
    .group_by(Equipe.c.equipe)
    .order_by(desc('moyenne_buts_marques'))
)

df_classement = run_query(query_classement)

if not df_classement.empty:
    total_equipes = len(df_classement)
    items_per_page = 10
    total_pages = (total_equipes - 1) // items_per_page + 1

    selected_page = st.number_input(
        "📄 Page :", 
        min_value=1, 
        max_value=total_pages, 
        value=1, 
        step=1
    )

    start_idx = (selected_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    df_page = df_classement.iloc[start_idx:end_idx]

    st.dataframe(df_page, use_container_width=True)
    st.bar_chart(df_page.set_index("Equipe")[["moyenne_buts_marques", "moyenne_buts_concedes"]])

    st.caption(f"📊 Page {selected_page}/{total_pages} — Affichage de {len(df_page)} équipes sur {total_equipes}")
else:
    st.warning("Aucune donnée ne correspond aux critères sélectionnés.")

st.download_button(
    "📥 Télécharger les données (CSV)", 
    df_classement.to_csv(index=False), 
    "classement_equipes.csv"
)

st.markdown("---")


# ! ========================================================================================================================
# ! ========================================================================================================================
st.header("7️⃣ Classement des équipes (3 pts victoire, 1 pt nul)")

victoires = func.sum(case((Resultat_Match.c.resultat == 'Victoire', 1), else_=0)).label('victoires')
nuls = func.sum(case((Resultat_Match.c.resultat == 'Nul', 1), else_=0)).label('nuls')
defaites = func.sum(case((Resultat_Match.c.resultat == 'Défaite', 1), else_=0)).label('defaites')
points = func.sum(case((Resultat_Match.c.resultat == 'Victoire', 3),
                      (Resultat_Match.c.resultat == 'Nul', 1),
                      else_=0)).label('points')
difference_buts = (func.sum(Resultat_Match.c.buts_marques) - func.sum(Resultat_Match.c.buts_concedes)).label('difference_buts')

query_q7 = (
    select(
        Equipe.c.equipe.label("Equipe"),
        func.count().label('Matches Joués'),
        victoires.label("Victoires"),
        nuls.label("Nuls"),
        defaites.label("Défaites"),
        func.sum(Resultat_Match.c.buts_marques).label('Buts Pour'),
        func.sum(Resultat_Match.c.buts_concedes).label('Buts Contre'),
        difference_buts.label("Différence"),
        points.label("Points")
    )
    .select_from(Resultat_Match.join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id))
    .group_by(Equipe.c.equipe)
    .order_by(desc(points), desc(difference_buts))
)

result_q7 = run_query(query_q7)

st.markdown("### ⚙️ Filtres de classement")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    page_size = st.selectbox("Afficher par page :", [5, 10, 15, 20], index=1)

with col2:
    tri_colonne = st.selectbox("Trier par :", result_q7.columns, index=list(result_q7.columns).index("Points"))

with col3:
    ordre = st.radio("Ordre :", ["⬇️ Décroissant", "⬆️ Croissant"], horizontal=True)

with col4:
    search = st.text_input("🔍 Rechercher une équipe :", "")


filtered_df = result_q7[result_q7["Equipe"].str.contains(search, case=False, na=False)] if search else result_q7

sorted_df = filtered_df.sort_values(by=tri_colonne, ascending=(ordre == "⬆️ Croissant"))

num_pages = (len(sorted_df) - 1) // page_size + 1
page = st.number_input("Page :", min_value=1, max_value=max(1, num_pages), step=1)

start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
paged_df = sorted_df.iloc[start_idx:end_idx]

st.subheader("🏆 Classement général des équipes")
st.dataframe(paged_df, use_container_width=True)

st.subheader("📈 Visualisation du classement (par points)")
st.bar_chart(paged_df.set_index("Equipe")["Points"])

csv = result_q7.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger toutes les données (CSV)",
    data=csv,
    file_name='classement_equipes.csv',
    mime='text/csv'
)

st.markdown("---")


# ! ========================================================================================================================
st.header("8️⃣ Équipes avec la meilleure défense (par buts concédés)")

query_q8 = (
    select(
        Equipe.c.equipe.label("Equipe"),
        func.sum(Resultat_Match.c.buts_concedes).label('Total_Buts_Concedes'),
        func.count(Resultat_Match.c.id).label('Nombre_Matches'),
        func.round(func.avg(Resultat_Match.c.buts_concedes), 2).label('Moyenne_Buts_Concedes_Match')
    )
    .select_from(
        Resultat_Match.join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id)
    )
    .group_by(Equipe.c.equipe)
    .order_by(asc('Total_Buts_Concedes'))
)

result_q8 = run_query(query_q8)

st.markdown("### ⚙️ Filtres d’affichage")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    page_size = st.selectbox("Afficher par page :", [5, 10, 15, 20], index=1, key="page_size_q8")

with col2:
    tri_colonne = st.selectbox("Trier par :", result_q8.columns, index=list(result_q8.columns).index("Total_Buts_Concedes"), key="tri_q8")

with col3:
    ordre = st.radio("Ordre :", ["⬆️ Croissant", "⬇️ Décroissant"], horizontal=True, key="ordre_q8")

with col4:
    search = st.text_input("🔍 Rechercher une équipe :", "", key="search_q8")


filtered_df = result_q8[result_q8["Equipe"].str.contains(search, case=False, na=False)] if search else result_q8

sorted_df = filtered_df.sort_values(by=tri_colonne, ascending=(ordre == "⬆️ Croissant"))

num_pages = (len(sorted_df) - 1) // page_size + 1
page = st.number_input("Page :", min_value=1, max_value=max(1, num_pages), step=1, key="num_input_8")

start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
paged_df = sorted_df.iloc[start_idx:end_idx]

st.subheader("Classement général des équipes avec la meilleure défense 🥇")
st.dataframe(paged_df, use_container_width=True)

st.subheader("Visualisation du classement (buts concédés moyens)")
st.bar_chart(paged_df.set_index("Equipe")["Moyenne_Buts_Concedes_Match"])

csv = result_q8.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger le classement complet (CSV)",
    data=csv,
    file_name='classement_equipes_meilleure_defense.csv',
    mime='text/csv'
)

st.markdown("---")


# ! ========================================================================================================================
st.header("9️⃣ Meilleurs buteurs par équipe — Identifier le meilleur buteur dans chaque formation.")

# =====================================================================
subquery = (
    select(
        Joueur.c.nom_joueur,
        Equipe.c.equipe,
        Equipe.c.id.label('equipe_id'),
        Stat_joueur.c.buts,
        Stat_joueur.c.passes_decisives,
        (Stat_joueur.c.buts + Stat_joueur.c.passes_decisives).label('total_contributions'),
        func.row_number().over(
            partition_by=Equipe.c.id,
            order_by=[desc(Stat_joueur.c.buts), desc(Stat_joueur.c.passes_decisives)]
        ).label('rang')
    )
    .select_from(
        Stat_joueur
        .join(Joueur, Stat_joueur.c.joueur_id == Joueur.c.id)
        .join(Equipe, Joueur.c.equipe_id == Equipe.c.id)
    )
    .where(Stat_joueur.c.buts > 0)
    .cte('classement_buteurs')
)

# =====================================================================
query_q9 = (
    select(
        subquery.c.nom_joueur.label("Nom_Joueur"),
        subquery.c.equipe.label("Equipe"),
        subquery.c.buts.label("Buts"),
        subquery.c.passes_decisives.label("Passes_Decisives"),
        subquery.c.total_contributions.label("Total_Contributions")
    )
    .where(subquery.c.rang == 1)
    .order_by(desc(subquery.c.buts), desc(subquery.c.total_contributions))
)

# =====================================================================
result_q9 = run_query(query_q9)

# =====================================================================
st.markdown("### ⚙️ Filtres d’affichage")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    page_size = st.selectbox("Afficher par page :", [5, 10, 15, 20], index=1, key="page_size_q9")

with col2:
    tri_colonne = st.selectbox("Trier par :", result_q9.columns, index=list(result_q9.columns).index("Buts"), key="tri_q9")

with col3:
    ordre = st.radio("Ordre :", ["⬆️ Croissant", "⬇️ Décroissant"], horizontal=True, key="ordre_q9")

with col4:
    search = st.text_input("🔍 Rechercher un joueur ou une équipe :", "", key="search_q9")

# =====================================================================

filtered_df = result_q9[
    result_q9["Nom_Joueur"].str.contains(search, case=False, na=False) |
    result_q9["Equipe"].str.contains(search, case=False, na=False)
] if search else result_q9

# Tri
sorted_df = filtered_df.sort_values(by=tri_colonne, ascending=(ordre == "⬆️ Croissant"))

# Pagination
num_pages = (len(sorted_df) - 1) // page_size + 1
page = st.number_input("Page :", min_value=1, max_value=max(1, num_pages), step=1, key="page_q9")
start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
paged_df = sorted_df.iloc[start_idx:end_idx]

# =====================================================================
st.subheader("🏆 Meilleurs buteurs par équipe")
st.dataframe(paged_df, use_container_width=True)

st.subheader("🎯 Visualisation des contributions (buts + passes)")
st.bar_chart(paged_df.set_index("Nom_Joueur")["Total_Contributions"])

# =====================================================================
csv = result_q9.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger le classement (CSV)",
    data=csv,
    file_name='meilleurs_buteurs_par_equipe.csv',
    mime='text/csv'
)

st.markdown("---")



# ! ========================================================================================================================
st.header("🔟 Nombre total de matchs joués par équipe — Comptabiliser les participations de chaque équipe au cours de la saison")

# =====================================================================
query_q10 = (
    select(
        Equipe.c.equipe.label("Equipe"),
        func.count(Resultat_Match.c.id).label("Total_Matchs_Joues"),
        func.count(func.distinct(Resultat_Match.c.matche_id)).label("Matchs_Uniques"),
        func.sum(case((Resultat_Match.c.resultat == "Victoire", 1), else_=0)).label("Victoires"),
        func.sum(case((Resultat_Match.c.resultat == "Nul", 1), else_=0)).label("Nuls"),
        func.sum(case((Resultat_Match.c.resultat == "Défaite", 1), else_=0)).label("Défaites"),
    )
    .select_from(Resultat_Match.join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id))
    .group_by(Equipe.c.equipe)
    .order_by(desc("Total_Matchs_Joues"), desc("Victoires"))
)

# =====================================================================
result_q10 = run_query(query_q10)

# =====================================================================
st.markdown("### ⚙️ Filtres d’affichage")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    page_size = st.selectbox("Afficher par page :", [5, 10, 15, 20], index=1, key="page_size_q10")

with col2:
    tri_colonne = st.selectbox("Trier par :", result_q10.columns, index=list(result_q10.columns).index("Total_Matchs_Joues"), key="tri_q10")

with col3:
    ordre = st.radio("Ordre :", ["⬆️ Croissant", "⬇️ Décroissant"], horizontal=True, key="ordre_q10")

with col4:
    search = st.text_input("🔍 Rechercher une équipe :", "", key="search_q10")

# =====================================================================

if search:
    filtered_df = result_q10[result_q10["Equipe"].str.contains(search, case=False, na=False)]
else:
    filtered_df = result_q10

sorted_df = filtered_df.sort_values(by=tri_colonne, ascending=(ordre == "⬆️ Croissant"))

# 📄 Pagination
num_pages = max(1, (len(sorted_df) - 1) // page_size + 1)
page = st.number_input("Page :", min_value=1, max_value=num_pages, step=1, key="page_q10")
start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
paged_df = sorted_df.iloc[start_idx:end_idx]

# =====================================================================
st.subheader("📋 Nombre total de matchs joués par équipe")
st.dataframe(paged_df, use_container_width=True)

st.subheader("📈 Visualisation du total de matchs par équipe")
st.bar_chart(paged_df.set_index("Equipe")["Total_Matchs_Joues"])

# =====================================================================
csv = result_q10.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Télécharger les statistiques (CSV)",
    data=csv,
    file_name="nombre_total_matchs_par_equipe.csv",
    mime="text/csv",
)

st.markdown("---")


# =====================================================================

st.success("✅ Analyses terminées.")
