import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
from pypdf import PdfReader

st.set_page_config(page_title="LP Sklad", layout="wide", page_icon="🎵")

# --- API NASTAVENÍ ---
API_KEY = "AIzaSyBGEFTjQGFBHmLFDxrHKw-XaJW5guSUCJs"
genai.configure(api_key=API_KEY)

st.title("🎵 LP Skladový Systém")

if 'sklad' not in st.session_state:
    st.session_state['sklad'] = pd.DataFrame(columns=['EAN', 'Interpret', 'Titul', 'Mnozstvi', 'Cena_s_DPH'])

uploaded_file = st.file_uploader("Nahrajte PDF fakturu", type="pdf")

if uploaded_file:
    if st.button("🚀 Analyzovat fakturu"):
        with st.spinner("Čtu text z faktury..."):
            try:
                # 1. Nejdřív sami vytáhneme text z PDF
                reader = PdfReader(uploaded_file)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text()
                
                # 2. Pošleme text AI (tohle ve Free verzi neselhává jako posílání souboru)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Z následujícího textu faktury vytáhni data o deskách. 
                Vrať POUZE CSV tabulku (středník jako oddělovač). 
                Sloupce: EAN;Interpret;Titul;Mnozstvi;Cena_s_DPH.
                
                TEXT FAKTURY:
                {full_text}
                """
                
                response = model.generate_content(prompt)
                
                # 3. Zpracování výsledku
                csv_text = response.text.replace('```csv', '').replace('```', '').strip()
                df = pd.read_csv(io.StringIO(csv_text), sep=';')
                
                st.success("Faktura úspěšně analyzována!")
                st.dataframe(df, use_container_width=True)
                
                if st.button("✅ Potvrdit naskladnění"):
                    st.session_state['sklad'] = pd.concat([st.session_state['sklad'], df]).drop_duplicates().reset_index(drop=True)
                    st.success("Uloženo do paměti!")
            
            except Exception as e:
                st.error(f"Nepodařilo se zpracovat: {e}")

st.divider()
st.subheader("🔍 Skener (pípněte EAN)")
ean_input = st.text_input("Zde klikněte a pípněte skenerem")
if ean_input:
    vysledek = st.session_state['sklad'][st.session_state['sklad']['EAN'].astype(str).str.contains(ean_input)]
    if not vysledek.empty:
        st.balloons()
        st.success(f"NALEZENO: {vysledek.iloc[0]['Interpret']} - {vysledek.iloc[0]['Titul']}")
    else:
        st.warning("Tento kód v databázi není.")
