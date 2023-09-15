####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################
# import local files
import db
import constants.constants as constants
import authentication.authorise_token as auth
import models.profile_record as profile_record
# system imports
from flask import Request, jsonify
from sqlalchemy import text, func, update, exc, orm
from geoalchemy2 import elements, functions
import geojson
from typing import TypeVar, List


def capture_profile_data(request: Request, session: orm.Session):
    if (auth.auth_token(request) == False):
        return jsonify({"result": "token authentication failed"})
    # if we get here, then the token is valid and we can get the record
    data = request.json
    user_id = data["user_id"]
    # check if the user is already in the database
    try:
        current_data = (session
                        .query(profile_record.Profile_Record)
                        .filter(profile_record.Profile_Record.user_id == user_id).one())
        # if this doesn't throw, it means an entry for them has already been created.
        # Simply update their details
        total_minutes = current_data.total_minutes + \
            float(data["total_minutes"])
        num_recordings = int(current_data.num_recordings + 1)
        data_point = {profile_record.Profile_Record.total_minutes: total_minutes,
                      profile_record.Profile_Record.num_recordings: num_recordings}
        # now commit the update to the db
        try:
            session.execute(update(profile_record.Profile_Record).where(
                profile_record.Profile_Record.user_id == data["user_id"]).values(data_point))
            session.commit()
            return jsonify({"result": "success"})

        except Exception as e:
            print(e)
            session.rollback()
            return jsonify({"result": "failed"})

    except exc.NoResultFound as e:
        # there is no previously existing entry, make a new one
        # the total number of recordings in this case will obviously be set to 1
        data_point = profile_record.Profile_Record(user_id=user_id,
                                                   email=data["email"],
                                                   num_recordings=1,
                                                   total_minutes=data["total_minutes"])
        # now commit the new record to the database
        try:
            session.add(data_point)
            session.commit()
            return jsonify({"result": "success"})

        except Exception as e:
            print(e)
            session.rollback()
            return jsonify({"result": "failed"})


def get_profile_data(request: Request, session: orm.Session):
    if (auth.auth_token(request) == False):
        return jsonify({"result": "token authentication failed"})

    data = request.json
    user_id = data["user_id"]
    try:
        result = session.query(profile_record.Profile_Record).where(
            profile_record.Profile_Record.user_id == user_id).one()
        return jsonify(result.asdict())

    except exc.NoResultFound as e:
        return jsonify({"result": "incorrect user_id, no result found"})
