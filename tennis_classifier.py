# Installer les dépendances (déjà fait)
!pip install streamlit pandas

# Écrire le fichier avec encodage simple
%%writefile tennis_classifier.py
import streamlit as st
import pandas as pd
from io import StringIO

st.title("Tennis Straight/Decider Sets Classifier")

st.write("Collez vos données de matchs ci-dessous (colonnes : Date, Tournoi, Surface, Score, etc.)")

# Upload ou collage de données
uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'])
data_text = st.text_area("Ou coller directement vos données CSV", height=200)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
elif data_text:
    try:
        data = pd.read_csv(StringIO(data_text))
    except:
        st.error("Erreur de format CSV. Vérifiez vos données.")
        st.stop()
else:
    st.stop()

# Trouver la colonne score
score_cols = [col for col in data.columns if any(word in col.lower() for word in ['score', 'resultat', 'result', 'résultat'])]
if score_cols:
    score_col = score_cols[0]
    st.success(f"Colonne score détectée : {score_col}")
else:
    st.error("Colonne 'score' ou 'résultat' non trouvée. Vérifiez vos données.")
    st.stop()

# Classifier simple
def classify_straight_decider(score_str):
    if pd.isna(score_str):
        return -1
    score_str = str(score_str).upper().strip()
    
    # Détecter straight sets
    if '2-0' in score_str or '3-0' in score_str or any(f'6-{i}' in score_str for i in ['0','1','2','3','4']):
        return 0
    
    # Détecter decider sets
    if '2-1' in score_str or '3-1' in score_str or '3-2' in score_str:
        return 1
    
    return -1

# Appliquer la classification
data['Straight_Decider'] = data[score_col].apply(classify_straight_decider)

# Afficher les résultats
st.subheader("Résultats de Classification")
display_cols = [score_col, 'Straight_Decider']
st.dataframe(data[display_cols], use_container_width=True)

# Statistiques
st.subheader("Statistiques")
col1, col2, col3, col4 = st.columns(4)
total = len(data)
straight = len(data[data['Straight_Decider'] == 0])
decider = len(data[data['Straight_Decider'] == 1])
unknown = len(data[data['Straight_Decider'] == -1])

with col1:
    st.metric("Total Matchs", total)
with col2:
    percent_straight = (straight/total*100) if total > 0 else 0
    st.metric("Straight Sets", straight, f"{percent_straight:.1f}%")
with col3:
    percent_decider = (decider/total*100) if total > 0 else 0
    st.metric("Decider Sets", decider, f"{percent_decider:.1f}%")
with col4:
    percent_unknown = (unknown/total*100) if total > 0 else 0
    st.metric("Inconnus", unknown, f"{percent_unknown:.1f}%")

# Colonne à copier
st.subheader("Colonne à Copier-Coller dans Excel")
st.write("Copiez cette colonne (0 = Straight, 1 = Decider, -1 = Inconnu) :")

# Filtrer les inconnus pour la copie
copy_data = data[data['Straight_Decider'] != -1]['Straight_Decider'].astype(str)
if len(copy_data) > 0:
    st.text_area("Colonne à copier :", "\n".join(copy_data), height=200, key="copy_area")
else:
    st.warning("Aucun match classifiable trouvé.")

# Téléchargement
csv_data = data[display_cols].to_csv(index=False)
st.download_button("Télécharger CSV", csv_data, "tennis_results.csv", "text/csv")

# Instructions simples
st.info("""
**Instructions :**
1. Collez vos données CSV dans la zone de texte
2. Vérifiez que la colonne score est détectée correctement
3. Copiez la colonne "Straight_Decider" dans votre Excel
4. 0 = Straight Sets, 1 = Decider Sets
""")