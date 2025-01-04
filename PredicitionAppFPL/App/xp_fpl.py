# xp_fpl.py
import requests
import pandas as pd

def get_fpl_data():
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    json_data = response.json()

    players = json_data['elements']
    players_df = pd.DataFrame(players)

    return players_df

fpl_data = get_fpl_data()
fpl_data.to_csv('fpl_player_data.csv', index=False)
print('Data saved to fpl_player_data.csv')

fpl_data = pd.read_csv('fpl_player_data.csv')

url = 'https://fantasy.premierleague.com/api/fixtures/'
response = requests.get(url)
json_data = response.json()

fixtures_df = pd.DataFrame(json_data)
fixtures_df.to_csv('fixture_info.csv', index=False)
print('Fixture data saved to fixture_info.csv')

fixtures_df = pd.read_csv('fixture_info.csv')
upcoming_fixtures = fixtures_df[fixtures_df['finished'] == False]
next_gameweek = upcoming_fixtures['event'].min()

# Filter fixtures for the next gameweek only
fixtures_next_gameweek = fixtures_df[fixtures_df['event'] == next_gameweek]

# Save the filtered DataFrame to a CSV file (optional)
fixtures_next_gameweek.to_csv('fixtures_next_gameweek.csv', index=False)

print('Fixture data for next gameweek saved to fixtures_next_gameweek.csv')

team_difficulty_dict = {}
for index, row in fixtures_next_gameweek.iterrows():
  team_h = row['team_h']
  team_a = row['team_a']
  team_h_difficulty = row['team_h_difficulty']
  team_a_difficulty = row['team_a_difficulty']

  if team_h not in team_difficulty_dict:
    team_difficulty_dict[team_h] = team_h_difficulty
  if team_a not in team_difficulty_dict:
    team_difficulty_dict[team_a] = team_a_difficulty

difficulty_multiplier = {
    1: 1.2,  # easiest
    2: 1.1,
    3: 1.0,  # neutral
    4: 0.9,
    5: 0.8   # hardest
}

def calculate_expected_points(player_row):
  """Calculates expected points based on various factors."""

  # Get the player's team
  player_team = player_row['team']

  # Find the fixture difficulty for the player's team
  if player_team in team_difficulty_dict:
    fixture_difficulty = team_difficulty_dict[player_team]
  else:
    fixture_difficulty = 3  # Default to neutral if team not found

  # Use the difficulty multiplier based on the fixture difficulty
  if fixture_difficulty in difficulty_multiplier:
    difficulty_factor = difficulty_multiplier[fixture_difficulty]
  else:
    difficulty_factor = 1.0  # Default to neutral if difficulty not found

  # Positional Points
  if player_row['element_type'] == 1:  # Goalkeeper
    goal_points = 10
    assist_points = 3
    clean_sheet_points = 4
  elif player_row['element_type'] == 2:  # Defender
    goal_points = 6
    assist_points = 3
    clean_sheet_points = 4
  elif player_row['element_type'] == 3:  # Midfielder
    goal_points = 5
    assist_points = 3
    clean_sheet_points = 1
  elif player_row['element_type'] == 4:  # Forward
    goal_points = 4
    assist_points = 3
    clean_sheet_points = 0
  else:
    goal_points = 0
    assist_points = 0
    clean_sheet_points = 0

  # Minimum minutes threshold
  min_minutes = 200  # Example threshold - adjust as needed
  if player_row['minutes'] < min_minutes:
    return 0  # Return 0 if player does not meet the minimum minutes

  # Calculate games played (approximation) only if minutes are above a threshold
  games_played = player_row['minutes'] / 90

  # Expected Points based on Goals, Assists, Clean Sheets, etc.
  expected_points = (
      (player_row['goals_scored'] / games_played) * goal_points +
      (player_row['assists'] / games_played) * assist_points +
      (player_row['clean_sheets'] / games_played) * clean_sheet_points +
      (player_row['minutes'] / games_played) * 0.01  # Basic playing time contribution
  )

  # Adjust for fixture difficulty
  expected_points = expected_points * difficulty_factor

  # Add points for playing 60+ minutes
  if player_row['minutes'] >= 60:
    expected_points += 1

  return expected_points



fpl_data['expected_points'] = fpl_data.apply(calculate_expected_points, axis=1)
sorted_players_df = fpl_data.sort_values('expected_points', ascending=False)

print("\nTop Players:")
print(sorted_players_df[['web_name', 'expected_points']])
def map_element_type_to_position(element_type):
    if element_type == 1:
        return "GK"
    elif element_type == 2:
        return "DEF"
    elif element_type == 3:
        return "MID"
    elif element_type == 4:
        return "FWD"
    else:
        return "Unknown"

fpl_data['position'] = fpl_data['element_type'].apply(map_element_type_to_position)

# Add 'price' column by dividing 'now_cost' by 10
fpl_data['price'] = fpl_data['now_cost'] / 10

# Sort players by expected points
sorted_players_df = fpl_data.sort_values('expected_points', ascending=False)

#into CSV
# Create the filename using the next gameweek number
filename = f"xPoint_{next_gameweek}.csv"

# Select the relevant columns for the CSV
csv_data = sorted_players_df[['code', 'web_name', 'expected_points']]

# Save the data to a CSV file
csv_data.to_csv(filename, index=False)

print(f"Data saved to {filename}")


def get_top_10_players(df):
    return df.sort_values('expected_points', ascending=False).head(10)[['web_name', 'expected_points', 'position', 'price']]

def sorted_players(df):
    """Sorts players by expected points in descending order."""
    return df.sort_values('expected_points', ascending=False)

def get_top_players_by_position(df, position, top_n=5):
    """
    Gets the top N players for a specific position based on expected points.

    Args:
        df: The DataFrame containing player data.
        position: The position to filter by ('GK', 'DEF', 'MID', 'FWD').
        top_n: The number of top players to return.

    Returns:
        A DataFrame with the top N players for the specified position.
    """
    position_players = df[df['position'] == position].sort_values('expected_points', ascending=False).head(top_n)
    return position_players[['web_name', 'expected_points', 'price']]


