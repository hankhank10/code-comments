from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Script, Line, Comment
from . import db
from . import app
import secrets
import requests
from coolname import generate_slug
from datetime import datetime

from random_words import RandomWords
rw = RandomWords()


def get_raw_url(url_source, pretty_url):
    if url_source == "github":
        raw_url = pretty_url.replace("github.com", "raw.githubusercontent.com")
        raw_url = raw_url.replace("blob/", "")

    if url_source == "pastebin":
        raw_url = pretty_url.replace("pastebin.com/", "pastebin.com/raw/")

    if url_source == "hastebin":
        raw_url = pretty_url.replace("hastebin.com/", "hastebin.com/raw/")

    return raw_url


def download_script(url):

    # Work out the source
    url_source = "unknown"
    if "github" in url: url_source = "github"
    if "pastebin.com" in url: url_source = "pastebin"
    if "hastebin.com" in url: url_source = "hastebin"
    if url_source == "unknown":
        return "The source could not be identified"

    print (url_source)

    if url_source == "github":
        # Check if it's a raw URL or a pretty URL
        url_type = "unknown"
        if "github.com" in url: url_type = "pretty"
        if "raw.githubusercontent.com" in url: url_type = "raw"

        if url_type == "unknown": return "That github url was not recognised", None, None
        if url_type == "pretty": raw_url = get_raw_url("github", url)
        if url_type == "raw": raw_url = url

        # Parse the url into the relevant bits
        stuffbefore, url_for_parsing = raw_url.split(".com/")
        source = url_source
        try:
            split_output = url_for_parsing.split("/", 3)
            gituser = split_output[0]
            gitrepo = split_output[1]
            gitbranch = split_output[2]
            filename = split_output[3]
        except:
            return "Could not parse that github url. Please provide a full URL link from github to a file (not a repo)", None, None

    if url_source == "pastebin":
        # Check if it's a raw URL or a pretty URL
        url_type = "pretty"
        if "pastebin.com/raw/" in url: url_type = "raw"

        if url_type == "pretty": raw_url = get_raw_url("pastebin", url)
        if url_type == "raw": raw_url = url

        # Parse the url into the relevant bits
        source = url_source
        gituser = ""
        gitrepo = ""
        gitbranch = ""
        filename = raw_url[-8:]

    if url_source == "hastebin":
        # Strip off any .pl
        url = url.replace(".pl", "")

        # Check if it's a raw URL or a pretty URL
        url_type = "pretty"
        if "hastebin.com/raw/" in url: url_type = "raw"

        if url_type == "pretty": raw_url = get_raw_url("hastebin", url)
        if url_type == "raw": raw_url = url

        # Parse the url into the relevant bits
        source = url_source
        gituser = ""
        gitrepo = ""
        gitbranch = ""
        filename = raw_url[-10:]

    # Download the file
    try:
        r = requests.get(raw_url)
    except:
        return "An error occurred when trying to download that file - check the url maybe?", None, None

    if r.status_code != 200:
        return "The server returned invalid status code when trying to download the file", None, None

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
        filename=filename,
        timestamp=datetime.utcnow()
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


def duplicate_script(unique_key):
    script_to_duplicate = Script.query.filter_by(unique_key=unique_key).first()
    lines_to_duplicate = Line.query.filter_by(script_id=script_to_duplicate.id).order_by(Line.line_number).all()

    # Create new script record
    unique_name = False
    while unique_name is False:
        script_unique_key = generate_slug(2)
        other_scripts_with_that_name = Script.query.filter_by(unique_key = script_unique_key).count()
        if other_scripts_with_that_name == 0: unique_name = True

    secret_key = rw.random_word()

    new_script = Script(
        source=script_to_duplicate.source,
        unique_key=script_unique_key,
        secret_key=secret_key,
        url=script_to_duplicate.url,
        gituser=script_to_duplicate.gituser,
        gitrepo=script_to_duplicate.gitrepo,
        gitbranch=script_to_duplicate.gitbranch,
        filename=script_to_duplicate.filename,
        timestamp=datetime.utcnow()
    )

    # add the new script to the database
    db.session.add(new_script)
    db.session.commit()

    # recall the newly created script so we can get the id
    script = Script.query.filter_by(unique_key=script_unique_key).first_or_404()

    for line in lines_to_duplicate:
        new_line = Line(
            script_id=script.id,
            line_number=line.line_number,
            unique_key="line_" + secrets.token_urlsafe(30),
            content=line.content
        )
        db.session.add(new_line)
        db.session.commit()

    return "success", script_unique_key, secret_key



