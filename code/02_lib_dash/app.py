import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash import Dash, html, dcc, Input, Output

# Importar os DataFrames dos arquivos CSV
professor_df = pd.read_csv('professor_df.csv')
aluno_df = pd.read_csv('aluno_df.csv')
disciplina_df = pd.read_csv('disciplina_df.csv')
turma_df = pd.read_csv('turma_df.csv')
notas_df = pd.read_csv('notas_df.csv')
notas_aluno_agrupadas = pd.read_csv('notas_aluno_agrupadas.csv')
media_final_df = pd.read_csv('media_final_df.csv')
media_notas_turma = pd.read_csv('media_notas_turma.csv')

# Inicializar a aplicação Dash
app = dash.Dash(__name__)

# Layout dos KPIs
kpis_layout = html.Div([
    html.Div([
        html.Div([
            html.H2('Média Total das Notas'),
            html.H3(id='media-total-notas')
        ], className='kpis'),
        html.Div([
            html.H2('Número de Disciplinas'),
            html.H3(id='num-disciplinas')
        ], className='kpis'),
        html.Div([
            html.H2('Número de Alunos'),
            html.H3(id='num-alunos')
        ], className='kpis')
    ], className='container', id='kpis-container')  # Verifique se o ID 'kpis-container' está definido corretamente aqui
])

# Layout do Gráfico de Barras
grafico_layout = html.Div([
    dcc.Graph(id='grafico-media-notas')
])

# Callback para atualizar o gráfico com os dados da média das notas por turma
@app.callback(
    Output('grafico-media-notas', 'figure'),
    [Input('dropdown-turma', 'value')]
)
def update_graph(selected_turma_ids):
    if not selected_turma_ids:  # Se nenhuma turma for selecionada, não faça nada
        return go.Figure()

    # Filtrar o DataFrame media_notas_turma com base nas turmas selecionadas
    media_notas_turma_filtrado = media_notas_turma[media_notas_turma.index.isin(selected_turma_ids)]

    # Criar o gráfico de barras
    data = []
    tickvals = []
    ticktext = []
    for i, (turma_id, media) in enumerate(media_notas_turma_filtrado.items()):
        trace = go.Bar(
            x=[i],  # Usar um índice como valor no eixo X
            y=[media],  # Média das notas
            name=f'Turma {turma_id}'
        )
        data.append(trace)
        tickvals.append(i)  # Adicionar o índice como valor de tick
        ticktext.append(f'Turma {turma_id}')  # Adicionar o nome da turma como rótulo do tick

    layout = go.Layout(
        title='Média das Notas por Turma',
        xaxis=dict(
            title='Turma ID',
            tickvals=tickvals,  # Valores dos ticks no eixo X
            ticktext=ticktext  # Rótulos dos ticks no eixo X
        ),
        yaxis=dict(title='Média das Notas')
    )

    fig = go.Figure(data=data, layout=layout)

    return fig

# Callback para atualizar os KPIs com base nas turmas selecionadas
@app.callback(
    Output('kpis-container', 'children'),
    [Input('dropdown-turma', 'value')]
)
def update_kpis(selected_turma_ids):
    if not selected_turma_ids:  # Se nenhuma turma for selecionada, não faça nada
        return [
            html.Div([
                html.H2('Média Total das Notas'),
                html.H3(f'{media_total:.2f}')  # <- Verifique se media_total está definido corretamente
            ], className='kpis'),
            html.Div([
                html.H2('Número de Disciplinas'),
                html.H3(f'{num_disciplinas}')  # <- Verifique se num_disciplinas está definido corretamente
            ], className='kpis'),
            html.Div([
                html.H2('Número de Alunos'),
                html.H3(f'{num_alunos}')  # <- Verifique se num_alunos está definido corretamente
            ], className='kpis')
        ]

    # Filtrar os DataFrames com base nas turmas selecionadas
    turmas_selecionadas = turma_df[turma_df['id'].isin(selected_turma_ids)]
    alunos_selecionados = aluno_df[aluno_df['id'].isin(turmas_selecionadas['aluno_id'].unique())]  # Corrigido aqui
    notas_turmas_selecionadas = notas_aluno_agrupadas[notas_aluno_agrupadas['turma_id'].isin(selected_turma_ids)]

    # Calcular as novas médias e contagens
    nova_media_total = notas_turmas_selecionadas['media_final'].mean()  # <- Aqui estava o problema, verifique se a coluna 'media_final' existe em turmas_selecionadas
    nova_num_disciplinas = len(turmas_selecionadas['disciplina_id'].unique())
    nova_num_alunos = len(alunos_selecionados)

    # Atualizar os KPIs com os novos valores
    return [
        html.Div([
            html.H2('Média Total das Notas'),
            html.H3(f'{nova_media_total:.2f}')
        ], className='kpis'),
        html.Div([
            html.H2('Número de Disciplinas'),
            html.H3(f'{nova_num_disciplinas}')
        ], className='kpis'),
        html.Div([
            html.H2('Número de Alunos'),
            html.H3(f'{nova_num_alunos}')
        ], className='kpis')
    ]

# Layout da aplicação
app.layout = html.Div([
    # KPIs
    kpis_layout,
    
    # Gráfico de barras
    grafico_layout,
    
    # Dropdown para seleção de turmas
    dcc.Dropdown(
        id='dropdown-turma',
        options=[{'label': f'Turma {turma_id}', 'value': turma_id} for turma_id in turma_df['id'].unique()],
        multi=True,
        value=[]
    )
])

# Layout completo da aplicação
app.layout = html.Div([
    # Dropdown para seleção de turmas
    dcc.Dropdown(
        id='dropdown-turma',
        options=[{'label': f'Turma {turma_id}', 'value': turma_id} for turma_id in turma_df['id'].unique()],
        multi=True,
        value=[]
    ),

    # KPIs
    kpis_layout,
    
    # Gráfico de barras
    grafico_layout
])

# Executar a aplicação
if __name__ == '__main__':
    app.run_server(debug=True)