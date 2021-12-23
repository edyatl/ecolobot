#!/usr/bin/env python3
from flask import Blueprint, current_app, redirect, jsonify
from flask import render_template, request, url_for
from flask_security import auth_required, roles_accepted

from models import Messages, Secrets, Members

from app import db, app
import requests
import json
import secrets, hashlib
import re

import ecologradbot.types as tg
from ecologradbot.forms import WebhookForm

ecologradbot = Blueprint('ecologradbot', __name__, template_folder='templates')

URL = 'https://api.telegram.org/bot{tg_token}/{method}'

cmd_set = {
        'help': '/help - Info about available commands',
        'start': '/start - Interact with Bot and welcome',
        'stop': '/stop - Disconnect from the channel',
        'secret': '/secret <name> - Get new secret (Admin)',
        'connect': '/connect <secret> - Connect yourself to the channel'
        }

forbidden_content = {
        'audio',
        'document',
        'animation',
        'game',
        'photo',
        'sticker',
        'video',
        'video_note',
        'voice',
        'contact',
        'location',
        'venue',
        'dice',
        'new_chat_members',
        'left_chat_member',
        'new_chat_title',
        'new_chat_photo',
        'delete_chat_photo',
        'group_chat_created',
        'supergroup_chat_created',
        'channel_chat_created',
        'migrate_to_chat_id',
        'migrate_from_chat_id',
        'pinned_message',
        'invoice',
        'successful_payment',
        'connected_website',
        'poll',
        'passport_data'
        }

non_msg_update = {
        'inline_query',
        'chosen_inline_result',
        'callback_query',
        'shipping_query',
        'pre_checkout_query',
        'poll',
        'poll_answer',
        'unknown'
        }


with app.app_context():
    wh_token = current_app.config['WH_TOKEN']


def _convert_markup(markup):
    if isinstance(markup, tg.JsonSerializable):
        return markup.to_json()
    return markup


def send_msg(chat_id, text='Yep, Sugar!', disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None, 
        parse_mode=None, disable_notification=None, timeout=None):
    """TODO: Docstring for send_msg.
    :returns: TODO

    """
    url = URL.format(tg_token = current_app.config['TG_TOKEN'], method = 'sendMessage')
    msg = {'chat_id': chat_id, 'text': text}
    if disable_web_page_preview is not None:
        msg['disable_web_page_preview'] = disable_web_page_preview
    if reply_to_message_id:
        msg['reply_to_message_id'] = reply_to_message_id
    if reply_markup:
        msg['reply_markup'] = _convert_markup(reply_markup)
    if parse_mode:
        msg['parse_mode'] = parse_mode
    if disable_notification is not None:
        msg['disable_notification'] = disable_notification
    if timeout:
        msg['connect-timeout'] = timeout
    r = requests.post(url, json=msg)
    return r.json()


def cb_answer(callback_query_id, text=None, show_alert=None, rurl=None, cache_time=None):
    """TODO: Docstring for cb_answer.

    :callback_query_id: TODO
    :text: TODO
    :show_alert: TODO
    :rurl: TODO
    :cache_time: TODO
    :returns: TODO

    """
    url = URL.format(tg_token = current_app.config['TG_TOKEN'], method = 'answerCallbackQuery')
    msg = {'callback_query_id': callback_query_id}
    if text:
        msg['text'] = text
    if show_alert is not None:
        msg['show_alert'] = show_alert
    if rurl:
        msg['rurl'] = rurl
    if cache_time is not None:
        msg['cache_time'] = cache_time
    r = requests.post(url, json=msg)
    return r.json()


def keyboard(*args):
    """TODO: Docstring for keyboard.
    :returns: TODO

    """
    itembtn = []
    markup = tg.ReplyKeyboardMarkup(row_width=2)

    for c in args:
        itembtn.append(tg.KeyboardButton('/'+c))
    markup.add(*itembtn)

    return markup


def inline_keyboard(**kwargs):
    """TODO: Docstring for inline_keyboard.

    :**kwargs: TODO
    :returns: TODO

    """
    itembtn = []
    markup = tg.InlineKeyboardMarkup(row_width=2)

    for k, v in kwargs.items():
        itembtn.append(tg.InlineKeyboardButton(k, callback_data=v))
    markup.add(*itembtn)

    return markup


