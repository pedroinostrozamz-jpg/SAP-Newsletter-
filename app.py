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
# Estilos SAP
# =========================
st.markdown("""
<style>
    /* ---- Hero ---- */
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
    /* ---- Alertas ---- */
    .sap-alert {
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        color: #9A3412;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-size: 14px;
    }
    .sap-info {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E40AF;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-size: 14px;
    }
    /* ---- Tarjetas de noticia ---- */
    .news-card {
        border: 1px solid #DBEAFE;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        background: #F8FBFF;
        transition: box-shadow .2s;
    }
    .news-card:hover { box-shadow: 0 4px 14px rgba(0,87,217,.12); }
    .news-title { font-weight: 600; color: #1E3A5F; font-size: 15px; }
    .news-meta  { color: #6B7280; font-size: 12px; margin-top: 4px; }
    .news-deep  {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 8px;
        font-size: 14px;
        color: #14532D;
    }
    /* ---- Steps ---- */
    .step-header {
        background: linear-gradient(90deg, #003A8C, #0057D9);
        color: white;
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 16px;
        margin: 20px 0 12px 0;
    }
    /* ---- Preview correo ---- */
    .email-preview {
        border: 2px solid #BFDBFE;
        border-radius: 14px;
        overflow: hidden;
        margin-top: 12px;
    }
    .email-header-bar {
        background: linear-gradient(120deg,#003A8C,#0057D9);
        color: white;
        padding: 16px 20px;
    }
    .email-body { padding: 20px; background: #fff; }
    /* ---- Botón Outlook ---- */
    .outlook-btn {
        display: inline-block;
        background: #0078D4;
        color: white !important;
        padding: 12px 24px;
        border-radius: 10px;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 15px;
        margin-top: 12px;
        box-shadow: 0 4px 14px rgba(0,120,212,.35);
    }
    .outlook-btn:hover { background: #005A9E; }
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
        <div style="font-weight:600; opacity:.9; font-size:15px;">Operations Team · Newsletter Intelligence</div>
    </div>
    <h1 style="margin:0; font-size:42px; line-height:1.05;">Newsletter Semanal</h1>
    <p style="margin:10px 0 16px 0; font-size:17px; opacity:.92;">
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
    <b>⚠ Aviso importante:</b> Las noticias son generadas por IA con base en conocimiento actualizado.
    Valida siempre con fuentes oficiales antes del envío final al equipo comercial.
</div>
""", unsafe_allow_html=True)

# =========================
# Claude API helper
# =========================
def get_claude_client() -> Optional[anthropic.Anthropic]:
    """Inicializa cliente Claude desde secrets de Streamlit o variable de entorno."""
    api_key = None

    # 1. Intentar desde st.secrets (GitHub + Streamlit Cloud)
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass

    # 2. Fallback: variable de entorno local
    if not api_key:
        import os
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return None

    return anthropic.Anthropic(api_key=api_key)


