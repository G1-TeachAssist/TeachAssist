from faker import Faker
import pandas as pd
import numpy as np
import random
import dash
import datetime
import re
import plotly.graph_objs as go
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Configurar o pandas para exibir todas as linhas e colunas
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# [OPCIONAL] Importar cada DataFrame ja criado
professor_df = pd.read_csv('professor_df.csv')
aluno_df =pd.read_csv('aluno_df.csv')
disciplina_df = pd.read_csv('disciplina_df.csv')
turma_df = pd.read_csv('turma_df.csv')
notas_df = pd.read_csv('notas_df.csv')
media_final_df = pd.read_csv('media_final_df.csv')

# KPIS sem nenhum filtro

# Nota média de todos os alunos por disciplina (com notas completas)
media_total = notas_df.agg(media_final=('nota', 'mean')).reset_index()['nota'].iloc[0]

# Contar o número de disciplinas e alunos
num_disciplinas_total = len(turma_df['disciplina_id'].unique())
num_alunos_total = len(turma_df['aluno_id'].unique())

# Turmas que faltam nota
disciplinas_pendentes = len(turma_df[turma_df['status'] != 'Finalizada']['disciplina_id'].unique())

# Especifica um arquivo CSS externo contendo uma família de fontes que deseja carregar em seu aplicativo
external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

# Inicializar a aplicação Dash
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Layout completo da aplicação
app.layout = html.Div([
    
    # Título
    html.Div([
        html.H1("Dashboard", className="header-title"),
        # html.P("Análise de notas escolares para apoiar os professores na verificação de assuntos/disciplinas que precisam ser melhor trabalhados com seus alunos",
        #        className="header-description")
    ], className="header", style={"height": "150px", "background-color": "#2f3640", "border-radius": "10px" , "margin-top" : "10px" } ),

    # Filtros
    html.Div([
        # Dropdown Disciplina
        html.Div([
        html.Div(children="Disciplina", className="menu-title"),
        dcc.Dropdown(
            id="dropdown-disciplina",
            options=[
                {"label": f"Disciplina {disciplina_id}", "value": disciplina_id}
                for disciplina_id in disciplina_df["id"].unique()
            ],
            value=list(disciplina_df["id"].unique()),  # valor padrão quando a página é carregada
            className="dropdown",
            multi=True,
            searchable=True,
            placeholder="Selecione uma disciplina..."
        ),
    ], style={'width': '50%', 'display': 'inline-block', 'margin-right': '5%'}),
    
        # Calendario
        html.Div([
            html.Div(children="Periodo", className="menu-title"),
            dcc.DatePickerRange(
                id="range-periodo",
                min_date_allowed=pd.to_datetime(turma_df["started_at"]).min().date(),
                max_date_allowed=pd.to_datetime(turma_df["started_at"]).max().date(),
                start_date=pd.to_datetime(turma_df["started_at"]).min().date(),
                end_date=pd.to_datetime(turma_df["started_at"]).max().date(),
                )
            ]
        )
    ], className="menu"),


    # KPIs
    html.Div([
        html.Div([
            html.H2("Disciplinas"),
            html.H3(id="total-disciplinas")
        ], className="card"),
        html.Div([
            html.H2("Alunos"),
            html.H3(id="total-alunos")
        ], className="card"),
        html.Div([
            html.H2("Média de Notas"),
            html.H3(id="media-notas")
        ], className="card"),
        html.Div([
            html.H2("Disciplinas Pendentes"),
            html.H3(id="disciplinas-pendentes")
        ], className="card"),
    ], id='kpis-container'),

    # Gráficos
    html.Div([
        dcc.Graph(id="media-nota-chart"),
        dcc.Graph(id="media-aval-chart"),
    ],  style={"width": "50%", "display": "inline-block"}),  # Define os gráficos como uma linha flexível e adiciona estilos para limitar a altura e largura
    html.Div([
        dcc.Graph(id="aprovacao-disciplina-chart"),
        dcc.Graph(id="histograma-notas-chart")
    ],  style={"width": "50%", "display": "inline-block"})  # Define os gráficos como uma linha flexível e adiciona estilos para limitar a altura e largura
])

# Callback para atualizar os KPIs com base nas turmas selecionadas
@app.callback(
    Output('kpis-container', 'children'),
    [Input('dropdown-disciplina', 'value'),
     Input('range-periodo', 'start_date'),
     Input('range-periodo', 'end_date')]
)

