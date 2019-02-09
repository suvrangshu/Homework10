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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #----------------------------------------
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    print(last_date)

    year_ago = last_date - dt.timedelta(days=366)
    print(year_ago)

    prcp_date = session.query(Measurement.prcp,Measurement.date).filter(Measurement.date >= year_ago).\
                order_by(Measurement.date).all()
    #prcp_date2 = pd.DataFrame(prcp_date, columns=["Precipitation", "Date"])
    session.close()
    return jsonify(prcp_date)
    #----------------------------------------
    #prcp_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date).all()
    #dic = {i[0]:i[1] for i in prcp_date}
    #return jsonify(dic)
        

@app.route("/api/v1.0/stations")
def stations():
    station = session.query(Station.station,Station.name).all()
    session.close()
    return jsonify(station)
    #stations = session.query(Measurement.station).group_by(Measurement.station).all()
    #stations = [i[0] for i in stations]
   # return "Available Stations: \n {}".format(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    print(last_date)

       
    year_ago = last_date - dt.timedelta(days=366)
    
    tmp_date = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= year_ago).\
                 order_by(Measurement.date).all()
    #.order_by(Measurement.date.desc()).all()
    tobs = {i[0]:i[1] for i in tmp_date}
    #tobs = jsonify(tobs)
    session.close()
    return jsonify(tobs)
    #return "Temperature Observed from {} to {}: <br/> {}".format(last_date,year_ago,tobs)
    
@app.route("/api/v1.0/<start>")
def start_dt(start):
    trip_start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    
    #try:
    pd_val = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= trip_start_date).all()
#print(pd_val)
#    sdate = []
#     for i in pd_val:
#         start_dict = {}
#         start_dict["Min tobs"] = i.tobs
#         start_dict["Avg tobs"] = i.tobs
#         start_dict["Max tobs"] = i.tobs
#         sdate.append(start_dict)
    
    #session.close()        
    #return jsonify(pd_val)

    #except:
    if not pd_val:
        session.close()
        return jsonify({"error": f"Input date : {start} not found."}), 404
    else:
        session.close()
        return jsonify(pd_val)

    #session.close()
    #return jsonify(pd_val)


#@app.route("/api/v1.0/justice-league/<real_name>")
#def justice_league_character(real_name):/api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    
    trip_start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    trip_end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    
    #date_range = []
    pd_values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= trip_start_date).filter(Measurement.date <= trip_end_date).all()
    if pd_values:
        session.close()
        return jsonify(pd_values)
    
    session.close()
    return jsonify({"error": f"Input date : {start} not found."})
    
    
    


if __name__ == '__main__':
    app.run(debug=True)


