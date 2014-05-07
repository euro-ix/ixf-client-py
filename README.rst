IXF Database - python client
============================

Python RESTful interface to the IXF database,


Installation
------------

The easiest method of installation is go get it directly from `PyPI`_ using
`pip`_ or `setuptools`_ by running the respective command below.

.. code-block:: bash

    pip install -U ixf

or:

.. code-block:: bash

    easy_install -U ixf

Otherwise you can clone it with:

.. code-block:: bash

    git clone https://github.com/euro-ix/ixf-client-py.git
    cd ixf-client-py

Then install it directly from source:

.. code-block:: bash

    python setup.py install

or if you want to hack on it, link it directly into your environment with:

.. code-block:: bash

    python setup.py develop


Using IXFClient
---------------

Import the module
^^^^^^^^^^^^^^^^^

.. code-block:: python

    from ixf import IXFClient

Create the connection
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # anonymous
    ixfc = IXFClient()

or

.. code-block:: python

    # writes require authentication
    ixfc = IXFClient(user='guest, password='guest')

or

.. code-block:: python

    # override to localhost for development
    ixfc = IXFClient(host="localhost", port=8000, user="test", password="test")


Common operations
^^^^^^^^^^^^^^^^^

.. code-block:: python

    # list all records of type IXP
    print ixfc.list_all('IXP')

    # get IXP42
    print ixfc.get('IXP', 42)

    # delete IXP42
    print ixfc.rm('IXP', 42)

    # create new IXP
    data = {
        "full_name": "Test IXP",
        "short_name": "TIX",
        }
    response = self.db.save("IXP", data)
    ixpid = response['id']

    # update from keyword variables
    ixfc.update('IXP', 42, full_name="Test IXP", short_name="TIX")

    # update from dict
    ixfc.update('IXP', 42, **data)


Any errors throw exceptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # try to get a non existent IXP
    ixfc.get('IXP', 999999999)

results in:

.. code-block:: python

    KeyError: u'Object not found: IXP.999999999'

.. _`PyPI`: http://pypi.python.org/
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`pip`: http://www.pip-installer.org/