def update_kpis(selected_disciplina_ids, start_date, end_date):
    if not selected_disciplina_ids:
        return [
            html.Div([
                html.H2('Disciplinas'),
                html.H3(f'{num_disciplinas_total:}')  
            ], className='card'),
            html.Div([
                html.H2('Alunos'),
                html.H3(f'{num_alunos_total:}')  
            ], className='card'),
            html.Div([
                html.H2('Média de Notas'),
                html.H3(f'{media_total:.2f}')  
            ], className='card'),
            html.Div([
                html.H2('Disciplinas Pendentes'),
                html.H3(f'{disciplinas_pendentes:}')  
                ], className='card')
        ]

    # Filtrar os DataFrames com base nas disciplinas selecionadas
    disciplinas_selecionadas = turma_df[turma_df['disciplina_id'].isin(selected_disciplina_ids)]
    disciplinas_selecionadas = disciplinas_selecionadas[(disciplinas_selecionadas['started_at'] >= start_date) & (disciplinas_selecionadas['started_at'] <= end_date)]
    notas_disciplinas_selecionadas = notas_df[notas_df['turma_id'].isin(disciplinas_selecionadas['id'])]

    # Calcular as novas médias e contagens
    nova_media_total = notas_disciplinas_selecionadas.agg(media_final=('nota', 'mean')).reset_index()['nota'].iloc[0]
    nova_num_disciplinas_total = len(disciplinas_selecionadas['disciplina_id'].unique())
    nova_num_alunos_total = len(disciplinas_selecionadas['aluno_id'].unique())
    
    # Calcular novas turmas que faltam nota
    nova_disciplinas_pendentes = len(disciplinas_selecionadas[disciplinas_selecionadas['status'] != 'Finalizada']['disciplina_id'].unique())

    # Atualizar os KPIs com os novos valores
    return [
        html.Div([
            html.H2('Disciplinas'),
            html.H3(f'{nova_num_disciplinas_total:}')  
        ], className='card'),
        html.Div([
            html.H2('Alunos'),
            html.H3(f'{nova_num_alunos_total:}')  
        ], className='card'),
        html.Div([
            html.H2('Média de Notas'),
            html.H3(f'{nova_media_total:.2f}')  
        ], className='card'),
            html.Div([
            html.H2('Disciplinas Pendentes'),
            html.H3(f'{nova_disciplinas_pendentes:}')  
        ], className='card')
    ]

# Callback para atualizar o gráfico com os dados da média das notas por turma
# Callback para atualizar o gráfico com os dados da média das notas por turma
@app.callback(
    Output('media-nota-chart', 'figure'),
    [Input('dropdown-disciplina', 'value'),
     Input('range-periodo', 'start_date'),
     Input('range-periodo', 'end_date')]
)
def update_graph(selected_disciplina_ids, start_date, end_date):
    if not selected_disciplina_ids:  # Se nenhuma turma for selecionada, não faça nada
        return go.Figure()

    # Filtrar o DataFrame media_notas_turma com base nas turmas selecionadas
    disciplinas_selecionadas = turma_df[turma_df['disciplina_id'].isin(selected_disciplina_ids)]
    disciplinas_selecionadas = disciplinas_selecionadas[(disciplinas_selecionadas['started_at'] >= start_date) & (disciplinas_selecionadas['started_at'] <= end_date)]
    notas_disciplinas_selecionadas = media_final_df[media_final_df['disciplina_id'].isin(disciplinas_selecionadas['disciplina_id'])]
    notas_disciplinas_selecionadas = notas_disciplinas_selecionadas.merge(disciplina_df, left_on=['disciplina_id'], right_on=['id'])
    media_notas_disciplinas_filtrado = notas_disciplinas_selecionadas.groupby(['disciplina_id','nome']).agg(media_final=('nota_final', 'mean')).reset_index()
    
    # Definir cores para as barras
    colors = ['#046157', '#079A82', '#04CCB6', '#4A4A4A', '#F4A261']
    
    # Criar o gráfico de barras
    data = []
    tickvals = []
    ticktext = []
    for i, (disciplina_id, media) in enumerate(media_notas_disciplinas_filtrado.iterrows()):
        trace = go.Bar(
            x=[i],  # Usar um índice como valor no eixo X
            y=[media['media_final']],  # Média das notas
            name=media["nome"],
            marker_color=colors[i % len(colors)],  # Definir a cor das barras
            text=[f'Média: {media["media_final"]:.2f}'],  # Texto do tick
            #textposition='outside'  # Posição do texto
        )
        data.append(trace)
        tickvals.append(i)  # Adicionar o índice como valor de tick
        ticktext.append(media["nome"])  # Adicionar o nome da disciplina como rótulo do tick
    
    layout = go.Layout(
        title=dict(
            text='Média das Notas por Disciplina',
            x=0.5  # Centralize the title
        ),
        xaxis=dict(
            title='Disciplina',
            tickvals=tickvals,  # Valores dos ticks no eixo X
            ticktext=ticktext  # Rótulos dos ticks no eixo X
        ),
        yaxis=dict(title='Média das Notas'),
        plot_bgcolor='rgba(0,0,0,0)',  # Remover o fundo
        paper_bgcolor='rgba(0,0,0,0)',  # Remover o fundo do papel
        showlegend=False  # Remover a legenda
    )
    
    fig = go.Figure(data=data, layout=layout)

    return fig

