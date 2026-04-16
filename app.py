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
    "Argentina": [ ],
    "Chile":     [],
    "Perú":      [],
    "Colombia":  [],
}

CC_EMAILS = ["Julieta.rigi@sap.com", "Nicolas.araneda@sap.com", "Agustina.landi@sap.com" , "luis.plazas@sap.com"]

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
        "A continuación encontrarán las noticias más relevantes de la semana "
        "para nuestros mercados en Latinoamérica, con análisis ejecutivo "
        "y oportunidades identificadas para el portafolio SAP."
        "</p>"

        # Separador
        "<hr style='border:none; border-top:2px solid #DBEAFE; margin:20px 0;'>"

        # Secciones por país
        + sections_html +

        # Footer
        "<hr style='border:none; border-top:2px solid #DBEAFE; margin:20px 0;'>"
        "<div style='background:#F8FBFF; border-radius:10px; padding:16px 20px;'>"
        "<p style='margin:0; font-size:13px; color:#6B7280;'>"
        "Este newsletter fue generado con asistencia de IA por <b>" + sender_name + "</b>.<br>"
        "Las noticias provienen de fuentes públicas y deben validarse antes de su uso comercial.<br>"
        "<span style='color:#9CA3AF;'>SAP Operations Team · " + today + "</span>"
        "</p>"
        "</div>"

        "</div>"  # cierre body
        "</div>"  # cierre contenedor principal
    )

    return html


# =========================
# Generar mailto para Outlook
# =========================
def build_mailto_link(
    to_emails: List[str],
    cc_emails: List[str],
    subject: str,
    body_plain: str
) -> str:
    to  = ";".join(to_emails)
    cc  = ";".join(cc_emails)
    subject_enc = urllib.parse.quote(subject)
    body_enc    = urllib.parse.quote(body_plain[:8000])  # límite seguro mailto
    return f"mailto:{to}?cc={cc}&subject={subject_enc}&body={body_enc}"


def build_plain_text_newsletter(
    selected_news: Dict[str, List[Dict]],
    deep_content: Dict[str, str],
    sender_name: str
) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    lines = []
    lines.append("=" * 60)
    lines.append("SAP OPERATIONS TEAM - NEWSLETTER SEMANAL")
    lines.append(f"Edición: {today}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Estimado equipo comercial,")
    lines.append("")
    lines.append(
        "A continuación las noticias más relevantes de la semana "
        "para nuestros mercados en Latinoamérica."
    )
    lines.append("")

    flags = {
        "Argentina": "🇦🇷",
        "Chile": "🇨🇱",
        "Perú": "🇵🇪",
        "Colombia": "🇨🇴"
    }

    for country in COUNTRIES:
        news_list = selected_news.get(country, [])
        if not news_list:
            continue

        flag = flags.get(country, "🌎")
        lines.append("-" * 60)
        lines.append(f"{flag} {country.upper()}")
        lines.append("-" * 60)

        for i, item in enumerate(news_list, 1):
            lines.append(f"\n{i}. {item['title']}")
            lines.append(f"   Fuente: {item['source']} | {item.get('date', '')}")
            lines.append(f"   Link: {item['url']}")

            key = country + "_" + item['title'][:50]
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
# SESSION STATE
# =========================
if "headlines"     not in st.session_state:
    st.session_state.headlines     = {}
if "selected_news" not in st.session_state:
    st.session_state.selected_news = {}
if "deep_content"  not in st.session_state:
    st.session_state.deep_content  = {}
if "newsletter_html" not in st.session_state:
    st.session_state.newsletter_html = ""
if "newsletter_plain" not in st.session_state:
    st.session_state.newsletter_plain = ""
if "phase" not in st.session_state:
    st.session_state.phase = 1  # 1=config, 2=selección, 3=preview


# =========================
# SIDEBAR - Configuración
# =========================
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("---")

    sender_name = st.text_input(
        "Tu nombre",
        value="Equipo de Operaciones SAP",
        help="Aparecerá en la firma del newsletter"
    )

    st.markdown("**Países a incluir:**")
    selected_countries = []
    for c in COUNTRIES:
        if st.checkbox(c, value=True, key=f"country_{c}"):
            selected_countries.append(c)

    st.markdown("**Industrias de interés:**")
    selected_industries = []
    for ind in INDUSTRIES:
        if st.checkbox(ind, value=True, key=f"ind_{ind}"):
            selected_industries.append(ind)

    st.markdown("---")
    st.markdown("**Destinatarios (AEs):**")
    to_emails = []
    for c in selected_countries:
        emails = AE_EMAILS.get(c, [])
        for email in emails:
            if st.checkbox(email, value=True, key=f"email_{email}"):
                to_emails.append(email)

    st.markdown("**Con copia (CC):**")
    cc_emails = []
    for email in CC_EMAILS:
        if st.checkbox(email, value=True, key=f"cc_{email}"):
            cc_emails.append(email)

    st.markdown("---")
    st.caption("💡 Configura tu API Key en Streamlit Secrets como `ANTHROPIC_API_KEY`")


