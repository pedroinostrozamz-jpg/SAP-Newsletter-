import streamlit as st
import anthropic
import urllib.parse
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

# =========================
# Configuración de página
# =========================
st.set_page_config(
    page_title="Newsletter SAP",
    page_icon="📰",
    layout="wide"
)

# =========================
# Datos base
# =========================
COUNTRIES = ["Argentina", "Chile", "Perú", "Colombia"]

AE_EMAILS: Dict[str, List[str]] = {
    "Argentina": ["ae.argentina1@sap.com", "ae.argentina2@sap.com"],
    "Chile":     ["ae.chile1@sap.com",     "ae.chile2@sap.com"],
    "Perú":      ["ae.peru1@sap.com",       "ae.peru2@sap.com"],
    "Colombia":  ["ae.colombia1@sap.com",   "ae.colombia2@sap.com"],
}

CC_EMAILS = ["operaciones@sap.com", "lider.comercial@sap.com"]

INDUSTRIES = [
    "Tecnología y Software Empresarial",
    "Manufactura e Industria",
    "Retail y Consumo Masivo",
    "Banca y Servicios Financieros",
    "Energía y Recursos Naturales",
    "Logística y Cadena de Suministro",
    "Agroindustria",
    "Telecomunicaciones",
]

# =========================
# Estilos
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
    .sap-alert {
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        color: #9A3412;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-size: 14px;
    }
    .news-card {
        border: 1px solid #DBEAFE;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        background: #F8FBFF;
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
    .email-preview {
        border: 2px solid #BFDBFE;
        border-radius: 14px;
        overflow: hidden;
        margin-top: 12px;
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
    <h1 style="margin:0; font-size:38px; line-height:1.05;">Newsletter Semanal</h1>
    <p style="margin:10px 0 16px 0; font-size:16px; opacity:.92;">
        Plataforma impulsada por IA · Noticias en tiempo real · Envío directo a Outlook
    </p>
    <span class="sap-badge">🇦🇷 Argentina</span>
    <span class="sap-badge">🇨🇱 Chile</span>
    <span class="sap-badge">🇵🇪 Perú</span>
    <span class="sap-badge">🇨🇴 Colombia</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sap-alert">
    <b>⚠ Aviso importante:</b> Las noticias son generadas por IA con base en conocimiento
    actualizado. Valida siempre con fuentes oficiales antes del envío final.
</div>
""", unsafe_allow_html=True)

# =========================
# Claude API helpers
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
        model="claude-opus-4-5",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# =========================
# Fase 1 · Buscar titulares
# =========================
def fetch_headlines(countries: List[str], industries: List[str]) -> Dict:
    today = datetime.now().strftime("%d de %B de %Y")
    countries_str  = ", ".join(countries)
    industries_str = ", ".join(industries)

    prompt = (
        f"Eres un analista de noticias empresariales especializado en Latinoamérica.\n"
        f"Hoy es {today}.\n\n"
        f"Tu tarea: generar titulares de noticias RECIENTES (no más de 30 días) sobre:\n"
        f"Países: {countries_str}\n"
        f"Industrias: {industries_str}\n\n"
        f"Reglas:\n"
        f"- Máximo 4 noticias por país, las más relevantes para empresas B2B.\n"
        f"- Solo portales confiables: Reuters, Bloomberg, Financial Times, El Financiero,\n"
        f"  La Nación, El Mercurio, Gestión, Portafolio, América Economía, Infobae Economía.\n"
        f"- El campo url debe ser la URL real del portal.\n"
        f"- Responde ÚNICAMENTE con JSON válido, sin texto adicional ni bloques markdown.\n\n"
        f"Formato exacto:\n"
        f'{{\n'
        f'  "Argentina": [\n'
        f'    {{\n'
        f'      "title": "Título de la noticia",\n'
        f'      "source": "Nombre del portal",\n'
        f'      "url": "https://...",\n'
        f'      "industry": "Industria relacionada",\n'
        f'      "date": "DD/MM/YYYY"\n'
        f'    }}\n'
        f'  ],\n'
        f'  "Chile": [],\n'
        f'  "Perú": [],\n'
        f'  "Colombia": []\n'
        f'}}'
    )

    raw = call_claude(prompt, max_tokens=3000)
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        st.error("Error al parsear respuesta de Claude. Intenta nuevamente.")
        return {c: [] for c in countries}


# =========================
# Fase 2 · Profundizar noticia
# =========================
def deepen_news_item(title: str, source: str, industry: str, country: str) -> str:
    prompt = (
        f"Eres un analista de negocios senior especializado en tecnología empresarial y SAP.\n\n"
        f"Noticia: \"{title}\"\n"
        f"Fuente: {source}\n"
        f"País: {country}\n"
        f"Industria: {industry}\n\n"
        f"Escribe un resumen ejecutivo con exactamente estas 3 secciones:\n"
        f"CONTEXTO: (2-3 oraciones sobre qué está pasando y por qué importa)\n"
        f"IMPACTO B2B: (2-3 oraciones sobre cómo afecta a empresas medianas y grandes)\n"
        f"OPORTUNIDAD SAP: (1-2 oraciones sobre qué solución SAP es relevante)\n\n"
        f"Tono profesional y directo. Máximo 120 palabras en total.\n"
        f"Responde solo el texto con las etiquetas CONTEXTO:, IMPACTO B2B:, OPORTUNIDAD SAP:"
    )
    return call_claude(prompt, max_tokens=400)


# =========================
# Fase 3 · Construir HTML del newsletter
# =========================
def build_news_item_html(item: Dict, deep_text: str, country: str) -> str:
    deep_block = ""
    if deep_text:
        lines = [l.strip() for l in deep_text.split("\n") if l.strip()]
        paragraphs = "".join(
            "<p style='margin:4px 0; font-size:13px; color:#1F2937;'>" + l + "</p>"
            for l in lines
        )
        deep_block = (
            "<div style='background:#F0FDF4; border-left:4px solid #22C55E;"
            "border-radius:6px; padding:12px 14px; margin-top:10px;'>"
            "<p style='margin:0 0 6px 0; font-weight:700; color:#15803D;"
            "font-size:11px; text-transform:uppercase;'>📊 Análisis Ejecutivo</p>"
            + paragraphs +
            "</div>"
        )

    return (
        "<div style='border:1px solid #DBEAFE; border-radius:10px;"
        "padding:14px 16px; margin-bottom:12px; background:#F8FBFF;'>"
        "<a href='" + item['url'] + "' style='color:#1D4ED8; text-decoration:none;"
        "font-weight:700; font-size:15px; line-height:1.4;'>" + item['title'] + "</a>"
        "<p style='margin:5px 0 0 0; color:#6B7280; font-size:12px;'>"
        "📰 " + item['source'] + " &nbsp;|&nbsp; 🏭 " + item['industry'] +
        " &nbsp;|&nbsp; 📅 " + item.get('date', '') + "</p>"
        + deep_block +
        "</div>"
    )


def build_country_section_html(country: str, news_items: List[Dict],
                                deep_content: Dict, flag: str) -> str:
    if not news_items:
        return ""

    items_html = ""
    for item in news_items:
        key = country + "_" + item['title'][:50]
        deep_text = deep_content.get(key, "")
        items_html += build_news_item_html(item, deep_text, country)

    return (
        "<div style='margin-bottom:28px;'>"
        "<div style='background:linear-gradient(90deg,#003A8C,#0057D9);"
        "color:white; padding:12px 18px; border-radius:10px; margin-bottom:14px;'>"
        "<h2 style='margin:0; font-size:20px;'>" + flag + " " + country + "</h2>"
        "</div>"
        + items_html +
        "</div>"
    )


def build_full_newsletter_html(
    selected_news: Dict[str, List[Dict]],
    deep_content: Dict[str, str],
    sender_name: str
) -> str:
    today = datetime.now().strftime("%d/%m/%Y")

    flags = {
        "Argentina": "🇦🇷",
        "Chile": "🇨🇱",
        "Perú": "🇵🇪",
        "Colombia": "🇨🇴"
    }

    sections_html = ""
    for country in COUNTRIES:
        news_list = selected_news.get(country, [])
        if news_list:
            sections_html += build_country_section_html(
                country, news_list, deep_content, flags.get(country, "🌎")
            )

    total_news = sum(len(v) for v in selected_news.values())

    html = (
        "<div style='font-family:Arial,sans-serif; max-width:700px;"
        "margin:0 auto; color:#1F2937;'>"

        # Header
        "<div style='background:linear-gradient(120deg,#003A8C,#0057D9);"
        "color:white; padding:28px 32px; border-radius:14px 14px 0 0;'>"
        "<div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>"
        "<div style='background:#fff; color:#0057D9; border-radius:6px;"
        "font-weight:700; padding:6px 10px; font-size:16px;'>SAP</div>"
        "<span style='opacity:.85; font-size:14px;'>Operations Team</span>"
        "</div>"
        "<h1 style='margin:0; font-size:28px;'>Newsletter Semanal</h1>"
        "<p style='margin:6px 0 0 0; opacity:.85; font-size:14px;'>"
        "Edición: " + today + " &nbsp;|&nbsp; " + str(total_news) + " noticias seleccionadas"
        "</p>"
        "</div>"

        # Body
        "<div style='padding:24px; background:#fff; border:1px solid #DBEAFE;"
        "border-top:none; border-radius:0 0 14px 14px;'>"

        "<p style='color:#374151; font-size:15px; margin-bottom:20px;'>"
        "Estimado equipo comercial,<br><br>"
        "A continuación encontrarán las noticias más relevantes de la sem
