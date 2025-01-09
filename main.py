import streamlit as st
import requests

# Funzione per rispondere a domande sul codice ATECO
def rispondi_domanda_ateco(domanda):
    # Logica per rispondere alla domanda
    return "Risposta unica basata sul codice ATECO"

import streamlit as st
import requests
from datetime import datetime, timedelta

# Funzione per bloccare richieste giornaliere basate sull'IP
def blocca_richiesta_giornaliera(ip):
    whitelist = st.secrets.get("ip_whitelist", [])
    print(f"Whitelist: {whitelist}")
    print(f"Checking IP: {ip}")
    if ip in whitelist:
        return False
    
    if 'last_request_time' not in st.session_state:
        st.session_state['last_request_time'] = {}
    
    last_request_time = st.session_state['last_request_time'].get(ip)
    
    if last_request_time:
        last_request_date = datetime.fromisoformat(last_request_time)
        today = datetime.now().date()
        if last_request_date.date() == today:
            return True
    
    st.session_state['last_request_time'][ip] = datetime.now().isoformat()
    return False

# Funzione per inviare un messaggio all'API e restituire la risposta
def inviare_messaggio_api(messaggio):
    try:
        api_url = "https://api-production-63f1.up.railway.app/v1/workflows/run"
        if messaggio.get("tipo_operazione") == "nuovo_codice":
            api_key = st.secrets["dify_api_key_new_code"]
        else:
            api_key = st.secrets["dify_api_key_update_code"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": messaggio,
            "response_mode": "blocking",
            "user": "ateco-assistant",
            "workflow_id": "0TpKAdyDHiFHr2xJ"
        }
        
        # Debug: Print request details
        print("Request URL:", api_url)
        print("Request Headers:", headers)
        print("Request Body:", data)
        
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        
        # Debug: Print successful response
        print("Response Status Code:", response.status_code)
        print("Response Body:", response.json())
        
        # Parse the response based on Dify API structure
        response_data = response.json()
        return response_data
        
    except requests.exceptions.HTTPError as e:
        # Debug: Print error details
        print("Error Status Code:", e.response.status_code)
        print("Error Response:", e.response.json())
        
        if e.response.status_code == 400:
            error_detail = e.response.json().get("detail", "Parametri non validi")
            return f"Errore 400: {error_detail}"
        elif e.response.status_code == 401:
            return "Errore 401: Autenticazione fallita. Verifica la chiave API."
        elif e.response.status_code == 404:
            return "Errore 404: Endpoint non trovato."
        return f"Errore API: {str(e)}"
    except ValueError:
        return "Errore: La risposta dell'API non è valida"
    except Exception as e:
        return f"Errore inaspettato: {str(e)}"

# App Streamlit
st.set_page_config(page_title="ATECO Code Assistant", page_icon="📊", layout="centered")

