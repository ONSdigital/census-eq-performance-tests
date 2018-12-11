import logging
import re
import time

import requests

absolute_http_url_regexp = re.compile(r"^https?://", re.I)
log = logging.getLogger(__name__)


class LocustResponse(requests.Response):

    def raise_for_status(self):
        if hasattr(self, 'error') and self.error:
            raise self.error
        requests.Response.raise_for_status(self)


class HttpSession(requests.Session):
    def __init__(self, base_url, stats, *args, **kwargs):
        super(HttpSession, self).__init__(*args, **kwargs)

        self.base_url = base_url
        self.stats = stats

    def _build_url(self, path):
        """ prepend url with hostname unless it's already an absolute URL """
        if absolute_http_url_regexp.match(path):
            return path
        else:
            return "%s%s" % (self.base_url, path)
    
    def request(self, method, url, name=None, catch_response=False, **kwargs):
        # prepend url with hostname unless it's already an absolute URL
        url = self._build_url(url)
        
        # store meta data that is used when reporting the request to locust's statistics
        request_meta = {}
        
        # set up pre_request hook for attaching meta data to the request object
        request_meta["method"] = method
        request_meta["start_time"] = time.time()
        
        response = self._send_request_safe_mode(method, url, **kwargs)
        
        # record the consumed time
        request_meta["response_time"] = int((time.time() - request_meta["start_time"]) * 1000)
        
    
        request_meta["name"] = name or (response.history and response.history[0] or response).request.path_url
        
        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body
        if kwargs.get("stream", False):
            request_meta["content_size"] = int(response.headers.get("content-length") or 0)
        else:
            request_meta["content_size"] = len(response.content or b"")
        
        if catch_response:
            response.locust_request_meta = request_meta
            return ResponseContextManager(response, self.stats)
        else:
            try:
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                log.exception(e)
                self.stats.record(request_meta["response_time"])
            else:
                log.debug(f'{method}: {url}')
                self.stats.record(request_meta["response_time"])
            return response
    
    def _send_request_safe_mode(self, method, url, **kwargs):
        """
        Send an HTTP request, and catch any exception that might occur due to connection problems.
        
        Safe mode has been removed from requests 1.x.
        """
        try:
            return requests.Session.request(self, method, url, **kwargs)
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL):
            raise
        except requests.exceptions.RequestException as e:
            r = LocustResponse()
            r.error = e
            r.status_code = 0  # with this status_code, content returns None
            r.request = requests.Request(method, url).prepare() 
            return r


class ResponseContextManager(LocustResponse):
    """
    A Response class that also acts as a context manager that provides the ability to manually 
    control if an HTTP request should be marked as successful or a failure in Locust's statistics

    This class is a subclass of :py:class:`Response <requests.Response>` with two additional 
    methods: :py:meth:`success <locust.clients.ResponseContextManager.success>` and 
    :py:meth:`failure <locust.clients.ResponseContextManager.failure>`.
    """

    _is_reported = False

    def __init__(self, response, stats):
        # copy data from response to this object
        self.__dict__ = response.__dict__
        self.stats = stats

    def __enter__(self):
        return self

    def __exit__(self, exc, value, traceback):
        if self._is_reported:
            # if the user has already manually marked this response as failure or success
            # we can ignore the default haviour of letting the response code determine the outcome
            return exc is None

        if exc:
            if isinstance(value, requests.exceptions.ResponseError):
                self.failure(value)
            else:
                return False
        else:
            try:
                self.raise_for_status()
            except requests.exceptions.RequestException as e:
                self.failure(e)
            else:
                self.success()
        return True

    def success(self):
        self.stats.record(self.locust_request_meta["response_time"])

        self._is_reported = True

    def failure(self, exc):
        log.exception(exc)
        self.stats.record(self.locust_request_meta["response_time"])

        self._is_reported = True
