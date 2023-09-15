####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import BigInteger, Integer, Text, String, DateTime, Float
from geoalchemy2 import Geometry
from sqlalchemy.sql import func

Base = declarative_base()


class ReceiverPoints_Record(Base):
    """Keep track of users location."""

    __tablename__ = "receiver_points_record"
    # the composite primary key
    user_id = Column(Text, primary_key=True, nullable=False, unique=False)
    # entries from the location_fix/locations_record
    # timestamp on the android location fix
    utc_time_ms = Column("(UTC)TimeInMs", BigInteger,
                         primary_key=True, nullable=False, unique=False)
    # location fix
    location = Column("location", Geometry(geometry_type='POINTZ',
                      srid=4326), primary_key=True, nullable=False, unique=False)

    # entries from the gnss_record
    svid = Column(String, nullable=False)  # THIS IS A STRING NOW! (ISG FORMAT)
    constellation = Column(Integer, nullable=False)
    cn0_dBHz = Column("cn0_dBHz", Float, nullable=False)
    baseband_cn0_dBHz = Column("baseband_cn0_dBHz", Float, nullable=True)
    # Post correlation and integration SNR
    snr_dB = Column("snr_dB", Float, nullable=True)
    # The sync state for the associated satellite
    state = Column(Integer, nullable=True)
    pseudorange_rate_mps = Column(Float, nullable=True)
    pseudorange_rate_uncertainty_mps = Column(Float, nullable=True)
    accumulated_deltarange = Column(Integer, nullable=True)
    accumulated_deltarange_metres = Column(Float, nullable=True)
    accumulated_deltarange_uncertainty_metres = Column(Float, nullable=True)
    carrier_frequency_hz = Column(Float, nullable=True)
    # The number of full carrier cycles between the satellite and the receiver
    carrier_cycles = Column(BigInteger, nullable=True)
    # This is the fractional part of the complete carrier phase measurement
    # range [0,1]
    carrier_phase = Column(Float, nullable=True)
    carrier_phase_uncertainty = Column(Float, nullable=True)  # 1 sigma
    altitude = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    agc_level = Column(Float, nullable=True)
    multipath_indicator = Column(Integer, nullable=True)
    # time variables
    # This represents the GNSS receiver internal hardware clock value.
    time_nanos = Column(BigInteger, nullable=False)
    # This is the uncertainty associated with the above measurement.
    time_uncertainty_nanos = Column(Float, nullable=True)
    # Full_Bias_Nano represents the difference between time_nanos and
    # true GPS time since Jan 6 1980 in nanoseconds.
    full_bias_nanos = Column(BigInteger, nullable=True)
    # the clock's sub-nanosecond bias.
    bias_nanos = Column(Float, nullable=True)
    # leap seconds associated with smartphone's GNSSClock. Use this to calculate
    # UTC time from the GNSS receiver time.
    leap_seconds = Column(Integer, nullable=True)
    # the instaneous time-derivative of the value given in bias_nanos
    drift_nanos_ps = Column(Float, nullable=True)
    received_svtime_nanos = Column(Float, nullable=True)
    received_svtime_uncertainty_nanos = Column(Float, nullable=True)

    # the new entries that are going to be added
    rx = Column("rx", Integer, nullable=False)
    tx = Column("tx", Integer, nullable=False)
    time = Column("time", DateTime(timezone=False), nullable=False)
    pr = Column("pseudorange", Integer, nullable=False)
