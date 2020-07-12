from src.data.sql_exec import SqlExec
import pandas as pd
import geopandas as gpd
from shapely import wkt


class SqlGetter(SqlExec):
    def __init__(self):

        super().__init__()

    def get_county_boundaries(self, state):

        sql_str = f"""
                    SELECT
                        geoid,
                        namelsad || ', ' || statename as full_name,
                        geometry
                    FROM
                        county_boundaries as c
                    WHERE
                        statename = '{state}'
                    """

        county_boundaries_df = pd.read_sql_query(
            sql_str, self.engine, index_col="geoid"
        )
        county_boundaries_df["geometry"] = county_boundaries_df.geometry.apply(
            wkt.loads
        )
        county_boundaries_gdf = gpd.GeoDataFrame(
            county_boundaries_df, geometry="geometry", crs="EPSG:4326"
        )

        return county_boundaries_gdf

    def get_table_meta(self):

        table_meta_df = pd.read_sql("table_metadata", self.engine, index_col="table_id")

        return table_meta_df

    def get_demo_data(self, state):

        sql_str = f"""
                    SELECT
                        *
                    FROM
                        demographics
                    WHERE
                        state = '{state}';
                    """

        demo_df = pd.read_sql_query(sql_str, self.engine, index_col="geoid")

        return demo_df


if __name__ == "__main__":

    sql_getter = SqlGetter()

    c_gdf = sql_getter.get_county_boundaries("Colorado")
    tm_df = sql_getter.get_table_meta()
    dem_c_df = sql_getter.get_demo_data("Colorado")

