import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# 1. CONFIGURAÇÃO E CSS PREMIUM (O "Drip" do Dashboard)
st.set_page_config(page_title="Intelligence Unit | Turnover", layout="wide", page_icon="👁️‍🗨️")

# Injeção de CSS para matar a cara de Streamlit e criar um visual SaaS Dark Mode
st.markdown("""
    <style>
    /* Sumir com o Header, Footer e Menu Hamburger nativos */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Reduzir o espaço em branco inútil no topo */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }

    /* Estilizando os cards de métricas estilo Glassmorphism/Neon */
    div[data-testid="metric-container"] {
        background-color: #1a1a1b;
        border-radius: 8px;
        padding: 15px 20px;
        border-left: 4px solid #00ffcc;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
    }

    /* Estilizando as Abas para parecerem botões de sistema */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 6px 6px 0px 0px;
        background-color: #1e1e1f;
        border: 1px solid #333;
        border-bottom: none;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2b2b2d;
        border-bottom: 3px solid #00ffcc;
        color: #00ffcc !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. AUTENTICAÇÃO BLINDADA
with open('auth.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login(location='main')

# --- O SHOW COMEÇA AQUI ---
if st.session_state["authentication_status"]:
    # 3. CARREGAMENTO DE ASSETS
    @st.cache_resource
    def load_assets():
        raiz = Path(__file__).resolve().parent
        caminho_dados = raiz / "Data" / "Processed" / "obt_turnover_preparada.csv"
        caminho_modelo = raiz / "Models" / "lr_turnover_model.pkl"

        if not caminho_dados.exists() or not caminho_modelo.exists():
            return None, None

        df = pd.read_csv(caminho_dados)
        modelo = joblib.load(caminho_modelo)
        return df, modelo


    df, modelo = load_assets()

    if df is not None:
        df['Status'] = df['target_pediu_demissao'].map({0: 'Ativo', 1: 'Demitido'})
        CORES_STATUS = {'Ativo': '#00ffcc', 'Demitido': '#ff4b4b'}

        # --- SIDEBAR PROFISSIONAL (MENU & FILTROS) ---
        authenticator.logout('Desconectar', 'sidebar')
        st.sidebar.markdown(f"**👤 Operador:** `{st.session_state['name']}`")
        st.sidebar.markdown("---")

        st.sidebar.markdown("### 🎛️ Filtros Globais")

        # Filtro de Departamento
        lista_deps = ["Todos"] + sorted(list(df['departamento_nome_api'].dropna().unique()))
        filtro_dep = st.sidebar.selectbox("Departamento", lista_deps)

        # Filtro de Perfil Comportamental
        lista_perfis = ["Todos"] + sorted(list(df['perfil_comportamental'].dropna().unique()))
        filtro_perfil = st.sidebar.selectbox("Perfil Comportamental", lista_perfis)

        st.sidebar.markdown("---")
        st.sidebar.caption("S-Rank Intelligence Unit © 2026")

        # --- LÓGICA DE FILTRAGEM ---
        df_filtered = df.copy()
        if filtro_dep != "Todos":
            df_filtered = df_filtered[df_filtered['departamento_nome_api'] == filtro_dep]
        if filtro_perfil != "Todos":
            df_filtered = df_filtered[df_filtered['perfil_comportamental'] == filtro_perfil]

        # --- CABEÇALHO DO DASHBOARD ---
        st.title("🛡️ Unidade de Inteligência de Retenção")

        # Renderiza KPIs apenas se houver dados após o filtro
        if not df_filtered.empty:
            total_colab = len(df_filtered)
            ativos = len(df_filtered[df_filtered['Status'] == 'Ativo'])
            demitidos = len(df_filtered[df_filtered['Status'] == 'Demitido'])
            taxa_turnover = (demitidos / total_colab) * 100 if total_colab > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Headcount", total_colab)
            c2.metric("Ativos", ativos)
            c3.metric("Evasões", demitidos)
            c4.metric("Turnover", f"{taxa_turnover:.1f}%", delta="Crítico" if taxa_turnover > 15 else "Normal",
                      delta_color="inverse")

            st.markdown("<br>", unsafe_allow_html=True)

            # --- NAVEGAÇÃO POR ABAS ---
            tab_visao, tab_grana, tab_demo, tab_risco = st.tabs([
                "🗺️ Panorama", "💸 Análise Salarial", "🧬 Demografia", "🚨 Target List"
            ])


            # FUNÇÃO PRA LIMPAR O FUNDO DOS GRÁFICOS
            def clean_layout(fig):
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#333333')
                )
                return fig


            with tab_visao:
                fig_sun = px.sunburst(
                    df_filtered, path=['departamento_nome_api', 'perfil_comportamental', 'Status'],
                    color='target_pediu_demissao', color_continuous_scale=['#00ffcc', '#ff4b4b'],
                    title="Mapeamento de Evasão Organizacional"
                )
                fig_sun.update_layout(margin=dict(t=40, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_sun, use_container_width=True)

            with tab_grana:
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    fig_vio = px.violin(
                        df_filtered, y="salario_contratual", x="Status", color="Status",
                        box=True, points="all", color_discrete_map=CORES_STATUS, title="Distribuição Salarial"
                    )
                    st.plotly_chart(clean_layout(fig_vio), use_container_width=True)

                with col_g2:
                    fig_tempo = px.histogram(
                        df_filtered, x="meses_de_casa", color="Status", barmode="overlay",
                        marginal="box", color_discrete_map=CORES_STATUS, nbins=24, title="Evasão vs Tempo de Casa"
                    )
                    st.plotly_chart(clean_layout(fig_tempo), use_container_width=True)

            with tab_demo:
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    if 'genero' in df_filtered.columns:
                        fig_gen = px.histogram(
                            df_filtered, x="genero", color="Status", barnorm="percent", text_auto='.1f',
                            color_discrete_map=CORES_STATUS, title="Saída por Gênero (%)"
                        )
                        st.plotly_chart(clean_layout(fig_gen), use_container_width=True)
                    else:
                        st.info("💡 Coluna 'genero' não encontrada.")

                with col_d2:
                    fig_age = px.histogram(
                        df_filtered, x="idade", color="Status", barmode="group",
                        color_discrete_map=CORES_STATUS, nbins=15, title="Evasão por Faixa Etária"
                    )
                    st.plotly_chart(clean_layout(fig_age), use_container_width=True)

            with tab_risco:
                st.markdown("### 🚨 Painel de Ação RH (Alto Risco)")
                df_ativos = df_filtered[df_filtered['target_pediu_demissao'] == 0].copy()

                if not df_ativos.empty:
                    df_ativos['is_perfil_Nao_Mapeado'] = df_ativos['perfil_comportamental'].apply(
                        lambda x: 1 if 'Não Mapeado' in str(x) else 0)
                    df_ativos['is_dep_RELACIONAMENTO'] = df_ativos['departamento_nome_api'].apply(
                        lambda x: 1 if x == 'RELACIONAMENTO' else 0)

                    cols = ['meses_de_casa', 'salario_contratual', 'idade', 'qtd_dependentes', 'is_perfil_Nao_Mapeado',
                            'is_dep_RELACIONAMENTO']

                    probs = modelo.predict_proba(df_ativos[cols])[:, 1]
                    df_ativos['Risco (%)'] = (probs * 100).round(2)

                    res = df_ativos[
                        ['colaborador_sk', 'departamento_nome_api', 'perfil_comportamental', 'Risco (%)']].sort_values(
                        'Risco (%)', ascending=False)

                    st.dataframe(
                        res.style.background_gradient(subset=['Risco (%)'], cmap='Reds'),
                        use_container_width=True, height=400, hide_index=True
                    )
                else:
                    st.success("Nenhum colaborador ativo encontrado para este filtro. Área segura!")
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        st.error("Falha na infraestrutura de dados. Verifique a pipeline S-Rank.")

elif st.session_state["authentication_status"] is False:
    st.error('Acesso Negado.')
elif st.session_state["authentication_status"] is None:
    st.warning('Aguardando credenciais.')