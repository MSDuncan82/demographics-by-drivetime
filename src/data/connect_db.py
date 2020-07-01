import os
import dotenv
from sqlalchemy import create_engine


def create_engine_to_rds(db_name, echo=True):
    """Connect to RDS database instance described by environment variables in .env"""

    dotenv.load_dotenv()
    username = os.getenv("RDS_USER")
    password = os.getenv("RDS_PASS")
    endpoint = os.getenv("RDS_ENDPOINT")
    port = os.getenv("RDS_PORT")

    db_string = f"postgres://{username}:{password}@{endpoint}:{port}/{db_name}"

    engine = create_engine(db_string, executemany_mode="batch", echo=echo)

    return engine


if __name__ == "__main__":

    engine = create_engine_to_rds("census_data")
