from api_wrapper.census_api import CensusBoundaries
import os
import shutil
import uuid
import pandas as pd
import numpy as np

from src.data.s3 import S3Exec
from proj_paths.paths import Paths


class CensusGeometry(object):

    def __init__(self):

        self.paths = Paths()
        self.census_boundaries = CensusBoundaries(
            table_data_dir=self.paths.data.census_description.summary_filetemplates.path,
            fips_sheet=self.paths.data.census_description.search_files("all-geocodes"),
        )

    def get_county_boundaries(self):
        """Get GeoPandasDataframe of all counties in the united states"""

        county_boundaries_gdf = self.census_boundaries.get_boundaries_gdf(
            "Colorado", "county"
        )

        county_boundaries_gdf = county_boundaries_gdf.set_index("GEOID")
        county_boundaries_gdf['STATENAME'] = county_boundaries_gdf['STATEFP'].apply(lambda fip: self.census_boundaries.state_names[fip])

        return county_boundaries_gdf

    def get_block_boundaries(self, state):
        pass

if __name__ == "__main__":

    census_geom = CensusGeometry()

    county_boundaries_gdf = census_geom.get_county_boundaries()
