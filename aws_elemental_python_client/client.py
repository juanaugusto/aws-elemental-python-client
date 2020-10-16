from collections import OrderedDict
from urllib.parse import urlparse
import hashlib
import requests
import time
import xmltodict


class ContentNotFoundException(Exception):
    pass


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
    def find_content_by_name(self, name):
        contents = self.do_request('get', '/contents?name=%s' % name)

        try:
            contents = xmltodict.parse(contents)['contents']['content']
        except KeyError:
            # It means that no content with matching name was found
            raise ContentNotFoundException('Not found content with provided name in this Delta!')

        if type(contents) is OrderedDict:
            contents = [contents]

        for content in contents:
            if content['name'] == name:
                # /contents?name= does not return filters
                # so, we will do a new request to get content
                # with its filters.
                return self.find_content_by_id(content['id'])

        raise ContentNotFoundException('Not found content with provided name in this Delta!')

    def delete_content(self, content_id):
        self.do_request('delete', '/contents/%s' % content_id)

    def find_content_by_id(self, content_id):
        content = self.do_request('get', '/contents/%s' % content_id)
        
        try:
            content = xmltodict.parse(content)['content']
        except KeyError:
            # It means that no content with matching name was found
            raise ContentNotFoundException('Not found content with provided id in this Delta!')
            
        filters = [{
            'id': filter_['id'],
            'filter_type': filter_['filter_type'],
            'url_extension': filter_['url_extension']
        } for filter_ in content['filters']['filter']]

        return {
            'id': content['id'],
            'name': content['name'],
            'status': content['status'],
            'filters': filters
        }


class ElementalLive(Elemental):
    pass


class ElementalConductor(Elemental):
    pass
    