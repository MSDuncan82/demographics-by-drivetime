from src.data.connect_db import create_engine_to_rds
from src.data.census_meta import CensusDescription
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
import pandas as pd

Base = declarative_base()


class TableMetaData(Base):
    """
    SqlAlchemy `table_metadata` Class
    
    Primary Key: table_id (i.e. "B01003_001")

    Source Files: 
        https://www2.census.gov/programs-surveys/acs/summary_file/2018/data/2018_5yr_Summary_FileTemplates.zip?#
    """

    __tablename__ = "table_metadata"

    table_id = Column(String, primary_key=True)
    overall_category = Column(String)
    subtitle_0 = Column(String)
    subtitle_1 = Column(String)
    subtitle_2 = Column(String)
    subtitle_3 = Column(String)
    subtitle_4 = Column(String)
    subtitle_5 = Column(String)
    subtitle_6 = Column(String)
    subtitle_7 = Column(String)

    def __repr__(self):

        subtitle_lst = [
            self.subtitle_0,
            self.subtitle_1,
            self.subtitle_2,
            self.subtitle_3,
            self.subtitle_4,
            self.subtitle_5,
            self.subtitle_6,
            self.subtitle_7,
        ]

        subtitle_lst = [str(subtitle) for subtitle in subtitle_lst if subtitle]

        return f"<Table: {self.table_id}, {self.overall_category}: {'%'.join(subtitle_lst)}>"


class SqlExec:
    def __init__(self, db="census_data"):

        self.engine = create_engine_to_rds("census_data")
        self.session = sessionmaker(bind=self.engine)()
        self.Base = Base
        self.tables = self.Base.metadata.tables

    def add(self, obj, name=None):
        """Add obj or list of objects of sqlalchemy table class"""

        if isinstance(obj, list):
            self.session.add_all(obj)
            self.session.commit()

        elif isinstance(obj, pd.DataFrame):
            if name is None:
                raise NameError("Need to include table_name")
            obj.to_sql(name, self.engine, if_exists="append", method="multi")

        else:
            self.session.add(obj)
            self.session.commit()

    def create_tables(self):
        """Create all tables from `Base`"""

        Base.metadata.create_all(self.engine)


if __name__ == "__main__":

    sql_exec = SqlExec()
    sql_exec.create_tables()

    census_description = CensusDescription()
    table_metadata_df = census_description.get_table_metadata_df()

    sql_exec.add(table_metadata_df, name="table_metadata")
