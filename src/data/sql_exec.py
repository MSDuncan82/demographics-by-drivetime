from src.data.connect_db import create_engine_to_rds
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Integer
from sqlalchemy import inspect
from sqlalchemy import Table
from sqlalchemy.orm import mapper
import pandas as pd


class SqlExec:
    """
    Interface to interact with SQL database
    
    Use SqlAlchemy to interact with SQL databases. The SqlExec needs to connect
    to an existing database. After the connection is made the class allows a 
    simple interface to create tables, add data and query data.
    
    Attributes
    ----------
    Base : sqlalchemy.ext.declarative.api.DeclarativeMeta
        SqlAlchemy's base class for table classes
        
    engine : sqlalchemy.engine.base.Engine
        SqlAlchemy's engine that is connected to the database
        
    session : sqlalchemy.orm.session.Session
        SqlAlchemy's ORM interface with the databse

    tables : sqlalchemy.util._collections.immutabledict
        tables that are mapped to the database from the ORM
    
    Methods
    ---------
    __init__(self, db='census_data')
        Initialize object with connection to database `db`
    
    add(self, obj, name=None, if_exists='append')
        Add data to a table in the database. 

        `obj`: pd.DataFrame, sqlalchemy.table.obj, list of sqlalchemy.table.obj
            Data to be added to a database table
        `name`: str
            if `obj` is type pd.DataFrame you must specify the table name
        `if_exists`: default='append', 'replace', 'fail'
            What action to take if the table already exists

    create_table_class(self, columns, table_name, class_name, pk_col='index')
        Create a sqlalchemy.table class. The class is not added to the database
        until the method `create_tables` is called.
    
    create_tables(self)
        Create tables in the database from table classes created with `create_table_class`
    """

    def __init__(self, db="census_data", verbose=True):

        self.engine = create_engine_to_rds("census_data", echo=verbose)
        self.session = sessionmaker(bind=self.engine)()
        self.Base = declarative_base()
        self.tables = self.Base.metadata.tables

    def get_table_info(self):

        inspector = inspect(self.engine)
        for table_name in inspector.get_table_names():
            for column in inspector.get_columns(table_name):
                print(f"Table: {table_name}, Column: {column}")

    def add(self, obj, name=None, if_exists="append"):
        """Add obj or list of objects of sqlalchemy table class"""

        if isinstance(obj, list):
            self.session.add_all(obj)
            self.session.commit()

        elif isinstance(obj, pd.DataFrame):
            if name is None:
                raise NameError("Need to include table_name")

            obj = obj.reset_index()
            obj.columns = [col.lower().replace(" ", "_") for col in obj.columns]

            obj.to_sql(
                name, self.engine, if_exists=if_exists, method="multi", index=False
            )

            self.add_pk_constraint(name, obj.columns[0])

        else:
            self.session.add(obj)
            self.session.commit()

    def add_pk_constraint(self, table_name, pk_col):

        with self.engine.connect() as con:
            con.execute(f"ALTER TABLE {table_name} ADD PRIMARY KEY ({pk_col})")

    def create_tables(self):
        """Create all tables from `Base`"""

        self.Base.metadata.create_all(self.engine)

    def create_table_class(self, columns, table_name, class_name):

        columns = list(columns)
        pk_col = columns.pop(0)
        attr_dict = {"__tablename__": table_name}

        attr_dict[pk_col] = Column(String, primary_key=True)
        attr_dict.update({col: Column(String) for col in columns})

        table_class = type(class_name, (self.Base,), attr_dict)

        return table_class

    def get_county_boundaries(self):

        county_boundaries_df = pd.read_sql(
            "county_boundaries", self.engine, index_col="geoid"
        )
        return county_boundaries_df

    def get_table_meta(self):

        table_meta_df = pd.read_sql("table_metadata", self.engine, index_col="table_id")
        return table_meta_df


if __name__ == "__main__":

    sql_exec = SqlExec()
    sql_exec.get_table_info()
    cb_df = sql_exec.get_county_boundaries()
    tm_df = sql_exec.get_table_meta()
