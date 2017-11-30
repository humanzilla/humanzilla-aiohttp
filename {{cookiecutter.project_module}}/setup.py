import os
from setuptools import setup, find_packages


project = '{{ cookiecutter.project_module }}'
assets = 'src/{{ cookiecutter.project_module }}/static'.format(project=project)


def static_files(path, prefix):
    for root, dir, files in os.walk(path):
        paths = []
        for item in files:
            paths.append(os.path.join(root, item))
        yield (root.replace(path, prefix), paths)


data_files = [item for item in static_files(assets, '')]


setup(
    name="{{ cookiecutter.project_module }}",
    version='1.0',
    url="{{ cookiecutter.project_url }}",
    author='{{ cookiecutter.author }}',
    author_email='{{ cookiecutter.author_email }}',
    description='{{ cookiecutter.description }}',
    zip_safe=False,
    include_package_data=True,
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['tests']),
    data_files=data_files
)
