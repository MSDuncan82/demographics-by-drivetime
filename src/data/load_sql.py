from src.data.sql_exec import SqlExec
from src.data.census_meta import CensusDescription
from src.data.census_boundaries import CensusGeometry
import pandas as pd
import argparse
import logging
from datetime import datetime


class SqlLoader(object):
    # TODO current finish moving functions to class methods
    # TODO add data functionality
    # TODO docs
    def __init__(self, cmd_args):

        self.cmd_args = cmd_args
        self._check_args(cmd_args)

        self.boundaries = cmd_args['boundaries']
        self.demographic = cmd_args['boundaries']

    def _check_args(self, cmd_args):
        """Check:
        - If at least one of the arguments evaluates to True
        - If one of `boundaries` or `data` is True but not both (XOR)"""

        if not any([arg_value for arg_value in cmd_args.__dict__.values()]):
            raise AttributeError("You need to specify at least one argument")

        if cmd_args['boundaries'] != cmd_args['data']: # XOR
            raise AttributeError("You cannot load boundaries and data at the same time")

    def createtable_table_metadata(self, sql_exec, boundaries=True, demographic=False):
        """
        SqlAlchemy `table_metadata` Class

        Primary Key: table_id (i.e. "B01003_001")

        Source Files: 
            https://www2.census.gov/programs-surveys/acs/summary_file/2018/data/2018_5yr_Summary_FileTemplates.zip?#
        """

        table_metadata_df = CensusDescription().get_table_metadata_df()
        table_metadata_cols = table_metadata_df.reset_index().columns

        table_metadata = sql_exec.create_table_class(
            table_metadata_cols, "table_metadata", "TableMetaData"
        )

        sql_exec.add(table_metadata_df, name="table_metadata", if_exists="replace")

        print("table_metadata created and filled")


    def createtable_county_boundaries(self, sql_exec, boundaries=True, demographic=False):
        """
        SqlAlchemy `county_boundaries` Class
        
        Primary Key: GEOID {State FIP}{County FIP} 

        Source Files: 
            https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
        """

        county_geom_gdf = CensusGeometry().get_county_boundaries()
        county_geom_df = pd.DataFrame(county_geom_gdf, dtype=str)

        county_geom_cols = county_geom_df.reset_index().columns

        county_boundaries = sql_exec.create_table_class(
            county_geom_cols, "county_boundaries", "CountyBoundaries"
        )

        sql_exec.add(county_geom_df, name="county_boundaries", if_exists="replace")

        print("county_boundaries table created and filled")


    def createtable_block_boundaries(self, sql_exec, state, boundaries=True, demographic=False):
        """
        SqlAlchemy `block_boundaries` Class
        
        Primary Key: GEOID {State FIP}{County FIP}{Tract FIP}{Block FIP} 

        Source Files: 
            https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
        """

        block_geom_gdf = CensusGeometry().get_block_boundaries(state)
        block_geom_df = pd.DataFrame(block_geom_gdf, dtype=str)
        del block_geom_gdf

        block_geom_cols = block_geom_df.reset_index().columns

        block_boundaries = sql_exec.create_table_class(
            block_geom_cols, "block_boundaries", "BlockBoundaries"
        )

        sql_exec.add(block_geom_df, name="block_boundaries", if_exists="append")

        print(f"block_boundaries table created and filled with {state} blocks")


def setup_argparse(boundaries=True)
    """
    Parse arguments from command line for Makefile.

    Arguments
    ----------
    boundaries : bool
        True if loading boundary files into db.

    Returns
    ---------
    cmd_args : Namespace
        A simple object that holds the parsed arguments.
    """

    parser = argparse.ArgumentParser("Choose what to load into database")

    parser.add_argument(
        "-b", "--boundaries", help="load census boundary data", action="store_true"
    )
    parser.add_argument(
        "-d", "--data", help="load census demographic data", action="store_true"
    )
    parser.add_argument(
        "-m", "--meta", help="load metadata into sql db", action="store_true"
    )
    parser.add_argument(
        "-c",
        "--county",
        help="load county demographic data/boundaries into sql db",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--state",
        help="select the state of the data you want to load",
        type=str,
    )
    parser.add_argument(
        "-l",
        "--log",
        help="select the level of logging [debug, info, none]",
        type=str,
        default="none",
    )

    parser._get_args()
    cmd_args = parser.parse_args()

    return cmd_args

def main_wrapper(main):
    def inner_wrapper():
        cmd_args = setup_argparse()
        log_level = cmd_args.log.lower()

        verbose = True if log_level == "debug" else False
        sql_exec = SqlExec(db="census_data", verbose=verbose)

        if cmd_args.log.lower() in ["debug", "info"]:
            current_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"""[{current_datetime_str}] Loading data to {sql_exec.session.bind}\nwith {', '.join(cmd_args.__dict__.keys())}"""
            )

        return main(cmd_args=cmd_args, sql_exec=sql_exec)

    return inner_wrapper


@main_wrapper
def main(cmd_args=None, sql_exec=None):
    """
    Run main functionality of load_sql
    
    Main function of load_sql that is to be used at the command line or in
    the Makefile to load the sql database with census data.
    """
    # TODO use class instead
    if cmd_args.meta:
        createtable_table_metadata(sql_exec)

    if cmd_args.county:
        createtable_county_boundaries(sql_exec)

    if cmd_args.state:
        createtable_block_boundaries(sql_exec, cmd_args.state)


if __name__ == "__main__":

    main()
