import streamlit as st
import pandas as pd
import io
import uuid
import hashlib
from datetime import datetime
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Importador Pro v2", layout="wide", page_icon="🚀")

# --- CSS PARA INTERFACE PROFISSIONAL ---
st.markdown("""
    <style>
    .editable-col { background-color: #e8f4ea; border-radius: 5px; padding: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #007bff !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO ---
if 'df_principal' not in st.session_state:
    st.session_state.df_principal = None
if 'qa_checks' not in st.session_state:
    st.session_state.qa_checks = {}
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8].upper()

# Colunas Editáveis (S) conforme solicitado
COLUNAS_EDITAVEIS = ["Marca", "EAN", "SKU", "Kit quantidade", "Código Depósito"]

def calcular_hash(df):
    return hashlib.sha256(df.to_csv().encode()).hexdigest()

# --- SIDEBAR: UPLOAD DO SISTEMA ---
with st.sidebar:
    st.title(f"Sessão: {st.session_state.session_id}")
    st.subheader("📁 Carga Interna")
    uploaded_file = st.file_uploader("Planilha do Sistema", type=["xlsx", "csv"])
    
    if uploaded_file:
        if st.session_state.df_principal is None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Garante que as colunas obrigatórias existem
            for col in COLUNAS_EDITAVEIS:
                if col not in df.columns:
                    df[col] = ""
            st.session_state.df_principal = df
            st.success("Base carregada!")

    st.divider()
    st.info("💡 Dica: Use Ctrl+Shift+V para pular para o PROCV")

# --- CORPO PRINCIPAL (ABAS) ---
if st.session_state.df_principal is not None:
    tab_busca, tab_editor, tab_procv, tab_erros, tab_export = st.tabs([
        "🔍 Busca & Preview", 
        "📝 Editor de Planilha", 
        "🔗 PROCV / De-Para", 
        "🚨 Validação & Erros", 
        "✅ Exportação (QA)"
    ])

    # --- ABA 1: BUSCA & PREVIEW ---
    with tab_busca:
        st.header("Pesquisa Rápida")
        termo = st.text_input("Filtrar por qualquer campo (SKU, Nome, Marca...):")
        if termo:
            mask = st.session_state.df_principal.astype(str).apply(lambda x: x.str.contains(termo, case=False)).any(axis=1)
            resultados = st.session_state.df_principal[mask]
            st.dataframe(resultados, use_container_width=True)
        else:
            st.write("Digite algo para buscar.")

    # --- ABA 2: EDITOR DE PLANILHA ---
    with tab_editor:
        st.header("Edição Live")
        st.caption("Colunas em destaque são as editáveis (S)")
        
        # Formatação para destacar colunas editáveis
        df_editavel = st.data_editor(
            st.session_state.df_principal,
            use_container_width=True,
            num_rows="dynamic",
            disabled=[c for c in st.session_state.df_principal.columns if c not in COLUNAS_EDITAVEIS],
            key="main_editor"
        )
        st.session_state.df_principal = df_editavel

    # --- ABA 3: PROCV / DE-PARA ---
    with tab_procv:
        st.header("Merge com Base Externa")
        ext_file = st.file_uploader("Suba a planilha do cliente", type=["xlsx", "csv"], key="ext")
        
        if ext_file:
            df_ext = pd.read_csv(ext_file) if ext_file.name.endswith('.csv') else pd.read_excel(ext_file)
            col_chave_cliente = st.selectbox("Coluna SKU do Cliente", df_ext.columns)
            col_alvo_sistema = st.selectbox("Coluna SKU do Sistema", st.session_state.df_principal.columns)
            
            if st.button("Executar De-Para"):
                # Simulação de PROCV
                df_merge = pd.merge(
                    st.session_state.df_principal, 
                    df_ext, 
                    left_on=col_alvo_sistema, 
                    right_on=col_chave_cliente, 
                    how="left", 
                    suffixes=('', '_ext')
                )
                # Atualiza campos editáveis se encontrados na planilha externa
                for col in COLUNAS_EDITAVEIS:
                    if f"{col}_ext" in df_merge.columns:
                        df_merge[col] = df_merge[f"{col}_ext"].fillna(df_merge[col])
                
                st.session_state.df_principal = df_merge[st.session_state.df_principal.columns]
                st.success("Dados mesclados com sucesso!")

    # --- ABA 4: VALIDAÇÃO & ERROS ---
    with tab_erros:
        st.header("Relatório de Consistência")
        df = st.session_state.df_principal
        erros = []

        for idx, row in df.iterrows():
            # Erro 1: Campos Vazios
            vazios = [col for col in COLUNAS_EDITAVEIS if pd.isna(row[col]) or str(row[col]).strip() == ""]
            if vazios:
                erros.append({"Linha": idx, "Erro": f"Campos obrigatórios vazios: {', '.join(vazios)}", "Severidade": "Alta"})
            
            # Erro 2: EAN Inválido (apenas dígitos)
            if not str(row["EAN"]).isdigit() and not pd.isna(row["EAN"]):
                erros.append({"Linha": idx, "Erro": "EAN deve conter apenas números", "Severidade": "Média"})

        if erros:
            df_erros = pd.DataFrame(erros)
            st.table(df_erros)
            st.info("💡 Dica: Localize a 'Linha' na aba Editor para corrigir.")
        else:
            st.success("Nenhum erro crítico detectado.")

    # --- ABA 5: EXPORTAÇÃO (QA GATE) ---
    with tab_export:
        st.header("QA Gate - Revisão Obrigatória")
        df_final = st.session_state.df_principal
        
        tamanho_lote = 10
        total_lotes = math.ceil(len(df_final) / tamanho_lote)
        
        st.write(f"Total de Produtos: {len(df_final)} | Lotes para revisão: {total_lotes}")
        
        lote_atual = st.number_input("Visualizar Lote", min_value=1, max_value=total_lotes, step=1)
        
        inicio = (lote_atual - 1) * tamanho_lote
        fim = inicio + tamanho_lote
        preview_lote = df_final.iloc[inicio:fim]
        
        colunas_exibicao = list(dict.fromkeys(COLUNAS_EDITAVEIS + ["SKU"]))
        st.dataframe(preview_lote[colunas_exibicao], use_container_width=True)
        
        col_ok, col_cor = st.columns(2)
        if col_ok.button(f"Marcar Lote {lote_atual} como OK"):
            st.session_state.qa_checks[lote_atual] = "OK"
        if col_cor.button(f"Marcar Lote {lote_atual} para CORREÇÃO"):
            st.session_state.qa_checks[lote_atual] = "CORRIGIR"

        # Progresso
        revisados = len(st.session_state.qa_checks)
        st.progress(revisados / total_lotes)
        st.write(f"Revisão: {revisados}/{total_lotes} lotes.")

        if revisados == total_lotes:
            st.success("✅ Todos os lotes revisados!")
            
            # Gerar Arquivos
            csv_data = df_final.to_csv(index=False).encode('utf-8')
            
            # Gerar Log
            log_content = f"""
            === LOG DE AUDITORIA QA ===
            Sessão: {st.session_state.session_id}
            Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            Hash SHA256: {calcular_hash(df_final)}
            Resultados por Lote: {st.session_state.qa_checks}
            ==========================
            """
            
            st.download_button("Baixar Planilha Final", data=csv_data, file_name=f"importacao_{st.session_state.session_id}.csv")
            st.download_button("Baixar Log de Auditoria (QA)", data=log_content, file_name=f"{st.session_state.session_id}_qa_log.txt")
        else:
            st.warning("A exportação será liberada após a revisão de todos os lotes.")

else:
    st.info("Aguardando upload da planilha do sistema no menu lateral.")