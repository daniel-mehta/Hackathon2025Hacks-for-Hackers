"""
This module defines a FastAPI application for the Fantasy Premier League (FPL) Prediction App.

Routes:
    - GET /: Returns a welcome message.
    - GET /top-10-players: Returns the top 10 players based on expected points.
    - GET /all-players: Returns a sorted list of all players with their data.
    - GET /best-per-position: Returns the top players for each position (GK, DEF, MID, FWD) based on expected points.

The application uses functions from the xp_fpl module to fetch and process FPL data.
"""

from fastapi import FastAPI
from xp_fpl import (
    get_fpl_data,
    calculate_expected_points,
    get_top_10_players,
    sorted_players_df,
    get_top_players_by_position
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to FPL Prediction App!"}

@app.get("/top-10-players")
def fetch_top_10_players():
    top_10 = get_top_10_players(sorted_players_df)
    return top_10.to_dict(orient='records')

@app.get("/all-players")
def fetch_sorted_players():
    clean_df = sorted_players_df.replace([float("inf"), float("-inf")], None).fillna(0)
    return clean_df.to_dict(orient='records')

@app.get("/best-per-position")
def fetch_get_top_players_by_position():
    positions = ['GK', 'DEF', 'MID', 'FWD']
    results = {}
    for pos in positions:
        top_players = get_top_players_by_position(sorted_players_df, pos)
        results[pos] = top_players.to_dict(orient='records')
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
