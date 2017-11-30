import time

import aiohttp
from aiohttp import web
from ..shortcuts import render

__all__ = ['user_detail', 'user_edit']


async def user_detail(request):
    return render(request, 'users/detail.html')


async def user_edit(request):
    return render(request, 'users/edit.html')