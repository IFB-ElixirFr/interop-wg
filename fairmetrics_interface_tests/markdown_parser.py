#!/usr/bin/python3
# -*- coding: utf-8 -*-

import mistune

class MyCustomRenderer(mistune.Renderer):
   def header(self, text, level, raw=None):
       return "<h%s class='my-cusom-header-cls'><u>%s</u></h%s>" % (level, text, level)
   def image(self, src, title, alt_text):
       return "<img src='%s' alt='%s' class='img-responsive'>" % (src, alt_text)
   def link(self, link, title, content):
       if link.lower().startswith('http://'):
           link = 'https://' + link[len('http://'):]
       elif link.lower().startswith('https://'):
           pass # we do not need any processing here
       else:
           # so it is a relative link.
           # We can add a domain in front of it.
           link = link.lstrip('/')
           link = 'https://example.com/' + link
       return "<a href='%s' title='%s'>%s</a>" % (link, title, content)
   def block_code(self, code, lang):
       if not lang:
           return '\n<pre><code>%s</code></pre>\n' % mistune.escape(code)
       lexer = get_lexer_by_name(lang, stripall=True)
       formatter = html.HtmlFormatter()
       return highlight(code, lexer, formatter)

if __name__ == "__main__":

    test_str = """I am using **mistune markdown parser**
# This is a first level header
This is a short one line paragraph.

Here is a [link](http://example.com)

Here is an image: ![img_test](https://www.w3schools.com/w3css/img_lights.jpg)

'testtune'

'''python\nprint("help")\n'''

| tableau | de | test |
| ------- | -- | ---- |
| toto | titi | tutu |
"""

    renderer = MyCustomRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    html_str = markdown(test_str)
    print(html_str)
