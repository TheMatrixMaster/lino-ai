import os
import uuid

import boto3
import cv2
from boto3.s3.transfer import S3Transfer

import config


class AWS_Controller:
    __s3_client = None
    __s3_resource = None

    def __init__(self):
        self.__s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws["aws_access_key_id"],
            aws_secret_access_key=config.aws["aws_secret_access_key"],
        )
        self.__s3_resource = boto3.resource(
            's3',
            aws_access_key_id=config.aws["aws_access_key_id"],
            aws_secret_access_key=config.aws["aws_secret_access_key"],
        )

    def save_image(self, image, prediction):
        unique_filename = str(uuid.uuid4()) + ".jpg"
        cv2.imwrite(unique_filename, image)
        transfer = S3Transfer(self.__s3_client)
        transfer.upload_file(unique_filename, "linorei", prediction + "/" + unique_filename)
        try:
            os.remove(unique_filename)
        except:
            pass
