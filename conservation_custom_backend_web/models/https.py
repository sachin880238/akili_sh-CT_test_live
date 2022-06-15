from odoo import http
import logging
import werkzeug.exceptions
import odoo
from odoo.tools import ustr

_logger = logging.getLogger(__name__)



class jsonhttp(http.JsonRequest):

    def _handle_exception(self, exception):
        """Called within an except block to allow converting exceptions
           to arbitrary responses. Anything returned (except None) will
           be used as response."""
        try:
            return super(jsonhttp, self)._handle_exception(exception)
        except Exception:
            if not isinstance(exception, (odoo.exceptions.Warning, http.SessionExpiredException,
                                          odoo.exceptions.except_orm, werkzeug.exceptions.NotFound)):
                _logger.exception("Exception during JSON request handling.")
            error = {
                    'code': 200,
                    'message': "Warning",
                    'data': http.serialize_exception(exception)
            }
            if isinstance(exception, werkzeug.exceptions.NotFound):
                error['http_status'] = 404
                error['code'] = 404
                error['message'] = "404: Not Found"
            if isinstance(exception, http.AuthenticationError):
                error['code'] = 100
                error['message'] = "Odoo Session Invalid"
            if isinstance(exception, http.SessionExpiredException):
                error['code'] = 100
                error['message'] = "Odoo Session Expired"
            return self._json_response(error=error)

http.JsonRequest._handle_exception = jsonhttp._handle_exception