from logging import getLogger

from aiohttp import web

logger = getLogger('aiohttp.server')

client_error = """<!DOCTYPE html>
<html lang=en>
<meta charset=utf-8>
<meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width">
<title>{status} {reason}!</title>
<style>
*{{margin:0;padding:0}}html,code{{font:15px/22px arial,sans-serif}}
html{{background:#fff;color:#222;padding:15px}}
body{{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}}
p{{margin:11px 0 22px;overflow:hidden}}ins{{color:#777;text-decoration:none}}
</style>
<p><b>{status}.</b> <ins>{reason}</ins>
{body}
""".format

not_found_text = client_error(status="404", reason="Not Found", body="""
<p>Page not found
""")

internal_error_text = client_error(status="500", reason="Internal Error", body="""
<p>Internal Error
<p>There was an error in our application.
""")


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status == 404:
            return web.HTTPNotFound(text=not_found_text, content_type='text/html')
    except web.HTTPNotFound as ex:
        return web.HTTPNotFound(text=not_found_text, content_type='text/html')
    except web.HTTPClientError as ex:
        return web.Response(text=client_error(status=ex.status, reason=ex.reason, body=''),
                            reason=ex.reason,
                            status=ex.status,
                            content_type='text/html')
    except Exception as ex:
        logger.exception(repr(ex))
        return web.HTTPInternalServerError(text=internal_error_text, content_type='text/html')
    else:
        return response


def setup(app: web.Application):
    if not app.debug:
        app.middlewares.append(error_middleware)