# =========================
# FASE 1 · Buscar titulares
# =========================
st.markdown(
    "<div class='step-header'>📡 Paso 1 · Buscar noticias recientes</div>",
    unsafe_allow_html=True
)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(
        "Haz clic en **Buscar Noticias** para obtener los titulares más recientes "
        "(últimos 30 días) de los países e industrias seleccionados."
    )
with col2:
    buscar = st.button(
        "🔍 Buscar Noticias",
        type="primary",
        use_container_width=True,
        disabled=not selected_countries or not selected_industries
    )

if buscar:
    if not selected_countries:
        st.warning("Selecciona al menos un país.")
    elif not selected_industries:
        st.warning("Selecciona al menos una industria.")
    else:
        with st.spinner("🤖 Claude está buscando las noticias más relevantes..."):
            st.session_state.headlines     = fetch_headlines(
                selected_countries, selected_industries
            )
            st.session_state.selected_news = {}
            st.session_state.deep_content  = {}
            st.session_state.newsletter_html  = ""
            st.session_state.newsletter_plain = ""
            st.session_state.phase = 2
        st.success("✅ Noticias encontradas. Selecciona las que quieres incluir.")
        st.rerun()


# =========================
# FASE 2 · Selección de noticias
# =========================
if st.session_state.headlines:
    st.markdown(
        "<div class='step-header'>✅ Paso 2 · Selecciona las noticias para el newsletter</div>",
        unsafe_allow_html=True
    )

    flags = {
        "Argentina": "🇦🇷",
        "Chile": "🇨🇱",
        "Perú": "🇵🇪",
        "Colombia": "🇨🇴"
    }

    total_selected = 0

    for country in COUNTRIES:
        news_list = st.session_state.headlines.get(country, [])
        if not news_list:
            continue

        flag = flags.get(country, "🌎")
        st.markdown(f"#### {flag} {country}")

        for idx, item in enumerate(news_list):
            key_cb = f"sel_{country}_{idx}"

            col_check, col_info = st.columns([0.5, 9.5])

            with col_check:
                selected = st.checkbox(
                    "",
                    key=key_cb,
                    label_visibility="collapsed"
                )

            with col_info:
                st.markdown(
                    "<div class='news-card'>"
                    "<div style='font-weight:600; color:#1E3A5F; font-size:15px;'>"
                    + item['title'] +
                    "</div>"
                    "<div style='color:#6B7280; font-size:12px; margin-top:4px;'>"
                    "📰 " + item['source'] +
                    " &nbsp;|&nbsp; 🏭 " + item['industry'] +
                    " &nbsp;|&nbsp; 📅 " + item.get('date', 'Reciente') +
                    " &nbsp;|&nbsp; <a href='" + item['url'] +
                    "' target='_blank' style='color:#3B82F6;'>Ver fuente ↗</a>"
                    "</div>"
                    "</div>",
                    unsafe_allow_html=True
                )

            if selected:
                total_selected += 1
                if country not in st.session_state.selected_news:
                    st.session_state.selected_news[country] = []
                # Evitar duplicados
                titles_in = [
                    n['title']
                    for n in st.session_state.selected_news[country]
                ]
                if item['title'] not in titles_in:
                    item_with_country = dict(item)
                    item_with_country['country'] = country
                    st.session_state.selected_news[country].append(item_with_country)
            else:
                # Remover si fue deseleccionado
                if country in st.session_state.selected_news:
                    st.session_state.selected_news[country] = [
                        n for n in st.session_state.selected_news[country]
                        if n['title'] != item['title']
                    ]

        st.markdown("---")

    # Contador y botón generar
    if total_selected > 0:
        st.info(f"📌 **{total_selected} noticia(s) seleccionada(s)**. "
                f"Haz clic en 'Generar Newsletter' para que la IA profundice cada una.")

        st.markdown(
            "<div class='step-header'>🤖 Paso 3 · Generar Newsletter con IA</div>",
            unsafe_allow_html=True
        )

        col_gen1, col_gen2 = st.columns([2, 1])
        with col_gen1:
            st.markdown(
                "La IA analizará en profundidad cada noticia seleccionada y armará "
                "el newsletter completo listo para enviar por Outlook."
            )
        with col_gen2:
            generar = st.button(
                "🚀 Generar Newsletter",
                type="primary",
                use_container_width=True
            )

        if generar:
            progress = st.progress(0, text="Iniciando análisis...")
            all_items = []
            for country, items in st.session_state.selected_news.items():
                for item in items:
                    all_items.append((country, item))

            total = len(all_items)

            for i, (country, item) in enumerate(all_items):
                pct  = int((i / total) * 100)
                text = f"Analizando: {item['title'][:55]}..."
                progress.progress(pct, text=text)

                key = country + "_" + item['title'][:50]
                if key not in st.session_state.deep_content:
                    deep = deepen_news_item(
                        title    = item['title'],
                        source   = item['source'],
                        industry = item['industry'],
                        country  = country
                    )
                    st.session_state.deep_content[key] = deep

            progress.progress(100, text="✅ Análisis completado. Generando newsletter...")

            st.session_state.newsletter_html = build_full_newsletter_html(
                st.session_state.selected_news,
                st.session_state.deep_content,
                sender_name
            )
            st.session_state.newsletter_plain = build_plain_text_newsletter(
                st.session_state.selected_news,
                st.session_state.deep_content,
                sender_name
            )
            st.session_state.phase = 3
            st.rerun()
    else:
        st.warning("☝️ Selecciona al menos una noticia para continuar.")


