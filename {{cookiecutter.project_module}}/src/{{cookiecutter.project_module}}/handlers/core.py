from .defaults import json_response


async def index(request):
    return json_response(data={
        'project': request.app.config.get('PROJECT_NAME')
    })
