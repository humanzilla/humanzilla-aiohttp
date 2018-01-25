import importlib
import inspect

BACKGROUND_TASKS = 'BACKGROUND_TASKS'


def get_background_tasks(app):
    if not BACKGROUND_TASKS in app:
        app[BACKGROUND_TASKS] = []
    return app[BACKGROUND_TASKS]


def append_background_task(app, task_handler):
    tasks = get_background_tasks(app)
    tasks.append(app.loop.create_task(task_handler(app)))


async def start_background_tasks(app):
    tasks_module = importlib.import_module('{{ cookiecutter.project_module }}.tasks')

    assert hasattr(tasks_module, '__all__'), 'Missing __all__ from tasks.py'

    for name in tasks_module.__all__:
        task_handler = getattr(tasks_module, name)
        assert inspect.iscoroutinefunction(task_handler), 'Task handler must be a couroutine'
        append_background_task(app, task_handler)


async def cleanup_background_tasks(app):
    for each_task in get_background_tasks(app):
        each_task.cancel()


def setup(app):
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
