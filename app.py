import streamlit as st
import pandas as pd
import io
import uuid
import hashlib
from datetime import datetime
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Importador Pro v3", layout="wide", page_icon="🚀")

# --- CSS PROFISSIONAL ---
st.markdown("""
    <style>
    /* Tema geral */
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 2px solid #e0e4eb; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f5f7fa;
        border-radius: 6px 6px 0 0;
        padding: 8px 18px;
        font-weight: 500;
        color: #555;
        border: 1px solid #e0e4eb;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a56db !important;
        color: white !important;
        border-color: #1a56db !important;
    }

    /* Badges de severidade */
    .badge-alta { background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:10px; font-size:0.78rem; font-weight:600; }
    .badge-media { background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:10px; font-size:0.78rem; font-weight:600; }
    .badge-baixa { background:#dcfce7; color:#166534; padding:2px 8px; border-radius:10px; font-size:0.78rem; font-weight:600; }

    /* Métricas customizadas */
    .metric-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-box .valor { font-size: 1.8rem; font-weight: 700; color: #1a56db; }
    .metric-box .label { font-size: 0.8rem; color: #64748b; margin-top: 2px; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #f0f4ff; }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
# Coluna obrigatória que será preenchida via PROCV
COLUNA_SKU = "SKU"
# Coluna chave da planilha do sistema para o De-Para
COLUNA_ID_ANUNCIO = "ID do canal de venda"
# Todas as colunas editáveis (apenas SKU é obrigatória)
COLUNAS_EDITAVEIS = ["Marca", "EAN", "SKU", "Kit quantidade", "Código Depósito"]
COLUNAS_OBRIGATORIAS = ["SKU"]
TAMANHO_LOTE = 10

# --- FUNÇÕES UTILITÁRIAS ---

def calcular_hash(df: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()


def normalizar_ean(valor) -> str:
    """Converte float (ex: 1234.0) para string inteira antes de validar."""
    if pd.isna(valor):
        return ""
    try:
        return str(int(float(str(valor).strip())))
    except (ValueError, OverflowError):
        return str(valor).strip()


def validar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna DataFrame de erros encontrados."""
    erros = []
    for idx, row in df.iterrows():
        # Apenas SKU é obrigatório
        vazios = [
            col for col in COLUNAS_OBRIGATORIAS
            if col in df.columns and (pd.isna(row[col]) or str(row[col]).strip() == "")
        ]
        if vazios:
            erros.append({
                "Linha": idx + 1,
                "Campo": ", ".join(vazios),
                "Descrição": "SKU não preenchido — execute o PROCV para preencher",
                "Severidade": "Alta",
            })

        # EAN — validação opcional (só se preenchido)
        if "EAN" in df.columns:
            ean_str = normalizar_ean(row["EAN"])
            if ean_str and not ean_str.isdigit():
                erros.append({
                    "Linha": idx + 1,
                    "Campo": "EAN",
                    "Descrição": f"EAN inválido: '{row['EAN']}' (deve conter apenas números)",
                    "Severidade": "Média",
                })
            if ean_str and ean_str.isdigit() and len(ean_str) not in (8, 12, 13):
                erros.append({
                    "Linha": idx + 1,
                    "Campo": "EAN",
                    "Descrição": f"EAN com {len(ean_str)} dígito(s) — esperado 8, 12 ou 13",
                    "Severidade": "Baixa",
                })

    return pd.DataFrame(erros) if erros else pd.DataFrame(
        columns=["Linha", "Campo", "Descrição", "Severidade"]
    )


def garantir_colunas(df: pd.DataFrame) -> pd.DataFrame:
    for col in COLUNAS_EDITAVEIS:
        if col not in df.columns:
            df[col] = ""
    return df


def ler_arquivo(file) -> pd.DataFrame:
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)


