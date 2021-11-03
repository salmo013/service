from sqlalchemy import Column, Integer, String, DateTime, BOOLEAN
from base import Base
import datetime


class DoorMotion(Base):
    """ motion """

    __tablename__ = "door_motion"

    id = Column(Integer, primary_key=True)
    location = Column(String(250), nullable=False)
    item = Column(String(250), nullable=False)
    time = Column(String(250), nullable=False)
    state = Column(BOOLEAN, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, location, item,time, state):
        """ Initializes a motion captured """
        #self.patient_id = patient_id
        self.location = location
        self.item = item
        self.time = time # datetime.datetime.now()  # Sets the date/time record is created
        self.state = state
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a motion detected """
        dict = {}
        dict['id'] = self.id
        dict['location'] = self.location
        dict['item'] = self.item
        dict['time'] = self.time
        dict['state'] = self.state
        dict['date_created'] = self.date_created

        return dict
