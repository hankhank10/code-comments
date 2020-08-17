from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Script, Line, Comment
from . import db
from . import app
import secrets
import requests
from coolname import generate_slug

from random_words import RandomWords
rw = RandomWords()


def get_raw_url(pretty_url):
    raw_url = pretty_url.replace("github.com", "raw.githubusercontent.com")
    raw_url = raw_url.replace("blob/", "")
    return raw_url


def download_script(url):

    # Check if it's a raw URL or a pretty URL
    url_type = "unknown"
    if "github.com" in url: url_type = "pretty"
    if "raw.githubusercontent.com" in url: url_type = "raw"

    if url_type == "unknown": return "Error: unrecognised github url", None, None
    if url_type == "pretty": raw_url = get_raw_url(url)
    if url_type == "raw": raw_url = url

    # Parse the url into the relevant bits
    stuffbefore, url_for_parsing = raw_url.split(".com/")
    source = "github"
    try:
        split_output = url_for_parsing.split("/", 3)
        gituser = split_output[0]
        gitrepo = split_output[1]
        gitbranch = split_output[2]
        filename = split_output[3]
    except:
        return "Error: could not parse url. Please provide a full URL link from github to a script (not a repo)", None, None

    # Download the file from github
    try:
        r = requests.get(raw_url)
    except:
        return "Error: error generated when trying to download file", None, None

    if r.status_code != 200:
        return "Error: server returned invalud status code", None, None

    # Create new script record
    unique_name = False
    while unique_name is False:
        script_unique_key = generate_slug(2)
        other_scripts_with_that_name = Script.query.filter_by(unique_key = script_unique_key).count()
        if other_scripts_with_that_name == 0: unique_name = True

    secret_key = rw.random_word()

    new_script = Script(
        source=source,
        unique_key=script_unique_key,
        secret_key=secret_key,
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

    return "success", script_unique_key, secret_key