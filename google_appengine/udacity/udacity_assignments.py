import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import os
import cgi
import re
import jinja2

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
        
        err1 = ''
        err2 = ''
        err3 = ''
        err4 = ''

        allok = True
        
        if not re.match("^[a-zA-Z0-9_-]{3,20}$",name):
            allok = False
            err1 = 'That\'s not a valid username.'
        
        if not re.match("^.{3,20}$",pw1):
            allok = False
            err2 = 'That\'s not a valid password.'

        if pw1 != pw2:
            allok = False
            err3 = 'Your passwords didn\'t match'
            
        if not re.match("^[\S]+@[\S]+\.[\S]+$",email) and email !='':
            allok = False
            err4 = 'That\'s not a valid email.'

        if allok:
            self.redirect('/welcome?username=%s' % name)
        else:
            self.write_form(name, '', '', email, err1, err2, err3, err4)


class welcome(Handler):
    def get(self):
        name = ''
        name = str(self.request.get('username'))
        self.render("welcomemsg.html", name=name)

application = webapp2.WSGIApplication([('/', MainPage),
                                       ('/rot13', rot13),
                                      ('/signup',signup),
                                      ('/welcome',welcome),
                                      ('/blog',blog),
                                      ('/blog/newpost',newpost),
                                      webapp2.Route('/blog/<postid>', handler=onepost, name="title")],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
