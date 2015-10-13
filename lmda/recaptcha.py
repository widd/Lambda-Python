import json
from flask import request
import requests
from lmda import app


def validate_captcha(response):
    payload = {'secret': app.config['RECAPTCHA_SECRET'],
               'response': response,
               'remoteip': request.remote_addr}
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    response_obj = json.loads(r.text)
    return response_obj.get('success', False)
