# -*- encoding: utf-8 -*-


from flask   import render_template, request
from jinja2  import TemplateNotFound

from apps import app
import requests
import yaml


@app.route('/', defaults={'path': 'pipelines.html'})
@app.route('/pipelines', defaults={'path': 'pipelines.html'})
@app.route('/<path>')
def index(path):

    try:
        pipelines = []
        for project in get_config():
            for pipeline_id in get_pipeline_ids(project['project_id'], project['access-token']):
                pipelines.append(get_pipelines(project['project_id'], pipeline_id, project['access-token']))

        return render_template( 'home/' + path, pipelines=pipelines)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404


def client(path, token):
    url = 'https://gitlab.com/api/v4/{0}'.format(path)
    r = requests.get(url, headers={'PRIVATE-TOKEN': token})
    return r


def get_config():
    with open("piplines_config.yml") as f:
        try:
            content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise FileNotFoundError(e)

    return content['gitlabs']


def get_project_name(project_id, token):
    r = client('projects/{0}'.format(project_id), token)
    json = r.json()
    name = [json['name']]
    return name[0]


def get_pipeline_ids(project_id, token):
    r = client('projects/{0}/pipeline_schedules/'.format(project_id), token)
    json = r.json()
    ids = []
    for id in json:
        ids.append(id['id'])
    return ids


def get_pipelines(project_id, pipeline_id, token):
    r = client('projects/{0}/pipeline_schedules/{1}'.format(project_id, pipeline_id), token)
    pipeline_json = r.json()
    pipelines = {"project": get_project_name(project_id, token),
                 "env": pipeline_json['description'],
                 "status": pipeline_json['last_pipeline']['status'],
                 "ref": pipeline_json['last_pipeline']['ref'],
                 "web_url": pipeline_json['last_pipeline']['web_url']}
    return pipelines
