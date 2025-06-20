import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from io import BytesIO

# Funktion zum Abrufen von SKUs für eine Serie
def fetch_skus(keyword):
    base_url = "https://partsurfer.hpe.com/Search.aspx?searchText="
    search_url = f"{base_url}{keyword.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr", class_="GridItemStyle")
    
    results = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            sku = cols[0].text.strip()
            name = cols[1].text.strip()
            desc = cols[2].text.strip()
            results.append({"SKU": sku, "Bezeichnung": name, "Beschreibung": desc})
    return results

# Streamlit UI
st.set_page_config(page_title="Aruba SKU Exporter", layout="centered")

st.title("📦 Aruba Switch SKU Exporter")
st.markdown("Exportiere alle HPE Aruba Switch SKUs mit Beschreibung direkt in eine CSV-Datei.")

# Liste der verfügbaren Serien
serien = [
    "CX 6000", "CX 6100", "CX 6200", "CX 6300", "CX 6400",
    "CX 8100", "CX 8325", "CX 8360", "CX 8400", "CX 9300", "CX 10000",
    "2530", "2540", "2920", "2930F", "2930M", "3810", "5400R"
]

auswahl = st.multiselect("🔍 Serien auswählen", serien, default=serien)

if st.button("🔄 Export starten"):
    alle_ergebnisse = []
    fortschritt = st.progress(0)

    for i, serie in enumerate(auswahl):
        st.write(f"🔎 Suche nach: `{serie}`")
        resultate = fetch_skus(serie)
        alle_ergebnisse.extend(resultate)
        fortschritt.progress((i + 1) / len(auswahl))
        time.sleep(1)

    if alle_ergebnisse:
        df = pd.DataFrame(alle_ergebnisse)
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        csv_bytes = BytesIO(csv.encode("utf-8-sig"))

        st.success(f"✅ {len(df)} Einträge gefunden.")
        st.download_button("⬇️ CSV herunterladen", data=csv_bytes, file_name="aruba_switches.csv", mime="text/csv")
    else:
        st.warning("⚠️ Keine Ergebnisse gefunden.")
