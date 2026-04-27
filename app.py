import streamlit as st
import pandas as pd
import io
import uuid
import hashlib
from datetime import datetime
import math
import json
import re
from typing import Tuple
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Importador Pro v5 | Enterprise",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# --- CSS LIMPO E REFINADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* =============================================
   VARIÁVEIS GLOBAIS
   ============================================= */
:root {
    --bg-primary:    #f8f9fb;
    --bg-card:       #ffffff;
    --bg-sidebar:    #0f172a;
    --text-primary:  #0f172a;
    --text-secondary:#64748b;
    --text-muted:    #94a3b8;
    --border:        #e2e8f0;
    --accent:        #2563eb;
    --accent-hover:  #1d4ed8;
    --accent-light:  #eff6ff;
    --success:       #059669;
    --warning:       #d97706;
    --danger:        #dc2626;
    --radius-sm:     6px;
    --radius-md:     10px;
    --radius-lg:     14px;
    --shadow-sm:     0 1px 3px rgba(0,0,0,0.07);
    --shadow-md:     0 4px 12px rgba(0,0,0,0.08);
    --shadow-lg:     0 8px 24px rgba(0,0,0,0.10);
    --font:          'DM Sans', sans-serif;
    --font-mono:     'DM Mono', monospace;
}

/* =============================================
   BASE - SEM FORÇAR CORES EM TUDO
   ============================================= */
html, body, .stApp {
    font-family: var(--font) !important;
    background-color: var(--bg-primary) !important;
}

.main .block-container {
    background-color: var(--bg-primary) !important;
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1440px !important;
}

/* Texto base — apenas onde necessário */
p, span, label, div {
    font-family: var(--font) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font) !important;
    color: var(--text-primary) !important;
}

/* =============================================
   SIDEBAR
   ============================================= */
section[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
}

section[data-testid="stSidebar"] > div {
    background-color: var(--bg-sidebar) !important;
}

/* Textos na sidebar — branco */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #cbd5e1 !important;
}

section[data-testid="stSidebar"] .sidebar-brand h2 {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

section[data-testid="stSidebar"] .sidebar-brand p {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
}

/* Métricas na sidebar */
section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 0.7rem !important;
}

/* Divider na sidebar */
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}

/* Caption na sidebar */
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #94a3b8 !important;
}

/* File uploader na sidebar */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: rgba(255,255,255,0.05) !important;
    border: 1.5px dashed rgba(255,255,255,0.18) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.6rem !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
}

/* Esconde o ícone grande de upload na sidebar para economizar espaço */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    display: none !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div > small {
    font-size: 0.72rem !important;
    color: #64748b !important;
}

/* Nome do arquivo carregado na sidebar */
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {
    background-color: rgba(255,255,255,0.06) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.3rem 0.5rem !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] * {
    color: #94a3b8 !important;
    font-size: 0.75rem !important;
}

/* Botões na sidebar */
section[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255,255,255,0.07) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.25) !important;
}

/* Expander na sidebar */
section[data-testid="stSidebar"] details {
    background-color: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important;
    overflow: visible !important;
}

section[data-testid="stSidebar"] details summary {
    color: #cbd5e1 !important;
    font-size: 0.82rem !important;
    padding: 0.6rem 0.75rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

section[data-testid="stSidebar"] details[open] {
    overflow: visible !important;
}

section[data-testid="stSidebar"] details > div {
    padding: 0.5rem 0.75rem 0.75rem !important;
}

section[data-testid="stSidebar"] details p,
section[data-testid="stSidebar"] details li,
section[data-testid="stSidebar"] details strong {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    line-height: 1.55 !important;
}

/* Subheader na sidebar */
section[data-testid="stSidebar"] h3 {
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #64748b !important;
    margin-bottom: 0.5rem !important;
}

/* =============================================
   INPUTS — ÁREA PRINCIPAL (não sidebar)
   ============================================= */
.main .stTextInput input,
.main [data-baseweb="input"] input {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font) !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

.main .stTextInput input:focus,
.main [data-baseweb="input"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    outline: none !important;
}

/* Selectbox */
.main .stSelectbox [data-baseweb="select"] > div:first-child {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}

/* Dropdown popover */
[data-baseweb="popover"] [data-baseweb="menu"],
[role="listbox"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-lg) !important;
}

[role="option"] {
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
}

[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background-color: var(--accent-light) !important;
    color: var(--accent) !important;
}

/* Multiselect tags */
[data-baseweb="tag"] {
    background-color: var(--accent-light) !important;
    border-color: var(--accent) !important;
}

[data-baseweb="tag"] span {
    color: var(--accent) !important;
}

/* =============================================
   BOTÕES — ÁREA PRINCIPAL
   ============================================= */
.main .stButton > button {
    font-family: var(--font) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.18s ease !important;
    padding: 0.5rem 1.1rem !important;
    letter-spacing: 0.01em !important;
}

.main .stButton > button[kind="primary"] {
    background-color: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(37,99,235,0.25) !important;
}

.main .stButton > button[kind="primary"]:hover {
    background-color: var(--accent-hover) !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.35) !important;
    transform: translateY(-1px) !important;
}

.main .stButton > button[kind="secondary"] {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border) !important;
}

.main .stButton > button[kind="secondary"]:hover {
    background-color: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
}

/* =============================================
   TABS
   ============================================= */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--bg-card) !important;
    border-bottom: 2px solid var(--border) !important;
    border-radius: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--text-secondary) !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    padding: 0.85rem 1.3rem !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    margin-bottom: -2px !important;
    transition: all 0.15s !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--accent) !important;
    background-color: var(--accent-light) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 600 !important;
    background-color: transparent !important;
}

/* =============================================
   DATAFRAME & DATA EDITOR
   ============================================= */
[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}

/* =============================================
   MÉTRICAS — ÁREA PRINCIPAL
   ============================================= */
