import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

st.set_page_config(page_title="LP Skladová Evidence", layout="wide")

# --- NASTAVENÍ API ---
API_KEY = "AIzaSyBGEFTjQGFBHmLFDxrHKw-XaJW5guSUCJs"
genai.configure(api_key=API_KEY)

st.title("🎵 LP Sklad & Skener")

tab1, tab2 = st.tabs(["📥 Naskladnění z PDF", "📦 Aktuální Sklad & Skener"])

with tab1:
    st.header("Nahrát fakturu")
    uploaded_file = st.file_uploader("Vyberte PDF fakturu", type="pdf")
    
    if uploaded_file:
        if st.button("Zpracovat fakturu"):
            with st.spinner("AI čte fakturu..."):
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                content = uploaded_file.read()
                response = model.generate_content([
                    "Vrať CSV tabulku (středník): EAN;Interpret;Titul;Mnozstvi;Cena_s_DPH",
                    {"mime_type": "application/pdf", "data": content}
                ])
                
                csv_data = response.text.replace('```csv', '').replace('```', '').strip()
                df = pd.read_csv(io.StringIO(csv_data), sep=';')
                st.session_state['sklad_priprava'] = df
                st.success("Faktura načtena!")
                st.dataframe(df)

with tab2:
    st.header("Fyzické naskladnění / Prodej")
    ean_input = st.text_input("NAČTI EAN SKENEREM (nebo napiš)", key="ean_scanner")
    
    if ean_input:
        st.info(f"Hledám v databázi EAN: {ean_input}")
        # Zde později dopíšeme logiku pro porovnání s objednávkami
        st.warning("Titul nalezen v objednávce č. 456! Nepouštět na sklad.")
