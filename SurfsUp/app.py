# Import the dependencies.
import flask
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime as dt

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    #Set routes
    return (
            f"Welcome to Hawaii Precipitaion Analysis<br>"
            f"/api/v1.0/precipitation<br>"
            f"/api/v1.0/stations<br>"
            f"/api/v1.0/tobs<br>"
            f"/api/v1.0/start<br>"
            f"/api/v1.0/start/end<br>"
)

#Returns json with the date as the key and the value as the precipitation.
#Only returns the jsonified precipitation data for the last year in the database 
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    #Determine last 12 months
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #query to retrieve the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_year).all()
    session.close()

    #create precipitaton dictionarya
    precip_dict = []
    for date, prcp in results:
        precip_dict.append({date: prcp})
    return jsonify(precip_dict)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    #return a JSON list of stations from the dataset.
    results = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    #Determine last 12 months for station USC00519281
    prior_year = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most-active (USC00519281) station for the previous year of data.
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= prior_year).all()
    session.close()
    all_tobs = list(np.ravel(results))
    return jsonify(all_tobs)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    #Define start
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()

    #Return a JSON list of the the min, max, and average temperatures calculated from the given start date to the end of the dataset.
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()
    session.close()
    min_avg_max_tobs = list(np.ravel(results))
    return jsonify(min_avg_max_tobs)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)
  
    #Define start and end 
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end = dt.datetime.strptime(start, '%Y-%m-%d').date()

    #Returns the min, max, and average temperatures calculated from the given start date to the given end date 
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    session.close()
    start_end = list(np.ravel(results))
    return jsonify(start_end)

if __name__ == '__main__':
    app.run(debug=True)