def call_claude(prompt: str, max_tokens: int = 2048) -> str:
    """Llama a Claude y retorna el texto de respuesta."""
    client = get_claude_client()
    if not client:
        st.error("❌ API Key de Anthropic no configurada. "
                 "Agrega ANTHROPIC_API_KEY en los Secrets de Streamlit.")
        st.stop()

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# =========================
# Fase 1 · Buscar titulares
# =========================
def fetch_headlines(countries: List[str], industries: List[str]) -> Dict[str, List[Dict]]:
    """
    Pide a Claude los titulares más recientes (≤ 1 mes) por país e industria.
    Retorna dict: { "Argentina": [ {title, source, url, industry, date}, ... ] }
    """
    today = datetime.now().strftime("%d de %B de %Y")
    countries_str  = ", ".join(countries)
    industries_str = ", ".join(industries)

    prompt = f"""
Eres un analista de noticias empresariales especializado en Latinoamérica.
Hoy es {today}.

Tu tarea: generar una lista de titulares de noticias REALES y RECIENTES (no más de 30 días de antigüedad)
sobre los siguientes países: {countries_str}
Y las siguientes industrias: {industries_str}

Reglas estrictas:
- Máximo 4 noticias por país (las más relevantes para empresas B2B).
- Solo portales confiables: Reuters, Bloomberg, Financial Times, El Financiero,
  La Nación, El Mercurio, Gestión, Portafolio, Diario Financiero, El Comercio,
  Expansión, América Economía, Infobae Economía, La República.
- Fecha de publicación dentro del último mes.
- El campo "url" debe ser la URL real del portal (homepage si no tienes la nota exacta).
- Responde ÚNICAMENTE con un JSON válido, sin texto adicional, sin markdown, sin bloques de código.

Formato exacto:
{{
  "Argentina": [
    {{
      "title": "Título de la noticia",
      "source": "Nombre del portal",
      "url": "https://...",
      "industry": "Industria relacionada",
      "date": "DD/MM/YYYY"
    }}
  ],
  "Chile": [...],
  "Perú": [...],
  "Colombia": [...]
}}
"""
    raw = call_claude(prompt, max_tokens=3000)

    # Limpiar posibles bloques markdown que Claude pueda agregar
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Intentar extraer JSON con regex como fallback
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            st.error("Error al parsear respuesta de Claude. Intenta nuevamente.")
            data = {c: [] for c in countries}

    return data


# =========================
# Fase 2 · Profundizar noticia
# =========================
def deepen_news_item(item: Dict) -> str:
    """
    Pide a Claude un resumen ejecutivo profundo de la noticia seleccionada.
    Retorna HTML listo para el newsletter.
    """
    prompt = f"""
Eres un analista de negocios senior especializado en tecnología empresarial y SAP.

Noticia: "{item['title']}"
Fuente: {item['source']}
País: se publicó en {item.get('country', 'Latinoamérica')}
Industria: {item.get('industry', 'Empresarial')}

Escribe un resumen ejecutivo de esta noticia con:
1. **Contexto** (2-3 oraciones): qué está pasando y por qué importa.
2. **Impacto en empresas B2B** (2-3 oraciones): cómo afecta a empresas medianas y grandes.
3. **Oportunidad para SAP** (1-2 oraciones): qué solución SAP es relevante aquí.

Tono: profesional, directo, sin jerga. Máximo 120 palabras en total.
Responde solo el texto, sin títulos markdown, sin asteriscos, en párrafos separados por salto de línea.
"""
    return call_claude(prompt, max_tokens=400)


# =========================
# Fase 3 · Generar newsletter HTML
# =========================
def build_newsletter_html(
    selected_news: Dict[str, List[Dict]],
    deep_content: Dict[str, str],
    sender_name: str = "Equipo de Operaciones SAP"
) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    sections = ""

    for country in COUNTRIES:
        news_list = selected_news.get(country, [])
        if not news_list:
            continue

        items_html = ""
        for item in news_list:
            key = f"{country}_{item['title'][:40]}"
            deep = deep_content.get(key, "")
            deep_block = ""
            if deep:
                # Convertir saltos de línea en párrafos
                paragraphs = "".join(
                    f"<p style='margin:6px 0;'>{p.strip()}</p>"
                    for p in deep.split("\n") if p.strip()
                )
                deep_block = f"""
                <div style="background:#F0FDF4; border-left:4px solid #22C55E;
                            border-radius:6px; padding:12px 14px; margin-top:8px;">
                    <p style="margin:0 0 6px 0; font-weight:700; color:#15803D;
                               font-size:12px;">📊 ANÁLISIS EJECUTIVO</p>
                    {paragraphs}
                </div>"""

            items_html += f"""
            <div style="border:1px solid #DBEAFE; border-radius:10px;
                        padding:14px 16px; margin-bottom:12px; background:#F8FBFF;">
                <a href="{item['url']}" style="color:#1D4ED8; text-decoration:none;
                   font-weight:700; font-size:15px;">{item['title']}</a>
                <p style="margin:5px 0 0 0; color:#6B7280; font-size:12px