# Callback para atualizar o gráfico com os dados da média das notas por avaliação
# Callback para atualizar o gráfico com os dados da média das notas por turma
@app.callback(
    Output('media-aval-chart', 'figure'),
    [Input('dropdown-disciplina', 'value'),
     Input('range-periodo', 'start_date'),
     Input('range-periodo', 'end_date')]
)
def update_graph(selected_disciplina_ids, start_date, end_date):
    if not selected_disciplina_ids:  # Se nenhuma turma for selecionada, não faça nada
        return go.Figure()

    # Filtrar o DataFrame media_notas_turma com base nas turmas selecionadas
    disciplinas_selecionadas = turma_df[turma_df['disciplina_id'].isin(selected_disciplina_ids)]
    disciplinas_selecionadas = disciplinas_selecionadas[(disciplinas_selecionadas['started_at'] >= start_date) & (disciplinas_selecionadas['started_at'] <= end_date)]
    notas_disciplinas_selecionadas = notas_df.merge(disciplinas_selecionadas, left_on=['turma_id','aluno_id'], right_on=['id','aluno_id'])
    notas_disciplinas_selecionadas = notas_disciplinas_selecionadas.merge(disciplina_df, left_on=['disciplina_id'], right_on=['id'])
    media_aval = notas_disciplinas_selecionadas.groupby(['disciplina_id','nome','aval']).agg(media_final=('nota', 'mean')).reset_index()

    # Definir cores para as barras
    colors = ['#046157', '#079A82', '#04CCB6', '#4A4A4A', '#F4A261']
    
    # Criar o gráfico de barras
    data = []
    for i, (aval, grupo) in enumerate(media_aval.groupby('aval')):
        trace = go.Bar(
            x=grupo['nome'],
            y=grupo['media_final'],
            name=f'Avaliação {aval}',
            marker=dict(color=colors[i % len(colors)])  # Assign colors cyclically
        )
        data.append(trace)
    
    layout = go.Layout(
        title=dict(
            text='Média das Notas por Disciplina e Avaliação',
            x=0.5  # Centralize the title
        ),
        xaxis=dict(title='Disciplina'),
        yaxis=dict(title='Média das Notas'),
        plot_bgcolor='rgba(0,0,0,0)',  # Remover o fundo
        paper_bgcolor='rgba(0,0,0,0)',  # Remover o fundo do papel
    )
    
    fig = go.Figure(data=data, layout=layout)

    return fig

