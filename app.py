#!/usr/bin/env python3
from flask import Flask, redirect, url_for, request, abort
from config import Configuration
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate #, MigrateCommand
# from flask_script import Manager

from flask_admin import Admin, AdminIndexView, helpers
from flask_admin.contrib.sqla import ModelView

from flask_security import SQLAlchemyUserDatastore, Security, \
        current_user, user_registered


app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)

migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)



### Admin ###
from models import *


# Create customized model view class
class AdminMixin():

    def is_accessible(self):
        return (current_user.is_active and 
                current_user.is_authenticated and
                current_user.has_role('admin')
                )


    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


class EditorAdminViewMixin(AdminView):

    def is_accessible(self):
        return (current_user.is_active and 
                current_user.is_authenticated and
                (current_user.has_role('admin') or current_user.has_role('editor'))
                )


class MessagesAdminView(EditorAdminViewMixin, AdminView):

    """Class to change view of Messages table in Admin."""

    form_columns = ['date', 'currentURL', 'name', 'mail', 'phone', 'body', 'unread']
    column_list = ['date', 'currentURL', 'name', 'body', 'unread']


class HistoryAdminView(EditorAdminViewMixin, AdminView):

    """Class to change view of History table in Admin."""

    column_list = ['date', 'chapter']


admin = Admin(
        app, 
        'EcologradApp', 
        url='/admin/', 
        index_view=HomeAdminView(name='Admin'), 
        template_mode='bootstrap4'
        )
admin.add_view(MessagesAdminView(Messages, db.session))
admin.add_view(HistoryAdminView(History, db.session))
admin.add_view(AdminView(Members, db.session))
admin.add_view(AdminView(Secrets, db.session))
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Role, db.session))


### Flask-Security-Too ###
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
            admin_base_template=admin.base_template, 
            admin_view=admin.index_view, 
            h=helpers, 
            get_url=url_for                                             
            )


# Adds default Role to recently registered user
@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token, form_data):
    default_role = user_datastore.find_role("user")
    user_datastore.add_role_to_user(user, default_role)
    db.session.commit()


### NavBar ###
from flask_nav import Nav
from flask_nav import register_renderer
from flask_nav.elements import *
from nav import BootstrapVRenderer


nav = Nav()

nav.init_app(app)


def top_nav():
    topmenu = [
            View('EcologradApp', 'index')
            ]

    authmenu_editor_admin = [
            View('Feedback', 'feedback.index'),
            View('Create', 'feedback.create_fb_msg'),
            ]  if current_user.is_active and current_user.is_authenticated and (
                    current_user.has_role('admin') or current_user.has_role('editor')) else []

    authmenu_admin = [
            View('Ecologradbot', 'ecologradbot.index'),
            View('Admin', 'admin.index'),
            ]  if current_user.is_active and current_user.is_authenticated and current_user.has_role('admin') else []

    authmenu_user = [
            Subgroup('User',
                Text(current_user.email),
                View('Change pass', 'security.change_password'),
                View('Logout', 'security.logout'),
                )
            ]  if current_user.is_active and current_user.is_authenticated else []

    topmenu.extend(authmenu_editor_admin)
    topmenu.extend(authmenu_admin)
    topmenu.extend(authmenu_user)
    return Navbar(*topmenu)


register_renderer(app, 'mybootstrap5', BootstrapVRenderer)

# registers the "top" menubar
nav.register_element(
        'top',
        top_nav
        )


