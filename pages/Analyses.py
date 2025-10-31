# ============================================================
# 🎯 IMPORTS
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy import create_engine, MetaData,Table, Column, Integer, String, ForeignKey, DateTime, Date, Time, Numeric, Text, insert, Float, Enum, case, select, desc, func
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
# st.code("""
#             SELECT 
#                 j.nom_joueur,
#                 e.equipe,
#                 sj.buts
#             FROM statistiques_joueurs sj
#             JOIN joueurs j ON sj.joueur_id = j.id
#             JOIN equipes e ON j.equipe_id = e.id
#             ORDER BY sj.buts DESC
#             LIMIT 10;
#     """, "sql")

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
    .order_by(desc(Stat_joueur.c.buts))
    .limit(10)
)
df_buteurs = run_query(query_buteurs)
st.bar_chart(df_buteurs.set_index("Nom_Joueur")["nb_Buts"])

st.dataframe(df_buteurs, use_container_width=True)
# fig, ax = plt.subplots(figsize=(8,4))
# sns.barplot(x="nb_Buts", y="Nom_Joueur", data=df_buteurs, ax=ax)
# ax.set_title("Top 10 des meilleurs buteurs")
# st.pyplot(fig)
st.download_button("📥 Télécharger les données (CSV)", df_buteurs.to_csv(index=False), "top_buteurs.csv")

st.markdown("---")


# ! ========================================================================================================================
st.header("2️⃣ Joueurs les plus décisifs (buts + passes)")
# st.code("""
#             SELECT 
#                 j.nom_joueur,
#                 e.equipe,
#                 sj.buts,
#                 sj.passes_decisives,
#                 (sj.buts + sj.passes_decisives) as total_contributions
#             FROM statistiques_joueurs sj
#             JOIN joueurs j ON sj.joueur_id = j.id
#             JOIN equipes e ON j.equipe_id = e.id
#             ORDER BY total_contributions DESC
#             LIMIT 10;
#         """, "sql")
total_buts_passes = (Stat_joueur.c.buts + Stat_joueur.c.passes_decisives).label("total_buts_passes")

query_decisifs = (
    select(
        Joueur.c.nom_joueur.label("Nom_Joueur"), 
        Equipe.c.equipe.label("Equipe"), 
        Stat_joueur.c.buts.label("Buts"), 
        Stat_joueur.c.passes_decisives.label("Passes_decisives"), 
        total_buts_passes.label("Total_Buts_Passes")
    )
    .select_from(
        Stat_joueur
        .join(Joueur, Stat_joueur.c.joueur_id == Joueur.c.id)
        .join(Equipe, Joueur.c.equipe_id == Equipe.c.id))
    .order_by(desc(total_buts_passes))
    .limit(10)
) 
df_decisifs = run_query(query_decisifs)

st.dataframe(df_decisifs, use_container_width=True)
st.bar_chart(df_decisifs.set_index("Nom_Joueur")["Total_Buts_Passes"])


# fig, ax = plt.subplots(figsize=(8,4))
# sns.barplot(x="Total_Buts_Passes", y="Nom_Joueur", data=df_decisifs, ax=ax)
# ax.set_title("Top 10 des joueurs les plus décisifs")
# st.pyplot(fig)
st.download_button("📥 Télécharger les données (CSV)", df_decisifs.to_csv(index=False), "joueurs_decisifs.csv")

st.markdown("---")


# ! ========================================================================================================================
st.header("3️⃣ Joueurs les plus disciplinés (cartons)")

# st.code("""
#             SELECT 
#                 j.nom_joueur,
#                 e.equipe,
#                 sj.cartons_jaunes,
#                 sj.cartons_rouges,
#                 (sj.cartons_jaunes + sj.cartons_rouges) as score_discipline
#             FROM statistiques_joueurs sj
#             JOIN joueurs j ON sj.joueur_id = j.id
#             JOIN equipes e ON j.equipe_id = e.id
#             ORDER BY score_discipline DESC
#             LIMIT 10;
#         """, "sql")

score_discipline = (Stat_joueur.c.cartons_jaunes + Stat_joueur.c.cartons_rouges).label('score_discipline')

