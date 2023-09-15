#!/usr/bin/env python

####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################

# main.py
import os
from flask import Flask, request, jsonify
from sqlalchemy import text, func, update, exc
import shapely.wkt
import geojson
# Import the Firebase service
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from geoalchemy2 import elements, functions
# import local files
import db
import models.gnss_record as gnss_model
import models.locations_record as location_record
import models.profile_record as profile_record
import methods.location_record_methods as loc_rec_meths
import methods.gnss_record_methods as gnss_rec_meths
import methods.profile_record_methods as profile_rec_meths
import methods.receiver_points_methods as recv_points_meths

app = Flask(__name__)
cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
default_app = firebase_admin.initialize_app(
    cred, options={"projectId": "crowdsourcedgnssdataproject"})

SRID = 4326


@app.route("/test")
def home():
    # db.open_connection()
    engine = db.init_connection_engine()
    result = engine.execute(
        text(
            "SELECT * FROM songs;"
        )
    )
    counter = 0
    for row in result.fetchall():
        print(row)
        counter += 1

    if (counter == 1):
        return "Success"
    else:
        return "FAILED TO CONNECT"


@app.route("/create_table", methods=["POST"])
def create_new_table():
    db.create_gnss_records()
    # db.create_location_records()
    # db.create_recv_points_records()
    return "Success"

# gnss_record_queue = []


@app.route("/capture_gnss_data", methods=["POST"])
def capture_gnss_data():
    return gnss_rec_meths.capture_gnss_data(request, db.session)


@app.route("/capture_location_data", methods=["POST"])
def capture_location_data():
    return loc_rec_meths.capture_location_data(request, db.session)


@app.route("/get_location_data", methods=["GET"])
def get_location_data():
    return loc_rec_meths.get_location_data(request, db.session)


@app.route("/capture_profile_data", methods=["POST"])
def capture_profile_data():
    return profile_rec_meths.capture_profile_data(request, db.session)


@app.route("/get_profile_data", methods=["POST"])
def get_profile_data():
    return profile_rec_meths.get_profile_data(request, db.session)


# this function is meant to be run by the App Engine Cron scheduler.
# it takes the data in the location and gnss_record databases and merges them
# into a single database, with only the information that Terry's code needs
# @app.route("/data_sweep", methods=["POST", "GET"])
# def run_data_sweep():
#     recv_points_meths.create_add_receiver_points()
#     return jsonify({"result":"success"})


if __name__ == "__main__":
    app.run(debug=True)
