import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc

# URL do VOSviewer
url = "https://tinyurl.com/233s5fwm"

# Carregar os dados para o gráfico de barras
termos_titulos = pd.read_csv('dados_streamlit/termos_titulos.csv')

# Definir as cores customizadas
custom_colors = [
    "#003f5b", "#2b4b7d", "#5f5195", "#98509d", 
    "#cc4c91", "#f25375", "#ff6f4e", "#ff9913"]

# Criar o gráfico de barras interativo para visualizar os 10 primeiros termos
fig = px.bar(
    termos_titulos.head(10),
    x='Count',
    y='Term',
    orientation='h',
    labels={'Count': 'Frequência', 'Term': 'Termo'},
    color='Count',
    color_continuous_scale=custom_colors
)

# Ajustar o layout do gráfico
fig.update_layout(
    xaxis_title='Frequência',
    yaxis_title='Termos',
    yaxis=dict(autorange='reversed'),  # Inverter a ordem dos termos no eixo y
    height=500,  # Aumentar a altura do gráfico
    margin=dict(l=30, r=30, t=40, b=40)  # Ajustar margens para dar mais espaço
)

# Layout do Streamlit
st.set_page_config(
    page_title="Dashboard - Usos de Data Science e Big Data no Planeamento Urbano",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
# Caminho base (diretório onde o script está a ser executado)
base = os.path.dirname(os.path.abspath(__file__))

# Caminho completo para o ficheiro
file = os.path.join(base, "dados_streamlit", "df_combined.csv")

# Verificar se o ficheiro existe antes de abrir
if os.path.exists(file):
    # Ler o ficheiro CSV com pandas
    df_all = pd.read_csv(file)
    print("Ficheiro carregado com sucesso!")
else:
    print(f"Ficheiro não encontrado: {file}")
    
# Supondo que 'df_all' contenha os dados com as colunas 'year', 'affiliation-country', e 'count'
df_all['count'] = 1  # Inicializar com 1 para representar cada artigo
df_all = df_all.groupby(['ano', 'affiliation-country'], as_index=False).agg({'count': 'sum'})

# Encontrar o valor máximo de 'count' em qualquer país ao longo de todos os anos
max_count = df_all['count'].max()

# Criar o mapa interativo
fig1 = px.choropleth(
    df_all,
    locations="affiliation-country",  # Nome do país
    locationmode="country names",  # Usando nomes de países
    color="count",  # Usando a coluna 'count' para a cor
    color_continuous_scale=custom_colors,
    hover_name="affiliation-country",  # Para exibir o nome do país
    animation_frame="ano",  # Para animar o mapa ao longo dos anos
    range_color=[0, max_count]  # Define a escala de cor de 0 até o valor máximo fixo
)

# Ajustar o layout do mapa com fundo preto
fig1.update_layout(
    geo=dict(
        showframe=False, 
        showcoastlines=True, 
        projection_type='natural earth',
        bgcolor="black"  # Define o fundo do mapa como preto
    ),
    coloraxis_colorbar=dict(title="Número de Artigos"),
    paper_bgcolor="black",  # Fundo da área de papel também preto
    plot_bgcolor="black"    # Fundo do gráfico também preto
)
base = os.path.dirname(os.path.abspath(__file__))

# Caminho completo para o ficheiro
file = os.path.join(base, "dados_streamlit", "df_authors.csv")

# Verificar se o ficheiro existe antes de abrir
if os.path.exists(file):
    # Ler o ficheiro CSV com pandas
    df_authors = pd.read_csv(file)
    print("Ficheiro carregado com sucesso!")
else:
    print(f"Ficheiro não encontrado: {file}")
    
# Definir as colunas obrigatórias
# Definição das colunas e dados (ajustar conforme necessário)
required_columns = ['author', 'n_artigos_pub', 'affiliation', 'country']
if not all(column in df_authors.columns for column in required_columns):
    raise ValueError(f"O DataFrame deve conter as colunas: {required_columns}")

# Criar uma coluna com as siglas das instituições
df_authors['institution_labels_simp'] = df_authors['affiliation'].apply(lambda x: ''.join([word[0].upper() for word in x.split()]))

# Selecionar os 10 autores com mais publicações
top_authors_df = df_authors.nlargest(10, 'n_artigos_pub')

# Preparar os dados para o diagrama de Sankey
authors = top_authors_df['author'].tolist()
affiliations = top_authors_df['affiliation'].tolist()
countries = top_authors_df['country'].dropna().unique().tolist()
institution_labels_simp = [df_authors[df_authors['affiliation'] == inst]['institution_labels_simp'].values[0] for inst in affiliations]

# Criar labels para países, instituições (simplificadas) e top 10 autores
labels = countries + institution_labels_simp + authors

# Criar dicionários para mapear os índices
country_indices = {country: i for i, country in enumerate(countries)}
affiliation_indices = {affiliation: i + len(countries) for i, affiliation in enumerate(institution_labels_simp)}
author_indices = {author: i + len(countries) + len(institution_labels_simp) for i, author in enumerate(authors)}

# Criar listas para as fontes e destinos
sources = []
targets = []
values = []
link_colors = []

# Definir cores para os países
custom_colors = [
    "#5f5195", "#98509d", 
    "#cc4c91", "#f25375",
    "#ff6f4e", "#ff9913"
]
country_colors = custom_colors[:len(countries)]

# Adicionar relações país -> instituição
for i, row in top_authors_df.iterrows():
    sources.append(country_indices[row['country']])
    targets.append(affiliation_indices[institution_labels_simp[affiliations.index(row['affiliation'])]])
    values.append(row['n_artigos_pub'])
    link_colors.append(country_colors[countries.index(row['country'])])

# Adicionar relações instituição -> autor
for i, row in top_authors_df.iterrows():
    sources.append(affiliation_indices[institution_labels_simp[affiliations.index(row['affiliation'])]])
    targets.append(author_indices[row['author']])
    values.append(row['n_artigos_pub'])
    # Criar uma cor mais clara para o autor
    base_color = pc.hex_to_rgb(country_colors[countries.index(row['country'])])
    lighter_color = pc.find_intermediate_color(base_color, (255, 255, 255), 0.5)
    lighter_color = f"rgb{lighter_color}"
    link_colors.append(lighter_color)

# Criar customdata para incluir o nome completo e o número de artigos
customdata = []
for label in labels:
    if label in authors:
        count = top_authors_df[top_authors_df['author'] == label]['n_artigos_pub'].values[0]
        customdata.append(f"{label}<br>Number of articles: {count}")
    elif label in institution_labels_simp:
        full_name = affiliations[institution_labels_simp.index(label)]
        count = top_authors_df[top_authors_df['affiliation'] == full_name]['n_artigos_pub'].sum()
        customdata.append(f"{full_name}<br>Number of articles: {count}")
    else:
        count = top_authors_df[top_authors_df['country'] == label]['n_artigos_pub'].sum()
        customdata.append(f"{label}<br>Number of articles: {count}")

# Criar o diagrama de Sankey
fig2 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=20,  # Espessura dos nós ajustada
        line=dict(color="white", width=0),  # Remover o contorno dos nós (sem outline)
        label=labels,
        customdata=customdata,  # Texto completo para o pop-up
        hovertemplate='%{customdata}<extra></extra>',  # Formato do pop-up
        color="#003f5c",  # Cor dos nós ajustada para cinza
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color=link_colors
    )
)])

