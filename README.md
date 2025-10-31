# ⚽ Football Data Analysis — Premier League 2024–2025

## 🎯 Objectif
Développer une solution d’analyse prédictive complète pour le football professionnel, capable d’exploiter les données de la Premier League afin d’anticiper les résultats et d’optimiser les stratégies des équipes.

---

## 🧩 Étapes du projet

### 1️⃣ Web Scraping
- Extraction des données depuis **FBref** avec **Selenium**.
- Collecte des informations sur les **équipes**, **joueurs** et **matchs**.
- Export des données au format **CSV**.

### 2️⃣ Transformation des données
- Nettoyage, standardisation et mise en cohérence des données.
- Structuration selon un **modèle relationnel PostgreSQL**.

### 3️⃣ Modélisation de la base
Tables principales :  
- `competition`  
- `saison`  
- `equipe`  
- `joueur`  
- `match`  
- `resultatmatch`  
- `statistiquejoueur`  

### 4️⃣ Analyse des données
Requêtes SQL pour :  
- 🔝 Top buteurs & joueurs décisifs  
- 🟥 Discipline (cartons jaunes et rouges)  
- ⚽ Puissance offensive & défensive  
- 🏆 Classement des équipes  
- 📊 Statistiques globales et comparatives  

### 5️⃣ Dashboard interactif (Streamlit)
- Connexion à la base via **SQLAlchemy**  
- Visualisations interactives (bar charts, tableaux filtrables)  
- Téléchargement des résultats au format **CSV**

---

## 🛠️ Stack technique
- **Python**, **Selenium**, **Pandas**, **SQLAlchemy**, **Streamlit**  
- **PostgreSQL** pour le stockage des données  

---

## 🚀 Installation et exécution

### 1️⃣ Cloner le projet
Ouvrez un terminal et exécutez la commande suivante :

```bash
git clone https://github.com/bouchramilo/FootData_Analytics_Modeling.git
cd FootData_Analytics_Modeling
```

---

## ⚽ Lancer le dashboard Streamlit

```bash
streamlit run main.py
```
