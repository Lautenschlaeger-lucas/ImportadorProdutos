import streamlit as st
import pandas as pd
import math
import io
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Portal de Importação de Produtos", layout="wide", page_icon="📦")

# ==========================================
# INICIALIZAÇÃO DO ESTADO (SESSION STATE)
# ==========================================
# Isso garante que a planilha não suma quando o usuário trocar de aba
if 'base_padrao' not in st.session_state:
    # Base de dados simulada (O seu sistema "interno")
    st.session_state.base_padrao = pd.DataFrame({
        "SKU": ["SKU001", "SKU002", "SKU003", "SKU004"],
        "Nome": ["Camiseta Básica", "Calça Jeans", "Tênis Esportivo", "Jaqueta Couro"],
        "Preco_Alvo": [49.90, 129.90, 199.90, 299.90],
        "Categoria": ["Roupas", "Roupas", "Calçados", "Roupas"]
    })

if 'df_trabalho' not in st.session_state:
    st.session_state.df_trabalho = pd.DataFrame(columns=["SKU", "Nome", "Preco_Alvo", "Categoria"])

if 'blocos_validados' not in st.session_state:
    st.session_state.blocos_validados = []

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.title("📦 Sistema de Importação & Validação de Produtos")
st.markdown("Bem-vindo. Siga as abas abaixo para mapear, validar e exportar seus produtos com segurança.")

# Criando as 6 Abas
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "① Busca & Preview", 
    "② Editor de Planilha", 
    "③ PROCV / De-Para", 
    "④ Validação & Erros", 
    "⑤ Perfis de Mapeamento", 
    "⑥ Checkout & Exportação"
])

# --- ABA 1: BUSCA E PREVIEW ---
with tab1:
    st.header("Busca Manual de Produtos")
    st.write("Pesquise um produto na base mestre para adicionar manualmente à sua planilha.")
    
    busca = st.text_input("🔍 Digite o SKU ou Nome do produto:")
    if busca:
        resultados = st.session_state.base_padrao[
            st.session_state.base_padrao['SKU'].str.contains(busca, case=False) |
            st.session_state.base_padrao['Nome'].str.contains(busca, case=False)
        ]
        st.dataframe(resultados, use_container_width=True)
        
        if not resultados.empty:
            if st.button("➕ Adicionar à Planilha de Trabalho"):
                st.session_state.df_trabalho = pd.concat([st.session_state.df_trabalho, resultados]).drop_duplicates(subset=['SKU'])
                st.success("Produto adicionado com sucesso! Vá para a aba 'Editor de Planilha'.")

# --- ABA 2: EDITOR VIVO ---
with tab2:
    st.header("Editor de Planilha (Live)")
    st.write("Edite os dados diretamente na tabela abaixo. As alterações são salvas automaticamente.")
    
    if st.session_state.df_trabalho.empty:
        st.info("Sua planilha está vazia. Adicione produtos na aba Busca ou importe via PROCV.")
    else:
        # st.data_editor permite edição estilo Excel
        df_editado = st.data_editor(
            st.session_state.df_trabalho,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_planilha"
        )
        st.session_state.df_trabalho = df_editado # Atualiza o estado com a edição

