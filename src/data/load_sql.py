from src.data.connect_db import create_engine_to_rds
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry

db = create_engine_to_rds('census_data')
Base = declarative_base()

table_list = pd.read_excel("https://www2.census.gov/programs-surveys/acs/tech_docs/table_shells/table_lists/2018_DataProductList.xlsx?#")

class 

def excel_to_sql(path):

class Test(Base):
    __tablename__ = 'test'

    col1 = Column(String, primary_key=True)
    col2 = Column(Integer)

Session = sessionmaker(db)
session = Session()

Base.metadata.create_all(db)

# Create
def create():
    row_1 = Test(col1="test", col2=5)
    session.add(row_1)
    session.commit()

# Read
def read():
    data = session.query(Test)
    for datum in data:
        print(datum.col1, datum.col2)

# Update
def update(row_1):
    row_1.col2 = 10
    session.commit()

def delete(row_1):
    session.delete(row_1)
    session.commit()