####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, Text, Float

Base = declarative_base()


class Profile_Record(Base):
    """Keep track of users location."""

    __tablename__ = "profile_records"
    # the composite primary key
    user_id = Column(Text, primary_key=True, nullable=False)
    email = Column(Text, nullable=True)
    num_recordings = Column(Integer, nullable=False)
    total_minutes = Column(Float, nullable=False)

    def asdict(self):
        return {'user_id': self.user_id,
                'email': self.email,
                'num_recordings': self.num_recordings,
                'total_minutes': self.total_minutes}
