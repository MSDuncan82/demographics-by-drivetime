from proj_paths.paths import Paths
import boto3
import pandas as pd
import os
import uuid

class S3Exec:
    def __init__(self,):
        """Initiate boto connection to S3"""

        self.s3_client = boto3.client("s3")
        self.s3_resource = boto3.resource("s3")
        self.session = boto3.session.Session()

    def list_buckets(self):
        """Return list of s3 buckets"""

        return list(self.s3_resource.buckets.all())

    def list_files(self, bucket):
        """Return list of file objects in a given s3 bucket"""

        return list(bucket.objects.all())

    def create_bucket_name(self, bucket_prefix):
        """The generated bucket name must be between 3 and 63 chars long"""

        return "".join([bucket_prefix, str(uuid.uuid4())])

    def create_bucket(self, bucket_prefix, s3_connection, versioning=True):
        """Create bucket with unique name"""

        if s3_connection is None:
            s3_connection = self.s3_resource

        current_region = self.session.region_name
        bucket_name = self.create_bucket_name(bucket_prefix)

        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": current_region},
        )

        if versioning is True:
            bkt_versioning = self.s3_resource.BucketVersioning(bucket_name)
            bkt_versioning.enable()

        return bucket_name, bucket_response

    def generate_random_filename(self, filename):
        """Generate filename with random prefix"""

        return "".join([str(uuid.uuid4().hex[:6]), f"_{filename}"])


    def rename_existing_files(self, filepath):
        """Remame existing file"""

        filename = os.path.basename(filepath).split(".")[0]
        filedir = os.path.join(*filepath.split("/")[:-1])
        random_file_name = self.generate_random_filename(filename)
        os.rename(filepath, f"{filedir}/{random_file_name}.csv")

    def delete_object(self, bucket, file):
        """Delete a file in a given bucket by substring"""
        pass

    def delete_all_objects(self, bucket):
        """Delete all objects in bucket"""

        res = []
        for obj_version in bucket.object_versions.all():
            res.append({"Key": obj_version.object_key, "VersionId": obj_version.id})

        bucket.delete_objects(Delete={"Objects": res})

class CensusDescription:

    def __init__(self):

        self.paths = Paths()
        self.census_data_path = self.paths.data.census_description.path

        self.census_summaryfiles_excel = [
            "https://www2.census.gov/programs-surveys/acs/tech_docs/table_shells/table_lists/2018_DataProductList.xlsx?#",
            "https://www2.census.gov/programs-surveys/popest/geographies/2018/all-geocodes-v2018.xlsx",
        ]
        
        self.s3_exec = S3Exec()
        self.bucket = self.s3_exec.list_buckets()[0]


    def add_summary_files_to_local(self, data_path=None):
        """Add census summary files to local `proj_root/data/`"""

        for summary_excel_file_url in self.census_summaryfiles_excel:

            self.add_excel_file_to_local(summary_excel_file_url, data_path=data_path)

    def add_excel_file_to_local(self, url, data_path=None, local=True):
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

    def list_s3_files(self):
        """list s3 files in census-data bucket"""

        return self.s3_exec.list_files(self.bucket)

if __name__ == "__main__":

    census_description = CensusDescription()

    # census_description.add_summary_files_to_local()

    print([obj.key for obj in census_description.list_s3_files()])