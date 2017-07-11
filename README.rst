.. image:: https://travis-ci.org/yunojuno/hipchat-notifications.svg?branch=master
    :target: https://travis-ci.org/yunojuno/hipchat-notifications

.. image:: https://badge.fury.io/py/hipchat-notifications.svg
    :target: https://badge.fury.io/py/hipchat-notifications

HipChat Notifications
=====================

This is a very simple library for sending user and room notifications to HipChat via their v2 API.

It contains a couple of generic functions for sending messages
to rooms and users within HipChat.

.. code:: python

    >>> hipchat.notify_room('Customer Service', 'This is a message')
    >>> hipchat.notify_user('hugo', 'Hello, Hugo')

It includes some colour-specific helpers for room-only notifications:

.. code:: python

    >>> hipchat.green('Customer service', 'This is a green message')

The functions support the ``message_format`` values:

    **html** - Message is rendered as HTML and receives no special treatment. Must be valid HTML and entities must be escaped (e.g.: '&amp;' instead of '&'). May contain basic tags: a, b, i, strong, em, br, img, pre, code, lists, tables.

    **text** - Message is treated just like a message sent by a user. Can include @mentions, emoticons, pastes, and auto-detected URLs (Twitter, YouTube, images, etc).

    >>> hipchat.green('Customer service', 'Hello @fred', message_format='text')

The ``color``, ``notify`` and ``from`` parameters are also supported (``from`` is passed as a kwarg called ``label``):

.. code:: python

    >>> notify_room(
    ...     'customer service',
    ...     'Hey there @Tony',
    ...     color='red',
    ...     label='baz',
    ...     notify=True,
    ...     message_format='text'
    ... )

Settings
--------

The following settings are read from the environment using ``os.getenv``

* ``HIPCHAT_API_TOKEN``

A valid API access token. See the `API docs <https://developer.atlassian.com/hipchat/guide/hipchat-rest-api/api-access-tokens>`_ for details on how to
generate a token. (Hint: the easiest way is to use a "Personal access token"
generated through the site.)

If there is no token set in the environment the notifications will be logged
using the 'hipchat' logger, with a DEBUG level.

Installation
------------

The library is available on PyPI as 'hipchat_notifications'.

Tests
-----

The tests can be run using ``tox``:

.. code:: shell

    $ tox


Contributors
------------

* Hugo Rodger-Brown - @hugorodgerbrown
* Roberto Salgado - @droberin
