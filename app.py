import streamlit as st
import urllib.parse
from datetime import datetime
from typing import Dict, List

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
    "Chile": ["ae.chile1@sap.com", "ae.chile2@sap.com"],
    "Perú": ["ae.peru1@sap.com", "ae.peru2@sap.com"],
    "Colombia": ["ae.colombia1@sap.com", "ae.colombia2@sap.com"],
}

CC_EMAILS = [
    "operaciones@sap.com",
    "lider.comercial@sap.com"
]

# Titulares simulados por país (MVP sin API externa)
MOCK_HEADLINES: Dict[str, List[Dict[str, str]]] = {
    "Argentina": [
        {"title": "Argentina impulsa inversión en litio para exportación", "source": "Reuters", "url": "https://www.reuters.com/"},
        {"title": "Sector retail acelera transformación digital en 2026", "source": "La Nación", "url": "https://www.lanacion.com.ar/"},
        {"title": "Nuevas oportunidades en energía renovable corporativa", "source": "Bloomberg Línea", "url": "https://www.bloomberglinea.com/"},
    ],
    "Chile": [
        {"title": "Minería chilena adopta IA para eficiencia operativa", "source": "Diario Financiero", "url": "https://www.df.cl/"},
        {"title": "Crecen proyectos de hidrógeno verde para industria", "source": "Reuters", "url": "https://www.reuters.com/"},
        {"title": "Banca chilena fortalece estrategia de ciberseguridad", "source": "El Mercurio", "url": "https://www.emol.com/"},
    ],
    "Perú": [
        {"title": "Perú prioriza modernización logística en puertos", "source": "Gestión", "url": "https://gestion.pe/"},
        {"title": "Manufactura peruana aumenta adopción de nube", "source": "Reuters", "url": "https://www.reuters.com/"},
        {"title": "Agroindustria invierte en analítica avanzada", "source": "El Comercio", "url": "https://elcomercio.pe/"},
    ],
    "Colombia": [
        {"title": "Colombia expande fintech empresarial en B2B", "source": "Portafolio", "url": "https://www.portafolio.co/"},
        {"title": "Telecom mejora infraestructura para servicios críticos", "source": "Reuters", "url": "https://www.reuters.com/"},
        {"title": "Empresas aceleran estrategia de datos e IA", "source": "La República", "url": "https://www.larepublica.co/"},
    ],
}


