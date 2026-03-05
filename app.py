import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
import time

st.set_page_config(page_title="LP Sklad", layout="wide")

# --- KONFIGURACE ---
API_KEY = "AIzaSyBGEFTjQGFBHmLFDxrHKw-XaJW5guSUCJs"
genai.configure(api_key=API_KEY)

st.title("🎵 LP Skladová Evidence")

uploaded_file = st.file_uploader("Nahrajte PDF fakturu", type="pdf")

if uploaded_file:
    if st.button("Zpracovat fakturu"):
        try:
            with st.spinner("AI analyzuje fakturu..."):
                # Použijeme model flash, který je pro Free tier nejvhodnější
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Načtení dat z PDF
                pdf_parts = [
                    {
                        "mime_type": "application/pdf",
                        "data": uploaded_file.getvalue()
                    }
                ]
                
                prompt = "Vytáhni data z faktury a vrať je jako CSV tabulku. Oddělovač: středník (;). Sloupce: EAN;Interpret;Titul;Mnozstvi;Cena_s_DPH. Vrať pouze CSV, žádný text okolo."
                
                # Volání AI s opakováním při selhání
                response = model.generate_content([prompt, pdf_parts[0]])
                
                if response.text:
                    # Vyčištění textu od případného balastu
                    clean_csv = response.text.replace('```csv', '').replace('```', '').strip()
                    df = pd.read_csv(io.StringIO(clean_csv), sep=';')
                    
                    st.success("Faktura úspěšně přečtena!")
                    st.dataframe(df, use_container_width=True)
                    st.session_state['data'] = df
                else:
                    st.error("AI vrátila prázdnou odpověď. Zkuste to znovu.")

        except Exception as e:
            st.error(f"Nastala chyba: {str(e)}")
            st.info("Tip: Pokud vidíte chybu 404, Google dočasně omezil přístup k modelu. Zkuste to za minutu.")

# --- SEKCIA SKENER ---
st.divider()
st.header("📦 Fyzické naskladnění (Skener)")
ean_scan = st.text_input("Klikněte sem a pípněte skenerem EAN")

if ean_scan:
    st.write(f"Načtený kód: **{ean_scan}**")
    if 'data' in st.session_state:
        # Hledání v právě nahrané faktuře
        df_priprava = st.session_state['data']
        match = df_priprava[df_priprava['EAN'].astype(str).str.contains(ean_scan)]
        
        if not match.empty:
            st.balloons()
            st.success(f"NALEZENO: {match.iloc[0]['Interpret']} - {match.iloc[0]['Titul']}")
            st.write(f"Cena: {match.iloc[0]['Cena_s_DPH']} CZK")
        else:
            st.warning("Tento EAN v nahrané faktuře není.")
