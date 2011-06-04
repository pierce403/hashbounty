import settings

from flask import Flask
app = Flask(__name__)

from flask import url_for, redirect, make_response, render_template, abort, request, flash

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
          address=form.address.data,
        )
        b.put()
        return redirect(url_for('bounties'))
    
    bounties = Bounty.all().order('-ctime').fetch(1000)
    
    return render_template('bounties.html', form=form, bounties=bounties)

@app.route('/bounty/<key_name>', methods=['GET', 'POST'])
def bounty(key_name):
    b = Bounty.get_by_key_name(key_name)
    form = SolutionForm(request.form)
    if request.method == 'POST' and form.validate():
        b.solved = True
        b.put()
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


# --forms
from wtforms import Form, TextField, SelectField, FloatField, validators

class BountyForm(Form):
    type = SelectField(u'Hash type', choices=[('md5', 'MD5'), ('sha1', 'SHA1')])
    hash = TextField(u'Hash data', [validators.Length(min=1, max=1000)])
    email = TextField(u'Email Address', [validators.Length(min=6, max=35)])
    bounty = FloatField(u'Bounty (BTC)')
    address = TextField(u'Bitcoin address', [validators.Length(min=34, max=34)])

class SolutionForm(Form):
    text = TextField(u'Solution text')
    address = TextField(u'Bitcoin address', [validators.Length(min=34, max=34)])

