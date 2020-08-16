from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from .models import Script, Line, Comment
from . import db
from . import app
from random import random, randint, randrange

from project import backend

from .forms import Load_Script

import secrets

from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return "Index"


@main.route('/load_script', methods=['GET', 'POST'])
def load_script():
    form = Load_Script()

    if form.validate_on_submit():
        url = backend.get_raw_url(form.github_url.data)
        script_unique_key = backend.download_script(url)
        return script_unique_key

    return render_template('load_script.html', form=form)


@main.route('/view_script/<unique_key>')
def view_script(unique_key):
    script_to_display = Script.query.filter_by(unique_key = unique_key).first()
    lines_to_display = Line.query.filter_by(script_id = script_to_display.id).all()

    comments_to_display = []
    for line in lines_to_display:
        if line.comment_count() == 0:
            comments_to_display.append (None)
        if line.comment_count() > 0:
            comment = Comment.query.filter_by(line_unique_key = line.unique_key).first()
            comments_to_display.append (comment.unique_key)

    print (comments_to_display)

    return render_template('show_script.html', script=script_to_display, lines_to_display = lines_to_display, comments_to_display = comments_to_display)


@main.route('/add_comment/<line_key>', methods=['GET', 'POST'])
def add_comment(line_key):

    line = Line.query.filter_by(unique_key=line_key).first()

    if request.method == 'GET':
        return render_template('edit_comment.html', new_comment=True, line=line, can_edit=True, contents="")

    if request.method == 'POST':
        new_comment = Comment(
            line_unique_key = line_key,
            unique_key = "comment_" + secrets.token_urlsafe(25),
            content_comment = request.values.get('new_comment')
        )

        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for('main.view_script', unique_key=line.script_unique_key()))

@main.route('/view_comment/<comment_key>', methods=['GET', 'POST'])
def view_comment(comment_key):
    comment_to_display = Comment.query.filter_by(unique_key = comment_key).first()

    return comment_key