# --- INICIALIZAÇÃO DE ESTADO ---
defaults = {
    "df_principal": None,
    "qa_checks": {},
    "session_id": str(uuid.uuid4())[:8].upper(),
    "nome_arquivo": "",
    "df_erros_cache": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(f"### 🚀 Importador Pro v3")
    st.caption(f"Sessão: `{st.session_state.session_id}`")
    st.divider()

    st.subheader("📁 Planilha do Sistema")
    uploaded_file = st.file_uploader(
        "Carregar / Substituir planilha",
        type=["xlsx", "csv"],
        help="Faça upload novamente para substituir a planilha atual.",
    )

    if uploaded_file:
        # Permite recarregar nova planilha a qualquer momento
        if (
            st.session_state.df_principal is None
            or uploaded_file.name != st.session_state.nome_arquivo
        ):
            df_novo = ler_arquivo(uploaded_file)
            df_novo = garantir_colunas(df_novo)
            st.session_state.df_principal = df_novo
            st.session_state.nome_arquivo = uploaded_file.name
            st.session_state.qa_checks = {}          # reset QA ao trocar arquivo
            st.session_state.df_erros_cache = None
            st.success(f"✅ `{uploaded_file.name}` carregado!")

    if st.session_state.df_principal is not None:
        st.divider()
        df_info = st.session_state.df_principal
        st.markdown(f"**Arquivo:** `{st.session_state.nome_arquivo}`")
        st.markdown(f"**Linhas:** {len(df_info):,}  |  **Colunas:** {len(df_info.columns)}")

        if st.button("🗑️ Limpar e carregar novo arquivo", use_container_width=True):
            st.session_state.df_principal = None
            st.session_state.nome_arquivo = ""
            st.session_state.qa_checks = {}
            st.session_state.df_erros_cache = None
            st.rerun()

    st.divider()
    st.info("💡 Use a aba **PROCV** para mesclar dados de planilhas externas.")


# ============================================================
# CORPO PRINCIPAL
# ============================================================
if st.session_state.df_principal is None:
    st.markdown("## 👋 Bem-vindo ao Importador Pro v3")
    st.info("Faça o upload da planilha do sistema no menu lateral para começar.")
    st.stop()

# Abas
tab_busca, tab_editor, tab_procv, tab_erros, tab_export = st.tabs([
    "🔍 Busca & Preview",
    "📝 Editor de Planilha",
    "🔗 PROCV / De-Para",
    "🚨 Validação & Erros",
    "✅ Exportação (QA)",
])


# ============================================================
# ABA 1 — BUSCA & PREVIEW
# ============================================================
with tab_busca:
    st.header("Pesquisa Rápida")
    df = st.session_state.df_principal

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-box"><div class="valor">{len(df):,}</div><div class="label">Total de Linhas</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="valor">{len(df.columns)}</div><div class="label">Colunas</div></div>', unsafe_allow_html=True)
    vazios_total = 0
    for col in COLUNAS_OBRIGATORIAS:
        if col in df.columns:
            vazios_total += df[col].isna().sum() + (df[col].astype(str).str.strip() == "").sum()
    pct_completo = 100 - (vazios_total / max(len(df), 1) * 100)
    c3.markdown(f'<div class="metric-box"><div class="valor">{int(vazios_total)}</div><div class="label">SKUs Vazios</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-box"><div class="valor">{pct_completo:.0f}%</div><div class="label">SKUs Preenchidos</div></div>', unsafe_allow_html=True)

    st.markdown("")
    termo = st.text_input("🔎 Filtrar por qualquer campo (SKU, Nome, Marca, EAN...):", placeholder="Digite para buscar...")

    if termo:
        mask = df.astype(str).apply(lambda x: x.str.contains(termo, case=False, na=False)).any(axis=1)
        resultados = df[mask]
        st.caption(f"{len(resultados)} resultado(s) encontrado(s) para `{termo}`")
        st.dataframe(resultados, use_container_width=True, height=400)
    else:
        st.dataframe(df.head(50), use_container_width=True, height=400)
        if len(df) > 50:
            st.caption(f"Exibindo 50 de {len(df)} linhas. Use o filtro acima para buscar.")


# ============================================================
# ABA 2 — EDITOR DE PLANILHA
# ============================================================
with tab_editor:
    st.header("Editor de Planilha")
    st.caption(
        f"Colunas editáveis: **{', '.join(COLUNAS_EDITAVEIS)}**. "
        "As demais são somente leitura."
    )

    colunas_bloqueadas = [
        c for c in st.session_state.df_principal.columns
        if c not in COLUNAS_EDITAVEIS
    ]

    df_editado = st.data_editor(
        st.session_state.df_principal,
        use_container_width=True,
        num_rows="dynamic",
        disabled=colunas_bloqueadas,
        key="editor_principal",
        height=500,
        column_config={
            "EAN": st.column_config.TextColumn("EAN", help="Apenas números (8, 12 ou 13 dígitos)"),
            "Kit quantidade": st.column_config.NumberColumn("Kit quantidade", min_value=0, step=1),
        },
    )

    # Só salva se houver mudança real para evitar re-renders desnecessários
    if not df_editado.equals(st.session_state.df_principal):
        st.session_state.df_principal = df_editado
        st.session_state.df_erros_cache = None  # invalida cache de erros
        st.toast("✅ Alterações salvas!", icon="✅")


# ============================================================
# ABA 3 — PROCV / DE-PARA
# ============================================================
with tab_procv:
    st.header("PROCV — Preencher SKU pelo ID do Anúncio")
    st.markdown(
        "Faça upload da planilha do cliente que contém o **ID do anúncio** e o **SKU** correspondente. "
        "O sistema irá cruzar pelo `ID do canal de venda` e preencher a coluna `SKU` automaticamente."
    )

    ext_file = st.file_uploader("Planilha do cliente (.xlsx ou .csv)", type=["xlsx", "csv"], key="ext_upload")

    if ext_file:
        df_ext = ler_arquivo(ext_file)
        st.caption(f"Planilha carregada: **{ext_file.name}** — {len(df_ext):,} linhas, {len(df_ext.columns)} colunas")

        with st.expander("👁️ Visualizar primeiras linhas da planilha do cliente"):
            st.dataframe(df_ext.head(8), use_container_width=True)

        st.divider()
        st.subheader("Configurar De-Para")

        col_a, col_b = st.columns(2)

        # Coluna chave do sistema — tenta pré-selecionar automaticamente
        opcoes_sistema = list(st.session_state.df_principal.columns)
        idx_default_sistema = (
            opcoes_sistema.index(COLUNA_ID_ANUNCIO)
            if COLUNA_ID_ANUNCIO in opcoes_sistema else 0
        )
        col_id_sistema = col_a.selectbox(
            "🔑 Coluna de ID na planilha do **Sistema**",
            opcoes_sistema,
            index=idx_default_sistema,
            help="Geralmente: 'ID do canal de venda'",
        )

        # Coluna chave do cliente
        col_id_cliente = col_b.selectbox(
            "🔑 Coluna de ID na planilha do **Cliente**",
            df_ext.columns,
            help="Coluna que contém o mesmo ID do anúncio",
        )

        col_c, col_d = st.columns(2)
        col_sku_cliente = col_c.selectbox(
            "📦 Coluna de SKU na planilha do **Cliente**",
            df_ext.columns,
            help="Coluna cujo valor será copiado para o SKU do sistema",
        )
        col_sku_sistema = col_d.selectbox(
            "📦 Coluna de SKU no **Sistema** (destino)",
            opcoes_sistema,
            index=opcoes_sistema.index(COLUNA_SKU) if COLUNA_SKU in opcoes_sistema else 0,
        )

        # Preview do mapeamento
        st.markdown("")
        st.info(
            f"**Lógica:** Para cada linha do sistema, busca `{col_id_sistema}` "
            f"na coluna `{col_id_cliente}` do cliente → copia `{col_sku_cliente}` para `{col_sku_sistema}`"
        )

        sobrescrever = st.checkbox(
            "Sobrescrever SKUs já preenchidos",
            value=False,
            help="Se desmarcado, apenas linhas com SKU vazio serão preenchidas.",
        )

        if st.button("▶️ Executar De-Para", type="primary"):
            df_base = st.session_state.df_principal.copy()

            # Normaliza tipo da coluna chave para evitar mismatch int/str
            df_base[col_id_sistema] = df_base[col_id_sistema].astype(str).str.strip()
            df_ext[col_id_cliente] = df_ext[col_id_cliente].astype(str).str.strip()

            # Cria dicionário de lookup: ID → SKU
            lookup = df_ext.dropna(subset=[col_id_cliente, col_sku_cliente])
            lookup = lookup.drop_duplicates(subset=[col_id_cliente])
            mapa_sku = dict(zip(lookup[col_id_cliente], lookup[col_sku_cliente]))

            # Garante que coluna destino existe
            if col_sku_sistema not in df_base.columns:
                df_base[col_sku_sistema] = ""

            # Aplica o lookup
            def preencher_sku(row):
                sku_atual = str(row[col_sku_sistema]).strip() if not pd.isna(row[col_sku_sistema]) else ""
                if sku_atual and not sobrescrever:
                    return row[col_sku_sistema]  # mantém existente
                return mapa_sku.get(str(row[col_id_sistema]).strip(), row[col_sku_sistema])

            df_base[col_sku_sistema] = df_base.apply(preencher_sku, axis=1)

            # Métricas do resultado
            total = len(df_base)
            preenchidos = df_base[col_sku_sistema].notna().sum()
            preenchidos -= (df_base[col_sku_sistema].astype(str).str.strip() == "").sum()
            nao_encontrados = total - preenchidos

            st.session_state.df_principal = df_base
            st.session_state.df_erros_cache = None

            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.success(f"✅ **{int(preenchidos):,}** SKUs preenchidos")
            col_r2.warning(f"⚠️ **{int(nao_encontrados):,}** IDs sem correspondência")
            col_r3.info(f"📋 **{total:,}** linhas no total")

            if nao_encontrados > 0:
                sem_match = df_base[
                    df_base[col_sku_sistema].isna() |
                    (df_base[col_sku_sistema].astype(str).str.strip() == "")
                ][[col_id_sistema]].copy()
                with st.expander(f"Ver {len(sem_match)} IDs sem correspondência"):
                    st.dataframe(sem_match, use_container_width=True)


# ============================================================
# ABA 4 — VALIDAÇÃO & ERROS
# ============================================================
with tab_erros:
    st.header("Relatório de Consistência")

    if st.button("🔄 Revalidar agora", type="primary"):
        st.session_state.df_erros_cache = None

    if st.session_state.df_erros_cache is None:
        st.session_state.df_erros_cache = validar_dataframe(st.session_state.df_principal)

    df_erros = st.session_state.df_erros_cache

    if df_erros.empty:
        st.success("🎉 Nenhum erro encontrado! Os dados estão consistentes.")
    else:
        n_alta = (df_erros["Severidade"] == "Alta").sum()
        n_media = (df_erros["Severidade"] == "Média").sum()
        n_baixa = (df_erros["Severidade"] == "Baixa").sum()

        ca, cm, cb = st.columns(3)
        ca.error(f"🔴 Alta: **{n_alta}** erro(s)")
        cm.warning(f"🟡 Média: **{n_media}** erro(s)")
        cb.info(f"🟢 Baixa: **{n_baixa}** aviso(s)")

        st.markdown("")

        # Filtro de severidade
        filtro_sev = st.multiselect(
            "Filtrar por severidade:",
            ["Alta", "Média", "Baixa"],
            default=["Alta", "Média", "Baixa"],
        )
        df_exibir = df_erros[df_erros["Severidade"].isin(filtro_sev)]

        st.dataframe(
            df_exibir,
            use_container_width=True,
            height=400,
            column_config={
                "Severidade": st.column_config.TextColumn("Severidade"),
                "Linha": st.column_config.NumberColumn("Linha", format="%d"),
            },
        )
        st.caption("💡 Anote o número da **Linha** e corrija na aba **Editor de Planilha**.")

        # Download do relatório de erros
        erros_csv = df_erros.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exportar relatório de erros (.csv)",
            data=erros_csv,
            file_name=f"erros_{st.session_state.session_id}.csv",
            mime="text/csv",
        )


