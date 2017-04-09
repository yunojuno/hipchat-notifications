# -*- coding: utf-8 -*-
import logging
import requests
import unittest

from .compat import mock
from .exceptions import HipChatError
from .logger import HipChatHandler
from .notifications import (
    _api,
    _headers,
    _token,
    gray,
    green,
    grey,
    notify_room,
    notify_user,
    purple,
    red,
    SEND_ROOM_MESSAGE_URL,
    SEND_USER_MESSAGE_URL,
    yellow,
)


class LoggerTests(unittest.TestCase):

    """hipchat.logger tests."""

    def setUp(self):
        self.logger = logging.getLogger('test')
        self.logger.setLevel(logging.DEBUG)

    @mock.patch('hipchat.logger.notify_room')
    def test_logger_defaults(self, mock_notify):
        handler = HipChatHandler('token', 'room')
        self.logger.handlers = [handler]
        self.logger.debug('foo')
        mock_notify.assert_called_with(
            'room',
            'foo',
            color='gray',
            label='',
            message_format='html',
            notify=False
        )

    @mock.patch('hipchat.logger.notify_room')
    def test_logger_settings(self, mock_notify):
        handler = HipChatHandler(
            'token',
            'room',
            colors={
                'DEBUG': 'red'
            },
            label='hello',
            message_format='text',
            notify=True
        )
        self.logger.handlers = [handler]
        self.logger.debug('foo')
        mock_notify.assert_called_with(
            'room',
            'foo',
            color='red',
            label='hello',
            message_format='text',
            notify=True
        )


class ErrorTests(unittest.TestCase):

    """hipchat.exceptions tests."""

    def test_init(self):
        """Test initialisation from JSON."""
        data = {
            'error': {
                'message': 'foobar'
            }
        }
        response = mock.Mock(spec=requests.Response)

        # good status code is not valid
        response.status_code = 200
        self.assertRaises(AssertionError, HipChatError, response)

        # error status code, incorrectly formatted response.json()
        response.status_code = 400
        response.json.return_value = {}
        self.assertRaises(AssertionError, HipChatError, response)

        # should pass
        response.json.return_value = data
        error = HipChatError(response)
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.message, 'foobar')


class FunctionTests(unittest.TestCase):

    """hipchat module function tests."""

    def test__token(self):
        """Test _token function can handle all variations of HIPCHAT_API_TOKEN."""
        # no env var set, should be None
        self.assertIsNone(_token())
        # a single token
        with mock.patch.dict('os.environ', {'HIPCHAT_API_TOKEN': 'abc'}):
            self.assertEqual(_token(), 'abc')
        # multiple tokens - can't be sure which one we'll get,
        # but can check that the string is split correctly
        with mock.patch.dict('os.environ', {'HIPCHAT_API_TOKEN': 'abc,def , ghi'}):
            self.assertTrue(_token() in ['abc', 'def', 'ghi'])

    def test__headers(self):
        """Test _headers formats token correctly."""
        self.assertEqual(
            _headers('foo'),
            {
                'Authorization': 'Bearer foo',
                'Host': 'api.hipchat.com',
                'Content-Type': 'application/json'
            }
        )

    @mock.patch('requests.post')
    def test__api(self, mock_post):
        """Test all code paths in the _api function work as expected."""
        # message is too short, long, missing
        self.assertRaises(AssertionError, _api, 'url', None)
        self.assertRaises(AssertionError, _api, 'url', '')
        # colour, format is invalid
        self.assertRaises(AssertionError, _api, 'url', 'foo', color='black')
        self.assertRaises(AssertionError, _api, 'url', 'foo', message_format='png')
        # no token - doesn't call api
        self.assertIsNone(_api('foo', 'bar'))
        mock_post.assert_not_called()
        # set a token
        with mock.patch.dict('os.environ', {'HIPCHAT_API_TOKEN': 'token'}):
            # try the defaults
            self.assertEqual(_api('foo', 'bar'), mock_post.return_value)
            mock_post.assert_called_once_with(
                'foo',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer token',
                    'Host': 'api.hipchat.com'
                },
                json={
                    'notify': False,
                    'message_format': 'html',
                    'color': 'yellow',
                    'message': 'bar',
                    'from': ''
                }
            )
            # try the kwargs
            self.assertEqual(
                _api('foo', 'bar', color='red', label='baz', notify=True, message_format='text'),
                mock_post.return_value
            )
            mock_post.assert_called_with(
                'foo',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer token',
                    'Host': 'api.hipchat.com'
                },
                json={
                    'notify': True,
                    'message_format': 'text',
                    'color': 'red',
                    'message': 'bar',
                    'from': 'baz',
                }
            )

            # force response.raise_for_status to raise an error
            response = mock.Mock(status_code=400)
            response.json.return_value = {'error': {'message': 'uh-oh'}}
            mock_post.side_effect = requests.HTTPError(response=response)
            self.assertRaises(HipChatError, _api, 'foo', 'bar')

    @mock.patch('hipchat.notifications._api')
    def test_notify_room(self, mock_api):
        """Test the notify_room function calls the correct API."""
        notify_room('foo', 'bar')
        mock_api.assert_called_once_with(
            SEND_ROOM_MESSAGE_URL('foo'),
            'bar',
            color='yellow',
            message_format='html',
            notify=False,
            label=None
        )

    @mock.patch('hipchat.notifications._api')
    def test_notify_user(self, mock_api):
        """Test the notify_user function calls the correct API."""
        notify_user('Fred', 'Hello, Fred')
        mock_api.assert_called_once_with(
            SEND_USER_MESSAGE_URL('Fred'),
            'Hello, Fred',
            message_format='html',
            notify=False,
        )

    @mock.patch('hipchat.notifications.notify_room')
    def test_yellow(self, mock_api):
        yellow('foo', 'bar')
        mock_api.assert_called_once_with('foo', 'bar', color='yellow')

    @mock.patch('hipchat.notifications.notify_room')
    def test_gray(self, mock_api):
        gray('foo', 'bar')
        mock_api.assert_called_once_with('foo', 'bar', color='gray')

    @mock.patch('hipchat.notifications.notify_room')
    def test_grey(self, mock_api):
        grey('foo', 'bar')
        mock_api.assert_called_once_with('foo', 'bar', color='gray')

    @mock.patch('hipchat.notifications.notify_room')
    def test_green(self, mock_api):
        green('foo', 'bar')
        mock_api.assert_called_once_with('foo', 'bar', color='green')

    @mock.patch('hipchat.notifications.notify_room')
    def test_purple(self, mock_api):
        purple('foo', 'bar')
        mock_api.assert_called_once_with('foo', 'bar', color='purple')

    @mock.patch('hipchat.notifications.notify_room')
    def test_red(self, mock_api):
        red('foo', 'bar')
        mock_api.assert_called_once_with('foo', 'bar', color='red')


if __name__ == '__main__':
    unittest.main()
