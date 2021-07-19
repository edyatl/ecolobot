#!/usr/bin/env python3
from wtforms import Form, StringField, TextAreaField, HiddenField


class FeedbackForm(Form):

    """Forms class for post messages. """

    currentURL = StringField('CurrentURL') 
    name = StringField('Name') 
    email = StringField('Mail')
    phone = StringField('Phone')
    message = TextAreaField('Body')


class HistoryForm(Form):

    """Forms class for history notes. """

    messageid = HiddenField('MessageId')
    chapter = TextAreaField('Note')

