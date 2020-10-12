from collections import OrderedDict
from urllib.parse import urlparse
import hashlib
import requests
import time
import xmltodict


class Elemental:

    def __init__(self, host, user, api_key):
        self.host = host
        self.user = user
        self.api_key = api_key
        self.base_url = 'http://%s' % self.host
    
    def get_auth_key(self, complete_url, expires):
        return hashlib.md5(
                    (self.api_key + 
                        hashlib.md5((complete_url + self.user + self.api_key + expires).
                        encode('utf-8')).hexdigest()).encode('utf-8')).hexdigest()

    def do_request(self, method, path):
        expires = str(int(time.time()) + 60)

        complete_url = '%s%s' % (self.base_url, path)

        headers = {
            'X-Auth-User': self.user,
            'X-Auth-Expires': expires,
            'X-Auth-Key': self.get_auth_key(urlparse(complete_url).path, expires),
            'Accept': 'application/xml',
            'Content-type': 'application/xml'
        }
        
        r = requests.request(method=method, url=complete_url, headers=headers)

        return r.text


class ElementalDelta(Elemental):

    def get_contents(self):
        return self.do_request('get', '/contents')

    # status can be [complete, active]
    def find_contents_by_name(self, name):
        contents = self.do_request('get', '/contents?name=%s' % name)

        try:
            contents = xmltodict.parse(contents)['contents']['content']
        except KeyError:
            # It means that no content with matching name was found
            return []

        if type(contents) is OrderedDict:
            contents = [contents]
        
        return [
            {
                'id': content['id'],
                'name': content['name'],
                'status': content['status']
            }
            for content in contents if content['name'] == name
        ]

    def delete_content(self, content_id):
        self.do_request('delete', '/contents/%s' % content_id)

            

class ElementalLive(Elemental):
    pass


class ElementalConductor(Elemental):
    pass
    