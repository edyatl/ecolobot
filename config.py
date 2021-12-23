#!/usr/bin/env python3
import os
from os import environ as env
from dotenv import load_dotenv
import bcrypt

project_dotenv = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(project_dotenv):
    load_dotenv(project_dotenv)

class Configuration(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{0}:{1}@localhost/{2}'.format(
            env.get('ENV_DB_USER'), 
            env.get('ENV_DB_PASS'), 
            env.get('ENV_DB_NAME')
            )
    SECRET_KEY = env.get('ENV_SECRET_KEY')
    PER_PAGE = 5
    TG_TOKEN = env.get('ENV_TG_TOKEN')
    MESSAGES_MAIL_KEY = env.get('ENV_MESSAGES_MAIL_KEY')
    MESSAGES_PHONE_KEY = env.get('ENV_MESSAGES_PHONE_KEY')
    WH_TOKEN = env.get('ENV_WH_TOKEN')

    # Flask-security-too
    SECURITY_PASSWORD_SALT = env.get('ENV_SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = 'bcrypt'

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False

    # SECURITY_RECOVERABLE = True
    # SECURITY_SEND_PASSWORD_RESET_EMAIL = False

    SECURITY_CHANGEABLE = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False

    # URLs
    SECURITY_URL_PREFIX = "/"
    SECURITY_LOGIN_URL = "/login/"
    SECURITY_LOGOUT_URL = "/logout/"
    SECURITY_POST_LOGIN_VIEW = "/"
    SECURITY_POST_LOGOUT_VIEW = "/login/"
    SECURITY_POST_CHANGE_VIEW = "/logout/"
    SECURITY_POST_REGISTER_VIEW = "/"
    SECURITY_REGISTER_URL = "/register/"
    SECURITY_POST_REGISTER_VIEW = "/registered/"
    # SECURITY_RESET_URL = "/reset/"
    SECURITY_CHANGE_URL = "/change/"


