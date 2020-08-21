from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for, request
from flask_login import login_required, current_user


class AdminView(ModelView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    def is_accessible(self):
        return False
