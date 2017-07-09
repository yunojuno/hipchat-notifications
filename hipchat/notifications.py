# -*- coding: utf-8 -*-
"""
Wrapper around the HipChat v2 API for sending user / room notifications.

This module contains a couple of generic functions for sending messages
to rooms and users within HipChat.

    >>> hipchat.notify_room('Customer Service', 'This is a message')
    >>> hipchat.notify_user('hugo', 'Hello, Hugo')

It includes some colour-specific helpers for room notifications:

    >>> hipchat.green('Customer service', 'This is a green message')

Requires HIPCHAT_API_TOKEN to be set.

"""
import logging
import os
import random
import requests

from .exceptions import HipChatError

if os.environ.get('HIPCHAT_API_SERVER'):
    API_SERVER_HOST = os.environ.get('HIPCHAT_SERVER')
else:
    API_SERVER_HOST = 'api.hipchat.com'

API_V2_ROOT = API_V2_ROOT = 'https://' + API_SERVER_HOST + '/v2/'
SEND_USER_MESSAGE_URL = lambda user: "{}user/{}/message".format(API_V2_ROOT, user)
SEND_ROOM_MESSAGE_URL = lambda room: "{}room/{}/notification".format(API_V2_ROOT, room)
VALID_COLORS = ('yellow', 'green', 'red', 'purple', 'gray', 'random')
VALID_FORMATS = ('text', 'html')

logger = logging.getLogger('hipchat')


def _token():
    """
    Get a valid 'personal' auth token from HIPCHAT_API_TOKEN env var.

    The HipChat API is rate limited, and the advice from the support team
    is that we either build a proper HipChat Connect app (which will take
    time, although may the way ahead), OR we use a set of tokens, each of
    which is a valid user token. To this end, the HIPCHAT_API_TOKEN var read
    in from the environ _could_ be a list of comma-separated tokens, in which
    case this function will pick one at random from the list.

    Return a token if one exists or None.

    """
    try:
        token = os.getenv('HIPCHAT_API_TOKEN')
        return random.choice(token.split(',')).strip()
    except AttributeError:
        return None


def _headers(auth_token):
    """
    Return authentication headers for API requests.

    Args:
        auth_token: string, a valid v2 API token.

    Returns a dict that can be passed into requests.post as the
    'headers' dict.

    """
    return {
        'Authorization': 'Bearer {}'.format(auth_token),
        'Host': API_SERVER_HOST,
        'Content-Type': 'application/json'
    }


def _api(
    url,
    message,
    color='yellow',
    label=None,
    notify=False,
    message_format='html'
):
    """
    Send message to user or room via API.

    Args:
        url: API endpoint
        message: The message body (1-10000 chars)

    Kwargs:
        color: background color for message (VALID_COLOR, default='yellow')
        label: label to be shown in addition to the sender's name, (0-64 chars)
        notify: bool (default=False), whether this message should trigger a
            user notification (change the tab color, play a sound, notify
            mobile phones, etc). Each recipient's notification preferences
            are taken into account.
        message_format: determines how the message is rendered inside
            HipChat applications (VALID_FORMAT, default='html')

    Returns HTTP Response object if successful, else raises HipChatError.

    """
    # asserts - message, colour and format are acceptable
    assert message is not None, "Missing message param"
    assert len(message) >= 1, "Message too short, must be 1-10,000 chars."
    assert color in VALID_COLORS, "Invalid color value: {}".format(color)
    assert message_format in VALID_FORMATS, "Invalid format: {}".format(message_format)

    token = _token()
    if token is None:
        logger.debug("HipChat API token not found, logging message instead:")
        logger.debug(message)
        return
    headers = _headers(auth_token=token)
    data = {
        'message': message[:10000],
        'color': color,
        'notify': notify,
        'message_format': message_format,
        'from': label[:64] if label else ''
    }

    try:
        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
        return resp
    except requests.HTTPError as ex:
        raise HipChatError(ex.response)


# see https://www.hipchat.com/docs/apiv2/method/send_room_notification
def notify_room(
    room,
    message,
    color='yellow',
    label=None,
    notify=False,
    message_format='html'
):
    """
    Send a room notification via 'Send room notification' API.

    Args:
        room: The id or url encoded name of the room
        message: The message body (1-10,000 chars)

    Kwargs:
        color: background color for message (VALID_COLOR, default='yellow')
        label: label to be shown in addition to the sender's name, (0-64 chars)
        notify: bool (default=False), whether this message should trigger a
            user notification (change the tab color, play a sound, notify
            mobile phones, etc). Each recipient's notification preferences
            are taken into account.
        message_format: determines how the message is rendered inside
            HipChat applications (VALID_FORMAT, default='html')

    Returns HTTP Response object if successful, else raises HipChatError.

    """
    return _api(
        SEND_ROOM_MESSAGE_URL(room),
        message,
        color=color,
        label=label,
        notify=notify,
        message_format=message_format
    )


# see https://www.hipchat.com/docs/apiv2/method/private_message_user
def notify_user(
    user,
    message,
    notify=False,
    message_format='html'
):
    """
    Send a user notification via 'Send private message' API.

    Args:
        user: The id, email address, or mention name of the recipient
        message: the message body (1-10,000 chars)

    Kwargs:
        notify: bool (default=False), whether this message should trigger a
            user notification (change the tab color, play a sound, notify
            mobile phones, etc). Each recipient's notification preferences
            are taken into account.
        message_format: determines how the message is rendered inside
            HipChat applications (VALID_FORMAT, default='html')

    Returns HTTP Response object if successful, else raises HipChatError.

    """
    return _api(
        SEND_USER_MESSAGE_URL(user),
        message,
        notify=notify,
        message_format=message_format
    )


# ================================
# Colour specific helper functions - NB these can only be sent to rooms.
# ================================

def yellow(room, message, **kwargs):
    """Send a yellow message to a room."""
    kwargs['color'] = 'yellow'
    return notify_room(room, message, **kwargs)


def gray(room, message, **kwargs):
    """Send a gray message to a room."""
    kwargs['color'] = 'gray'
    return notify_room(room, message, **kwargs)


# Aliased for UK spelling.
grey = gray


def green(room, message, **kwargs):
    """Send a green message to a room."""
    kwargs['color'] = 'green'
    return notify_room(room, message, **kwargs)


def purple(room, message, **kwargs):
    """Send a purple message to a room."""
    kwargs['color'] = 'purple'
    return notify_room(room, message, **kwargs)


def red(room, message, **kwargs):
    """Send a red message to a room."""
    kwargs['color'] = 'red'
    return notify_room(room, message, **kwargs)