# ============================================================
# ABA 5 — EXPORTAÇÃO (QA GATE)
# ============================================================
with tab_export:
    st.header("QA Gate — Revisão por Lotes")
    df_final = st.session_state.df_principal

    # Guarda de segurança: DataFrame vazio
    if len(df_final) == 0:
        st.warning("A planilha está vazia. Nada para revisar.")
        st.stop()

    total_lotes = math.ceil(len(df_final) / TAMANHO_LOTE)

    # Métricas de progresso
    revisados = len(st.session_state.qa_checks)
    lotes_ok = sum(1 for v in st.session_state.qa_checks.values() if v == "OK")
    lotes_corrigir = sum(1 for v in st.session_state.qa_checks.values() if v == "CORRIGIR")

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-box"><div class="valor">{len(df_final):,}</div><div class="label">Total de Produtos</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-box"><div class="valor">{total_lotes}</div><div class="label">Total de Lotes</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-box"><div class="valor" style="color:#16a34a">{lotes_ok}</div><div class="label">Lotes OK</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-box"><div class="valor" style="color:#dc2626">{lotes_corrigir}</div><div class="label">Lotes p/ Corrigir</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.progress(revisados / total_lotes, text=f"Revisão: {revisados}/{total_lotes} lotes concluídos")

    st.divider()

    lote_atual = st.number_input(
        "Selecionar lote para revisão",
        min_value=1,
        max_value=total_lotes,
        step=1,
        value=1,
    )

    inicio = (lote_atual - 1) * TAMANHO_LOTE
    fim = min(inicio + TAMANHO_LOTE, len(df_final))
    preview_lote = df_final.iloc[inicio:fim]

    # Exibe colunas relevantes: ID do anúncio + SKU + outras editáveis presentes
    colunas_preview = [COLUNA_ID_ANUNCIO] if COLUNA_ID_ANUNCIO in df_final.columns else []
    colunas_preview += [c for c in COLUNAS_EDITAVEIS if c in df_final.columns and c not in colunas_preview]
    colunas_exibicao = list(dict.fromkeys(colunas_preview))  # sem duplicatas

    status_atual = st.session_state.qa_checks.get(lote_atual, "—")
    st.caption(f"Lote **{lote_atual}/{total_lotes}** | Linhas {inicio + 1}–{fim} | Status atual: `{status_atual}`")

    st.dataframe(preview_lote[colunas_exibicao], use_container_width=True, height=300)

    col_ok, col_cor, col_limpar = st.columns([1, 1, 0.5])
    if col_ok.button(f"✅ Marcar Lote {lote_atual} como OK", use_container_width=True):
        st.session_state.qa_checks[lote_atual] = "OK"
        st.rerun()
    if col_cor.button(f"⚠️ Marcar Lote {lote_atual} para CORREÇÃO", use_container_width=True):
        st.session_state.qa_checks[lote_atual] = "CORRIGIR"
        st.rerun()
    if col_limpar.button("↩️ Limpar", use_container_width=True):
        st.session_state.qa_checks.pop(lote_atual, None)
        st.rerun()

    # Mapa visual de lotes
    st.divider()
    st.subheader("Mapa de Lotes")
    cols_mapa = st.columns(min(total_lotes, 10))
    for i, col in enumerate(cols_mapa):
        lote_n = i + 1
        s = st.session_state.qa_checks.get(lote_n, "")
        emoji = "✅" if s == "OK" else ("⚠️" if s == "CORRIGIR" else "⬜")
        col.markdown(f"<div style='text-align:center'>{emoji}<br><small>L{lote_n}</small></div>", unsafe_allow_html=True)

    # Exportação liberada somente após revisão total
    st.divider()
    if revisados < total_lotes:
        st.warning(f"⏳ Revise todos os {total_lotes} lotes para liberar a exportação. Faltam {total_lotes - revisados}.")
    else:
        st.success("🎉 Todos os lotes foram revisados! Exportação liberada.")

        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        hash_final = calcular_hash(df_final)

        csv_data = df_final.to_csv(index=False).encode("utf-8")

        log_lines = [
            "=" * 50,
            "  LOG DE AUDITORIA QA — IMPORTADOR PRO v3",
            "=" * 50,
            f"Sessão       : {st.session_state.session_id}",
            f"Arquivo      : {st.session_state.nome_arquivo}",
            f"Data/Hora    : {ts}",
            f"Total Linhas : {len(df_final)}",
            f"Total Lotes  : {total_lotes}",
            f"Hash SHA256  : {hash_final}",
            "",
            "Resultado por Lote:",
        ]
        for lote_n in range(1, total_lotes + 1):
            resultado = st.session_state.qa_checks.get(lote_n, "NÃO REVISADO")
            log_lines.append(f"  Lote {lote_n:03d}: {resultado}")
        log_lines += ["", "=" * 50]
        log_content = "\n".join(log_lines)

        dl1, dl2 = st.columns(2)
        dl1.download_button(
            "⬇️ Baixar Planilha Final (.csv)",
            data=csv_data,
            file_name=f"importacao_{st.session_state.session_id}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        dl2.download_button(
            "⬇️ Baixar Log de Auditoria (.txt)",
            data=log_content,
            file_name=f"qa_log_{st.session_state.session_id}.txt",
            mime="text/plain",
            use_container_width=True,
        )