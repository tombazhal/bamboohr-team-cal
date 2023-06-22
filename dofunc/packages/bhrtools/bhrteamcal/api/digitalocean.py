import boto3
from botocore.client import Config


class DigitalOcean:

    def __init__(self, spaces_key, spaces_secret, spaces_region, spaces_bucket, spaces_path):
        self.spaces_key = spaces_key
        self.spaces_secret = spaces_secret
        self.spaces_region = spaces_region
        self.spaces_bucket = spaces_bucket
        self.spaces_path = spaces_path


    def upload_to_spaces(self, file_data):
        session = boto3.session.Session()

        client = session.client('s3',
                                region_name=self.spaces_region,
                                endpoint_url=f'https://{self.spaces_region}.digitaloceanspaces.com',
                                aws_access_key_id=self.spaces_key,
                                aws_secret_access_key=self.spaces_secret,
                                config=Config(signature_version='s3v4'))

        try:
            response = client.put_object(Bucket=self.spaces_bucket,
                                         Key=self.spaces_path,
                                         Body=file_data,
                                         ContentType='text/calendar',
                                         CacheControl='max-age=120',
                                         ACL='public-read')

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"Error uploading iCal to Spaces: {response}")

        except BotoCoreError as e:
            raise Exception(f"Error uploading iCal to Spaces: {e}")

        except ClientError as e:
            raise Exception(f"Error uploading iCal to Spaces: {e}")
