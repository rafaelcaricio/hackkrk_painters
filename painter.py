#!/usr/bin/env python

import os
import base64
from json import dumps, loads
from StringIO import StringIO

from PIL import Image
import requests


class ChallengeService(object):
    NEW_URL = 'http://canvas.hackkrk.com/api/new_challenge.json'
    SOLUTION_URL = 'http://canvas.hackkrk.com/api/challenge/{challenge_id}.json'

    def __init__(self, token):
        self.token = token
        self.basic_auth = {
            'api_token': self.token
        }

    def get_new_challenge(self):
        return self.call(ChallengeService.NEW_URL)

    def call(self, url, data={}):
        data.update(self.basic_auth)
        headers = {'Content-Type': 'application/json'}
        print data
        print url
        response = requests.post(url, data=dumps(data), headers=headers)
        if response.status_code == 200:
            return loads(response.text)
        else:
            print response.text
            raise Exception("Non 200 code returned by the server.")

    def solve(self, challenge, base64_image):
        url = ChallengeService.SOLUTION_URL.format(challenge_id=challenge['id'])
        return self.call(url, data={'image': base64_image})

class ImageFinder(object):
    def get_image_with_color(self, r, g, b):
        raise NotImplementedError

    def convert_to_base64(self, image):
        return base64.b64encode(image)

class PILImageGenerator(ImageFinder):
    def get_image_with_color(self, r, g, b):
        image_object = Image.new('RGB', (64, 64), (r, g, b))
        byte_array = StringIO()
        image_object.save(byte_array, format='PNG')
        result = byte_array.getvalue()
        byte_array.close()
        return self.convert_to_base64(result)

if __name__ == '__main__':
    chlgs = ChallengeService(token=os.environ.get('HACKKRK_TOKEN', ''))
    current_challenge = chlgs.get_new_challenge()
    print 'Got the challenge: %s' % dumps(current_challenge)
    base64_image = PILImageGenerator().get_image_with_color(*current_challenge['color'])
    print 'Image generated: %s' % base64_image
    print chlgs.solve(current_challenge, base64_image)
