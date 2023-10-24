# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# All app routes for the root, precipitation, stations, tobs, start and end dates
@app.route("/")

def welcome():
    """List of all available api routes."""
    return (
        f"Available Routes for Hawaii Weather Data:<br/><br>"
        f"- Precipitation: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"- Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"- TOBS: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"- Temp format for all Date Range(s): /api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd<br>"
        f"NOTE: End date does data analysis through 08/23/17<br>" 
    )

# Precipitation app routes
@app.route("/api/v1.0/precipitation")

def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data for last year"""
    
    # Create new variable to store results from query to Measurement table for prcp and date columns
    precipitation_qresults = session.query(Measurement.prcp, Measurement.date).all()

    # Close session
    session.close()

    # Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value.
    precipitaton_values = []
    for prcp, date in precipitation_qresults:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict["date"] = date
        precipitaton_values.append(precipitation_dict)
   
    # Return the JSON representation of your dictionary
    return jsonify(precipitaton_values) 

# Stations app routes
@app.route("/api/v1.0/stations")

def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all the active Weather stations in Hawaii"""

    # Create new variable to store results from query to Station table for station and id columns
    station_qresults = session.query(Station.station,Station.id).all()

    # Close session
    session.close()  
    
    # Convert the query results from your station analysis to a dictionary using id as the key and station as the value.
    stations_values = []
    for station, id in station_qresults:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['id'] = id
        stations_values.append(stations_dict)

    # Return the JSON representation of your dictionary
    return jsonify (stations_values) 

# TOBS app routes 
@app.route("/api/v1.0/tobs")

def tobs():
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of the last 12 months of temperature observation data for the most active station""" 

    # Create query to find the last date in the database    
    most_recent_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first() 
    print(most_recent_date)
        
    # Checking to see if the last year was displayed correctly by creating a dictionary in JSON format
    most_recent_values = []
    for date in most_recent_date:
        most_recent_dict = {}
        most_recent_dict["date"] = date
        most_recent_values.append(most_recent_dict) 
    print(most_recent_values)
    
    # Checking for date time differences between ["2017-08-23" & 365 days]
    start_qdate = dt.date(2017, 8, 23)-dt.timedelta(days=365) 
    print(start_qdate) 
    
    # Create query to find most active station in the database 
    active_station= session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).first()
    most_active_station = active_station[0] 

    session.close() 
    
    print(most_active_station)
    
    # Create a query to find dates and tobs for the most active station (USC00519281) within the last year
    tobs_most_recent_date = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date > start_qdate).\
        filter(Measurement.station == most_active_station) 
    

    # Creating dictionary values for date, tobs, and station number queried above
    tobs_most_recent_values = []
    for date, tobs, station in tobs_most_recent_date:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_dict["station"] = station
        tobs_most_recent_values.append(tobs_dict)

    # Return a JSON list of temperature observations for the previous year    
    return jsonify(tobs_most_recent_values) 

# Start/End Date app routes
@app.route("/api/v1.0/trip/<start_date>")
def startdate(start_date, end_date='2017-08-23'):
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date range
    # If no end date is provided, the function defaults to 2017-08-23.
    session = Session(engine)
    start_date = '2016-08-23'
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results otherwise return an error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date {start_date} not found! Date not formatted correctly @ YYYY-MM-DD."}), 404
  
@app.route("/api/v1.0/trip/<start_date>/<end_date>")
def startenddate(start_date, end_date='2017-08-23'):
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end date range
    # If no valid end date is provided, the function defaults to 2017-08-23.

    session = Session(engine)
    start_date = '2016-08-23'
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results otherwise return an error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date(s) not found! Invalid date range/Date(s) not formatted correctly @ YYYY-MM-DD."}), 404
  

if __name__ == '__main__':
    app.run(debug=True)