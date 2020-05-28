import zipfile
import io
import requests
import os
import shutil
import uuid
import pandas as pd
import numpy as np

from src.data.s3 import S3Exec
from proj_paths.paths import Paths


class CensusDescription:
    def __init__(self):

        self.paths = Paths()

        try:
            self.census_data_path = self.paths.data.census_description
            self.summary_file_path = (
                self.paths.data.census_description.summary_filetemplates
            )

        except AttributeError("`census_data` and `summary_file` not found"):
            self.census_data_path = None
            self.summary_file_path = None

        self.census_summaryfiles_excel = [
            "https://www2.census.gov/programs-surveys/acs/tech_docs/table_shells/table_lists/2018_DataProductList.xlsx?#",
            "https://www2.census.gov/programs-surveys/popest/geographies/2018/all-geocodes-v2018.xlsx",
        ]

        self.census_summaryfiles_zip = [
            "https://www2.census.gov/programs-surveys/acs/summary_file/2018/data/2018_5yr_Summary_FileTemplates.zip?#"
        ]

        self.s3_exec = S3Exec()
        self.bucket = self.s3_exec.list_buckets()[0]

    def add_summary_files_to_local(self, data_path=None, overwrite=True):
        """Add census summary files to local `proj_root/data/`"""

        for summary_zip_file_url in self.census_summaryfiles_zip:
            self.add_zip_file_to_local(
                summary_zip_file_url, data_path=data_path, overwrite=overwrite
            )

        for summary_excel_file_url in self.census_summaryfiles_excel:
            self.add_excel_file_to_local(
                summary_excel_file_url, data_path=data_path, overwrite=overwrite
            )

    def add_zip_file_to_local(
        self,
        url,
        data_path=None,
        dirname="summary_filetemplates",
        local=True,
        overwrite=True,
    ):
        """Add zip file as directory to data_path"""

        if data_path is None:
            data_path = self.census_data_path.path

        r = requests.get(url, stream=True)

        with zipfile.ZipFile(io.BytesIO(r.content)) as summary_zip:
            temp_directory = f"/tmp/{dirname}"
            shutil.rmtree(temp_directory,)
            os.mkdir(temp_directory)
            summary_zip.extractall(temp_directory)

        os.rename(temp_directory, os.path.join(data_path, dirname))

    def add_excel_file_to_local(self, url, data_path=None, local=True, overwrite=True):
        """Add excel file from url as uniquely named csv file to s3"""

        df, filename = self.get_excel_file(url)

        if local:
            self.write_excel_file_to_local(df, filename, data_path)

    def get_excel_file(self, url):
        """Get DataFrame from excel file"""

        df = pd.read_excel(url)
        filename = os.path.basename(url).split(".")[0]
        return df, filename

    def write_excel_file_to_local(self, df, filename, data_path=None):
        """Write excel file from DataFrame to csv"""

        if data_path is None:
            data_path = self.census_data_path

        random_file_name = self.s3_exec.generate_random_filename(filename)
        filepath = os.path.join(f"{data_path}", f"{random_file_name}.csv")
        df.to_csv(filepath)

    def list_s3_files(self, substring="census_description"):
        """List s3 files in census-data bucket"""

        bucket_objects = self.s3_exec.list_files(self.bucket)
        census_description_s3_files = [
            obj for obj in bucket_objects if substring in obj.key
        ]

        return census_description_s3_files

    def get_table_metadata_df(self, dir_path=None):
        """Get table_metadata df from summary directory of seq.xlsx files"""

        if dir_path is None:
            dir_path = self.summary_file_path.path

        seq_dfs_lst = [
            self._parse_seq_excel(os.path.join(dir_path, file))
            for file in os.listdir(dir_path)
            if self._is_seq(file)
        ]

        table_metadata_df = pd.concat(seq_dfs_lst, axis=0)

        table_metadata_df.columns = ["overall_category"] + [
            f"subtitle_{n}" for n in range(8)
        ]
        table_metadata_df.index.name = "table_id"

        return table_metadata_df

    def _is_seq(self, file):
        """Check if file is a seq.xlsx file"""

        is_seq = file.endswith(".xlsx") and "seq" in file

        return is_seq

    def _parse_seq_excel(self, seq_excel_file):
        """Transform seq.xlsx summary file into df for concatenation"""

        df = pd.read_excel(seq_excel_file)
        df = df.drop(df.columns[:6], axis=1)

        df = df.T
        df.columns = ["table_data"]

        df["table_data"] = df.table_data.str.split("%")
        df = pd.DataFrame(df["table_data"].to_list(), index=df.index)

        return df


if __name__ == "__main__":

    census_description = CensusDescription()
