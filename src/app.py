import settings

from flask import Flask
app = Flask(__name__)

from flask import url_for, redirect, make_response, render_template, abort, request, flash

from email_messages import send_message

# --views
@app.route('/')
def main():
    return render_template("construction.html")

@app.route('/bounties', methods=['GET', 'POST'])
def bounties():
    form = BountyForm(request.form)
    if request.method == 'POST' and form.validate():
        b = Bounty(
          key_name=form.hash.data,
          type=form.type.data,
          hash=form.hash.data,
          email=form.email.data,
          bounty=form.bounty.data,
        )
        b.put()
        send_message(b.email, "bounty_submitted", bounty=b)
        return redirect(url_for('bounties'))
   
    bounties = Bounty.all().order('-ctime').fetch(1000)
    
    return render_template('bounties.html', form=form, bounties=bounties)

@app.route('/bounty/<key_name>', methods=['GET', 'POST'])
def bounty(key_name):
    b = Bounty.get_by_key_name(key_name)
    form = SolutionForm(request.form)
    form.bounty = b
    if request.method == 'POST' and form.validate():        
        b.solved = True
        b.solution = form.text.data
        b.put()
        send_message(b.email, "bounty_solved", bounty=b)
        return redirect(url_for('bounties'))
    
    return render_template('bounty.html', form=form, bounty=b)
    

# --models
from google.appengine.ext import db


class TimeMixin(db.Model):
    ctime = db.DateTimeProperty(auto_now_add=True)
    mtime = db.DateTimeProperty(auto_now=True)

class Bounty(TimeMixin, db.Model):
    type = db.StringProperty()
    hash = db.StringProperty()
    email = db.StringProperty()
    bounty = db.FloatProperty()
    address = db.StringProperty()
    
    solved = db.BooleanProperty(default=False)
    solution = db.StringProperty()

# --forms
from wtforms import Form, TextField, SelectField, FloatField, validators

class BountyForm(Form):
    type = SelectField(u'Hash type', choices=[('md5', 'MD5'), ('sha1', 'SHA1')])
    hash = TextField(u'Hash data', [validators.Length(min=1, max=1000)])
    email = TextField(u'Email Address', [validators.Length(min=6, max=35)])
    bounty = FloatField(u'Bounty (BTC)')


class SolutionValidator(object):
    def __call__(self, form, field):
        b = form.bounty
        if b.type == 'md5':
            import md5
            if md5.md5(field.data).hexdigest() != b.hash:
                raise validators.ValidationError(u'Bad solution.')
        elif b.type == 'sha1':
            import hashlib
            if hashlib.sha1(field.data).hexdigest() != b.hash:
                raise validators.ValidationError(u'Bad solution.')

class SolutionForm(Form):
    text = TextField(u'Solution text', [SolutionValidator()])
    address = TextField(u'Bitcoin address', [validators.Length(min=34, max=34)])
    

