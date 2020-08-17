from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from .models import Script, Line, Comment
from . import db
from . import app
from random import random, randint, randrange

from project import backend

from .forms import Load_Script

import secrets
import markdown

from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def load_script():
    form = Load_Script()

    # The POST method
    if form.validate_on_submit():
        url = backend.get_raw_url(form.github_url.data)

        status, script_unique_key, secret_key = backend.download_script(url)
        if status == "success":
            return redirect(url_for('main.view_script', unique_key=script_unique_key, secret_key=secret_key))
        if status != "success":
            return status

    # The GET method
    return render_template('index.html', form=form)


@main.route('/view_script/<unique_key>/')
@main.route('/view_script/<unique_key>/secret/<secret_key>')
def view_script(unique_key, secret_key = None):
    script_to_display = Script.query.filter_by(unique_key = unique_key).first()

    print (secret_key)

    edit_mode = False
    if secret_key != None:
        if secret_key == script_to_display.secret_key: edit_mode = True

    print (edit_mode)

    lines_to_display = Line.query.filter_by(script_id = script_to_display.id).all()

    comments_to_display = []
    for line in lines_to_display:
        if line.comment_count() == 0:
            comments_to_display.append (None)
        if line.comment_count() > 0:
            comment = Comment.query.filter_by(line_unique_key = line.unique_key).first()
            comments_to_display.append (comment.unique_key)

    sharing_link = "http://0.0.0.0:1234/view_script/" + unique_key
    if secret_key == None: private_sharing_link = sharing_link
    if secret_key != None: private_sharing_link = sharing_link + "/secret/" + secret_key

    return render_template('show_script.html',
                           script=script_to_display,
                           lines_to_display = lines_to_display,
                           comments_to_display = comments_to_display,
                           edit_mode = edit_mode,
                           secret_key = secret_key,
                           sharing_link = sharing_link,
                           private_sharing_link=private_sharing_link)


@main.route('/add_comment/<line_key>', methods=['GET', 'POST'])
def add_comment(line_key):

    line = Line.query.filter_by(unique_key=line_key).first()

    if request.method == 'GET':
        return render_template('edit_comment.html', new_comment=True, line=line, can_edit=True, contents="")

    if request.method == 'POST':
        new_comment = Comment(
            line_unique_key = line_key,
            unique_key = "comment_" + secrets.token_urlsafe(25),
            line_number = line.line_number,
            content_comment = request.values.get('comment_contents')
        )

        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for('main.view_script', unique_key=line.script_unique_key()))


@main.route('/edit_comment/<comment_key>/secret/<secret_key>', methods=['GET', 'POST'])
def edit_comment(comment_key, secret_key):
    comment_to_edit = Comment.query.filter_by(unique_key = comment_key).first()

    if comment_to_edit.script_secret_key() != secret_key:
        return "Invalid secret key"

    if request.method == 'GET':
        return render_template('edit_comment.html', new_comment=False, line=comment_to_edit.line_number, can_edit=True, contents=comment_to_edit.content_comment, comment_key = comment_key, secret_key=secret_key)

    if request.method == 'POST':
        comment_to_edit.content_comment = request.values.get('comment_contents')
        db.session.commit()
        return redirect(url_for('main.view_script', unique_key=comment_to_edit.script_unique_key(), secret_key=secret_key))

@main.route('/view_comment/<comment_key>')
def view_comment(comment_key):

    comment_to_display = Comment.query.filter_by(unique_key = comment_key).first()

    output_content = comment_to_display.content_comment
    print (output_content)
    output_content = markdown.markdown(output_content)
    print (output_content)

    return render_template('view_comment.html', comment_to_display = comment_to_display, output_content = output_content)