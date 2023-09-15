####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################
"""
Functions related to the Locations Table.
This table keeps track of the user and their location at set time intervals.
See the location_record model for more details on this table.
"""
# import local files
import db
import constants.constants as constants
import authentication.authorise_token as auth
import models.locations_record as location_record
# system imports
from flask import Request, jsonify
from sqlalchemy import text, func, update, exc, orm
from geoalchemy2 import elements, functions
import geojson
from typing import TypeVar, List

DB_Result = TypeVar('DB_Result', dict, None)


def capture_location_data(request: Request, session: orm.Session):
    if not auth.auth_token(request):
        return jsonify({"result": "token authentication failed"})

    data = request.json
    location = elements.WKTElement("POINT({lng} {lat})".format(lat=data["latitude"], lng=data["longitude"]),
                                   srid=constants.SRID)
    data_point = location_record.Locations_Record(user_id=data["user_id"],
                                                  utc_time_ms=data["utc_time_ms"],
                                                  location=location,
                                                  latitude=data["latitude"],
                                                  longitude=data["longitude"],
                                                  altitude=data["altitude"],
                                                  timestamp=data["timestamp"])
    try:
        session.add(data_point)
        session.commit()
        return jsonify({"result": "success"})

    except Exception as e:
        res = {'code': 500, 'errorType': 'Internal Server Error',
               'errorMessage': e.message if hasattr(e, 'message') else f'{e}'}

        print(e)
        session.rollback()

        return jsonify(res)


def get_location_data(request: Request, session: orm.Session):
    """
    Returns all location data records for a particular user in the form of a
    list of Location Record like objects.
    If the user_id is not in the database, the returned list will be empty.
    """
    if not auth.auth_token(request):
        return jsonify({"result": "token authentication failed"})

    data = request.json
    try:
        # don't get the timestamp, since that's not an important var that
        # should face the user
        records = (session.query(location_record.Locations_Record.user_id,
                                 location_record.Locations_Record.utc_time_ms,
                                 location_record.Locations_Record.latitude,
                                 location_record.Locations_Record.longitude)
                   .filter(location_record.Locations_Record.user_id == data["user_id"])
                   .all())

        results = []
        for record in records:
            locationObject = {
                'user_id': record.user_id,
                'utc_time_ms': record.utc_time_ms,
                'lat': record.latitude,
                'lng': record.longitude
            }
            results.append(locationObject)

        return jsonify(results)

    except Exception as e:
        session.rollback()
        return jsonify({"result": "unknown error. Query failed."})