query_discipline = (
    select(
        Joueur.c.nom_joueur.label("Nom_Joueur"), 
        Equipe.c.equipe.label("Equipe"), 
        Stat_joueur.c.cartons_jaunes.label("Cartons_jaunes"), 
        Stat_joueur.c.cartons_rouges.label("Cartons_rouges"), 
        score_discipline.label("Score_discipline")
    )
    .select_from(
        Stat_joueur
            .join(Joueur, Stat_joueur.c.joueur_id == Joueur.c.id)
            .join(Equipe, Joueur.c.equipe_id == Equipe.c.id))
    .order_by(desc(score_discipline))
    .limit(10)
)

df_discipline = run_query(query_discipline)

st.dataframe(df_discipline, use_container_width=True)
st.bar_chart(df_discipline.set_index("Nom_Joueur")["Score_discipline"])
# fig, ax = plt.subplots(figsize=(8,4))
# sns.barplot(x="Score_discipline", y="Nom_Joueur", data=df_discipline, ax=ax)
# ax.set_title("Joueurs les plus sanctionnés")
# st.pyplot(fig)

st.download_button("📥 Télécharger les données (CSV)", df_discipline.to_csv(index=False), "joueurs_disciplinés.csv")

st.markdown("---")


# ! ========================================================================================================================
st.header("4️⃣ Répartition des nationalités par équipe")
# st.code("""
#             SELECT 
#                 e.equipe,
#                 j.nationalite,
#                 COUNT(*) as nombre_joueurs
#             FROM joueurs j
#             JOIN equipes e ON j.equipe_id = e.id
#             GROUP BY e.equipe, j.nationalite
#             ORDER BY e.equipe, nombre_joueurs DESC;
#         """, "sql")
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

selected_team = st.selectbox("Sélectionnez une équipe :", sorted(df_nat['Equipe'].unique()))
filtered_nat = df_nat[df_nat['Equipe'] == selected_team]

st.dataframe(filtered_nat, use_container_width=True)

fig, ax = plt.subplots(figsize=(6,6))
ax.pie(filtered_nat['nombre_joueurs'], labels=filtered_nat['Nationalite'], autopct='%1.1f%%')
ax.set_title(f"Répartition des nationalités — {selected_team}")
st.pyplot(fig)

st.download_button("📥 Télécharger les données (CSV)", df_nat.to_csv(index=False), "repartition_nationalites.csv")

st.markdown("---")


# ! ========================================================================================================================
st.header("5️⃣ Nombre total de buts par équipe")
# st.code("""
#             SELECT 
#                 e.equipe,
#                 SUM(rm.buts_marques) as total_buts_marques
#             FROM resultat_matchs rm
#             JOIN equipes e ON rm.equipe_id = e.id
#             GROUP BY e.equipe
#             ORDER BY total_buts_marques DESC;
#         """, "sql")
query_buts_equipe = (
    select(
        Equipe.c.equipe.label("Equipe"), 
        func.sum(Resultat_Match.c.buts_marques).label('total_buts_marques')
    )
    .select_from(
        Resultat_Match
        .join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id))
    .group_by(Equipe.c.equipe)
    .order_by(desc('total_buts_marques'))
)
df_buts_equipe = run_query(query_buts_equipe)

st.dataframe(df_buts_equipe, use_container_width=True)

st.bar_chart(df_buts_equipe.set_index("Equipe"))

st.download_button("📥 Télécharger les données (CSV)", df_buts_equipe.to_csv(index=False), "buts_par_equipe.csv")

st.markdown("---")


# ! ========================================================================================================================
st.header("6️⃣ Moyenne de buts marqués et encaissés par match — Mesurer l’efficacité et la défense moyenne des équipes.")
# st.code("""
#             SELECT 
#                 e.equipe,
#                 ROUND(AVG(rm.buts_marques)::numeric, 2) as moyenne_buts_marques,
#                 ROUND(AVG(rm.buts_concedes)::numeric, 2) as moyenne_buts_concedes,
#                 COUNT(rm.id) as nombre_matches
#             FROM resultat_matchs rm
#             JOIN equipes e ON rm.equipe_id = e.id
#             GROUP BY e.equipe
#             ORDER BY moyenne_buts_marques DESC;
#         """, "sql")
query_classement = (
    select(
        Equipe.c.equipe.label("Equipe"), 
        func.round(func.avg(Resultat_Match.c.buts_marques), 2).label('moyenne_buts_marques'),
        func.round(func.avg(Resultat_Match.c.buts_concedes), 2).label('moyenne_buts_concedes'),
        func.count(Resultat_Match.c.id).label('nombre_matches'))
    .select_from(
        Resultat_Match
        .join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id))
    .group_by(Equipe.c.equipe)
    .order_by(desc('moyenne_buts_marques'))
)
df_classement = run_query(query_classement)

