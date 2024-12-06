import base64
import io
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import matplotlib.pyplot as plt
import seaborn as sns

# File paths
DATA_FILE_PATH = "spotify_top_songs_audio_features.csv"

# Function to load and preprocess data
def load_and_preprocess_data(file_path):
    """
    Load the dataset and preprocess it by adding a popularity category column.
    """
    data = pd.read_csv(file_path)
    data['popularity_category'] = pd.qcut(data['streams'], q=3, labels=['Low', 'Medium', 'High'])
    return data

# Function to generate heatmap image
def generate_heatmap_image(data):
    """
    Generate a heatmap image for Key and Mode combinations.
    """
    plt.figure(figsize=(10, 6))
    heatmap_data = pd.crosstab(data['key'], data['mode'])
    sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='Blues')
    plt.title("Key and Mode Combinations")
    plt.xlabel("Mode")
    plt.ylabel("Key")
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    heatmap_image = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return heatmap_image

# Load and preprocess data
df = load_and_preprocess_data(DATA_FILE_PATH)
heatmap_image = generate_heatmap_image(df)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Spotify Music Dashboard"

# App layout
app.layout = html.Div(
    style={'backgroundColor': '#f4f4f4', 'font-family': 'Arial'},
    children=[
        html.H1("Spotify Music Dashboard 🎵", style={'textAlign': 'center', 'color': 'green'}),
        html.H4("Explore Spotify's top songs with interactive visuals.", style={'textAlign': 'center'}),

        # Top Songs by Weeks on Chart
        html.Div([
            dcc.Graph(
                id='top-10-bar-chart',
                config={'displayModeBar': False}
            )
        ]),

        # Streams vs. Weeks on Chart
        html.Div([
            dcc.Graph(
                id='streams-scatter-plot',
                config={'displayModeBar': True}
            )
        ]),

        # Danceability by Popularity Category
        html.Div([
            dcc.Graph(
                id='violin-plot',
                config={'displayModeBar': False}
            )
        ]),

        # Key and Mode Combinations (Static Heatmap)
        html.Div([
            html.H3("Key and Mode Combinations", style={'textAlign': 'center'}),
            html.Img(
                src=f"data:image/png;base64,{heatmap_image}",
                style={'display': 'block', 'margin': '0 auto', 'max-width': '80%'}
            )
        ])
    ]
)

# Callback to update the Top 10 bar chart
@app.callback(
    Output('top-10-bar-chart', 'figure'),
    Input('top-10-bar-chart', 'id')
)
def update_bar_chart(_):
    """
    Update the bar chart for top 10 songs by weeks on chart with artist name in hover info.
    """
    top_10 = df.nlargest(10, 'weeks_on_chart')
    fig = px.bar(
        top_10,
        x='weeks_on_chart',
        y='track_name',
        orientation='h',
        color='track_name',
        title='Top 10 Songs by Weeks on Chart',
        hover_data={'artist_names': True, 'weeks_on_chart': True}
    )
    fig.update_layout(showlegend=False)
    return fig

# Callback to update the scatter plot
@app.callback(
    Output('streams-scatter-plot', 'figure'),
    Input('streams-scatter-plot', 'id')
)
def update_scatter_plot(_):
    """
    Update the scatter plot for streams vs. weeks on chart with hover info and zoom capability.
    """
    fig = px.scatter(
        df, x='streams', y='weeks_on_chart',
        color='popularity_category',
        log_x=True,
        title='Streams vs. Weeks on Chart (Log Scale)',
        hover_data={'track_name': True, 'streams': True, 'weeks_on_chart': True}
    )
    fig.update_traces(marker=dict(size=8))
    fig.update_layout(showlegend=True)
    return fig

# Callback to update the violin plot
@app.callback(
    Output('violin-plot', 'figure'),
    Input('violin-plot', 'id')
)
def update_violin_plot(_):
    """
    Update the violin plot for danceability by popularity category.
    """
    fig = px.violin(
        df, x='popularity_category', y='danceability',
        color='popularity_category', box=True, points=False
    )
    fig.update_traces(meanline_visible=True)
    fig.update_layout(
        title="Danceability by Popularity Category"
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
