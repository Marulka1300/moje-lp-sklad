import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

st.set_page_config(page_title="LP Skladová Evidence", layout="wide")

# --- NASTAVENÍ API ---
# Klíč máte v pořádku, použijeme ho
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
                # ZKOUŠÍME VÍCE NÁZVŮ MODELŮ, ABYCHOM SE VYHNULI CHYBĚ 404
                success = False
                for model_name in ['gemini-1.5-flash', 'models/gemini-1.5-flash']:
                    try:
                        model = genai.GenerativeModel(model_name)
                        content = uploaded_file.read()
                        response = model.generate_content([
                            "Vrať CSV tabulku (středník): EAN;Interpret;Titul;Mnozstvi;Cena_s_DPH. Jen čisté CSV.",
                            {"mime_type": "application/pdf", "data": content}
                        ])
                        
                        csv_data = response.text.replace('```csv', '').replace('```', '').strip()
                        df = pd.read_csv(io.StringIO(csv_data), sep=';')
                        st.session_state['sklad_priprava'] = df
                        st.success(f"Faktura úspěšně načtena modelem {model_name}!")
                        st.dataframe(df)
                        success = True
                        break
                    except Exception as e:
                        continue # Pokud tento název nefunguje, zkusíme další
                
                if not success:
                    st.error("Nepodařilo se spojit s Google AI. Zkuste to za chvíli nebo zkontrolujte připojení.")

with tab2:
    st.header("Skladová databáze")
    st.write("Zde bude seznam titulů a políčko pro skener.")
    # Políčko pro skener
    ean_scan = st.text_input("NAČTI EAN SKENEREM")
    if ean_scan:
        st.write(f"Naskenováno: {ean_scan}")