st.dataframe(df_classement, use_container_width=True)
st.bar_chart(df_classement.set_index("Equipe"))

st.download_button("📥 Télécharger les données (CSV)", df_classement.to_csv(index=False), "classement_equipes.csv")

st.markdown("---")

# ! ========================================================================================================================
st.header("7️⃣ Classement des équipes (3 pts victoire, 1 pt nul)")
# st.code("""
#             SELECT 
#                 e.equipe,
#                 COUNT(*) as matches_joues,
#                 SUM(CASE WHEN rm.resultat = 'Victoire' THEN 1 ELSE 0 END) as victoires,
#                 SUM(CASE WHEN rm.resultat = 'Nul' THEN 1 ELSE 0 END) as nuls,
#                 SUM(CASE WHEN rm.resultat = 'Défaite' THEN 1 ELSE 0 END) as defaites,
#                 SUM(rm.buts_marques) as buts_pour,
#                 SUM(rm.buts_concedes) as buts_contre,
#                 (SUM(rm.buts_marques) - SUM(rm.buts_concedes)) as difference_buts,
#                 SUM(CASE 
#                     WHEN rm.resultat = 'Victoire' THEN 3 
#                     WHEN rm.resultat = 'Nul' THEN 1 
#                     ELSE 0 
#                 END) as points
#             FROM resultat_matchs rm
#             JOIN equipes e ON rm.equipe_id = e.id
#             GROUP BY e.equipe
#             ORDER BY points DESC, difference_buts DESC;
#     """, "sql")



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
              func.count().label('matches_joues'),
              victoires.label("Win"),
              nuls.label("Nuls"),
              defaites.label("Loss"),
              func.sum(Resultat_Match.c.buts_marques).label('buts_pour'),
              func.sum(Resultat_Match.c.buts_concedes).label('buts_contre'),
              difference_buts.label("difference_buts"),
              points.label("points")
       )
       .select_from(
              Resultat_Match
              .join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id)
       )
       .group_by(Equipe.c.equipe)
       .order_by(desc(points), desc(difference_buts)))


result_q7 = run_query(query_q7)

st.subheader("Classement général des équipes 🥇")
st.dataframe(result_q7, use_container_width=True)

st.subheader("Visualisation du classement (par points)")
st.bar_chart(result_q7.set_index("Equipe")["points"])

csv = result_q7.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger les données (CSV)",
    data=csv,
    file_name='classement_equipes.csv',
    mime='text/csv'
)


st.markdown("---")

# ! ========================================================================================================================
st.header("8️⃣ Équipes avec la meilleure défense (par buts concédés)")
# st.code("""
#             SELECT 
#                 e.equipe,
#                 SUM(rm.buts_concedes) as total_buts_concedes,
#                 COUNT(rm.id) as nombre_matches,
#                 ROUND(AVG(rm.buts_concedes)::numeric, 2) as moyenne_buts_concedes_par_match
#             FROM resultat_matchs rm
#             JOIN equipes e ON rm.equipe_id = e.id
#             GROUP BY e.equipe
#             ORDER BY total_buts_concedes ASC;
#     """, "sql")


from sqlalchemy import select, func

query_q8 = (
    select(
        Equipe.c.equipe.label("Equipe"),
        func.sum(Resultat_Match.c.buts_concedes).label('total_buts_concedes'),
        func.count(Resultat_Match.c.id).label('nombre_matches'),
        func.round(func.avg(Resultat_Match.c.buts_concedes), 2).label('moyenne_buts_concedes_par_match')
    )
    .select_from(
        Resultat_Match
        .join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id)
    )
    .group_by(Equipe.c.equipe)
    .order_by('total_buts_concedes')
)


result_q8 = run_query(query_q8)

st.subheader("Classement général des équipes avec la meilleure défense 🥇")
st.dataframe(result_q8, use_container_width=True)

st.subheader("Visualisation du classement des équipes avec la meilleure défense (par buts concédés)")
st.bar_chart(result_q8.set_index("Equipe")["moyenne_buts_concedes_par_match"])

csv = result_q8.to_csv(index=False).encode('utf-8')



st.download_button(
    label="📥 Télécharger le classement en CSV",
    data=csv,
    file_name='classement_equipes_la_meilleure_defense.csv',
    mime='text/csv'
)

st.markdown("---")