# --- ABA 3: PROCV / DE-PARA ---
with tab3:
    st.header("Importação em Massa (De-Para)")
    arquivo_cliente = st.file_uploader("📂 Suba a planilha do seu sistema (.csv ou .xlsx)", type=['csv', 'xlsx'])
    
    if arquivo_cliente:
        try:
            if arquivo_cliente.name.endswith('.csv'):
                df_cliente = pd.read_csv(arquivo_cliente)
            else:
                df_cliente = pd.read_excel(arquivo_cliente)
                
            colunas_cliente = df_cliente.columns.tolist()
            
            st.subheader("Mapeamento de Colunas")
            col1, col2 = st.columns(2)
            
            with col1:
                chave_cliente = st.selectbox("1. Qual coluna da sua planilha tem o SKU?", ["Selecione..."] + colunas_cliente)
            with col2:
                st.info("A chave alvo no sistema será sempre o 'SKU'.")
                
            if chave_cliente != "Selecione...":
                if st.button("🚀 Executar Merge (PROCV)"):
                    # Faz o merge da base do cliente com a base padrão usando o SKU
                    df_merge = pd.merge(df_cliente, st.session_state.base_padrao, left_on=chave_cliente, right_on="SKU", how="inner")
                    st.session_state.df_trabalho = df_merge
                    st.success(f"{len(df_merge)} produtos cruzados e importados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

# --- ABA 4: VALIDAÇÃO & ERROS ---
with tab4:
    st.header("Painel de Validação")
    df_atual = st.session_state.df_trabalho
    
    if df_atual.empty:
        st.warning("Nenhum dado para validar.")
    else:
        erros = df_atual[df_atual.isnull().any(axis=1)]
        linhas_ok = len(df_atual) - len(erros)
        
        col1, col2 = st.columns(2)
        col1.metric("✅ Linhas Validadas", linhas_ok)
        col2.metric("❌ Linhas com Erro (Campos Vazios)", len(erros))
        
        if not erros.empty:
            st.error("Atenção: As linhas abaixo possuem campos vazios e precisam de correção na aba Editor.")
            st.dataframe(erros, use_container_width=True)
        else:
            st.success("Tudo certo! Base pronta para revisão e exportação.")

# --- ABA 5: PERFIS ---
with tab5:
    st.header("Perfis de Mapeamento")
    st.write("Salve o mapeamento feito na aba anterior para não precisar refazer na próxima semana.")
    
    nome_perfil = st.text_input("Nome do Perfil (Ex: Sistema Loja B)")
    if st.button("💾 Salvar Perfil"):
        st.success(f"Perfil '{nome_perfil}' salvo com sucesso! (Função visual no MVP)")

# --- ABA 6: EXPORTAÇÃO & CHECK-STEP (A Lógica dos 10 em 10) ---
with tab6:
    st.header("Revisão Crítica e Exportação")
    df_final = st.session_state.df_trabalho
    
    if df_final.empty:
        st.warning("Planilha vazia. Preencha os dados antes de exportar.")
    else:
        st.write("Para garantir a segurança, valide os lotes de produtos antes de liberar o download.")
        
        tamanho_bloco = 10
        total_blocos = math.ceil(len(df_final) / tamanho_bloco)
        
        # Loop para criar os blocos de validação
        for i in range(total_blocos):
            inicio = i * tamanho_bloco
            fim = inicio + tamanho_bloco
            bloco_df = df_final.iloc[inicio:fim]
            
            with st.expander(f"📦 Bloco {i+1} de {total_blocos} (Produtos {inicio+1} a {min(fim, len(df_final))})", expanded=(i not in st.session_state.blocos_validados)):
                st.dataframe(bloco_df[['SKU', 'Nome']], use_container_width=True)
                
                # Checkbox de validação
                check = st.checkbox(f"Confirmo que revisei os SKUs do Bloco {i+1}", key=f"check_{i}")
                
                if check and i not in st.session_state.blocos_validados:
                    st.session_state.blocos_validados.append(i)
                elif not check and i in st.session_state.blocos_validados:
                    st.session_state.blocos_validados.remove(i)

        # Barra de progresso geral
        progresso = len(st.session_state.blocos_validados) / total_blocos if total_blocos > 0 else 0
        st.progress(progresso, text=f"Status de Revisão: {len(st.session_state.blocos_validados)}/{total_blocos} blocos confirmados.")

        # Liberação do Download
        if len(st.session_state.blocos_validados) == total_blocos and total_blocos > 0:
            st.success("Tudo aprovado! Arquivo liberado para download.")
            
            # Prepara o Excel em memória
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False, sheet_name='Base_Validada')
            
            # Botão de Download
            st.download_button(
                label="⬇️ Baixar Planilha Final (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"importacao_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.download_button(
                label="📝 Baixar Log de Auditoria (.txt)",
                data=f"Auditoria gerada em {datetime.now()}\nTotal Itens: {len(df_final)}\nBlocos revisados: {total_blocos}\nStatus: 100% Validado pelo Cliente.",
                file_name="log_auditoria.txt",
                mime="text/plain"
            )
        else:
            st.error("Valide todos os blocos acima marcando os checkboxes para liberar o download.")