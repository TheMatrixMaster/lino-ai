import os
from flask_uploads import IMAGES


class Config(object):
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'linomtl'

    aws = dict(
        aws_access_key_id="AKIATVH75DPZI4GGHZVL",
        aws_secret_access_key="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",
        aws_username="linodataset_s3",
        aws_password="",
        aws_console_login_link="https://251792268274.signin.aws.amazon.com/console"
    )



class DevConfig(Config):
    # Uploads
    UPLOADED_IMAGES_ALLOW = IMAGES
    UPLOADED_IMAGES_DEST = '/static/img/'
    UPLOADED_IMAGES_URL = 'http://localhost:5000/static/img/'


configs = {
    'development': DevConfig,
}