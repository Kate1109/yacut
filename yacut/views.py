import random
import string

from flask import flash, redirect, render_template

from . import app, db
from .forms import URLMapForm
from .models import URLMap

MIN_LENGTH = 6


def get_unique_short_id():
    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    short_id = ''.join(random.choice(symbols) for i in range(MIN_LENGTH))
    if URLMap.query.filter_by(short=short_id).first():
        get_unique_short_id()
    return short_id


@app.route('/', methods=['POST', 'GET'])
def index_view():
    form = URLMapForm()
    custom_id = form.custom_id.data
    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    elif not custom_id:
        custom_id = get_unique_short_id()
    elif URLMap.query.filter_by(short=custom_id).first():
        flash('Предложенный вариант короткой ссылки уже существует.')
        form.custom_id.data = None
        return render_template('index.html', form=form)
    new_url = URLMap(
        original=form.original_link.data,
        short=custom_id
    )
    db.session.add(new_url)
    db.session.commit()
    return render_template('index.html', url=new_url, form=form)


@app.route('/<short_id>')
def redirect_view(short_id):
    url = URLMap.query.filter_by(short=short_id).first_or_404()
    if url is not None:
        original_link = url.original
        return redirect(original_link)