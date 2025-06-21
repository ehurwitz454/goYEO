"""
Oberlin Baseball At-Bat Simulator - Dash App
Beautiful UI matching thaAPP.py styling
"""

import dash
from dash import dcc, html, Input, Output, State
import json
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional

# Initialize Dash app with external CSS
app = dash.Dash(__name__)

# Add custom CSS to the app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>OCHSTEIN - Oberlin Baseball Simulator</title>
        {%favicon%}
        {%css%}
        <style>
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes pulse {
                0%, 100% {
                    opacity: 0.8;
                    transform: scale(1);
                }
                50% {
                    opacity: 1;
                    transform: scale(1.1);
                }
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(100px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            body {
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #1a1a1a;
                background-image: 
                    radial-gradient(circle at 20% 50%, rgba(200, 50, 47, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(249, 199, 79, 0.1) 0%, transparent 50%);
            }
            
            .Select-control {
                background-color: white !important;
                border: 2px solid #f9c74f !important;
                color: #333 !important;
            }
            
            .Select-value-label {
                color: #333 !important;
            }
            
            .Select-input input {
                color: #333 !important;
            }
            
            .Select-placeholder {
                color: #666 !important;
            }
            
            .Select-menu-outer {
                background-color: white !important;
                border: 1px solid #f9c74f !important;
            }
            
            .Select-option {
                background-color: white !important;
                color: #333 !important;
            }
            
            .Select-option:hover {
                background-color: #c8322f !important;
                color: white !important;
            }
            
            .Select-option.is-selected {
                background-color: #f9c74f !important;
                color: #333 !important;
            }
            
            .Select-arrow-zone {
                color: #333 !important;
            }
            
            .Select-clear-zone {
                color: #333 !important;
            }
            
            .gradient-button {
                position: relative;
                overflow: hidden;
            }
            
            .gradient-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 15px 40px rgba(200, 50, 47, 0.6) !important;
            }
            
            .gradient-button:before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            
            .gradient-button:hover:before {
                left: 100%;
            }
            
            .gradient-button:active {
                transform: translateY(0);
                box-shadow: 0 5px 15px rgba(200, 50, 47, 0.4) !important;
            }
            
            input[type="number"] {
                background-color: white !important;
                color: #333 !important;
                border: 2px solid #f9c74f !important;
            }
            
            input[type="number"]:focus {
                outline: none !important;
                border-color: #c8322f !important;
                box-shadow: 0 0 10px rgba(200, 50, 47, 0.5) !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Color scheme from thaAPP - Updated with Oberlin colors
COLORS = {
    'background': '#1a1a1a',
    'oberlin_red': '#c8322f',
    'oberlin_gold': '#f9c74f',
    'surface': 'rgba(0, 0, 0, 0.7)',
    'text_primary': '#f9c74f',
    'text_secondary': 'rgba(249, 199, 79, 0.8)',
    'text_light': 'rgba(255, 255, 255, 0.9)',
    'accent': '#c8322f',
    'gradient_primary': 'linear-gradient(135deg, #c8322f 0%, #8b1f1b 100%)',
    'gradient_accent': 'linear-gradient(135deg, #f9c74f 0%, #d4942a 100%)',
    'gradient_dark': 'linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)',
    'card_shadow': '0 8px 32px rgba(0, 0, 0, 0.5)',
    'success': '#4ECDC4',
    'warning': '#f9c74f',
    'info': '#4A90E2',
    'error': '#c8322f'
}

class OberlinAtBatSimulator:
    """Simulator class adapted from atbatsimmyYEO"""
    def __init__(self):
        self.batters = self.load_batters()
        self.pitchers = self.load_pitchers()
        print(f"✅ Loaded {len(self.batters)} batters and {len(self.pitchers)} pitchers")
        # Debug: print sample player IDs to see format
        if self.batters:
            sample_id = list(self.batters.keys())[0]
            print(f"Sample batter ID format: {sample_id}")
        if self.pitchers:
            sample_id = list(self.pitchers.keys())[0]
            print(f"Sample pitcher ID format: {sample_id}")

    def load_batters(self) -> Dict:
        try:
            with open('oberlin_baseball_data/batters.json', 'r') as f:
                batters_list = json.load(f)
            return {b['player_id']: b for b in batters_list}
        except FileNotFoundError:
            return {}

    def load_pitchers(self) -> Dict:
        try:
            with open('oberlin_baseball_data/pitchers.json', 'r') as f:
                pitchers_list = json.load(f)
            return {p['player_id']: p for p in pitchers_list}
        except FileNotFoundError:
            return {}

    def get_outcomes(self, batter: Dict, pitcher: Dict) -> List[Tuple[str, float]]:
        outcomes = []
        outcome_types = ['1B%', '2B%', '3B%', 'HR%', 'BB%', 'K%', 'HBP%', 'FO%']

        for outcome in outcome_types:
            batter_prob = batter.get(outcome, 0.125)
            pitcher_prob = pitcher.get(outcome, 0.125)
            avg_prob = (batter_prob + pitcher_prob) / 2
            outcome_name = outcome.replace('%', '')
            outcomes.append((outcome_name, avg_prob))

        total = sum(prob for _, prob in outcomes)
        if total > 0:
            outcomes = [(name, prob/total) for name, prob in outcomes]

        return outcomes

    def simulate_at_bat(self, batter: Dict, pitcher: Dict) -> str:
        outcomes = self.get_outcomes(batter, pitcher)
        outcome_names = [name for name, _ in outcomes]
        probabilities = [prob for _, prob in outcomes]
        result = np.random.choice(outcome_names, p=probabilities)
        return result

    def simulate_multiple_at_bats(self, batter: Dict, pitcher: Dict, n: int = 1000, park_factor: float = 1.0) -> Dict:
        results = []
        for _ in range(n):
            result = self.simulate_at_bat(batter, pitcher)
            results.append(result)

        stats = {}
        outcomes = ['1B', '2B', '3B', 'HR', 'BB', 'K', 'HBP', 'FO']
        for outcome in outcomes:
            count = results.count(outcome)
            stats[outcome] = {
                'count': count,
                'pct': count / n
            }

        # Apply park factors to positive offensive outcomes
        positive_outcomes = ['1B', '2B', '3B', 'HR']
        if park_factor != 1.0:
            # Adjust the counts based on park factor
            for outcome in positive_outcomes:
                original_count = stats[outcome]['count']
                adjusted_count = int(original_count * park_factor)
                diff = adjusted_count - original_count

                # Add or remove hits based on park factor
                if diff > 0:
                    # Add more of this outcome (convert some outs)
                    fo_count = stats['FO']['count']
                    if fo_count >= diff:
                        stats[outcome]['count'] += diff
                        stats['FO']['count'] -= diff
                elif diff < 0:
                    # Remove some of this outcome (convert to outs)
                    stats[outcome]['count'] += diff  # diff is negative
                    stats['FO']['count'] -= diff  # diff is negative, so this adds

            # Recalculate percentages
            for outcome in outcomes:
                stats[outcome]['pct'] = stats[outcome]['count'] / n

        # Calculate adjusted stats
        hits = sum(stats[x]['count'] for x in ['1B', '2B', '3B', 'HR'])
        at_bats = n - stats['BB']['count'] - stats['HBP']['count']

        stats['summary'] = {
            'AVG': hits / at_bats if at_bats > 0 else 0,
            'OBP': (hits + stats['BB']['count'] + stats['HBP']['count']) / n,
            'SLG': self.calculate_slg_from_stats(stats, at_bats),
            'total_sims': n,
            'park_factor': park_factor
        }

        return stats

    def calculate_slg_from_stats(self, stats: Dict, at_bats: int) -> float:
        if at_bats == 0:
            return 0
        total_bases = (stats['1B']['count'] +
                      stats['2B']['count'] * 2 +
                      stats['3B']['count'] * 3 +
                      stats['HR']['count'] * 4)
        return total_bases / at_bats

    def calculate_slg(self, results: List[str], at_bats: int) -> float:
        if at_bats == 0:
            return 0
        total_bases = (results.count('1B') +
                      results.count('2B') * 2 +
                      results.count('3B') * 3 +
                      results.count('HR') * 4)
        return total_bases / at_bats

    def calculate_slg_from_stats(self, stats: Dict, at_bats: int) -> float:
        if at_bats == 0:
            return 0
        total_bases = (stats['1B']['count'] +
                      stats['2B']['count'] * 2 +
                      stats['3B']['count'] * 3 +
                      stats['HR']['count'] * 4)
        return total_bases / at_bats

# Initialize simulator
simulator = OberlinAtBatSimulator()

def create_modern_glass_card(content, animation_delay='0s'):
    """Create a modern glassmorphism card with animations"""
    return html.Div(
        content,
        style={
            'background': COLORS['surface'],
            'backdropFilter': 'blur(10px)',
            'WebkitBackdropFilter': 'blur(10px)',
            'borderRadius': '24px',
            'border': f'2px solid {COLORS["oberlin_gold"]}',
            'padding': '32px',
            'boxShadow': COLORS['card_shadow'],
            'transition': 'all 0.3s ease',
            'animation': f'fadeInUp 0.8s ease-out {animation_delay} both'
        }
    )

def create_sleek_dropdown(label, dropdown_id, options, placeholder, value=None, animation_delay='0s'):
    """Create a styled dropdown with label"""
    return html.Div([
        html.Label(label, style={
            'fontWeight': '700',
            'color': COLORS['oberlin_gold'],
            'fontSize': '14px',
            'marginBottom': '8px',
            'display': 'block',
            'textTransform': 'uppercase',
            'letterSpacing': '0.05em'
        }),
        dcc.Dropdown(
            id=dropdown_id,
            options=options,
            placeholder=placeholder,
            value=value,
            style={
                'borderRadius': '12px',
                'marginBottom': '20px'
            },
            className='oberlin-dropdown'
        )
    ], style={'animation': f'fadeInUp 0.6s ease-out {animation_delay} both'})

def create_player_card(player_type, player, color_gradient):
    """Create a player display card"""
    if not player:
        return html.Div()

    # Try to get year from player data or extract from ID
    year = player.get('year', 'N/A')
    if year == 'N/A' and 'player_id' in player:
        # Try to extract from player_id format: OBR_YYYY_...
        try:
            parts = player['player_id'].split('_')
            if len(parts) >= 2 and parts[1].isdigit():
                year = parts[1]
        except:
            pass

    return html.Div([
        html.Div([
            html.I(className=f"fas fa-{'user' if player_type == 'Batter' else 'baseball-ball'}",
                   style={
                       'fontSize': '48px',
                       'marginBottom': '16px',
                       'color': COLORS['oberlin_gold']
                   }),
            html.H3(player['name'], style={
                'fontSize': '24px',
                'fontWeight': '700',
                'marginBottom': '8px',
                'color': COLORS['oberlin_gold']
            }),
            html.P(f"#{player.get('jersey', 'N/A')} • {year}", style={
                'fontSize': '16px',
                'color': COLORS['text_light'],
                'marginBottom': '16px'
            })
        ], style={'textAlign': 'center'}),

        html.Div([
            html.Div([
                html.Span("AVG" if player_type == 'Batter' else "ERA", style={
                    'fontSize': '12px',
                    'color': COLORS['text_light'],
                    'display': 'block'
                }),
                html.Span(f"{player.get('avg' if player_type == 'Batter' else 'era', 0):.3f}", style={
                    'fontSize': '28px',
                    'fontWeight': '700',
                    'color': COLORS['oberlin_red']
                })
            ], style={'textAlign': 'center', 'marginBottom': '12px'}),

            html.Div([
                html.Span("OPS" if player_type == 'Batter' else "WHIP", style={
                    'fontSize': '12px',
                    'color': COLORS['text_light'],
                    'display': 'block'
                }),
                html.Span(f"{player.get('ops' if player_type == 'Batter' else 'whip', 0):.3f}", style={
                    'fontSize': '28px',
                    'fontWeight': '700',
                    'color': COLORS['oberlin_red']
                })
            ], style={'textAlign': 'center'})
        ])
    ], style={
        'padding': '24px',
        'background': 'rgba(0,0,0,0.5)',
        'borderRadius': '16px',
        'border': f'1px solid {COLORS["oberlin_gold"]}'
    })

# App layout
app.layout = html.Div([
    # CSS and Font Awesome
    html.Link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'),
    html.Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'),



    # Main container
    html.Div([
        # Header with OCHSTEIN branding
        html.Div([
            # Logo and title section
            html.Div([
                html.Div([
                    html.I(className="fas fa-baseball-ball", style={
                        'fontSize': '80px',
                        'color': COLORS['oberlin_gold'],
                        'marginBottom': '20px',
                        'animation': 'pulse 2s infinite'
                    }),
                    html.H1("OCHSTEIN", style={
                        'fontSize': '72px',
                        'fontWeight': '900',
                        'color': COLORS['oberlin_gold'],
                        'letterSpacing': '4px',
                        'marginBottom': '8px',
                        'textShadow': '3px 3px 6px rgba(0,0,0,0.7)'
                    }),
                    html.H2("OBERLIN CAGE HIERARCHAL SIMULATOR", style={
                        'fontSize': '24px',
                        'fontWeight': '700',
                        'color': COLORS['oberlin_red'],
                        'letterSpacing': '2px',
                        'marginBottom': '4px'
                    }),
                    html.H3("TO EVALUATE INDOOR NUMERICAL-METRICS", style={
                        'fontSize': '18px',
                        'fontWeight': '500',
                        'color': COLORS['text_secondary'],
                        'letterSpacing': '1px'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '40px',
                    'background': COLORS['gradient_dark'],
                    'borderRadius': '24px',
                    'border': f'3px solid {COLORS["oberlin_gold"]}',
                    'marginBottom': '40px',
                    'animation': 'fadeInUp 0.8s ease-out'
                })
            ]),

            html.P("Simulate matchups between any Oberlin batter and pitcher", style={
                'fontSize': '20px',
                'color': COLORS['text_light'],
                'textAlign': 'center',
                'marginBottom': '48px',
                'animation': 'fadeInUp 0.8s ease-out 0.2s both'
            })
        ]),

        # Configuration card
        create_modern_glass_card([
            html.H3("⚾ Configure Matchup", style={
                'fontFamily': 'Inter, sans-serif',
                'fontWeight': '700',
                'color': COLORS['oberlin_gold'],
                'marginBottom': '32px',
                'fontSize': '28px',
                'textAlign': 'center'
            }),

            # Configuration grid
            html.Div([
                # Left column - Year and simulations
                html.Div([
                    create_sleek_dropdown(
                        "Season",
                        'year-select',
                        [
                            {'label': '🏆 2025 Season', 'value': 2025},
                            {'label': '📅 2024 Season', 'value': 2024},
                            {'label': '📅 2023 Season', 'value': 2023}
                        ],
                        "Select season...",
                        value=2025,
                        animation_delay='0.1s'
                    ),

                    html.Div([
                        html.Label("Number of Simulations", style={
                            'fontWeight': '700',
                            'color': COLORS['oberlin_gold'],
                            'fontSize': '14px',
                            'marginBottom': '8px',
                            'display': 'block',
                            'textTransform': 'uppercase',
                            'letterSpacing': '0.05em'
                        }),
                        dcc.Input(
                            id='sim-count',
                            type='number',
                            value=1000,
                            min=100,
                            max=10000,
                            step=100,
                            style={
                                'width': '100%',
                                'padding': '12px',
                                'borderRadius': '12px',
                                'border': f'2px solid {COLORS["oberlin_gold"]}',
                                'backgroundColor': 'white',
                                'color': '#333',
                                'fontSize': '16px'
                            }
                        )
                    ], style={'animation': 'fadeInUp 0.6s ease-out 0.2s both'})
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right column - Player selections
                html.Div([
                    create_sleek_dropdown(
                        "Select Batter",
                        'batter-select',
                        [],
                        "Choose a batter...",
                        animation_delay='0.3s'
                    ),

                    create_sleek_dropdown(
                        "Select Pitcher",
                        'pitcher-select',
                        [],
                        "Choose a pitcher...",
                        animation_delay='0.4s'
                    ),

                    create_sleek_dropdown(
                        "Select Batting Cage",
                        'ballpark-select',
                        [
                            {'label': '⬅️ Left Cage (Pitcher Friendly - Park Factor: 0.95)', 'value': 'left'},
                            {'label': '➡️ Right Cage (Hitter Friendly - Park Factor: 1.05)', 'value': 'right'}
                        ],
                        "Choose a cage...",
                        value='right',
                        animation_delay='0.5s'
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
            ]),

            # Run button
            html.Div([
                html.Button([
                    html.I(className="fas fa-play", style={
                        'marginRight': '12px',
                        'animation': 'pulse 2s infinite'
                    }),
                    "Run Simulation"
                ], id='run-sim-btn',
                    className='gradient-button',
                    style={
                        'background': COLORS['gradient_primary'],
                        'color': 'white',
                        'border': 'none',
                        'padding': '18px 48px',
                        'fontSize': '18px',
                        'fontWeight': '700',
                        'borderRadius': '50px',
                        'cursor': 'pointer',
                        'boxShadow': '0 10px 30px rgba(200, 50, 47, 0.5)',
                        'transition': 'all 0.3s ease',
                        'fontFamily': 'Inter, sans-serif',
                        'display': 'block',
                        'margin': '48px auto 0',
                        'animation': 'slideInUp 0.8s ease-out 0.6s both',
                        'position': 'relative',
                        'overflow': 'hidden'
                    }
                )
            ])
        ]),

        # Results container
        html.Div(id='results-container', style={'marginTop': '40px'}),

        # Hidden store for player data
        dcc.Store(id='player-store', data={})

    ], style={
        'minHeight': '100vh',
        'padding': '40px',
        'background': f'linear-gradient(180deg, {COLORS["background"]} 0%, #2d1414 50%, {COLORS["background"]} 100%)',
        'position': 'relative'
    })
])

# Callbacks
@app.callback(
    [Output('batter-select', 'options'),
     Output('pitcher-select', 'options')],
    Input('year-select', 'value')
)
def update_player_options(year):
    """Update player dropdowns based on selected year"""
    if not year:
        return [], []

    # Filter players by year - with fallback for missing year field
    batter_options = []
    pitcher_options = []

    for pid, batter in simulator.batters.items():
        # Check if player matches year or if year field is missing (include all)
        player_year = batter.get('year', None)
        if player_year == year or player_year is None:
            # Extract year from player_id if possible
            if player_year is None and '_' in pid:
                try:
                    # Format: OBR_YYYY_JERSEY_NAME
                    parts = pid.split('_')
                    if len(parts) >= 2 and parts[1].isdigit():
                        id_year = int(parts[1])
                        if id_year == year:
                            batter_options.append({
                                'label': f"⚾ {batter['name']} (#{batter.get('jersey', 'N/A')})",
                                'value': pid
                            })
                except:
                    pass
            else:
                batter_options.append({
                    'label': f"⚾ {batter['name']} (#{batter.get('jersey', 'N/A')})",
                    'value': pid
                })

    for pid, pitcher in simulator.pitchers.items():
        # Check if player matches year or if year field is missing (include all)
        player_year = pitcher.get('year', None)
        if player_year == year or player_year is None:
            # Extract year from player_id if possible
            if player_year is None and '_' in pid:
                try:
                    # Format: OBR_YYYY_JERSEY_NAME
                    parts = pid.split('_')
                    if len(parts) >= 2 and parts[1].isdigit():
                        id_year = int(parts[1])
                        if id_year == year:
                            pitcher_options.append({
                                'label': f"⚾ {pitcher['name']} (#{pitcher.get('jersey', 'N/A')})",
                                'value': pid
                            })
                except:
                    pass
            else:
                pitcher_options.append({
                    'label': f"⚾ {pitcher['name']} (#{pitcher.get('jersey', 'N/A')})",
                    'value': pid
                })

    # Sort by name
    batter_options.sort(key=lambda x: x['label'])
    pitcher_options.sort(key=lambda x: x['label'])

    # If no players found for the year, show all players
    if not batter_options:
        print(f"No batters found for year {year}, showing all batters")
        for pid, batter in simulator.batters.items():
            batter_options.append({
                'label': f"⚾ {batter['name']} (#{batter.get('jersey', 'N/A')})",
                'value': pid
            })
        batter_options.sort(key=lambda x: x['label'])

    if not pitcher_options:
        print(f"No pitchers found for year {year}, showing all pitchers")
        for pid, pitcher in simulator.pitchers.items():
            pitcher_options.append({
                'label': f"⚾ {pitcher['name']} (#{pitcher.get('jersey', 'N/A')})",
                'value': pid
            })
        pitcher_options.sort(key=lambda x: x['label'])

    return batter_options, pitcher_options

@app.callback(
    Output('results-container', 'children'),
    [Input('run-sim-btn', 'n_clicks')],
    [State('batter-select', 'value'),
     State('pitcher-select', 'value'),
     State('sim-count', 'value'),
     State('ballpark-select', 'value')],
    prevent_initial_call=True
)
def run_simulation(n_clicks, batter_id, pitcher_id, sim_count, ballpark):
    """Run simulation and display results"""
    if not batter_id or not pitcher_id:
        return create_modern_glass_card([
            html.Div([
                html.I(className="fas fa-exclamation-circle", style={
                    'fontSize': '64px',
                    'color': COLORS['oberlin_red'],
                    'marginBottom': '24px'
                }),
                html.H3("Missing Selection", style={
                    'color': COLORS['oberlin_gold'],
                    'marginBottom': '16px'
                }),
                html.P("Please select both a batter and pitcher", style={
                    'color': COLORS['text_light']
                })
            ], style={'textAlign': 'center'})
        ])

    # Get player data
    batter = simulator.batters.get(batter_id)
    pitcher = simulator.pitchers.get(pitcher_id)

    if not batter or not pitcher:
        return html.Div("Error: Player not found")

    # Add player_id to the player dicts if not present
    if 'player_id' not in batter:
        batter['player_id'] = batter_id
    if 'player_id' not in pitcher:
        pitcher['player_id'] = pitcher_id

    # Determine park factor
    park_factor = 1.05 if ballpark == 'right' else 0.95

    # Run simulation with park factor
    stats = simulator.simulate_multiple_at_bats(batter, pitcher, sim_count, park_factor)

    # Create results display
    return html.Div([
        # Matchup header
        create_modern_glass_card([
            html.Div([
                # Batter card
                html.Div([
                    create_player_card("Batter", batter, COLORS['gradient_primary'])
                ], style={'width': '45%', 'display': 'inline-block'}),

                # VS text
                html.Div([
                    html.H2("VS", style={
                        'fontSize': '48px',
                        'fontWeight': '800',
                        'color': COLORS['oberlin_red'],
                        'textShadow': '2px 2px 4px rgba(0,0,0,0.5)'
                    })
                ], style={'width': '10%', 'display': 'inline-block', 'textAlign': 'center', 'verticalAlign': 'middle'}),

                # Pitcher card
                html.Div([
                    create_player_card("Pitcher", pitcher, COLORS['gradient_accent'])
                ], style={'width': '45%', 'display': 'inline-block', 'float': 'right'})
            ])
        ], animation_delay='0.1s'),

        # Results stats
        create_modern_glass_card([
            html.H3("Simulation Results", style={
                'fontSize': '24px',
                'fontWeight': '700',
                'color': COLORS['oberlin_gold'],
                'marginBottom': '16px',
                'textAlign': 'center'
            }),

            # Cage info with icon
            html.Div([
                html.I(className="fas fa-baseball-ball", style={
                    'fontSize': '24px',
                    'color': COLORS['oberlin_red'] if stats['summary'].get('park_factor', 1.0) > 1 else COLORS['oberlin_gold'],
                    'marginRight': '12px'
                }),
                html.Span(f"{'➡️ Right Cage (Hitter Friendly)' if stats['summary'].get('park_factor', 1.0) > 1 else '⬅️ Left Cage (Pitcher Friendly)'}", style={
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'color': COLORS['text_light']
                }),
                html.Span(f" • Park Factor: {stats['summary'].get('park_factor', 1.0):.2f}", style={
                    'fontSize': '16px',
                    'color': COLORS['text_secondary'],
                    'fontStyle': 'italic'
                })
            ], style={
                'textAlign': 'center',
                'marginBottom': '24px',
                'padding': '12px',
                'backgroundColor': 'rgba(0,0,0,0.3)',
                'borderRadius': '12px',
                'border': f'1px solid {"#c8322f" if stats["summary"].get("park_factor", 1.0) > 1 else "#f9c74f"}'
            }),

            # Summary stats
            html.Div([
                html.Div([
                    html.Div([
                        html.Div("AVG", style={'fontSize': '12px', 'color': COLORS['text_light']}),
                        html.Div(f"{stats['summary']['AVG']:.3f}", style={
                            'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['oberlin_gold']
                        })
                    ], style={'textAlign': 'center', 'padding': '16px'})
                ], style={'width': '25%', 'display': 'inline-block'}),

                html.Div([
                    html.Div([
                        html.Div("OBP", style={'fontSize': '12px', 'color': COLORS['text_light']}),
                        html.Div(f"{stats['summary']['OBP']:.3f}", style={
                            'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['oberlin_gold']
                        })
                    ], style={'textAlign': 'center', 'padding': '16px'})
                ], style={'width': '25%', 'display': 'inline-block'}),

                html.Div([
                    html.Div([
                        html.Div("SLG", style={'fontSize': '12px', 'color': COLORS['text_light']}),
                        html.Div(f"{stats['summary']['SLG']:.3f}", style={
                            'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['oberlin_gold']
                        })
                    ], style={'textAlign': 'center', 'padding': '16px'})
                ], style={'width': '25%', 'display': 'inline-block'}),

                html.Div([
                    html.Div([
                        html.Div("OPS", style={'fontSize': '12px', 'color': COLORS['text_light']}),
                        html.Div(f"{stats['summary']['OBP'] + stats['summary']['SLG']:.3f}", style={
                            'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['oberlin_red']
                        })
                    ], style={'textAlign': 'center', 'padding': '16px'})
                ], style={'width': '25%', 'display': 'inline-block'})
            ], style={'marginBottom': '32px'}),

            # Outcome breakdown
            html.Div([
                html.H4("Outcome Breakdown", style={
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'color': COLORS['oberlin_gold'],
                    'marginBottom': '16px'
                }),

                # Note about park factor
                html.P(f"* {'↑' if stats['summary'].get('park_factor', 1.0) > 1 else '↓'} Hit outcomes adjusted by {abs(stats['summary'].get('park_factor', 1.0) - 1)*100:.0f}% for cage dimensions", style={
                    'fontSize': '12px',
                    'color': COLORS['text_secondary'],
                    'fontStyle': 'italic',
                    'marginBottom': '16px'
                }),

                # Create outcome bars
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(format_outcome(outcome), style={
                                'display': 'inline-block',
                                'width': '100px',
                                'fontSize': '14px',
                                'color': COLORS['text_light']
                            }),
                            html.Div(style={
                                'display': 'inline-block',
                                'width': f"{stats[outcome]['pct'] * 300}px",
                                'height': '24px',
                                'background': get_outcome_color(outcome),
                                'borderRadius': '12px',
                                'marginLeft': '12px',
                                'verticalAlign': 'middle'
                            }),
                            html.Span(f"{stats[outcome]['pct']*100:.1f}%", style={
                                'marginLeft': '12px',
                                'fontSize': '14px',
                                'fontWeight': '600',
                                'color': COLORS['oberlin_gold']
                            })
                        ], style={'marginBottom': '12px'})
                    ]) for outcome in ['1B', '2B', '3B', 'HR', 'BB', 'K', 'HBP', 'FO']
                ])
            ])
        ], animation_delay='0.2s')
    ])

def format_outcome(outcome):
    """Format outcome for display"""
    outcome_map = {
        '1B': 'Single',
        '2B': 'Double',
        '3B': 'Triple',
        'HR': 'Home Run',
        'BB': 'Walk',
        'K': 'Strikeout',
        'HBP': 'Hit by Pitch',
        'FO': 'Field Out'
    }
    return outcome_map.get(outcome, outcome)

def get_outcome_color(outcome):
    """Get color for outcome type"""
    color_map = {
        '1B': '#f9c74f',  # Gold for singles
        '2B': '#f77f00',  # Orange for doubles
        '3B': '#ee6c4d',  # Coral for triples
        'HR': '#c8322f',  # Oberlin Red for home runs
        'BB': '#6a994e',  # Green for walks
        'K': '#bc4749',  # Dark red for strikeouts
        'HBP': '#577590',  # Blue-gray for HBP
        'FO': '#495057'   # Gray for field outs
    }
    return color_map.get(outcome, '#666')

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)