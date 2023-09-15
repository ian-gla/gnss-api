####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import BigInteger, Integer, Text, String, DateTime, Float
from geoalchemy2 import Geometry

Base = declarative_base()


class Locations_Record(Base):
    """
    Keep track of users location.
    Composite primary key consisting of: {user_id, utc_time_ms, location}
    """
    __tablename__ = "location_records"

    # user id as received from Firebase
    user_id = Column("user_id", Text, primary_key=True,
                     nullable=False, unique=False)
    # timestamp on the android location fix
    utc_time_ms = Column("(UTC)TimeInMs", BigInteger,
                         primary_key=True, nullable=False, unique=False)
    # location fix
    location = Column("location", Geometry(geometry_type='POINT',
                      srid=4326), primary_key=True, nullable=False, unique=False)
    # same points and with altitude, but as separate columns (obtained via the same location fix)
    latitude = Column("latitude", Float, nullable=False, unique=False)
    longitude = Column("longitude", Float, nullable=False, unique=False)
    altitude = Column("altitude", Float, nullable=True, unique=False)
    # timestamp which stores the date time when the package was created (on the android phone). Timezone should be UTC.
    timestamp = Column("timestamp", DateTime(timezone=False),
                       server_default=func.now(), nullable=False, unique=False)

    def __repr__(self):
        return "<Locations_Record {self.user_id}, {self.utc_time_ms}, ({self.location}; {self.timestamp})>".format(self=self)

    def __str__(self):
        return "<Locations_Record {self.user_id}, {self.utc_time_ms}, ({self.location}; {self.timestamp})>".format(self=self)
