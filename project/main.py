from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from .models import Script, Line, Comment
from . import db
from . import app

from project import backend, mailman

from .forms import Load_Script

import secrets
import markdown



main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
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


@main.route('/load_script')
def load_script_manual():
    url = request.args.get('url')

    status, script_unique_key, secret_key = backend.download_script(url)
    if status == "success":
        return redirect(url_for('main.view_script', unique_key=script_unique_key, secret_key=secret_key))
    if status != "success":
        return status


@main.route('/view_script/<unique_key>/')
@main.route('/view_script/<unique_key>/secret/<secret_key>')
def view_script(unique_key, secret_key = None):
    script_to_display = Script.query.filter_by(unique_key = unique_key).first()

    if script_to_display == None: return "Script not found"

    edit_mode = False
    if secret_key != None:
        if secret_key == script_to_display.secret_key: edit_mode = True

    lines_to_display = Line.query.filter_by(script_id = script_to_display.id).all()

    comments_to_display = []
    for line in lines_to_display:
        if line.comment_count() == 0:
            comments_to_display.append (None)
        if line.comment_count() > 0:
            comment = Comment.query.filter_by(line_unique_key = line.unique_key).first()
            comments_to_display.append (comment.unique_key)

    return render_template('show_script.html',
                           script=script_to_display,
                           lines_to_display=lines_to_display,
                           comments_to_display=comments_to_display,
                           edit_mode=edit_mode,
                           secret_key=secret_key,
                           sharing_link=script_to_display.sharing_link(),
                           private_sharing_link=script_to_display.secret_link())


@main.route('/view_script/<unique_key>/secret/<secret_key>/email_reminder', methods=['POST'])
def email_reminder(unique_key, secret_key):
    script = Script.query.filter_by(unique_key = unique_key).first()

    error_has_occurred = False
    # Verify they know the secret
    if secret_key == None:
        flash ("No secret key provided", "error")
        error_has_occurred = True

    if secret_key != script.secret_key:
        flash ("Not authorised", "error")
        error_has_occurred = True

    email_address_provided = request.values.get('emailaddress')
    if email_address_provided == None or email_address_provided == "":
        flash ("No email address provided", "error")
        error_has_occurred = True

    if error_has_occurred == False:
        email_body = "You asked to be reminded by email that you have provided comments on the script at " + script.url + ".\r\n\r\nYour comment set is known as " + script.unique_key + " and your secret key is " + script.secret_key + "\r\n\r\nThe public url of this comment set for sharing is " + script.sharing_link() + "\r\n\r\nYou can access the private link at " + script.secret_link()
        try:
            mailman.send_email("codecomments@codecomments.dev", email_address_provided, "codecomments.dev: your secret key for " + script.unique_key, email_body)
        except:
            flash ("Error sending email", "error")
            error_has_occurred = True

        if error_has_occurred == False:
            flash ('Email reminder sent', 'success')
            script.associated_email = email_address_provided
            db.session.commit()

    return redirect(url_for('main.view_script', unique_key=unique_key, secret_key=secret_key))


@main.route('/add_comment/<line_key>/secret/<secret_key>', methods=['GET', 'POST'])
def add_comment(line_key, secret_key):

    line = Line.query.filter_by(unique_key=line_key).first()

    if request.method == 'GET':
        return render_template('edit_comment.html', new_comment=True, line=line, can_edit=True, contents="", secret_key=secret_key)

    if request.method == 'POST':
        new_comment = Comment(
            line_unique_key=line_key,
            unique_key="comment_" + secrets.token_urlsafe(25),
            line_number=line.line_number,
            content_comment=request.values.get('comment_contents')
        )

        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for('main.view_script', unique_key=line.script_unique_key(), secret_key=secret_key))


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
    output_content = markdown.markdown(output_content)

    return render_template('view_comment.html', comment_to_display = comment_to_display, output_content = output_content)


@main.route('/stats')
def stats():
    script_count = Script.query.count()
    line_count = Line.query.count()
    comment_count = Comment.query.count()

    return "Scripts :" + str(script_count) + "<br>Lines: " + str(line_count) + "<br>Comments: " + str(comment_count)


@main.route('/flashtest')
def flashtest():
    flash ("This is a test from python!", "error")
    return redirect(url_for('main.view_script', unique_key="radiant-cockle", secret_key="district"))
