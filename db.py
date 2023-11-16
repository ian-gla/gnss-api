####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################
from models.receiver_points_record import ReceiverPoints_Record
import os

import pg8000
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import connector
from models.gnss_record import GNSS_Record
from models.locations_record import Locations_Record
from models.profile_record import Profile_Record

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

# [START cloud_sql_connector_postgres_pg8000]
# The Cloud SQL Python Connector can be used along with SQLAlchemy using the
# 'creator' argument to 'create_engine'
# https://cloud.google.com/sql/docs/postgres/connect-connectors


def init_connection_engine() -> sqlalchemy.engine.Engine:
    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            os.environ.get("INSTANCE_CONNECTION_NAME"),
            "pg8000",
            user=os.environ.get("CLOUD_SQL_USERNAME"),
            # os.environ.get("CLOUD_SQL_PASSWORD"),
            password="831Ocean32kashmirFibreous#$11",
            db=os.environ.get("CLOUD_SQL_DATABASE_NAME"),
        )
        return conn

    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    engine.dialect.description_encoding = None
    return engine


def create_gnss_records():
    # Create the Metadata Object
    # metadata_obj = sqlalchemy.MetaData()
    engine = init_connection_engine()
    GNSS_Record.__table__.create(engine)


def create_location_records():
    engine = init_connection_engine()
    Locations_Record.__table__.create(engine)


def create_user_profile_records():
    engine = init_connection_engine()
    Profile_Record.__table__.create(engine)


def create_recv_points_records():
    engine = init_connection_engine()
    ReceiverPoints_Record.__table__.create(engine)


engine = init_connection_engine()
Session = sessionmaker(bind=engine)
session = Session()
