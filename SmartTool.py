#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import random
import logging
import requests
import vk
from forismatic import Forismatic

class SmartTool:

    def __init__(self, app_id, access_token, group_id, myprofile_id):
        self.vkapi = vk.API(access_token=access_token)
        self.group_id = group_id
        self.myprofile_id = myprofile_id

    def listdir_nohidden(self, path):
        filelist = []
        for f in os.listdir(path):
            if not f.startswith('.'):
                filelist.append(f)
        return filelist

    def replace_non_ascii(self, x):
        return ''.join(i if ord(i) < 128 else '_' for i in x) 

    def get_photo_attachment(self, path_to_file):
        upload_url = self.vkapi.photos.getWallUploadServer(group_id=self.group_id)[u'upload_url']
        files = {'photo': (self.replace_non_ascii(os.path.basename(path_to_file)), open(path_to_file, 'r'))}
        post_response = requests.post(upload_url, files=files)
        photo_response = self.vkapi.photos.saveWallPhoto(group_id=self.group_id, server=post_response.json()[u'server'], photo=post_response.json()[u'photo'], hash=post_response.json()[u'hash'])
        photo_attachment = 'photo' + str(photo_response[0][u'owner_id']) + '_' + str(photo_response[0][u'id'])
        return photo_attachment

    def get_audio_attachment(self, query):
        audio_response = self.vkapi.audio.search(q=query, auto_complete=1, count=1, sort=2)
        audio_attachment = 'audio' + str(audio_response[u'items'][0][u'owner_id']) + '_' + str(audio_response[u'items'][0][u'id'])
        return audio_attachment

    def wall_post(self, owner_id=None, from_group=1, message=None, attachments=None):
        owner_id = -self.group_id
        self.vkapi.wall.post(owner_id=owner_id, from_group=from_group, message=message, attachments=attachments)

    def make_post(self, path_to_file):
        try:
            data = {'message': os.path.basename(path_to_file).split(';')[0], 'audio': os.path.basename(path_to_file).split('.jpg')[0].split(';')[1]}
        except IndexError:
            self.wall_post(attachments=self.get_photo_attachment(path_to_file))
        else:
            if (data['message'] == ''):
                trackname = data['audio']
                try:
                    self.wall_post(attachments=self.get_photo_attachment(path_to_file) + ',' + self.get_audio_attachment(trackname))
                except IndexError:
                    self.wall_post(attachments=self.get_photo_attachment(path_to_file))
            elif (data['audio'] == ''):
                message = data['message']
                self.wall_post(message=message, attachments=self.get_photo_attachment(path_to_file))
            else:
                message = data['message']
                trackname = data['audio']
                self.wall_post(message=message, attachments=self.get_photo_attachment(path_to_file) + ',' + self.get_audio_attachment(trackname))
        os.unlink(path_to_file)
        return 0

    def post_quote(self):
        f = Forismatic()
        q = f.get_quote(lang='ru')
        quote = '%s\n%s' % (q.quote.encode('utf-8', 'ignore'), q.author.encode('utf-8', 'ignore'))
        self.wall_post(message=quote)

    def post_message(self, path_to_file):
        with open(path_to_file,'r') as cytaty_orig:
            cytaty = cytaty_orig.readlines()
            cytata = cytaty[0].strip()
            self.vkapi.wall.post(owner_id=-self.group_id, from_group=1, message=cytata)
        with open(path_to_file,'w') as cytaty_changed:
            for w in cytaty[1:]:
                cytaty_changed.write(w)

if __name__ == '__main__':
    x = SmartTool('app_id', 'your_token', group_id, 'your_profile_id')
    if (random.randint(0,99) > 20):
        try:
            pics_for_vk = 'directory_where_stored_pics'
            filename = x.listdir_nohidden(pics_for_vk)[0]
            path_to_file = os.path.join(pics_for_vk, filename)
            x.make_post(path_to_file)
        except Exception:
            logging.basicConfig(level=logging.DEBUG, filename='your_logfile', format='%(asctime)s %(levelname)s:%(message)s')
            logging.exception('Failed to upload photo: ' + filename)
            x.post_quote()
            
    else:
        x.post_quote()