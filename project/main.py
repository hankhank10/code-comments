from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from .models import Script, Line, Comment, User
from . import db
from . import app

from project import backend, mailman, mysecretstuff

from .forms import Load_Script

import secrets
import markdown

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = Load_Script()

    # The POST method
    if form.validate_on_submit():
        url = form.github_url.data

        status, script_unique_key, secret_key = backend.download_script(url)
        if status == "success":
            return redirect(url_for('main.view_script', unique_key=script_unique_key, secret_key=secret_key))
        if status != "success":
            flash(status, "error")
            return redirect(url_for('main.index'))

    # The GET method
    return render_template('index.html', form=form)


@main.route('/script/load/')
def load_script_manual():
    url = request.args.get('url')

    status, script_unique_key, secret_key = backend.download_script(url)
    if status == "success":
        return redirect(url_for('main.view_script', unique_key=script_unique_key, secret_key=secret_key))
    if status != "success":
        flash(status, "error")
        return redirect(url_for('main.index'))


@main.route('/script/view/<unique_key>/')
@main.route('/script/view/<unique_key>/secret/<secret_key>')
def view_script(unique_key, secret_key=None):
    script_to_display = Script.query.filter_by(unique_key=unique_key).first()

    if script_to_display is None:
        flash("Comment set not found", "error")
        return redirect(url_for('main.index'))

    edit_mode = False
    if secret_key is not None:
        if secret_key == script_to_display.secret_key: edit_mode = True

    lines_to_display = Line.query.filter_by(script_id=script_to_display.id).all()

    comments_to_display = []
    for line in lines_to_display:
        if line.comment_count() == 0:
            comments_to_display.append(None)
        if line.comment_count() > 0:
            comment = Comment.query.filter_by(line_unique_key=line.unique_key).first()
            comments_to_display.append(comment.unique_key)

    return render_template('show_script.html',
                           script=script_to_display,
                           lines_to_display=lines_to_display,
                           comments_to_display=comments_to_display,
                           edit_mode=edit_mode,
                           secret_key=secret_key,
                           sharing_link=script_to_display.sharing_link(),
                           private_sharing_link=script_to_display.secret_link())


@main.route('/script/duplicate/<unique_key>/')
def duplicate_script(unique_key):
    status, script_unique_key, secret_key = backend.duplicate_script(unique_key)
    if status == "success":
        return redirect(url_for('main.view_script', unique_key=script_unique_key, secret_key=secret_key))
    if status != "success":
        flash(status, "Error duplicating script")
        return redirect(url_for('main.index'))


@main.route('/script/view/<unique_key>/secret/<secret_key>/email_reminder', methods=['POST'])
def email_reminder(unique_key, secret_key):
    script = Script.query.filter_by(unique_key=unique_key).first()

    error_has_occurred = False
    # Verify they know the secret
    if secret_key is None:
        flash("No secret key provided", "error")
        error_has_occurred = True

    if secret_key != script.secret_key:
        flash("Not authorised", "error")
        error_has_occurred = True

    email_address_provided = request.values.get('emailaddress')
    if email_address_provided is None or email_address_provided == "":
        flash("No email address provided", "error")
        error_has_occurred = True

    if not error_has_occurred:
        email_body = "You asked to be reminded by email that you have provided comments on the script at " + script.url + ".\r\n\r\nYour comment set is known as " + script.unique_key + " and your secret key is " + script.secret_key + "\r\n\r\nThe public url of this comment set for sharing is " + script.sharing_link() + "\r\n\r\nYou can access the private link at " + script.secret_link()
        try:
            mailman.send_email("codecomments@codecomments.dev", email_address_provided,
                               "codecomments.dev: your secret key for " + script.unique_key, email_body)
        except:
            flash("Error sending email", "error")
            error_has_occurred = True

        if not error_has_occurred:
            # Create the new user record, if it doesn't already exist
            existing_user_count = User.query.filter_by(email_address=email_address_provided).count()
            if existing_user_count == 0:
                new_user = User(
                    email_address=email_address_provided,
                    login_key=secrets.token_urlsafe(15),
                )
                db.session.add(new_user)

            # Associate the script with the user
            script.associated_email = email_address_provided
            db.session.commit()

            flash('Email reminder sent', 'success')

    return redirect(url_for('main.view_script', unique_key=unique_key, secret_key=secret_key))


