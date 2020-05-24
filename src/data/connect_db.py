import os
import dotenv
from sqlalchemy import create_engine


def create_engine_to_rds(db_name):

    dotenv.load_dotenv()
    username = os.getenv("RDS_USER")
    password = os.getenv("RDS_PASS")
    endpoint = os.getenv("RDS_ENDPOINT")
    port = os.getenv("RDS_PORT")

    db_string = f"postgres://{username}:{password}@{endpoint}:{port}/{db_name}"

    db = create_engine(db_string)

    return db
