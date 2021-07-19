#!/usr/bin/env python3
from flask import Blueprint, current_app, redirect
from flask import render_template, request, url_for
from flask_security import auth_required, roles_accepted, \
        MailUtil, PhoneUtil

from models import Messages, History, Members
from .forms import FeedbackForm, HistoryForm

from app import db, app
# from app import context_processor

from ecologradbot.ecologradbot_module import send_msg
from cryptography.fernet import Fernet

feedback = Blueprint('feedback', __name__, template_folder='templates')


class ExtPhoneUtil(PhoneUtil):

    """description"""

    def validate(self, phone):
        """
        Validate the given phone.
        If valid, the normalized version is returned.
        ValueError is thrown if not valid.
        """

        if not self.validate_phone_number(phone) == None:
            raise ValueError(self.validate_phone_number(phone))

        return self.get_canonical_form(phone) 


def encrypt_field(value, key):
    """Encrypts a field value.

    :param value: string for encryption
    :returns: encrypted string
    """
    return Fernet(key).encrypt(value.encode('utf8'))


@feedback.context_processor
def utility_processor():
    def decrypt_field(value, key):
        """Decrypts a field value, and if field not encrypted 
        than show it as is, and trys to encrypt it in db.

        :param value: encrypted string
        :returns: decrypted string
        """
        try:
            res = Fernet(key).decrypt(value.encode('utf8')).decode('utf8')
        except:
            res = value
            try:
                mail = Messages.query.filter(Messages.mail == value).update(
                        {'mail': encrypt_field(value, key)}
                        )
                db.session.commit()
            except Exception as e:
                print('ERROR: Can not update message: {}'.format(e))
        return res 
    return dict(decrypt_field=decrypt_field)


@feedback.route('/create', methods=['POST', 'GET'])
def create_fb_msg():
    """Create new feedback message

    :returns: create or redirect to referer

    """
    if request.method == 'POST':
        mail_validator = MailUtil(app)
        phone_validator = ExtPhoneUtil(app)
        currentURL = request.form['currentURL']
        name = request.form['name']
        mail = request.form['email']
        phone = request.form['phone']
        body = request.form['message']
        # print(phone, phone_validator.validate_phone_number(phone), phone_validator.get_canonical_form(phone), sep='\n')

        try:
            msg = Messages(
                    currentURL=currentURL, 
                    name=name, 
                    mail=encrypt_field(
                        mail_validator.validate(mail), 
                        current_app.config['MESSAGES_MAIL_KEY']
                        ), 
                    phone=encrypt_field(
                        phone_validator.validate(phone),
                        current_app.config['MESSAGES_PHONE_KEY']
                        ), 
                    body=body
                    )
            db.session.add(msg)
            db.session.commit()
            users = Members.query.all()
            for user in users:
                send_msg(user.chatid, name+'\n'+mail+'\n'+phone_validator.get_canonical_form(phone)+'\n'+body)
        except Exception as e:
            print('ERROR: Can not create message: {}'.format(e))

        return redirect("{}?fs=1".format(currentURL))


    form = FeedbackForm()
    return render_template('feedback/create.html', form=form)


@feedback.route('/', methods=['POST', 'GET'])
@auth_required()
@roles_accepted("admin", "editor")
def index():
    """Rendering html of feedback index
    :returns: rendered page of feedback index

    """
    messageid = None
    q = request.args.get('q')
    page = request.args.get('page')

    if request.method == 'POST':
        messageid = int(request.form['messageid'])
        chapter = request.form['chapter']
        q = request.form['q']
        page = request.form['page']

        try:
            note = History(messageid=messageid, chapter=chapter)
            unread = Messages.query.filter(Messages.id == messageid).update({'unread': False})
            db.session.add(note)
            db.session.commit()
        except Exception as e:
            print('ERROR: Can not create note: {}'.format(e))

    if q:
        messages = Messages.query.filter(Messages.name.contains(q) | Messages.mail.contains(q) | Messages.body.contains(q))
    else:
        messages = Messages.query.order_by(Messages.id.desc()) #.all()


    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    pages = messages.paginate(page=page, per_page=current_app.config['PER_PAGE'])
    form = HistoryForm()

    return render_template('feedback/index.html', pgs=pages, q=q, hform=form, active=messageid)

