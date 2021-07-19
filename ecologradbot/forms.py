
#!/usr/bin/env python3
from wtforms import Form, StringField, TextAreaField, HiddenField


class WebhookForm(Form):

    """Forms class for webhook """

    webhook_url = StringField('WebhookURL') 
