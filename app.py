import streamlit as st
import anthropic
import urllib.parse
import json
import re
import feedparser
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

# =========================
# Configuración de página
# =========================
st.set_page_config(
    page_title="Newsletter SAP",
    page_icon="📰",
    layout="wide"
)

# =========================
# DATOS EMBEBIDOS - Territorios
# =========================
# Estructura: lista de dicts con las columnas del archivo
# Para mantener el código manejable, parseamos el texto directamente

@st.cache_data
def load_territory_data() -> List[Dict]:
    """Carga los datos de territorios (AE, industria, manager y país — sin cuentas)."""
    raw_data = """Alejandra Guzman	Agribusiness	Daniel Castro	COLOMBIA
Alejandro Nunez	Consumer Products	Fernando Oriolo	ARGENTINA
Alejandro Nunez	Engineering, Construction, and O	Fernando Oriolo	ARGENTINA
Alejandro Nunez	Life Sciences	Fernando Oriolo	ARGENTINA
Alejandro Nunez	Media	Fernando Oriolo	ARGENTINA
Alejandro Nunez	Retail	Fernando Oriolo	ARGENTINA
Alejandro Nunez	Wholesale Distribution	Fernando Oriolo	ARGENTINA
Alejandro Roncancio	Agribusiness	Daniel Castro	COLOMBIA
Alejandro Roncancio	Banking	Daniel Castro	COLOMBIA
Angie Monroy	Automotive	Daniel Castro	COLOMBIA
Angie Monroy	Banking	Daniel Castro	COLOMBIA
Barbara Rodriguez	Agribusiness	Maria José Amezaga	ARGENTINA
Barbara Rodriguez	Chemicals	Maria José Amezaga	ARGENTINA
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA
Barbara Rodriguez	Professional Services	Maria José Amezaga	ARGENTINA
Barbara Rodriguez	Retail	Maria José Amezaga	ARGENTINA
Barbara Rodriguez	Wholesale Distribution	Maria José Amezaga	ARGENTINA
Carlos Yepez	Agribusiness	Fernando Oriolo	PERU
Carlos Yepez	Automotive	Fernando Oriolo	PERU
Carolina Latorre	Agribusiness	Fernando Oriolo	CHILE
Carolina Latorre	Automotive	Fernando Oriolo	CHILE
Carolina Latorre	Consumer Products	Fernando Oriolo	CHILE
Carolina Latorre	Engineering, Construction, and O	Fernando Oriolo	CHILE
Carolina Latorre	Insurance	Fernando Oriolo	CHILE
Carolina Latorre	Life Sciences	Fernando Oriolo	CHILE
Carolina Latorre	Mill Products and Mining	Fernando Oriolo	CHILE
Carolina Latorre	Professional Services	Fernando Oriolo	CHILE
Carolina Latorre	Public Sector	Fernando Oriolo	CHILE
Carolina Latorre	Travel and Transportation	Fernando Oriolo	CHILE
Carolina Latorre	Wholesale Distribution	Fernando Oriolo	CHILE
Claudia Chirino	Agribusiness	Fernando Oriolo	CHILE
Claudia Chirino	Automotive	Fernando Oriolo	CHILE
Claudia Chirino	Banking	Fernando Oriolo	CHILE
Claudia Chirino	Higher Education and Research	Fernando Oriolo	CHILE
Claudia Chirino	Life Sciences	Fernando Oriolo	CHILE
Claudia Chirino	Mill Products and Mining	Fernando Oriolo	CHILE
Claudia Chirino	Professional Services	Fernando Oriolo	CHILE
Claudia Chirino	Public Sector	Fernando Oriolo	CHILE
Claudia Chirino	Telecommunications	Fernando Oriolo	CHILE
Claudia Chirino	Travel and Transportation	Fernando Oriolo	CHILE
Diana Garcia Ceballos	Aerospace and Defense	Soledad Novas	COLOMBIA
Diana Garcia Ceballos	Agribusiness	Soledad Novas	COLOMBIA
Diana Romero	Agribusiness	Daniel Castro	COLOMBIA
Diana Romero	Consumer Products	Daniel Castro	COLOMBIA
Diana Romero	Mill Products and Mining	Daniel Castro	COLOMBIA
Diana Romero	Professional Services	Daniel Castro	COLOMBIA
Diana Romero	Retail	Daniel Castro	COLOMBIA
Diana Romero	Wholesale Distribution	Daniel Castro	COLOMBIA
Federico Martinez	Consumer Products	Fernando Oriolo	ARGENTINA
Federico Martinez	Mill Products and Mining	Fernando Oriolo	ARGENTINA
Federico Martinez	Professional Services	Fernando Oriolo	ARGENTINA
Federico Martinez	Retail	Fernando Oriolo	ARGENTINA
Felipe Rodriguez	Agribusiness	Daniel Castro	COLOMBIA
Felipe Rodriguez	Automotive	Daniel Castro	COLOMBIA
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU
Gurin Arauco	Automotive	Maria José Amezaga	PERU
Gurin Arauco	Banking	Maria José Amezaga	PERU
Gurin Arauco	Chemicals	Maria José Amezaga	PERU
Gurin Arauco	Mill Products and Mining	Maria José Amezaga	PERU
Gurin Arauco	Oil, Gas, and Energy	Maria José Amezaga	PERU
Gurin Arauco	Public Sector	Maria José Amezaga	PERU
Gurin Arauco	Utilities	Maria José Amezaga	PERU
Joaquin Biagini	Automotive	Maria José Amezaga	ARGENTINA
Joaquin Biagini	Banking	Maria José Amezaga	ARGENTINA
Joaquin Biagini	Healthcare	Maria José Amezaga	ARGENTINA
Joaquin Biagini	Media	Maria José Amezaga	ARGENTINA
Joaquin Biagini	Professional Services	Maria José Amezaga	ARGENTINA
Jorge Pizarro	Aerospace and Defense	Maria José Amezaga	CHILE
Jorge Pizarro	Automotive	Maria José Amezaga	CHILE
Jorge Pizarro	Banking	Maria José Amezaga	CHILE
Jorge Pizarro	Engineering, Construction, and O	Maria José Amezaga	CHILE
Jorge Pizarro	Insurance	Maria José Amezaga	CHILE
Jorge Pizarro	Life Sciences	Maria José Amezaga	CHILE
Jorge Pizarro	Media	Maria José Amezaga	CHILE
Jorge Pizarro	Professional Services	Maria José Amezaga	CHILE
Jorge Pizarro	Utilities	Maria José Amezaga	CHILE
Juan Duran	Agribusiness	Daniel Castro	COLOMBIA
Juan Duran	Life Sciences	Daniel Castro	COLOMBIA
Juan Duran	Oil, Gas, and Energy	Daniel Castro	COLOMBIA
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA
Julian Grinstein	Engineering, Construction, and O	Maria José Amezaga	ARGENTINA
Julian Grinstein	Industrial Manufacturing	Maria José Amezaga	ARGENTINA
Julian Grinstein	Oil, Gas, and Energy	Maria José Amezaga	ARGENTINA
Maria Teresa Romero	Banking	Maria José Amezaga	PERU
Maria Teresa Romero	Consumer Products	Maria José Amezaga	PERU
Maria Teresa Romero	Healthcare	Maria José Amezaga	PERU
Maria Teresa Romero	Insurance	Maria José Amezaga	PERU
Maria Teresa Romero	Media	Maria José Amezaga	PERU
Maria Teresa Romero	Professional Services	Maria José Amezaga	PERU
Micaela Storni	Aerospace and Defense	Soledad Novas	CHILE
Milena Gimenez	Aerospace and Defense	Soledad Novas	ARGENTINA
Milena Gimenez	Agribusiness	Soledad Novas	ARGENTINA
Nahuel Frias	Agribusiness	Fernando Oriolo	ARGENTINA
Nahuel Frias	Banking	Fernando Oriolo	ARGENTINA
Nahuel Frias	Chemicals	Fernando Oriolo	ARGENTINA
Nahuel Frias	Consumer Products	Fernando Oriolo	ARGENTINA
Nahuel Frias	Mill Products and Mining	Fernando Oriolo	ARGENTINA
Nahuel Frias	Oil, Gas, and Energy	Fernando Oriolo	ARGENTINA
Nahuel Frias	Professional Services	Fernando Oriolo	ARGENTINA
Nahuel Frias	Retail	Fernando Oriolo	ARGENTINA
Nahuel Frias	Travel and Transportation	Fernando Oriolo	ARGENTINA
Nahuel Frias	Wholesale Distribution	Fernando Oriolo	ARGENTINA
Rodrigo Salgado	Aerospace and Defense	Maria José Amezaga	PERU
Rodrigo Salgado	Engineering, Construction, and O	Maria José Amezaga	PERU
Rodrigo Salgado	Higher Education and Research	Maria José Amezaga	PERU
Rodrigo Salgado	Retail	Maria José Amezaga	PERU
Rodrigo Salgado	Travel and Transportation	Maria José Amezaga	PERU
Rodrigo Salgado	Wholesale Distribution	Maria José Amezaga	PERU
Salome Martinez	Agribusiness	Fernando Oriolo	CHILE
Salome Martinez	Banking	Fernando Oriolo	CHILE
Salome Martinez	Consumer Products	Fernando Oriolo	CHILE
Salome Martinez	Higher Education and Research	Fernando Oriolo	CHILE
Salome Martinez	Industrial Manufacturing	Fernando Oriolo	CHILE
Salome Martinez	Insurance	Fernando Oriolo	CHILE
Salome Martinez	Mill Products and Mining	Fernando Oriolo	CHILE
Salome Martinez	Retail	Fernando Oriolo	CHILE
Salome Martinez	Travel and Transportation	Fernando Oriolo	CHILE
Salome Martinez	Utilities	Fernando Oriolo	CHILE
Salome Martinez	Wholesale Distribution	Fernando Oriolo	CHILE
Sebastian Figueroa	Agribusiness	Maria José Amezaga	CHILE
Sebastian Figueroa	Chemicals	Maria José Amezaga	CHILE
Sebastian Figueroa	Consumer Products	Maria José Amezaga	CHILE
Sebastian Figueroa	Higher Education and Research	Maria José Amezaga	CHILE
Sebastian Figueroa	Industrial Manufacturing	Maria José Amezaga	CHILE
Sebastian Figueroa	Mill Products and Mining	Maria José Amezaga	CHILE
Sebastian Figueroa	Public Sector	Maria José Amezaga	CHILE
Sebastian Figueroa	Retail	Maria José Amezaga	CHILE
Sebastian Figueroa	Travel and Transportation	Maria José Amezaga	CHILE
Sebastian Figueroa	Wholesale Distribution	Maria José Amezaga	CHILE
Veronica Ares	Agribusiness	Fernando Oriolo	ARGENTINA
Veronica Ares	Automotive	Fernando Oriolo	ARGENTINA
Veronica Ares	Consumer Products	Fernando Oriolo	ARGENTINA
Veronica Ares	Industrial Manufacturing	Fernando Oriolo	ARGENTINA
Veronica Ares	Life Sciences	Fernando Oriolo	ARGENTINA
Veronica Ares	Mill Products and Mining	Fernando Oriolo	ARGENTINA
Veronica Ares	Oil, Gas, and Energy	Fernando Oriolo	ARGENTINA
Yadira Castañeda	Agribusiness	Daniel Castro	COLOMBIA"""

    records = []
    for line in raw_data.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) >= 4:
            records.append({
                "ae": parts[0].strip(),
                "industry": parts[1].strip(),
                "manager": parts[2].strip(),
                "country": parts[3].strip().upper(),
            })
    return records


