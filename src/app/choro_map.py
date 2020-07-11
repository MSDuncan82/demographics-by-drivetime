import pandas as pd
import json
import plotly.express as px
from src.data.get_sql import SqlGetter

class Mapper(object):

    def __init__(self):

        self.sql_getter = SqlGetter()

    def get_county_boundaries(self, state):

        boundaries_gdf = self.sql_getter.get_county_boundaries(state)

        return boundaries_gdf 

    def get_demo_data(self, state):

        demo_df = self.sql_getter.get_demo_data(state)

        return demo_df

    def get_table_meta(self):

        table_meta_df = self.sql_getter

    def map_counties(self, state):

        boundaries_gdf = self.get_county_boundaries(state)
        boundaries_gdf.to_file('/tmp/tmpjson.json', driver="GeoJSON")
        with open('/tmp/tmpjson.json') as county_json:
            county_boundaries = json.load(county_json)

        
        demo_df = self.get_demo_data(state)
        import ipdb; ipdb.set_trace()
        fig = px.choropleth_mapbox(demo_df.reset_index(),
                                    geojson=county_boundaries,
                                    locations="geoid",
                                    featureidkey="properties.geoid",
                                    color='b01003_001e',
                                    color_continuous_scale='Viridis',
                                    mapbox_style="carto-positron",
                                    zoom=10,
                                    center={"lat": 39.742043, "lon": -104.991531},
                                    opacity=0.5,
                                    labels={'b01003_001e':'Total Population'}
                                )

        fig.update_layout(margin={'r':0, 't':0, 'l':0, 'b':0})
        fig.show()

    
if __name__ == '__main__':
    mapper = Mapper()    

    mapper.map_counties('Montana')

