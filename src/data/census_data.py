from api_wrapper.census_api.census_api import CensusDataAPI
import os
import shutil
import uuid
import pandas as pd
import numpy as np

from src.data.s3 import S3Exec
from proj_paths.paths import Paths


class CensusData(object):
    """
    Retrieve data from census
    
    Access the CensusDataAPI from the api_wrapper package to retrieve census data.
    
    Attributes
    ----------
    census_data : CensusDataAPI
        CensusDataAPI from api_wrapper. Takes `year` and `survey` in __init__.
        Defaults are year=2018, survey="acs5". See api_wrapper docs for more 
        details
    
    Methods
    ---------
    get_county_data(state, county="*")
        Get default data from CensusDataAPI for a given state and county.
        Default is to get data from all counties in state. TODO Add tables kwarg
    """

    def __init__(self, year=2018, survey="acs5"):

        self.paths = Paths()
        self.census_data = CensusDataAPI(survey="acs5", year=2018)

    def get_county_data(self, state, county="*"):
        """Get default data from CensusDataAPI for a given state and county.
        Default is to get data from all counties in state."""

        # kwargs = dict(state=state, county=county)
        # hierarchy = self.census_data._parse_hierarchy(kwargs)
        df = self.census_data.get_data(state=state, county=county)

        return df


if __name__ == "__main__":

    census_data = CensusData()
    df = census_data.get_county_data(state="Colorado")

