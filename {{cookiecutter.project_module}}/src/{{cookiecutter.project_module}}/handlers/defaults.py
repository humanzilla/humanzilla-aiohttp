import json
import aiohttp_jinja2
from aiohttp import web
from ..shortcuts import render


async def handle_403(request, response):
    return render(request, '403.html')


async def handle_404(request, response):
    return render(request, '404.html')


async def handle_500(request, response):
    return render(request, '500.html')
