#Author : Suv Ghosh
#------------------------------------------------

import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:///hawaii.sqlite")
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)



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

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-02-03<br/>"
        f"/api/v1.0/2017-06-10/2017-06-25<br/>"
    )

#Convert the query results to a Dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    #----------------------------------------
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    

    year_ago = last_date - dt.timedelta(days=366)
    

    prcp_date = session.query( Measurement.prcp,Measurement.date).filter(Measurement.date >= year_ago).\
                order_by(Measurement.date).all()
    
    prcp1 = pd.DataFrame(prcp_date, columns=["Precipitation", "Date"])

    prcp1.set_index(["Date"], inplace = True, drop = True)

    prcp1.sort_index(inplace=True)
    prcp_dict = prcp1.to_dict()
    session.close() #Session close, to ensure the page doesnt crash, if called again
    return jsonify(prcp_dict)
    #----------------------------------------

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    station = session.query(Station.station,Station.name).all()
    session.close()
    return jsonify(station)
    
#query for the dates and temperature observations from a year from the last data point.
@app.route("/api/v1.0/tobs")
def tobs():
    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
           
    year_ago = last_date - dt.timedelta(days=366)
    
    tmp_date = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= year_ago).\
                 order_by(Measurement.date).all()
    
    
    #tobs = {i[0]:i[1] for i in tmp_date}
    
    tobs1 = pd.DataFrame(tmp_date, columns=['temperature', 'date'])
    tobs1.set_index('date', inplace=True)
    out_tobs = tobs1.to_dict()
    
    session.close()
    return jsonify(out_tobs)
    #return "Temperature Observed from last_date,year_ago,tobs

#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_dt(start):
    
    trip_start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        
    pd_val = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= trip_start_date).all()
    minT, avgT, maxT = pd_val[0] 
    #show message incase date is not in file
    if minT is None:
        session.close()
        return jsonify({"error": f"Input date : {start} not found."})
        
        
    session.close()
    return jsonify(pd_val)
        
    #return jsonify({"error": f"Input date : {start} not found."}), 404


#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    
    #get the first date from the data file
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()
    first_date = dt.datetime.strptime(first_date[0], '%Y-%m-%d')
    #get the last date from the file
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    
    trip_start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    trip_end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    
    
    pd_values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= trip_start_date).filter(Measurement.date <= trip_end_date).all()
    minT, avgT, maxT = pd_values[0] 
    #show message incase date is not in file
    if minT is None: 
        session.close()
        return jsonify({"error": f"Input date : {start},{end} not found.Valid range is {first_date}- {last_date}"})
    
    session.close()
    return jsonify(pd_values)

    
    
            
    


if __name__ == '__main__':
    app.run(debug=True)