# ! ========================================================================================================================
st.header("9️⃣ Meilleurs buteurs par équipe — Identifier le meilleur buteur dans chaque formation.")
# st.code("""
#             WITH classement_buteurs AS (
#                 SELECT 
#                     j.nom_joueur,
#                     e.equipe,
#                     sj.buts,
#                     sj.passes_decisives,
#                     (sj.buts + sj.passes_decisives) as total_contributions,
#                     ROW_NUMBER() OVER (PARTITION BY e.id ORDER BY sj.buts DESC, sj.passes_decisives DESC) as rang
#                 FROM statistiques_joueurs sj
#                 JOIN joueurs j ON sj.joueur_id = j.id
#                 JOIN equipes e ON j.equipe_id = e.id
#                 WHERE sj.buts > 0
#             )
#             SELECT 
#                 nom_joueur, 
#                 equipe, 
#                 buts,
#                 passes_decisives,
#                 total_contributions
#             FROM classement_buteurs
#             WHERE rang = 1
#             ORDER BY buts DESC, total_contributions DESC;
#     """, "sql")



# Méthode avec sous-requête fenêtrée
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

query_q9 = (
    select(
        subquery.c.nom_joueur.label("Nom_joueur"),
        subquery.c.equipe.label("Equipe"),
        subquery.c.buts.label("Buts"),
        subquery.c.passes_decisives.label("Passes_decisives"),
        subquery.c.total_contributions.label("total_contributions")
    )
    .where(subquery.c.rang == 1)
    .order_by(desc(subquery.c.buts), desc(subquery.c.total_contributions))
)

result_q9 = run_query(query_q9)

st.subheader("Classement général des équipes avec la meilleure défense 🥇")
st.dataframe(result_q9, use_container_width=True)

st.subheader("Visualisation du classement des équipes avec la meilleure défense (par buts concédés)")
st.bar_chart(result_q9.set_index("Nom_joueur")["total_contributions"])

csv = result_q9.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger le classement en CSV",
    data=csv,
    file_name='buteurs_equipes.csv',
    mime='text/csv'
)

st.markdown("---")



# !========================================================================================================================
st.header("🔟 Nombre total de matchs joués par équipe — Comptabiliser les participations de chaque équipe au cours de la saison:")
# st.code("""
#             SELECT 
#                 e.equipe,
#                 COUNT(rm.id) as total_matches_joues,
#                 COUNT(DISTINCT rm.matche_id) as matches_uniques,
#                 SUM(CASE WHEN rm.resultat = 'Victoire' THEN 1 ELSE 0 END) as victoires,
#                 SUM(CASE WHEN rm.resultat = 'Nul' THEN 1 ELSE 0 END) as nuls,
#                 SUM(CASE WHEN rm.resultat = 'Défaite' THEN 1 ELSE 0 END) as defaites
#             FROM resultat_matchs rm
#             JOIN equipes e ON rm.equipe_id = e.id
#             GROUP BY e.equipe
#             ORDER BY total_matches_joues DESC, victoires DESC;
#     """, "sql")



query_q10 = (
    select(
        Equipe.c.equipe.label("Equipe"),
        func.count(Resultat_Match.c.id).label('total_matches_joues'),
        func.count(func.distinct(Resultat_Match.c.matche_id)).label('matches_uniques'),
        func.sum(case((Resultat_Match.c.resultat == 'Victoire', 1), else_=0)).label('victoires'),
        func.sum(case((Resultat_Match.c.resultat == 'Nul', 1), else_=0)).label('nuls'),
        func.sum(case((Resultat_Match.c.resultat == 'Défaite', 1), else_=0)).label('defaites')
    )
    .select_from(
        Resultat_Match
        .join(Equipe, Resultat_Match.c.equipe_id == Equipe.c.id))
    .group_by(Equipe.c.equipe)
    .order_by(desc('total_matches_joues'), desc('victoires'))
)




result_q10 = run_query(query_q10)

st.subheader("Classement général des équipes avec la meilleure défense 🥇")
st.dataframe(result_q10, use_container_width=True)

st.subheader("Visualisation du classement des équipes avec la meilleure défense (par buts concédés)")
st.bar_chart(result_q10.set_index("Equipe")["total_matches_joues"])

csv = result_q10.to_csv(index=False).encode('utf-8')



st.download_button(
    label="📥 Télécharger le classement en CSV",
    data=csv,
    file_name='matches_equipes.csv',
    mime='text/csv'
)


st.markdown("---")

st.success("✅ Analyses terminées. Explorez les graphiques et exportez les résultats en CSV !")

