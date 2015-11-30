#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'TBBack'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import Page, APIValueError, APIResourceNotFoundError

from models import User, Project, Chart, next_id
from config import configs

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

#用户管理员权限认证
def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()
#获取页码
def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p
#cookie操作函数
def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

#文本转换为HTML
def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

#首页路由
@get('/')
def index(request):
    if request.__user__ is None:
        return {
            '__template__': 'home_without_signin.html'
        }
    else:
        return {
            '__template__': 'home_with_signin.html'
        }

#注册页路由
@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }
#用户注册API
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
@post('/api/users')
def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), admin = True,email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

#登录页路由
@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }
#登录鉴权API
@post('/api/authenticate')
def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = yield from User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

#退出页处理函数
@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

#工程创建页路由
@get('/project/create')
def create_project(request):
    project = Project(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, title='', summary='', status=False)
    yield from project.save()
    return {
        '__template__': 'project_edit.html',
        'id': project.id,
        'action': '/api/project/save/'
    }

#工程编辑页路由
@get('/project/edit/{id}')
def edit_project(id):
    return {
        '__template__': 'project_edit.html',
        'id': id,
        'action': '/api/project/save/'
    }

#工程保存API
@post('/api/project/save/{id}')
def api_save_project(request, *, id, title, summary):
    if not title or not title.strip():
        raise APIValueError('title', 'title cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    project = yield from Project.find(id)
    project.status = True
    project.title = title
    project.summary =summary
    yield from project.update()
    return project

#日志管理页路由
@get('/projects/manage')
def manage_projects(*, page='1'):
    return {
        '__template__': 'projects_manage.html',
        'page_index': get_page_index(page)
    }
#工程列表获取API
@get('/api/projects')
def api_projects(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Project.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, projects=())
    projects = yield from Project.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, projects=projects)

#工程获取API
@get('/api/project/{id}')
def api_get_project(*, id):
    project = yield from Project.find(id)
    charts = yield from Chart.findAll('project_id=?', [id], orderBy='created_at desc')
    for chart in charts:
        chart.option = json.loads(chart.option)
    return dict(project=project, charts=charts)

#工程删除API
@post('/api/project/delete/{id}')
def api_delete_project(request, *, id):
    check_admin(request)
    project = yield from Project.find(id)
    yield from project.remove()
    return dict(id=id)

#工程浏览页路由
@get('/project/view/{id}')
def view_project(id):
    return {
        '__template__': 'project_view.html',
        'id': id,
        'action' : 'api/project/'
    }

#图表创建页路由
@get('/{id}/chart/create/{chartType}')
def create_chart(chartType, id):
    if chartType == "bar":
        return {
            '__template__': 'chart_edit/bar_edit.html',
            'project_id': id,
            'chart_id': '',
            'action': '/api/chart/create'
            }
#图表创建API
@post('/api/chart/create')
def api_create_chart(request , *, type, description, project_id, option):
    Option = json.dumps(option, ensure_ascii=False).encode('utf-8')
    chart = Chart(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, project_id=project_id.strip(), type=type.strip(), description=description.strip(), status=False, option = Option)
    yield from chart.save()
    chart.option = markdown2.markdown(chart.option)
    return chart

#图表修改页路由
@get('/chart/edit/{chartType}/{id}')
def edit_chart(chartType, id):
    if chartType == "bar":
        return {
            '__template__': 'chart_edit/bar_edit.html',
            'project_id': '',
            'chart_id': id,
            'action': '/api/chart/save/'
            }
#图表获取API
@get('/api/chart/{id}')
def api_get_chart(*,id):
    chart = yield from Chart.find(id)
    chart.option = json.loads(chart.option)
    return chart
#图表保存API
@post('/api/chart/save/{id}')
def api_save_chart(request , *, type, description, id, option):
    chart = yield from Chart.find(id)
    chart.status = True
    chart.option = json.dumps(option, ensure_ascii=False).encode('utf-8')
    chart.description = description
    yield from chart.update()
    chart.option = markdown2.markdown(chart.option)
    return chart

#图表删除API
@post('/api/chart/delete/{id}')
def api_delete_chart(request, *, id):
    check_admin(request)
    chart = yield from Chart.find(id)
    yield from chart.remove()
    return dict(id=id)