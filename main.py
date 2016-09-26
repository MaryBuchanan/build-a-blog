#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
import cgi
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

t_base = jinja_env.get_template("base.html")

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    """Base RequestHandler"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class blog(Handler):
     """Handles requests coming in to '/blog' """

     def render_front(self, title="", body="", error=""):
        blog_posts = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC LIMIT 5')
        self.render("blog.html", blog_posts=blog_posts)

     def get(self):
        self.render_front()


class NewPost(Handler):
    """ handles requests coming in to /newpost"""

    def get(self):
         self.render("form.html")

    def post(self, title="", body="", error=""):
        title= self.request.get("title")
        body= self.request.get("body")

         #if nothing entered, redirect and error message
        if title and body:
            b = Blog(title = title, body= body)
            b.put()
            x=str(b.key().id())
            self.redirect("/blog/" + x)

        else:
            error = "OOPS! We need both a title and body for the blog post."
            self.render("form.html", title=title, body=body, error=error)

class ViewPostHandler(Handler):
    """handles requests coming in to /blog/<id:\d+>"""

    def get(self, id):
        post = Blog.get_by_id(int(id), parent=None)
        self.render("Post.html", post = post)




app = webapp2.WSGIApplication([
    webapp2.Route(r'/blog', handler=blog, name='blog'),
    webapp2.Route(r'/newpost', handler=NewPost, name='newpost'),
    webapp2.Route(r'/blog/<id:\d+>', handler=ViewPostHandler, name='viewpost'),
], debug=True)