# Ajuste do layout para tornar o gráfico mais clean e bonito
fig2.update_layout(
    hovermode='x',
    font=dict(size=14, color='Black', family="Arial"),  # Aumentar o tamanho da fonte
    plot_bgcolor='black',  # Fundo preto
    paper_bgcolor='black',  # Fundo da página também preto
    width=700,  # Largura do gráfico mais ajustada
    height=300,  # Altura ajustada para um aspecto mais equilibrado
    showlegend=False  # Remover a legenda para não sobrecarregar o gráfico
)


# CSS styling para o fundo da rede
st.markdown("""
<div style="background-color: black; padding: 20px; border-radius: 5px; text-align: left;">
    <h1 style="font-size: 40px; font-weight: bold; color: #bc5090;">Análise de Artigos Científicos da área das Ciências Sociais</h1>
    <h2 style="font-size: 32px; font-weight: normal; color: #ffa600;">Data Science e Big Data, aplicadas ao Planeamento Urbano</h2>
</div>

<style>
/* Estilo do iframe da rede com fundo preto */
iframe {
    background-color: black;
}
</style>
""", unsafe_allow_html=True)


# Criar a aba
tab1, tab2 = st.tabs([" 📈 Análise Bibliográfica", " 📊 Análise Bibliométrica"])

# Aba 1: Análise Bibliográfica
with tab1:
    st.markdown("""
<div style="background-color: #333; padding: 10px; border-radius: 5px; color: white; font-size: 16px; margin-bottom: 20px;">
    Query da pesquisa SCOPUS: Data Science OR Big Data AND (Urban Planning OR Urban Management OR Spatial Planning OR Urban Development), limited to Social Sciences
</div>
""", unsafe_allow_html=True)

    # Dividir a tela em três colunas, conforme exemplo fornecido
    col = st.columns((5, 5), gap='medium')

    with col[0]:
        st.markdown('#### Rede bibliométrica de co-ocorrência de keywords dos autores')
        # Incorporar o conteúdo do VOSviewer diretamente com fundo preto
        st.components.v1.html(f'<iframe src="{url}" width="100%" height="600px" style="border: 0px solid #ddd; max-width: 1000px; min-height: 500px; background-color: black;"></iframe>', height=600)
        st.markdown('### País de publicação dos artigos')
        st.plotly_chart(fig1, use_container_width=True)

    with col[1]:
        st.markdown('#### Top 10: Termos mais recorrentes nos títulos dos artigos')
        # Exibir o gráfico de barras
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('###   ')
        st.markdown('###   ')
        st.markdown('### TOP 10 de Autores, por nº de publicações')
        st.plotly_chart(fig2)

# Aba 2: Análise Bibliométrica
with tab2:
    st.title("📈 Análise Bibliométrica")
    st.write("Nesta aba, apresentamos métricas e análises bibliométricas com base nos artigos selecionados.")
