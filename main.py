#!/usr/bin/env python3
from app import app
from app import db

from feedback.feedback_module import feedback
from ecologradbot.ecologradbot_module import ecologradbot
import view

app.register_blueprint(feedback, url_prefix='/feedback')
app.register_blueprint(ecologradbot, url_prefix='/ecologradbot')

if __name__ == "__main__":
    app.run()
