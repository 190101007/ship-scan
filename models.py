from database import Base
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey


class Senders(Base):
    __tablename__ = 'sender'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_name = Column(String, nullable=False)
    sender_phone = Column(String, nullable=False)


class Shipments(Base):
    __tablename__ = 'shipments'
    id = Column(String, primary_key=True)
    sender_id = Column(Integer, ForeignKey('sender.id'))
    receiver_name = Column(String, nullable=False)
    receiver_phone = Column(String, nullable=False)
    receiver_address = Column(String, nullable=False)
    shipments_qr_code = Column(LargeBinary)


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_phone = Column(String, nullable=False)
    role = Column(String, nullable=False)
