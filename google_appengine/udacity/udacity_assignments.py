#! /Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7

import webapp2
#from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import os
#import cgi
import re
import jinja2
import string
import random
import hashlib

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
   
    def get(self):
        self.render("home.html")

class blog(Handler):
    def get(self, username=""):
        posts = db.GqlQuery('select * from blogp order by created_at desc')
        self.render("blog.html", username=username, posts=posts)

class onepost(Handler):
    def get(self, postid):
        entity = blogp.get_by_id(int(postid))
        title = entity.title
        content = entity.content 
        created = entity.created_at
        username = 'dan'
        self.render("onepost.html", id=postid, username=username, title=title, content=content, created=created)

class newpost(Handler):
    def write_form(self, title="", blogp="", error=""):
        self.render('newpost.html', title=title, blogp=blogp, error=error) 

    def get(self):
        self.write_form()

    def post(self):
        title = self.request.get('subject')
        content = self.request.get('content')
        if title and content:
            entry = blogp(title=title, content=content)
            entry.put()
            self.redirect('/blog/'+str(entry.key().id()))
#        self.write_form(title, blogp, '')
        else: self.write_form(title, content, '')

class blogp(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created_at = db.DateTimeProperty(auto_now_add = True)
    #url = db.

class rot13(Handler):
    def write_form(self, input=""):
        self.render("rot13.html", input=input)

    
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form()

    def post(self):
        input = self.request.get('text')
        input = self.shift13(input)
        self.write_form(input)

    def shift13(self, s):
        lowers = 'abcdefghijklmnopqrstuvwxyz'
        uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i in range(0,len(s)):
            if s[i] in lowers:
                s = s[:i] + lowers[(lowers.find(s[i])+13) % 26] + s[i+1:]
            if s[i] in uppers:
                s = s[:i] + uppers[(uppers.find(s[i])+13) % 26] + s[i+1:]
        return s

class users(db.Model):
    #user_id = db.IntegerProperty(required = True)
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)


class signup(Handler):
    
    def write_form(self, user="", pw1="", pw2="", email="", err1="", err2="", err3="", err4=""):
        self.render("signup1.html", user=user, pw1=pw1, pw2=pw2, email=email, err1=err1,
                                              err2=err2, err3=err3, err4=err4)
    
    def get(self):
        self.write_form()

    def post(self):
        name = self.request.get('username')
        pw1 = self.request.get('password')
        pw2 = self.request.get('verify')
        email = self.request.get('email')
        
        errors = check_input(name, pw1, pw2, email)
        if errors == ['','','','']:
            
            user = users(username=name, pw_hash=make_user_hash(name, pw1)) 
            user.put()
            user_id = user.key().id()
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.headers.add_header('Set-Cookie', 'user_id=%s' % user_id)  # FIXX
            self.redirect('/welcome?username=%s' % name)
        else:
            self.write_form(name, '', '', email, errors[0], errors[1], errors[2], errors[3])



def check_input(name, pw1, pw2, email):
    #allok = True
    errors=['','','','']

    if not re.match("^[a-zA-Z0-9_-]{3,20}$",name):
        #allok = False
        errors[0] = 'That\'s not a valid username.'

    if not re.match("^.{3,20}$",pw1):
        #allok = False
        errors[1] = 'That\'s not a valid password.'

    if pw1 != pw2:
        #allok = False
        errors[2] = 'Your passwords didn\'t match'

    if not re.match("^[\S]+@[\S]+\.[\S]+$",email) and email !='':
        #allok = False
        errors[3] = 'That\'s not a valid email.'

    return errors

 
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_user_hash(name, pw, salt=None):
    if not salt:
        salt=make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)

class welcome(Handler):
    def get(self):
        name = ''
        name = str(self.request.get('username'))
        self.render("welcomemsg.html", name=name)

app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/rot13', rot13),
                                      ('/signup',signup),
                                      ('/welcome',welcome),
                                      ('/blog',blog),
                                      ('/blog/newpost',newpost),
                                      webapp2.Route('/blog/<postid>', handler=onepost, name="title")],
                                     debug=True)

#def main():
#    run_wsgi_app(application)

#if __name__ == "__main__":
#    main()
