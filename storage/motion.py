from sqlalchemy import Column, Integer, String, DateTime, BOOLEAN
from base import Base
import datetime


class Motion(Base):
    """ motion """

    __tablename__ = "motion"

    id = Column(Integer, primary_key=True)
    location = Column(String(250), nullable=False)
    item = Column(String(250), nullable=False)
    time = Column(String(250), nullable=False)
    action = Column(BOOLEAN, nullable=False)
    date_created = Column(DateTime, nullable=False)


    def __init__(self,location, item, time, action):
        """ Initializes a motion captured """
        self.location = location
        self.item = item
        self.time = time #datetime.datetime.now() Sets the date/time record is created
        self.action = action
        self.date_created = datetime.datetime.now()


    def to_dict(self):
        """ Dictionary Representation of a motion detected """
        dict = {}
        dict['id'] = self.id
        dict['location'] = self.location
        dict['item'] = self.item
        dict['time'] = self.time
        dict['action'] = self.action
        dict['date_created'] = self.date_created

        return dict
