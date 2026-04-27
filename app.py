import streamlit as st
import pandas as pd
import io
import uuid
import hashlib
from datetime import datetime
import math
import json
import re
from typing import Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Importador Pro v4 | Enterprise",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# --- CSS PROFISSIONAL AVANÇADO ---
st.markdown("""
    <style>
    /* ========== DESIGN SYSTEM ========== */
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --success: #059669;
        --warning: #d97706;
        --danger: #dc2626;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-900: #111827;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }

    /* ========== GLOBAL STYLES ========== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
    }

    /* ========== HEADER ========== */
    .app-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }
    .app-header h1 {
        color: white !important;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .app-header p {
        color: #94a3b8;
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }

    /* ========== TABS AVANÇADAS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--gray-100);
        padding: 8px;
        border-radius: 12px;
        box-shadow: var(--shadow-sm);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        color: var(--gray-600);
        border: none;
        transition: all 0.3s;
        font-size: 0.95rem;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: white;
        color: var(--primary);
        box-shadow: var(--shadow-sm);
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: var(--primary) !important;
        box-shadow: var(--shadow-md) !important;
        font-weight: 600 !important;
    }

    /* ========== CARDS & METRICS ========== */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--gray-200);
        transition: all 0.3s;
    }
    .card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    .metric-card {
        text-align: center;
        padding: 1.5rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary) 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
    }
    .metric-label {
        color: var(--gray-600);
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ========== BADGES ========== */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-success { background: #d1fae5; color: #065f46; }
    .badge-warning { background: #fef3c7; color: #92400e; }
    .badge-danger { background: #fee2e2; color: #991b1b; }
    .badge-info { background: #dbeafe; color: #1e40af; }

    /* ========== BUTTONS ========== */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
        padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }

    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        border-right: 1px solid var(--gray-200);
    }
    .sidebar-header {
        padding: 1rem;
        background: var(--primary);
        color: white;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    /* ========== DATA EDITOR ========== */
    .stDataEditor {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }

    /* ========== PROGRESS BAR ========== */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, #7c3aed 100%);
        border-radius: 10px;
    }

    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--gray-700);
    }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
COLUNA_SKU = "SKU"
COLUNA_ID_ANUNCIO = "ID do canal de venda"
COLUNAS_EDITAVEIS = ["Marca", "EAN", "SKU", "Kit quantidade", "Código Depósito"]
COLUNAS_OBRIGATORIAS = ["SKU"]
TAMANHO_LOTE = 10

# --- FUNÇÕES UTILITÁRIAS MELHORADAS ---

@st.cache_data(ttl=3600)
def normalizar_nome_col(nome: str) -> str:
    """Remove sufixos e normaliza nomes de colunas com cache."""
    nome = re.sub(r'\s*\([A-Z]\)\s*$', '', str(nome))
    return nome.strip().lower()


def resolver_coluna(df: pd.DataFrame, nome_desejado: str, criar_se_nao_existir: bool = False) -> str:
    """
    Encontra o nome real da coluna no DataFrame, com opção de criar se não existir.
    """
    alvo = normalizar_nome_col(nome_desejado)
    for col in df.columns:
        if normalizar_nome_col(col) == alvo:
            return col
    
    if criar_se_nao_existir and nome_desejado not in df.columns:
        df[nome_desejado] = ""
        return nome_desejado
    
    return nome_desejado


def resolver_colunas_editaveis(df: pd.DataFrame) -> list:
    """Retorna os nomes reais das colunas editáveis."""
    return [resolver_coluna(df, c, criar_se_nao_existir=True) for c in COLUNAS_EDITAVEIS]


def resolver_colunas_obrigatorias(df: pd.DataFrame) -> list:
    """Retorna os nomes reais das colunas obrigatórias."""
    return [resolver_coluna(df, c) for c in COLUNAS_OBRIGATORIAS]


def calcular_hash(df: pd.DataFrame) -> str:
    """Calcula hash SHA256 otimizado do DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=True).values.tobytes()
    ).hexdigest()


def normalizar_ean(valor) -> str:
    """Normaliza valores EAN para string numérica."""
    if pd.isna(valor):
        return ""
    try:
        return str(int(float(str(valor).strip())))
    except (ValueError, OverflowError):
        return str(valor).strip()


