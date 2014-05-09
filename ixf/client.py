#!/bin/env python

import base64
import httplib
import json
import urllib
import urlparse

class IXFClient(object):

    def __init__(self, **kwargs):
        """
        IX-F database client


        """
        self.host = 'ixf.20c.com'
        self.port = 7010
        self.path = '/api/'
        self.user = None
        self.password = None
        self.timeout = None
        self.validate_ssl = True

        # overwrite any param from keyword args
        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])

    def _url(self, __typ, __id=None, **kwargs):
        """
        Build URL for connection
        """
        url = self.path + __typ

        if __id:
            url += '/' + str(__id)

        if kwargs:
            url += '?' + urllib.urlencode(kwargs)

        return url

    def _request(self, url, method='GET', data=None, cxn=None):
        """
        send the request, return response obj
        """
        if not cxn:
            cxn = httplib.HTTPSConnection(self.host, self.port, strict=True, timeout=self.timeout)

        headers = {
                  "Accept": "application/json"
                  }

        if self.user:
            auth = 'Basic ' + base64.urlsafe_b64encode("%s:%s" % (self.user, self.password))
            headers['Authorization'] = auth

        if data:
            data = json.dumps(data)
            headers["Content-length"] = len(data)
            headers["Content-type"] = "application/json"

#        print "%s %s headers:'%s' data:'%s' " % (method, url, str(headers), str(data))
        cxn.request(method, url, data, headers)
        return cxn.getresponse()

    def _throw(self, res, data):
        err = data.get('meta', {}).get('error', 'Unknown')
        if res.status < 600:
            if res.status == 404:
                raise KeyError(err)
            else:
                raise Exception("%d %s" % (res.status, err))

        # Internal
        raise Exception("Internal error %d %s" % (res.status, err))

    def _load(self, res):
        try:
            data = json.load(res)
#            data = res.read()
#            print "%d got data: %s" % (res.status, data)
#            data = json.loads(data)

        except ValueError:
            data = {}

        if res.status < 300:
            return data.get('data', [])

        self._throw(res, data)

    def _mangle_data(self, data):
        if not 'id' in data and 'pk' in data:
            data['id'] = data['pk']
        if '_rev' in data:
            del data['_rev']
        if 'pk' in data:
            del data['pk']
        if '_id' in data:
            del data['_id']

    def all(self, typ, **kwargs):
        return self._load(self._request(self._url(typ, **kwargs)))

    def get(self, typ, id):
        """
        Load type by id
        """
        return self._load(self._request(self._url(typ, id)))

    def create(self, typ, data):
        res = self._request(self._url(typ), 'POST', data)
        if res.status != 201:
            data = res.read()
            self._throw(res, data)

        loc = res.getheader('Location')
        if loc.startswith('/'):
            return self._load(self._request(loc))

        url = urlparse.urlparse(loc)
        cxn = httplib.HTTPSConnection(url.netloc, strict=True, timeout=self.timeout)
# TODO check scheme, add args
        return self._load(self._request(url.path, cxn=cxn))

    def update(self, typ, id, **kwargs):
        """
        update just fields sent by keyword args
        """
        return self._load(self._request(self._url(typ, id), 'PUT', kwargs))

    def save(self, typ, data):
        """
        Save the dataset pointed to by data (create or update)
        """
        if 'id' in data:
            return self._load(self._request(self._url(typ, data['id']), 'PUT', data))

        return self.create(typ, data)

    def rm(self, typ, id):
        """
        remove typ by id
        """
        return self._load(self._request(self._url(typ, id), 'DELETE'))


    def ixp_all(self, **kwargs):
        """
        List all IXPs
        Valid arguments:
            skip : number of records to skip
            limit : number of records to limit request to
        """
        return self.all('IXP', **kwargs)

    def ixp(self, id):
        """
        Load IXP by id
        """
        return self.get('IXP', id)

    def ixp_save(self, data):
        return self.save('IXP', data)

    def ixp_rm(self, id):
        """
        remove IXP by id
        """
        return self.rm('IXP', id)