# Header con stile
st.markdown("""
    <style>
        .header {
            font-size: 40px;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            padding: 20px;
        }
        .subheader {
            font-size: 20px;
            color: #2ca02c;
            text-align: center;
            padding: 10px;
        }
        .stButton>button {
            background-color: #1f77b4;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stTextArea>textarea {
            border-radius: 5px;
            border: 1px solid #1f77b4;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #1f77b4;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">ATECO Code Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Trova o aggiorna il tuo codice ATECO</div>', unsafe_allow_html=True)

# Sidebar for instructions and system info
with st.sidebar:
    st.markdown("### Istruzioni per l'uso")
    st.markdown("""
    Questo sistema è progettato per assistere nella ricerca e nell'aggiornamento dei codici ATECO.
    Si prega di seguire attentamente le istruzioni:

    1.  **Seleziona l'operazione:** Scegli se cercare un nuovo codice ATECO o modificare un codice esistente (2007 -> 2025).
    2.  **Inserisci le informazioni:** Compila i campi richiesti in base all'operazione selezionata.
        - Per la ricerca di un nuovo codice ATECO, la richiesta deve essere specifica per il codice ATECO, non come se si utilizzasse un chatbot generico (es. ChatGPT).
    3.  **Verifica i risultati:** Le informazioni fornite sono generate da un'intelligenza artificiale e vanno verificate in autonomia.
    """)

    st.markdown("---")
    st.markdown("### Informazioni sul sistema")
    st.markdown("""
    Questo sistema è stato creato interamente con intelligenza artificiale, senza l'ausilio di sviluppatori software.
    Il motore di intelligenza artificiale utilizzato è **DeepSeek v3**.
    Si ricorda che questo sistema non è un chatbot, ma fornisce una risposta univoca basata sulle informazioni inserite.
    Per la privacy, si ricorda che non vengono inserite informazioni sensibili al momento, ma è un sistema generico.
    """)
    st.markdown("---")

# Selezione del tipo di operazione
with st.container():
    st.markdown("### Seleziona l'operazione")
    operazione = st.radio("", 
                         ["Cercare un nuovo codice ATECO", 
                          "Modificare il codice ATECO esistente (2007 → 2025)"],
                         label_visibility="collapsed")

# Input dell'utente
with st.container():
    if operazione == "Cercare un nuovo codice ATECO":
        st.markdown("### Descrivi la tua attività")
        descrizione_attivita = st.text_area("Inserisci una descrizione dettagliata dell'attività per cui vuoi trovare il codice ATECO:", 
                                           placeholder="Esempio: Ristorante con cucina tradizionale italiana...",
                                           height=150)
    else:
        st.markdown("### Informazioni sull'attività esistente")
        codice_ateco_2007 = st.text_input("Codice ATECO 2007 attuale:", 
                                        placeholder="Esempio: 56.10.11")
        
        st.markdown("### Dettagli aggiuntivi (opzionali)")
        attivita_camera_commercio = st.text_area("Attività registrata in Camera di Commercio (opzionale):", 
                                               placeholder="Descrivi l'attività come registrata...",
                                               height=100)
        sito_web = st.text_input("Sito web dell'attività (opzionale):", 
                               placeholder="https://www.esempio.com")
        note_aggiuntive = st.text_area("Note aggiuntive (opzionale):", 
                                     placeholder="Inserisci eventuali informazioni aggiuntive...",
                                     height=100)

# Bottone per inviare la richiesta
with st.container():
    if st.button("Trova codice ATECO", use_container_width=True):
        ip = requests.get('https://api.ipify.org').text
        if ip:
            if blocca_richiesta_giornaliera(ip):
                st.error(f"Richiesta giornaliera bloccata per l'IP: {ip}. Riprova domani.")
            else:
                if operazione == "Cercare un nuovo codice ATECO":
                    if not descrizione_attivita:
                        st.error("Per favore, inserisci una descrizione dell'attività")
                    else:
                        # Preparazione dati per il nuovo flusso Dify
                        dati = {
                            "tipo_operazione": "nuovo_codice",
                            "richiesta": descrizione_attivita
                        }
                else:
                    if not codice_ateco_2007:
                        st.error("Per favore, inserisci il codice ATECO 2007")
                    else:
                        # Preparazione dati per il nuovo flusso Dify
                        dati = {
                            "tipo_operazione": "aggiornamento_codice",
                            "richiesta": "Aggiornamento codice ATECO",
                            "codice_ateco": codice_ateco_2007,
                            "attivita": attivita_camera_commercio if attivita_camera_commercio else "",
                            "sito_internet": sito_web if sito_web else ""
                        }
        
                # Invio richiesta all'API e visualizzazione risposta
                risposta_api = inviare_messaggio_api(dati)
                if isinstance(risposta_api, dict) and 'data' in risposta_api:
                    if 'outputs' in risposta_api['data'] and 'output' in risposta_api['data']['outputs']:
                        st.markdown(risposta_api['data']['outputs']['output'])
                    else:
                        st.write("Formato della risposta non valido")
                else:
                    st.write(f"Errore nella risposta: {risposta_api}")
    
    st.markdown("---")
    st.markdown("### Allegati")
    with open("Nota-metodologica-1.pdf", "rb") as file:
        st.download_button(
            label="Scarica PDF con note metodologiche",
            data=file,
            file_name="Nota-metodologica-1.pdf",
            mime="application/pdf"
        )
    with open("StrutturaATECO-2025-IT-EN-1.xlsx", "rb") as file:
        st.download_button(
            label="Scarica Excel con struttura ATECO 2025",
            data=file,
            file_name="StrutturaATECO-2025-IT-EN-1.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Bloccare richieste giornaliere
ip = requests.get('https://api.ipify.org').text
if ip:
    if blocca_richiesta_giornaliera(ip):
        st.write(f"Richiesta giornaliera bloccata per l'IP: {ip}")