def get_country_data(data: List[Dict], country: str) -> Dict:
    """Extrae información organizada por país (AEs, industrias y managers — sin cuentas)."""
    country_upper = country.upper()
    filtered = [r for r in data if r["country"] == country_upper]

    # AEs únicos
    aes = list(set(r["ae"] for r in filtered))

    # Industrias únicas
    industries = list(set(r["industry"] for r in filtered))

    # AEs por industria
    aes_by_industry = defaultdict(set)
    for r in filtered:
        aes_by_industry[r["industry"]].add(r["ae"])

    # Managers únicos
    managers = list(set(r["manager"] for r in filtered))

    return {
        "aes": sorted(aes),
        "industries": sorted(industries),
        "aes_by_industry": {k: sorted(v) for k, v in aes_by_industry.items()},
        "managers": sorted(managers),
        "records": filtered
    }


# =========================
# Configuración de emails por AE
# =========================
AE_EMAILS = {
    "Agustina Landi": "agustina.landi@sap.com",
    "Diana Garcia Ceballos": "diana.garcia.ceballos@sap.com",
    "Jorge Pizarro": "jorge.pizarro@sap.com",
    "Rodrigo Salgado": "rodrigo.salgado@sap.com",
    "Micaela Storni": "micaela.storni@sap.com",
    "Milena Gimenez": "milena.gimenez@sap.com",
    "Alejandra Guzman": "alejandra.guzman@sap.com",
    "Felipe Rodriguez": "felipe.rodriguez@sap.com",
    "Veronica Ares": "veronica.ares@sap.com",
    "Diana Romero": "diana.romero@sap.com",
    "Julian Grinstein": "julian.grinstein@sap.com",
    "Nahuel Frias": "nahuel.frias@sap.com",
    "Barbara Rodriguez": "barbara.rodriguez@sap.com",
    "Joaquin Biagini": "joaquin.biagini@sap.com",
    "Gonzalo Delosrios": "gonzalo.delosrios@sap.com",
    "Carlos Yepez": "carlos.yepez@sap.com",
    "Maria Teresa Romero": "maria.teresa.romero@sap.com",
    "Gurin Arauco": "gurin.arauco@sap.com",
    "Sebastian Figueroa": "sebastian.figueroa@sap.com",
    "Carolina Latorre": "carolina.latorre@sap.com",
    "Claudia Chirino": "claudia.chirino@sap.com",
    "Salome Martinez": "salome.martinez@sap.com",
    "Noelia Madeo": "noelia.madeo@sap.com",
    "Pilar Nunez Pessano": "pilar.nunez.pessano@sap.com",
    "Lucila Moglianesi": "lucila.moglianesi@sap.com",
    "Sofia Pepe": "sofia.pepe@sap.com",
    "Angie Monroy": "angie.monroy@sap.com",
    "Alejandro Roncancio": "alejandro.roncancio@sap.com",
    "Juan Duran": "juan.duran@sap.com",
    "Yadira Castañeda": "yadira.castaneda@sap.com",
    "Federico Martinez": "federico.martinez@sap.com",
    "Alejandro Nunez": "alejandro.nunez@sap.com",
}

