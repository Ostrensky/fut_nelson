import dash
from dash import dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Carregar dados (Load data)
file_path = 'De Placa Soccer - novo (2).xlsx'
jogos_df = pd.read_excel(file_path, sheet_name='Jogos')
atletas_df = pd.read_excel(file_path, sheet_name='Atletas')
dim_df = pd.read_excel(file_path, sheet_name='Dim')

jogos_df['Data'] = pd.to_datetime(jogos_df['Data'], errors='coerce')

# Mesclar informações de time (Merge team information)
if 'Team' not in jogos_df.columns:
    if 'Team' in atletas_df.columns:
        jogos_df = jogos_df.merge(atletas_df[['Atleta', 'Team']], on='Atleta', how='left')
    else:
        # Se a informação de time não estiver disponível, atribuir times padrão alternadamente
        jogos_df['Team'] = ['Time A' if i % 2 == 0 else 'Time B' for i in range(len(jogos_df))]

# Resumir estatísticas dos jogadores (Summarize player statistics)
total_goals_by_player = jogos_df.groupby('Atleta')['Gols'].sum().reset_index()
total_goals_by_player.columns = ['Atleta', 'Total de Gols']

total_matches_by_player = jogos_df.groupby('Atleta').size().reset_index(name='Total de Partidas')

total_wins_by_player = jogos_df[jogos_df['Resultado'] == 'V'].groupby('Atleta').size().reset_index(name='Total de Vitórias')

player_summary = pd.merge(total_goals_by_player, total_matches_by_player, on='Atleta', how='left')
player_summary = pd.merge(player_summary, total_wins_by_player, on='Atleta', how='left')

player_summary['Total de Vitórias'] = player_summary['Total de Vitórias'].fillna(0)

player_summary['Média de Gols'] = player_summary['Total de Gols'] / player_summary['Total de Partidas']
player_summary['Média de Vitórias'] = player_summary['Total de Vitórias'] / player_summary['Total de Partidas']

player_summary = player_summary.round(2)

# Inicializar o aplicativo Dash com um tema Bootstrap claro (Initialize the Dash app)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Definir cores dos times (Define team colors)
team_colors = {
    'Time A': '#1f77b4',  # Azul
    'Time B': '#ff7f0e',  # Laranja
    'Time C': '#2ca02c',  # Verde
    # Adicione mais times se necessário
}

# Layout do aplicativo (Layout for the app)
app.layout = dbc.Container([
    # Barra de navegação com logo (Navigation bar with logo)
    dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.Img(src="https://media.licdn.com/dms/image/C4E03AQFdJOG5TFWscQ/profile-displayphoto-shrink_200_200/0/1615905852785?e=2147483647&v=beta&t=-VQkt7LaP-on2Mufsa8eoNh2V3SSswCeepcoHzMF9wM", height="50px")),
                    dbc.Col(dbc.NavbarBrand("Fut do Nelson", className="ml-2")),
                ], align="center", className="g-0"),
                href="#",
            ),
        ]),
        color="primary",
        dark=True,
        sticky="top",
    ),
    html.Br(),
    dbc.Tabs([
        # Aba 1: Detalhes da Partida (Tab 1: Match Details)
        dbc.Tab(label='Detalhes da Partida', children=[
            html.Br(),
            dcc.Dropdown(
                id='match-dropdown',
                options=[{'label': date.strftime('%Y-%m-%d'), 'value': date.isoformat()} for date in jogos_df['Data'].unique()],
                placeholder="Selecione uma partida",
            ),
            html.Br(),
            html.Div(id='match-details')
        ]),
        
        # Aba 2: Resumo dos Jogadores (Tab 2: Player Summary)
        dbc.Tab(label='Resumo dos Jogadores', children=[
            html.Br(),
            dcc.Dropdown(
                id='stats-dropdown',
                options=[
                    {'label': 'Total de Gols', 'value': 'Total de Gols'},
                    {'label': 'Média de Gols', 'value': 'Média de Gols'},
                    {'label': 'Total de Vitórias', 'value': 'Total de Vitórias'},
                    {'label': 'Média de Vitórias', 'value': 'Média de Vitórias'},
                    {'label': 'Total de Partidas', 'value': 'Total de Partidas'},
                ],
                value='Total de Gols',
                placeholder="Selecione uma estatística para exibir",
            ),
            html.Br(),
            # Linha com cartões de destaque e gráfico (Row with highlight cards and graph)
            dbc.Row([
                dbc.Col(
                    dbc.Row([
                        dbc.Col(dbc.Card(
                            [dbc.CardHeader("Mais Gols"), dbc.CardBody(html.H5(id='most-goals'))],
                            color="info", inverse=True, className="text-center mb-2"
                        ), width=12),
                        dbc.Col(dbc.Card(
                            [dbc.CardHeader("Mais Vitórias"), dbc.CardBody(html.H5(id='most-wins'))],
                            color="success", inverse=True, className="text-center mb-2"
                        ), width=12),
                        dbc.Col(dbc.Card(
                            [dbc.CardHeader("Maior Média de Gols"), dbc.CardBody(html.H5(id='highest-goal-average'))],
                            color="warning", inverse=True, className="text-center mb-2"
                        ), width=12),
                        dbc.Col(dbc.Card(
                            [dbc.CardHeader("Maior Média de Vitórias"), dbc.CardBody(html.H5(id='highest-win-average'))],
                            color="danger", inverse=True, className="text-center mb-2"
                        ), width=12),
                    ]),
                width=3),
                dbc.Col(
                    dcc.Graph(id='stats-graph'),
                width=9
                )
            ]),
            html.Br(),
            # Tabela de dados (Data table)
            dash_table.DataTable(
                id='stats-table',
                columns=[{"name": i, "id": i} for i in player_summary.columns],
                data=player_summary.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                },
                style_header={
                    'fontWeight': 'bold',
                },
                page_size=10,
                sort_action='native',
            )
        ])
    ])
], fluid=True)

