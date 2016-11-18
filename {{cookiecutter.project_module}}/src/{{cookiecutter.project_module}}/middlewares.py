from aiohttp import web

from .handlers.defaults import handle_404, handle_500


async def error_middleware(app, handler):
    overrides = {
        404: handle_404,
    }
    if not app['debug']:
        overrides['500'] = handle_500()

    async def middleware_handler(request):
        try:
            response = await handler(request)
            override = overrides.get(response.status)
            if override is None:
                return response
            else:
                return await override(request, response)
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override is None:
                raise
            else:
                return await override(request, ex)

    return middleware_handler
