from src.data.sql_exec import SqlExec
from src.data.census_meta import CensusDescription
from src.data.census_boundaries import CensusGeometry
from src.data.census_data import CensusData
import pandas as pd
import argparse
import logging
from datetime import datetime


class SqlLoader(SqlExec):
    # TODO add data functionality
    # TODO docs
    def __init__(self, cmd_args):

        super().__init__(db="census_data", verbose=True)

        self.cmd_args = cmd_args
        self._check_args(self.cmd_args)

        self.boundaries = self.cmd_args.boundaries
        self.demographic = self.cmd_args.data

        if self.boundaries:
            self.census_geo = CensusGeometry()
            self.census_description = CensusDescription()

        if self.demographic:
            self.census_data = CensusData(
                year=self.cmd_args.year, survey=self.cmd_args.type_survey
            )

    def _check_args(self, cmd_args):
        """Check:
        - If at least one of the arguments evaluates to True
        - If one of `boundaries` or `data` is True but not both (XOR)"""

        if not any([arg_value for arg_value in cmd_args.__dict__.values()]):
            raise AttributeError("You need to specify at least one argument")

        if cmd_args.boundaries == cmd_args.data:  # XOR
            raise AttributeError("You cannot load boundaries and data at the same time")

    def createtable_table_metadata(self):
        """
        SqlAlchemy `table_metadata` Class

        Primary Key: table_id (i.e. "B01003_001")

        Source Files: 
            https://www2.census.gov/programs-surveys/acs/summary_file/2018/data/2018_5yr_Summary_FileTemplates.zip?#
        """

        table_metadata_df = self.census_description.get_table_metadata_df()
        table_metadata_cols = table_metadata_df.reset_index().columns

        table_metadata = self.create_table_class(
            table_metadata_cols, "table_metadata", "TableMetaData"
        )

        self.add(table_metadata_df, name="table_metadata", if_exists="replace")

        print("table_metadata created and filled")

    def createtable_county_boundaries(self):
        """
        SqlAlchemy `county_boundaries` Class
        
        Primary Key: GEOID {State FIP}{County FIP} 

        Source Files: 
            https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
        """

        county_geom_gdf = self.census_geo.get_county_boundaries()
        county_geom_df = pd.DataFrame(county_geom_gdf, dtype=str)

        county_geom_cols = county_geom_df.reset_index().columns

        county_boundaries = self.create_table_class(
            county_geom_cols, "county_boundaries", "CountyBoundaries"
        )

        self.add(county_geom_df, name="county_boundaries", if_exists="replace")

        print("county_boundaries table created and filled")

    def createtable_block_boundaries(self, state):
        """
        SqlAlchemy `block_boundaries` Class
        
        Primary Key: GEOID {State FIP}{County FIP}{Tract FIP}{Block FIP} 

        Source Files: 
            https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
        """

        block_geom_gdf = self.census_geo.get_block_boundaries(state)
        block_geom_df = pd.DataFrame(block_geom_gdf, dtype=str)
        del block_geom_gdf

        block_geom_cols = block_geom_df.reset_index().columns

        block_boundaries = self.create_table_class(
            block_geom_cols, "block_boundaries", "BlockBoundaries"
        )

        self.add(block_geom_df, name="block_boundaries", if_exists="append")

        print(f"block_boundaries table created and filled with {state} blocks")

    def createtable_county_demographic_data(self, state):
        """
        SqlAlchemy `county_demographics` Class

        Primary Key: GEOID {State FIP}{County FIP} 
        """
        df = self.census_data.get_county_data(state=state)

        ## Geo Names AKA County Names

        geo_df = df[["geo_names"]].iloc[1:]
        geo_df.columns = ["geo_names"]
        geo_df.index.name = "geo_id"

        geo_table_cols = [geo_df.index.name, geo_df.columns[0]]

        geo_names = self.create_table_class(geo_table_cols, "geo_names", "GeoNames")
        self.add(geo_df, name="geo_names", if_exists="append")

        print(f"Filled county geo names for {state} in the geo_names table")

        ## census_data

        data_df = df.iloc[1:, :-1]
        data_df["state"] = state
        data_df.index.name = "geoid"
        data_table_cols = [data_df.index.name] + data_df.columns.tolist()

        data_table = self.create_table_class(
            data_table_cols, "demographics", "Demographics"
        )
        self.add(data_df, name="demographics", if_exists="replace")

        print(f"Filled demographics table with {state} data")


class ArgParserLoadSql(object):
    """
    Parse Arguments for Load Sql CLI
    
    Attributes
    ----------
    arguments : dict
        nested dictionary to keep track of arguments 
    parser : ArgumentParser
        ArgumentParser from the argparse library

    Methods
    ---------
    get_cli_arguments():
        setup arguments and return cmd_args
    """

    def __init__(self):

        self.parser = argparse.ArgumentParser("Choose what to load into database")
        self.arguments = {
            "boundaries": {"help": "load census boundary data", "action": "store_true"},
            "data": {"help": "load census demographic data", "action": "store_true"},
            "meta": {"help": "load metadata into sql db", "action": "store_true"},
            "county": {
                "help": "load county demographic data/boundaries into sql db",
                "action": "store_true",
            },
            "state": {
                "help": "select the state of the data you want to load",
                "type": str,
            },
            "log": {
                "help": "select the level of logging [debug, info, none]",
                "type": str,
                "default": "none",
            },
            "year": {
                "help": "select year of the census that you want data from",
                "type": int,
                "default": 2018,
            },
            "type_survey": {
                "help": "select the census survey type you want data from ['acs5', 'acs1', etc.]",
                "type": str,
                "default": "acs5",
            },
        }

    def get_cli_arguments(self):

        for var_name, kwargs in self.arguments.items():
            self.setup_single_argument(var_name, **kwargs)

        self.parser._get_args()
        cmd_args = self.parser.parse_args()

        return cmd_args

    def setup_single_argument(self, var_name, **kwargs):

        self.parser.add_argument(f"-{var_name[0]}", f"--{var_name}", **kwargs)


def main_wrapper(main):
    def inner_wrapper():
        argparser = ArgParserLoadSql()
        cmd_args = argparser.get_cli_arguments()

        log_level = cmd_args.log.lower()

        verbose = True if log_level == "debug" else False
        sql_exec = SqlExec()

        if cmd_args.log.lower() in ["debug", "info"]:
            current_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"""[{current_datetime_str}] Loading data to {sql_exec.session.bind}\nwith {', '.join(cmd_args.__dict__.keys())}"""
            )

        return main(cmd_args=cmd_args, sql_loader=sql_loader)

    return inner_wrapper


@main_wrapper
def main(cmd_args=None, sql_loader=None):
    """
    Run main functionality of load_sql
    
    Main function of load_sql that is to be used at the command line or in
    the Makefile to load the sql database with census data.
    """
    sql_loader = SqlLoader(cmd_args)

    if sql_loader.boundaries:

        if cmd_args.meta:
            sql_loader.createtable_table_metadata()
        if cmd_args.county:
            sql_loader.createtable_county_boundaries()
        if cmd_args.state:
            sql_loader.createtable_block_boundaries(cmd_args.state)

    if sql_loader.demographic:

        if cmd_args.state:
            sql_loader.createtable_county_demographic_data(cmd_args.state)


if __name__ == "__main__":

    cmd_args = ArgParserLoadSql().get_cli_arguments()
    sql_loader = SqlLoader(cmd_args)

    main()