def show_help():
    """TODO: Docstring for show_help.
    :returns: TODO

    """
    global cmd_set
    res = 'Available commands are:\n\n'
    for cmd in cmd_set:
        res += cmd_set[cmd] + '\n\n'
    return res


def validate_cmd(cmd):
    """TODO: Docstring for validate_cmd.

    :cmd: TODO
    :returns: TODO

    """
    global cmd_set
    flag = False

    if cmd in cmd_set:
        res = 'Command /{} ok...'.format(cmd)
        flag = True
    else:
        res = 'Command /{} unknown :(\nMaybe try the help page at /help'.format(cmd)
    return res, flag


def check_su(chat_id):
    """TODO: Docstring for check_su.

    :chat_id: TODO
    :returns: TODO

    """
    try:
        return Members.query.filter(Members.chatid == chat_id).all()[0].su
    except:
        return False


def create_secret(chat_id, phone='111-11-11'):
    """TODO: Docstring for create_secret.
    :returns: TODO

    """
    if not check_su(chat_id):
        return 'You are not allowed make secrets!'

    tkn = secrets.token_hex(8)
    sha = hashlib.sha1(phone.encode('utf8')).hexdigest()
    try:
        secret = Secrets(secret=sha[:8]+tkn)
        db.session.add(secret)
        db.session.commit()
    except:
        print('ERROR: Can not create secret.')

    return sha[:8] + tkn


def is_member(chat_id):
    """TODO: Docstring for is_member.

    :chat_id: TODO
    :returns: TODO

    """
    try:
        if Members.query.filter(Members.chatid == chat_id).all():
            return True
        else:
            return False
    except:
        return False


def add_member(chat_id, secret):
    """TODO: Docstring for add_member.
    :returns: TODO

    """
    if is_member(chat_id):
        return 'You are already connected!'

    if Secrets.query.filter(Secrets.secret == secret).all() and not Members.query.filter(
            Members.secret.has(Secrets.secret == secret)).all():
        secret_id = Secrets.query.filter(Secrets.secret == secret).all()[0].id
        try:
            member = Members(chatid=chat_id, secretid=secret_id)
            db.session.add(member)
            db.session.commit()
        except Exception as e:
            print('ERROR: Can not create member: {}'.format(e))
            return -1
    else:
        return -2

    return Members.query.filter(Members.chatid == chat_id).all()[0].id 


def del_member(chat_id=None, secret=None, user_cid=None):
    """TODO: Docstring for del_member.

    :chat_id: TODO
    :returns: TODO

    """
    if chat_id:
        if not is_member(chat_id):
            return False, 'You are not connected yet!'
        try:
            secret_id = Members.query.filter(Members.chatid == chat_id).all()[0].secretid
            secret = Secrets.query.filter(Secrets.id == secret_id).all()[0].secret

            Members.query.filter(Members.chatid == chat_id).delete()
            db.session.commit()
            Secrets.query.filter(Secrets.id == secret_id).delete()
            db.session.commit()
            return chat_id, secret
        except Exception as e:
            print('ERROR: Can not delete member: {}'.format(e))

    if secret:
        if not check_su(user_cid):
            return False, 'You are not allowed drop secrets!'

        try:
            secret_id = Secrets.query.filter(Secrets.secret == secret).all()[0].id
            if Members.query.filter(Members.secretid == secret_id).all():
                chat_id = Members.query.filter(Members.secretid == secret_id).all()[0].chatid

                Members.query.filter(Members.chatid == chat_id).delete()
                db.session.commit()

            Secrets.query.filter(Secrets.id == secret_id).delete()
            db.session.commit()
            return chat_id, secret
        except Exception as e:
            print('ERROR: Can not delete member: {}'.format(e))
    
    return False


@ecologradbot.route('/', methods=['POST', 'GET'])
@auth_required()
@roles_accepted("admin")
def index():
    """Rendering html of ecologradbot index
    :returns: rendered page of ecologradbot index

    """
    if request.method == 'POST':
        webhook_url = request.form['webhook_url']
        try:
            webhook_del = requests.get(
                    URL.format(tg_token = current_app.config['TG_TOKEN'], method = 'deleteWebhook')
                    ).json()
            webhook_set = requests.get(
                    URL.format(tg_token = current_app.config['TG_TOKEN'], method = 'setWebhook?url=') + webhook_url
                    ).json()
        except Exception as e:
            print('ERROR: Can not set new webhook: {}'.format(e))

    r = requests.get(
        URL.format(tg_token = current_app.config['TG_TOKEN'], method = 'getWebhookInfo')
        ).json()
    # resp = json.dumps(r, indent=2, ensure_ascii=False)
    wh = tg.WebhookInfo.de_json(r.get('result'))
    prps = vars(wh)
    prps = {p: getattr(wh, p) for p in prps}
    form = WebhookForm()

    return render_template('ecologradbot/index.html', prps=prps, form=form)


