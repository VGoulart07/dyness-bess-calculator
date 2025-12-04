# calculadora_baterias.py
import streamlit as st
import math
import os

# ---------- Configuração da página ----------
st.set_page_config(page_title="Dyness BESS Calculator", layout="wide", page_icon="🟧")

# ---------- Tema ----------
st.markdown(
    """
    <style>
    .stApp { background-color: #F7F7F7; color: #111111 !important; }
    html, body, [class*="css"] { color: #111111 !important; }
    label, .stRadio, .stSelectbox, .stNumberInput label, .stTextInput label {
        color: #111111 !important; font-weight: 500 !important;
    }
    div[role="radiogroup"] * { color: #111111 !important; }
    .dyness-header {
        background: #FFFFFF; padding: 12px 18px; border-radius: 10px;
        display: flex; align-items: center; gap: 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 12px;
    }
    .dyness-title { font-size: 22px; font-weight: 700; color: #111111 !important; }
    .dyness-subtitle { color: #333333 !important; font-size: 13px; }
    .result-card {
        background: #FFFFFF; padding: 12px; border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .stButton>button {
        background-color: #FF6600 !important; color: white !important;
        border-radius: 6px; padding: 8px 12px; border: none;
    }
    h1, h2, h3, h4, h5 { color: #111111 !important; }
    .stAlert p { color: #111111 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Logo ----------
logo_filename = "Dyness logo.jpg"
logo_path = os.path.join("Logo", logo_filename)

with st.container():
    st.write("")
    cols = st.columns([0.25, 1])
    with cols[0]:
        if os.path.exists(logo_path):
            st.image(logo_path, width=140)
    with cols[1]:
        st.markdown(
            """
            <div class="dyness-header">
                <div>
                    <div class="dyness-title">Dimensionamento Preliminar – Dyness BESS</div>
                    <div class="dyness-subtitle">Ferramenta de apoio para engenharia, pré-vendas e propostas</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------- Entradas ----------
st.header("📥 Entradas do Cliente")

col1, col2, col3 = st.columns(3)

with col1:
    carga_kw = st.number_input("Potência das Cargas (kW)", min_value=0.0, step=0.1, value=3.0)
    autonomia_h = st.number_input("Autonomia Desejada (h)", min_value=0.0, step=0.5, value=4.0)
    motores_trifasicos_sel = st.radio(
        "Possui motores trifásicos?",
        options=["Não", "Sim"],
        index=0
    )
    motores_trifasicos = motores_trifasicos_sel == "Sim"

with col2:
    pot_inversor_kw = st.number_input("Potência do Inversor (kW)", min_value=0.0, step=0.1, value=5.0)
    corrente_carga_inv = st.number_input("Corrente de Carga do Inversor (A)", min_value=0.0, step=1.0, value=0.0)
    corrente_descarga_inv = st.number_input("Corrente de Descarga do Inversor (A)", min_value=0.0, step=1.0, value=0.0)

with col3:
    st.subheader("Faixa DC do Inversor")
    tensao_min_inv = st.number_input("Tensão Mínima (V)", min_value=0.0, step=1.0, value=200.0)
    tensao_max_inv = st.number_input("Tensão Máxima (V)", min_value=0.0, step=1.0, value=560.0)

# ---------- Base de dados ----------
baterias = {
    "DL5.0C": {
        "tipo": "LV",
        "capacidade_nominal": 5.12,
        "dod": 0.90,
        "tensao_modulo": 51.2,
        "corrente_carga": 75.0,
        "corrente_descarga": 100.0,
        "max_paralelo": 50,
        "tensao_min": 44.8,
        "tensao_max": 57.6
    },
    "Powerbox G2": {
        "tipo": "LV",
        "capacidade_nominal": 10.24,
        "dod": 0.95,
        "tensao_modulo": 51.2,
        "corrente_carga": 100.0,
        "corrente_descarga": 200.0,
        "max_paralelo": 50,
        "tensao_min": 44.8,
        "tensao_max": 57.6
    },
    "Stack100": {
        "tipo": "HV",
        "capacidade_nominal": 5.12,
        "dod": 0.95,
        "tensao_modulo": 51.2,
        "corrente_carga": 100.0,
        "corrente_descarga": 100.0,
        "tensao_min_string": 134.0,
        "tensao_max_string": 864.0,
        "max_modulos_por_torre": 12,
        "max_modulos_por_bdu": 15,
        "max_strings": 12
    }
}

# ---------- Seleção ----------
st.header("🔋 Seleção do Modelo Dyness")
modelo = st.selectbox("Modelo", list(baterias.keys()))
bat = baterias[modelo]

# ---------- Cálculo energético ----------
energia_necessaria = carga_kw * autonomia_h
if motores_trifasicos:
    energia_necessaria *= 1.2

st.markdown(
    f"<div class='result-card'>🔹 <b>Energia total necessária:</b> {energia_necessaria:.2f} kWh</div>",
    unsafe_allow_html=True,
)

cap_util_modulo = bat["capacidade_nominal"] * bat["dod"]
modulos_totais = math.ceil(energia_necessaria / cap_util_modulo) if energia_necessaria > 0 else 0

st.markdown(
    f"""
    <div class="result-card">
    🔹 <b>Capacidade útil por módulo:</b> {cap_util_modulo:.2f} kWh<br>
    🔹 <b>Módulos necessários:</b> {modulos_totais} módulos
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Configuração ----------
if modelo == "Stack100":
    mod_torre = bat["max_modulos_por_torre"]
    torres = math.ceil(modulos_totais / mod_torre)
    bdus = math.ceil(modulos_totais / bat["max_modulos_por_bdu"])

    st.subheader("📦 Configuração HV — Stack100")
    st.write(f"• Módulos por torre (máx): **{mod_torre}**")
    st.write(f"• Torres necessárias: **{torres}**")
    st.write(f"• BDUs necessárias: **{bdus}**")

    if torres > bat["max_strings"]:
        st.error("❌ Excede o limite de 12 strings.")
    else:
        st.success("✔ Strings dentro do limite.")

    tensao_total_min = bat["tensao_min_string"]
    tensao_total_max = bat["tensao_max_string"]

    st.write(f"🔹 Faixa de tensão nomeada: **{tensao_total_min} – {tensao_total_max} V**")

else:
    st.subheader("📦 Configuração LV — Paralelo")

    if modulos_totais > bat["max_paralelo"]:
        st.error(f"❌ Excede limite de {bat['max_paralelo']} módulos.")
    else:
        st.success("✔ Dentro do limite.")

    tensao_total_min = bat["tensao_min"]
    tensao_total_max = bat["tensao_max"]

    st.write(f"🔹 Faixa de tensão do módulo: **{tensao_total_min} – {tensao_total_max} V**")

# ---------- Correntes ----------
st.header("⚡ Validação de Corrente")

corr_carga_mod = bat["corrente_carga"]
corr_desc_mod = bat["corrente_descarga"]

if modelo == "Stack100":
    paralelos = torres
else:
    paralelos = modulos_totais

corr_carga_total = corr_carga_mod * paralelos
corr_desc_total = corr_desc_mod * paralelos

st.write(f"• Corrente total de carga suportada: **{corr_carga_total:.1f} A**")
st.write(f"• Corrente total de descarga suportada: **{corr_desc_total:.1f} A**")

if corrente_carga_inv > 0:
    if corrente_carga_inv > corr_carga_total:
        st.error("❌ Corrente de carga do inversor EXCEDE o limite do banco.")
    else:
        st.success("✔ Corrente de carga dentro do limite.")
else:
    st.info("ℹ️ Corrente de carga do inversor não informada (0).")

if corrente_descarga_inv > 0:
    if corrente_descarga_inv > corr_desc_total:
        st.error("❌ Corrente de descarga do inversor EXCEDE o limite do banco.")
    else:
        st.success("✔ Corrente de descarga dentro do limite.")
else:
    st.info("ℹ️ Corrente de descarga do inversor não informada (0).")

# ---------- Potência ----------
st.header("🔌 Validação de Potência Máxima (teórica)")

# ============================================================
# 🔧 AJUSTE DA POTÊNCIA – CORRETO PARA HV
# ============================================================

if modelo == "Stack100":
    tensao_nominal = (bat["tensao_min_string"] + bat["tensao_max_string"]) / 2
else:
    tensao_nominal = bat.get("tensao_modulo", 51.2)

pot_max = (tensao_nominal * corr_desc_total) / 1000

# ============================================================

st.write(f"• Potência máxima teórica do banco: **{pot_max:.2f} kW**")

if pot_inversor_kw > pot_max:
    st.error("❌ O inversor exige mais potência do que o banco fornece.")
else:
    st.success("✔ Potência compatível.")

# ---------- Observação Final ----------
st.markdown(
    """
    <div style="
        background-color:#FFFFFF;
        border-left: 4px solid #FF6600;
        padding: 10px 14px;
        border-radius: 6px;
        color:#111111;
        font-size: 14px;
    ">
        🟧 <b>Observação:</b> pré-dimensionamento. Projeto executivo deve ser validado com fabricante.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Sidebar ----------
st.sidebar.header("ℹ️ Sobre a Calculadora")
st.sidebar.markdown(
    """
    **Dyness BESS Calculator – Versão 1.0**

    Desenvolvido para:
    - Engenharia  
    - Pré-vendas  
    - Propostas  

    Valida:
    - Dimensionamento
    - Corrente
    - Tensão
    - Potência

    **Responsável Técnico:** Vinícius Goulart  
    **Empresa:** Dyness Brasil  
    """
)

st.sidebar.header("📄 Datasheets Dyness")
PASTA_DATASHEETS = "datasheets"

datasheets = {
    "DL5.0C": "DL5.0C Datasheet-PT-BR(LATAM)-20250708.pdf",
    "Powerbox G2": "Dyness Powerbox G2 datasheet-20250528-BR.pdf",
    "SBDU100": "SBDU100 Datasheet-PT-20251010.pdf",
    "Stack100": "STACK100 Datasheet-20250617-PT-BR.pdf",
}

for nome, arquivo in datasheets.items():
    caminho = os.path.join(PASTA_DATASHEETS, arquivo)
    st.sidebar.write(f"**{nome}**")
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            st.sidebar.download_button(
                label=f"⬇️ Baixar {nome}",
                data=f,
                file_name=arquivo,
                mime="application/pdf"
            )
    else:
        st.sidebar.error(f"Arquivo não encontrado: {arquivo}")
