from fastapi import FastAPI
from xp_fpl import (
    get_fpl_data,
    calculate_expected_points,
    get_top_10_players,
    sorted_players_df
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
