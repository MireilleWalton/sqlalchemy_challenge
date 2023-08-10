#Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import datetime as dt

#  ____________________
#  SET UP THE DATABASE
#  ____________________

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#  reflect database into a new model and reflect model

base = automap_base()

base.prepare(engine, reflect=True)

base.classes.keys()

#  create references to the tables

mes = base.classes.measurement
stn = base.classes.station


#  ____________________
#  FLASK SET UP
#  ____________________

# create the app, pass the name

app = Flask (__name__)

# define available routes

@app.route("/")
def home():
    print ("Server received request for homepage")
    return (f"HAWAII CLIMATE INFORMATION <br/>"
            "<br/>"
            f"Hello, thank you for visiting Hawaii's climate information page.  Here you can find information relating to the following topics:<br/>"
            "<br/>"
            f"____________________________________________<br/>"
            f"PRECIPITATION DATA (  /api/v1.0/precipitation  )<br/> "
            f"<br/>"
            f"Available data from 2016-08-22 to 2017-08-23."
            f"Result returns a dictionary including date, precipitation (mm), weather station name and elevation information.<br/>"
            "<br/>"
            "<br/>"
            f"____________________________________________<br/>"
            f"WEATHER STATIONS (  /api/v1.0/stations  )<br/>"
            "<br/>"
            f"Here you will find a list of weather stations on Hawaii.<br/> "
            f"Results return a dictionary including station name, station id, latitude and longitude.<br/>"
            "<br/>"
            "<br/>"
            f"____________________________________________<br/>"
            f"TOBS - STATION ID USC00519281 (  /api/v1.0/tobs_station_id_USC00519281  )<br/>"
            f"<br/>"
            f"Here you will find 12 months of temperature observations for Hawaii's most active weather station.<br/>"
            f"Results return a dictionary of dates and TOBS data from 2016-08-22.<br/>"
            "<br/>"
            "<br/>"
            f"____________________________________________<br/>"
            f"SEARCH TOBS DATA (  /api/v1.0/tobs_specify_from_date/<from_date>  )<br/>"
            f"-- (from specified date) -- <br/>" 
            "<br/>"
            f"Available data from 2010-01-01 to 2017-08-23.  To search, please enter date in 'YYYY-MM-DD' format only.<br/>"
            f"Information includes minimum, average and maximum temperature observations by weather station ID. <br/>"
            "<br/>"
            "<br/>"
            f"____________________________________________<br/>"
            f"SEARCH TOBS DATA (  /api/v1.0/tobs_specify_between_dates/<from_date><to_date>  )<br/>"
             f" -- (between specified start and end date) -- <br/>"
            "<br/>"
            F"Results will return a list of minimum, average and maximum temperature observations for all weather stations for the period specified.<br>"
            f"Available data from 2010-01-01 to 2017-08-23.<br/>"
            f"To search, please enter first and last dates in format 'YYYY-MM-DD/YYYY-MM-DD'.<br/>"
            "<br/>"
            )


#  ____________________
#  DEFINE PRECIPITATION ROUTE
#  ____________________

@app.route("/api/v1.0/precipitation")
def precipitation():

#  Create a query using a join to return rain data including station name and elevation

    session = Session(engine)

    prcp_sel = [mes.date, mes.prcp, stn.name, stn.elevation]
    prcp_12m = session.query(*prcp_sel).filter(mes.station == stn.station).\
    filter(mes.date > "2016-08-22").\
    order_by(mes.date).\
    all()

    session.close()

    rain_data = []  # Create an empty list to store dictionary results
    for date, prcp, station_name, elevation in prcp_12m:
        rain_dict = {}  # Create dictionary to hold key value pairs
        rain_dict["date"] = date
        rain_dict["prcp"] = prcp
        rain_dict["station_name"] = station_name
        rain_dict["elevation"] = elevation
        rain_data.append(rain_dict) # Append dictionary results in list

    return jsonify(rain_data)


#  ____________________
#  DEFINE STATIONS ROUTE
#  ____________________

@app.route("/api/v1.0/stations")
def stations():

    #  Create a query to return weather station information (name, station id, latitude & longitude)
    
    session = Session(engine)
    
    ttl_stns = session.query(stn.name, stn.station, stn.latitude, stn.longitude)

    session.close()

    stn_data = []   # Create an empty list to store dictionary results
    for name, station, lat, long in ttl_stns:
        stn_dict = {}   # Create dictionary to hold key value pairs
        stn_dict["name"] = name
        stn_dict["station id"] = station
        stn_dict["lat"] = lat
        stn_dict["long"] = long
        stn_data.append(stn_dict) # Append dictionary results in list

    return jsonify(stn_data)


#  ____________________
#  DEFINE TOBS ROUTE
#  ____________________

@app.route("/api/v1.0/tobs_station_id_USC00519281")
def tobs_station_id_USC00519281():

    #  DEFINE TOBS ROUTE - FROM SPECIFIED DATE -

    session = Session(engine)

    sel_tmp_12 = [mes.date, mes.tobs]
    tmp_12m = session.query(*sel_tmp_12).\
        filter(mes.station == "USC00519281").\
        filter(mes.date > "2016-08-22").\
        all()
    
    session.close()

    #  Return results in a list

    tmp_12m_data = list(np.ravel(tmp_12m))

    return jsonify(tmp_12m_data)


#  ____________________
#  DEFINE TOBS ROUTE - FROM SPECIFIED DATE - assistance received from AskBCS
#  ____________________

@app.route("/api/v1.0/tobs_specify_from_date/<from_date>")
def tobs_from_specified_date(from_date):

     # ensure date is returned correctly

    from_date = dt.datetime.strptime(from_date, "%Y-%m-%d")

     # Create a query which calculates min, avg, max temps from user specified date grouped by weather stations 

    session = Session(engine)

    sel = [mes.station,func.min(mes.tobs), func.avg(mes.tobs), func.max(mes.tobs)]
    sel_query = session.query(*sel).group_by(mes.station).filter(mes.date >= from_date).all()  
    print(sel_query)

    session.close()  
    
    #  Return results in a dictionary

    fd_data = []  # Create an empty list to store dictionary results
    for station, min_temp, avg_temp, max_temp in sel_query:
        fd_dict={} # Create dictionary to hold key value pairs
        fd_dict["station"] =  station
        fd_dict["min_temp"] = min_temp
        fd_dict["avg_temp"] = avg_temp
        fd_dict["max_temp"] = max_temp
        fd_data.append(fd_dict) # Append dictionary results in list
    
    result=jsonify(fd_data)    
    return result

             
#  ____________________
#   DEFINE TOBS FROM AND TO SPECIFIED DATE - assistance received from AskBCS re formatting date and url
#  ____________________

@app.route("/api/v1.0/tobs_specify_between_dates/<first_date>/<last_date>")
def tobs_specify_between_dates(first_date, last_date):

    # ensure dates are returned correctly

    first_date = dt.datetime.strptime(first_date, "%Y-%m-%d")
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")

     # Create a query which calculates min, avg, max temps for ALL stations between user specified dates
    
    session = Session(engine)

    sel2 = [func.min(mes.tobs), func.avg(mes.tobs), func.max(mes.tobs)]
    sel2_query = session.query(*sel2).filter(mes.date >= first_date).filter(mes.date <= last_date).all()

    session.close()

    #  Return results in a list 

    fd_td_data = list(np.ravel(sel2_query))
              
    return jsonify(fd_td_data) 

if __name__ == '__main__':
    app.run(debug=True)

