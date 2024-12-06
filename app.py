import dash
from dash import html
import os

app = dash.Dash(__name__)
server = app.server  # Gunicorn needs this

app.layout = html.Div([
    html.H1("Hello Render!")
])

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
