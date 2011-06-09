import logging, time
from datetime import datetime

from google.appengine.api import taskqueue

import settings

from flask import Flask
app = Flask(__name__)

from flask import url_for, redirect, make_response, render_template, abort, request, flash

from email_messages import send_message
import btc


# --views
@app.route('/')
def main():
    return redirect(url_for('bounties'))

@app.route('/bounties', methods=['GET', 'POST'])
def bounties():
    cursor = request.values.get("cursor")
    
    sortfilterform = SortFilterForm(request.values)
    form = BountyForm(request.form)
    
    if request.method == 'POST' and form.validate():
        b = Bounty.from_form(form)
        b.put()
        send_message(b.email, "bounty_submitted", bounty=b)
        return redirect(url_for('bounties'))

    query = Bounty.all().filter('active =', True)

    if sortfilterform.validate():
        sort = sortfilterform.sort.data
        filter = sortfilterform.filter.data
        if sort == 'age_desc':
            query = query.order('-ctime')
        elif sort == 'age_asc':
            query = query.order('ctime')
        elif sort == 'reward_desc':
            query = query.order('-bounty')
        elif sort == 'reward_asc':
            query = query.order('bounty')
        if filter == 'md5':
            query = query.filter('type =', 'md5') 
        elif filter == 'sha1':
            query = query.filter('type =', 'sha1') 

    if cursor:
        query.with_cursor(cursor)
    bounties = query.fetch(24)
    cursor = query.cursor()


    return render_template('bounties.html',
      form=form, sortfilterform=sortfilterform,
      bounties=bounties,
      cursor=cursor)

@app.route('/bounty/<int:id>', methods=['GET', 'POST'])
def bounty(id):
    b = Bounty.get_by_id(id)
    if b.solved:
        return "This bounty has already been solved."
    form = SolutionForm(request.form)
    form.bounty = b
    if request.method == 'POST' and form.validate():        
        b.solve(solution=form.text.data, winner=form.address.data)
        return redirect(url_for('bounties'))
    
    return render_template('bounty.html', form=form, bounty=b)


# --cronjobs
@app.route('/jobs/bounty_address_watch')
def bounty_address_watch():
    s = ""
    bounties = Bounty.all().filter('solved =', False).order('-ctime').fetch(1000)
    for b in bounties:
        # update the bounty's BTC budget
        amount = b.update_budget()
        s += "[%s] %s: %s/%s/%s BTC active=%s\n" % (
          b.hash, b.address, amount, b.budget, b.bounty, b.active)
          
    # spawn more tasks
    spawn = int(request.values.get("spawn", "0"))
    if spawn:
        for i in range(spawn):
            countdown = int(60 / (spawn + 1)) * (i+1)
            taskqueue.add(url='/bounty_address_watch', countdown=countdown, method="GET")
    
    return "<pre>%s</pre>" % s

@app.route('/jobs/claim_solved_bounties')
def claim_solved_bounties():
    bounties = Bounty.all().filter('solved =', True).filter(
      'claimed =', False).order('-ctime').fetch(1000)
    s = ""
    for b in bounties:
        try:
            amount = b.claim_bounty()
            s += "[%s] %s: %s/%s BTC\n" % (b.hash, b.address, amount, b.budget)
        except Exception, e:
            logging.exception(b.address)
    return "<pre>%s</pre>" % s


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
    budget = db.FloatProperty(default=0.0)
    active = db.BooleanProperty(default=False)
    
    solved = db.BooleanProperty(default=False)
    solution = db.StringProperty()
    claimed = db.BooleanProperty(default=False)
    winner = db.StringProperty(default=None)

    @classmethod
    def from_form(cls, form):
        address = btc.connection.getnewaddress(settings.BITCOIN_ACCOUNT)
        b = cls(
          type=form.type.data,
          hash=form.hash.data,
          email=form.email.data,
          bounty=0.0, #form.bounty.data,
          address=address,
        )
        return b

    def update_budget(self):
        amount = 0
        try:
            budget = btc.connection.getreceivedbyaddress(self.address, minconf=0)
        except Exception, e:
            logging.exception(self.address)
            return amount
            
        if self.budget != budget:
            amount = budget - self.budget
            logging.info("Bounty %s received %s BTC" % (self.hash, amount))
            self.budget = budget
            self.bounty = budget
            self.active = True
            self.put()
            send_message(self.email, "bitcoins_received", bounty=self, amount=amount)
        return amount        

    def solve(self, solution, winner):
        self.active = False
        self.solved = True
        self.solution = solution
        self.winner = winner
        self.put()
        send_message(self.email, "bounty_solved", bounty=self)

    def claim_bounty(self):
        if self.claimed:
            raise Exception("Bounty already claimed!")        

        amount = self.bounty

        # verify budget to be sure
        budget = btc.connection.getreceivedbyaddress(self.address, minconf=1)
        if budget < amount:
            raise Exception("Budget not yet confirmed, waiting for at least 1 confirmation.")        
            

        btc.connection.sendtoaddress(self.winner, amount)

        self.claimed = True
        self.put()

        return amount
        
    def age_string(self):
        dt = datetime.now() - self.ctime
        mins, secs = divmod(dt.seconds, 60)
        hours, mins = divmod(mins, 60)
        if dt.days:
            return u"%s days" % dt.days
        if hours:
            return u"%s hours" % hours
        if mins:
            return u"%s minutes" % mins
        return u"%s seconds" % secs

        
# --forms
from wtforms import Form, TextField, SelectField, FloatField, validators
from utils.bitcoin_address import AddressValidator
from utils.hashutils import SolutionValidator, HashValidator

class BountyForm(Form):
    type = SelectField(u'Hash type', choices=[('md5', 'MD5'), ('sha1', 'SHA1')])
    hash = TextField(u'Hash data', [HashValidator()])
    email = TextField(u'Email Address', [validators.Length(min=6, max=35)])
    #bounty = FloatField(u'Bounty (BTC)')

class SolutionForm(Form):
    text = TextField(u'Solution text', [SolutionValidator()])
    address = TextField(u'Bitcoin address', [AddressValidator()])
    

class SortFilterForm(Form):
    sort = SelectField(u'Sort', choices=[
        ('age_desc', 'Sort by age, descending'),
        ('age_asc', 'Sort by age, ascending'),
        ('reward_desc', 'Sort by reward, descending'),
        ('reward_asc', 'Sort by reward, ascending'),
        
        ], default='age_desc')
    filter = SelectField(u'Filter', choices=[('all', 'No filter'), ('md5', 'Only MD5 hashes'), ('sha1', 'Only SHA1 hashes')], default='all')

