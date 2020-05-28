from proj_paths.paths import Paths
import zipfile
import io
import requests
import boto3
import pandas as pd
import os
import shutil
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

        if versioning:
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


if __name__ == "__main__":
    pass
