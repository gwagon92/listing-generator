import csv
import os
from datetime import datetime

import anthropic
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USAGE_LOG = os.path.join(_BASE_DIR, "usage_log.csv")
FEEDBACK_LOG = os.path.join(_BASE_DIR, "feedback_log.csv")


def log_usage(productnaam: str) -> None:
    file_exists = os.path.isfile(USAGE_LOG)
    with open(USAGE_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["tijdstip", "productnaam"])
        writer.writerow([datetime.now().isoformat(), productnaam])


def log_feedback(productnaam: str, rating: int, wat_goed: str, wat_beter: str) -> None:
    file_exists = os.path.isfile(FEEDBACK_LOG)
    with open(FEEDBACK_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["tijdstip", "productnaam", "beoordeling", "wat_goed", "wat_beter"])
        writer.writerow([datetime.now().isoformat(), productnaam, rating, wat_goed, wat_beter])


st.set_page_config(page_title="Bol.com Listing Generator", page_icon="🛒", layout="centered")
st.title("Bol.com Listing Generator")
st.markdown("Vul de productdetails in en genereer direct een volledige listing.")

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

    submitted = st.form_submit_button("Genereer listing", use_container_width=True, type="primary")

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
[Klantgerichte omschrijving van 150-300 woorden in het Nederlands]

Schrijf alles in het Nederlands. Gebruik zoekwoorden die shoppers op bol.com intypen."""

            response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
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

    st.success("Listing gegenereerd!")
    st.divider()

    titel = sections.get("titel", "").strip()
    st.subheader("Titel")
    st.text_area(
        label="titel_veld",
        value=titel,
        height=75,
        key="titel_output",
        label_visibility="collapsed",
    )
    char_count = len(titel)
    color = "green" if char_count <= 150 else "red"
    st.markdown(f":{color}[{char_count} / 150 tekens]")

    st.subheader("USP Bullets")
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
    st.subheader(f"Productomschrijving  (~{word_count} woorden)")
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

    st.divider()
    st.subheader("Feedback")

    if not st.session_state.get("feedback_sent"):
        with st.form("feedback_form"):
            rating = st.slider("Beoordeling (1–5 sterren)", min_value=1, max_value=5, value=3)
            wat_goed = st.text_area("Wat vond je goed?", height=80)
            wat_beter = st.text_area("Wat kan beter?", height=80)
            fb_submitted = st.form_submit_button("Verstuur feedback", use_container_width=True)

        if fb_submitted:
            log_feedback(listing_data["productnaam"], rating, wat_goed, wat_beter)
            st.session_state["feedback_sent"] = True
            st.rerun()
    else:
        st.success("Feedback ontvangen, bedankt!")
