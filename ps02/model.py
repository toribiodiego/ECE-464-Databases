from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state = Column(String, nullable=False)
    subdirectory = Column(String, nullable=False)
    categories = relationship('Category', back_populates='city')
    restaurants = relationship('Restaurant', back_populates='city')

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    subdirectory = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'))
    city = relationship('City', back_populates='categories')

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'))
    city = relationship('City', back_populates='restaurants')