CC_EMAILS = ["julieta.rigi@sap.com", "nicolas.araneda@sap.com", "luis.plazas@sap.com"]

COUNTRIES = ["ARGENTINA", "CHILE", "PERU", "COLOMBIA"]
COUNTRY_DISPLAY = {
    "ARGENTINA": "Argentina",
    "CHILE": "Chile",
    "PERU": "Perú",
    "COLOMBIA": "Colombia"
}
COUNTRY_FLAGS = {
    "ARGENTINA": "🇦🇷",
    "CHILE": "🇨🇱",
    "PERU": "🇵🇪",
    "COLOMBIA": "🇨🇴"
}

# =========================
# Estilos CSS
# =========================
st.markdown("""
<style>
    .sap-hero {
        background: linear-gradient(120deg, #003A8C 0%, #0057D9 65%, #0070F2 100%);
        border-radius: 18px;
        padding: 28px 32px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,.18);
    }
    .sap-badge {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 10px;
        background: rgba(255,255,255,.18);
        margin-right: 8px;
        font-size: 12px;
        font-weight: 600;
    }
    .step-header {
        background: linear-gradient(90deg, #003A8C, #0057D9);
        color: white;
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 16px;
        margin: 20px 0 12px 0;
    }
    .news-card {
        border: 1px solid #DBEAFE;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        background: #F8FBFF;
    }
    .industry-header {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 8px 14px;
        border-radius: 0 8px 8px 0;
        margin: 16px 0 10px 0;
        font-weight: 700;
        color: #1E3A5F;
    }
    .entity-tag {
        display: inline-block;
        background: #DBEAFE;
        color: #1E40AF;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        margin: 2px;
    }
    .sap-alert {
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        color: #9A3412;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Hero
# =========================
st.markdown("""
<div class="sap-hero">
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
        <div style="background:#fff; color:#0057D9; border-radius:8px;
                    font-weight:700; padding:8px 12px; font-size:18px;">SAP</div>
        <div style="font-weight:600; opacity:.9; font-size:15px;">
            Operations Team · Newsletter Intelligence
        </div>
    </div>
    <h1 style="margin:0; font-size:38px; line-height:1.05;">Newsletter por País</h1>
    <p style="margin:10px 0 16px 0; font-size:16px; opacity:.92;">
        Noticias reales · Segmentadas por industria · Cuentas nuevas · Envío por Outlook
    </p>
    <span class="sap-badge">🇦🇷 Argentina</span>
    <span class="sap-badge">🇨🇱 Chile</span>
    <span class="sap-badge">🇵🇪 Perú</span>
    <span class="sap-badge">🇨🇴 Colombia</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sap-alert">
    <b>⚠ Aviso:</b> Las noticias se obtienen de Google News RSS (fuentes reales).
    El análisis ejecutivo es generado por IA. Valida siempre antes del envío.
</div>
""", unsafe_allow_html=True)

# =========================
# Claude API
# =========================
def get_api_key() -> Optional[str]:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    import os
    return os.getenv("ANTHROPIC_API_KEY")


def call_claude(prompt: str, max_tokens: int = 2048) -> str:
    api_key = get_api_key()
    if not api_key:
        st.error("❌ API Key no configurada. Agrega ANTHROPIC_API_KEY en Secrets.")
        st.stop()
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# =========================
# Google News RSS - Noticias reales
# =========================
def search_google_news(query: str, country_code: str = "", max_results: int = 10) -> List[Dict]:
    """Busca noticias reales en Google News RSS."""
    # Mapeo de país a código de Google News
    country_gl = {
        "ARGENTINA": "AR",
        "CHILE": "CL",
        "PERU": "PE",
        "COLOMBIA": "CO"
    }
    country_hl = {
        "ARGENTINA": "es-419",
        "CHILE": "es-419",
        "PERU": "es-419",
        "COLOMBIA": "es-419"
    }

    gl = country_gl.get(country_code, "")
    hl = country_hl.get(country_code, "es-419")

    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl={hl}&gl={gl}&ceid={gl}:es-419"

    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:max_results]:
            # Extraer fuente del título (Google News format: "Título - Fuente")
            title = entry.get("title", "")
            source = ""
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1] if len(parts) > 1 else ""

            pub_date = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    from time import mktime
                    dt = datetime.fromtimestamp(mktime(entry.published_parsed))
                    pub_date = dt.strftime("%d/%m/%Y")
                except Exception:
                    pub_date = entry.get("published", "")[:10]

            results.append({
                "title": title,
                "source": source,
                "url": entry.get("link", ""),
                "date": pub_date,
                "summary": entry.get("summary", "")[:200]
            })
        return results
    except Exception as e:
        st.warning(f"Error buscando noticias para '{query}': {str(e)}")
        return []


def search_industry_news(industry: str, country: str,
                         existing_entities: Set[str] = None,
                         max_results: int = 10) -> List[Dict]:
    """Busca noticias de empresas específicas del sector en el país:
    inversiones, expansiones, licitaciones, fusiones, levantamiento de capital, etc.
    El objetivo es encontrar empresas que sean potenciales clientes nuevos."""

    # Mapeo de industrias a términos del sector
    industry_search_terms = {
        "Aerospace and Defense": "aeroespacial defensa",
        "Agribusiness": "agroindustria agro exportaciones",
        "Automotive": "automotriz concesionaria vehículos",
        "Banking": "banco fintech financiera",
        "Chemicals": "química petroquímica",
        "Consumer Products": "consumo masivo alimentos bebidas",
        "Engineering, Construction, and O": "construcción ingeniería infraestructura",
        "Healthcare": "salud clínica hospital",
        "Higher Education and Research": "universidad educación superior",
        "Industrial Manufacturing": "manufactura industrial planta",
        "Insurance": "seguro aseguradora",
        "Life Sciences": "farmacéutica laboratorio biotecnología",
        "Media": "medios comunicación digital",
        "Mill Products and Mining": "minería metalurgia acero litio",
        "Oil, Gas, and Energy": "petróleo gas energía renovable",
        "Professional Services": "servicios consultoría tecnología",
        "Public Sector": "gobierno licitación concesión",
        "Retail": "retail tienda ecommerce comercio",
        "Telecommunications": "telecomunicaciones telecom fibra 5G",
        "Travel and Transportation": "transporte logística aviación naviera",
        "Utilities": "electricidad agua servicios sanitarios",
        "Wholesale Distribution": "distribución mayorista cadena suministro"
    }

    # Términos de eventos corporativos que indican potencial cliente nuevo
    business_event_terms = [
        "inversión millones", "levantó capital", "recibió financiamiento",
        "inauguró planta", "abrió operaciones", "nueva empresa", "startup",
        "fusión adquisición", "expansión", "licitación adjudicó",
        "contrato millones", "proyecto nuevo", "empresa ingresa",
        "emprendimiento", "ronda de inversión", "fondo invirtió"
    ]

    country_names = {
        "ARGENTINA": "Argentina",
        "CHILE": "Chile",
        "PERU": "Perú",
        "COLOMBIA": "Colombia"
    }

    sector = industry_search_terms.get(industry, industry)
    country_name = country_names.get(country, country)

    all_news = []
    seen_titles = set()

    # Query principal: empresas específicas con eventos corporativos relevantes
    queries = [
        f"empresa {sector} {country_name} inversión expansión 2025",
        f"empresa {sector} {country_name} nuevo proyecto financiamiento 2025",
        f"startup empresa {sector} {country_name} capital 2025",
    ]

    for query in queries:
        raw = search_google_news(query, country, max_results=max_results)
        for news in raw:
            t = news["title"].lower()
            if t not in seen_titles:
                seen_titles.add(t)
                news["industry"] = industry
                all_news.append(news)

    return all_news[:max_results]


# =========================
# Profundizar noticia con Claude
# =========================
def deepen_news_item(title: str, source: str, industry: str, country: str) -> str:
    prompt = (
        f"Eres un analista comercial B2B especializado en identificar oportunidades de negocio.\n\n"
        f"Noticia: \"{title}\"\n"
        f"Fuente: {source}\n"
        f"País: {country}\n"
        f"Industria: {industry}\n\n"
        f"Escribe un análisis ejecutivo breve y directo en 3-4 oraciones:\n"
        f"- Qué está ocurriendo con esta empresa o en este sector\n"
        f"- Por qué es relevante como señal de mercado o oportunidad de prospección\n"
        f"- Qué tipo de empresa o perfil aparece como potencial cliente\n\n"
        f"Tono profesional, sin etiquetas ni subtítulos. Solo párrafo corrido. Máximo 80 palabras."
    )
    return call_claude(prompt, max_tokens=300)


# =========================
# Construir HTML del newsletter
# =========================
def build_news_item_html(item: Dict, deep_text: str) -> str:
    analysis_block = ""
    if deep_text:
        clean = " ".join(l.strip() for l in deep_text.split("\n") if l.strip())
        analysis_block = (
            f"<p style='margin:10px 0 0 0; font-size:13px; color:#374151; "
            f"line-height:1.6; border-top:1px solid #E5E7EB; padding-top:10px;'>"
            f"{clean}</p>"
        )

    source = item.get("source", "")
    date = item.get("date", "")
    industry = item.get("industry", "")
    meta_parts = []
    if source: meta_parts.append(f"<b>{source}</b>")
    if date: meta_parts.append(date)
    if industry: meta_parts.append(industry)
    meta_html = " &middot; ".join(meta_parts)

    return (
        f"<table width='100%' cellpadding='0' cellspacing='0' "
        f"style='border:1px solid #E5E7EB; border-radius:10px; "
        f"margin-bottom:14px; background:#FFFFFF; border-collapse:separate;'>"
        f"<tr><td style='padding:16px 20px;'>"
        f"<a href='{item['url']}' style='color:#1E40AF; text-decoration:none; "
        f"font-weight:700; font-size:15px; line-height:1.5; display:block;'>"
        f"{item['title']}</a>"
        f"<p style='margin:6px 0 0 0; color:#9CA3AF; font-size:11px; "
        f"text-transform:uppercase; letter-spacing:.4px;'>{meta_html}</p>"
        + analysis_block +
        f"</td></tr></table>"
    )


def build_full_newsletter_html(
    country: str,
    news_by_industry: Dict[str, List[Dict]],
    deep_content: Dict[str, str],
    sender_name: str,
    aes: List[str]
) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    week_num = datetime.now().isocalendar()[1]
    flag = COUNTRY_FLAGS.get(country, "🌎")
    display_name = COUNTRY_DISPLAY.get(country, country)
    total_news = sum(len(v) for v in news_by_industry.values())
    industries_count = len([v for v in news_by_industry.values() if v])

    # --- Noticias por industria ---
    sections_html = ""
    for industry in sorted(news_by_industry.keys()):
        items = news_by_industry[industry]
        if not items:
            continue
        items_html = ""
        for item in items:
            key = f"{country}_{industry}_{item['title'][:50]}"
            deep_text = deep_content.get(key, "")
            items_html += build_news_item_html(item, deep_text)

        sections_html += f"""
        <tr><td style="padding:0 0 32px 0;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding:0 0 14px 0;">
                <table width="100%" cellpadding="0" cellspacing="0"
                       style="border-bottom:2px solid #1E40AF;">
                  <tr>
                    <td style="padding:0 0 8px 0; font-family:Arial,sans-serif;
                               font-size:11px; font-weight:700; color:#1E40AF;
                               text-transform:uppercase; letter-spacing:1px;">
                      {industry}
                    </td>
                    <td align="right" style="padding:0 0 8px 0; font-family:Arial,sans-serif;
                                             font-size:11px; color:#9CA3AF;">
                      {len(items)} noticia{"s" if len(items) != 1 else ""}
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr><td>{items_html}</td></tr>
          </table>
        </td></tr>"""

    # --- AEs chips ---
    ae_chips = "".join(
        f"<span style='display:inline-block; background:#EFF6FF; color:#1E40AF; "
        f"border:1px solid #BFDBFE; border-radius:20px; padding:3px 11px; "
        f"font-size:11px; font-weight:600; margin:3px 4px 3px 0;'>{ae}</span>"
        for ae in sorted(aes)
    )

    # --- Estadísticas del header ---
    stats_html = f"""
    <table cellpadding="0" cellspacing="0" style="margin-top:20px;">
      <tr>
        <td style="padding-right:32px;">
          <div style="font-size:28px; font-weight:700; color:#fff;">{total_news}</div>
          <div style="font-size:11px; color:rgba(255,255,255,.7); text-transform:uppercase;
                      letter-spacing:.5px;">Noticias</div>
        </td>
        <td style="padding-right:32px; border-left:1px solid rgba(255,255,255,.2);
                   padding-left:32px;">
          <div style="font-size:28px; font-weight:700; color:#fff;">{industries_count}</div>
          <div style="font-size:11px; color:rgba(255,255,255,.7); text-transform:uppercase;
                      letter-spacing:.5px;">Industrias</div>
        </td>
        <td style="border-left:1px solid rgba(255,255,255,.2); padding-left:32px;">
          <div style="font-size:28px; font-weight:700; color:#fff;">{len(aes)}</div>
          <div style="font-size:11px; color:rgba(255,255,255,.7); text-transform:uppercase;
                      letter-spacing:.5px;">AEs</div>
        </td>
      </tr>
    </table>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SAP Newsletter · {flag} {display_name} · Semana {week_num}</title>
</head>
<body style="margin:0; padding:0; background:#F3F4F6;">

<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#F3F4F6; padding:32px 16px;">
  <tr><td align="center">

    <!-- Contenedor principal 680px -->
    <table width="680" cellpadding="0" cellspacing="0"
           style="max-width:680px; width:100%;">

      <!-- ═══ HEADER ═══ -->
      <tr>
        <td style="background:#0F172A; border-radius:14px 14px 0 0;
                   padding:32px 40px 28px 40px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>
                <table cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="background:#2563EB; border-radius:6px;
                               padding:5px 11px; font-family:Arial,sans-serif;
                               font-size:13px; font-weight:700; color:#fff;
                               letter-spacing:.5px;">SAP</td>
                    <td style="padding-left:10px; font-family:Arial,sans-serif;
                               font-size:12px; color:rgba(255,255,255,.55);
                               text-transform:uppercase; letter-spacing:.8px;">
                      Operations Team
                    </td>
                  </tr>
                </table>
                <h1 style="margin:16px 0 4px 0; font-family:Arial,sans-serif;
                            font-size:26px; font-weight:700; color:#FFFFFF;
                            line-height:1.2;">
                  {flag} Newsletter de Prospección
                </h1>
                <p style="margin:0; font-family:Arial,sans-serif; font-size:14px;
                           color:rgba(255,255,255,.6);">
                  {display_name} &middot; Semana {week_num} &middot; {today}
                </p>
                {stats_html}
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- ═══ INTRO ═══ -->
      <tr>
        <td style="background:#1E293B; padding:20px 40px;">
          <p style="margin:0; font-family:Arial,sans-serif; font-size:13px;
                     color:rgba(255,255,255,.75); line-height:1.7;">
            Estimado equipo comercial, a continuación encontrarán noticias de
            <strong style="color:#93C5FD;">empresas con señales de crecimiento</strong>
            — inversiones, expansiones, nuevos proyectos y financiamiento —
            organizadas por industria. Estas representan oportunidades de prospección
            de clientes nuevos en {display_name}.
          </p>
        </td>
      </tr>

      <!-- ═══ AEs ═══ -->
      <tr>
        <td style="background:#1E293B; padding:0 40px 24px 40px;
                   border-bottom:3px solid #2563EB;">
          <p style="margin:0 0 8px 0; font-family:Arial,sans-serif; font-size:10px;
                     font-weight:700; color:rgba(255,255,255,.4); text-transform:uppercase;
                     letter-spacing:1px;">Account Executives</p>
          {ae_chips.replace("#EFF6FF", "#1E3A5F").replace("#1E40AF", "#93C5FD").replace("#BFDBFE", "#2563EB")}
        </td>
      </tr>

      <!-- ═══ NOTICIAS ═══ -->
      <tr>
        <td style="background:#FFFFFF; padding:32px 40px 8px 40px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            {sections_html}
          </table>
        </td>
      </tr>

      <!-- ═══ FOOTER ═══ -->
      <tr>
        <td style="background:#F8FAFC; border:1px solid #E5E7EB;
                   border-top:none; border-radius:0 0 14px 14px;
                   padding:20px 40px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="font-family:Arial,sans-serif; font-size:11px;
                          color:#9CA3AF; line-height:1.6;">
                Newsletter generado con asistencia de IA por <strong>{sender_name}</strong>
                &middot; Las noticias provienen de Google News &middot;
                El análisis es generado por IA, validar antes del envío.
              </td>
              <td align="right" style="font-family:Arial,sans-serif; font-size:11px;
                                        color:#CBD5E1; white-space:nowrap; padding-left:20px;">
                SAP &copy; {datetime.now().year}
              </td>
            </tr>
          </table>
        </td>
      </tr>

    </table>
    <!-- /Contenedor -->

  </td></tr>
</table>
</body>
</html>"""

    return html


def build_plain_text_newsletter(
    country: str,
    news_by_industry: Dict[str, List[Dict]],
    deep_content: Dict[str, str],
    sender_name: str,
    aes: List[str]
) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    flag = COUNTRY_FLAGS.get(country, "🌎")
    display_name = COUNTRY_DISPLAY.get(country, country)

    lines = []
    lines.append("=" * 60)
    lines.append(f"SAP OPERATIONS TEAM - NEWSLETTER SEMANAL")
    lines.append(f"{flag} {display_name.upper()}")
    lines.append(f"Edición: {today}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Estimado equipo comercial de {display_name},")
    lines.append("")
    lines.append(
        "A continuación las noticias de EMPRESAS CON SEÑALES DE CRECIMIENTO "
        "(inversiones, expansiones, nuevos proyectos) como oportunidades de prospección."
    )
    lines.append("")
    lines.append(f"AEs del país: {', '.join(aes[:10])}")
    lines.append("")

    for industry in sorted(news_by_industry.keys()):
        items = news_by_industry[industry]
        if not items:
            continue

        lines.append("-" * 60)
        lines.append(f"🏭 {industry.upper()}")
        lines.append("-" * 60)

        for i, item in enumerate(items, 1):
            lines.append(f"\n{i}. {item['title']}")
            lines.append(f"   Fuente: {item['source']} | {item.get('date', '')}")
            lines.append(f"   Link: {item['url']}")

            key = f"{country}_{industry}_{item['title'][:50]}"
            deep = deep_content.get(key, "")
            if deep:
                lines.append("")
                for l in deep.split("\n"):
                    if l.strip():
                        lines.append(f"   {l.strip()}")

        lines.append("")

    lines.append("=" * 60)
    lines.append(f"Generado por: {sender_name}")
    lines.append(f"SAP Operations Team · {today}")
    lines.append("=" * 60)

    return "\n".join(lines)


# =========================
# Mailto para Outlook
# =========================
def build_mailto_link(
    to_emails: List[str],
    cc_emails: List[str],
    subject: str,
    body_plain: str
) -> str:
    to = ";".join(to_emails)
    cc = ";".join(cc_emails)
    subject_enc = urllib.parse.quote(subject)
    body_enc = urllib.parse.quote(body_plain[:8000])
    return f"mailto:{to}?cc={cc}&subject={subject_enc}&body={body_enc}"


# =========================
# SESSION STATE
# =========================
if "territory_data" not in st.session_state:
    st.session_state.territory_data = load_territory_data()
if "selected_country" not in st.session_state:
    st.session_state.selected_country = None
if "country_info" not in st.session_state:
    st.session_state.country_info = None
if "headlines_by_industry" not in st.session_state:
    st.session_state.headlines_by_industry = {}
if "selected_news_by_industry" not in st.session_state:
    st.session_state.selected_news_by_industry = {}
if "deep_content" not in st.session_state:
    st.session_state.deep_content = {}
if "newsletter_html" not in st.session_state:
    st.session_state.newsletter_html = ""
if "newsletter_plain" not in st.session_state:
    st.session_state.newsletter_plain = ""
if "phase" not in st.session_state:
    st.session_state.phase = 1
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("---")

    sender_name = st.text_input(
        "Tu nombre",
        value="Equipo de Operaciones SAP",
        help="Aparecerá en la firma del newsletter"
    )

    st.markdown("---")
    st.markdown("### 🌎 Seleccionar País")

    country_options = {
        "🇦🇷 Argentina": "ARGENTINA",
        "🇨🇱 Chile": "CHILE",
        "🇵🇪 Perú": "PERU",
        "🇨🇴 Colombia": "COLOMBIA"
    }

    selected_display = st.radio(
        "País para el newsletter:",
        options=list(country_options.keys()),
        index=0
    )
    selected_country = country_options[selected_display]

    # Cargar datos del país
    if selected_country != st.session_state.selected_country:
        st.session_state.selected_country = selected_country
        st.session_state.country_info = get_country_data(
            st.session_state.territory_data, selected_country
        )
        # Reset phases
        st.session_state.headlines_by_industry = {}
        st.session_state.selected_news_by_industry = {}
        st.session_state.deep_content = {}
        st.session_state.newsletter_html = ""
        st.session_state.newsletter_plain = ""
        st.session_state.search_completed = False
        st.session_state.phase = 1

    country_info = st.session_state.country_info

    if country_info:
        st.markdown("---")
        st.markdown("### 📊 Datos del País")
        st.metric("Account Executives", len(country_info["aes"]))
        st.metric("Industrias", len(country_info["industries"]))

        with st.expander("👥 AEs del país"):
            for ae in country_info["aes"]:
                email = AE_EMAILS.get(ae, "")
                if email:
                    st.markdown(f"- **{ae}** · `{email}`")
                else:
                    st.markdown(f"- **{ae}**")

        with st.expander("🏭 Industrias"):
            for ind in country_info["industries"]:
                aes_in = country_info["aes_by_industry"].get(ind, [])
                st.markdown(f"- {ind} ({len(aes_in)} AE{'s' if len(aes_in) != 1 else ''})")

    st.markdown("---")
    st.markdown("### 📧 Con copia (CC)")
    active_cc = []
    for email in CC_EMAILS:
        if st.checkbox(email, value=True, key=f"cc_{email}"):
            active_cc.append(email)

    st.markdown("---")
    st.caption("💡 API Key: configura `ANTHROPIC_API_KEY` en Streamlit Secrets")


# =========================
# FASE 1 · Seleccionar industrias y buscar
# =========================
if country_info:
    display_name = COUNTRY_DISPLAY.get(selected_country, selected_country)
    flag = COUNTRY_FLAGS.get(selected_country, "🌎")

    st.markdown(
        f"<div class='step-header'>📡 Paso 1 · Buscar noticias de cuentas nuevas "
        f"en {flag} {display_name}</div>",
        unsafe_allow_html=True
    )

    # Selección de industrias
    st.markdown("**Selecciona las industrias para buscar noticias:**")

    selected_industries = []
    cols = st.columns(3)
    for i, ind in enumerate(country_info["industries"]):
        col_idx = i % 3
        with cols[col_idx]:
            if st.checkbox(ind, value=True, key=f"ind_sel_{ind}"):
                selected_industries.append(ind)

    st.markdown("---")

    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(
            f"Se buscarán noticias de **empresas con eventos corporativos relevantes** "
            f"(inversiones, expansiones, nuevos proyectos, financiamiento) en {display_name}. "
            f"Máximo 10 noticias por industria."
        )
    with col_btn:
        buscar = st.button(
            "🔍 Buscar Noticias",
            type="primary",
            use_container_width=True,
            disabled=not selected_industries
        )

    if buscar:
        st.session_state.headlines_by_industry = {}
        st.session_state.selected_news_by_industry = {}
        st.session_state.deep_content = {}
        st.session_state.newsletter_html = ""
        st.session_state.newsletter_plain = ""

        progress = st.progress(0, text="Iniciando búsqueda...")
        total_ind = len(selected_industries)

        for i, industry in enumerate(selected_industries):
            pct = int((i / total_ind) * 100)
            progress.progress(pct, text=f"Buscando: {industry}...")

            news = search_industry_news(
                industry=industry,
                country=selected_country,
                max_results=10
            )

            if news:
                st.session_state.headlines_by_industry[industry] = news

        progress.progress(100, text="✅ Búsqueda completada")
        st.session_state.search_completed = True
        st.session_state.phase = 2
        st.rerun()


# =========================
# FASE 2 · Selección de noticias
# =========================
if st.session_state.search_completed and st.session_state.headlines_by_industry:
    display_name = COUNTRY_DISPLAY.get(selected_country, selected_country)
    flag = COUNTRY_FLAGS.get(selected_country, "🌎")

    total_found = sum(len(v) for v in st.session_state.headlines_by_industry.values())
    industries_with_news = len(st.session_state.headlines_by_industry)

    st.markdown(
        f"<div class='step-header'>✅ Paso 2 · Selecciona noticias para el newsletter "
        f"({total_found} encontradas en {industries_with_news} industrias)</div>",
        unsafe_allow_html=True
    )

    total_selected = 0

    for industry in sorted(st.session_state.headlines_by_industry.keys()):
        news_list = st.session_state.headlines_by_industry[industry]
        if not news_list:
            continue

        # Header de industria
        aes_in_industry = country_info["aes_by_industry"].get(industry, [])
        aes_str = ", ".join(aes_in_industry[:5])
        if len(aes_in_industry) > 5:
            aes_str += f" +{len(aes_in_industry) - 5}"

        st.markdown(
            f"<div class='industry-header'>"
            f"🏭 {industry} "
            f"<span style='font-weight:400; font-size:12px; color:#6B7280;'>"
            f"({len(news_list)} noticias · AEs: {aes_str})</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        for idx, item in enumerate(news_list):
            key_cb = f"sel_{industry}_{idx}"

            col_check, col_info = st.columns([0.5, 9.5])

            with col_check:
                selected = st.checkbox("", key=key_cb, label_visibility="collapsed")

            with col_info:
                summary_text = ""
                if item.get("summary"):
                    summary_text = (
                        f"<p style='color:#4B5563; font-size:12px; margin-top:6px; "
                        f"font-style:italic;'>{item['summary'][:150]}...</p>"
                    )

                st.markdown(
                    f"<div class='news-card'>"
                    f"<div style='font-weight:600; color:#1E3A5F; font-size:14px;'>"
                    f"{item['title']}</div>"
                    f"<div style='color:#6B7280; font-size:12px; margin-top:4px;'>"
                    f"📰 {item['source']} &nbsp;|&nbsp; "
                    f"📅 {item.get('date', 'Reciente')} &nbsp;|&nbsp; "
                    f"<a href='{item['url']}' target='_blank' "
                    f"style='color:#3B82F6;'>Ver fuente ↗</a>"
                    f"</div>"
                    f"{summary_text}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            if selected:
                total_selected += 1
                if industry not in st.session_state.selected_news_by_industry:
                    st.session_state.selected_news_by_industry[industry] = []
                titles_in = [
                    n['title']
                    for n in st.session_state.selected_news_by_industry[industry]
                ]
                if item['title'] not in titles_in:
                    st.session_state.selected_news_by_industry[industry].append(item)
            else:
                if industry in st.session_state.selected_news_by_industry:
                    st.session_state.selected_news_by_industry[industry] = [
                        n for n in st.session_state.selected_news_by_industry[industry]
                        if n['title'] != item['title']
                    ]

        st.markdown("---")

    # Botón generar
    if total_selected > 0:
        st.info(
            f"📌 **{total_selected} noticia(s) seleccionada(s)**. "
            f"Haz clic en 'Generar Newsletter' para que la IA profundice cada una."
        )

        st.markdown(
            "<div class='step-header'>🤖 Paso 3 · Generar Newsletter con análisis IA</div>",
            unsafe_allow_html=True
        )

        col_gen1, col_gen2 = st.columns([2, 1])
        with col_gen1:
            st.markdown(
                "La IA analizará cada noticia seleccionada e identificará por qué "
                "la empresa es un prospecto potencial (señales de inversión, expansión, etc.)."
            )
        with col_gen2:
            generar = st.button(
                "🚀 Generar Newsletter",
                type="primary",
                use_container_width=True
            )

        if generar:
            progress = st.progress(0, text="Iniciando análisis con IA...")

            all_items = []
            for industry, items in st.session_state.selected_news_by_industry.items():
                for item in items:
                    all_items.append((industry, item))

            total = len(all_items)

            for i, (industry, item) in enumerate(all_items):
                pct = int((i / total) * 100)
                progress.progress(
                    pct,
                    text=f"Analizando ({i+1}/{total}): {item['title'][:50]}..."
                )

                key = f"{selected_country}_{industry}_{item['title'][:50]}"
                if key not in st.session_state.deep_content:
                    deep = deepen_news_item(
                        title=item['title'],
                        source=item['source'],
                        industry=industry,
                        country=COUNTRY_DISPLAY.get(selected_country, selected_country)
                    )
                    st.session_state.deep_content[key] = deep

            progress.progress(100, text="✅ Análisis completado. Generando newsletter...")

            st.session_state.newsletter_html = build_full_newsletter_html(
                country=selected_country,
                news_by_industry=st.session_state.selected_news_by_industry,
                deep_content=st.session_state.deep_content,
                sender_name=sender_name,
                aes=country_info["aes"]
            )
            st.session_state.newsletter_plain = build_plain_text_newsletter(
                country=selected_country,
                news_by_industry=st.session_state.selected_news_by_industry,
                deep_content=st.session_state.deep_content,
                sender_name=sender_name,
                aes=country_info["aes"]
            )
            st.session_state.phase = 3
            st.rerun()
    else:
        st.warning("☝️ Selecciona al menos una noticia para continuar.")


# =========================
# FASE 3 · Preview y envío
# =========================
if st.session_state.newsletter_html:
    display_name = COUNTRY_DISPLAY.get(selected_country, selected_country)
    flag = COUNTRY_FLAGS.get(selected_country, "🌎")

    st.markdown(
        f"<div class='step-header'>📧 Paso 4 · Preview y envío - "
        f"{flag} {display_name}</div>",
        unsafe_allow_html=True
    )

    tab_preview, tab_html, tab_plain = st.tabs(
        ["👁️ Vista previa", "🔤 HTML", "📄 Texto plano"]
    )

    with tab_preview:
        st.markdown(
            "<div style='border:2px solid #BFDBFE; border-radius:14px; overflow:hidden; "
            "margin-top:12px;'>" +
            st.session_state.newsletter_html +
            "</div>",
            unsafe_allow_html=True
        )

    with tab_html:
        st.code(st.session_state.newsletter_html, language="html")
        st.download_button(
            label="⬇️ Descargar HTML",
            data=st.session_state.newsletter_html,
            file_name=f"newsletter_sap_{display_name}_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html"
        )

    with tab_plain:
        st.text_area(
            "Texto plano del newsletter",
            value=st.session_state.newsletter_plain,
            height=400
        )
        st.download_button(
            label="⬇️ Descargar TXT",
            data=st.session_state.newsletter_plain,
            file_name=f"newsletter_sap_{display_name}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

    # --- Sección de envío ---
    st.markdown("---")
    st.markdown(f"### 📤 Enviar por Outlook - {flag} {display_name}")

    # Obtener emails de AEs del país
    ae_emails_for_country = []
    for ae in country_info["aes"]:
        email = AE_EMAILS.get(ae, "")
        if email:
            ae_emails_for_country.append(email)

    col_mail1, col_mail2 = st.columns(2)

    with col_mail1:
        st.markdown("**Destinatarios (Para) - AEs del país:**")
        selected_to = []
        for email in ae_emails_for_country:
            if st.checkbox(email, value=True, key=f"to_send_{email}"):
                selected_to.append(email)

    with col_mail2:
        st.markdown("**Con copia (CC):**")
        for email in active_cc:
            st.markdown(f"- `{email}`")

    # Asunto
    today_str = datetime.now().strftime("%d/%m/%Y")
    total_news_final = sum(
        len(v) for v in st.session_state.selected_news_by_industry.values()
    )
    default_subject = (
        f"SAP Newsletter Semanal · {display_name} · {today_str} · "
        f"{total_news_final} noticias - Cuentas Nuevas"
    )

    email_subject = st.text_input(
        "✏️ Asunto del correo",
        value=default_subject,
        help="Puedes editar el asunto antes de abrir Outlook"
    )

    st.markdown("""
    <div style='background:#EFF6FF; border:1px solid #BFDBFE; color:#1E40AF;
                padding:12px 16px; border-radius:10px; margin:12px 0; font-size:13px;'>
        <b>💡 Opciones de envío:</b><br>
        - <b>Opción A:</b> Abre Outlook con texto plano (compatibilidad máxima).<br>
        - <b>Opción B:</b> Descarga HTML, ábrelo en navegador, copia y pega en Outlook
          para formato visual completo.
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if selected_to:
            mailto_link = build_mailto_link(
                to_emails=selected_to,
                cc_emails=active_cc,
                subject=email_subject,
                body_plain=st.session_state.newsletter_plain
            )
            st.markdown(
                f"<a href='{mailto_link}' "
                f"style='display:block; text-align:center; background:#0078D4; "
                f"color:white; padding:12px 20px; border-radius:10px; "
                f"text-decoration:none; font-weight:700; font-size:14px; "
                f"box-shadow:0 4px 14px rgba(0,120,212,.35);'>"
                f"📧 Abrir en Outlook</a>",
                unsafe_allow_html=True
            )
        else:
            st.button("📧 Abrir en Outlook", disabled=True)
            st.caption("Selecciona al menos un destinatario.")

    with col_btn2:
        st.download_button(
            label="⬇️ Descargar HTML",
            data=st.session_state.newsletter_html,
            file_name=f"newsletter_{display_name}_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )

    with col_btn3:
        if st.button(
            "🔄 Nuevo Newsletter",
            use_container_width=True,
            help="Limpia todo y comienza desde cero"
        ):
            for key in [
                "headlines_by_industry", "selected_news_by_industry",
                "deep_content"
            ]:
                st.session_state[key] = {}
            st.session_state.newsletter_html = ""
            st.session_state.newsletter_plain = ""
            st.session_state.search_completed = False
            st.session_state.phase = 1
            st.rerun()

    # --- Instrucciones HTML en Outlook ---
    with st.expander("📋 ¿Cómo pegar el HTML con formato en Outlook?"):
        st.markdown("""
        **Pasos para enviar con formato visual completo:**

        1. Haz clic en **⬇️ Descargar HTML** para guardar el archivo.
        2. Abre el archivo `.html` en tu navegador (Chrome, Edge, Firefox).
        3. Selecciona todo: `Ctrl + A`
        4. Copia: `Ctrl + C`
        5. Abre un **nuevo correo en Outlook**.
        6. Pega: `Ctrl + V` en el cuerpo del mensaje.
        7. Completa destinatarios y asunto.
        8. ¡Envía! 🚀

        > **Tip:** Asegúrate de que Outlook esté en modo **HTML**
        > (no texto plano) para conservar el formato.
        """)

    # --- Resumen final ---
    st.markdown("---")
    st.markdown(f"### 📊 Resumen del Newsletter - {flag} {display_name}")

    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.metric("Total noticias", total_news_final)
    with summary_cols[1]:
        st.metric(
            "Industrias cubiertas",
            len([v for v in st.session_state.selected_news_by_industry.values() if v])
        )
    with summary_cols[2]:
        st.metric("AEs destinatarios", len(selected_to) if selected_to else 0)

    # Detalle por industria
    for industry in sorted(st.session_state.selected_news_by_industry.keys()):
        items = st.session_state.selected_news_by_industry[industry]
        if not items:
            continue

        with st.expander(f"🏭 {industry} · {len(items)} noticia(s)"):
            for item in items:
                key = f"{selected_country}_{industry}_{item['title'][:50]}"
                deep = st.session_state.deep_content.get(key, "")

                st.markdown(
                    f"<div style='border:1px solid #DBEAFE; border-radius:10px;"
                    f"padding:14px 16px; margin-bottom:10px; background:#F8FBFF;'>"
                    f"<b style='color:#1E3A5F;'>{item['title']}</b><br>"
                    f"<span style='color:#6B7280; font-size:12px;'>"
                    f"📰 {item['source']} | 📅 {item.get('date', 'Reciente')} | "
                    f"<a href='{item['url']}' target='_blank' "
                    f"style='color:#3B82F6;'>Ver fuente ↗</a>"
                    f"</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                if deep:
                    with st.expander("Ver análisis ejecutivo", expanded=False):
                        st.markdown(deep)

else:
    if not st.session_state.search_completed and not st.session_state.headlines_by_industry:
        st.markdown("---")
        st.info(
            "👈 Selecciona un país en el sidebar y haz clic en "
            "'🔍 Buscar Noticias' para comenzar."
        )


# =========================
# Footer
# =========================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#9CA3AF; font-size:12px; padding:10px 0;'>"
    "SAP Operations Team · Newsletter Intelligence · "
    "Noticias reales via Google News RSS · Made By Pedro Inostroza · "
    + datetime.now().strftime("%Y") +
    "</div>",
    unsafe_allow_html=True
)
