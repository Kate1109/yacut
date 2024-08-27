from re import match
from http import HTTPStatus

from flask import jsonify, request

from . import app, db
from .models import URLMap
from .views import get_unique_short_id
from .error_handlers import InvalidAPIUsage


MIN_LENGTH = 6
MAX_LENGTH = 16


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    if not data.get('custom_id'):
        data['custom_id'] = get_unique_short_id()
    if len(data['custom_id']) > MAX_LENGTH:
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки',
            HTTPStatus.BAD_REQUEST
        )
    elif not match(r'^[A-Za-z0-9_]+$', data['custom_id']):
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
    elif URLMap.query.filter_by(short=data['custom_id']).first():
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )
    new_url = URLMap()
    new_url.from_dict(data)
    db.session.add(new_url)
    db.session.commit()
    return jsonify(new_url.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    url = URLMap.query.filter_by(short=short_id).first()
    if url is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify(url=url.original), HTTPStatus.OK
