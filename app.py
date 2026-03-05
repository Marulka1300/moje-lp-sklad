import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
from pypdf import PdfReader

# --- ZÁKLADNÍ NASTAVENÍ ---
st.set_page_config(page_title="LP Skladový Systém", layout="wide", page_icon="🎵")

# Váš API klíč (z image_2f7c8b.png vidím, že je v pořádku)
API_KEY = "AIzaSyBGEFTjQGFBHmLFDxrHKw-XaJW5guSUCJs"
genai.configure(api_key=API_KEY)

st.title("🎵 LP Skladový Systém")

# Inicializace skladu v paměti
if 'sklad' not in st.session_state:
    st.session_state['sklad'] = pd.DataFrame(columns=['EAN', 'Interpret', 'Titul', 'Mnozstvi', 'Cena_s_DPH'])

tab1, tab2 = st.tabs(["📥 Naskladnění z PDF", "🔍 Skener & Databáze"])

with tab1:
    st.header("1. Nahrát fakturu")
    uploaded_file = st.file_uploader("Nahrajte PDF fakturu", type="pdf")
    
    if uploaded_file:
        if st.button("🚀 Analyzovat text faktury"):
            with st.spinner("Čtu text z PDF..."):
                try:
                    # SAMOTNÉ ČTENÍ PDF (bez posílání souboru Googlu)
                    reader = PdfReader(uploaded_file)
                    text_z_faktury = ""
                    for page in reader.pages:
                        text_z_faktury += page.extract_text() + "\n"
                    
                    # VOLÁNÍ AI (posíláme pouze text)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Z následujícího textu faktury vytáhni data o zakoupených titulech. 
                    Vrať výsledek POUZE jako CSV tabulku (středník jako oddělovač).
                    Sloupce: EAN;Interpret;Titul;Mnozstvi;Cena_s_DPH
                    Pokud text obsahuje více položek, vypiš je všechny.
                    
                    TEXT FAKTURY:
                    {text_z_faktury}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # Zpracování CSV textu na tabulku
                    csv_clean = response.text.replace('```csv', '').replace('```', '').strip()
                    df_nova = pd.read_csv(io.StringIO(csv_clean), sep=';')
                    
                    st.success("Faktura úspěšně přečtena!")
                    st.dataframe(df_nova, use_container_width=True)
                    
                    if st.button("✅ Potvrdit a uložit do skladu"):
                        st.session_state['sklad'] = pd.concat([st.session_state['sklad'], df_nova]).drop_duplicates().reset_index(drop=True)
                        st.balloons()
                        st.success("Uloženo!")
                        
                except Exception as e:
                    st.error(f"Došlo k chybě: {e}")
                    st.info("Zkuste PDF nahrát znovu nebo zkontrolujte, zda není zašifrované.")

with tab2:
    st.header("2. Vyhledávání skenerem")
    ean_input = st.text_input("Zde klikněte a pípněte EAN skenerem")
    
    if ean_input:
        # Hledání v session_state
        db = st.session_state['sklad']
        vysledek = db[db['EAN'].astype(str).str.contains(ean_input)]
        
        if not vysledek.empty:
            st.success(f"NALEZENO: {vysledek.iloc[0]['Interpret']} - {vysledek.iloc[0]['Titul']}")
            st.write(f"Množství naskladněno: {vysledek.iloc[0]['Mnozstvi']} ks")
        else:
            st.warning("Tento EAN není v naskladněné databázi.")

st.divider()
st.subheader("📊 Přehled skladu v paměti")
st.dataframe(st.session_state['sklad'], use_container_width=True)
