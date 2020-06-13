# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json
import random
import string


class ApiLifesize(models.TransientModel):
    _name = 'api.lifesize'
    _description = "Api Lifesize"

    def api_crud(self, vals):
        token_company = self.env.user.company_id.key_lifesize
        if not token_company:
            raise ValidationError("Please write token")

        def code(length=4, chars=string.digits):
            return ''.join([random.choice(chars) for i in range(length)])

        def api_create(vals):
            url = 'http://meetingapi.lifesizecloud.com' + '/meeting/create'
            try:
                description = vals.get('description').replace('\n',' - ')
            except:
                description = vals.get('description')
            body = {
                "displayName": vals.get('displayName'),
                "description": description,
                "pin": code(),
                "ownerExtension": vals.get('ownerExtension'),
                "tempMeeting": "true",
                "hiddenMeeting": vals.get('hiddenMeeting'),
            }
            resp = requests.post(url=url,
                                 data=json.dumps(body),
                                 headers={"key": token_company,
                                          "Content-type": "application/json"})
            if resp.ok:
                if not resp.json().get('errorDescription'):
                    res = resp.json()
                    resp.close
                    return res
                else:
                    resp.close
                    raise ValidationError('API message: {}'.format(
                        resp.json().get('errorDescription'))
                    )
            else:
                raise ValidationError('Bad response: %s.' % (resp.json()))

        def api_read(vals):
            url = 'http://meetingapi.lifesizecloud.com' + '/meeting/get'
            params = {
                "uuid": vals.get('uuid'),
            }
            resp = requests.get(url=url,
                                params=params,
                                headers={"key": token_company,
                                         "Content-type": "application/json"})
            if resp.ok:
                res = resp.json()
                resp.close
                return res
            else:
                raise ValidationError('Bad response: %s.' % (resp.json()))

        def api_update(vals):
            url = 'http://meetingapi.lifesizecloud.com' + '/meeting/update'
            body = {
                "uuid": vals.get('uuid'),
                "description": vals.get('description'),
                "ownerExtension": vals.get('ownerExtension'),
            }
            resp = requests.put(url=url,
                                data=json.dumps(body),
                                headers={"key": token_company,
                                         "Content-type": "application/json"})
            if resp.ok:
                if not resp.json().get('errorDescription'):
                    res = resp.json()
                    resp.close
                    return res
                else:
                    resp.close
                    raise ValidationError('API message: {}'.format(
                        resp.json().get('errorDescription'))
                    )
            else:
                raise ValidationError('Bad response: %s.' % (resp.json()))

        def api_delete(vals):
            url = 'http://meetingapi.lifesizecloud.com' + '/meeting/delete'
            body = {
                "uuid": vals.get('uuid'),
            }
            resp = requests.delete(url=url,
                                   data=json.dumps(body),
                                   headers={"key": token_company,
                                            "Content-type": "application/json"})
            if resp.ok:
                if not vals.get('errorDescription'):
                    res = resp.json()
                    resp.close
                    return res
                else:
                    raise ValidationError('API message: {}'.format(resp.json().get('errorDescription')))
            else:
                raise ValidationError('Bad response: %s.' % (resp.json()))

        def api_load(vals):
            url = 'http://meetingapi.lifesizecloud.com' + '/meeting/load'
            params = {'limitSize': vals.get('number')}
            resp = requests.get(url=url,
                                params=params,
                                headers={"key": token_company,
                                         "Content-type": "application/json"})
            if resp.ok:
                res = resp.json()
                resp.close
                return res
            else:
                raise ValidationError('Bad response: %s.' % (resp.json()))

        if vals['method'] == 'create':
            return api_create(vals)
        elif vals['method'] == 'read':
            return api_read(vals)
        elif vals['method'] == 'update':
            return api_update(vals)
        elif vals['method'] == 'delete':
            return api_delete(vals)
        elif vals['method'] == 'load':
            return api_load(vals)

    def resp2dict(self, resp):
        body = resp.get('body')
        if body.get('action') == 'UPDATED':
            res = dict(lifesize_modified = True)
            return res
        if body.get('action') == 'CREATED':
            res = dict(
                lifesize_pin = body.get('pin'),
                lifesize_uuid = body.get('uuid'),
                lifesize_url = 'https://call.lifesizecloud.com/{}'.format(body.get('extension')),
                lifesize_meeting_ext = body.get('extension'),
                lifesize_owner = body.get('ownerExtension'),
            )
            return res