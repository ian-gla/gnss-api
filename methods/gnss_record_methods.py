####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################
"""
Functions related to the GNSS Data Table.
The functions here should facilitate the collection of GNSS data from client
smartphones, as well as allow for the querying of data from the database so that
the various maps and visualisation tools can work.

Note: these methods may need to be optimised somehow.
Consider:
- saving up data, bundling it together and doing bulk writes using the core lib
- async io?
- websocket dedicated to get or put method?
"""
# import local files
import db
import constants.constants as constants
import authentication.authorise_token as auth
import models.gnss_record as gnss_model
# system imports
from flask import Request, jsonify
from sqlalchemy import orm, null
from geoalchemy2 import elements


# gnss_record_queue = []
def capture_gnss_data(request: Request, session: orm.Session):
    if (auth.auth_token(request) == False):
        return jsonify({"result": "token authentication failed"})
    # if we get here, then the token is valid and we can get the record
    data = request.json
    print(data)
    # create the gnss_record object and enqueue it
    data_point = gnss_model.GNSS_Record(user_id=data["user_id"],
                                        timestamp=data["timestamp"],
                                        svid=data["svid"],
                                        constellation=data["constellation"],
                                        cn0_dBHz=data["cn0_dBHz"],
                                        # the fields that are collected via .get are the ones which are only available on
                                        # newer Android OSs.
                                        baseband_cn0_dBHz=data.get(
                                            "baseband_cn0_dBHz"),
                                        snr_dB=data.get("snr_dB"),
                                        state=data["state"],
                                        pseudorange_rate_mps=data["pseudorange_rate_mps"],
                                        pseudorange_rate_uncertainty_mps=data["pseudorange_rate_uncertainty_mps"],
                                        accumulated_deltarange=data["accumulated_deltarange"],
                                        accumulated_deltarange_metres=data["accumulated_deltarange_metres"],
                                        accumulated_deltarange_uncertainty_metres=data[
                                            "accumulated_deltarange_uncertainty_metres"],
                                        carrier_frequency_hz=data.get(
                                            "carrier_frequency_hz"),
                                        carrier_cycles=data.get(
                                            "carrier_cycles"),
                                        carrier_phase=data.get(
                                            "carrier_phase"),
                                        carrier_phase_uncertainty=data.get(
                                            "carrier_phase_uncertainty"),
                                        altitude=data.get("altitude"),
                                        speed=data.get("speed"),
                                        agc_level=data.get("agc_level"),
                                        multipath_indicator=data["multipath_indicator"],
                                        time_nanos=data["time_nanos"],
                                        time_uncertainty_nanos=data.get(
                                            "time_uncertainty_nanos"),
                                        full_bias_nanos=data.get(
                                            "full_bias_nanos"),
                                        bias_nanos=data.get("bias_nanos"),
                                        drift_nanos_ps=data.get(
                                            "drift_nanos_ps"),
                                        received_svtime_nanos=data["received_svtime_nanos"],
                                        received_svtime_uncertainty_nanos=data.get("received_svtime_uncertainty_nanos"))

    # gnss_record_queue.append(data_point)
    # if (len(gnss_record_queue) > 1):
    #     db.session.add_all(gnss_record_queue)
    #     try:
    #         db.session.commit()
    #         gnss_record_queue.clear()
    #         return jsonify({"result":"success"})
    try:
        session.add(data_point)
        session.commit()
        return jsonify({"result": "success"})

    except Exception as e:
        # gnss_record_queue.clear()
        res = {'code': 500, 'errorType': 'Internal Server Error',
               'errorMessage': e.message if hasattr(e, 'message') else f'{e}'}

        print(e)
        session.rollback()
        return jsonify(res)


def create_base_query(session):
    return session.query(gnss_model.GNSS_Record.user_id,
                         gnss_model.GNSS_Record.timestamp,
                         gnss_model.GNSS_Record.svid,
                         gnss_model.GNSS_Record.constellation,
                         gnss_model.GNSS_Record.cn0_db)


# def get_gnss_record_from_user(request: Request, session: orm.Session):
#     if (auth.auth_token(request) == False):
#         return jsonify({"result":"token authentication failed"})
#
#     # parse the arguments to see what the user actually wants:
#     user_id = request.args.get("user_id", default=None, type=str)
#     start_time = request.args.get("start", default=None, type=str)
#     end_time = request.args.get("end", default=None, type=str)
#     lat = request.args.get("lat", default=None, type=Float)
#     lng = request.args.get("lng", default=None, type=Float)
#     svid = request.args.get("svid", default=None, type=str)
#     constellation = request.args.get("constellation", default=None, type=str)
#     cn0_db = request.args.get("cn0_db", default=None, type=str)
#
#     if (user_id & start_time==None & end_time==None &  lat==None & lng==None & svid==None & constellation==None & cn0_db==None):
#         records = (create_base_query(session)
#                           .filter(user_id=user_id)
#                           .all())
#         results = []
#         for record in records:
#             point = geojson.loads(record.location)
#             gnss_record_result = {"user_id": record.user_id,
#                                   "timestamp": record.timestamp,
#                                   "lat": point["coordinates"][1],
#                                   "lng": point["coordinates"][0],
#                                   "svid":record.svid,
#                                   "constellation": record.constellation,
#                                   "cn0_db": record.cn0_db}
#             results.append(gnss_record_result)
#         return jsonify(results)
#
#     if (user_id & start_time & lat==None & lng==None & svid==None & constellation==None & cn0_db==None):
#         records = (create_base_query(session)
#                           .filter(user_id=user_id)
#                           .all())
#         results = []
#         for record in records:
#             point = geojson.loads(record.location)
#             gnss_record_result = {"user_id": record.user_id,
#                                   "timestamp": record.timestamp,
#                                   "lat": point["coordinates"][1],
#                                   "lng": point["coordinates"][0],
#                                   "svid":record.svid,
#                                   "constellation": record.constellation,
#                                   "cn0_db": record.cn0_db}
#             results.append(gnss_record_result)
#         return jsonify(results)