@main.route('/comment/add/<line_key>/secret/<secret_key>', methods=['GET', 'POST'])
def add_comment(line_key, secret_key):
    line = Line.query.filter_by(unique_key=line_key).first()

    if request.method == 'GET':
        return render_template('edit_comment.html', new_comment=True, line=line, can_edit=True, contents="",
                               secret_key=secret_key)

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


@main.route('/comment/edit/<comment_key>/secret/<secret_key>', methods=['GET', 'POST'])
def edit_comment(comment_key, secret_key):
    comment_to_edit = Comment.query.filter_by(unique_key=comment_key).first()

    if comment_to_edit.script_secret_key() != secret_key:
        return "Invalid secret key"

    if request.method == 'GET':
        return render_template('edit_comment.html', new_comment=False, line=comment_to_edit.line_number, can_edit=True,
                               contents=comment_to_edit.content_comment, comment_key=comment_key, secret_key=secret_key)

    if request.method == 'POST':
        comment_to_edit.content_comment = request.values.get('comment_contents')
        db.session.commit()
        return redirect(
            url_for('main.view_script', unique_key=comment_to_edit.script_unique_key(), secret_key=secret_key))


@main.route('/comment/view/<comment_key>')
def view_comment(comment_key):
    comment_to_display = Comment.query.filter_by(unique_key=comment_key).first()

    output_content = comment_to_display.content_comment
    output_content = markdown.markdown(output_content)

    return render_template('view_comment.html', comment_to_display=comment_to_display, output_content=output_content)


@main.route('/user/reminder')
def email_reminder_of_login_key():

    email_address = request.args.get('email_address')

    error_has_occurred = False

    if email_address is None:
        flash("No email address provided", "error")
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email_address=email_address).first()

    if user is None:
        flash("Email address not found - have you previously provided comments?", "error")
        return redirect(url_for('main.index'))

    # update the user key
    new_user_key = "userkey_" + secrets.token_urlsafe(10)
    user.login_key = new_user_key
    db.session.commit()

    # send the email
    email_body = "You asked for a link to access your comments on codecomments.dev. Here it is:\r\n\r\n " + mysecretstuff.website_url + "/user/view/" + email_address + "/secret/" + new_user_key
    try:
        mailman.send_email("codecomments@codecomments.dev", email_address,
                           "codecomments.dev: your user login link", email_body)
    except:
        flash("Error sending email", "error")
        error_has_occurred = True

    if not error_has_occurred:
        flash('Login link sent', 'success')

    return redirect(url_for('main.index'))


@main.route('/user/view/<email_address>/secret/<secret_key>')
def view_user(email_address, secret_key):

    if email_address is None or secret_key is None:
        flash("No credentials provider", "error")
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email_address=email_address).first_or_404()

    if user.login_key != secret_key:
        flash("Invalid credentials", "error")
        return redirect(url_for('main.index'))

    scripts = Script.query.filter_by(associated_email=email_address).all()

    return render_template('view_user.html', user=user, scripts=scripts)


@main.route('/stats')
def stats():
    script_count = Script.query.count()
    line_count = Line.query.count()
    comment_count = Comment.query.count()

    return "Scripts :" + str(script_count) + "<br>Lines: " + str(line_count) + "<br>Comments: " + str(comment_count)


@main.route('/flashtest')
def flashtest():
    flash("This is a test from python!", "error")
    return redirect(url_for('main.view_script', unique_key="radiant-cockle", secret_key="district"))


@main.route('/happybirthday' + mysecretstuff.secret_tutorial_url)
def happy_birthday():
    url = "https://github.com/hankhank10/happy-birthday/blob/master/happybirthday.py"
    unique_key_to_create = "uncovered-ammonite"
    secret_key_to_create = mysecretstuff.happy_birthday_secret_key

    script_already_there = Script.query.filter_by(unique_key=unique_key_to_create).first()
    if script_already_there is not None:
        print("Found a script already there so deleting")
        lines_already_there = Line.query.filter_by(script_id=script_already_there.id)

        for line in lines_already_there:
            db.session.delete(line)

        db.session.delete(script_already_there)
        db.session.commit()

    status, script_unique_key, secret_key = backend.download_script(url)

    if status != "success": return "Error downloading script"

    script = Script.query.filter_by(unique_key=script_unique_key).first()
    script.unique_key = unique_key_to_create
    script.secret_key = secret_key_to_create
    db.session.commit()

    return redirect(url_for('main.view_script', unique_key=unique_key_to_create, secret_key=secret_key_to_create))
