"""HipChat enabled python logger."""
import logging

from .notifications import notify_room


class HipChatHandler(logging.Handler):

    """Log handler used to send notifications to HipChat."""

    DEFAULT_COLOURS = {
        'DEBUG': 'gray',
        'INFO': 'yellow',
        'WARN': 'purple',
        'WARNING': 'purple',
        'ERROR': 'red',
        'CRITICAL': 'red',
    }

    def __init__(
        self,
        token,
        room,
        label='',
        notify=False,
        colors=DEFAULT_COLOURS,
        message_format='html'
    ):
        """
        Args:
            token: the auth token for access to the API - see hipchat.com
            room: the numerical id of the room to send the message to

        Kwargs:
            sender : the 'from' property of the message - appears in the HipChat window
            notify : if True, HipChat pings / bleeps / flashes when message is received
            colors : a dict of level:color pairs (e.g. {'DEBUG:'red'} used to
                override the default color)

        """
        logging.Handler.__init__(self)
        self.token = token
        self.room = room
        self.label = label
        self.notify = notify
        self.colors = colors
        self.message_format = message_format

    def emit(self, record):
        """Send the record info to HipChat."""
        notify_room(
            self.room,
            record.getMessage(),
            color=self.colors.get(record.levelname, 'yellow'),
            label=self.label,
            notify=self.notify,
            message_format=self.message_format
        )
