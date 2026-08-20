# SESSION STATUS — Listing Generator
Bijgewerkt: 2026-05-21

## Wat werkt

- **Streamlit web-app** — `app.py` draait als lokale UI voor bol.com listing generatie
- **Claude API integratie** — gebruikt `anthropic` client om titel + USPs + omschrijving te genereren
- **Google Sheets logging** — logt gebruik en feedback via `gspread` naar spreadsheet `1rgrQ4rzl0Xv7Tj-E2NqQKqfoQ6vNWJSD5FDNuXO7gwg`
- **Inputformulier** — productnaam, materiaal, doelgroep, prijs, voordelen
- **Output** — titel (max 150 tekens met teller), USP bullets, omschrijving
- **Feedbackformulier** — rating + vrije tekst, wordt gelogd naar Sheets
- **Dual authenticatie** — Streamlit secrets (cloud) óf lokaal `service-account.json`

## Beslissingen gemaakt

- Streamlit als UI-framework — snel te bouwen, geen frontend-kennis vereist
- Google Sheets voor logging — geen database nodig, direct inzichtelijk
- `@st.cache_resource` voor Sheets-client — niet bij elke generate opnieuw verbinden
- `venv/` lokaal voor dependencies
- Twee tabbladen in Sheets: usage logging + feedback logging

## Bestandsstructuur

| Bestand | Doel |
|---------|------|
| `app.py` | Streamlit app — hoofd applicatie |
| `requirements.txt` | streamlit, anthropic, gspread, google-auth, python-dotenv |
| `service-account.json` | Google Sheets service account (gitignored) |
| `streamlit_secrets.toml` | Secrets voor Streamlit Cloud deploy (gitignored) |
| `secrets_template.txt` | Template voor secrets (wél in git) |
| `venv/` | Virtual environment (gitignored) |
| `.devcontainer/` | Dev container configuratie |
| `.gitignore` | Sluit secrets en venv uit |

## Exacte volgende stap

App starten en testen:
```bash
cd ~/AI-business/listing-generator && source venv/bin/activate && streamlit run app.py
```

Of integreren als stap in de BolBot pipeline — listing-agent is de agent-variant, deze app is de standalone UI-versie.

## Bekende problemen / openstaande vragen

- Relatie tussen deze app en de `listing-agent.md` in `.claude/agents/` is onduidelijk — zijn dit duplicaten of complementair?
- Geen `.devcontainer/` setup getest
- Google Sheets spreadsheet ID hardcoded in `app.py` — zou naar `.env` moeten