def contar_vazios(df: pd.DataFrame, coluna: str) -> int:
    """Conta valores vazios de forma padronizada."""
    if coluna not in df.columns:
        return len(df)
    return (
        df[coluna].isna() | 
        df[coluna].astype(str).str.strip().isin(["", "None", "nan"])
    ).sum()


def validar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validação completa do DataFrame com categorização de erros."""
    erros = []
    cols_obrigatorias_reais = resolver_colunas_obrigatorias(df)
    col_ean_real = resolver_coluna(df, "EAN")
    
    # Processing em lotes para melhor performance
    for idx in range(len(df)):
        row = df.iloc[idx]
        
        # Validação de SKU (obrigatório)
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
        
        # Validação de EAN (opcional)
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


def garantir_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Garante que todas as colunas editáveis existam no DataFrame."""
    for col in COLUNAS_EDITAVEIS:
        if col not in df.columns:
            df[col] = ""
    return df


def ler_arquivo(file) -> pd.DataFrame:
    """Leitura robusta de arquivos com múltiplos encodings."""
    try:
        if file.name.endswith(".csv"):
            # Tenta múltiplos encodings
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


def executar_merge_procv(
    df_sistema: pd.DataFrame,
    df_cliente: pd.DataFrame,
    col_id_sistema: str,
    col_id_cliente: str,
    col_sku_cliente: str,
    col_sku_sistema: str,
    sobrescrever: bool = False
) -> Tuple[pd.DataFrame, dict]:
    """
    Executa o merge PROCV de forma otimizada usando pandas merge.
    Retorna o DataFrame atualizado e estatísticas.
    """
    # Normaliza colunas de ID
    df_sistema[col_id_sistema] = df_sistema[col_id_sistema].astype(str).str.strip()
    df_cliente[col_id_cliente] = df_cliente[col_id_cliente].astype(str).str.strip()
    
    # Prepara DataFrame de lookup único
    df_lookup = df_cliente.dropna(subset=[col_id_cliente, col_sku_cliente])
    df_lookup = df_lookup.drop_duplicates(subset=[col_id_cliente])[[col_id_cliente, col_sku_cliente]]
    df_lookup = df_lookup.rename(columns={col_sku_cliente: f"{col_sku_sistema}_lookup"})
    
    # Executa merge
    df_resultado = df_sistema.merge(
        df_lookup,
        left_on=col_id_sistema,
        right_on=col_id_cliente,
        how='left',
        suffixes=('', '_drop')
    )
    
    # Aplica lógica de sobrescrita
    col_lookup = f"{col_sku_sistema}_lookup"
    if col_sku_sistema not in df_resultado.columns:
        df_resultado[col_sku_sistema] = ""
    
    if sobrescrever:
        df_resultado[col_sku_sistema] = df_resultado[col_lookup].fillna(df_resultado[col_sku_sistema])
    else:
        mask_vazio = (
            df_resultado[col_sku_sistema].isna() | 
            (df_resultado[col_sku_sistema].astype(str).str.strip() == "")
        )
        df_resultado.loc[mask_vazio, col_sku_sistema] = df_resultado.loc[mask_vazio, col_lookup]
    
    # Remove coluna temporária
    df_resultado = df_resultado.drop(columns=[col_lookup, col_id_cliente], errors='ignore')
    
    # Calcula estatísticas
    total = len(df_resultado)
    preenchidos = (~df_resultado[col_sku_sistema].isna() & 
                   (df_resultado[col_sku_sistema].astype(str).str.strip() != "")).sum()
    
    stats = {
        "total_linhas": total,
        "preenchidos": int(preenchidos),
        "nao_encontrados": total - int(preenchidos),
        "taxa_sucesso": f"{(preenchidos/total*100):.1f}%" if total > 0 else "N/A"
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
# SIDEBAR PROFISSIONAL
# ============================================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h2 style="margin:0; font-size:1.5rem;">🚀 Importador Pro v4</h2>
            <p style="margin:0; font-size:0.8rem; opacity:0.9;">Enterprise Suite</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"📋 Sessão: `{st.session_state.session_id}`")
    
    st.divider()
    
    # Status do sistema
    if st.session_state.df_principal is not None:
        col1, col2 = st.columns(2)
        col1.metric("📄 Arquivo", st.session_state.nome_arquivo[:20] + "..." if len(st.session_state.nome_arquivo) > 20 else st.session_state.nome_arquivo)
        col2.metric("📊 Registros", f"{len(st.session_state.df_principal):,}")
    
    st.divider()
    
    st.subheader("📁 Gerenciar Planilha")
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
            with st.spinner("🔄 Processando arquivo..."):
                df_novo = ler_arquivo(uploaded_file)
                df_novo = garantir_colunas(df_novo)
                st.session_state.df_principal = df_novo
                st.session_state.nome_arquivo = uploaded_file.name
                st.session_state.qa_checks = {}
                st.session_state.df_erros_cache = None
                st.session_state.historico_alteracoes = []
            st.success(f"✅ `{uploaded_file.name}` carregado com sucesso!")
            st.rerun()

    if st.session_state.df_principal is not None:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Nova Planilha", use_container_width=True, type="secondary"):
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
    
    # Informações úteis
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
# CORPO PRINCIPAL
# ============================================================
if st.session_state.df_principal is None:
    # Página de boas-vindas
    st.markdown("""
        <div class="app-header" style="text-align: center;">
            <h1>🚀 Bem-vindo ao Importador Pro v4</h1>
            <p>Sistema inteligente de importação e validação de dados</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="card">
                <h3>🎯 Precisão</h3>
                <p>Validação inteligente de EAN, SKU e campos obrigatórios</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="card">
                <h3>⚡ Performance</h3>
                <p>Processamento otimizado para grandes volumes de dados</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="card">
                <h3>🔒 Confiabilidade</h3>
                <p>QA Gate com revisão por lotes e log de auditoria</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("👈 Faça o upload da planilha no menu lateral para começar.")
    st.stop()

# Header da aplicação
st.markdown(f"""
    <div class="app-header">
        <h1>📊 {st.session_state.nome_arquivo}</h1>
        <p>Sessão: {st.session_state.session_id} | Atualizado: {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
""", unsafe_allow_html=True)

# Abas principais
tab_busca, tab_editor, tab_procv, tab_erros, tab_export = st.tabs([
    "🔍 Dashboard & Busca",
    "📝 Editor Avançado",
    "🔗 PROCV / De-Para",
    "🚨 Validação & Erros",
    "✅ QA Exportação"
])


# ============================================================
# ABA 1 — DASHBOARD & BUSCA
# ============================================================
with tab_busca:
    df = st.session_state.df_principal
    
    # Métricas principais
    st.subheader("📈 Visão Geral")
    cols_metric = st.columns(4)
    
    # SKU preenchidos
    col_sku_real = resolver_coluna(df, COLUNA_SKU)
    skus_vazios = contar_vazios(df, col_sku_real) if col_sku_real in df.columns else len(df)
    skus_preenchidos = len(df) - skus_vazios
    taxa_sku = (skus_preenchidos / len(df) * 100) if len(df) > 0 else 0
    
    with cols_metric[0]:
        st.markdown(f"""
            <div class="card metric-card">
                <div class="metric-value">{len(df):,}</div>
                <div class="metric-label">Total Registros</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols_metric[1]:
        st.markdown(f"""
            <div class="card metric-card">
                <div class="metric-value">{len(df.columns)}</div>
                <div class="metric-label">Colunas</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols_metric[2]:
        color = "var(--success)" if taxa_sku > 90 else "var(--warning)"
        st.markdown(f"""
            <div class="card metric-card">
                <div class="metric-value" style="color: {color}">{taxa_sku:.1f}%</div>
                <div class="metric-label">Taxa SKU</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols_metric[3]:
        # Conta erros se cache existir
        if st.session_state.df_erros_cache is not None:
            n_erros = len(st.session_state.df_erros_cache)
        else:
            n_erros = "..."
        st.markdown(f"""
            <div class="card metric-card">
                <div class="metric-value">{n_erros}</div>
                <div class="metric-label">Erros Detectados</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Busca avançada
    st.subheader("🔎 Pesquisa Inteligente")
    col_search, col_filter = st.columns([3, 1])
    
    with col_search:
        termo = st.text_input(
            "Buscar por SKU, Marca, EAN, ID...",
            placeholder="Digite para filtrar resultados...",
            label_visibility="collapsed"
        )
    
    with col_filter:
        modo_busca = st.selectbox(
            "Modo",
            ["Contém", "Exato", "Regex"],
            label_visibility="collapsed"
        )
    
    if termo:
        if modo_busca == "Contém":
            mask = df.astype(str).apply(
                lambda x: x.str.contains(termo, case=False, na=False)
            ).any(axis=1)
        elif modo_busca == "Exato":
            mask = df.astype(str).apply(
                lambda x: x.str.strip().str.lower() == termo.strip().lower()
            ).any(axis=1)
        else:  # Regex
            try:
                mask = df.astype(str).apply(
                    lambda x: x.str.contains(termo, case=False, na=False, regex=True)
                ).any(axis=1)
            except:
                st.error("Expressão regular inválida!")
                mask = pd.Series([True] * len(df))
        
        resultados = df[mask]
        st.caption(f"✨ {len(resultados):,} resultado(s) para: `{termo}`")
        st.dataframe(
            resultados,
            use_container_width=True,
            height=500,
            column_config={
                "EAN": st.column_config.TextColumn("EAN", width="medium"),
                "SKU": st.column_config.TextColumn("SKU", width="medium"),
            }
        )
    else:
        # Preview com gráfico de completude
        col_preview, col_chart = st.columns([3, 1])
        
        with col_preview:
            st.dataframe(
                df.head(50),
                use_container_width=True,
                height=500
            )
            if len(df) > 50:
                st.caption(f"📄 Exibindo primeiras 50 de {len(df):,} linhas")
        
        with col_chart:
            st.markdown("**Completude das Colunas**")
            completude = {}
            for col in df.columns:
                completude[col] = (len(df) - contar_vazios(df, col)) / len(df) * 100
            
            df_completude = pd.DataFrame({
                "Coluna": completude.keys(),
                "% Preenchido": completude.values()
            }).sort_values("% Preenchido", ascending=True)
            
            fig = px.bar(
                df_completude,
                x="% Preenchido",
                y="Coluna",
                orientation='h',
                color="% Preenchido",
                color_continuous_scale="RdYlGn",
                range_color=[0, 100]
            )
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ABA 2 — EDITOR AVANÇADO
# ============================================================
with tab_editor:
    st.header("📝 Editor de Planilha Avançado")
    
    col_info, col_stats = st.columns([2, 1])
    with col_info:
        st.caption(
            f"✏️ Colunas editáveis: **{', '.join(COLUNAS_EDITAVEIS)}** | "
            f"Demais colunas são somente leitura"
        )
    with col_stats:
        if st.session_state.historico_alteracoes:
            st.info(f"🕒 {len(st.session_state.historico_alteracoes)} alterações nesta sessão")
    
    # Data editor com configurações avançadas
    colunas_bloqueadas = [
        c for c in st.session_state.df_principal.columns
        if c not in COLUNAS_EDITAVEIS
    ]
    
    # Configuração de colunas dinâmica
    column_config = {}
    for col in st.session_state.df_principal.columns:
        if col == "EAN":
            column_config[col] = st.column_config.TextColumn(
                "EAN 📊",
                help="Código EAN (8, 12 ou 13 dígitos)",
                validate="^[0-9]*$"
            )
        elif col == "Kit quantidade":
            column_config[col] = st.column_config.NumberColumn(
                "Kit Qtd 📦",
                min_value=0,
                step=1,
                format="%d"
            )
        elif col in COLUNAS_EDITAVEIS:
            column_config[col] = st.column_config.TextColumn(col)
    
    df_editado = st.data_editor(
        st.session_state.df_principal,
        use_container_width=True,
        num_rows="dynamic",
        disabled=colunas_bloqueadas,
        key="editor_principal",
        height=600,
        column_config=column_config,
        hide_index=None,
    )
    
    # Controles de edição
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
            if not df_editado.equals(st.session_state.df_principal):
                st.session_state.historico_alteracoes.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": "admin"
                })
                st.session_state.df_principal = df_editado
                st.session_state.df_erros_cache = None
                st.toast("✅ Alterações salvas com sucesso!", icon="✅")
                st.rerun()
    
    with col2:
        if st.button("↩️ Desfazer Última", use_container_width=True):
            if st.session_state.historico_alteracoes:
                st.session_state.historico_alteracoes.pop()
                st.info("Funcionalidade em desenvolvimento")
    
    with col3:
        st.download_button(
            "⬇️ Exportar Editado",
            data=df_editado.to_csv(index=False).encode('utf-8'),
            file_name=f"editado_{st.session_state.session_id}.csv",
            mime="text/csv",
            use_container_width=True
        )


# ============================================================
# ABA 3 — PROCV / DE-PARA
# ============================================================
with tab_procv:
    st.header("🔗 PROCV Inteligente — De/Para Automático")
    st.markdown(
        "Combine dados de planilhas externas usando **ID do canal de venda** como chave. "
        "O sistema preenche automaticamente os SKUs correspondentes."
    )
    
    # Upload da planilha externa
    ext_file = st.file_uploader(
        "📤 Planilha do Cliente (fonte dos SKUs)",
        type=["xlsx", "csv"],
        key="ext_upload",
        help="Esta planilha deve conter ID do anúncio e SKU correspondente"
    )

    if ext_file:
        df_ext = ler_arquivo(ext_file)
        
        # Métricas da planilha externa
        col1, col2, col3 = st.columns(3)
        col1.metric("Registros", f"{len(df_ext):,}")
        col2.metric("Colunas", len(df_ext.columns))
        col3.metric("Tamanho", f"{ext_file.size / 1024:.1f} KB")
        
        with st.expander("👁️ Preview da Planilha Fonte"):
            st.dataframe(df_ext.head(10), use_container_width=True)
        
        st.divider()
        
        # Configuração do De-Para com assistente
        st.subheader("⚙️ Configurar Mapeamento")
        
        with st.expander("🧙 Assistente de Configuração", expanded=True):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**🔵 Planilha do Sistema (Destino)**")
                col_id_sistema = st.selectbox(
                    "Coluna de ID",
                    st.session_state.df_principal.columns,
                    help="Chave de ligação (ex: ID do canal de venda)",
                    key="id_sistema"
                )
                col_sku_sistema = st.selectbox(
                    "Coluna SKU (destino)",
                    st.session_state.df_principal.columns,
                    help="Onde os SKUs serão salvos",
                    key="sku_sistema"
                )
            
            with col_b:
                st.markdown("**🟢 Planilha do Cliente (Origem)**")
                col_id_cliente = st.selectbox(
                    "Coluna de ID",
                    df_ext.columns,
                    help="Chave correspondente à do sistema",
                    key="id_cliente"
                )
                col_sku_cliente = st.selectbox(
                    "Coluna SKU (origem)",
                    df_ext.columns,
                    help="SKUs que serão copiados",
                    key="sku_cliente"
                )
        
        # Preview do mapeamento
        st.info(
            f"🔗 **Lógica:** `Sistema.{col_id_sistema}` ↔ `Cliente.{col_id_cliente}` → "
            f"`Cliente.{col_sku_cliente}` → `Sistema.{col_sku_sistema}`"
        )
        
        # Opções avançadas
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            sobrescrever = st.checkbox(
                "🔄 Sobrescrever SKUs já preenchidos",
                value=False,
                help="Se ativado, substitui SKUs existentes"
            )
        with col_opt2:
            ignorar_na = st.checkbox(
                "🚫 Ignorar IDs não encontrados",
                value=True,
                help="Não modifica linhas sem correspondência"
            )
        
        # Execução
        if st.button("🚀 Executar PROCV", type="primary", use_container_width=True):
            with st.spinner("Processando merge..."):
                try:
                    df_resultado, stats = executar_merge_procv(
                        df_sistema=st.session_state.df_principal.copy(),
                        df_cliente=df_ext,
                        col_id_sistema=col_id_sistema,
                        col_id_cliente=col_id_cliente,
                        col_sku_cliente=col_sku_cliente,
                        col_sku_sistema=col_sku_sistema,
                        sobrescrever=sobrescrever
                    )
                    
                    # Atualiza estado
                    st.session_state.df_principal = df_resultado
                    st.session_state.df_erros_cache = None
                    
                    # Exibe resultados com gráficos
                    st.success("✅ PROCV executado com sucesso!")
                    
                    col_r1, col_r2, col_r3 = st.columns(3)
                    col_r1.metric("✅ SKUs Preenchidos", f"{stats['preenchidos']:,}")
                    col_r2.metric("⚠️ Não Encontrados", f"{stats['nao_encontrados']:,}")
                    col_r3.metric("📊 Taxa de Sucesso", stats['taxa_sucesso'])
                    
                    # Gráfico de resultados
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Preenchidos', 'Não Encontrados'],
                            values=[stats['preenchidos'], stats['nao_encontrados']],
                            hole=.4,
                            marker_colors=['#059669', '#d97706']
                        )
                    ])
                    fig.update_layout(
                        title="Resultado do PROCV",
                        height=300,
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabela de não encontrados
                    if stats['nao_encontrados'] > 0:
                        with st.expander(f"📋 {stats['nao_encontrados']} IDs não encontrados"):
                            sem_match = df_resultado[
                                df_resultado[col_sku_sistema].isna() |
                                (df_resultado[col_sku_sistema].astype(str).str.strip() == "")
                            ][[col_id_sistema]]
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
    
    # Botão de validação
    col_btn, col_auto = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 Executar Validação", type="primary", use_container_width=True):
            with st.spinner("Validando dados..."):
                st.session_state.df_erros_cache = validar_dataframe(st.session_state.df_principal)
            st.rerun()
    with col_auto:
        st.caption("💡 A validação é executada automaticamente ao carregar/editar")
    
    # Executa validação se não houver cache
    if st.session_state.df_erros_cache is None:
        with st.spinner("Executando validação inicial..."):
            st.session_state.df_erros_cache = validar_dataframe(st.session_state.df_principal)
    
    df_erros = st.session_state.df_erros_cache
    
    # Dashboard de erros
    st.subheader("📊 Dashboard de Qualidade")
    
    if df_erros.empty:
        st.success("""
            <div style="text-align: center; padding: 2rem;">
                <h2>🎉 Dados 100% Consistentes!</h2>
                <p>Nenhum erro ou inconsistência encontrada.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Contagem por severidade
        criticos = len(df_erros[df_erros["Severidade"] == "🚨 Crítico"])
        alertas = len(df_erros[df_erros["Severidade"] == "⚠️ Alerta"])
        infos = len(df_erros[df_erros["Severidade"] == "ℹ️ Informativo"])
        
        # Métricas de erro
        col_c, col_a, col_i = st.columns(3)
        with col_c:
            st.error(f"🚨 **{criticos} Críticos**")
        with col_a:
            st.warning(f"⚠️ **{alertas} Alertas**")
        with col_i:
            st.info(f"ℹ️ **{infos} Informativos**")
        
        # Gráfico de distribuição
        fig = go.Figure(data=[
            go.Bar(
                x=['Críticos', 'Alertas', 'Informativos'],
                y=[criticos, alertas, infos],
                marker_color=['#dc2626', '#d97706', '#2563eb'],
                text=[criticos, alertas, infos],
                textposition='auto',
            )
        ])
        fig.update_layout(
            title="Distribuição de Erros",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Filtros avançados
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            filtro_sev = st.multiselect(
                "🔍 Filtrar por Severidade",
                ["🚨 Crítico", "⚠️ Alerta", "ℹ️ Informativo"],
                default=["🚨 Crítico", "⚠️ Alerta"]
            )
        with col_filtro2:
            colunas_erro = df_erros["Campo"].unique()
            filtro_campo = st.multiselect(
                "📋 Filtrar por Campo",
                colunas_erro,
                default=list(colunas_erro)
            )
        
        # Aplica filtros
        df_exibir = df_erros[
            df_erros["Severidade"].isin(filtro_sev) &
            df_erros["Campo"].isin(filtro_campo)
        ]
        
        # Tabela de erros estilizada
        st.dataframe(
            df_exibir,
            use_container_width=True,
            height=400,
            column_config={
                "Nº Linha": st.column_config.NumberColumn("Nº Linha", format="%d"),
                "Severidade": st.column_config.TextColumn("Severidade", width="small"),
                "Descrição": st.column_config.TextColumn("Descrição", width="large"),
            },
            hide_index=True
        )
        
        st.caption(f"📄 {len(df_exibir)} erros exibidos | Corrija na aba **Editor de Planilha**")
        
        # Exportação do relatório
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "⬇️ Relatório CSV",
                data=df_erros.to_csv(index=False, sep=';').encode('utf-8'),
                file_name=f"erros_{st.session_state.session_id}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_dl2:
            st.download_button(
                "📊 Relatório Excel",
                data=io.BytesIO(),
                file_name=f"erros_{st.session_state.session_id}.xlsx",
                disabled=True,  # Implementar se necessário
                use_container_width=True
            )


# ============================================================
# ABA 5 — QA EXPORTAÇÃO
# ============================================================
with tab_export:
    st.header("✅ QA Gate — Revisão por Lotes")
    
    df_final = st.session_state.df_principal
    
    if len(df_final) == 0:
        st.warning("📭 A planilha está vazia. Nada para revisar.")
        st.stop()
    
    total_lotes = math.ceil(len(df_final) / TAMANHO_LOTE)
    revisados = len(st.session_state.qa_checks)
    lotes_ok = sum(1 for v in st.session_state.qa_checks.values() if v == "OK")
    lotes_corrigir = sum(1 for v in st.session_state.qa_checks.values() if v == "CORRIGIR")
    progresso = revisados / total_lotes if total_lotes > 0 else 0
    
    # Métricas de QA
    st.subheader("📈 Progresso QA")
    cols_qa = st.columns(4)
    
    with cols_qa[0]:
        st.markdown(f"""
            <div class="card metric-card">
                <div class="metric-value">{progresso:.0%}</div>
                <div class="metric-label">Progresso</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols_qa[1]:
        st.markdown(f"""
            <div class="card metric-card">
                <div class="metric-value" style="color: var(--success)">{lotes_ok}</div>
                <div class="metric-label">Lotes Aprovados</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols_qa[2]:
        st.markdown(f"""
            <div class="card metric-card">
                <div class="metric-value" style="color: var(--danger)">{lotes_corrigir}</div>
                <div class="metric-label">Lotes p/ Correção</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols_qa[3]:
        st.markdown(f"""
            <div class="card metric-card">
                <div class="metric-value">{total_lotes - revisados}</div>
                <div class="metric-label">Pendentes</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Barra de progresso
    st.progress(progresso, text=f"✅ {revisados}/{total_lotes} lotes revisados")
    
    st.divider()
    
    # Seleção de lote
    st.subheader("🔍 Revisar Lote")
    lote_atual = st.selectbox(
        "Selecionar lote para revisão:",
        range(1, total_lotes + 1),
        format_func=lambda x: f"Lote {x} ({'✅ OK' if st.session_state.qa_checks.get(x) == 'OK' else '⚠️ CORRIGIR' if st.session_state.qa_checks.get(x) == 'CORRIGIR' else '⬜ Pendente'})"
    )
    
    inicio = (lote_atual - 1) * TAMANHO_LOTE
    fim = min(inicio + TAMANHO_LOTE, len(df_final))
    preview_lote = df_final.iloc[inicio:fim]
    
    # Colunas para preview
    colunas_preview = []
    for col in [COLUNA_ID_ANUNCIO] + COLUNAS_EDITAVEIS:
        col_real = resolver_coluna(df_final, col)
        if col_real in df_final.columns and col_real not in colunas_preview:
            colunas_preview.append(col_real)
    
    # Status do lote
    status_atual = st.session_state.qa_checks.get(lote_atual, "⬜ Pendente")
    st.caption(
        f"📋 Lote **{lote_atual}/{total_lotes}** | "
        f"Linhas {inicio + 1}–{fim} | "
        f"Status: `{status_atual}`"
    )
    
    # Preview dos dados
    st.dataframe(
        preview_lote[colunas_preview],
        use_container_width=True,
        height=400
    )
    
    # Controles de revisão
    col_ok, col_cor, col_limpar = st.columns([1, 1, 0.5])
    
    with col_ok:
        if st.button(f"✅ Aprovar Lote {lote_atual}", use_container_width=True, type="primary"):
            st.session_state.qa_checks[lote_atual] = "OK"
            st.toast(f"✅ Lote {lote_atual} aprovado!", icon="✅")
            st.rerun()
    
    with col_cor:
        if st.button(f"⚠️ Corrigir Lote {lote_atual}", use_container_width=True):
            st.session_state.qa_checks[lote_atual] = "CORRIGIR"
            st.toast(f"⚠️ Lote {lote_atual} marcado para correção", icon="⚠️")
            st.rerun()
    
    with col_limpar:
        if st.button("↩️", use_container_width=True, help="Limpar status"):
            st.session_state.qa_checks.pop(lote_atual, None)
            st.rerun()
    
    # Mapa visual de lotes
    st.divider()
    st.subheader("🗺️ Mapa de Lotes")
    
    n_cols = min(total_lotes, 12)
    cols_mapa = st.columns(n_cols)
    
    for i in range(total_lotes):
        lote_n = i + 1
        status = st.session_state.qa_checks.get(lote_n, "")
        
        with cols_mapa[i % n_cols]:
            if status == "OK":
                emoji = "✅"
                cor = "var(--success)"
            elif status == "CORRIGIR":
                emoji = "⚠️"
                cor = "var(--danger)"
            else:
                emoji = "⬜"
                cor = "var(--gray-600)"
            
            st.markdown(f"""
                <div style="text-align:center; padding:0.5rem;">
                    <div style="font-size:1.5rem;">{emoji}</div>
                    <small style="color:{cor}">L{lote_n}</small>
                </div>
            """, unsafe_allow_html=True)
    
    # Exportação final
    st.divider()
    
    if revisados < total_lotes:
        st.warning(
            f"⏳ **Revisão incompleta**: {total_lotes - revisados} lotes pendentes. "
            "Revise todos os lotes para liberar a exportação final."
        )
    else:
        st.success("🎉 **Todos os lotes revisados!** Exportação final liberada.")
        st.balloons()
        
        # Prepara dados para exportação
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_final = calcular_hash(df_final)
        
        # Log de auditoria estruturado
        log_auditoria = {
            "sistema": "Importador Pro v4",
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
        
        # Exportações
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Planilha final
            csv_data = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Download Planilha Final",
                data=csv_data,
                file_name=f"importacao_final_{ts}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
            
            # Também em Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False, sheet_name='Dados')
            st.download_button(
                "📊 Download Excel",
                data=output.getvalue(),
                file_name=f"importacao_final_{ts}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_exp2:
            # Log de auditoria
            log_json = json.dumps(log_auditoria, indent=2, ensure_ascii=False)
            st.download_button(
                "📋 Log Auditoria (JSON)",
                data=log_json,
                file_name=f"qa_log_{ts}.json",
                mime="application/json",
                use_container_width=True
            )
            
            # Log em texto
            log_txt = "\n".join([
                "=" * 50,
                "  LOG DE AUDITORIA QA — IMPORTADOR PRO v4",
                "=" * 50,
                f"Sessão: {log_auditoria['sessao']}",
                f"Arquivo: {log_auditoria['arquivo']}",
                f"Data/Hora: {log_auditoria['data_hora']}",
                f"Total Linhas: {log_auditoria['total_linhas']}",
                f"Total Lotes: {log_auditoria['total_lotes']}",
                f"Hash: {log_auditoria['hash_sha256']}",
                "",
                "Resultado por Lote:",
            ] + [
                f"  Lote {k.replace('lote_', '').zfill(3)}: {v}"
                for k, v in log_auditoria['resultado_lotes'].items()
            ])
            
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
    f"<div style='text-align: center; color: var(--gray-600); font-size: 0.8rem;'>"
    f"🚀 Importador Pro v4 Enterprise | Sessão: {st.session_state.session_id} | "
    f"© {datetime.now().year} | Todos os direitos reservados"
    f"</div>",
    unsafe_allow_html=True
)
