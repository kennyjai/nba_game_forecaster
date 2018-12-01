# import necessary libaries
import json
from flask import Flask, render_template, redirect
import nba_scraper
from pymongo import MongoClient
import numpy as np
import pandas as pd
import sklearn
import sklearn.datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from flask import Flask, render_template, request, redirect
from keras import backend as K
from keras.models import load_model
from keras.utils import to_categorical
import os, csv

# client = MongoClient('mongodb://localhost:27017/nba_db')
client = MongoClient('mongodb://kenneth:nba2018@ds123399.mlab.com:23399/nba_db')


app = Flask(__name__)
app.debug = True

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/send', methods=['GET','POST'])
def send():
    if request.method == 'POST':
        selected_home_name = request.form['hometeam']
        selected_away_name = request.form['awayteam']

    print('The home team is' + selected_home_name)
    print('The away team is' + selected_away_name)

    K.clear_session()
    
    nba_model = load_model("NBA_model.h5")

    csvpath = os.path.join("historical_stats.csv")

    with open(csvpath, 'r') as csvfile:

        # Split the data on commas
        csvreader = csv.reader(csvfile, delimiter=',')

        header = next(csvreader)

        # Loop through the data
        for row in csvreader:

            # Search for teams name in csv and retrieve respective data row
            if(selected_home_name == row[0]):
                global hometeamdata
                hometeamdata =row

            if(selected_away_name == row[0]):
                global awayteamdata
                awayteamdata =row
    #retrieve specific stats from the hometeamdata and awayteamdata lists
    team_stats = np.array([[hometeamdata[23], hometeamdata[18], hometeamdata[20], hometeamdata[17], hometeamdata[21], hometeamdata[22], awayteamdata[23], awayteamdata[18], awayteamdata[20], awayteamdata[17], awayteamdata[21], awayteamdata[22]]])
    
    home_points = hometeamdata[23]
    home_assists = hometeamdata[18]
    home_blocks = hometeamdata[20]
    home_rebounds = hometeamdata[17]
    home_turnovers = hometeamdata[21]
    home_fouls = hometeamdata[22]

    away_points = awayteamdata[23]
    away_assists = awayteamdata[18]
    away_blocks = awayteamdata[20]
    away_rebounds = awayteamdata[17]
    away_turnovers = awayteamdata[21]
    away_fouls = awayteamdata[22]

    final_encoded_prediction = nba_model.predict_classes(team_stats)
    if (final_encoded_prediction >0):
        output = "Wins!!!"
    else:
        output = "Loses!!!" 

    return render_template("results.html", output=output, hometeam=selected_home_name, awayteam=selected_away_name, home_points = home_points, home_assists = home_assists, home_blocks = home_blocks, home_rebounds = home_rebounds, home_turnovers = home_turnovers, home_fouls = home_fouls, away_points = away_points, away_assists = away_assists, away_blocks = away_blocks, away_rebounds = away_rebounds, away_turnovers = away_turnovers, away_fouls = away_fouls)

@app.route("/gathering_the_data")
def gathering_the_data():
    return render_template('gathering_the_data.html')

@app.route("/do_the_stats_matter")
def do_the_stats_matter():
    return render_template('do_the_stats_matter.html')

@app.route("/teaching_the_machine")
def teaching_the_machine():
    return render_template('teaching_the_machine.html')

@app.route("/conclusion")
def conclusion():
    return render_template('conclusion.html')

@app.route("/sources")
def sources():
    return render_template('sources.html')

@app.route("/about_the_project")
def about_the_project():
    return render_template('about_the_project.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

def machine_model(home_team, away_team):
    K.clear_session()

    # load nba model into nba_model variable
    nba_model = load_model("NBA_model.h5")

    # load historical_stats.csv of 2017-2018 team data into cvspath
    csvpath = os.path.join("historical_stats.csv")

    # open csv 
    with open(csvpath, 'r') as csvfile:

        # Split the data on commas
        csvreader = csv.reader(csvfile, delimiter=',')

        # skip the header
        header = next(csvreader)

        # Loop through the data
        for row in csvreader:

            # If the home teams' name in a row is equal to that which the user input
            if(home_team == row[0]):
                global hometeamdata
                # assign row to hometeamdata
                hometeamdata = row

            # If the away teams' name in a row is equal to that which the user input
            if(away_team == row[0]):
                # getawayStats(row)
                global awayteamdata
                awayteamdata = row

    # load both team stats into an array and assign to team_stats
    team_stats = np.array([[hometeamdata[23], hometeamdata[18], hometeamdata[20], hometeamdata[17], hometeamdata[21], hometeamdata[22], awayteamdata[23], awayteamdata[18], awayteamdata[20], awayteamdata[17], awayteamdata[21], awayteamdata[22]]])

    # use our nba model to predict the score and store in final_encoded_prediction
    prediction = nba_model.predict_classes(team_stats)

    return prediction

# upcoming games for today route
@app.route("/scrape_today", methods=['GET','POST'])
def scrape_today():

    # Drop data if database already exists and then run functions to scrape games
    client.nba_db.today.drop()
    today_games = nba_scraper.todays_games()

    # Insert games into todays database and insert into today
    client.nba_db.today.insert_many(today_games)
    today = client.nba_db.today.find()

    # return template and data
    return render_template("upcoming_games.html", today=today)


# upcoming games for tomorrow route
@app.route("/scrape_tomorrow", methods=['GET','POST'])
def scrape_tomorrow():

    # Drop data if database already exists and then run functions to scrape games
    client.nba_db.tomorrow.drop()
    games = nba_scraper.tomorrows_games()

    # Insert games into tomorrows database and insert into tomorrow
    client.nba_db.tomorrow.insert_many(games)
    tomorrow = client.nba_db.tomorrow.find()

    # return template and data
    return render_template("tmrw_games.html", tomorrow=tomorrow)

@app.route('/today_results', methods=['GET','POST'])
def today_results():

    today = client.nba_db.today.find()

    if request.method == 'POST':
        selected_home_name = request.form['hometeam']
        selected_away_name = request.form['awayteam']

    final_encoded_prediction = machine_model(selected_home_name, selected_away_name)

    if (final_encoded_prediction > 0):
        team1 = "WINS"
        team2 = "LOSES"
    else:
        team1 = "LOSES"
        team2 = "WINS"

    return render_template("todays_results.html", today=today, team1=team1, team2=team2, hometeam=selected_home_name, awayteam=selected_away_name)

@app.route('/tomorrow_results', methods=['GET','POST'])
def tomorrow_results():

    tomorrow = client.nba_db.tomorrow.find()

    if request.method == 'POST':
        selected_home_name = request.form['hometeam']
        selected_away_name = request.form['awayteam']

    final_encoded_prediction = machine_model(selected_home_name, selected_away_name)

    if (final_encoded_prediction > 0):
        team1 = "WINS"
        team2 = "LOSES"
    else:
        team1 = "LOSES"
        team2 = "WINS"

    return render_template("tomorrows_results.html", tomorrow=tomorrow, team1=team1, team2=team2, hometeam=selected_home_name, awayteam=selected_away_name)

if __name__ == "__main__":
    app.run()
