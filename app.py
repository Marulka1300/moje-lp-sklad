import streamlit as st
import pandas as pd

st.set_page_config(page_title="LP Sklad", layout="wide")

st.title("🎵 LP Skladový Systém")

# Inicializace skladu v paměti
if 'sklad' not in st.session_state:
    st.session_state['sklad'] = pd.DataFrame(columns=['EAN', 'Interpret', 'Titul', 'Mnozstvi', 'Cena'])

tab1, tab2 = st.tabs(["📥 Nahrát data (Excel/CSV)", "🔍 Skener & Databáze"])

with tab1:
    st.header("1. Nahrát naskladňovací tabulku")
    st.info("Převeďte PDF fakturu na Excel (xlsx) nebo CSV a nahrajte ji sem.")
    
    uploaded_file = st.file_uploader("Vyberte soubor", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            # Načtení podle typu souboru
            if uploaded_file.name.endswith('.csv'):
                df_new = pd.read_csv(uploaded_file, sep=None, engine='python')
            else:
                df_new = pd.read_excel(uploaded_file)
            
            st.success("Tabulka nahrána!")
            st.dataframe(df_new, use_container_width=True)
            
            if st.button("✅ Uložit do databáze pro skener"):
                st.session_state['sklad'] = pd.concat([st.session_state['sklad'], df_new]).drop_duplicates().reset_index(drop=True)
                st.success("Data připravena k pípání!")
        except Exception as e:
            st.error(f"Chyba při načítání: {e}")

with tab2:
    st.header("2. Vyhledávání skenerem")
    ean_input = st.text_input("Klikněte sem a pípněte EAN")
    
    if ean_input:
        db = st.session_state['sklad']
        # Vyhledávání (funguje i když je EAN v tabulce jako číslo nebo text)
        match = db[db.apply(lambda row: row.astype(str).str.contains(ean_input).any(), axis=1)]
        
        if not match.empty:
            st.balloons()
            st.success(f"NALEZENO: {match.iloc[0].get('Interpret', 'Neznámý')} - {match.iloc[0].get('Titul', 'Neznámý')}")
            st.write(match.iloc[0])
        else:
            st.warning("Tento kód v databázi není.")

st.divider()
st.subheader("📊 Aktuální obsah databáze")
st.dataframe(st.session_state['sklad'])
