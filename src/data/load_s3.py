from proj_paths.paths import Paths
import boto3
import pandas as pd
import os
import uuid

class S3Exec():

    def __init__(self,):
        """Initiate boto connection to S3"""

        self.s3_client = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')
        self.session = boto3.session.Session()

    def create_bucket_name(self, bucket_prefix):
        """The generated bucket name must be between 3 and 63 chars long"""

        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def create_bucket(self, bucket_prefix, s3_connection):
        """Create bucket with unique name"""

        if s3_connection is None:
            s3_connection = self.s3_resource

        current_region = self.session.region_name
        bucket_name = self.create_bucket_name(bucket_prefix)

        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
            'LocationConstraint': current_region})

        return bucket_name, bucket_response
    
    def generate_random_filename(self, filename):
        """Generate filename with random prefix"""

        return ''.join([str(uuid.uuid4().hex[:6]), f'_{filename}'])

    def get_excel_file(self, url):
        """Get DataFrame from excel file"""

        df = pd.read_excel(url)
        filename = url.split('/')[-1].split('.')[-2]
        return df, filename

    def write_excel_file(self, df, filename, data_path=census_data_path):
        """Write excel file from DataFrame to csv"""

        random_file_name = self.generate_random_filename(filename)
        filepath = f'{data_path}{random_file_name}.csv'
        df.to_csv(filepath)
        
    def rename_existing_files(self, filepath):
        filename = filepath.split('/')[-1].split('.')[-2]
        filedir = os.path.join(*filepath.split('/')[:-1])
        random_file_name = self.generate_random_filename(filename)
        os.rename(filepath, f'{filedir}/{random_file_name}.csv')
    
if __name__ == '__main__':
    print(proj_path())