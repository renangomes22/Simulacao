import gzip
import base64
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

import datetime as dt_module

def to_date(obj):
    if obj is None:
        return None
    if isinstance(obj, pd.Timestamp):
        return obj.date()
    if isinstance(obj, dt_module.datetime):
        return obj.date()
    if isinstance(obj, dt_module.date):
        return obj
    if isinstance(obj, str):
        try:
            return dt_module.datetime.strptime(obj.strip(), "%Y-%m-%d").date()
        except:
            try:
                return pd.to_datetime(obj.strip()).date()
            except:
                return None
    return obj


# =====================================================================
# 1. ESTILIZAÇÃO E CONFIGURAÇÃO DA INTERFACE (STREAMLIT)
# =====================================================================
st.set_page_config(
    page_title="GCP-Molas | Gêmeo Digital, APS & DDMRP V38",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: bold;
    color: #1E3A8A;
    margin-bottom: 2px;
}
.sub-title {
    font-size: 15px;
    color: #4B5563;
    margin-bottom: 20px;
}
.card-metric-critical {
    background-color: #FEE2E2;
    padding: 15px;
    border-radius: 8px;
    border-left: 5px solid #DC2626;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
}
.card-metric-warning {
    background-color: #FEF3C7;
    padding: 15px;
    border-radius: 8px;
    border-left: 5px solid #D97706;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
}
.card-metric-normal {
    background-color: #E0F2FE;
    padding: 15px;
    border-radius: 8px;
    border-left: 5px solid #0284C7;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
}
.sidebar-section-title {
    font-size: 16px;
    font-weight: bold;
    color: #1E3A8A;
    margin-top: 15px;
    margin-bottom: 5px;
    border-bottom: 1px solid #E5E7EB;
    padding-bottom: 3px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. DEFINIÇÃO DA BASE DE DADOS OPERACIONAIS (ROTEIRO PADRÃO COM SEQUÊNCIAS)
# =====================================================================
DEMANDA_B64 = """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"""

ROTEIRO_B64 = """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"""

def carregar_dados_iniciais():
    try:
        dem_decomp = gzip.decompress(base64.b64decode(DEMANDA_B64)).decode("utf-8")
        demandas = json.loads(dem_decomp)
    except Exception as e:
        demandas = []
        
    try:
        rot_decomp = gzip.decompress(base64.b64decode(ROTEIRO_B64)).decode("utf-8")
        roteiros = json.loads(rot_decomp)
    except Exception as e:
        roteiros = []
        
    return demandas, roteiros


RECURSOS_PADRAO_FALLBACK = {
    "Fornos": [
        ("Forno 6m C01", 0.85),
        ("Forno 6m C02", 0.85),
        ("Forno 3m C03", 0.85),
        ("Forno 3m (Têmpera)", 0.85)
    ],
    "Retíficas": [
        ("Retífica Grande 152 - Lado A", 0.75),
        ("Retífica Grande 152 - Lado B", 0.75),
        ("Retífica Grande 153 - Lado A", 0.75),
        ("Retífica Grande 153 - Lado B", 0.75),
        ("Retífica Pequena 154 - Seco", 0.75),
        ("Retífica Pequena 319 - Lado A", 0.75),
        ("Retífica Pequena 319 - Lado B", 0.75)
    ],
    "Acabamento": [
        ("Qualidade", 0.90),
        ("Pintura Epoxi", 0.90)
    ]
}

DEMANDAS_INICIAIS, ROTEIROS_PADRAO_DADOS = carregar_dados_iniciais()


# =====================================================================
# 3. CONTROLE DE ESTADO DA SESSÃO (SESSION STATE)
# =====================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def renderizar_tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='background-color: #FFFFFF; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; margin-top: 40px;'>
            <div style='text-align: center; margin-bottom: 20px;'>
                <div style='font-size: 48px; margin-bottom: 5px;'>⚙️</div>
                <h2 style='color: #1E3A8A; margin: 0; font-weight: 700;'>GCP-Molas</h2>
                <p style='color: #64748B; font-size: 14px; margin-top: 5px;'>Gêmeo Digital & Sistema de Capacidade Produtiva</p>
            </div>
            <hr style='border: None; border-top: 1px solid #E2E8F0; margin: 15px 0 25px 0;'>
            <h4 style='color: #334155; margin-bottom: 15px; text-align: center;'>🔐 Autenticação de Usuário</h4>
        """, unsafe_allow_html=True)
        
        login_input = st.text_input("👤 Usuário", key="login_usuario_field", placeholder="Digite seu usuário")
        senha_input = st.text_input("🔑 Senha", type="password", key="login_senha_field", placeholder="Digite sua senha")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Entrar no Simulador", use_container_width=True, type="primary"):
            if login_input == "admin" and senha_input == "simulador":
                st.session_state.autenticado = True
                st.success("✅ Acesso liberado com sucesso!")
                st.rerun()
            else:
                st.error("🔒 Usuário ou senha incorretos! Verifique suas credenciais.")
                
        st.markdown("""
            <div style='text-align: center; margin-top: 25px; font-size: 12px; color: #94A3B8;'>
                GCP-Molas APS & DDMRP &bull; Acesso Restrito ao PCP
            </div>
        </div>
        """, unsafe_allow_html=True)

if not st.session_state.autenticado:
    renderizar_tela_login()
    st.stop()


if "recursos_padrao" not in st.session_state:
    st.session_state.recursos_padrao = {
        "Fornos": [
            ("Forno 6m C01", 0.85),
            ("Forno 6m C02", 0.85),
            ("Forno 3m C03", 0.85),
            ("Forno 3m (Têmpera)", 0.85)
        ],
        "Retíficas": [
            ("Retífica Grande 152 - Lado A", 0.75),
            ("Retífica Grande 152 - Lado B", 0.75),
            ("Retífica Grande 153 - Lado A", 0.75),
            ("Retífica Grande 153 - Lado B", 0.75),
            ("Retífica Pequena 154 - Seco", 0.75),
            ("Retífica Pequena 319 - Lado A", 0.75),
            ("Retífica Pequena 319 - Lado B", 0.75)
        ],
        "Acabamento": [
            ("Qualidade", 0.90),
            ("Pintura Epoxi", 0.90)
        ]
    }

if "definicao_eficiencias" not in st.session_state:
    st.session_state.definicao_eficiencias = {}
    for grupo, maquinas in st.session_state.recursos_padrao.items():
        for m, ef in maquinas:
            st.session_state.definicao_eficiencias[m] = int(ef * 100)

if "definicao_turnos" not in st.session_state:
    st.session_state.definicao_turnos = {
        "Turno 1": 9.0,
        "Turno 2": 0.0,
        "Turno 3": 0.0
    }

if "recursos_operadores" not in st.session_state:
    st.session_state.recursos_operadores = {}
    for grupo, maquinas in st.session_state.recursos_padrao.items():
        for m, _ in maquinas:
            st.session_state.recursos_operadores[m] = 1

if "roteiros_tempos" not in st.session_state:
    st.session_state.roteiros_tempos = pd.DataFrame(ROTEIROS_PADRAO_DADOS)
st.session_state.roteiros_tempos["Produto"] = st.session_state.roteiros_tempos["Produto"].astype(str).str.strip()

if "demandas" not in st.session_state:
    st.session_state.demandas = pd.DataFrame(DEMANDAS_INICIAIS)
st.session_state.demandas["PRODUTO"] = st.session_state.demandas["PRODUTO"].astype(str).str.strip()

if "ultimo_arquivo_demanda" not in st.session_state:
    st.session_state.ultimo_arquivo_demanda = None

if "ultimo_arquivo_roteiro" not in st.session_state:
    st.session_state.ultimo_arquivo_roteiro = None

if "horas_extras" not in st.session_state:
    st.session_state.horas_extras = {
        "2026-09-07_Retífica Pequena 319 - Lado A": 8.0,
        "2026-09-07_Retífica Pequena 319 - Lado B": 8.0
    }

if "digital_twin_enabled" not in st.session_state:
    st.session_state.digital_twin_enabled = False
if "digital_twin_runs" not in st.session_state:
    st.session_state.digital_twin_runs = 50
if "digital_twin_var_process" not in st.session_state:
    st.session_state.digital_twin_var_process = 10
if "digital_twin_breakdown_prob" not in st.session_state:
    st.session_state.digital_twin_breakdown_prob = 5
if "digital_twin_mttr" not in st.session_state:
    st.session_state.digital_twin_mttr = 4.0

# =====================================================================
# 4. CONSTRUÇÃO DO PAINEL LATERAL (SIDEBAR PARAMETRIZÁVEL)
# =====================================================================
st.sidebar.image("https://img.icons8.com/color/120/000000/settings.png", width=60)
st.sidebar.markdown("<div style='font-size: 20px; font-weight: bold; color: #1E3A8A; margin-bottom:5px;'>Painel de Configurações</div>", unsafe_allow_html=True)
col_usr1, col_usr2 = st.sidebar.columns([2, 1])
with col_usr1:
    st.markdown("<span style='font-size:12px; color:#475569;'>👤 Logado: <b>admin</b></span>", unsafe_allow_html=True)
with col_usr2:
    if st.button("🔒 Sair", key="btn_logout_top", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
st.sidebar.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# ----------------- SEÇÃO 1: HORIZONTE TEMPORAL -----------------
with st.sidebar.expander("📅 1. Data de Início e Fim", expanded=True):
    data_inicio_val = datetime.strptime("2026-09-01", "%Y-%m-%d").date()
    data_fim_val = datetime.strptime("2026-09-30", "%Y-%m-%d").date()
    periodo_selecionado = st.date_input(
        "Intervalo da Simulação",
        value=(data_inicio_val, data_fim_val),
        min_value=datetime.strptime("2026-01-01", "%Y-%m-%d").date(),
        max_value=datetime.strptime("2027-12-31", "%Y-%m-%d").date(),
        format="DD/MM/YYYY"
    )
    if isinstance(periodo_selecionado, tuple) and len(periodo_selecionado) == 2:
        data_inicio, data_fim = to_date(periodo_selecionado[0]), to_date(periodo_selecionado[1])
    else:
        data_inicio, data_fim = to_date(data_inicio_val), to_date(data_fim_val)

# ----------------- SEÇÃO 2: DEFINIÇÃO (EFICIÊNCIAS POR MÁQUINA E TURNOS) -----------------
with st.sidebar.expander("⚙️ 2. Definição (Eficiência por Máquina & Turnos)", expanded=False):
    st.markdown("**Eficiência Geral OEE por Máquina (%):**")
    for grupo, maquinas in st.session_state.recursos_padrao.items():
        st.markdown(f"**Grupo: {grupo}**")
        for m, _ in maquinas:
            st.session_state.definicao_eficiencias[m] = st.slider(
                f"Eficiência {m}",
                min_value=0, max_value=100,
                value=st.session_state.definicao_eficiencias.get(m, 85 if grupo=="Fornos" else (75 if grupo=="Retíficas" else 90)),
                step=5,
                key=f"ef_slider_{m}"
            )
            
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    st.markdown("**Jornada do Turno (Horas/Dia):**")
    for turno in ["Turno 1", "Turno 2", "Turno 3"]:
        st.session_state.definicao_turnos[turno] = st.number_input(
            f"Horas {turno}",
            min_value=0.0, max_value=12.0,
            value=st.session_state.definicao_turnos[turno],
            step=0.5
        )

    st.markdown("---")
    st.markdown("**🛠️ Gerenciar Equipamentos (GCP)**")
    
    # Adicionar nova máquina
    st.markdown("*➕ Incluir Novo Equipamento:*")
    col_add1, col_add2 = st.columns(2)
    with col_add1:
        nova_maq_nome = st.text_input("Nome da Máquina", key="nova_maq_nome_input")
        nova_maq_grupo = st.selectbox("Grupo", options=list(st.session_state.recursos_padrao.keys()), key="nova_maq_grupo_input")
    with col_add2:
        nova_maq_oee = st.slider("OEE Padrão (%)", min_value=0, max_value=100, value=85, step=5, key="nova_maq_oee_input")
        add_btn = st.button("🚀 Incluir", use_container_width=True)
        
    if add_btn:
        if nova_maq_nome.strip():
            nome_clean = nova_maq_nome.strip()
            ja_existe = False
            for g, mqs in st.session_state.recursos_padrao.items():
                if any(m[0] == nome_clean for m in mqs):
                    ja_existe = True
                    break
            if ja_existe:
                st.error("Erro: Esta máquina já existe!")
            else:
                st.session_state.recursos_padrao[nova_maq_grupo].append((nome_clean, nova_maq_oee / 100.0))
                st.session_state.definicao_eficiencias[nome_clean] = nova_maq_oee
                st.session_state.recursos_operadores[nome_clean] = 1
                st.session_state.simulacao_disparada = False
                st.success(f"Adicionada: {nome_clean}!")
                st.rerun()
        else:
            st.warning("Insira um nome.")

    st.markdown("---")
    # Deletar máquina existente
    st.markdown("*🗑️ Deletar Equipamento:*")
    todas_maquinas_select = []
    for g, mqs in st.session_state.recursos_padrao.items():
        for m, _ in mqs:
            todas_maquinas_select.append(f"{m} ({g})")
            
    if todas_maquinas_select:
        col_del1, col_del2 = st.columns(2)
        with col_del1:
            maq_a_remover = st.selectbox("Selecionar Máquina", options=todas_maquinas_select, key="maq_remover_input")
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True) # Alinhamento vertical
            del_btn = st.button("🗑️ Deletar", use_container_width=True, type="primary")
            
        if del_btn:
            nome_maq_rem = maq_a_remover.rsplit(" (", 1)[0]
            grupo_rem = maq_a_remover.rsplit(" (", 1)[1].rstrip(")")
            
            st.session_state.recursos_padrao[grupo_rem] = [m for m in st.session_state.recursos_padrao[grupo_rem] if m[0] != nome_maq_rem]
            
            if nome_maq_rem in st.session_state.definicao_eficiencias:
                del st.session_state.definicao_eficiencias[nome_maq_rem]
            if nome_maq_rem in st.session_state.recursos_operadores:
                del st.session_state.recursos_operadores[nome_maq_rem]
                
            st.session_state.simulacao_disparada = False
            st.success(f"Removida: {nome_maq_rem}!")
            st.rerun()

        st.markdown("---")
        st.markdown("**🛠️ Gerenciar Grupos (GCP)**")
        
        # Adicionar novo grupo
        st.markdown("*➕ Incluir Novo Grupo:*")
        col_g_add1, col_g_add2 = st.columns(2)
        with col_g_add1:
            novo_grupo_nome = st.text_input("Nome do Novo Grupo", key="novo_grupo_nome_input")
        with col_g_add2:
            st.markdown("<br>", unsafe_allow_html=True)
            add_g_btn = st.button("🚀 Criar Grupo", use_container_width=True)
            
        if add_g_btn:
            if novo_grupo_nome.strip():
                g_nome_clean = novo_grupo_nome.strip()
                if g_nome_clean in st.session_state.recursos_padrao:
                    st.error("Erro: Este grupo já existe!")
                else:
                    st.session_state.recursos_padrao[g_nome_clean] = []
                    st.session_state.simulacao_disparada = False
                    st.success(f"Grupo '{g_nome_clean}' incluído com sucesso!")
                    st.rerun()
            else:
                st.warning("Insira um nome válido para o grupo.")
                
        st.markdown("---")
        # Deletar grupo existente
        st.markdown("*🗑️ Deletar Grupo:*")
        todos_grupos_lista = list(st.session_state.recursos_padrao.keys())
        if todos_grupos_lista:
            col_g_del1, col_g_del2 = st.columns(2)
            with col_g_del1:
                grupo_a_remover = st.selectbox("Selecionar Grupo para Remover", options=todos_grupos_lista, key="grupo_remover_input")
            with col_g_del2:
                st.markdown("<br>", unsafe_allow_html=True)
                del_g_btn = st.button("🗑️ Deletar Grupo", use_container_width=True, type="primary")
                
            if del_g_btn:
                # Remover do st.session_state.recursos_padrao
                maquinas_removidas = st.session_state.recursos_padrao.pop(grupo_a_remover, [])
                
                # Limpar eficiências e operadores das máquinas que estavam no grupo
                for m, _ in maquinas_removidas:
                    if m in st.session_state.definicao_eficiencias:
                        del st.session_state.definicao_eficiencias[m]
                    if m in st.session_state.recursos_operadores:
                        del st.session_state.recursos_operadores[m]
                        
                st.session_state.simulacao_disparada = False
                st.success(f"Grupo '{grupo_a_remover}' e todas as suas máquinas associadas foram removidos!")
                st.rerun()
        else:
            st.caption("Nenhum grupo cadastrado.")
    else:
        st.caption("Nenhuma máquina cadastrada.")

# ----------------- SEÇÃO 3: RECURSOS (OPERADORES) -----------------
with st.sidebar.expander("👥 3. Recursos (Operadores por Máquina)", expanded=False):
    st.markdown("Defina a quantidade de operadores ativos por posto de trabalho:")
    todas_maquinas_lista = []
    for grupo, maquinas in st.session_state.recursos_padrao.items():
        st.markdown(f"**Grupo: {grupo}**")
        for m, _ in maquinas:
            st.session_state.recursos_operadores[m] = st.number_input(
                f"Op. {m}",
                min_value=0, max_value=10,
                value=st.session_state.recursos_operadores.get(m, 1),
                step=1,
                key=f"op_input_{m}"
            )
            todas_maquinas_lista.append(m)

# ----------------- SEÇÃO 4: ROTEIROS E TEMPOS (UPLOAD) -----------------
with st.sidebar.expander("📝 4. Roteiros e Tempos (Produtividade)", expanded=False):
    st.markdown("### Upload Direto de Roteiros")
    arquivo_roteiro = st.file_uploader("Upload Roteiro (.csv/.xlsx)", type=["csv", "xlsx"], key="upload_roteiro")
    
    # Gerar modelo de Roteiros contendo o campo de sequência
    modelo_roteiro_csv = "Produto,Sequencia,Equipamento,Prod_Hora\n284269,10,Forno 6m C01,151.0\n284269,20,Retífica Pequena 319 - Lado A,13.0\n284269,35,Qualidade,151.0\n284269,40,Pintura Epoxi,151.0"
    st.download_button(
        label="📥 Baixar Modelo de Roteiro (CSV)",
        data=modelo_roteiro_csv,
        file_name="modelo_roteiro.csv",
        mime="text/csv"
    )

    if arquivo_roteiro is not None and st.session_state.ultimo_arquivo_roteiro != arquivo_roteiro.name:
        try:
            if arquivo_roteiro.name.endswith('.csv'):
                df_up_rot = pd.read_csv(arquivo_roteiro)
            else:
                df_up_rot = pd.read_excel(arquivo_roteiro)
            
            # Padronizar nomes de colunas
            df_up_rot.columns = [str(c).strip() for c in df_up_rot.columns]
            
            # Validar colunas minimas
            colunas_requeridas_rot = {"Produto", "Sequencia", "Equipamento", "Prod_Hora"}
            if colunas_requeridas_rot.issubset(set(df_up_rot.columns)):
                # Normalizar dados de upload
                df_up_rot["Produto"] = df_up_rot["Produto"].astype(str).str.strip()
                df_up_rot["Equipamento"] = df_up_rot["Equipamento"].astype(str).str.strip()
                df_up_rot["Sequencia"] = pd.to_numeric(df_up_rot["Sequencia"], errors="coerce").fillna(10).astype(int)
                df_up_rot["Prod_Hora"] = pd.to_numeric(df_up_rot["Prod_Hora"], errors="coerce").fillna(0.0).astype(float)
                
                # Normalizar dados existentes no state para garantir tipos compativeis antes do merge
                st.session_state.roteiros_tempos["Produto"] = st.session_state.roteiros_tempos["Produto"].astype(str).str.strip()
                st.session_state.roteiros_tempos["Equipamento"] = st.session_state.roteiros_tempos["Equipamento"].astype(str).str.strip()
                st.session_state.roteiros_tempos["Sequencia"] = pd.to_numeric(st.session_state.roteiros_tempos["Sequencia"], errors="coerce").fillna(10).astype(int)
                st.session_state.roteiros_tempos["Prod_Hora"] = pd.to_numeric(st.session_state.roteiros_tempos["Prod_Hora"], errors="coerce").fillna(0.0).astype(float)
                
                # Mesclar priorizando a planilha de Upload para os repetidos (Produto, Sequencia, Equipamento)
                df_combined = pd.concat([df_up_rot, st.session_state.roteiros_tempos], ignore_index=True)
                df_combined = df_combined.drop_duplicates(subset=["Produto", "Sequencia", "Equipamento"], keep="first")
                
                st.session_state.ultimo_arquivo_roteiro = arquivo_roteiro.name
                st.session_state.roteiros_tempos = df_combined
                st.session_state.simulacao_disparada = False # Resetar para forcar novo clique
                st.success("Tabela de Roteiros importada e mesclada com sucesso (conflitos resolvidos a favor do upload)! Clique em 'Iniciar Simulação' para atualizar.")
                st.rerun()
            else:
                st.error("Erro: Colunas obrigatórias ausentes no arquivo de Roteiro (Requerido: Produto, Sequencia, Equipamento, Prod_Hora)")
        except Exception as e:
            st.error(f"Erro ao ler arquivo de roteiro: {str(e)}")

# ----------------- SEÇÃO 5: DISPONIBILIDADE LÍQUIDA BASE -----------------
with st.sidebar.expander("📊 5. Disponibilidade Líquida Base", expanded=False):
    st.markdown("Capacidade diária útil em horas normais por máquina (calculada):")
    cap_base_lista = []
    for grupo, maquinas in st.session_state.recursos_padrao.items():
        horas_turno = sum(st.session_state.definicao_turnos.values())
        for m, _ in maquinas:
            ef = st.session_state.definicao_eficiencias.get(m, 85.0) / 100.0
            op_m = st.session_state.recursos_operadores.get(m, 1)
            cap_liq_m = horas_turno * op_m * ef
            cap_base_lista.append({"Máquina": m, "Cap. Líquida (h)": round(cap_liq_m, 2)})
    st.dataframe(pd.DataFrame(cap_base_lista), hide_index=True)

# ----------------- SEÇÃO 6: UPLOAD DIRETO DE PLANILHAS DE DEMANDA -----------------
with st.sidebar.expander("📤 6. Upload de Planilha de Demanda", expanded=False):
    st.markdown("Importe as planilhas de demanda contendo os campos: **PEDIDO DE VENDA, ORDEM, PRODUTO, CLIENTE, QUANTIDADE, DATA DE ENTREGA**")
    
    arquivo_demanda = st.file_uploader("Upload Demanda (.csv/.xlsx)", type=["csv", "xlsx"], key="upload_demanda")
    
    # Gerar modelo de Demanda com os campos requeridos
    modelo_dem_csv = "PEDIDO DE VENDA,ORDEM,PRODUTO,CLIENTE,QUANTIDADE,DATA DE ENTREGA\nPV-1010,0105294-002,284269,MRS Logística S/A,130,2026-05-06\nPV-1011,0106147-002,282001,Ferrovia Norte Sul S/A,180,2026-05-05"
    st.download_button(
        label="📥 Baixar Modelo de Demanda (CSV)",
        data=modelo_dem_csv,
        file_name="modelo_demanda.csv",
        mime="text/csv"
    )

    if arquivo_demanda is not None and st.session_state.ultimo_arquivo_demanda != arquivo_demanda.name:
        try:
            if arquivo_demanda.name.endswith('.csv'):
                df_up_dem = pd.read_csv(arquivo_demanda)
            else:
                df_up_dem = pd.read_excel(arquivo_demanda)
            
            # Normalizar cabeçalhos para evitar erros de espaços ou caixa
            df_up_dem.columns = [str(c).upper().strip() for c in df_up_dem.columns]
            
            colunas_requeridas_dem = {"PEDIDO DE VENDA", "ORDEM", "PRODUTO", "CLIENTE", "QUANTIDADE", "DATA DE ENTREGA"}
            if colunas_requeridas_dem.issubset(set(df_up_dem.columns)):
                # Armazenar no session state como dataframe de demandas ativos
                st.session_state.ultimo_arquivo_demanda = arquivo_demanda.name
                st.session_state.demandas = df_up_dem
                st.session_state.simulacao_disparada = False # Resetar para forçar novo clique
                st.success("Planilha de Demanda carregada e importada com sucesso! Clique em 'Iniciar Simulação' para atualizar.")
                st.rerun()
            else:
                st.error("Erro: Colunas obrigatórias ausentes na planilha de demanda (Requerido: PEDIDO DE VENDA, ORDEM, PRODUTO, CLIENTE, QUANTIDADE, DATA DE ENTREGA)")
        except Exception as e:
            st.error(f"Erro ao carregar planilha de demanda: {str(e)}")

# ----------------- SEÇÃO 7: CONFIGURAÇÃO DO MOTOR APS DE CAPACIDADE FINITA -----------------
with st.sidebar.expander("🧠 7. Configuração do Motor APS", expanded=True):
    tipo_planejamento = st.selectbox(
        "Tipo de Planejamento",
        options=["Finito (FCS - Finite Capacity Scheduling)", "Infinito (MRP II / CRP)"],
        key="tipo_planejamento"
    )
    regra_sequenciamento = st.selectbox(
        "Regra de Sequenciamento (Dispatching Rule)",
        options=[
            "EDD - Earliest Due Date", 
            "SPT - Shortest Processing Time", 
            "Prioridade de Cliente", 
            "TOC - Carga do Grupo Gargalo Primeiro"
        ],
        key="regra_sequenciamento"
    )
    
    if regra_sequenciamento == "TOC - Carga do Grupo Gargalo Primeiro":
        grupos_existentes = list(st.session_state.recursos_padrao.keys())
        default_idx = grupos_existentes.index("Retíficas") if "Retíficas" in grupos_existentes else 0
        st.selectbox(
            "Selecione o Grupo Gargalo",
            options=grupos_existentes,
            index=default_idx,
            key="grupo_gargalo_selecionado"
        )

# ----------------- SEÇÃO 8: GÊMEO DIGITAL ESTOCÁSTICO -----------------
with st.sidebar.expander("🧠 8. Gêmeo Digital Estocástico", expanded=False):
    digital_twin_enabled = st.checkbox(
        "Habilitar Variabilidade (RPS)",
        value=st.session_state.digital_twin_enabled,
        key="digital_twin_enabled"
    )
    digital_twin_runs = st.slider(
        "Qtd. Simulações (Monte Carlo)",
        min_value=10, max_value=200,
        value=st.session_state.digital_twin_runs,
        step=10,
        key="digital_twin_runs"
    )
    digital_twin_var_process = st.slider(
        "Variabilidade do Tempo (%)",
        min_value=0, max_value=50,
        value=st.session_state.digital_twin_var_process,
        step=5,
        key="digital_twin_var_process"
    )
    digital_twin_breakdown_prob = st.slider(
        "Chance Diária de Falha (%)",
        min_value=0, max_value=30,
        value=st.session_state.digital_twin_breakdown_prob,
        step=1,
        key="digital_twin_breakdown_prob"
    )
    digital_twin_mttr = st.slider(
        "Tempo de Reparo (MTTR - horas)",
        min_value=1.0, max_value=12.0,
        value=st.session_state.digital_twin_mttr,
        step=0.5,
        key="digital_twin_mttr"
    )

# ----------------- SEÇÃO 9: BOTÃO DE EXECUÇÃO DA SIMULAÇÃO -----------------
st.sidebar.markdown("<br>", unsafe_allow_html=True)
executar_simulacao = st.sidebar.button("⚙️ Iniciar Simulação", use_container_width=True, type="primary")

if "simulacao_disparada" not in st.session_state:
    st.session_state.simulacao_disparada = False

if executar_simulacao:
    st.session_state.simulacao_disparada = True
    st.sidebar.success("Simulação executada com sucesso!")

# =====================================================================
# 5. MOTOR DE CÁLCULO DE CAPACIDADE PRODUTIVA E SIMULAÇÃO (EXPLOSÃO MRP)
# =====================================================================

# Se a simulação não foi disparada pelo usuário, exibimos uma mensagem convidativa e paramos a execução
if not st.session_state.get("simulacao_disparada", False):
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("💡 **Aguardando início da simulação:** Configure seus parâmetros de eficiências, operadores, turnos ou carregue seus arquivos de demanda e roteiros na barra lateral, e então clique no botão **⚙️ Iniciar Simulação** para processar o planejamento e visualizar os cronogramas e gráficos interativos de capacidade.")
    st.stop()


# Controle de Execução e Cache em Session State
if executar_simulacao or "sim_resultado_df" not in st.session_state:
    with st.spinner("⚡ Executando motor de planejamento de capacidade finita (FCS) e Monte Carlo..."):
        # Gerar calendário de datas com capacidade de máquinas
        datas_periodo = [data_inicio + timedelta(days=x) for x in range((data_fim - data_inicio).days + 1)]
        registros_simulacao = []
        
        for dt in datas_periodo:
            dt_str = dt.strftime("%Y-%m-%d")
            dia_semana_num = dt.weekday()
            fator_calendario = 1 if dia_semana_num < 5 else 0
            dia_semana_nome = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][dia_semana_num]
            
            for grupo, maquinas in st.session_state.recursos_padrao.items():
                horas_turno = sum(st.session_state.definicao_turnos.values())
                for m, _ in maquinas:
                    eficiencia = st.session_state.definicao_eficiencias.get(m, 85.0) / 100.0
                    op_ativos = st.session_state.recursos_operadores.get(m, 1)
                    # Recuperar horas extras
                    chave_he = f"{dt_str}_{m}"
                    horas_extras = st.session_state.horas_extras.get(chave_he, 0.0)
                    
                    cap_regular = horas_turno * op_ativos * fator_calendario * eficiencia
                    cap_extra = horas_extras * eficiencia
                    cap_total = round(cap_regular + cap_extra, 2)
                    
                    registros_simulacao.append({
                        "Data": dt_str,
                        "Dia_Semana": dia_semana_nome,
                        "Grupo": grupo,
                        "Maquina": m,
                        "Capacidade_Regular": cap_regular,
                        "Horas_Extras": horas_extras,
                        "Capacidade_Liquida": cap_total
                    })
        
        df_cap_calculada = pd.DataFrame(registros_simulacao)
        
        # EXPLODIR DEMANDA CONTRA OS ROTEIROS DE MAQUINA E PRODUTO
        cargas_simuladas = []
        erros_roteiro = []
        demandas_ativas_brutas = []
        
        if st.session_state.simulacao_disparada and not st.session_state.demandas.empty:
            for _, d_row in st.session_state.demandas.iterrows():
                pv = d_row.get("PEDIDO DE VENDA", "-")
                op = d_row.get("ORDEM", "-")
                prod = str(d_row.get("PRODUTO", "")).strip()
                cliente = d_row.get("CLIENTE", "Cliente Geral")
                qtd = float(d_row.get("QUANTIDADE", 0))
                dt_ent = d_row.get("DATA DE ENTREGA")
                
                # Converter data de entrega para string %Y-%m-%d
                if isinstance(dt_ent, datetime):
                    dt_ent_str = dt_ent.strftime("%Y-%m-%d")
                else:
                    try:
                        dt_ent_str = pd.to_datetime(dt_ent).strftime("%Y-%m-%d")
                    except:
                        dt_ent_str = str(dt_ent)
                        
                # Buscar roteiros
                rot_match = st.session_state.roteiros_tempos[st.session_state.roteiros_tempos["Produto"] == prod]
                if rot_match.empty:
                    erros_roteiro.append(prod)
                    continue
                    
                demandas_ativas_brutas.append({
                    "Pedido": pv,
                    "OP": op,
                    "Produto": prod,
                    "Cliente": cliente,
                    "Quantidade": int(qtd),
                    "Data_Entrega_Original": dt_ent_str,
                    "Rot_Match": rot_match
                })
        
        # 1. ORDENAÇÃO SELETIVA DE ACORDO COM A DISPATCHING RULE PARA DIVISÃO DINÂMICA
        if demandas_ativas_brutas:
            if regra_sequenciamento == "EDD - Earliest Due Date":
                demandas_ativas_brutas = sorted(demandas_ativas_brutas, key=lambda x: x["Data_Entrega_Original"])
            elif regra_sequenciamento == "SPT - Shortest Processing Time":
                # Estimar horas com divisão igual simples para SPT
                def est_hours(item):
                    tot = 0.0
                    for seq, gp in item["Rot_Match"].groupby("Sequencia"):
                        n = len(gp)
                        for _, r in gp.iterrows():
                            p_h = float(r["Prod_Hora"])
                            if p_h > 0:
                                tot += (item["Quantidade"] / n) / p_h
                    return tot
                demandas_ativas_brutas = sorted(demandas_ativas_brutas, key=est_hours)
            elif regra_sequenciamento == "Prioridade de Cliente":
                def priority_rule(x):
                    cli = x["Cliente"].upper()
                    if "MRS" in cli: return 1
                    elif "NORTE" in cli or "CENTRO" in cli or "FERROVIA" in cli: return 2
                    else: return 3
                demandas_ativas_brutas = sorted(demandas_ativas_brutas, key=priority_rule)
            else:  # TOC - Carga do Grupo Gargalo Primeiro
                # Encontrar os equipamentos que pertencem ao grupo gargalo selecionado dinamicamente
                grupo_gargalo_nome = st.session_state.get("grupo_gargalo_selecionado", "Retíficas")
                gargalo_maquinas = [m[0] for m in st.session_state.recursos_padrao.get(grupo_gargalo_nome, [])]
                def est_gargalo_hours_and_edd(item):
                    tot = 0.0
                    for seq, gp in item["Rot_Match"].groupby("Sequencia"):
                        n = len(gp)
                        for _, r in gp.iterrows():
                            maq = r["Equipamento"]
                            if maq in gargalo_maquinas:
                                p_h = float(r["Prod_Hora"])
                                if p_h > 0:
                                    tot += (item["Quantidade"] / n) / p_h
                    return (-tot, item["Data_Entrega_Original"]) # Maior carga primeiro, depois EDD
                demandas_ativas_brutas = sorted(demandas_ativas_brutas, key=est_gargalo_hours_and_edd)

        # 2. DISTRIBUIÇÃO INTEGRA DE PEÇAS COM BASE NA DISP. ACUMULADA RESTANTE
        maquina_capacidade_acumulada_restante = {m: df_cap_calculada[df_cap_calculada["Maquina"] == m]["Capacidade_Liquida"].sum() for m in todas_maquinas_lista}
        
        demandas_ativas = []
        for op_item in demandas_ativas_brutas:
            op_id = op_item["OP"]
            qtd = op_item["Quantidade"]
            rot_match = op_item["Rot_Match"]
            
            total_op_horas = 0.0
            operacoes_op = []
            
            # Agrupar roteiro por Sequencia
            rot_groups = rot_match.groupby("Sequencia")
            for seq, group in rot_groups:
                num_alt = len(group)
                
                # Ordenar as alternativas pela capacidade restante acumulada da máquina
                sorted_rows = []
                for _, r_row in group.iterrows():
                    m = r_row["Equipamento"]
                    disp = maquina_capacidade_acumulada_restante.get(m, 0.0)
                    sorted_rows.append((disp, r_row))
                
                # Ordenar decrescente por disponibilidade
                sorted_rows = sorted(sorted_rows, key=lambda x: x[0], reverse=True)
                
                # Divisão inteira exata sem floats
                base_qty = int(qtd // num_alt)
                rem_qty = int(qtd % num_alt)
                
                for idx, (disp, r_row) in enumerate(sorted_rows):
                    qtd_alocada = base_qty + (1 if idx < rem_qty else 0)
                    
                    if qtd_alocada > 0:
                        prod_hora = float(r_row["Prod_Hora"])
                        carga_h = round(qtd_alocada / prod_hora, 2) if prod_hora > 0 else 0.0
                        total_op_horas += carga_h
                        
                        # Atualizar a disponibilidade acumulada restante da máquina
                        maquina_capacidade_acumulada_restante[r_row["Equipamento"]] -= carga_h
                        
                        operacoes_op.append({
                            "Maquina": r_row["Equipamento"],
                            "Carga": carga_h,
                            "Sequencia": seq,
                            "Quantidade_Alocada": int(qtd_alocada),
                            "Prod_Hora": prod_hora
                        })
            
            demandas_ativas.append({
                "Pedido": op_item["Pedido"],
                "OP": op_id,
                "Produto": op_item["Produto"],
                "Cliente": op_item["Cliente"],
                "Quantidade": int(qtd),
                "Data_Entrega_Original": op_item["Data_Entrega_Original"],
                "Total_Horas": total_op_horas,
                "Operacoes": operacoes_op
            })
            
        # ----------------- ALGORITMO DE SEQUENCIAMENTO E PROGRAMAÇÃO DE CAPACIDADE -----------------
        cargas_finitas_detalhadas = []
        gantt_records = []
        
        if tipo_planejamento == "Finito (FCS - Finite Capacity Scheduling)" and demandas_ativas:
            # Já estão ordenadas pelo passo anterior de explosão dinâmica
            demandas_ativas_ordenadas = demandas_ativas
        
            # Dicionário de rastreamento de alocações diárias: maquina_ocupada[data_str][maquina] = horas_consumidas
            maquina_ocupada_diaria = {}
            for dt in datas_periodo:
                dt_str = dt.strftime("%Y-%m-%d")
                maquina_ocupada_diaria[dt_str] = {m: 0.0 for m in todas_maquinas_lista}
        
            # Mapeamento rápido de capacidade para otimizar pesquisas O(1)
            cap_liquida_lookup = {
                (row.Data, row.Maquina): row.Capacidade_Liquida 
                for row in df_cap_calculada.itertuples()
            }
        
            # 2. ALOCAÇÃO SEQUENCIAL FINITA (FORWARD LOADING) - COM LOGICA DE CASCATA TOC V28
            for op_item in demandas_ativas_ordenadas:
                op_id = op_item["OP"]
                cliente = op_item["Cliente"]
                prod = op_item["Produto"]
                due_date_str = op_item["Data_Entrega_Original"]
                
                # Agrupar as operações por sequência para planejar em paralelo as alternativas
                from collections import defaultdict
                operacoes_por_seq = defaultdict(list)
                for operacao in op_item["Operacoes"]:
                    operacoes_por_seq[operacao["Sequencia"]].append(operacao)
                
                sequencias_ordenadas = sorted(operacoes_por_seq.keys())
                
                # Data de partida para a OP é o início do período ou o dia de hoje
                earliest_start_date = data_inicio
                
                # Quantidade vinda do posto anterior (inicialmente é a total do pedido)
                qtd_limite_anterior = op_item["Quantidade"]
                
                for seq in sequencias_ordenadas:
                    operacoes_da_seq = operacoes_por_seq[seq]
                    datas_fim_da_seq = []
                    
                    num_alt = len(operacoes_da_seq)
                    
                    # Divisão original do lote completo (caso não houvesse gargalo a montante)
                    base_qty_original = int(op_item["Quantidade"] // num_alt)
                    rem_qty_original = int(op_item["Quantidade"] % num_alt)
                    
                    # Divisão dinâmica do lote de fato recebido da sequência anterior
                    base_qty_received = int(qtd_limite_anterior // num_alt)
                    rem_qty_received = int(qtd_limite_anterior % num_alt)
                    
                    # Somador de peças que de fato conseguimos agendar nesta sequência
                    qtd_agendada_seq_total = 0
                    
                    for idx, operacao in enumerate(operacoes_da_seq):
                        maq = operacao["Maquina"]
                        prod_hora = operacao["Prod_Hora"]
                        
                        qtd_original_maquina = base_qty_original + (1 if idx < rem_qty_original else 0)
                        qtd_alocada_maquina = base_qty_received + (1 if idx < rem_qty_received else 0)
                        
                        # Carga de horas recalculada em tempo real com base na quantidade real herdada
                        carga_req = round(qtd_alocada_maquina / prod_hora, 2) if prod_hora > 0 else 0.0
                        
                        scheduled_on_days = []
                        current_day_search = earliest_start_date
                        
                        op_total_qty = qtd_alocada_maquina
                        op_total_carga = carga_req
                        remaining_qty = op_total_qty
                        
                        # Executar o agendamento diário caso tenhamos quantidade de peças a produzir
                        while carga_req > 0.01:
                            if current_day_search > data_fim:
                                break
                            
                            day_str = current_day_search.strftime("%Y-%m-%d")
                            cap_liquida = cap_liquida_lookup.get((day_str, maq), 0.0)
                            horas_ocupadas = maquina_ocupada_diaria[day_str].get(maq, 0.0)
                            cap_restante = max(0.0, cap_liquida - horas_ocupadas)
                            
                            if cap_restante > 0.05:
                                allocated = min(carga_req, cap_restante)
                                maquina_ocupada_diaria[day_str][maq] += allocated
                                carga_req -= allocated
                                
                                if carga_req <= 0.01:
                                    day_qty = remaining_qty
                                else:
                                    day_qty = int(round((allocated / op_total_carga) * op_total_qty)) if op_total_carga > 0 else 0
                                    day_qty = min(day_qty, remaining_qty)
                                remaining_qty -= day_qty
                                qtd_agendada_seq_total += day_qty
                                
                                cargas_finitas_detalhadas.append({
                                    "Data": day_str,
                                    "Maquina": maq,
                                    "OP": op_id,
                                    "Pedido": op_item["Pedido"],
                                    "Cliente": cliente,
                                    "Produto": prod,
                                    "Sequencia": seq,
                                    "Carga_Demandada": allocated,
                                    "Quantidade_Alocada_Dia": day_qty
                                })
                                scheduled_on_days.append(current_day_search)
                            
                            current_day_search += timedelta(days=1)
                        
                        # Computar as peças agendadas de fato e as perdas de capacidade
                        qtd_agendada_real = qtd_alocada_maquina - remaining_qty
                        qtd_sem_capacidade_maquina = qtd_original_maquina - qtd_agendada_real
                        
                        # Adicionar o saldo excedente como "Sem Capacidade" na tabela
                        if qtd_sem_capacidade_maquina > 0:
                            cargas_finitas_detalhadas.append({
                                "Data": "-",
                                "Maquina": maq,
                                "OP": op_id,
                                "Pedido": op_item["Pedido"],
                                "Cliente": cliente,
                                "Produto": prod,
                                "Sequencia": seq,
                                "Carga_Demandada": 0.0,
                                "Quantidade_Alocada_Dia": qtd_sem_capacidade_maquina,
                                "Sem_Capacidade": True
                            })
                        
                        if scheduled_on_days:
                            op_start_dt = min(scheduled_on_days)
                            op_end_dt = max(scheduled_on_days)
                            datas_fim_da_seq.append(op_end_dt)
                            
                            status_entrega = "No Prazo" if op_end_dt.strftime("%Y-%m-%d") <= due_date_str else "ATRASADO"
                            
                            gantt_records.append({
                                "Tarefa": f"OP {op_id} - Seq {seq}",
                                "Maquina": maq,
                                "Início": op_start_dt.strftime("%Y-%m-%d"),
                                "Término": (op_end_dt + timedelta(days=1)).strftime("%Y-%m-%d"),
                                "OP": op_id,
                                "Cliente": cliente,
                                "Produto": prod,
                                "Quantidade": int(qtd_agendada_real),
                                "Status": status_entrega
                            })
                    
                    if datas_fim_da_seq:
                        earliest_start_date = max(datas_fim_da_seq)
                        
                    # O teto de produção para a próxima etapa é a soma do que de fato processamos na atual
                    qtd_limite_anterior = qtd_agendada_seq_total
            
            # Build daily split table records for Gantt tab table
            op_status_map = {}
            for rec in gantt_records:
                try:
                    seq_num = int(rec["Tarefa"].split("Seq ")[1])
                    op_status_map[(rec["OP"], seq_num, rec["Maquina"])] = rec["Status"]
                except:
                    pass

            gantt_table_records = []
            for c in cargas_finitas_detalhadas:
                if c.get("Sem_Capacidade", False):
                    status_val = "Sem Capacidade"
                    start_date_str = "-"
                    end_date_str = "-"
                else:
                    status_val = op_status_map.get((c["OP"], c["Sequencia"], c["Maquina"]), "No Prazo")
                    start_date_str = c["Data"]
                    end_date_str = c["Data"]
                    
                gantt_table_records.append({
                    "OP": c["OP"],
                    "Cliente": c["Cliente"],
                    "Produto": c["Produto"],
                    "Quantidade": int(c.get("Quantidade_Alocada_Dia", 0)),
                    "Maquina": c["Maquina"],
                    "Tarefa": f"OP {c['OP']} - Seq {c['Sequencia']}",
                    "Início": start_date_str,
                    "Término": end_date_str,
                    "Status": status_val
                })

            # Consolidar a carga finite calculada para o cruzamento no GRID e nos gráficos
            if cargas_finitas_detalhadas:
                cargas_validas = [c for c in cargas_finitas_detalhadas if not c.get("Sem_Capacidade", False)]
                if cargas_validas:
                    df_cargas_consolidadas = pd.DataFrame(cargas_validas).groupby(["Data", "Maquina"], as_index=False).agg({
                        "Carga_Demandada": "sum",
                        "OP": lambda x: ", ".join(sorted(list(set(x)))),
                        "Pedido": lambda x: ", ".join(sorted(list(set(x)))),
                        "Cliente": lambda x: ", ".join(sorted(list(set(x))))
                    })
                else:
                    df_cargas_consolidadas = pd.DataFrame(columns=["Data", "Maquina", "Carga_Demandada", "OP", "Pedido", "Cliente"])
            else:
                df_cargas_consolidadas = pd.DataFrame(columns=["Data", "Maquina", "Carga_Demandada", "OP", "Pedido", "Cliente"])
        
        # =====================================================================
        # 5.2 MOTOR DE SIMULAÇÃO ESTOCÁSTICA DE MONTE CARLO (GÊMEO DIGITAL / RPS)
        # =====================================================================
        stochastic_results_df = None
        avg_stochastic_otd = 100.0
        
        if tipo_planejamento == "Finito (FCS - Finite Capacity Scheduling)" and demandas_ativas and st.session_state.digital_twin_enabled:
            n_runs = int(st.session_state.digital_twin_runs)
            var_p = float(st.session_state.digital_twin_var_process)
            brk_p = float(st.session_state.digital_twin_breakdown_prob)
            mttr_val = float(st.session_state.digital_twin_mttr)
            
            op_delays_count = {op_item["OP"]: 0 for op_item in demandas_ativas}
            op_finish_dates = {op_item["OP"]: [] for op_item in demandas_ativas}
            all_runs_otd_list = []
            
            # Mapeamento rápido de capacidade nominal para Monte Carlo O(1)
            nom_cap_lookup = {
                (row.Data, row.Maquina): row.Capacidade_Liquida 
                for row in df_cap_calculada.itertuples()
            }
        
            # Executar runs de simulação
            for r_idx in range(n_runs):
                run_lates_count = 0
                maquina_ocupada_diaria_run = {}
                for dt_it in datas_periodo:
                    dt_it_str = dt_it.strftime("%Y-%m-%d")
                    maquina_ocupada_diaria_run[dt_it_str] = {m: 0.0 for m in todas_maquinas_lista}
                    
                # Simular variações diárias na capacidade líquida das máquinas (quebras)
                capacidades_mutadas_run = {}
                for dt_it in datas_periodo:
                    dt_it_str = dt_it.strftime("%Y-%m-%d")
                    capacidades_mutadas_run[dt_it_str] = {}
                    for grupo, mqs in st.session_state.recursos_padrao.items():
                        for m, _ in mqs:
                            nom_cap = nom_cap_lookup.get((dt_it_str, m), 0.0)
                            
                            if brk_p > 0 and nom_cap > 0 and np.random.rand() < (brk_p / 100.0):
                                actual_repair = np.random.uniform(1.0, mttr_val)
                                ef_m = st.session_state.definicao_eficiencias.get(m, 85.0) / 100.0
                                loss_hours = actual_repair * ef_m
                                nom_cap = max(0.0, nom_cap - loss_hours)
                            capacidades_mutadas_run[dt_it_str][m] = nom_cap
                            
                # Escalonar OPs com cargas flutuantes (máquinas alternativas em paralelo)
                for op_item in demandas_ativas_ordenadas:
                    op_id = op_item["OP"]
                    due_dt = to_date(op_item["Data_Entrega_Original"])
                    
                    # Agrupar as operações por sequência para planejar em paralelo as alternativas
                    from collections import defaultdict
                    operacoes_por_seq_run = defaultdict(list)
                    for operacao in op_item["Operacoes"]:
                        operacoes_por_seq_run[operacao["Sequencia"]].append(operacao)
                    
                    sequencias_ordenadas_run = sorted(operacoes_por_seq_run.keys())
                    earliest_dt = data_inicio
                    op_scheduled_days = []
                    
                    for seq in sequencias_ordenadas_run:
                        operacoes_da_seq = operacoes_por_seq_run[seq]
                        datas_fim_da_seq = []
                        
                        for operacao in operacoes_da_seq:
                            m_op = operacao["Maquina"]
                            
                            # Variabilidade estocástica do tempo de processamento
                            if var_p > 0:
                                var_f = np.random.normal(1.0, var_p / 100.0)
                                var_f = max(0.1, var_f)
                            else:
                                var_f = 1.0
                            carga_req_run = operacao["Carga"] * var_f
                            
                            curr_search = earliest_dt
                            scheduled_on_days_run = []
                            
                            while carga_req_run > 0.01:
                                if curr_search > data_fim:
                                    scheduled_on_days_run.append(data_fim)
                                    break
                                    
                                day_str = curr_search.strftime("%Y-%m-%d")
                                cap_liq = capacidades_mutadas_run[day_str].get(m_op, 0.0)
                                horas_ocup = maquina_ocupada_diaria_run[day_str].get(m_op, 0.0)
                                cap_rest = max(0.0, cap_liq - horas_ocup)
                                
                                if cap_rest > 0.05:
                                    alloc = min(carga_req_run, cap_rest)
                                    maquina_ocupada_diaria_run[day_str][m_op] += alloc
                                    carga_req_run -= alloc
                                    scheduled_on_days_run.append(curr_search)
                                    
                                curr_search += timedelta(days=1)
                            
                            if scheduled_on_days_run:
                                max_day = max(scheduled_on_days_run)
                                datas_fim_da_seq.append(max_day)
                                op_scheduled_days.extend(scheduled_on_days_run)
                                
                        if datas_fim_da_seq:
                            earliest_dt = max(datas_fim_da_seq)
                            
                    if op_scheduled_days:
                        final_dt = max(op_scheduled_days)
                        op_finish_dates[op_id].append(final_dt)
                        if final_dt > due_dt:
                            op_delays_count[op_id] += 1
                            run_lates_count += 1
                    else:
                        op_finish_dates[op_id].append(data_inicio)
                        
                run_otd = round(((len(demandas_ativas) - run_lates_count) / len(demandas_ativas)) * 100, 1)
                all_runs_otd_list.append(run_otd)
                
            avg_stochastic_otd = round(float(np.mean(all_runs_otd_list)), 1)
            
            # Consolidar registros de análise estocástica
            records_stoch = []
            for op_item in demandas_ativas:
                op_id = op_item["OP"]
                due_str = op_item["Data_Entrega_Original"]
                due_dt = to_date(due_str)
                dates_list = op_finish_dates[op_id]
                
                prob_atraso = round((op_delays_count[op_id] / n_runs) * 100, 1)
                
                ordinals = [d.toordinal() for d in dates_list]
                mean_ordinal = int(np.mean(ordinals))
                mean_finish_dt = datetime.fromordinal(mean_ordinal)
                
                sorted_ordinals = sorted(ordinals)
                p90_idx = int(len(sorted_ordinals) * 0.90)
                p90_idx = min(p90_idx, len(sorted_ordinals) - 1)
                p90_finish_dt = datetime.fromordinal(sorted_ordinals[p90_idx])
                
                risk_lvl = "Baixo ✅"
                if prob_atraso > 50.0:
                    risk_lvl = "Crítico 🚨"
                elif prob_atraso > 20.0:
                    risk_lvl = "Médio ⚠️"
                    
                records_stoch.append({
                    "Pedido": op_item["Pedido"],
                    "OP": op_id,
                    "Cliente": op_item["Cliente"],
                    "Produto": op_item["Produto"],
                    "Quantidade": op_item["Quantidade"],
                    "Prazo Acordado": due_str,
                    "Término Médio": mean_finish_dt.strftime("%Y-%m-%d"),
                    "Prazo de Confiança (90%)": p90_finish_dt.strftime("%Y-%m-%d"),
                    "Probabilidade de Atraso (%)": prob_atraso,
                    "Risco": risk_lvl
                })
            stochastic_results_df = pd.DataFrame(records_stoch)
        
        else:
            # PLANEJAMENTO DE CAPACIDADE INFINITA PADRÃO (CRP) - Conforme v4 original
            for op_item in demandas_ativas:
                op_id = op_item["OP"]
                due_date_str = op_item["Data_Entrega_Original"]
                for operacao in op_item["Operacoes"]:
                    cargas_simuladas.append({
                        "Data": due_date_str,
                        "Maquina": operacao["Maquina"],
                        "OP": op_id,
                        "Pedido": op_item["Pedido"],
                        "Cliente": op_item["Cliente"],
                        "Carga_Demandada": operacao["Carga"]
                    })
                    
            if cargas_simuladas:
                df_cargas_consolidadas = pd.DataFrame(cargas_simuladas).groupby(["Data", "Maquina"], as_index=False).agg({
                    "Carga_Demandada": "sum",
                    "OP": lambda x: ", ".join(set(x)),
                    "Pedido": lambda x: ", ".join(set(x)),
                    "Cliente": lambda x: ", ".join(set(x))
                })
            else:
                df_cargas_consolidadas = pd.DataFrame(columns=["Data", "Maquina", "Carga_Demandada", "OP", "Pedido", "Cliente"])
        
        # União final de dados
        df_resultado = pd.merge(df_cap_calculada, df_cargas_consolidadas, on=["Data", "Maquina"], how="left")
        df_resultado["Carga_Demandada"] = df_resultado["Carga_Demandada"].fillna(0.0)
        df_resultado["OP"] = df_resultado["OP"].fillna("-")
        df_resultado["Pedido"] = df_resultado["Pedido"].fillna("-")
        df_resultado["Cliente"] = df_resultado["Cliente"].fillna("-")
        
        # Cálculo de Ocupação e Status
        ocupacoes_lista = []
        status_lista = []
        
        for idx, row in df_resultado.iterrows():
            carga = row["Carga_Demandada"]
            cap = row["Capacidade_Liquida"]
            if cap == 0:
                if carga > 0:
                    ocupacoes_lista.append(float('inf'))
                    status_lista.append("Gargalo Crítico (Zero Cap)")
                else:
                    ocupacoes_lista.append(0.0)
                    status_lista.append("Inativo (FDS)")
            else:
                taxa = round((carga / cap) * 100, 1)
                ocupacoes_lista.append(taxa)
                if taxa > 100:
                    status_lista.append("SOBRECARGA (GARGALO!)")
                elif taxa >= 80:
                    status_lista.append("ATENÇÃO")
                elif taxa > 0:
                    status_lista.append("Ocupação Normal")
                else:
                    status_lista.append("Livre")
        
        df_resultado["Ocupacao_Pct"] = ocupacoes_lista
        df_resultado["Status"] = status_lista
        
        # =====================================================================
        # 5.3 CÁLCULO DE BUFFER PENETRATION (DDMRP - DEMAND DRIVEN MRP)
        # =====================================================================
        ddmrp_records = []
        if tipo_planejamento == "Finito (FCS - Finite Capacity Scheduling)" and gantt_records:
            df_gantt_temp = pd.DataFrame(gantt_records)
            df_op_boundaries = df_gantt_temp.groupby("OP").agg({
                "Início": "min",
                "Término": "max",
                "Cliente": "first",
                "Produto": "first"
            }).reset_index()
            
            for _, op_row in df_op_boundaries.iterrows():
                op_id = op_row["OP"]
                cliente = op_row["Cliente"]
                prod = op_row["Produto"]
                
                # Encontrar data de entrega original na planilha de demandas
                due_date_dt = None
                due_date_str = None
                if not st.session_state.demandas.empty:
                    dem_row = st.session_state.demandas[st.session_state.demandas["ORDEM"] == op_id]
                    if not dem_row.empty:
                        due_date_str = str(dem_row.iloc[0]["DATA DE ENTREGA"])
                        try:
                            due_date_dt = to_date(due_date_str)
                            if due_date_dt is None:
                                due_date_dt = data_fim
                        except:
                            due_date_dt = data_fim
                    else:
                        due_date_dt = data_fim
                        due_date_str = data_fim.strftime("%Y-%m-%d")
                else:
                    due_date_dt = data_fim
                    due_date_str = data_fim.strftime("%Y-%m-%d")
                    
                start_dt = to_date(pd.to_datetime(op_row["Início"]))
                finish_dt = to_date(pd.to_datetime(op_row["Término"])) - timedelta(days=1)
                
                total_buffer_window = (due_date_dt - data_inicio).days
                if total_buffer_window <= 0:
                    total_buffer_window = 10
                    
                consumed_buffer = (finish_dt - data_inicio).days
                if consumed_buffer < 0:
                    consumed_buffer = 0
                    
                penetration_pct = round((consumed_buffer / total_buffer_window) * 100, 1)
                
                if penetration_pct > 100.0:
                    zone = "Rompido 🖤"
                elif penetration_pct >= 85.0:
                    zone = "Crítico (Vermelho) 🚨"
                elif penetration_pct >= 50.0:
                    zone = "Atenção (Amarelo) ⚠️"
                else:
                    zone = "Saudável (Verde) ✅"
                    
                ddmrp_records.append({
                    "OP": op_id,
                    "Cliente": cliente,
                    "Produto": prod,
                    "Início Real": start_dt.strftime("%Y-%m-%d"),
                    "Término Real": finish_dt.strftime("%Y-%m-%d"),
                    "Prazo de Entrega": due_date_dt.strftime("%Y-%m-%d"),
                    "Janela Total (Dias)": total_buffer_window,
                    "Buffer Consumido (Dias)": consumed_buffer,
                    "Penetração do Buffer (%)": penetration_pct,
                    "Status do Buffer": zone
                })
        
        # =====================================================================
        # 6. LAYOUT DA TELA PRINCIPAL (INTERATIVIDADE E GRÁFICOS)
        # =====================================================================

        # Salvar resultados calculados no st.session_state
        st.session_state.sim_resultado_df = df_resultado
        st.session_state.sim_gantt_records = gantt_records
        st.session_state.sim_gantt_table_records = gantt_table_records
        st.session_state.sim_stochastic_results_df = stochastic_results_df
        st.session_state.sim_ddmrp_records = ddmrp_records
        st.session_state.sim_erros_roteiro = erros_roteiro
        st.session_state.sim_avg_stochastic_otd = avg_stochastic_otd
        st.session_state.sim_todas_maquinas_lista = todas_maquinas_lista
else:
    # Recuperar resultados salvos para renderização instantânea sem recálculos
    df_resultado = st.session_state.sim_resultado_df
    gantt_records = st.session_state.sim_gantt_records
    gantt_table_records = st.session_state.sim_gantt_table_records
    stochastic_results_df = st.session_state.sim_stochastic_results_df
    ddmrp_records = st.session_state.sim_ddmrp_records
    erros_roteiro = st.session_state.sim_erros_roteiro
    avg_stochastic_otd = st.session_state.sim_avg_stochastic_otd
    todas_maquinas_lista = st.session_state.sim_todas_maquinas_lista
st.markdown("<div class='main-title'>GCP-Molas - Gêmeo Digital, APS & DDMRP V37</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Plataforma avançada de simulação de capacidade com motor de agendamento de capacidade finita (FCS), motor estocástico (Monte Carlo) e amortecedores DDMRP</div>", unsafe_allow_html=True)

# Alertas de Roteiros ausentes
erros_roteiro = list(set(erros_roteiro))
if erros_roteiro:
    st.warning(f"⚠️ **Atenção PCP:** Os seguintes produtos importados na planilha de demanda não possuem roteiros cadastrados em seu banco de dados: **{', '.join(erros_roteiro)}**. Cadastre-os no painel lateral de roteiros para que sua carga seja calculada na simulação.")

# =====================================================================
# NAVEGAÇÃO DE ABAS POR BOTÕES INTERATIVOS INTUITIVOS
# =====================================================================
if "aba_ativa_nome" not in st.session_state:
    st.session_state.aba_ativa_nome = "📊 Resultados"

st.markdown("""
<style>
/* Estilização avançada para a barra de botões de navegação das abas */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #334155 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    height: 48px !important;
    transition: all 0.2s ease-in-out !important;
}
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border-color: #2563EB !important;
    color: #2563EB !important;
    background-color: #EFF6FF !important;
    transform: translateY(-1px);
}
div[data-testid="stHorizontalBlock"] button[kind="primary"] {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    font-size: 13px !important;
    height: 48px !important;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='font-size: 14px; font-weight: bold; color: #475569; margin-bottom: 6px;'>🎯 Painel de Navegação Módulos PCP (Clique no Botão para Acessar):</div>", unsafe_allow_html=True)

ABAS_CONFIG = [
    ("📊 Resultados", "📊 Resultados da Simulação"),
    ("📅 Gantt Interativo", "📅 Cronograma de Gantt Interativo"),
    ("🧠 Riscos & Gêmeo", "🧠 Análise de Riscos (Gêmeo Digital)"),
    ("🛑 Buffers DDMRP", "🛑 Gestão de Buffers DDMRP"),
    ("📝 Demandas OPs", "📝 Demandas Cadastradas (OPs)"),
    ("⚙️ Roteiros & Tempos", "⚙️ Roteiro e Tempos"),
    ("⏰ Horas Extras", "⏰ Lançamento de Horas Extras")
]

col_nav_1, col_nav_2, col_nav_3, col_nav_4, col_nav_5, col_nav_6, col_nav_7 = st.columns(7)
cols_nav = [col_nav_1, col_nav_2, col_nav_3, col_nav_4, col_nav_5, col_nav_6, col_nav_7]

for idx, (short_label, full_label) in enumerate(ABAS_CONFIG):
    with cols_nav[idx]:
        is_selected = (st.session_state.aba_ativa_nome == short_label)
        if st.button(
            short_label,
            key=f"btn_tab_nav_{idx}",
            type="primary" if is_selected else "secondary",
            use_container_width=True
        ):
            st.session_state.aba_ativa_nome = short_label
            st.rerun()

# Banner informativo da aba ativa selecionada
full_label_ativa = dict(ABAS_CONFIG).get(st.session_state.aba_ativa_nome, "📊 Resultados da Simulação")
st.markdown(f"""
<div style='background-color: #EFF6FF; padding: 10px 18px; border-radius: 8px; border-left: 5px solid #2563EB; font-size: 15px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;'>
    <span>📌 Módulo Ativo: {full_label_ativa}</span>
    <span style='font-size: 12px; font-weight: normal; color: #3B82F6;'>Navegação ativa em tempo real</span>
</div>
""", unsafe_allow_html=True)

# ----------------- TAB 1: RESULTADOS DA SIMULAÇÃO -----------------
if st.session_state.aba_ativa_nome == "📊 Resultados":
    # 1. Indicadores Chave de Performance (KPIs)
    gargalos_criticos = df_resultado[df_resultado["Ocupacao_Pct"] > 100].shape[0]
    dias_atencao = df_resultado[(df_resultado["Ocupacao_Pct"] >= 80) & (df_resultado["Ocupacao_Pct"] <= 100)].shape[0]
    total_horas_extras_periodo = df_resultado["Horas_Extras"].sum()
    
    # Calcular SLA / OTD em tempo real para a simulação finita
    if tipo_planejamento == "Finito (FCS - Finite Capacity Scheduling)" and gantt_records:
        df_gantt_calc = pd.DataFrame(gantt_records)
        # OTD % = (Qtd de OPs sem nenhum atraso em suas operações) / Total de OPs
        ops_com_atraso = set(df_gantt_calc[df_gantt_calc["Status"] == "ATRASADO"]["OP"])
        todas_ops = set(df_gantt_calc["OP"])
        total_ops_cont = len(todas_ops) if todas_ops else 1
        ops_no_prazo_cont = len(todas_ops - ops_com_atraso)
        otd_valor = round((ops_no_prazo_cont / total_ops_cont) * 100, 1)
        
        if st.session_state.digital_twin_enabled:
            otd_label = f"{avg_stochastic_otd}%"
            otd_sub = "OTD Estocástico (Monte Carlo)"
        else:
            otd_label = f"{otd_valor}%"
            otd_sub = f"{ops_no_prazo_cont} de {total_ops_cont} OPs no prazo (Estático)"
    else:
        otd_label = "N/A"
        otd_sub = "Disponível apenas em modo Finito (FCS)"

    # 1.1 Cálculo dos 5 KPIs Principais
    # OTIF ESTIMADO
    if tipo_planejamento == "Finito (FCS - Finite Capacity Scheduling)" and gantt_records:
        df_gantt_calc = pd.DataFrame(gantt_records)
        ops_com_atraso = set(df_gantt_calc[df_gantt_calc["Status"] == "ATRASADO"]["OP"]) if "Status" in df_gantt_calc else set()
        ops_sem_capacidade = set(c["OP"] for c in cargas_finitas_detalhadas if c.get("Sem_Capacidade", False)) if 'cargas_finitas_detalhadas' in locals() else set()
        ops_falhas = ops_com_atraso.union(ops_sem_capacidade)
        todas_ops = set(df_gantt_calc["OP"]) if not df_gantt_calc.empty else set()
        total_ops_cont = len(todas_ops) if todas_ops else 1
        ops_otif_cont = len(todas_ops - ops_falhas)
        otif_valor = round((ops_otif_cont / total_ops_cont) * 100, 1)
        otif_label = f"{otif_valor}%"
        otif_sub = f"{ops_otif_cont} de {total_ops_cont} OPs no prazo e completas"
    else:
        otif_label = "N/A"
        otif_sub = "Requer modo Finito (FCS)"

    # OCUPAÇÃO DO GARGALO
    grupo_gargalo_nome = st.session_state.get("grupo_gargalo_selecionado", "Retíficas")
    gargalo_maquinas = [m[0] for m in st.session_state.recursos_padrao.get(grupo_gargalo_nome, [])]
    df_gargalo = df_resultado[df_resultado["Maquina"].isin(gargalo_maquinas)]
    cg_sum = df_gargalo["Carga_Demandada"].sum() if not df_gargalo.empty else 0.0
    cp_sum = df_gargalo["Capacidade_Liquida"].sum() if not df_gargalo.empty else 0.0
    ocup_gargalo = round((cg_sum / cp_sum) * 100, 1) if cp_sum > 0 else 0.0
    gargalo_label = f"{ocup_gargalo}%"
    gargalo_sub = f"Grupo: {grupo_gargalo_nome} ({cg_sum:.0f}h / {cp_sum:.0f}h)"

    # OEE MÉDIO DA PLANTA
    list_ef = list(st.session_state.definicao_eficiencias.values())
    oee_medio = round(float(np.mean(list_ef)), 1) if list_ef else 80.0
    oee_label = f"{oee_medio}%"
    oee_sub = f"Média de {len(list_ef)} equipamentos"

    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
    with col_kpi1:
        st.markdown(f"""
        <div class='card-metric-normal' style='border-left: 5px solid #059669;'>
            <h5 style='margin:0; color:#065F46;'>📦 OTIF ESTIMADO</h5>
            <h2 style='margin:5px 0 0 0; color:#047857;'>{otif_label}</h2>
            <small style='color:#065F46;'>{otif_sub}</small>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi2:
        st.markdown(f"""
        <div class='card-metric-normal' style='border-left: 5px solid #2563EB;'>
            <h5 style='margin:0; color:#1E40AF;'>🎯 ON-TIME DELIVERY</h5>
            <h2 style='margin:5px 0 0 0; color:#1D4ED8;'>{otd_label}</h2>
            <small style='color:#1E40AF;'>{otd_sub}</small>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi3:
        st.markdown(f"""
        <div class='card-metric-critical' style='border-left: 5px solid #DC2626;'>
            <h5 style='margin:0; color:#991B1B;'>🔥 OCUPAÇÃO GARGALO</h5>
            <h2 style='margin:5px 0 0 0; color:#B91C1C;'>{gargalo_label}</h2>
            <small style='color:#991B1B;'>{gargalo_sub}</small>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi4:
        st.markdown(f"""
        <div class='card-metric-warning' style='border-left: 5px solid #D97706;'>
            <h5 style='margin:0; color:#92400E;'>⚙️ OEE MÉDIO PLANTA</h5>
            <h2 style='margin:5px 0 0 0; color:#B45309;'>{oee_label}</h2>
            <small style='color:#92400E;'>{oee_sub}</small>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi5:
        st.markdown(f"""
        <div class='card-metric-normal' style='border-left: 5px solid #0284C7;'>
            <h5 style='margin:0; color:#0369A1;'>⏰ TOTAL HORAS EXTRAS</h5>
            <h2 style='margin:5px 0 0 0; color:#0C4A6E;'>{total_horas_extras_periodo:.1f} h</h2>
            <small style='color:#0369A1;'>Programadas no período</small>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Gráficos de Produção (Plotly)
    col_chart1, col_chart2 = st.columns([2, 1])
    with col_chart1:
        st.markdown("### 📊 Gráfico de Ocupação de Carga vs. Capacidade por Máquina")
        df_agrupado_chart = df_resultado.groupby("Maquina", as_index=False).agg({
            "Capacidade_Liquida": "sum",
            "Carga_Demandada": "sum"
        })
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df_agrupado_chart["Maquina"],
            y=df_agrupado_chart["Capacidade_Liquida"],
            name="Capacidade Disponível (h)",
            marker_color="#0284C7"
        ))
        fig_bar.add_trace(go.Bar(
            x=df_agrupado_chart["Maquina"],
            y=df_agrupado_chart["Carga_Demandada"],
            name="Carga Alocada (h)",
            marker_color="#EF4444"
        ))
        fig_bar.update_layout(
            barmode="group",
            xaxis_tickangle=-45,
            margin=dict(l=30, r=30, t=10, b=80),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_chart2:
        st.markdown("### 🍕 Distribuição de Alertas")
        df_pizza_data = df_resultado[df_resultado["Carga_Demandada"] > 0].groupby("Status").size().reset_index(name="Count")
        cores_status_map = {
            "SOBRECARGA (GARGALO!)": "#EF4444",
            "ATENÇÃO": "#F59E0B",
            "Ocupação Normal": "#10B981",
            "Gargalo Crítico (Zero Cap)": "#7F1D1D"
        }
        fig_pie = px.pie(
            df_pizza_data,
            values="Count",
            names="Status",
            color="Status",
            color_discrete_map=cores_status_map,
            hole=0.4
        )
        fig_pie.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=380,
            showlegend=False
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    # 3. Tabela de Projeção Detalhada
    st.markdown("### 🔍 Cronograma Diário Analítico de Capacidade")
    ver_apenas_atividades = st.checkbox("Exibir somente dias com carga programada / horas extras", value=True)
    if ver_apenas_atividades:
        df_grid = df_resultado[(df_resultado["Carga_Demandada"] > 0) | (df_resultado["Horas_Extras"] > 0)]
    else:
        df_grid = df_resultado
        
    df_grid = df_grid.sort_values(by=["Data", "Grupo", "Maquina"])
    
    # Adicionando a Seção de Filtros Dinâmicos Multi-colunas
    with st.expander("🔍 Filtros Avançados por Coluna", expanded=False):
        col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
        
        # Filtro de Data e Dia da Semana
        with col_filtro1:
            datas_unicas = sorted(df_grid["Data"].unique())
            selecionar_datas = st.multiselect("Filtrar por Data", options=datas_unicas, default=[])
            
            dias_unicos = sorted(df_grid["Dia_Semana"].unique())
            selecionar_dias = st.multiselect("Filtrar por Dia da Semana", options=dias_unicos, default=[])
            
        # Filtro de Máquina e Status
        with col_filtro2:
            maquinas_unicas = sorted(df_grid["Maquina"].unique())
            selecionar_maquinas = st.multiselect("Filtrar por Máquina", options=maquinas_unicas, default=[])
            
            status_unicos = sorted(df_grid["Status"].unique())
            selecionar_status = st.multiselect("Filtrar por Status", options=status_unicos, default=[])
            
        # Filtro de OP e Pedido
        with col_filtro3:
            ops_list = []
            for item in df_grid["OP"].dropna().unique():
                for sub_item in str(item).split(","):
                    val = sub_item.strip()
                    if val and val != "-":
                        ops_list.append(val)
            ops_unicas = sorted(list(set(ops_list)))
            selecionar_ops = st.multiselect("Filtrar por Ordem (OP)", options=ops_unicas, default=[])
            
            pedidos_list = []
            for item in df_grid["Pedido"].dropna().unique():
                for sub_item in str(item).split(","):
                    val = sub_item.strip()
                    if val and val != "-":
                        pedidos_list.append(val)
            pedidos_unicos = sorted(list(set(pedidos_list)))
            selecionar_pedidos = st.multiselect("Filtrar por Pedido de Venda", options=pedidos_unicos, default=[])
            
        # Filtro de Cliente e Ocupação %
        with col_filtro4:
            clientes_list = []
            for item in df_grid["Cliente"].dropna().unique():
                for sub_item in str(item).split(","):
                    val = sub_item.strip()
                    if val and val != "-":
                        clientes_list.append(val)
            clientes_unicos = sorted(list(set(clientes_list)))
            selecionar_clientes = st.multiselect("Filtrar por Cliente", options=clientes_unicos, default=[])
            
            # Filtro numérico de faixa de Ocupação %
            max_ocup = float(df_grid["Ocupacao_Pct"].replace(float('inf'), 500).max())
            if np.isnan(max_ocup) or max_ocup == 0:
                max_ocup = 100.0
            faixa_ocupacao = st.slider("Filtrar Ocupação (%)", min_value=0.0, max_value=float(max_ocup), value=(0.0, float(max_ocup)), step=10.0)

    # Aplicar filtros ao dataframe
    df_grid_filtrado = df_grid.copy()
    
    if selecionar_datas:
        df_grid_filtrado = df_grid_filtrado[df_grid_filtrado["Data"].isin(selecionar_datas)]
        
    if selecionar_dias:
        df_grid_filtrado = df_grid_filtrado[df_grid_filtrado["Dia_Semana"].isin(selecionar_dias)]
        
    if selecionar_maquinas:
        df_grid_filtrado = df_grid_filtrado[df_grid_filtrado["Maquina"].isin(selecionar_maquinas)]
        
    if selecionar_status:
        df_grid_filtrado = df_grid_filtrado[df_grid_filtrado["Status"].isin(selecionar_status)]
        
    if selecionar_ops:
        mascara = df_grid_filtrado["OP"].apply(lambda x: any(op in str(x) for op in selecionar_ops))
        df_grid_filtrado = df_grid_filtrado[mascara]
        
    if selecionar_pedidos:
        mascara = df_grid_filtrado["Pedido"].apply(lambda x: any(ped in str(x) for ped in selecionar_pedidos))
        df_grid_filtrado = df_grid_filtrado[mascara]
        
    if selecionar_clientes:
        mascara = df_grid_filtrado["Cliente"].apply(lambda x: any(cli in str(x) for cli in selecionar_clientes))
        df_grid_filtrado = df_grid_filtrado[mascara]
        
    if faixa_ocupacao:
        min_f, max_f = faixa_ocupacao
        if max_f >= max_ocup:
            df_grid_filtrado = df_grid_filtrado[
                (df_grid_filtrado["Ocupacao_Pct"] >= min_f) | 
                (df_grid_filtrado["Ocupacao_Pct"] == float('inf'))
            ]
        else:
            df_grid_filtrado = df_grid_filtrado[
                (df_grid_filtrado["Ocupacao_Pct"] >= min_f) & 
                (df_grid_filtrado["Ocupacao_Pct"] <= max_f)
            ]

    df_grid_formatado = df_grid_filtrado.copy()
    df_grid_formatado["Ocupacao_Pct_Label"] = df_grid_formatado["Ocupacao_Pct"].apply(
        lambda x: f"{x}%" if x != float('inf') else "⚠️ INFINITO"
    )
    
    def destacar_cor_linha(row):
        pct = df_grid_formatado.loc[row.name, "Ocupacao_Pct"]
        style_color = ""
        if pct == float('inf'):
            style_color = "background-color: #FCE7F3; color: #9D174D; font-weight: bold;"
        elif pct > 100:
            style_color = "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
        elif pct >= 80:
            style_color = "background-color: #FEF3C7; color: #92400E; font-weight: bold;"
        elif pct > 0:
            style_color = "background-color: #D1FAE5; color: #065F46;"
        return [style_color] * len(row)
        
    colunas_grid = ["Data", "Dia_Semana", "Maquina", "Capacidade_Liquida", "Horas_Extras", "Carga_Demandada", "Ocupacao_Pct_Label", "Status", "OP", "Pedido", "Cliente"]
    df_grid_exibicao = df_grid_formatado[colunas_grid].copy()
    
    st.dataframe(
        df_grid_exibicao.style.apply(destacar_cor_linha, axis=1),
        use_container_width=True,
        height=400
    )

# ----------------- TAB 2: CRONOGRAMA DE GANTT INTERATIVO -----------------
elif st.session_state.aba_ativa_nome == "📅 Gantt Interativo":
    st.markdown("### 📅 Cronograma de Escalonamento de Operações (FCS)")
    if tipo_planejamento == "Infinito (MRP II / CRP)":
        st.info("💡 **Dica:** Ative o modo **Finito (FCS)** no painel lateral de configurações para que as operações sejam escalonadas de forma cronológica sem sobreposição de capacidade e para gerar o gráfico de Gantt realista.")
    else:
        if gantt_records:
            df_gantt = pd.DataFrame(gantt_records)
            df_gantt_table = pd.DataFrame(gantt_table_records) if 'gantt_table_records' in locals() else df_gantt
            
            # Desenhar Gantt com plotly timeline
            fig_gantt = px.timeline(
                df_gantt,
                x_start="Início",
                x_end="Término",
                y="Maquina",
                color="Status",
                color_discrete_map={"No Prazo": "#10B981", "ATRASADO": "#EF4444"},
                hover_data=["OP", "Cliente", "Produto", "Tarefa"],
                title="Linha do Tempo de Ocupação das Máquinas"
            )
            fig_gantt.update_yaxes(categoryorder="category ascending")
            fig_gantt.update_layout(
                height=450,
                xaxis_title="Dias de Operação",
                yaxis_title="Equipamentos",
                margin=dict(l=30, r=30, t=40, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_gantt, use_container_width=True)
            
            # Seção expansível Filtros Avançados por Coluna adicionada acima do Sequenciamento de Carga Programada
            with st.expander("🔍 Filtros Avançados por Coluna", expanded=False):
                col_g_f1, col_g_f2, col_g_f3, col_g_f4 = st.columns(4)
                
                with col_g_f1:
                    g_ops = sorted(df_gantt_table["OP"].dropna().unique())
                    sel_g_ops = st.multiselect("Filtrar por OP", options=g_ops, key="g_filter_op")
                    
                    g_clientes = sorted(df_gantt_table["Cliente"].dropna().unique())
                    sel_g_clientes = st.multiselect("Filtrar por Cliente", options=g_clientes, key="g_filter_cliente")
                    
                with col_g_f2:
                    g_produtos = sorted(df_gantt_table["Produto"].dropna().unique())
                    sel_g_produtos = st.multiselect("Filtrar por Produto", options=g_produtos, key="g_filter_produto")
                    
                    g_maquinas = sorted(df_gantt_table["Maquina"].dropna().unique())
                    sel_g_maquinas = st.multiselect("Filtrar por Máquina", options=g_maquinas, key="g_filter_maquina")
                    
                with col_g_f3:
                    g_tarefas = sorted([str(x) for x in df_gantt_table["Tarefa"].dropna().unique()])
                    sel_g_tarefas = st.multiselect("Filtrar por Tarefa/Sequência", options=g_tarefas, key="g_filter_tarefa")
                    
                    g_status = sorted(df_gantt_table["Status"].dropna().unique())
                    sel_g_status = st.multiselect("Filtrar por Status de Entrega", options=g_status, key="g_filter_status")
                    
                with col_g_f4:
                    g_inicios = sorted(df_gantt_table["Início"].dropna().unique())
                    sel_g_inicios = st.multiselect("Filtrar por Data de Início", options=g_inicios, key="g_filter_inicio")
                    
                    g_terminos = sorted(df_gantt_table["Término"].dropna().unique())
                    sel_g_terminos = st.multiselect("Filtrar por Data de Término", options=g_terminos, key="g_filter_termino")

            # Aplicar filtros dinâmicos
            df_gantt_filtrado = df_gantt_table.copy()
            if sel_g_ops:
                df_gantt_filtrado = df_gantt_filtrado[df_gantt_filtrado["OP"].isin(sel_g_ops)]
            if sel_g_clientes:
                df_gantt_filtrado = df_gantt_filtrado[df_gantt_filtrado["Cliente"].isin(sel_g_clientes)]
            if sel_g_produtos:
                df_gantt_filtrado = df_gantt_filtrado[df_gantt_filtrado["Produto"].isin(sel_g_produtos)]
            if sel_g_maquinas:
                df_gantt_filtrado = df_gantt_filtrado[df_gantt_filtrado["Maquina"].isin(sel_g_maquinas)]
            if sel_g_tarefas:
                df_gantt_filtrado = df_gantt_filtrado[df_gantt_filtrado["Tarefa"].astype(str).isin(sel_g_tarefas)]
            if sel_g_status:
                df_gantt_filtrado = df_gantt_filtrado[df_gantt_filtrado["Status"].isin(sel_g_status)]
            if sel_g_inicios:
                df_gantt_filtrado = df_gantt_filtrado[df_gantt_filtrado["Início"].isin(sel_g_inicios)]
            if sel_g_terminos:
                df_gantt_filtrado = df_gantt_filtrado[df_gantt_filtrado["Término"].isin(sel_g_terminos)]
            
            st.markdown("### 📋 Sequenciamento de Carga Programada")
            st.dataframe(df_gantt_filtrado[["OP", "Cliente", "Produto", "Quantidade", "Maquina", "Tarefa", "Início", "Término", "Status"]], use_container_width=True)
        else:
            st.write("Nenhuma operação carregada para exibição de Gantt.")

# ----------------- TAB 3: ANÁLISE DE RISCOS (GÊMEO DIGITAL) -----------------
elif st.session_state.aba_ativa_nome == "🧠 Riscos & Gêmeo":
    st.markdown("### 🧠 Gêmeo Digital e Análise de Riscos (RPS - Risk-Based Scheduling)")
    st.markdown("""
    De acordo com os conceitos de **Gêmeo Digital de Manufatura** e **RPS (Risk-Based Planning and Scheduling)** descritos na literatura de Simulação e APS (como Simio, frePPLe e SimPy), as variáveis reais de chão de fábrica não são determinísticas.
    Quebras imprevistas de equipamentos (MTBF/MTTR) e oscilações operacionais no ritmo de cada turno impactam significativamente a data de entrega final.
    
    Esta tela utiliza o **Gêmeo Digital Estocástico** do motor de sequenciamento para simular dezenas de cenários através de simulações de **Monte Carlo**, revelando a probabilidade estatística real de atraso para cada Ordem de Produção (OP).
    """, unsafe_allow_html=True)
    
    if not st.session_state.digital_twin_enabled:
        st.info("💡 **Dica de Evolução:** Ative a opção **'Habilitar Variabilidade (RPS)'** no painel lateral de configurações, ajuste os parâmetros de variabilidade e clique em **'Iniciar Simulação'** para rodar o Gêmeo Digital.")
    elif tipo_planejamento == "Infinito (MRP II / CRP)":
        st.warning("⚠️ **Aviso:** A simulação de Monte Carlo está ativa, mas requer o modo de planejamento **'Finito (FCS)'** para escalonar cronologicamente as operações e calcular os riscos de atraso.")
    else:
        if stochastic_results_df is not None and not stochastic_results_df.empty:
            # Indicadores do Gêmeo Digital
            col_st1, col_st2, col_st3 = st.columns(3)
            with col_st1:
                st.metric("🎯 OTD Estocástico Médio", f"{avg_stochastic_otd}%", help="Média de entregas no prazo calculada através de todas as simulações de Monte Carlo.")
            with col_st2:
                # OPs com alto risco (>50% de probabilidade de atraso)
                ops_alto_risco = stochastic_results_df[stochastic_results_df["Probabilidade de Atraso (%)"] > 50.0].shape[0]
                st.metric("🚨 OPs de Alto Risco", f"{ops_alto_risco} OPs", help="Quantidade de ordens com probabilidade de atraso maior que 50% devido a oscilações e quebras de máquinas.")
            with col_st3:
                st.metric("🧪 Rodadas de Monte Carlo", f"{st.session_state.digital_twin_runs} Iterações", help="Número de vezes que o motor de planejamento simulou o comportamento dinâmico do chão de fábrica.")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráficos Estocásticos
            col_chart_s1, col_chart_s2 = st.columns([2, 1])
            with col_chart_s1:
                st.markdown("#### 📊 Distribuição de Risco de Atraso por OP")
                fig_st_bar = px.bar(
                    stochastic_results_df,
                    x="OP",
                    y="Probabilidade de Atraso (%)",
                    color="Risco",
                    color_discrete_map={"Crítico 🚨": "#EF4444", "Médio ⚠️": "#F59E0B", "Baixo ✅": "#10B981"},
                    text=stochastic_results_df["Probabilidade de Atraso (%)"].apply(lambda x: f"{x}%"),
                    title="Risco Estatístico de Atraso por OP"
                )
                fig_st_bar.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_st_bar, use_container_width=True)
                
            with col_chart_s2:
                st.markdown("#### 🍕 Perfil de Risco da Carteira")
                df_risco_count = stochastic_results_df.groupby("Risco").size().reset_index(name="Quantidade")
                fig_st_pie = px.pie(
                    df_risco_count,
                    values="Quantidade",
                    names="Risco",
                    color="Risco",
                    color_discrete_map={"Crítico 🚨": "#EF4444", "Médio ⚠️": "#F59E0B", "Baixo ✅": "#10B981"},
                    hole=0.4
                )
                fig_st_pie.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
                st.plotly_chart(fig_st_pie, use_container_width=True)
                
            st.markdown("#### 📋 Matriz de Avaliação Estocástica de Prazos")
            st.markdown("""
            A coluna **'Prazo de Confiança (90%)'** representa a data de entrega segura calculada estatisticamente. 
            Em 90% dos cenários simulados de chão de fábrica, a ordem de produção estará concluída até esta data civil (incluindo desvios operacionais).
            """, unsafe_allow_html=True)
            
            def destacar_risco_stochastic(row):
                risco = row["Risco"]
                style_color = ""
                if "Crítico" in risco:
                    style_color = "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
                elif "Médio" in risco:
                    style_color = "background-color: #FEF3C7; color: #92400E; font-weight: bold;"
                else:
                    style_color = "background-color: #D1FAE5; color: #065F46;"
                return [style_color] * len(row)
                
            colunas_st_table = ["Pedido", "OP", "Cliente", "Produto", "Quantidade", "Prazo Acordado", "Término Médio", "Prazo de Confiança (90%)", "Probabilidade de Atraso (%)", "Risco"]
            st.dataframe(
                stochastic_results_df[colunas_st_table].style.apply(destacar_risco_stochastic, axis=1),
                use_container_width=True,
                height=300
            )
        else:
            st.write("Aguardando execução da simulação para exibir os indicadores estocásticos.")

# ----------------- TAB: GESTÃO DE BUFFERS DDMRP -----------------
elif st.session_state.aba_ativa_nome == "🛑 Buffers DDMRP":
    st.markdown("### 🛑 Gestão de Buffers de Estoque e de Tempo (DDMRP)")
    st.markdown("""
    O **Demand Driven MRP (DDMRP)** introduz amortecedores (buffers) coloridos para proteger a fábrica contra variabilidade e para garantir que a produção seja guiada pelo consumo real, em vez de previsões de longo prazo.
    Nesta aba, você gerencia a **Penetração do Buffer de Tempo** de cada Ordem de Produção (com base no cronograma finito) e pode **Simular e Dimensionar os Buffers de Estoque** dinâmicos dos postos críticos.
    """, unsafe_allow_html=True)
    
    if tipo_planejamento == "Infinito (MRP II / CRP)":
        st.info("💡 **Dica:** Ative o modo **Finito (FCS)** no painel lateral para planejar os buffers DDMRP de cada ordem de produção com base no cronograma de capacidade real.")
    else:
        if ddmrp_records:
            df_ddmrp = pd.DataFrame(ddmrp_records)
            
            # 1. KPIs de Buffers DDMRP
            col_b1, col_z2, col_z3, col_z4 = st.columns(4)
            with col_b1:
                b_green = df_ddmrp[df_ddmrp["Status do Buffer"].str.contains("Saudável")].shape[0]
                st.metric("🟢 Buffers Saudáveis", f"{b_green} OPs", help="Ordens concluídas bem antes da data de entrega, com buffer preservado.")
            with col_z2:
                b_yellow = df_ddmrp[df_ddmrp["Status do Buffer"].str.contains("Atenção")].shape[0]
                st.metric("🟡 Cobertura Nominal", f"{b_yellow} OPs", help="Ordens em ritmo normal de consumo de lead-time buffer.")
            with col_z3:
                b_red = df_ddmrp[df_ddmrp["Status do Buffer"].str.contains("Crítico")].shape[0]
                st.metric("🔴 Alerta Crítico", f"{b_red} OPs", help="Ordens operando com pouca margem de segurança no prazo de entrega.")
            with col_z4:
                b_broken = df_ddmrp[df_ddmrp["Status do Buffer"].str.contains("Rompido")].shape[0]
                st.metric("🖤 Buffers Rompidos", f"{b_broken} OPs", help="Ordens programadas para entrega após o prazo acordado.")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 2. Gráfico Plotly de Penetração de Buffers por OP
            st.markdown("### 📊 Gráfico de Penetração de Buffer por Ordem de Produção")
            df_ddmrp_sorted = df_ddmrp.sort_values(by="Penetração do Buffer (%)", ascending=False)
            
            # Criar barra horizontal
            fig_ddmrp_bar = px.bar(
                df_ddmrp_sorted,
                x="Penetração do Buffer (%)",
                y="OP",
                color="Status do Buffer",
                color_discrete_map={
                    "Saudável (Verde) ✅": "#10B981",
                    "Atenção (Amarelo) ⚠️": "#F59E0B",
                    "Crítico (Vermelho) 🚨": "#EF4444",
                    "Rompido 🖤": "#4B5563"
                },
                hover_data=["Cliente", "Produto", "Prazo de Entrega", "Término Real"],
                orientation="h",
                title="Penetração de Buffer de Tempo por OP (Limite Crítico = 100%)"
            )
            fig_ddmrp_bar.add_vline(x=100.0, line_dash="dash", line_color="red", annotation_text="Prazo de Entrega (100%)")
            fig_ddmrp_bar.update_layout(height=max(180, len(df_ddmrp_sorted)*40), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_ddmrp_bar, use_container_width=True)
            
            # 3. Tabela Detalhada com Estilos
            st.markdown("### 📋 Detalhamento dos Buffers DDMRP por OP")
            
            def destacar_buffers_cores(row):
                status_b = row["Status do Buffer"]
                style_color = ""
                if "Saudável" in status_b:
                    style_color = "background-color: #D1FAE5; color: #065F46;"
                elif "Atenção" in status_b:
                    style_color = "background-color: #FEF3C7; color: #92400E;"
                elif "Crítico" in status_b:
                    style_color = "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
                else: # Rompido
                    style_color = "background-color: #E2E8F0; color: #1E293B; font-weight: bold; text-decoration: line-through;"
                return [style_color] * len(row)
                
            st.dataframe(
                df_ddmrp[["OP", "Cliente", "Produto", "Início Real", "Término Real", "Prazo de Entrega", "Janela Total (Dias)", "Buffer Consumido (Dias)", "Penetração do Buffer (%)", "Status do Buffer"]]                .style.apply(destacar_buffers_cores, axis=1),                use_container_width=True,                height=300            )
        else:
            st.write("Aguardando execução do sequenciamento fino para exibir os buffers.")
            
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📐 Dimensionamento de Buffer de Estoque Desacoplado (DDMRP)")
    st.markdown("De acordo com a metodologia DDMRP, os pulmões de estoque são colocados estrategicamente nos pontos de desacoplamento da planta e calculados em três zonas de dimensionamento:")
    
    col_dim1, col_dim2 = st.columns([1, 1])
    with col_dim1:
        selected_resource_ddmrp = st.selectbox(
            "Selecione o Ponto de Desacoplamento / Recurso Crítico",
            options=["Forno 6m C01", "Forno 6m C02", "Retífica Grande 152 - Lado A", "Retífica Grande 152 - Lado B", "Qualidade", "Pintura Epoxi"],
            key="ddmrp_res_select"
        )
        adu_val = st.slider("Consumo Médio Diário (ADU) - Unidades/Dia", min_value=10, max_value=500, value=150, step=10, key="adu_slider")
        dlt_val = st.slider("Lead Time Desacoplado (DLT) - Dias", min_value=1, max_value=15, value=4, step=1, key="dlt_slider")
        vf_val = st.slider("Fator de Variabilidade do Processo (VF)", min_value=10, max_value=80, value=30, step=5, key="vf_slider") / 100.0
        lt_factor = st.slider("Fator de Lead Time (LTF) - Proporcional à Categoria", min_value=10, max_value=100, value=40, step=5, key="ltf_slider") / 100.0
        
    with col_dim2:
        yellow_zone = adu_val * dlt_val
        red_base = yellow_zone * lt_factor
        red_safety = red_base * vf_val
        total_red = round(red_base + red_safety, 1)
        green_zone = round(yellow_zone * lt_factor, 1)
        total_buffer = round(total_red + yellow_zone + green_zone, 1)
        
        st.markdown(f"#### 📐 Tamanho Total do Buffer de Estoque: **{total_buffer} Unidades**")
        st.write(f"Este buffer atua como amortecedor dinâmico para o recurso **{selected_resource_ddmrp}**, garantindo a proteção do fluxo produtivo mesmo em caso de variações severas de fornecimento.")
        
        col_z1, col_z2, col_z3 = st.columns(3)
        with col_z1:
            st.metric("🔴 Zona Vermelha (Segurança)", f"{total_red} Unid.")
        with col_z2:
            st.metric("🟡 Zona Amarela (Cobertura)", f"{yellow_zone} Unid.")
        with col_z3:
            st.metric("🟢 Zona Verde (Lote)", f"{green_zone} Unid.")
            
        fig_profile = go.Figure()
        fig_profile.add_trace(go.Bar(
            y=["Pulmão DDMRP"],
            x=[total_red],
            name="Zona Vermelha (Segurança)",
            orientation='h',
            marker=dict(color='#EF4444')
        ))
        fig_profile.add_trace(go.Bar(
            y=["Pulmão DDMRP"],
            x=[yellow_zone],
            name="Zona Amarela (Cobertura)",
            orientation='h',
            marker=dict(color='#F59E0B')
        ))
        fig_profile.add_trace(go.Bar(
            y=["Pulmão DDMRP"],
            x=[green_zone],
            name="Zona Verde (Lote/Ciclo)",
            orientation='h',
            marker=dict(color='#10B981')
        ))
        fig_profile.update_layout(
            barmode='stack',
            height=180,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_profile, use_container_width=True)

# ----------------- TAB 4: DEMANDAS ATIVAS NO PLANEJAMENTO -----------------
elif st.session_state.aba_ativa_nome == "📝 Demandas OPs":
    st.markdown("### 📋 Planilha de Importação da Demanda")
    st.dataframe(st.session_state.demandas, use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📝 Adicionar Demanda Avulsa Manual")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        manual_pv = st.text_input("Pedido de Venda", value="PV-2000")
        manual_op = st.text_input("Ordem de Produção", value="0105294-010")
    with col_d2:
        manual_prod = st.text_input("Produto (Código)", value="284269")
        manual_cli = st.text_input("Cliente", value="MRS Logística S/A")
    with col_d3:
        manual_qtd = st.number_input("Quantidade de Molas", min_value=1, value=100)
        manual_data = st.date_input("Data de Entrega", value=data_inicio, format="DD/MM/YYYY")
        
    if st.button("🚀 Confirmar Lançamento de Demanda", use_container_width=True):
        nova_row = pd.DataFrame([{
            "PEDIDO DE VENDA": manual_pv,
            "ORDEM": manual_op,
            "PRODUTO": manual_prod,
            "CLIENTE": manual_cli,
            "QUANTIDADE": manual_qtd,
            "DATA DE ENTREGA": manual_data.strftime("%Y-%m-%d")
        }])
        st.session_state.demandas = pd.concat([st.session_state.demandas, nova_row], ignore_index=True)
        st.session_state.simulacao_disparada = False # Resetar
        st.success("Nova demanda adicionada com sucesso! Clique em 'Iniciar Simulação' para atualizar.")
        st.rerun()
        
    if st.button("🗑️ Limpar Banco de Dados de Demandas"):
        st.session_state.demandas = pd.DataFrame(columns=["PEDIDO DE VENDA", "ORDEM", "PRODUTO", "CLIENTE", "QUANTIDADE", "DATA DE ENTREGA"])
        st.session_state.simulacao_disparada = False # Resetar
        st.success("Toda a carga do sistema foi reinicializada. Clique em 'Iniciar Simulação' para atualizar.")
        st.rerun()

# ----------------- TAB 5: CADASTRO E VISUALIZAÇÃO DE ROTEIROS -----------------
elif st.session_state.aba_ativa_nome == "⚙️ Roteiros & Tempos":
    st.markdown("### 📋 Tabela de Roteiros e Tempos do Banco de Dados")
    st.info("Aqui são definidas as sequências e produtividades das molas (unidades por hora) para cada máquina. A carga diária é calculada dividindo a quantidade pedida pela produtividade por hora. As operações estão organizadas sequencialmente. Você pode editar diretamente na tabela abaixo, adicionar ou excluir linhas.")
    
    df_roteiros_editado = st.data_editor(
        st.session_state.roteiros_tempos,
        num_rows="dynamic",
        key="roteiros_editor_central",
        use_container_width=True
    )
    if not df_roteiros_editado.equals(st.session_state.roteiros_tempos):
        st.session_state.roteiros_tempos = df_roteiros_editado
        st.session_state.simulacao_disparada = False # Resetar para forçar novo clique
        st.success("Alterações salvas! Clique em 'Iniciar Simulação' para atualizar.")
        st.rerun()

    st.markdown("---")
    st.markdown("### ➕ Inclusão Avulsa de Roteiro")
    col_r_add1, col_r_add2 = st.columns(2)
    with col_r_add1:
        add_r_prod = st.text_input("Mola/Produto (Código)", key="add_r_prod_input")
        add_r_seq = st.number_input("Sequência Numérica", min_value=1, value=10, step=10, key="add_r_seq_input")
    with col_r_add2:
        # todas_maquinas_lista contains all current machines
        add_r_maq = st.selectbox("Equipamento / Máquina", options=todas_maquinas_lista, key="add_r_maq_input")
        add_r_prod_hora = st.number_input("Produtividade (Peças/Hora)", min_value=0.1, value=50.0, step=5.0, key="add_r_prod_hora_input")
        
    add_r_btn = st.button("🚀 Confirmar Lançamento de Roteiro", use_container_width=True)
    if add_r_btn:
        if add_r_prod.strip():
            prod_clean = add_r_prod.strip()
            # Ver se ja existe essa combinacao
            exists = st.session_state.roteiros_tempos[
                (st.session_state.roteiros_tempos["Produto"] == prod_clean) & 
                (st.session_state.roteiros_tempos["Sequencia"] == add_r_seq) & 
                (st.session_state.roteiros_tempos["Equipamento"] == add_r_maq)
            ]
            if not exists.empty:
                # Atualizar o Prod_Hora
                st.session_state.roteiros_tempos.loc[
                    (st.session_state.roteiros_tempos["Produto"] == prod_clean) & 
                    (st.session_state.roteiros_tempos["Sequencia"] == add_r_seq) & 
                    (st.session_state.roteiros_tempos["Equipamento"] == add_r_maq),
                    "Prod_Hora"
                ] = add_r_prod_hora
                st.success(f"Roteiro atualizado para o Produto {prod_clean} na sequência {add_r_seq}!")
            else:
                # Adicionar nova row
                new_row_df = pd.DataFrame([{
                    "Produto": prod_clean,
                    "Sequencia": int(add_r_seq),
                    "Equipamento": add_r_maq,
                    "Prod_Hora": float(add_r_prod_hora)
                }])
                st.session_state.roteiros_tempos = pd.concat([st.session_state.roteiros_tempos, new_row_df], ignore_index=True)
                st.success(f"Novo roteiro inserido para o Produto {prod_clean} na sequência {add_r_seq} com sucesso!")
                
            st.session_state.simulacao_disparada = False
            st.rerun()
        else:
            st.warning("Insira o código do produto/mola.")

    st.markdown("---")
    if st.button("🗑️ Limpar Banco de Dados de Roteiros e Tempos", type="primary", use_container_width=True):
        st.session_state.roteiros_tempos = pd.DataFrame(columns=["Produto", "Sequencia", "Equipamento", "Prod_Hora"])
        st.session_state.simulacao_disparada = False
        st.success("Toda a base de Roteiros e Tempos foi limpa com sucesso! Adicione ou faça o upload de novos roteiros para simular.")
        st.rerun()

# ----------------- TAB 6: LANÇAMENTO DE HORAS EXTRAS -----------------
elif st.session_state.aba_ativa_nome == "⏰ Horas Extras":
    st.markdown("### ⏰ Programar Horas Extras Preventivas")
    st.info("Utilize este espaço para responder aos alertas de gargalo diários. Lançamentos de horas extras em finais de semana ou feriados ativam a máquina especificamente para essas datas.")
    col_he1, col_he2, col_he3 = st.columns(3)
    with col_he1:
        input_he_data = st.date_input("Data da Hora Extra", value=data_inicio, format="DD/MM/YYYY")
    with col_he2:
        input_he_maquina = st.selectbox("Selecione a Máquina para Horas Extras", options=todas_maquinas_lista)
    with col_he3:
        input_he_horas = st.number_input("Total de Horas Extras (h)", min_value=0.0, max_value=12.0, value=4.0, step=0.5)
        
    if st.button("⚡ Programar Horas Extras no Calendário", use_container_width=True):
        chave_he_state = f"{input_he_data.strftime('%Y-%m-%d')}_{input_he_maquina}"
        st.session_state.horas_extras[chave_he_state] = input_he_horas
        st.session_state.simulacao_disparada = False # Resetar
        st.success(f"Foram programadas {input_he_horas}h extras na máquina '{input_he_maquina}' em {input_he_data.strftime('%d/%m/%Y')}! Clique em 'Iniciar Simulação' para atualizar.")
        st.rerun()
        
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📊 Log de Horas Extras Ativas no Período")
    if st.session_state.horas_extras:
        linhas_he = []
        for key, val in st.session_state.horas_extras.items():
            if val > 0:
                dt_he, maq_he = key.split("_")
                linhas_he.append({"Data": dt_he, "Máquina": maq_he, "Horas Extras": val})
        if linhas_he:
            st.dataframe(pd.DataFrame(linhas_he).sort_values(by="Data"), use_container_width=True)
        else:
            st.write("Nenhuma hora extra cadastrada.")
    else:
        st.write("Nenhuma hora extra cadastrada.")
        
    if st.button("🗑️ Limpar Log de Horas Extras"):
        st.session_state.horas_extras = {}
        st.session_state.simulacao_disparada = False # Resetar
        st.success("Todas as horas extras foram removidas! Clique em 'Iniciar Simulação' para atualizar.")
        st.rerun()
