"""Custom hipchat exception classes."""
# see https://developer.atlassian.com/hipchat/guide/hipchat-rest-api/api-response-codes
BAD_RESPONSE_CODES = (400, 401, 403, 404, 405, 429, 500, 503)


class HipChatError(Exception):

    """Custom error raised when communicating with HipChat API."""

    def __init__(self, response):
        assert response.status_code in BAD_RESPONSE_CODES, (
            "Invalid HipChatError response.status_code:{}".format(response)
        )
        assert 'error' in response.json(), (
            "Invalid HipChatError response.json(): {}".format(response)
        )
        self.status_code = response.status_code
        # NB this is brittle and depends on the API error response existing
        # in the correct format. This is by design - if the response format
        # changes we need to know.
        self.message = response.json()['error']['message']
        super(HipChatError, self).__init__()
