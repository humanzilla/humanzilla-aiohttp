from aiohttp_jinja2 import render_template

__all__ = ['handler_landing']


async def handler_landing(request):
    return render_template('index.html', request, None)