.main [data-testid="stMetricValue"] {
    font-family: var(--font) !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

.main [data-testid="stMetricLabel"] {
    font-family: var(--font) !important;
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-weight: 600 !important;
}

/* =============================================
   ALERTAS
   ============================================= */
.stAlert {
    border-radius: var(--radius-md) !important;
    border-left-width: 4px !important;
}

/* =============================================
   PROGRESS BAR
   ============================================= */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent), #7c3aed) !important;
    border-radius: 99px !important;
}

.stProgress > div > div {
    background-color: var(--border) !important;
    border-radius: 99px !important;
}

/* =============================================
   SCROLLBAR
   ============================================= */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* =============================================
   DIVIDER
   ============================================= */
.main hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* =============================================
   CAPTION
   ============================================= */
.main .stCaption,
.main [data-testid="stCaptionContainer"] {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
}

/* =============================================
   TOAST
   ============================================= */
[data-testid="stToast"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-lg) !important;
}

/* =============================================
   DOWNLOAD BUTTON
   ============================================= */
.main [data-testid="stDownloadButton"] button {
    font-family: var(--font) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.18s !important;
}

/* =============================================
   SUBHEADER / HEADER
   ============================================= */
.main h2, .main h3 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}

/* =============================================
   CARDS CUSTOMIZADOS
   ============================================= */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s, transform 0.2s;
    text-align: center;
}

.kpi-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.kpi-value {
    font-size: 2.1rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 0.35rem;
}

.kpi-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
}

.kpi-accent  { color: var(--accent); }
.kpi-success { color: var(--success); }
.kpi-warning { color: var(--warning); }
.kpi-danger  { color: var(--danger); }
.kpi-purple  { color: #7c3aed; }

/* App header */
.app-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    padding: 1.75rem 2rem;
    border-radius: var(--radius-lg);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.06);
}

.app-header h1 {
    color: #ffffff !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
    letter-spacing: -0.02em !important;
}

.app-header p {
    color: #64748b !important;
    font-size: 0.82rem !important;
    margin: 0.35rem 0 0 !important;
    font-family: var(--font-mono) !important;
}

/* Oculta o botão "add row" do data_editor que vaza para fora da aba */
section[data-testid="stSidebar"] [data-testid="stDataEditorAddRowButton"],
[data-testid="stDataEditorAddRowButton"] {
    display: none !important;
}

/* Sidebar header */
.sidebar-brand {
    padding: 0.25rem 0 1rem;
}

.sidebar-brand h2 {
    color: #ffffff !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    margin: 0 !important;
}

