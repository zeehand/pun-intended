from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import cgi
import re

homepage = """
<html>
  <head>
    <title>Dan's Workspace</title>
  </head>

  <body>
    <h2>Applications</h2>
    <a href="/rot13">rot13</a><br>
    <a href="/signup">user signup form</a><br>
  </body>

</html>
"""

form = """
<html>
  <head>
    <title>Unit 2 Rot 13</title>
  </head>

  <body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text"
                style="height: 100px; width: 400px;">%(input)s</textarea>
      <br>
      <input type="submit">
    </form>
   <a href="/">Home</a> 
  </body>

</html>
"""

welcomemsg = """
<html>
  <head>
    <title>Welcome</title>
  </head>

  <body>
    <h2>Welcome %(name)s!</h2>
    <a href='/'>Home</a>
  </body>
</html>
"""

signupform = """
<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>

  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="%(user)s">
          </td>
          <td class="error">%(err1)s
            
          </td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="%(pw1)s">
          </td>
          <td class="error">%(err2)s
            
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="%(pw2)s">
          </td>
          <td class="error">%(err3)s
            
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="%(email)s">
          </td>
          <td class="error">%(err4)s
            
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
  <a href="/">Home</a>
  </body>

</html>
"""

class MainPage(webapp.RequestHandler):
   
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(homepage)
    
  

class rot13(webapp.RequestHandler):
    def write_form(self, input=""):
        self.response.out.write(form % {"input":input})

    
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form()

    def post(self):
        input = self.request.get('text')
        input = self.shift13(input)
        self.write_form(cgi.escape(input))

        #if input == 'dan':
        #    self.response.out.write('thanks, that is dan')
        #else:
        #    self.write_form(input)

    def shift13(self, s):
        lowers = 'abcdefghijklmnopqrstuvwxyz'
        uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i in range(0,len(s)):
            if s[i] in lowers:
                s = s[:i] + lowers[(lowers.find(s[i])+13) % 26] + s[i+1:]
            if s[i] in uppers:
                s = s[:i] + uppers[(uppers.find(s[i])+13) % 26] + s[i+1:]
        return s

class signup(webapp.RequestHandler):
    
    def write_form(self, user="", pw1="", pw2="", email="", err1="", err2="", err3="", err4=""):
        self.response.out.write(signupform % {'user':user, 'pw1':pw1, 'pw2':pw2, 'email':email, 'err1':err1,
                                              'err2':err2, 'err3':err3, 'err4':err4})
    
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

class TestHandler(webapp.RequestHandler):
    def post(self):
        #q = self.request.get("q")
        #self.response.out.write(q)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(self.request)

class welcome(webapp.RequestHandler):
    def get(self):
        name = ''
        name = str(self.request.get('username'))
        self.response.out.write(welcomemsg % {'name':name})

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/testform', TestHandler),
                                      ('/rot13', rot13),
                                      ('/signup',signup),
                                      ('/welcome',welcome)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()