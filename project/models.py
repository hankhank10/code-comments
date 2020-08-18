from . import db
from sqlalchemy.ext import hybrid


class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_key = db.Column(db.String)
    secret_key = db.Column(db.String)
    url = db.Column(db.String)
    source = db.Column(db.String)
    gituser = db.Column(db.String)
    gitrepo = db.Column(db.String)
    gitbranch = db.Column(db.String)
    filename = db.Column(db.String)
    associated_email = db.Column(db.String)

    def sharing_link(self):
        sharing_link = "https://codecomments.dev/view_script/" + self.unique_key  # use for deployment
        # sharing_link = "http://0.0.0.0:1234/view_script/"+ self.unique_key   #use for local testing
        return sharing_link

    def secret_link(self):
        return self.sharing_link() + "/secret/" + self.secret_key



class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_id = db.Column(db.Integer)
    line_number = db.Column(db.Integer)
    unique_key = db.Column(db.String)
    content = db.Column(db.String)

    def script_unique_key(self):
        script = Script.query.filter_by(id = self.script_id).first()
        return script.unique_key

    def script_secret_key(self):
        script = Script.query.filter_by(id = self.script_id).first()
        return script.secret_key

    def comment_count(self):
        comments_count = Comment.query.filter_by(line_unique_key = self.unique_key).count()
        return comments_count

    def has_comment(self):
        if self.comment_count() == 0: return False
        if self.comment_count() > 0: return True

    def comment_unique_key(self):
        comment = Comment.query.filter_by(line_unique_key = self.unique_key).first()
        return comment.unique_key


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_id = db.Column(db.Integer)  #delete
    line_number = db.Column(db.Integer)
    line_unique_key = db.Column(db.String)
    unique_key = db.Column(db.String)
    written_by = db.Column(db.String)
    comment_type = db.Column(db.String)
    content_comment = db.Column(db.String)
    content_code = db.Column(db.String)

    def script_unique_key(self):
        line = Line.query.filter_by(unique_key = self.line_unique_key).first()
        script_unique_key = line.script_unique_key()
        return script_unique_key

    def script_secret_key(self):
        line = Line.query.filter_by(unique_key = self.line_unique_key).first()
        script_secret_key = line.script_secret_key()
        return script_secret_key


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String)
    login_key = db.Column(db.String)