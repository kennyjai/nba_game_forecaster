# import dependencies
import json
import datetime
import requests

# Function to scrape for nba game data
def todays_games():

    # get current date
    day = datetime.date.today()
    today = day.strftime('%Y%m%d')
    url_today = ("http://data.nba.net/10s/prod/v1/%s/scoreboard.json" %today)
    response = requests.get(url_today).json()

    # find the number of games in the day
    numofgames = response['numGames']

    # iterate through number of games to store in dictionary
    games = []
    x = 0

    while x < numofgames:
        y = response['games'][x]
        game = {}

        game['home_team'] = y['hTeam']['triCode']
        game['away_team'] = y['vTeam']['triCode']
        game['arena'] = y['arena']['name']
        game['start_time'] = y['startTimeEastern']
        game['home_record'] = y['hTeam']['win']+'-'+y['hTeam']['loss']
        game['away_record'] = y['vTeam']['win']+'-'+y['vTeam']['loss']
        game['date'] = day.strftime('%m/%d/%Y')
        
        # append game object to list
        games.append(game)
        x += 1

    return games
    
# Function to scrape for nba game data
def tomorrows_games():

    # initialize json
    # get tomorrows date
    add_a_day = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow = add_a_day.strftime('%Y%m%d')
    
    url_tomorrow = ("http://data.nba.net/10s/prod/v1/%s/scoreboard.json" %tomorrow)
    response = requests.get(url_tomorrow).json()

    # find the number of games in the day
    numofgames = response['numGames']

    # iterate through number of games to store in dictionary
    games = []
    x = 0

    while x < numofgames:
        y = response['games'][x]
        game = {}

        game['home_team'] = y['hTeam']['triCode']
        game['away_team'] = y['vTeam']['triCode']
        game['arena'] = y['arena']['name']
        game['start_time'] = y['startTimeEastern']
        game['home_record'] = y['hTeam']['win']+'-'+y['hTeam']['loss']
        game['away_record'] = y['vTeam']['win']+'-'+y['vTeam']['loss']
        game['date'] = add_a_day.strftime('%m/%d/%Y')
        
        # append game object to list
        games.append(game)
        x += 1

    return games

