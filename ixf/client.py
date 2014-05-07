#!/bin/env python

import httplib
import json
import urllib

class IXFClient(object):

    def __init__(self, **kwargs):
        """
        IX-F database client


        """
        self.host = 'ixf.20c.com'
        self.port = 7010
        self.path = '/api/'
        self.user = None
        self.passwd = None
        self.timeout = None

        # overwrite any param from keyword args
        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])

    def _url(self, __typ, __id=None, **kwargs):
        """
        Build URL for connection
        """
        url = 'https://' + self.host

        if self.port != 443:
            url = url + ":" + str(self.port)

        url += self.path + __typ

        if __id:
            url += '/' + str(__id)

        if kwargs:
            url += '?' + urllib.urlencode(kwargs)

        return url

    def _request(self, url, method='GET', data=None):
        """
        send the request, return response obj
        """
        cxn = httplib.HTTPSConnection(self.host, self.port, strict=True, timeout=self.timeout)

        headers = {
                  "Accept": "text/plain"
                  }

        if self.user:
            auth = 'Basic ' + base64.urlsafe_b64encode("%s:%s" % (self.user, self.passwd))
            headers['Authorization'] = auth

        if data:
            data = urllib.urlencode({'arg': json.dumps(data)})
            headers["Content-type"] = "application/x-www-form-urlencoded"

#        print "%s to %s data: '%s' " % (method, url, str(data))
        cxn.request(method, url, data, headers)

        return cxn.getresponse()

    def _load(self, req):
        data = json.load(req)

#        data = req.read()
#        data = json.loads(data)
#        print "got data: %s" % data

        if 'error' in data:
            err = data['error']
            if err.startswith('Object not found'):
                raise KeyError(err)
            else:
                raise Exception(err)

        return data

    def _mangle_data(self, data):
        if not 'id' in data and 'pk' in data:
            data['id'] = data['pk']
        if '_rev' in data:
            del data['_rev']
        if 'pk' in data:
            del data['pk']
        if '_id' in data:
            del data['_id']

    def list_all(self, typ, **kwargs):
        return self._load(self._request(self._url(typ, **kwargs)))

    def get(self, typ, id):
        """
        Load type by id
        """
        return self._load(self._request(self._url(typ, id)))

    def save(self, typ, data):
        """
        Save the dataset pointed to by data
        """
        if 'id' in data:
            return self._load(self._request(self._url(typ, data['id']), 'PUT', data))

        return self._load(self._request(self._url(typ), 'POST', data))

    def update(self, typ, id, **kwargs):
        """
        update just fields sent by keywork arg
        """
        return self._load(self._request(self._url(typ, id), 'PUT', kwargs))

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
        return self.list_all('IXP', **kwargs)

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