# Callbacks para conteúdo dinâmico (Callbacks for dynamic content)
@app.callback(
    Output('stats-table', 'data'),
    Output('most-goals', 'children'),
    Output('most-wins', 'children'),
    Output('highest-goal-average', 'children'),
    Output('highest-win-average', 'children'),
    Output('stats-graph', 'figure'),
    Input('stats-dropdown', 'value')
)
def update_stats_table(selected_stat):
    # Atualizar a tabela com base na estatística selecionada (Update the table based on the selected statistic)
    sorted_data = player_summary.sort_values(by=selected_stat, ascending=False)
    table_data = sorted_data.to_dict('records')
    
    # Encontrar os jogadores com os valores mais altos para cada destaque (Find the players with the highest values)
    most_goals_player = player_summary.loc[player_summary['Total de Gols'].idxmax(), 'Atleta']
    most_wins_player = player_summary.loc[player_summary['Total de Vitórias'].idxmax(), 'Atleta']
    highest_goal_average_player = player_summary.loc[player_summary['Média de Gols'].idxmax(), 'Atleta']
    highest_win_average_player = player_summary.loc[player_summary['Média de Vitórias'].idxmax(), 'Atleta']
    
    # Criar conteúdo dos cartões de destaque (Create highlight boxes content)
    most_goals = most_goals_player
    most_wins = most_wins_player
    highest_goal_avg = highest_goal_average_player
    highest_win_avg = highest_win_average_player
    
    # Criar um gráfico de barras para a estatística selecionada (Create a bar chart for the selected statistic)
    fig = px.bar(sorted_data, x='Atleta', y=selected_stat, color='Atleta', title=f'Jogador - {selected_stat}',
                 labels={'Atleta': 'Jogador', selected_stat: selected_stat},
                 template='plotly_white')
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    
    return table_data, most_goals, most_wins, highest_goal_avg, highest_win_avg, fig

@app.callback(
    Output('match-details', 'children'),
    Input('match-dropdown', 'value')
)
def update_match_details(selected_match):
    if not selected_match:
        return html.Div("Por favor, selecione uma partida para ver os detalhes.", style={'textAlign': 'center', 'marginTop': '20px'})

    # Converter selected_match para datetime (Convert selected_match to datetime)
    try:
        selected_match_dt = pd.to_datetime(selected_match)
    except Exception as e:
        return html.Div(f"Erro ao analisar a data: {e}", style={'textAlign': 'center', 'marginTop': '20px'})

    # Filtrar dados da partida com base na seleção (Filter match data based on selected match)
    match_data = jogos_df[jogos_df['Data'] == selected_match_dt]

    # Se não houver partidas, retornar uma mensagem (If there are no matches)
    if match_data.empty:
        return html.Div("Não há dados disponíveis para a partida selecionada.", style={'textAlign': 'center', 'marginTop': '20px'})

    # Obter a lista de times envolvidos (Get list of teams involved)
    teams = match_data['Team'].unique()

    # Criar data frames dos times (Create team data frames)
    team_players = {}
    team_total_goals = {}
    for team in teams:
        team_data = match_data[match_data['Team'] == team]
        # Somar gols por jogador (Sum goals per player)
        player_goals = team_data.groupby('Atleta')['Gols'].sum().reset_index()
        team_total_goals[team] = player_goals['Gols'].sum()
        team_players[team] = player_goals

    # Criar listas de times (Create team lists)
    team_lists = []
    for team in teams:
        team_color = team_colors.get(team, '#FFFFFF')
        df = team_players[team]
        # Criar itens de lista (Create list items)
        player_items = []
        for _, row in df.iterrows():
            player_name = row['Atleta']
            goals = int(row['Gols']) if not pd.isnull(row['Gols']) else 0
            # Criar uma string de emojis de bola de futebol (Create a string of soccer ball emojis)
            if goals > 0:
                goals_icons = '⚽' * goals
            else:
                goals_icons = ''
            player_items.append(
                dbc.ListGroupItem(
                    [html.Span(player_name), html.Span(goals_icons)],
                    className="d-flex justify-content-between align-items-center"
                )
            )
        # Criar ListGroup (Create ListGroup)
        team_list = dbc.Card([
            dbc.CardHeader(
                html.H5(f"{team} - Total de Gols: {team_total_goals[team]}", className="card-title"),
                style={'backgroundColor': team_color, 'color': 'white', 'textAlign': 'center'}
            ),
            dbc.CardBody(
                dbc.ListGroup(player_items)
            )
        ], className="h-100")
        team_lists.append(team_list)

    # Organizar listas de times lado a lado (Arrange team lists side by side)
    match_layout = dbc.Row([
        dbc.Col(team_lists[0], width=6),
        dbc.Col(team_lists[1], width=6)
    ], className="mb-4") if len(team_lists) > 1 else dbc.Row([
        dbc.Col(team_lists[0], width=12)
    ], className="mb-4")

    # Título da partida (Match title)
    match_title = html.Div([
        html.H3(f"Data da Partida: {selected_match_dt.strftime('%Y-%m-%d')}", style={'textAlign': 'center', 'marginTop': '20px'}),
    ])

    return html.Div([match_title, match_layout])

# Executar o aplicativo (Run the app)
if __name__ == '__main__':
    app.run_server(debug=True)