.sidebar-brand p {
    color: #475569 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin: 0.2rem 0 0 !important;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 99px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-green  { background: #d1fae5; color: #065f46; }
.badge-orange { background: #fef3c7; color: #92400e; }
.badge-red    { background: #fee2e2; color: #991b1b; }

/* Info box */
.info-box {
    background: var(--accent-light);
    border: 1px solid #bfdbfe;
    border-radius: var(--radius-md);
    padding: 0.85rem 1rem;
    font-size: 0.85rem;
    color: #1e40af;
    margin: 0.5rem 0;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
COLUNA_SKU = "SKU"
COLUNA_ID_ANUNCIO = "ID do canal de venda"
COLUNAS_EDITAVEIS = ["Marca", "EAN", "SKU", "Kit quantidade", "Código Depósito"]
COLUNAS_OBRIGATORIAS = ["SKU"]
TAMANHO_LOTE = 10

# --- FUNÇÕES UTILITÁRIAS ---

@st.cache_data(ttl=3600)
def normalizar_nome_col(nome: str) -> str:
    nome = re.sub(r'\s*\([A-Z]\)\s*$', '', str(nome))
    return nome.strip().lower()


def resolver_coluna(df: pd.DataFrame, nome_desejado: str, criar_se_nao_existir: bool = False) -> str:
    alvo = normalizar_nome_col(nome_desejado)
    for col in df.columns:
        if normalizar_nome_col(col) == alvo:
            return col
    if criar_se_nao_existir and nome_desejado not in df.columns:
        df[nome_desejado] = ""
        return nome_desejado
    return nome_desejado


def resolver_colunas_editaveis(df: pd.DataFrame) -> list:
    return [resolver_coluna(df, c, criar_se_nao_existir=True) for c in COLUNAS_EDITAVEIS]


def calcular_hash(df: pd.DataFrame) -> str:
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=True).values.tobytes()
    ).hexdigest()


def normalizar_ean(valor) -> str:
    if pd.isna(valor):
        return ""
    try:
        return str(int(float(str(valor).strip())))
    except (ValueError, OverflowError):
        return str(valor).strip()


def contar_vazios(df: pd.DataFrame, coluna: str) -> int:
    if coluna not in df.columns:
        return len(df)
    return (
        df[coluna].isna() |
        df[coluna].astype(str).str.strip().isin(["", "None", "nan"])
    ).sum()


def validar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    erros = []
    cols_obrigatorias_reais = resolver_colunas_obrigatorias(df)
    col_ean_real = resolver_coluna(df, "EAN")

    for idx in range(len(df)):
        row = df.iloc[idx]

        for col in cols_obrigatorias_reais:
            valor = row.get(col)
            if pd.isna(valor) or str(valor).strip() in ("", "None", "nan"):
                erros.append({
                    "Nº Linha": idx + 1,
                    "Campo": "SKU",
                    "Valor Atual": str(valor),
                    "Descrição": "SKU não preenchido — execute o PROCV para preencher",
                    "Severidade": "🚨 Crítico",
                })

        if col_ean_real in df.columns:
            ean_str = normalizar_ean(row.get(col_ean_real))
            if ean_str:
                if not ean_str.isdigit():
                    erros.append({
                        "Nº Linha": idx + 1,
                        "Campo": "EAN",
                        "Valor Atual": str(row.get(col_ean_real)),
                        "Descrição": "EAN inválido — deve conter apenas números",
                        "Severidade": "⚠️ Alerta",
                    })
                elif len(ean_str) not in (8, 12, 13):
                    erros.append({
                        "Nº Linha": idx + 1,
                        "Campo": "EAN",
                        "Valor Atual": ean_str,
                        "Descrição": f"EAN com {len(ean_str)} dígitos — esperado 8, 12 ou 13",
                        "Severidade": "ℹ️ Informativo",
                    })

    return pd.DataFrame(erros) if erros else pd.DataFrame(
        columns=["Nº Linha", "Campo", "Valor Atual", "Descrição", "Severidade"]
    )


def resolver_colunas_obrigatorias(df: pd.DataFrame) -> list:
    return [resolver_coluna(df, c) for c in COLUNAS_OBRIGATORIAS]


def garantir_colunas(df: pd.DataFrame) -> pd.DataFrame:
    for col in COLUNAS_EDITAVEIS:
        if col not in df.columns:
            df[col] = ""
    return df


def ler_arquivo(file) -> pd.DataFrame:
    try:
        if file.name.endswith(".csv"):
            for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
                try:
                    file.seek(0)
                    return pd.read_csv(file, encoding=encoding)
                except (UnicodeDecodeError, UnicodeError):
                    continue
            raise ValueError("Não foi possível determinar o encoding do arquivo CSV")
        else:
            return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        st.error(f"❌ Erro ao ler arquivo: {str(e)}")
        st.stop()


def _chave_composta(df: pd.DataFrame, col_id: str, col_var: str | None) -> pd.Series:
    """Gera coluna de chave: 'id||variacao' se variacao preenchida, senão só 'id'."""
    base = df[col_id].astype(str).str.strip()
    if col_var is None or col_var not in df.columns:
        return base
    var = df[col_var].astype(str).str.strip().replace({"nan": "", "None": "", "0": ""})
    # Onde variação está preenchida: id||var; caso contrário só id
    return base.where(var == "", base + "||" + var)


def executar_merge_procv(
    df_sistema: pd.DataFrame,
    df_cliente: pd.DataFrame,
    col_id_sistema: str,
    col_id_cliente: str,
    col_sku_cliente: str,
    col_sku_sistema: str,
    sobrescrever: bool = False,
    col_var_sistema: str | None = None,
    col_var_cliente: str | None = None,
) -> Tuple[pd.DataFrame, dict]:
    """
    Merge com suporte a chave composta (ID Anúncio + ID Variação).

    Prioridade:
      1. Se a linha do sistema tiver ID Variação preenchido → busca por ID+Variação
      2. Senão → busca só por ID (comportamento original)

    Na planilha do cliente, linhas com variação preenchida formam chaves compostas;
    linhas sem variação formam chaves simples.
    """
    _LOOKUP = f"__sku_lookup__"

    # ── Normalizar IDs ──────────────────────────────────────────────────────
    df_s = df_sistema.copy()
    df_c = df_cliente.copy()

    # ── Construir chaves no sistema ─────────────────────────────────────────
    df_s["__chave_s__"] = _chave_composta(df_s, col_id_sistema, col_var_sistema)

    # ── Construir lookup do cliente ─────────────────────────────────────────
    # Cada linha do cliente pode gerar até duas entradas:
    #   - chave composta (id||var)  quando variação preenchida
    #   - chave simples  (id)       sempre (fallback)
    df_c_base = df_c.dropna(subset=[col_id_cliente, col_sku_cliente]).copy()
    df_c_base[col_id_cliente] = df_c_base[col_id_cliente].astype(str).str.strip()

    entradas = []

    if col_var_cliente and col_var_cliente in df_c_base.columns:
        df_c_base["__var_c__"] = (
            df_c_base[col_var_cliente].astype(str).str.strip()
            .replace({"nan": "", "None": "", "0": ""})
        )
        # Linhas com variação → chave composta (prioridade)
        com_var = df_c_base[df_c_base["__var_c__"] != ""].copy()
        com_var["__chave_c__"] = com_var[col_id_cliente] + "||" + com_var["__var_c__"]
        entradas.append(com_var[["__chave_c__", col_sku_cliente]])

        # Linhas SEM variação → chave simples (fallback)
        sem_var = df_c_base[df_c_base["__var_c__"] == ""].copy()
        sem_var["__chave_c__"] = sem_var[col_id_cliente]
        entradas.append(sem_var[["__chave_c__", col_sku_cliente]])
    else:
        # Sem coluna de variação: chave simples para tudo
        df_c_base["__chave_c__"] = df_c_base[col_id_cliente]
        entradas.append(df_c_base[["__chave_c__", col_sku_cliente]])

    df_lookup = pd.concat(entradas, ignore_index=True)
    df_lookup = df_lookup.drop_duplicates(subset=["__chave_c__"])
    df_lookup = df_lookup.rename(columns={col_sku_cliente: _LOOKUP})

    # ── Merge ────────────────────────────────────────────────────────────────
    df_resultado = df_s.merge(
        df_lookup,
        left_on="__chave_s__",
        right_on="__chave_c__",
        how="left",
        suffixes=("", "_drop"),
    )

    if col_sku_sistema not in df_resultado.columns:
        df_resultado[col_sku_sistema] = ""

    if sobrescrever:
        df_resultado[col_sku_sistema] = df_resultado[_LOOKUP].fillna(df_resultado[col_sku_sistema])
    else:
        mask_vazio = (
            df_resultado[col_sku_sistema].isna() |
            (df_resultado[col_sku_sistema].astype(str).str.strip() == "")
        )
        df_resultado.loc[mask_vazio, col_sku_sistema] = df_resultado.loc[mask_vazio, _LOOKUP]

    # Limpar colunas auxiliares
    df_resultado = df_resultado.drop(
        columns=[c for c in ["__chave_s__", "__chave_c__", _LOOKUP] if c in df_resultado.columns],
        errors="ignore",
    )

    total = len(df_resultado)
    preenchidos = int(
        (~df_resultado[col_sku_sistema].isna() &
         (df_resultado[col_sku_sistema].astype(str).str.strip() != "")).sum()
    )

    stats = {
        "total_linhas": total,
        "preenchidos": preenchidos,
        "nao_encontrados": total - preenchidos,
        "taxa_sucesso": f"{(preenchidos / total * 100):.1f}%" if total > 0 else "N/A",
    }

    return df_resultado, stats


# --- INICIALIZAÇÃO DE ESTADO ---
defaults = {
    "df_principal": None,
    "qa_checks": {},
    "session_id": str(uuid.uuid4())[:8].upper(),
    "nome_arquivo": "",
    "df_erros_cache": None,
    "historico_alteracoes": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <h2>🚀 Importador Pro</h2>
            <p>v5 · Enterprise Suite</p>
        </div>
    """, unsafe_allow_html=True)

    st.caption(f"Sessão · `{st.session_state.session_id}`")
    st.divider()

    if st.session_state.df_principal is not None:
        col1, col2 = st.columns(2)
        nome_exibir = st.session_state.nome_arquivo
        if len(nome_exibir) > 18:
            nome_exibir = nome_exibir[:18] + "…"
        col1.metric("Arquivo", nome_exibir)
        col2.metric("Registros", f"{len(st.session_state.df_principal):,}")

    st.divider()
    st.subheader("📁 Planilha Principal")

    uploaded_file = st.file_uploader(
        "Carregar planilha do sistema",
        type=["xlsx", "csv"],
        help="Formatos aceitos: .xlsx e .csv",
        label_visibility="collapsed"
    )

    if uploaded_file:
        if (
            st.session_state.df_principal is None
            or uploaded_file.name != st.session_state.nome_arquivo
        ):
            with st.spinner("Processando…"):
                df_novo = ler_arquivo(uploaded_file)
                df_novo = garantir_colunas(df_novo)
                st.session_state.df_principal = df_novo
                st.session_state.nome_arquivo = uploaded_file.name
                st.session_state.qa_checks = {}
                st.session_state.df_erros_cache = None
                st.session_state.historico_alteracoes = []
            st.success(f"✅ `{uploaded_file.name}` carregado!")
            st.rerun()

    if st.session_state.df_principal is not None:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpar", use_container_width=True):
                for key in defaults:
                    st.session_state[key] = defaults[key]
                st.rerun()
        with col2:
            st.download_button(
                "⬇️ Template",
                data=pd.DataFrame(columns=COLUNAS_EDITAVEIS).to_csv(index=False).encode('utf-8'),
                file_name="template_importador.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.divider()
    with st.expander("ℹ️ Guia Rápido"):
        st.markdown("""
        **Fluxo de trabalho:**
        1. 📤 Carregue a planilha principal
        2. 🔗 Use o PROCV para preencher SKUs
        3. 📝 Edite dados se necessário
        4. 🚨 Valide consistência
        5. ✅ Revise por lotes e exporte
        """)


# ============================================================
# CORPO PRINCIPAL — TELA INICIAL
# ============================================================
if st.session_state.df_principal is None:
    st.markdown("""
        <div class="app-header" style="text-align:center; padding: 3rem 2rem;">
            <h1 style="font-size:2rem !important; margin-bottom:0.5rem !important;">🚀 Importador Pro v5</h1>
            <p>Sistema inteligente de importação e validação de dados · Enterprise</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    features = [
        ("🎯", "Precisão", "Validação inteligente de EAN, SKU e campos obrigatórios"),
        ("⚡", "Performance", "Processamento otimizado para grandes volumes de dados"),
        ("🔒", "Confiabilidade", "QA Gate com revisão por lotes e log de auditoria"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(f"""
                <div class="kpi-card" style="text-align:left; padding:1.5rem;">
                    <div style="font-size:1.75rem; margin-bottom:0.6rem;">{icon}</div>
                    <div style="font-weight:700; font-size:0.95rem; color:#0f172a; margin-bottom:0.4rem;">{title}</div>
                    <div style="font-size:0.82rem; color:#64748b;">{desc}</div>
                </div>
            """, unsafe_allow_html=True)

    st.info("👈 Faça o upload da planilha no menu lateral para começar.")
    st.stop()


# ============================================================
# APP HEADER
# ============================================================
st.markdown(f"""
    <div class="app-header">
        <h1>📊 {st.session_state.nome_arquivo}</h1>
        <p>Sessão: {st.session_state.session_id} · Atualizado: {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
""", unsafe_allow_html=True)

# ABAS
tab_busca, tab_editor, tab_procv, tab_erros, tab_export = st.tabs([
    "🔍 Dashboard & Busca",
    "📝 Editor",
    "🔗 PROCV / De-Para",
    "🚨 Validação",
    "✅ QA Exportação",
])


# ============================================================
# ABA 1 — DASHBOARD & BUSCA
# ============================================================
with tab_busca:
    df = st.session_state.df_principal

    col_sku_real = resolver_coluna(df, COLUNA_SKU)
    skus_vazios = contar_vazios(df, col_sku_real) if col_sku_real in df.columns else len(df)
    skus_preenchidos = len(df) - skus_vazios
    taxa_sku = (skus_preenchidos / len(df) * 100) if len(df) > 0 else 0

    if st.session_state.df_erros_cache is not None:
        n_erros = len(st.session_state.df_erros_cache)
        erros_label = str(n_erros)
    else:
        erros_label = "—"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        cor_valor = "kpi-accent"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value {cor_valor}">{len(df):,}</div>
                <div class="kpi-label">Total Registros</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value kpi-purple">{len(df.columns)}</div>
                <div class="kpi-label">Colunas</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        cor = "kpi-success" if taxa_sku > 90 else "kpi-warning"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value {cor}">{taxa_sku:.1f}%</div>
                <div class="kpi-label">Taxa SKU</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        cor_e = "kpi-danger" if erros_label not in ("0", "—") else "kpi-success"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value {cor_e}">{erros_label}</div>
                <div class="kpi-label">Erros Detectados</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("🔎 Pesquisa")

    col_search, col_filter = st.columns([3, 1])
    with col_search:
        termo = st.text_input(
            "Buscar",
            placeholder="Buscar por SKU, Marca, EAN, ID…",
            label_visibility="collapsed"
        )
    with col_filter:
        modo_busca = st.selectbox("Modo", ["Contém", "Exato", "Regex"], label_visibility="collapsed")

    if termo:
        if modo_busca == "Contém":
            mask = df.astype(str).apply(lambda x: x.str.contains(termo, case=False, na=False)).any(axis=1)
        elif modo_busca == "Exato":
            mask = df.astype(str).apply(lambda x: x.str.strip().str.lower() == termo.strip().lower()).any(axis=1)
        else:
            try:
                mask = df.astype(str).apply(lambda x: x.str.contains(termo, case=False, na=False, regex=True)).any(axis=1)
            except:
                st.error("Expressão regular inválida!")
                mask = pd.Series([True] * len(df))

        resultados = df[mask]
        st.caption(f"{len(resultados):,} resultado(s) para `{termo}`")
        st.dataframe(resultados, use_container_width=True, height=480)
    else:
        col_prev, col_chart = st.columns([3, 1])

        with col_prev:
            st.dataframe(df.head(50), use_container_width=True, height=480)
            if len(df) > 50:
                st.caption(f"Exibindo 50 de {len(df):,} linhas")

        with col_chart:
            st.markdown("**Completude das Colunas**")
            completude = {
                col: (len(df) - contar_vazios(df, col)) / len(df) * 100
                for col in df.columns
            }
            df_completude = pd.DataFrame({
                "Coluna": list(completude.keys()),
                "% Preenchido": list(completude.values())
            }).sort_values("% Preenchido", ascending=True)

            fig = px.bar(
                df_completude,
                x="% Preenchido",
                y="Coluna",
                orientation='h',
                color="% Preenchido",
                color_continuous_scale=["#fca5a5", "#fde68a", "#6ee7b7"],
                range_color=[0, 100],
            )
            fig.update_layout(
                height=max(280, len(df.columns) * 22),
                margin=dict(l=0, r=10, t=10, b=0),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 100]),
                yaxis=dict(showgrid=False),
                font=dict(family="DM Sans", size=11),
                coloraxis_showscale=False,
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ABA 2 — EDITOR AVANÇADO  (INLINE EDITING CORRIGIDO)
# ============================================================
with tab_editor:
    st.header("📝 Editor de Planilha")

    df_atual = st.session_state.df_principal

    # Identificar colunas editáveis que realmente existem no df
    colunas_edit_reais = []
    for c in COLUNAS_EDITAVEIS:
        col_real = resolver_coluna(df_atual, c)
        if col_real in df_atual.columns:
            colunas_edit_reais.append(col_real)

    # Colunas bloqueadas = todas as que NÃO estão na lista editável
    colunas_bloqueadas = [c for c in df_atual.columns if c not in colunas_edit_reais]

    col_info, col_stats = st.columns([2, 1])
    with col_info:
        edit_names = ", ".join([f"`{c}`" for c in colunas_edit_reais])
        st.caption(f"✏️ Colunas editáveis: {edit_names} · Demais são somente leitura")
    with col_stats:
        if st.session_state.historico_alteracoes:
            st.info(f"🕒 {len(st.session_state.historico_alteracoes)} alterações nesta sessão")

    # -------------------------------------------------------
    # Preparar DataFrame para o editor:
    # - Colunas editáveis de texto: converter para str (evita conflito de tipo)
    # - "Kit quantidade": manter numérico se possível
    # - Colunas bloqueadas: deixar como estão (somente leitura)
    # -------------------------------------------------------
    df_editor_input = df_atual.copy()

    col_kit_real = resolver_coluna(df_editor_input, "Kit quantidade")
    col_ean_real = resolver_coluna(df_editor_input, "EAN")

    for col in colunas_edit_reais:
        if col == col_kit_real:
            # Tentar converter para numérico; NaN vira 0
            df_editor_input[col] = pd.to_numeric(df_editor_input[col], errors='coerce').fillna(0).astype(int)
        else:
            # Converter para string limpa
            df_editor_input[col] = (
                df_editor_input[col]
                .fillna("")
                .astype(str)
                .str.strip()
                .replace("nan", "")
                .replace("None", "")
            )

    # column_config apenas para colunas editáveis com tipos bem definidos
    column_config = {}
    for col in colunas_edit_reais:
        if col == col_kit_real:
            column_config[col] = st.column_config.NumberColumn(
                col,
                min_value=0,
                step=1,
                format="%d",
                help="Quantidade do kit"
            )
        else:
            column_config[col] = st.column_config.TextColumn(col)

    # DATA EDITOR
    df_editado = st.data_editor(
        df_editor_input,
        use_container_width=True,
        num_rows="fixed",
        disabled=colunas_bloqueadas,
        key="editor_principal",
        height=600,
        column_config=column_config,
        hide_index=False,
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
            if not df_editado.equals(df_atual):
                st.session_state.historico_alteracoes.append({
                    "timestamp": datetime.now().isoformat(),
                    "linhas_alteradas": int((df_editado != df_atual).any(axis=1).sum())
                })
                st.session_state.df_principal = df_editado
                st.session_state.df_erros_cache = None
                st.toast("✅ Alterações salvas!", icon="✅")
                st.rerun()
            else:
                st.toast("ℹ️ Nenhuma alteração detectada")

    with col2:
        if st.button("↩️ Reverter", use_container_width=True):
            st.info("💡 Para reverter, recarregue o arquivo original no menu lateral.")

    with col3:
        st.download_button(
            "⬇️ Exportar Editado (CSV)",
            data=df_editado.to_csv(index=False).encode('utf-8'),
            file_name=f"editado_{st.session_state.session_id}.csv",
            mime="text/csv",
            use_container_width=True
        )


# ============================================================
# ABA 3 — PROCV / DE-PARA
# ============================================================
with tab_procv:
    st.header("🔗 PROCV — De/Para Automático")
    st.markdown(
        "Combine dados de planilhas externas usando **ID do canal de venda** como chave. "
        "O sistema preenche automaticamente os SKUs correspondentes."
    )

    st.caption("📤 Planilha do Cliente (fonte dos SKUs)")
    ext_file = st.file_uploader(
        "Planilha do Cliente",
        type=["xlsx", "csv"],
        key="ext_upload",
        label_visibility="collapsed",
    )

    if ext_file:
        df_ext = ler_arquivo(ext_file)

        c1, c2, c3 = st.columns(3)
        c1.metric("Registros", f"{len(df_ext):,}")
        c2.metric("Colunas", len(df_ext.columns))
        c3.metric("Tamanho", f"{ext_file.size / 1024:.1f} KB")

        with st.expander("👁️ Preview da Planilha Fonte"):
            st.dataframe(df_ext.head(10), use_container_width=True)

        st.divider()
        st.subheader("⚙️ Configurar Mapeamento")

        # ── Colunas obrigatórias ───────────────────────────────────────────
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**🔵 Planilha do Sistema (Destino)**")
            col_id_sistema  = st.selectbox("Coluna de ID do Anúncio", st.session_state.df_principal.columns, key="id_sistema")
            col_sku_sistema = st.selectbox("Coluna SKU (destino)",    st.session_state.df_principal.columns, key="sku_sistema")

        with col_b:
            st.markdown("**🟢 Planilha do Cliente (Origem)**")
            col_id_cliente  = st.selectbox("Coluna de ID do Anúncio", df_ext.columns, key="id_cliente")
            col_sku_cliente = st.selectbox("Coluna SKU (origem)",     df_ext.columns, key="sku_cliente")

        # ── Coluna de variação (opcional) ──────────────────────────────────
        st.divider()
        st.markdown("**🔀 Chave de Variação (opcional)**")
        st.caption(
            "Quando preenchido, o sistema usa **ID Anúncio + ID Variação** como chave composta. "
            "Linhas sem variação continuam usando só o ID do Anúncio."
        )

        cols_none_s = ["— não usar —"] + list(st.session_state.df_principal.columns)
        cols_none_c = ["— não usar —"] + list(df_ext.columns)

        cv_a, cv_b = st.columns(2)
        with cv_a:
            col_var_sistema_raw = st.selectbox(
                "ID Variação — Sistema", cols_none_s, key="var_sistema",
                help="Coluna de ID de variação na planilha do sistema"
            )
        with cv_b:
            col_var_cliente_raw = st.selectbox(
                "ID Variação — Cliente", cols_none_c, key="var_cliente",
                help="Coluna de ID de variação na planilha do cliente"
            )

        col_var_sistema = None if col_var_sistema_raw == "— não usar —" else col_var_sistema_raw
        col_var_cliente = None if col_var_cliente_raw == "— não usar —" else col_var_cliente_raw

        # ── Info box dinâmico ──────────────────────────────────────────────
        if col_var_sistema and col_var_cliente:
            logica_txt = (
                f"<code>Sistema.{col_id_sistema}</code> + <code>Sistema.{col_var_sistema}</code> "
                f"↔ <code>Cliente.{col_id_cliente}</code> + <code>Cliente.{col_var_cliente}</code> "
                f"→ <code>Cliente.{col_sku_cliente}</code> → <code>Sistema.{col_sku_sistema}</code><br>"
                f"<small>⚡ Fallback automático: se variação não for encontrada, tenta só pelo ID do anúncio.</small>"
            )
        else:
            logica_txt = (
                f"<code>Sistema.{col_id_sistema}</code> ↔ <code>Cliente.{col_id_cliente}</code> "
                f"→ <code>Cliente.{col_sku_cliente}</code> → <code>Sistema.{col_sku_sistema}</code>"
            )

        st.markdown(f'''
            <div class="info-box">
                🔗 <strong>Lógica:</strong> {logica_txt}
            </div>
        ''', unsafe_allow_html=True)

        st.divider()
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            sobrescrever = st.checkbox("🔄 Sobrescrever SKUs já preenchidos", value=False)
        with col_opt2:
            st.checkbox("🚫 Ignorar IDs não encontrados", value=True)

        if st.button("🚀 Executar PROCV", type="primary", use_container_width=True):
            with st.spinner("Processando merge…"):
                try:
                    df_resultado, stats = executar_merge_procv(
                        df_sistema=st.session_state.df_principal.copy(),
                        df_cliente=df_ext,
                        col_id_sistema=col_id_sistema,
                        col_id_cliente=col_id_cliente,
                        col_sku_cliente=col_sku_cliente,
                        col_sku_sistema=col_sku_sistema,
                        sobrescrever=sobrescrever,
                        col_var_sistema=col_var_sistema,
                        col_var_cliente=col_var_cliente,
                    )
                    st.session_state.df_principal = df_resultado
                    st.session_state.df_erros_cache = None
                    st.success("✅ PROCV executado com sucesso!")

                    r1, r2, r3 = st.columns(3)
                    r1.metric("✅ SKUs Preenchidos", f"{stats['preenchidos']:,}")
                    r2.metric("⚠️ Não Encontrados", f"{stats['nao_encontrados']:,}")
                    r3.metric("📊 Taxa de Sucesso", stats['taxa_sucesso'])

                    fig = go.Figure(data=[go.Pie(
                        labels=['Preenchidos', 'Não Encontrados'],
                        values=[stats['preenchidos'], stats['nao_encontrados']],
                        hole=.45,
                        marker_colors=['#059669', '#f59e0b'],
                        textinfo='label+percent',
                    )])
                    fig.update_layout(
                        title="Resultado do PROCV",
                        height=300,
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="DM Sans"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    if stats['nao_encontrados'] > 0:
                        with st.expander(f"📋 {stats['nao_encontrados']} IDs sem match"):
                            cols_sem = [col_id_sistema]
                            if col_var_sistema and col_var_sistema in df_resultado.columns:
                                cols_sem.append(col_var_sistema)
                            sem_match = df_resultado[
                                df_resultado[col_sku_sistema].isna() |
                                (df_resultado[col_sku_sistema].astype(str).str.strip() == "")
                            ][cols_sem]
                            st.dataframe(sem_match, use_container_width=True)

                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro no merge: {str(e)}")
    else:
        st.info("👆 Faça upload da planilha do cliente para configurar o De-Para")


# ============================================================
# ABA 4 — VALIDAÇÃO & ERROS
# ============================================================
with tab_erros:
    st.header("🚨 Central de Validação")

    col_btn, col_auto = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 Validar Agora", type="primary", use_container_width=True):
            with st.spinner("Validando…"):
                st.session_state.df_erros_cache = validar_dataframe(st.session_state.df_principal)
            st.rerun()
    with col_auto:
        st.caption("💡 Clique em Validar Agora ou a validação roda automaticamente ao abrir a aba")

    if st.session_state.df_erros_cache is None:
        with st.spinner("Executando validação…"):
            st.session_state.df_erros_cache = validar_dataframe(st.session_state.df_principal)

    df_erros = st.session_state.df_erros_cache

    if df_erros.empty:
        st.success("🎉 **Dados 100% consistentes!** Nenhum erro encontrado.")
    else:
        criticos = len(df_erros[df_erros["Severidade"] == "🚨 Crítico"])
        alertas  = len(df_erros[df_erros["Severidade"] == "⚠️ Alerta"])
        infos    = len(df_erros[df_erros["Severidade"] == "ℹ️ Informativo"])

        c_c, c_a, c_i = st.columns(3)
        with c_c: st.error(f"🚨 **{criticos} Críticos**")
        with c_a: st.warning(f"⚠️ **{alertas} Alertas**")
        with c_i: st.info(f"ℹ️ **{infos} Informativos**")

        fig = go.Figure(data=[go.Bar(
            x=['Críticos', 'Alertas', 'Informativos'],
            y=[criticos, alertas, infos],
            marker_color=['#dc2626', '#d97706', '#2563eb'],
            text=[criticos, alertas, infos],
            textposition='auto',
        )])
        fig.update_layout(
            title="Distribuição de Erros",
            height=280,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans"),
            margin=dict(t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        f1, f2 = st.columns(2)
        with f1:
            filtro_sev = st.multiselect(
                "Severidade",
                ["🚨 Crítico", "⚠️ Alerta", "ℹ️ Informativo"],
                default=["🚨 Crítico", "⚠️ Alerta"]
            )
        with f2:
            filtro_campo = st.multiselect(
                "Campo",
                list(df_erros["Campo"].unique()),
                default=list(df_erros["Campo"].unique())
            )

        df_exibir = df_erros[
            df_erros["Severidade"].isin(filtro_sev) &
            df_erros["Campo"].isin(filtro_campo)
        ]

        st.dataframe(
            df_exibir,
            use_container_width=True,
            height=380,
            column_config={
                "Nº Linha": st.column_config.NumberColumn("Linha", format="%d"),
                "Severidade": st.column_config.TextColumn("Severidade", width="small"),
                "Descrição": st.column_config.TextColumn("Descrição", width="large"),
            },
            hide_index=True
        )
        st.caption(f"{len(df_exibir)} erros exibidos · Corrija na aba **Editor**")

        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "⬇️ Relatório CSV",
                data=df_erros.to_csv(index=False, sep=';').encode('utf-8'),
                file_name=f"erros_{st.session_state.session_id}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with d2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                df_erros.to_excel(w, index=False, sheet_name='Erros')
            st.download_button(
                "📊 Relatório Excel",
                data=buf.getvalue(),
                file_name=f"erros_{st.session_state.session_id}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


# ============================================================
# ABA 5 — QA EXPORTAÇÃO
# ============================================================
with tab_export:
    st.header("✅ QA Gate — Revisão por Lotes")

    df_final = st.session_state.df_principal

    if len(df_final) == 0:
        st.warning("📭 A planilha está vazia.")
        st.stop()

    total_lotes  = math.ceil(len(df_final) / TAMANHO_LOTE)
    revisados    = len(st.session_state.qa_checks)
    lotes_ok     = sum(1 for v in st.session_state.qa_checks.values() if v == "OK")
    lotes_cor    = sum(1 for v in st.session_state.qa_checks.values() if v == "CORRIGIR")
    progresso    = revisados / total_lotes if total_lotes > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value kpi-accent">{progresso:.0%}</div><div class="kpi-label">Progresso</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value kpi-success">{lotes_ok}</div><div class="kpi-label">Aprovados</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value kpi-danger">{lotes_cor}</div><div class="kpi-label">p/ Correção</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value kpi-warning">{total_lotes - revisados}</div><div class="kpi-label">Pendentes</div></div>', unsafe_allow_html=True)

    st.progress(progresso, text=f"{revisados}/{total_lotes} lotes revisados")
    st.divider()

    st.subheader("🔍 Revisar Lote")
    lote_atual = st.selectbox(
        "Selecionar lote:",
        range(1, total_lotes + 1),
        format_func=lambda x: (
            f"Lote {x} · ✅ OK" if st.session_state.qa_checks.get(x) == "OK"
            else f"Lote {x} · ⚠️ Corrigir" if st.session_state.qa_checks.get(x) == "CORRIGIR"
            else f"Lote {x} · ⬜ Pendente"
        )
    )

    inicio = (lote_atual - 1) * TAMANHO_LOTE
    fim    = min(inicio + TAMANHO_LOTE, len(df_final))
    preview_lote = df_final.iloc[inicio:fim]

    colunas_preview = []
    for col in [COLUNA_ID_ANUNCIO] + COLUNAS_EDITAVEIS:
        col_real = resolver_coluna(df_final, col)
        if col_real in df_final.columns and col_real not in colunas_preview:
            colunas_preview.append(col_real)

    status_atual = st.session_state.qa_checks.get(lote_atual, "⬜ Pendente")
    st.caption(f"Lote **{lote_atual}/{total_lotes}** · Linhas {inicio+1}–{fim} · Status: `{status_atual}`")

    st.dataframe(
        preview_lote[colunas_preview] if colunas_preview else preview_lote,
        use_container_width=True,
        height=380
    )

    col_ok, col_cor, col_limpar = st.columns([2, 2, 0.8])
    with col_ok:
        if st.button(f"✅ Aprovar Lote {lote_atual}", use_container_width=True, type="primary"):
            st.session_state.qa_checks[lote_atual] = "OK"
            st.toast(f"✅ Lote {lote_atual} aprovado!")
            st.rerun()
    with col_cor:
        if st.button(f"⚠️ Marcar p/ Correção", use_container_width=True):
            st.session_state.qa_checks[lote_atual] = "CORRIGIR"
            st.toast(f"⚠️ Lote {lote_atual} marcado para correção")
            st.rerun()
    with col_limpar:
        if st.button("↩️", use_container_width=True, help="Limpar status"):
            st.session_state.qa_checks.pop(lote_atual, None)
            st.rerun()

    st.divider()
    st.subheader("🗺️ Mapa de Lotes")

    n_cols = min(total_lotes, 14)
    cols_mapa = st.columns(n_cols)
    for i in range(total_lotes):
        lote_n = i + 1
        status = st.session_state.qa_checks.get(lote_n, "")
        emoji = "✅" if status == "OK" else "⚠️" if status == "CORRIGIR" else "⬜"
        cor   = "#059669" if status == "OK" else "#dc2626" if status == "CORRIGIR" else "#94a3b8"
        with cols_mapa[i % n_cols]:
            st.markdown(f"""
                <div style="text-align:center; padding:0.3rem 0;">
                    <div style="font-size:1.3rem;">{emoji}</div>
                    <div style="font-size:0.65rem; color:{cor}; font-weight:700;">L{lote_n}</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    if revisados < total_lotes:
        st.warning(f"⏳ **{total_lotes - revisados} lotes pendentes.** Revise todos para liberar a exportação.")
    else:
        st.success("🎉 **Todos os lotes revisados!** Exportação liberada.")
        st.balloons()

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_final = calcular_hash(df_final)

        log = {
            "sistema": "Importador Pro v5",
            "sessao": st.session_state.session_id,
            "arquivo": st.session_state.nome_arquivo,
            "data_hora": ts,
            "total_linhas": int(len(df_final)),
            "total_lotes": total_lotes,
            "hash_sha256": hash_final,
            "resultado_lotes": {
                f"lote_{i}": st.session_state.qa_checks.get(i, "NÃO REVISADO")
                for i in range(1, total_lotes + 1)
            }
        }

        e1, e2 = st.columns(2)
        with e1:
            st.download_button(
                "⬇️ Planilha Final (CSV)",
                data=df_final.to_csv(index=False).encode('utf-8'),
                file_name=f"importacao_final_{ts}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                df_final.to_excel(w, index=False, sheet_name='Dados')
            st.download_button(
                "📊 Planilha Final (Excel)",
                data=buf.getvalue(),
                file_name=f"importacao_final_{ts}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with e2:
            st.download_button(
                "📋 Log Auditoria (JSON)",
                data=json.dumps(log, indent=2, ensure_ascii=False),
                file_name=f"qa_log_{ts}.json",
                mime="application/json",
                use_container_width=True
            )
            log_txt = "\n".join([
                "=" * 52,
                "  LOG DE AUDITORIA — IMPORTADOR PRO v5",
                "=" * 52,
                f"Sessão   : {log['sessao']}",
                f"Arquivo  : {log['arquivo']}",
                f"Data/Hora: {log['data_hora']}",
                f"Linhas   : {log['total_linhas']}",
                f"Lotes    : {log['total_lotes']}",
                f"Hash SHA : {log['hash_sha256']}", "",
                "Resultado por Lote:",
            ] + [f"  {k.replace('lote_','Lote ').zfill(3)}: {v}" for k, v in log['resultado_lotes'].items()])
            st.download_button(
                "📄 Log Auditoria (TXT)",
                data=log_txt,
                file_name=f"qa_log_{ts}.txt",
                mime="text/plain",
                use_container_width=True
            )


# --- RODAPÉ ---
st.markdown("---")
st.markdown(
    f"<div style='text-align:center; color:#94a3b8; font-size:0.75rem; font-family:DM Mono,monospace;'>"
    f"🚀 Importador Pro v5 Enterprise · Sessão {st.session_state.session_id} · "
    f"© {datetime.now().year}"
    f"</div>",
    unsafe_allow_html=True
)
