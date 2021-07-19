#!/usr/bin/env python3
from app import db
from datetime import datetime
from flask_security import UserMixin, RoleMixin
# from sqlalchemy_utils import EncryptedType
# from flask import current_app

class Messages(db.Model):

    """Posting feedback messages. """

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now())
    currentURL = db.Column(db.String(140))
    name = db.Column(db.String(140))
    mail = db.Column(db.String(140))
    # mail = db.Column(EncryptedType(db.String(), key='SECRET_KEY'))
    phone = db.Column(db.String(140))
    body = db.Column(db.Text)
    unread = db.Column(db.Boolean, default=True)
    history = db.relationship("History", backref=db.backref("messages"), order_by="desc(History.id)")


    def __init__(self, *args, **kwargs):
        """Messages class Constructor"""
        super(Messages, self).__init__(*args, **kwargs)


    def __repr__(self):
        """Change class print view.
        :returns: formated view

        """
        return '<Message id: {}, date: {}, mail: {}>'.format(self.id, self.date, self.mail)


class History(db.Model):

    """Docstring for History. """

    id = db.Column(db.Integer, primary_key=True)
    messageid = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())
    chapter = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        """TODO: to be defined. """
        super(History, self).__init__(*args, **kwargs)


    def __repr__(self):
        """Change class print view.
        :returns: formated view

        """
        return '<History id: {}, date: {}>'.format(self.id, self.date)

        

class Secrets(db.Model):

    """Docstring for Secrets. """

    id = db.Column(db.Integer, primary_key=True)
    secret = db.Column(db.String(140))
    member = db.relationship("Members", backref=db.backref("secret", uselist=False))


    def __init__(self, *args, **kwargs):
        """TODO: to be defined. """
        super(Secrets, self).__init__(*args, **kwargs)


    def __repr__(self):
        """Change class print view.
        :returns: formated view

        """
        return '<Secrets id: {}, secret: {}>'.format(self.id, self.secret)


class Members(db.Model):

    """Docstring for Members. """

    id = db.Column(db.Integer, primary_key=True)
    secretid = db.Column(db.Integer, db.ForeignKey('secrets.id'), nullable=False)
    chatid = db.Column(db.BigInteger, unique=True)
    date = db.Column(db.DateTime, default=datetime.now())
    su = db.Column(db.Boolean, default=False)


    def __init__(self, *args, **kwargs):
        """Members class Constructor"""
        super(Members, self).__init__(*args, **kwargs)


    def __repr__(self):
        """Change class print view.
        :returns: formated view

        """
        return '<Members id: {}, date: {}, chatid: {}>'.format(self.id, self.date, self.chatid)


### Flask-security-too models ###

class RolesUsers(db.Model):

    """Class of Secondary table for reletion many2many User and Role"""

    __tablename__ = 'roles_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer, db.ForeignKey('role.id'))


class Role(db.Model, RoleMixin):

    """Class of role table for user permitions levels"""

    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        """Change class print view.
        :returns: formated view

        """
        return '<Role {}>'.format(self.name)


class User(db.Model, UserMixin):

    """Class of user table for user authorization"""

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    # username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    # last_login_at = db.Column(db.DateTime())
    # current_login_at = db.Column(db.DateTime())
    # last_login_ip = db.Column(db.String(100))
    # current_login_ip = db.Column(db.String(100))
    # login_count = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    # confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary='roles_users', 
            backref=db.backref('users', lazy='dynamic'))