# =========================
# FASE 3 · Preview y envío
# =========================
if st.session_state.newsletter_html:
    st.markdown(
        "<div class='step-header'>📧 Paso 4 · Preview y envío por Outlook</div>",
        unsafe_allow_html=True
    )

    tab_preview, tab_html, tab_plain = st.tabs(
        ["👁️ Vista previa", "🔤 HTML", "📄 Texto plano"]
    )

    with tab_preview:
        st.markdown(
            "<div class='email-preview'>" +
            st.session_state.newsletter_html +
            "</div>",
            unsafe_allow_html=True
        )

    with tab_html:
        st.code(st.session_state.newsletter_html, language="html")
        st.download_button(
            label="⬇️ Descargar HTML",
            data=st.session_state.newsletter_html,
            file_name=f"newsletter_sap_{datetime.now().strftime('%Y%m%d')}.html",
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
            file_name=f"newsletter_sap_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

    # --- Sección de envío ---
    st.markdown("---")
    st.markdown("### 📤 Enviar por Outlook")

    col_mail1, col_mail2 = st.columns(2)

    with col_mail1:
        st.markdown("**Destinatarios (Para:)**")
        if to_emails:
            for email in to_emails:
                st.markdown(f"- `{email}`")
        else:
            st.warning("No hay destinatarios seleccionados en el sidebar.")

    with col_mail2:
        st.markdown("**Con copia (CC:)**")
        if cc_emails:
            for email in cc_emails:
                st.markdown(f"- `{email}`")
        else:
            st.info("Sin destinatarios en copia.")

    # Asunto del correo
    today_str = datetime.now().strftime("%d/%m/%Y")
    total_news_selected = sum(
        len(v) for v in st.session_state.selected_news.values()
    )
    default_subject = (
        f"SAP Newsletter Semanal · {today_str} · "
        f"{total_news_selected} noticias destacadas"
    )

    email_subject = st.text_input(
        "✏️ Asunto del correo",
        value=default_subject,
        help="Puedes editar el asunto antes de abrir Outlook"
    )

    # Advertencia sobre límite mailto
    st.markdown("""
    <div style='background:#EFF6FF; border:1px solid #BFDBFE; color:#1E40AF;
                padding:12px 16px; border-radius:10px; margin:12px 0; font-size:13px;'>
        <b>💡 Opciones de envío:</b><br>
        - <b>Opción A:</b> Abre Outlook con el texto plano (recomendado para compatibilidad).<br>
        - <b>Opción B:</b> Descarga el HTML y pégalo manualmente en Outlook para
          conservar el formato visual completo.
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        # Botón mailto con texto plano
        if to_emails:
            mailto_link = build_mailto_link(
                to_emails  = to_emails,
                cc_emails  = cc_emails,
                subject    = email_subject,
                body_plain = st.session_state.newsletter_plain
            )
            st.markdown(
                f"<a href='{mailto_link}' class='outlook-btn' "
                f"style='display:block; text-align:center; background:#0078D4; "
                f"color:white; padding:12px 20px; border-radius:10px; "
                f"text-decoration:none; font-weight:700; font-size:14px; "
                f"box-shadow:0 4px 14px rgba(0,120,212,.35);'>"
                f"📧 Abrir en Outlook</a>",
                unsafe_allow_html=True
            )
        else:
            st.button("📧 Abrir en Outlook", disabled=True)
            st.caption("Selecciona destinatarios en el sidebar.")

    with col_btn2:
        # Descargar HTML para pegar en Outlook
        st.download_button(
            label="⬇️ Descargar HTML",
            data=st.session_state.newsletter_html,
            file_name=f"newsletter_sap_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True,
            help="Descarga el HTML y ábrelo en tu navegador para copiarlo en Outlook"
        )

    with col_btn3:
        # Botón para reiniciar todo el proceso
        if st.button(
            "🔄 Nuevo Newsletter",
            use_container_width=True,
            help="Limpia todo y comienza desde cero"
        ):
            # Limpiar session state
            for key in [
                "headlines", "selected_news", "deep_content",
                "newsletter_html", "newsletter_plain"
            ]:
                st.session_state[key] = {} if key != "newsletter_html" \
                    and key != "newsletter_plain" else ""
            st.session_state.phase = 1
            st.rerun()

    # --- Instrucciones para pegar HTML en Outlook ---
    with st.expander("📋 ¿Cómo pegar el HTML con formato en Outlook?"):
        st.markdown("""
        **Pasos para enviar con formato visual completo:**

        1. Haz clic en **⬇️ Descargar HTML** para guardar el archivo.
        2. Abre el archivo `.html` descargado en tu navegador
           (Chrome, Edge o Firefox).
        3. Selecciona todo el contenido con `Ctrl + A`.
        4. Cópialo con `Ctrl + C`.
        5. Abre un **nuevo correo en Outlook**.
        6. Pega el contenido con `Ctrl + V` en el cuerpo del mensaje.
        7. Completa los destinatarios y el asunto.
        8. ¡Envía! 🚀

        > **Tip:** Asegúrate de que Outlook esté en modo **HTML**
        > (no texto plano) para que el formato se conserve correctamente.
        """)

    # --- Resumen final del newsletter ---
    st.markdown("---")
    st.markdown("### 📊 Resumen del Newsletter generado")

    flags = {
        "Argentina": "🇦🇷",
        "Chile": "🇨🇱",
        "Perú": "🇵🇪",
        "Colombia": "🇨🇴"
    }

    summary_cols = st.columns(len(COUNTRIES))

    for i, country in enumerate(COUNTRIES):
        news_list = st.session_state.selected_news.get(country, [])
        with summary_cols[i]:
            st.metric(
                label=f"{flags.get(country, '🌎')} {country}",
                value=f"{len(news_list)} noticias",
                delta="incluidas" if news_list else "sin noticias"
            )

    # Detalle por país
    for country in COUNTRIES:
        news_list = st.session_state.selected_news.get(country, [])
        if not news_list:
            continue

        flag = flags.get(country, "🌎")
        with st.expander(f"{flag} {country} · {len(news_list)} noticia(s) incluida(s)"):
            for item in news_list:
                key = country + "_" + item['title'][:50]
                deep = st.session_state.deep_content.get(key, "")

                st.markdown(
                    "<div style='border:1px solid #DBEAFE; border-radius:10px;"
                    "padding:14px 16px; margin-bottom:10px; background:#F8FBFF;'>"
                    "<b style='color:#1E3A5F;'>" + item['title'] + "</b><br>"
                    "<span style='color:#6B7280; font-size:12px;'>"
                    "📰 " + item['source'] +
                    " | 📅 " + item.get('date', 'Reciente') +
                    " | <a href='" + item['url'] +
                    "' target='_blank' style='color:#3B82F6;'>Ver fuente ↗</a>"
                    "</span>"
                    "</div>",
                    unsafe_allow_html=True
                )

                if deep:
                    with st.expander("Ver análisis ejecutivo"):
                        st.markdown(deep)

# =========================
# Footer de la app
# =========================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#9CA3AF; font-size:12px; padding:10px 0;'>"
    "SAP Operations Team · Newsletter Intelligence · "
    "Powered by Claude AI (Anthropic) · "
    + datetime.now().strftime("%Y") +
    "</div>",
    unsafe_allow_html=True)
