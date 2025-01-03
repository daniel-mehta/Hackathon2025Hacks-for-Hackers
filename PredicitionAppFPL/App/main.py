from fastapi import FastAPI
import pandas as pd
from typing import List, Dict
from xp_fpl import (  # Assuming the Colab code is saved in colab_code.py
    get_fpl_data,
    calculate_expected_points,
    get_top_players_by_position,
    get_top_10_players,
    next_gameweek,
    sorted_players
)

# Initialize FastAPI app
app = FastAPI()

# Load data once at startup
fpl_data = get_fpl_data()
fpl_data['expected_points'] = fpl_data.apply(calculate_expected_points, axis=1)

# Endpoint to fetch top players by position
@app.get("/top-players/{position}")
def fetch_top_players(position: str, top_n: int = 5):
    """Fetch the top N players for a given position."""
    if position.upper() not in ['GK', 'DEF', 'MID', 'FWD']:
        return {"error": "Invalid position. Choose from GK, DEF, MID, FWD."}
    top_players = get_top_players_by_position(sorted_players, position.upper(), top_n)
    return top_players.to_dict(orient='records')

# Endpoint to fetch top 10 players overall
@app.get("/top-10-players")
def fetch_top_10_players():
    """Fetch the top 10 players overall."""
    top_10 = get_top_10_players(sorted_players)
    return top_10.to_dict(orient='records')

# Endpoint to fetch next gameweek info
@app.get("/next-gameweek")
def fetch_next_gameweek():
    """Fetch the next gameweek number."""
    return {"next_gameweek": next_gameweek}

# Endpoint to fetch all players
@app.get("/all-players")
def fetch_all_players():
    """Fetch all players with expected points."""
    return sorted_players.to_dict(orient='records')

# Endpoint to fetch player details by name
@app.get("/player/{name}")
def fetch_player(name: str):
    """Fetch details of a player by name."""
    player = sorted_players[sorted_players['web_name'].str.contains(name, case=False, na=False)]
    if player.empty:
        return {"error": f"Player with name {name} not found."}
    return player.to_dict(orient='records')

# Endpoint to fetch data for the next gameweek
@app.get("/next-gameweek-fixtures")
def fetch_next_gameweek_fixtures():
    """Fetch fixture data for the next gameweek."""
    fixtures = sorted_players[sorted_players['event'] == next_gameweek]
    return fixtures.to_dict(orient='records')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
