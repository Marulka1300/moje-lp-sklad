import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="LP Sklad & Skener", layout="wide", page_icon="🎵")

# --- NASTAVENÍ GOOGLE AI ---
# Tvůj klíč je v pořádku, ponecháváme ho
API_KEY = "AIzaSyBGEFTjQGFBHmLFDxrHKw-XaJW5guSUCJs"
genai.configure(api_key=API_KEY)

# --- FUNKCE PRO VOLÁNÍ AI (Zkouší více názvů modelů) ---
def ziskej_data_z_pdf(file_bytes):
    # Seznam modelů od nejnovějšího po nejstabilnější
    zkusebni_modely = [
        'gemini-1.5-flash-8b', 
        'models/gemini-1.5-flash', 
        'gemini-1.5-flash'
    ]
    
    last_error = ""
    for model_name in zkusebni_modely:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = "Vytáhni data z faktury. Vrať POUZE CSV tabulku (středník jako oddělovač). Sloupce: EAN;Interpret;Titul;Mnozstvi;Cena_s_DPH. Žádný okecávání."
            
            response = model.generate_content([
                prompt,
                {"mime_type": "application/pdf", "data": file_bytes}
            ])
            
            # Vyčištění odpovědi od případných ```csv značek
            raw_text = response.text.replace('```csv', '').replace('```', '').strip()
            df = pd.read_csv(io.StringIO(raw_text), sep=';')
            return df, model_name
        except Exception as e:
            last_error = str(e)
            continue
    
    return None, last_error

# --- HLAVNÍ ROZHRANÍ ---
st.title("🎵 LP Skladový Systém")

# Použijeme session_state pro trvalost dat během práce v prohlížeči
if 'sklad' not in st.session_state:
    st.session_state['sklad'] = pd.DataFrame(columns=['EAN', 'Interpret', 'Titul', 'Mnozstvi', 'Cena_s_DPH'])

tab1, tab2 = st.tabs(["📥 Naskladnění faktury", "🔍 Skener & Prodej"])

# --- TAB 1: NASKLADNĚNÍ ---
with tab1:
    st.header("1. Nahrát fakturu v PDF")
    soubor = st.file_uploader("Přetáhněte sem fakturu", type="pdf")
    
    if soubor:
        if st.button("🚀 Analyzovat fakturu"):
            with st.spinner("AI čte fakturu, moment..."):
                df_vysledek, pouzity_model = ziskej_data_z_pdf(soubor.getvalue())
                
                if df_vysledek is not None:
                    st.success(f"Úspěšně načteno pomocí {pouzity_model}!")
                    st.dataframe(df_vysledek, use_container_width=True)
                    
                    if st.button("✅ Uložit tyto desky do skladu"):
                        st.session_state['sklad'] = pd.concat([st.session_state['sklad'], df_vysledek]).drop_duplicates().reset_index(drop=True)
                        st.balloons()
                        st.success("Naskladněno!")
                else:
                    st.error(f"Chyba při čtení: {df_vysledek}")

# --- TAB 2: SKENER ---
with tab2:
    st.header("2. Práce s EAN skenerem")
    
    # Automatické zaměření (focus) na toto pole je klíčové pro skener
    ean_kod = st.text_input("PÍPNĚTE SKENEREM ZDE", key="scanner_input", help="Klikněte sem, aby skener mohl psát.")
    
    if ean_kod:
        st.subheader(f"Výsledek pro EAN: {ean_kod}")
        sklad_df = st.session_state['sklad']
        
        # Hledání v našem "dočasném" skladu
        nalezene_lp = sklad_df[sklad_df['EAN'].astype(str).str.contains(ean_kod)]
        
        if not nalezene_lp.empty:
            st.success(f"✅ NAJDENO: {nalezene_lp.iloc[0]['Interpret']} - {nalezene_lp.iloc[0]['Titul']}")
            col1, col2 = st.columns(2)
            col1.metric("Skladem", f"{nalezene_lp.iloc[0]['Mnozstvi']} ks")
            col2.metric("Cena", f"{nalezene_lp.iloc[0]['Cena_s_DPH']} Kč")
        else:
            st.warning("⚠️ Tento titul není v aktuální naskladněné faktuře.")

# Zobrazení celého skladu pro kontrolu
st.divider()
st.subheader("📊 Aktuální přehled (v paměti)")
st.dataframe(st.session_state['sklad'], use_container_width=True)
