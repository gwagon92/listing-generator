import os
from datetime import datetime

import anthropic
import gspread
import streamlit as st
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_SA_FILE = os.path.join(_BASE_DIR, "service-account.json")
_SHEET_ID = "1rgrQ4rzl0Xv7Tj-E2NqQKqfoQ6vNWJSD5FDNuXO7gwg"
_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


@st.cache_resource
def _gs_client() -> gspread.Client:
    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=_SCOPES
        )
    else:
        creds = Credentials.from_service_account_file(_SA_FILE, scopes=_SCOPES)
    return gspread.authorize(creds)


def _get_worksheet(title: str, headers: list[str]) -> gspread.Worksheet:
    sh = _gs_client().open_by_key(_SHEET_ID)
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=1000, cols=len(headers))
        ws.append_row(headers)
    else:
        if not ws.row_values(1):
            ws.append_row(headers)
    return ws


def log_usage(productnaam: str) -> None:
    ws = _get_worksheet("Usage", ["tijdstip", "productnaam"])
    ws.append_row([datetime.now().isoformat(), productnaam])


def log_feedback(productnaam: str, rating: int, wat_goed: str, wat_beter: str) -> None:
    ws = _get_worksheet("Feedback", ["tijdstip", "productnaam", "beoordeling", "wat_goed", "wat_beter"])
    ws.append_row([datetime.now().isoformat(), productnaam, rating, wat_goed, wat_beter])


st.set_page_config(page_title="BolBot — Listing Generator", page_icon="⚡", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background-color: #111111 !important;
}

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 720px !important;
}