# Callback para atualizar o gráfico de setor com os dados de aprovação por disciplina
# Callback para atualizar o gráfico com os dados de aprovação por disciplina
@app.callback(
    Output('aprovacao-disciplina-chart', 'figure'),
    [Input('dropdown-disciplina', 'value'),
     Input('range-periodo', 'start_date'),
     Input('range-periodo', 'end_date')]
)
def update_aprovacao_disciplina(selected_disciplina_ids, start_date, end_date):
    if not selected_disciplina_ids:  # Se nenhuma disciplina for selecionada, não faça nada
        return go.Figure()

    # Filtrar o DataFrame com base nas disciplinas selecionadas
    disciplinas_selecionadas = turma_df[turma_df['disciplina_id'].isin(selected_disciplina_ids)]
    disciplinas_selecionadas = disciplinas_selecionadas[(disciplinas_selecionadas['started_at'] >= start_date) & (disciplinas_selecionadas['started_at'] <= end_date)]
    notas_disciplinas_selecionadas = disciplinas_selecionadas.merge(media_final_df, left_on=['disciplina_id','aluno_id'], right_on=['disciplina_id','aluno_id'], how='left')

    # Calcular o número total de alunos na turma
    total_alunos_turma = notas_disciplinas_selecionadas.drop_duplicates(['aluno_id', 'disciplina_id']).shape[0]

    # Calcular o número de alunos aprovados, reprovados e sem nota
    aprovados = notas_disciplinas_selecionadas[notas_disciplinas_selecionadas['aprovado'] == True].drop_duplicates(['aluno_id', 'disciplina_id']).shape[0]
    reprovados = notas_disciplinas_selecionadas[notas_disciplinas_selecionadas['aprovado'] == False].drop_duplicates(['aluno_id', 'disciplina_id']).shape[0]
    sem_nota = notas_disciplinas_selecionadas[notas_disciplinas_selecionadas['status'] != 'Finalizada'].drop_duplicates(['aluno_id', 'disciplina_id']).shape[0]

    # Calcular o percentual de cada categoria
    percent_aprovados = (aprovados / total_alunos_turma) * 100
    percent_reprovados = (reprovados / total_alunos_turma) * 100
    percent_sem_nota = (sem_nota / total_alunos_turma) * 100

    # Criar o gráfico de rosca
    labels = ['Aprovados', 'Reprovados', 'Sem Nota']
    values = [percent_aprovados, percent_reprovados, percent_sem_nota]
    colors = ['#079A82', '#F4A261', '#4A4A4A']  # Cores personalizadas

    layout = go.Layout(
        title=dict(
            text='Percentual de Alunos Aprovados, Reprovados e Sem Nota',
            x=0.5  # Centralize the title
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Remover o fundo
        paper_bgcolor='rgba(0,0,0,0)',  # Remover o fundo do papel
    )

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3, marker=dict(colors=colors))],
                    layout=layout)

    return fig

# Callback para atualizar o gráfico com os dados do histograma de notas
@app.callback(
    Output('histograma-notas-chart', 'figure'),
    [Input('dropdown-disciplina', 'value'),
     Input('range-periodo', 'start_date'),
     Input('range-periodo', 'end_date')]
)
def update_histograma_notas(selected_disciplina_ids, start_date, end_date):
    if not selected_disciplina_ids:  # Se nenhuma disciplina for selecionada, não faça nada
        return go.Figure()

    # Filtrar o DataFrame com base nas disciplinas selecionadas
    disciplinas_selecionadas = turma_df[turma_df['disciplina_id'].isin(selected_disciplina_ids)]
    disciplinas_selecionadas = disciplinas_selecionadas[(disciplinas_selecionadas['started_at'] >= start_date) & (disciplinas_selecionadas['started_at'] <= end_date)]
    notas_disciplinas_selecionadas = disciplinas_selecionadas.merge(notas_df, left_on=['id','aluno_id'], right_on=['turma_id','aluno_id'], how='left')

    # Excluir linhas com valores NaN na coluna 'nota'
    notas_disciplinas_selecionadas.dropna(subset=['nota'], inplace=True)

    # Criar o histograma de notas
    fig = go.Figure(data=[go.Histogram(x=notas_disciplinas_selecionadas['nota'])])

    # Gerar o histograma
    BINS = 10
    y, x = np.histogram(notas_disciplinas_selecionadas['nota'], bins=BINS)
    x = [(a + b) / 2 for a, b in zip(x, x[1:])]

   # Definir a escala de cores personalizada
    color_scale = [[0, '#F4A261'], [1, '#079A82']]

    fig = px.bar(x=x, 
                 y=y, 
                 color=x,
                 labels={'y': 'Frequência'},  # Define o rótulo para o eixo y
                 color_continuous_scale=color_scale)
    fig.update_traces(marker_line_color="black", hovertemplate='Frequência: %{y}<extra></extra>')

    fig.update_layout(
        title=dict(
            text='Distribuição das notas dos alunos',
            x=0.5  # Centralize the title
        ),
        xaxis_title='Nota',
        yaxis_title='Frequência',
        plot_bgcolor='rgba(0,0,0,0)',  # Remover o fundo
        paper_bgcolor='rgba(0,0,0,0)',  # Remover o fundo do papel
        coloraxis_colorbar=dict(
            title="Cores"
        )
        
    )

    return fig

# Executar a aplicação
if __name__ == '__main__':
    app.run_server(debug=True)