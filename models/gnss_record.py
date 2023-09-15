####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import BigInteger, Integer, Text, String, DateTime, Float
from geoalchemy2 import Geometry

Base = declarative_base()
# Notes:
# These measurements come from the libs: GnssMeasurement and GnssClock.
# The locations_record meanwhile contains GPS Fix data that comes from the
# Location library. The location library only has access to UTC time, in particular
# a UTC time that is not monotonic (so that UTC time can stay in sync with Earth's
# mildly irregular orbit).
# The result is that we obtain location fixes at a particular UTC time,
# and obtain GNSS measurement data at a slightly different time.
# The GNSS measurement result does not include the location of the smartphone(!),
# while the location result obviously doesn't include the GNSS measurments.
# We therefore have to perform a join between these two databases, using some
# notion of matching the timestamps within a particular tolerance (the gnssmapper)
# package uses a tolerance of 990ms for making these joins, which it does using
# pandas (since each db is represented their as pandas dataframe).
# The location attributes in this table is therefore expected to AA be blank when
# received from the database!
#
# The different time variables included in this table therefore, are meant to
# facilitate this process of matching the times across the two tables, as well
# as to get an accurate estimate for the time onboard the satellite, the time
# on the smartphone's GNSS Receiver Clock, the UTC time at the time the GNSS
# measurement was generated, as well as some degree of future proofing.


class GNSS_Record(Base):
    """A GNSS Measurement."""

    __tablename__ = "gnss_records"
    # the composite primary key
    user_id = Column(Text, primary_key=True, nullable=False)
    # Timestamp here is an estimate of the UTC time at which the GNSS Record
    # object was generated on the Android device.
    # time_nanos and the other nanos time values are the only ones actually used
    # for the real gnss calculations. Timestamp is merely for indexing the db.
    timestamp = Column(DateTime(timezone=False),
                       server_default=func.now(), primary_key=True, nullable=False)
    svid = Column(Integer, primary_key=True, nullable=False)
    constellation = Column(Integer, primary_key=True, nullable=False)
    cn0_dBHz = Column(Float, nullable=False)
    baseband_cn0_dBHz = Column(Float, nullable=True)
    # Post correlation and integration SNR
    snr_dB = Column(Float, nullable=True)
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
    time_nanos = Column(BigInteger, primary_key=True, nullable=False)
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

    def __repr__(self):
        return "<GNSS_Record {self.user_id}, {self.location}, {self.timestamp}>".format(self=self)

    def __str__(self):
        return "<GNSS_Record {self.user_id}, {self.location}, {self.timestamp}>".format(self=self)
