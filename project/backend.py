from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Script, Line, Comment
from . import db
from . import app
from random import random, randint, randrange
import secrets
import datetime
import requests
from coolname import generate_slug


def get_raw_url(pretty_url):
    raw_url = pretty_url.replace("github.com", "raw.githubusercontent.com")
    raw_url = raw_url.replace("blob/", "")
    return raw_url


def download_script(url):
    raw_url = get_raw_url(url)

    # Parse the url into the relevant bits
    stuffbefore, url_for_parsing = raw_url.split(".com/")

    source = "github"
    gituser, gitrepo, gitbranch, filename = url_for_parsing.split("/")

    # Create new script record
    unique_name = False
    while unique_name is False:
        script_unique_key = generate_slug(2)
        other_scripts_with_that_name = Script.query.filter_by(unique_key = script_unique_key).count()
        if other_scripts_with_that_name == 0: unique_name = True

    new_script = Script(
        source=source,
        unique_key=script_unique_key,
        url=url,
        gituser=gituser,
        gitrepo=gitrepo,
        gitbranch=gitbranch,
        filename=filename
    )

    # add the new script to the database
    db.session.add(new_script)
    db.session.commit()

    # recall the newly created script so we can get the id
    script = Script.query.filter_by(unique_key = script_unique_key).first()


    # Download the file fro github
    r = requests.get(raw_url)

    line_number = 1
    for line in r.iter_lines():
        new_line = Line(
            script_id = script.id,
            line_number = line_number,
            unique_key = "line_" + secrets.token_urlsafe(30),
            content = line.decode()
        )
        db.session.add(new_line)
        db.session.commit()
        line_number = line_number + 1

    return script_unique_key