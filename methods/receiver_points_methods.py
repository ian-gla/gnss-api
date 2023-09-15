# """
# Functions for joining the data from the gnss and location databases, in order
# to create the cleaned database that contains only the data the MapBuilder
# code requires.
# """
# # import local files
# import db
# import constants.constants as constants
# import authentication.authorise_token as auth
# import models.gnss_record as gnss_model
# # system imports
# from flask import Request, jsonify
# from sqlalchemy import engine, orm, null
# from geoalchemy2 import elements
# import pandas as pd
# import geopandas as gpd
# import gnssmapper as gm
#
# from models.receiver_points_record import ReceiverPoints_Record
#
#
# def get_inputs_as_pandas(db_engine: engine.Engine) -> (pd.DataFrame, gpd.GeoDataFrame):
#     """
#     Returns the new entries from the gnss_records and locations_records database
#     where "new" is defined as those having been captured "today" (since this is
#     part of a cron job that will run at the end of each day).
#     """
#     # create the query. Manually name all columns so that I can easily delete
#     # the ones I end up not using.
#     gnss_records_query = 'SELECT user_id, timestamp, svid, constellation, \
#                           "cn0_dBHz", "baseband_cn0_dBHz", "snr_dB", state, \
#                           "pseudorange_rate_mps", "pseudorange_rate_uncertainty_mps", \
#                           "accumulated_deltarange", "accumulated_deltarange_metres", \
#                           "accumulated_deltarange_uncertainty_metres", "carrier_frequency_hz", \
#                           "carrier_cycles", "carrier_phase", "carrier_phase_uncertainty", \
#                           altitude, speed, "agc_level", "multipath_indicator", \
#                           "time_nanos", "time_uncertainty_nanos", "full_bias_nanos", \
#                           "bias_nanos", "leap_seconds", "drift_nanos_ps", "received_svtime_nanos", \
#                           "received_svtime_uncertainty_nanos" FROM gnss_records where timestamp between \
#                           current_date and current_date+1 order by timestamp desc'
#
#     gnss_records = pd.read_sql_query(gnss_records_query, db_engine)
#     gnss_records.to_csv("gnss_records_2022_04_25.csv")
#     # print(gnss_records.head())
#
#     location_records_query = 'SELECT user_id, "(UTC)TimeInMs", timestamp, latitude, longitude, altitude \
#                               FROM location_records where timestamp between current_date and current_date+1 \
#                               order by timestamp desc'
#     location_records = pd.read_sql_query(location_records_query, db_engine)
#     location_records.to_csv("location_records_2022_04_25.csv")
#
#     # print(location_records.head())
#     return gnss_records, location_records
#
#
# def make_observation_data(gnss_record: pd.DataFrame) -> pd.DataFrame:
#     """
#     Takes in the gnss_records dataframe and creates an 'observation' dataframe.
#     In other words, it calculates and adds the following columns/attributes:
#     #   - svid (this gets changed to be ISG format, i.e. G02 etc. using constellation and svid as inputs)
#     #   - rx (receiver time)
#     #   - tx (transmission time)
#     #   - time (GPS time converted to UTC) (calculated using rx,which is calculated using time_nanos and fullbias_nanos
#     #   - time_ms (same as time, but in miliseconds)
#     #   - pr (pseudorange)
#     """
#     # now we want to make sure that the State column contains ints
#     # (it does in the DB, but because the value is nullable, if it contains
#     #  nulls, the entire column gets promoted to Float64 so that NaNs can be
#     #  inserted)
#     gnss_record.dropna(axis=0, subset=["state"], inplace=True)
#     gnss_record = gnss_record.astype({"state": "int32"})
#     print(gnss_record.dtypes)
#
#     # we first have to rename some columns in the gnss_records dataframe so that we can apply the existing code
#     # without making any further alterations to it.
#     # note: inplace means we don't incur a deepcopy on the .rename call, but we still overwrite existing data
#     # and check if the cache must be updated.
#     gnss_record.rename(columns={"constellation": "ConstellationType",
#                                 "time_nanos": "TimeNanos",
#                                 "svid": "Svid",
#                                 "full_bias_nanos": "FullBiasNanos",
#                                 "received_svtime_nanos": "ReceivedSvTimeNanos",
#                                 "state": "State"},
#                        inplace=True)
#
#     # make and return the new "observations" DataFrame
#     return gm.process_raw(gnss_record)
#
#
# def create_add_receiver_points() -> gpd.GeoDataFrame:
#     """
#     Converts the gnss_records and location_records databases into a set of
#     receiver points, and then inserts them into the receiver point database.
#     """
#     # get db engine
#     db_engine = db.init_connection_engine()
#     # fetch ALL items in gnss_records and locations_records databases
#     gnss_raw_records, gnss_fix_records = get_inputs_as_pandas(db_engine)
#     print(gnss_raw_records.head())
#     print(gnss_fix_records.head())
#     print(gnss_fix_records.dtypes)
#
#     # now create the observations
#     observations = make_observation_data(gnss_raw_records)
#     print(observations.head())
#     print(observations.columns)
#     print(observations[["user_id", "svid", "pr"]])
#
#     # now make the receiver receiver points
#     # first rename some columns in gnss_fix
#     gnss_fix_records.rename(columns={"latitude": "Latitude",
#                                      "longitude": "Longitude",
#                                      "altitude": "Altitude"},
#                             inplace=True)
#     recv_points = gm.merge_make_receiver_points(observations, gnss_fix_records)
#     print(recv_points.head())
#     print(recv_points.columns)
#     print(recv_points["user_id", "location", "cn0_dBHz"])
#
#     # now rename the column names that were previously changed
#     recv_points.rename(columns={"ConstellationType": "constellation",
#                                 "Svid": "svid",
#                                 "TimeNanos": "time_nanos",
#                                 "FullBiasNanos": "full_bias_nanos",
#                                 "ReceivedSvTimeNanos": "received_svtime_nanos",
#                                 "State": "state",
#                                 "latitude": "latitude",
#                                 "Longitude": "longitude",
#                                 "Altitude": "altitude"
#                                 },
#                        inplace=True)
#
#     # now add them to the database
#     recv_points.to_postgis(ReceiverPoints_Record.__tablename__, db.engine)
#
#     return recv_points
#
#
# # def join_databases(request: Request, session: orm.Session):
# #     if (auth.auth_token(request) == False):
# #         return jsonify({"result":"token authentication failed"})
# # if we get here, then the token is valid and we can get the record
# # we now want to start borrowing from Terry's code. We want to correct
# # for
#
#
# #     # create the gnss_record object and enqueue it
# #     # note that the WKT format is lng then lat, as in (x;y)
# #     location = elements.WKTElement("POINT({lng} {lat})".format(lat=0.0,
# #                                                                lng=0.0),
# #                                                                srid=constants.SRID)
# #     if (data.get("latitude") != None and data.get("longitude") != None):
# #         location = elements.WKTElement("POINT({lng} {lat})".format(lat=data["latitude"],
# #                                                                    lng=data["longitude"]),
# #                                                                    srid=constants.SRID)
# #
# #
# #     data_point = gnss_model.GNSS_Record(user_id=data["user_id"],
# #                                         location=location,
# #                                         # location = null(),
# #                                         timestamp=data["timestamp"],
# #                                         svid=data["svid"],
# #                                         constellation=data["constellation"],
# #                                         cn0_dBHz=data["cn0_dBHz"],
# #                                         # the fields that are collected via .get are the ones which are only available on
# #                                         # newer Android OSs.
# #                                         baseband_cn0_dBHz=data.get("baseband_cn0_dBHz"),
# #                                         snr_dB=data.get("snr_dB"),
# #                                         state=data["state"],
# #                                         pseudorange_rate_mps=data["pseudorange_rate_mps"],
# #                                         pseudorange_rate_uncertainty_mps=data["pseudorange_rate_uncertainty_mps"],
# #                                         accumulated_deltarange=data["accumulated_deltarange"],
# #                                         accumulated_deltarange_metres=data["accumulated_deltarange_metres"],
# #                                         accumulated_deltarange_uncertainty_metres=data["accumulated_deltarange_uncertainty_metres"],
# #                                         carrier_frequency_hz=data.get("carrier_frequency_hz"),
# #                                         carrier_cycles=data.get("carrier_cycles"),
# #                                         carrier_phase=data.get("carrier_phase"),
# #                                         carrier_phase_uncertainty=data.get("carrier_phase_uncertainty"),
# #                                         altitude=data.get("altitude"),
# #                                         speed=data.get("speed"),
# #                                         agc_level=data.get("agc_level"),
# #                                         multipath_indicator=data["multipath_indicator"],
# #                                         time_nanos=data["time_nanos"],
# #                                         time_uncertainty_nanos=data["time_uncertainty_nanos"],
# #                                         full_bias_nanos=data.get("full_bias_nanos"),
# #                                         bias_nanos=data.get("bias_nanos"),
# #                                         drift_nanos_ps=data.get("drift_nanos_ps"),
# #                                         received_svtime_nanos=data["received_svtime_nanos"],
# #                                         received_svtime_uncertainty_nanos=data["received_svtime_uncertainty_nanos"])
# #
# #     # gnss_record_queue.append(data_point)
# #     # if (len(gnss_record_queue) > 1):
# #     #     db.session.add_all(gnss_record_queue)
# #     #     try:
# #     #         db.session.commit()
# #     #         gnss_record_queue.clear()
# #     #         return jsonify({"result":"success"})
# #     try:
# #         session.add(data_point)
# #         session.commit()
# #         return jsonify({"result":"success"})
# #
# #     except Exception as e:
# #         # gnss_record_queue.clear()
# #         print(e)
# #         session.rollback()
# #         return jsonify({"result":"failed"})
# #
# #
# # def create_base_query(session):
# #     return session.query(gnss_record.GNSS_Record.user_id,
# #                              gnss_record.GNSS_Record.timestamp,
# #                              gnss_record.GNSS_Record.location.ST_AsGeoJSON().label("location"),
# #                              gnss_record.GNSS_Record.svid,
# #                              gnss_record.GNSS_Record.constellation,
# #                              gnss_record.GNSS_Record.cn0_db)