@ecologradbot.route('/webhook-{}/'.format(wh_token), methods=['POST', 'GET'])
def webhook():
    """Rendering html of ecologradbot index
    :returns: rendered page of ecologradbot webhook

    """
    if request.method == 'POST':
        r = request.get_json()
        print(json.dumps(r, indent=2, ensure_ascii=False))
        u = tg.Make.de_json(r)

        global non_msg_update
        if u.update_type in non_msg_update:
            if u.update_type == 'callback_query':
                if getattr(u, u.update_type).data == 'cb_yes':
                    try:
                        res = del_member(getattr(u, u.update_type).message.chat.id)
                        res = 'You are disconnect secret: {}'.format(res[1])
                    except:
                        res = 'ERROR: Can not disconnect'
                    send_msg(getattr(u, u.update_type).message.chat.id, 'Result: {}'.format(res))
                    cb_answer(getattr(u, u.update_type).id) 

                elif getattr(u, u.update_type).data == 'cb_no':
                    res = 'Disconnection terminated'
                    send_msg(getattr(u, u.update_type).message.chat.id, 'Result: {}'.format(res))
                    cb_answer(getattr(u, u.update_type).id)
                return jsonify(r)

            send_msg(
                getattr(u, u.update_type).message.chat.id, 
                'Such update not supported.' 
            )
            return jsonify(r)

        global forbidden_content
        if getattr(u, u.update_type).content_type in forbidden_content:
            send_msg(
                getattr(u, u.update_type).chat.id, 
                'Such content not supported.', 
                reply_to_message_id=getattr(u, u.update_type).message_id
            )
            return jsonify(r)

        chat_id = getattr(u, u.update_type).chat.id
        message = getattr(u, u.update_type).text


        pattern = r'/\w+'

        if re.search(pattern, message):
            cmd = re.search(pattern, message).group()[1:]
            send_msg(chat_id, validate_cmd(cmd)[0])

            if validate_cmd(cmd)[1]:
                if cmd == 'start':
                    res = (
                            'Welcome to EcologradBot!\n'
                            'Enter \"/connect <secret>\" to get channel.\n'
                            'Secret is a token from Admin.\n\n'
                        )
                    send_msg(chat_id, '{}{}'.format(res, show_help()), parse_mode='Markdown', reply_markup=keyboard())

                elif cmd == 'help':
                    global cmd_set
                    res = 'Read help.\n'
                    send_msg(chat_id, 'Result: {}{}'.format(res, show_help()), reply_markup=keyboard(*cmd_set))

                elif cmd == 'secret':
                    try:
                        res = create_secret(chat_id, message.split()[1])
                    except:
                        res = create_secret(chat_id)
                    send_msg(chat_id, 'secret: <a href="https://t.me/ecologradbot?connect={0}">{0}</a>'.format(res),  parse_mode='HTML')

                elif cmd == 'connect':
                    try:
                        res = add_member(chat_id, message.split()[1])
                        res = 'You are connected with id: {}'.format(res)
                    except:
                        res = 'You are need to enter secret!'
                    send_msg(chat_id, 'Result: {}'.format(res))

                elif cmd == 'stop':
                    try:
                        res = del_member(None, message.split()[1], chat_id)
                        res = 'You are disconnect secret: {}'.format(res[1])
                        send_msg(chat_id, 'Result: {}'.format(res))
                    except:
                        btns = {
                                'Yes': 'cb_yes', 
                                'No': 'cb_no'
                                }
                        res = 'Are you really want to disconnect?'
                        send_msg(chat_id, 'Result: {}'.format(res), reply_markup=inline_keyboard(**btns))

        else:
            send_msg(chat_id)

        return jsonify(r)

    return redirect(url_for('ecologradbot.index'))

