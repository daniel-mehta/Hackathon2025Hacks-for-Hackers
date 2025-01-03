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

team_difficulty_dict = {}
for index, row in fixtures_df[fixtures_df['event'] == next_gameweek].iterrows():
    team_difficulty_dict[row['team_h']] = row['team_h_difficulty']
    team_difficulty_dict[row['team_a']] = row['team_a_difficulty']

difficulty_multiplier = {1: 1.2, 2: 1.1, 3: 1.0, 4: 0.9, 5: 0.8}

def calculate_expected_points(player_row):
    player_team = player_row['team']
    fixture_difficulty = team_difficulty_dict.get(player_team, 3)
    difficulty_factor = difficulty_multiplier.get(fixture_difficulty, 1.0)

    if player_row['element_type'] == 1:
        goal_points = 10
        assist_points = 3
        clean_sheet_points = 4
    elif player_row['element_type'] == 2:
        goal_points = 6
        assist_points = 3
        clean_sheet_points = 4
    elif player_row['element_type'] == 3:
        goal_points = 5
        assist_points = 3
        clean_sheet_points = 1
    elif player_row['element_type'] == 4:
        goal_points = 4
        assist_points = 3
        clean_sheet_points = 0
    else:
        goal_points = 0
        assist_points = 0
        clean_sheet_points = 0

    games_played = max(player_row['minutes'] / 90, 1)

    expected_points = (
        (player_row['goals_scored'] / games_played) * goal_points +
        (player_row['assists'] / games_played) * assist_points +
        (player_row['clean_sheets'] / games_played) * clean_sheet_points +
        (player_row['minutes'] / games_played) * 0.01
    )

    expected_points *= difficulty_factor

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

def get_top_10_players(df):
    return df.sort_values('expected_points', ascending=False).head(10)[['web_name', 'expected_points', 'position', 'price']]

# Add 'position' column to represent player positions