# =========================
# Estilos SAP-like
# =========================
st.markdown(
    """
    <style>
        .sap-hero {
            background: linear-gradient(120deg, #003A8C 0%, #0057D9 65%, #0070F2 100%);
            border-radius: 18px;
            padding: 26px 28px;
            color: white;
            margin-bottom: 18px;
            box-shadow: 0 8px 30px rgba(0,0,0,.15);
        }
        .sap-badge {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 10px;
            background: rgba(255,255,255,.15);
            margin-right: 8px;
            font-size: 12px;
            font-weight: 600;
        }
        .sap-alert {
            background: #FFF7ED;
            border: 1px solid #FDBA74;
            color: #9A3412;
            padding: 12px 14px;
            border-radius: 10px;
            margin-bottom: 16px;
            font-size: 14px;
        }
        .box {
            border: 1px solid #dbe4ff;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 10px;
            background: #f8fbff;
        }
        .small {
            color: #4b5563;
            font-size: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Header / Hero
# =========================
st.markdown(
    """
    <div class="sap-hero">
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:8px;">
            <div style="background:#fff; color:#0057D9; border-radius:8px; font-weight:700; padding:8px 10px;">SAP</div>
            <div style="font-weight:700; opacity:.9;">Operations Team</div>
        </div>
        <h1 style="margin:0; font-size:44px; line-height:1.05;">Newsletter</h1>
        <p style="margin:10px 0 14px 0; font-size:18px; opacity:.95;">Plataforma de noticias por país para equipo comercial (AE)</p>
        <span class="sap-badge">Argentina</span>
        <span class="sap-badge">Chile</span>
        <span class="sap-badge">Perú</span>
        <span class="sap-badge">Colombia</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="sap-alert">
        <b>⚠ Aviso importante:</b> Uno debe elegir la noticia que quiere enviar y debe validarse con fuentes oficiales antes de su envío final.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Estado de sesión
# =========================
if "headlines" not in st.session_state:
    st.session_state.headlines = {}
if "selected_news" not in st.session_state:
    st.session_state.selected_news = {country: [] for country in COUNTRIES}
if "generated" not in st.session_state:
    st.session_state.generated = False


def generate_headlines():
    # MVP: usa datos simulados confiables de medios reales predefinidos
    st.session_state.headlines = MOCK_HEADLINES
    st.session_state.generated = True


def build_newsletter_html(selected_news: Dict[str, List[Dict[str, str]]]) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    sections = ""
    for country in COUNTRIES:
        news = selected_news.get(country, [])
        if not news:
            continue
        items = ""
        for n in news:
            items += f"""
            <li style="margin-bottom:10px;">
                <a href="{n['url']}" style="color:#0a6ed1; text-decoration:none;"><b>{n['title']}</b></a><br/>
                <span style="color:#6b7280; font-size:12px;">Fuente: {n['source']}</span>
            </li>
            """
        sections += f"""
        <h3 style="color:#003A8C; margin-top:20px;">{country}</h3>
        <ul style="padding-left:20px;">{items}</ul>
        """

    html = f"""
    <html>
      <body style="font-family:Arial,sans-serif; color:#111827;">
        <div style="max-width:760px; margin:0 auto; border:1px solid #e5e7eb; border-radius:12px; overflow:hidden;">
          <div style="background:linear-gradient(120deg,#003A8C,#0057D9,#0070F2); color:#fff; padding:20px;">
            <h2 style="margin:0;">Newsletter Semanal</h2>
            <p style="margin:8px 0 0 0; opacity:.95;">Fecha: {today}</p>
          </div>
          <div style="padding:20px;">
            <p>Hola equipo,</p>
            <p>Compartimos las noticias destacadas por país:</p>
            {sections if sections else "<p>No se seleccionaron noticias.</p>"}
            <p style="margin-top:24px;">Saludos,<br/>Equipo de Operaciones</p>
          </div>
        </div>
      </body>
    </html>
    """
    return html


def open_outlook_link(subject: str, to_list: List[str], cc_list: List[str], body_html: str):
    # mailto no soporta HTML real en todos los clientes, pero Outlook suele mantener formato básico.
    # Para escenarios enterprise se recomienda integración COM (pywin32) en siguiente fase.
    mailto = (
        f"mailto:{','.join(to_list)}"
        f"?cc={urllib.parse.quote(','.join(cc_list))}"
        f"&subject={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body_html)}"
    )
    st.markdown(
        f'<a href="{mailto}" target="_self">📧 Abrir Outlook con correo generado</a>',
        unsafe_allow_html=True
    )


# =========================
# Flujo principal
# =========================
st.subheader("1) Generar titulares")
if st.button("Generar noticias", type="primary", use_container_width=True):
    with st.spinner("Buscando titulares relevantes por país..."):
        generate_headlines()
    st.success("Titulares obtenidos. Selecciona cuáles deseas profundizar y enviar.")

if st.session_state.generated:
    st.subheader("2) Selecciona noticias a incluir")

    for country in COUNTRIES:
        with st.expander(f"{country} — titulares encontrados", expanded=False):
            country_news = st.session_state.headlines.get(country, [])
            chosen = []
            for i, item in enumerate(country_news):
                key = f"{country}_{i}"
                checked = st.checkbox(
                    f"{item['title']}  \nFuente: {item['source']}",
                    key=key
                )
                if checked:
                    chosen.append(item)
            st.session_state.selected_news[country] = chosen

    st.subheader("3) Generar correo para Outlook")
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_countries = st.multiselect(
            "Países a incluir en destinatarios AE",
            COUNTRIES,
            default=COUNTRIES
        )
    with col2:
        custom_subject = st.text_input(
            "Asunto del correo",
            value="Newsletter Semanal"
        )

    if st.button("Armar correo y abrir Outlook", use_container_width=True):
        to_recipients = []
        for c in selected_countries:
            to_recipients.extend(AE_EMAILS.get(c, []))

        # quitar duplicados preservando orden
        seen = set()
        to_recipients = [x for x in to_recipients if not (x in seen or seen.add(x))]

        html_body = build_newsletter_html(st.session_state.selected_news)

        if not to_recipients:
            st.error("No hay destinatarios AE configurados para los países seleccionados.")
        else:
            st.success("Correo generado. Haz click en el enlace para abrir Outlook.")
            open_outlook_link(
                subject=custom_subject,
                to_list=to_recipients,
                cc_list=CC_EMAILS,
                body_html=html_body
            )

    st.markdown("---")
    st.caption("Nota: este MVP prepara y abre el correo para revisión manual antes de enviar.")