p, li, span, div { color: #D0D0D0; }
h1, h2, h3, h4   { color: #F0F0F0 !important; font-family: 'Inter', sans-serif !important; }

/* Form card */
[data-testid="stForm"] {
    background-color: #1C1C1C !important;
    border: 1px solid #2C2C2C !important;
    border-radius: 16px !important;
    padding: 1.75rem 2rem !important;
}

/* Inputs */
[data-testid="stTextInput"]  input,
[data-testid="stTextArea"]   textarea,
[data-testid="stNumberInput"] input {
    background-color: #1A1A1A !important;
    border: 1.5px solid #333333 !important;
    color: #E8E8E8 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

[data-testid="stTextInput"]  input:focus,
[data-testid="stTextArea"]   textarea:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #E8571A !important;
    box-shadow: 0 0 0 3px rgba(232, 87, 26, 0.18) !important;
    outline: none !important;
}

[data-testid="stTextInput"]   input::placeholder,
[data-testid="stTextArea"]    textarea::placeholder { color: #4A4A4A !important; }

/* Labels */
[data-testid="stTextInput"]   label,
[data-testid="stTextArea"]    label,
[data-testid="stNumberInput"] label,
[data-testid="stForm"]        label {
    color: #777777 !important;
    font-size: 0.73rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}

/* Primary CTA button */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #E8571A 0%, #C94010 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    min-height: 56px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(232, 87, 26, 0.30) !important;
}

[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg, #F06422 0%, #D4501A 100%) !important;
    box-shadow: 0 6px 28px rgba(232, 87, 26, 0.45) !important;
    transform: translateY(-2px) !important;
}

[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 10px rgba(232, 87, 26, 0.30) !important;
}

/* Slider thumb + fill */
[data-baseweb="slider"] [role="slider"]      { background-color: #E8571A !important; border-color: #E8571A !important; }
[data-baseweb="slider"] [role="progressbar"] { background-color: #E8571A !important; }

/* Alerts */
[data-testid="stAlert"] { border-radius: 10px !important; border-left-width: 3px !important; }

/* Divider */
hr { border-color: #2A2A2A !important; }

/* Column gap */
[data-testid="stHorizontalBlock"] { gap: 1rem !important; }

/* Mobile */
@media (max-width: 640px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    [data-testid="stForm"] { padding: 1.25rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2.75rem 0 2rem 0;">
  <div style="display:inline-flex; align-items:center; gap:14px; margin-bottom:10px;">
    <div style="
        width:52px; height:52px;
        background: linear-gradient(135deg, #E8571A, #C94010);
        border-radius:14px;
        display:flex; align-items:center; justify-content:center;
        font-size:1.6rem;
        box-shadow: 0 4px 18px rgba(232,87,26,0.40);
    ">⚡</div>
    <span style="
        font-family:'Inter',sans-serif;
        font-size:2.6rem; font-weight:800;
        color:#F0F0F0; letter-spacing:-0.04em; line-height:1;
    ">BolBot</span>
  </div>
  <p style="
      color:#555555; font-size:1rem; margin:0;
      font-family:'Inter',sans-serif; font-weight:400; letter-spacing:0.01em;
  ">Jouw bol.com listing in 30 seconden</p>
</div>
""", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────────────────────────
with st.form("listing_form"):
    productnaam = st.text_input("Productnaam *", placeholder="bijv. Ergonomische Bureaustoelkussen")

    col1, col2 = st.columns(2)
    with col1:
        materiaal = st.text_input("Materiaal", placeholder="bijv. traagschuim, ademend mesh")
        doelgroep = st.text_input("Doelgroep", placeholder="bijv. thuiswerkers, kantoormedewerkers")
    with col2:
        prijs = st.number_input("Verkoopprijs (€) *", min_value=0.01, step=0.50, format="%.2f", value=29.99)

    voordelen = st.text_area(
        "Voordelen / kenmerken",
        placeholder="bijv. verstelbare bandjes, wasbare hoes, anti-slip onderkant",
        height=100,
    )

    submitted = st.form_submit_button("Genereer listing →", use_container_width=True, type="primary")

if submitted:
    if not productnaam:
        st.error("Voer een productnaam in.")
    else:
        log_usage(productnaam)

        with st.spinner("Listing wordt gegenereerd..."):
            prompt = f"""Schrijf een professionele Nederlandse bol.com productlisting voor het volgende product:

Product: {productnaam}
Materiaal: {materiaal if materiaal else 'niet opgegeven'}
Voordelen / kenmerken: {voordelen if voordelen else 'niet opgegeven'}
Doelgroep: {doelgroep if doelgroep else 'algemeen'}
Verkoopprijs: €{prijs:.2f}

Geef de output EXACT in onderstaand formaat (met de labels op een aparte regel):

TITEL:
[Producttitel, max 150 tekens, SEO-geoptimaliseerd voor bol.com]

USP BULLETS:
• [USP 1 — concreet voordeel, max 1 zin]
• [USP 2 — concreet voordeel, max 1 zin]
• [USP 3 — concreet voordeel, max 1 zin]
• [USP 4 — concreet voordeel, max 1 zin]
• [USP 5 — concreet voordeel, max 1 zin]

PRODUCTOMSCHRIJVING:
[Schrijf de omschrijving in 3 alinea's, elk voorafgegaan door een passende emoji-kop.
 Kies koppen die aansluiten bij het product — gebruik NIET altijd dezelfde koppen.
 Voorbeelden van geschikte koppen (pas aan op het product):
   🎯 Waarom kiezen voor [productnaam]?
   ✅ Geschikt voor
   📦 Wat krijg je?
   💡 Hoe gebruik je het?
   🌿 Duurzaam & verantwoord
   🏠 Perfect voor thuis
   ⚡ Kenmerken in één oogopslag
 Formaat per alinea:
   [emoji] [Koptekst]
   [alineatekst van 2-4 zinnen]
 Totaal 150-300 woorden, klantgericht en overtuigend.]

Schrijf alles in het Nederlands. Gebruik zoekwoorden die shoppers op bol.com intypen."""

            response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1500,
                system=[{
                    "type": "text",
                    "text": (
                        "Je bent een expert bol.com seller die professionele Nederlandse "
                        "productlistings schrijft. Je listings zijn SEO-geoptimaliseerd, "
                        "klantgericht en overtuigend. Je schrijft altijd in het Nederlands."
                    ),
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=[{"role": "user", "content": prompt}],
            )

            output = response.content[0].text

        sections: dict[str, str] = {}
        current_section: str | None = None
        current_lines: list[str] = []

        for line in output.split("\n"):
            stripped = line.strip()
            if stripped == "TITEL:":
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = "titel"
                current_lines = []
            elif stripped == "USP BULLETS:":
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = "usps"
                current_lines = []
            elif stripped == "PRODUCTOMSCHRIJVING:":
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = "omschrijving"
                current_lines = []
            elif current_section is not None:
                current_lines.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_lines).strip()

        st.session_state["listing"] = {
            "productnaam": productnaam,
            "sections": sections,
            "output": output,
        }
        st.session_state.pop("feedback_sent", None)

if "listing" in st.session_state:
    listing_data = st.session_state["listing"]
    sections = listing_data["sections"]
    output = listing_data["output"]

    # ── Result header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="
        border-left: 3px solid #E8571A;
        padding: 0.25rem 0 0.25rem 1rem;
        margin: 2rem 0 1.25rem 0;
    ">
        <p style="font-size:1.2rem; font-weight:700; color:#F0F0F0; margin:0; font-family:'Inter',sans-serif;">
            Listing klaar
        </p>
        <p style="font-size:0.83rem; color:#555555; margin:4px 0 0 0; font-family:'Inter',sans-serif;">
            Kopieer de tekst direct naar bol.com Verkooppartner
        </p>
    </div>
    """, unsafe_allow_html=True)

    titel = sections.get("titel", "").strip()
    st.markdown('<p style="color:#E8571A;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;font-family:\'Inter\',sans-serif;">Titel</p>', unsafe_allow_html=True)
    st.text_area(
        label="titel_veld",
        value=titel,
        height=75,
        key="titel_output",
        label_visibility="collapsed",
    )
    char_count = len(titel)
    color = "green" if char_count <= 150 else "red"
    st.markdown(f'<p style="font-size:0.78rem; color:{"#4CAF50" if char_count <= 150 else "#E53935"}; margin-top:-8px; font-family:\'Inter\',sans-serif;">{char_count} / 150 tekens</p>', unsafe_allow_html=True)

    st.markdown('<p style="color:#E8571A;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin:1rem 0 4px 0;font-family:\'Inter\',sans-serif;">USP Bullets</p>', unsafe_allow_html=True)
    usps = sections.get("usps", "").strip()
    st.text_area(
        label="usps_veld",
        value=usps,
        height=170,
        key="usps_output",
        label_visibility="collapsed",
    )

    omschrijving = sections.get("omschrijving", "").strip()
    word_count = len(omschrijving.split()) if omschrijving else 0
    st.markdown(f'<p style="color:#E8571A;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin:1rem 0 4px 0;font-family:\'Inter\',sans-serif;">Productomschrijving &nbsp;<span style="color:#555555;font-weight:400;text-transform:none;letter-spacing:0;">~{word_count} woorden</span></p>', unsafe_allow_html=True)
    st.text_area(
        label="omschrijving_veld",
        value=omschrijving,
        height=260,
        key="omschrijving_output",
        label_visibility="collapsed",
    )

    if not any(sections.values()):
        st.warning("Kon de output niet automatisch opdelen. Ruwe output:")
        st.text_area("Ruwe output", value=output, height=400)

    # ── Feedback ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="
        border-top: 1px solid #2A2A2A;
        margin: 2rem 0 1.25rem 0;
        padding-top: 1.5rem;
    ">
        <p style="font-size:0.95rem; font-weight:600; color:#888888; margin:0; font-family:'Inter',sans-serif;">
            Hoe was de listing?
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("feedback_sent"):
        with st.form("feedback_form"):
            rating = st.slider("Beoordeling (1–5 sterren)", min_value=1, max_value=5, value=3)
            wat_goed = st.text_area("Wat vond je goed?", height=80)
            wat_beter = st.text_area("Wat kan beter?", height=80)
            fb_submitted = st.form_submit_button("Verstuur feedback →", use_container_width=True)

        if fb_submitted:
            log_feedback(listing_data["productnaam"], rating, wat_goed, wat_beter)
            st.session_state["feedback_sent"] = True
            st.rerun()
    else:
        st.success("Feedback ontvangen, bedankt!")
