from src.data.sql_exec import SqlExec
from src.data.census_meta import CensusDescription
from src.data.census_geom import CensusGeometry
import pandas as pd


def createtable_table_metadata(sql_exec):
    """
    SqlAlchemy `table_metadata` Class

    Primary Key: table_id (i.e. "B01003_001")

    Source Files: 
        https://www2.census.gov/programs-surveys/acs/summary_file/2018/data/2018_5yr_Summary_FileTemplates.zip?#
    """

    table_metadata_df = CensusDescription().get_table_metadata_df()
    table_metadata_cols = table_metadata_df.reset_index().columns

    table_metadata = sql_exec.create_table_class(
        table_metadata_cols, "table_metadata", "TableMetaData", "table_id"
    )

    sql_exec.add(table_metadata_df, name="table_metadata")

    print("table_metadata created and filled")


def createtable_county_boundaries(sql_exec):
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
        county_geom_cols, "county_boundaries", "CountyBoundaries", "GEOID"
    )

    sql_exec.add(county_geom_df, name="county_boundaries")

    print("county_boundaries table created and filled")


def createtable_block_boundaries(sql_exec, state):
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
        block_geom_cols, "block_boundaries", "BlockBoundaries", "GEOID10"
    )

    sql_exec.add(block_geom_df, name="block_boundaries")

    print(f"block_boundaries table created and filled with {state} blocks")


if __name__ == "__main__":

    sql_exec = SqlExec()
    sql_exec.create_tables()

    createtable_table_metadata(sql_exec)
    createtable_county_boundaries(sql_exec)
    createtable_block_boundaries(sql_exec, "Colorado")
