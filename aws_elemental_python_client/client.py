from collections import OrderedDict
from urllib.parse import urlparse
import hashlib
import requests
import time
import xmltodict


class ContentNotFoundException(Exception):
    pass


class FilterNotFoundException(Exception):
    pass


class ElementalHTTPError(Exception):

    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message
        super().__init__('Status: %s -  Error Message: %s' % (self.status_code, self.error_message))


class ElementalHTTP404Error(ElementalHTTPError):
    
    def __init__(self, error_message):
        super().__init__(404, error_message)


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

    def do_request(self, method, path, data=None):
        expires = str(int(time.time()) + 60)

        complete_url = '%s%s' % (self.base_url, path)

        headers = {
            'X-Auth-User': self.user,
            'X-Auth-Expires': expires,
            'X-Auth-Key': self.get_auth_key(urlparse(complete_url).path, expires),
            'Accept': 'application/xml',
            'Content-type': 'application/xml'
        }
        
        r = requests.request(method=method, 
                             url=complete_url, 
                             headers=headers,
                             data=data)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            if r.status_code == 404:
                raise ElementalHTTP404Error(r.text)
            else:
                raise ElementalHTTPError(r.status_code, r.text)

        return r.text


class ElementalDelta(Elemental):

    # status can be [complete, active]
    def find_content_by_name(self, name):
        try:
            contents = self.do_request('get', '/contents?name=%s' % name)
        except ElementalHTTP404Error as e:
            raise ContentNotFoundException('Not found content with provided name in this Delta!')

        contents = xmltodict.parse(contents).get('contents', {}).get('content', [])

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
        try:
            content = self.do_request('get', '/contents/%s' % content_id)
        except ElementalHTTP404Error as e:
            raise ContentNotFoundException('Not found content with provided id in this Delta!')
        
        content = xmltodict.parse(content)['content']
        
        try:
            filters = content.get('filters', {}).get('filter', [])
        except AttributeError:
            filters = []
           
        if type(filters) is OrderedDict:
            filters = [filters]

        filters = [{
            'id': filter_['id'],
            'filter_type': filter_['filter_type'],
            'url_extension': filter_['url_extension']
        } for filter_ in filters]

        return {
            'id': content['id'],
            'name': content['name'],
            'status': content['status'],
            'filters': filters
        }

    def update_filter(self, xml, content_id, filter_id):

        self.do_request('put', 
                        '/contents/%s/filters/%s' % (content_id, filter_id),
                        data=xmltodict.unparse(xml))


class ElementalLive(Elemental):
    pass


class ElementalConductor(Elemental):
    pass
    