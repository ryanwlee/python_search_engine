from bottle import template, route, run, static_file, request, get, post, redirect, response, error
import bottle
import string, operator

# For google auth
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from apiclient.errors import HttpError
from apiclient.discovery import build
import httplib2

# For session
from beaker.middleware import SessionMiddleware
session_opts={'session.type': 'file', 'session.cookie-expires': 300, 'session.auto': True, 'session.data_dir': './data'}
app = SessionMiddleware(bottle.app(), session_opts)

import os

# For db access
import sqlite3 as lite
from BeautifulSoup import BeautifulSoup
import urllib2


################################################################################################
# First pages
################################################################################################

# Check user's mode
@route('/',method='get')
def ask_mode():
 s = bottle.request.environ.get('beaker.session')
 if 'signed' in s and s['signed'] == cre:
  s['signed'] = cre

  family_name=s['family_name']
  name=s['name']
  picture=s['picture']
  gender=s['gender']
  email=s['email']
  s.save()

  return template('noauth', family_name=family_name, name=name, picture=picture, gender=gender, email=email)
 else:
  return template('auth')

# If anonymous, redirect to anonymous main page
# If google, redirect to google auth
@route('/',method='post')
def decide_mode():
 check = request.forms.get('check')
 acheck = request.forms.get('acheck')

# logged in user
 if check == 'Anonymous Mode':
  redirect("/signout_anonymous")
 elif check == 'Sign In Mode':
  redirect("/signedin")
 elif check == 'Sign Out':
  redirect("/signout")

# Not logged in user
 if acheck == 'Sign In Mode':
  redirect("/auth")
 elif acheck == 'Anonymous Mode':
    redirect("/anonymous")

 redirect("/error")


################################################################################################
# Redirect when sign out.
################################################################################################

# When user wants to sign out and use anonymous
@route('/signout_anonymous')
def out():
 s = bottle.request.environ.get('beaker.session')
 s.delete()
 redirect("/anonymous")

# Just sign out
@route('/signout')
def out():
 s = bottle.request.environ.get('beaker.session')
 s.delete()
 redirect("/")


################################################################################################
# error section
################################################################################################

# error page when there is a problem at the first page! Simply return to the first page.
@route('/error',method='get')
def general_error():
 return template('error')

@route('/error',method='post')
def general_error_return():
 check = request.forms.get('check')
 if check == 'Try Again':
  redirect("/")
 else:
  redirect("/error")

@error(404)
def error404(error):
 return template('error500')

@error(500)
def error404(error):
 return template('error500')

# error page when the user is signed in, but in anonymous page
@route('/error_signed_user',method='get')
def signed_user_error():
 s = bottle.request.environ.get('beaker.session')
 if 'signed' in s and s['signed'] == cre:
  s['signed'] = cre

  family_name=s['family_name']
  name=s['name']
  picture=s['picture']
  gender=s['gender']
  email=s['email']
  s.save()
 return template('error_signed_user', family_name=family_name, name=name, picture=picture, gender=gender, email=email)

@route('/error_signed_user',method='post')
def signed_user_error_return():
 check = request.forms.get('check')
 if check == 'Signed In Mode':
  redirect("/signedin")
 elif check == 'Sign Out':
  redirect("/signout")
 else:
  redirect("/error")

# error page when the user is not signed in, but in signed in page
@route('/error_signed_out_user',method='get')
def signed_out_user_error():
 return template('error_signed_out_user')

@route('/error_signed_out_user',method='post')
def signed_out_user_error_return():
 check = request.forms.get('check')
 if check == 'Signed In Mode':
  redirect("/auth")
 elif check == 'Anonymous Mode':
  redirect("/anonymous")
 else:
  redirect("/error")


################################################################################################
# Authentication
################################################################################################

# Authentication
@route('/auth')
def auth():
 flow = flow_from_clientsecrets("client_secrets.json", scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', redirect_uri="redirect_URL")
  
 uri = flow.step1_get_authorize_url()
 bottle.redirect(str(uri))

# Redirect
@route('/redirect')
def redir():
 code=request.query.get('code', '')
 flow=OAuth2WebServerFlow(client_id='myid', client_secret='my_secret', scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', redirect_uri="redirect_URL")
 credentials=flow.step2_exchange(code)
 token=credentials.id_token['sub']
 http=httplib2.Http()
 http=credentials.authorize(http)
 users_service=build('oauth2', 'v2', http=http)
 u_info=users_service.userinfo().get().execute()
 s = bottle.request.environ.get('beaker.session')
 s['signed'] = cre
 s['family_name'] = u_info['family_name']
 s['name'] = u_info['name']
 s['picture'] = u_info['picture']
 s['gender'] = u_info['gender']
 s['email'] = u_info['email']
 s.save()
 redirect('/signedin')


################################################################################################
# Anonymous mode
################################################################################################

# From here, anonymous codes  
# Load main page and wait for the keywords
@route('/anonymous',method='get')
def anonymous_home():
 s = bottle.request.environ.get('beaker.session')
 if 'signed' in s and s['signed'] == cre:
  redirect('/error_signed_user')
 else:
  return template('anonymous_main')

@route('/anonymous',method='post')
def anonymous_get_parse():
 s = bottle.request.environ.get('beaker.session')
 if 'signed' in s and s['signed'] == cre:
  redirect('/error_signed_user')
 
 check = request.forms.get('check')
 if check == 'Sign In':
  redirect('/auth')

 # Get keywords string
 search = request.forms.get('keywords')

 # Make keywords lower case then get array of words
 rawkeywords = search.lower()
 keywords = rawkeywords.split(' ')
 keyword = keywords[0]
 search = keyword

 # Select data from database
 con = lite.connect("dbFile.db")
 cur = con.cursor()
 cur.execute("SELECT inverted_index.word, inverted_index.doc, pagerank.value FROM inverted_index, pagerank WHERE inverted_index.word=? and inverted_index.doc_id = pagerank.doc_id", (keyword,))
 data = cur.fetchall()

 # With queried data, sort with the pagerank value, high goes top
 temp_url = []
 temp_rank = []

 for lines in data:
  temp_url.append(lines[1])
  temp_rank.append(int(lines[2]))

 temp = dict(zip(temp_url,temp_rank))
 result=sorted(temp.items(), key=operator.itemgetter(1), reverse=True)
 
 preview = []
 i = 0

 # Get title of webpages
 for lines in result:
  if i>9:
   break
  source = urllib2.urlopen(lines[0])
  bs = BeautifulSoup(source)
  bstitle = bs.find('title').text
  preview.append(bstitle)
  i+=1
 
 con.close()

 if len(result)!=0:
  return template('anonymous_result', search=search, result=result, page=0, preview=preview)
 else:
  return template('no_result', search=search)

@route('/anonymous/<new>')
def anonymous_get_parse2(new):
 s = bottle.request.environ.get('beaker.session')
 if 'signed' in s and s['signed'] == cre:
  redirect('/error_signed_user')
 
 check = request.forms.get('check')
 if check == 'Sign In':
  redirect('/auth')

 new_url = new.split('=')
 keyword = new_url[0]
 search = keyword
 page = new_url[1]
 
 # Select data from database
 con = lite.connect("dbFile.db")
 cur = con.cursor()
 cur.execute("SELECT inverted_index.word, inverted_index.doc, pagerank.value FROM inverted_index, pagerank WHERE inverted_index.word=? and inverted_index.doc_id = pagerank.doc_id", (keyword,))
 data = cur.fetchall()

 # With queried data, sort with the pagerank value, high goes top
 temp_url = []
 temp_rank = []

 for lines in data:
  temp_url.append(lines[1])
  temp_rank.append(int(lines[2]))

 temp = dict(zip(temp_url,temp_rank))
 result=sorted(temp.items(), key=operator.itemgetter(1), reverse=True)

 if int(page)>len(result)-1:
  redirect('/error')

 preview = []
 i = 0
 fr = int(page)
 to = int(page)+10

 # Get title of webpages
 for lines in result:
  if i<to and i>=fr and i<len(result):
   source = urllib2.urlopen(lines[0])
   bs = BeautifulSoup(source)
   bstitle = bs.find('title').text
   preview.append(bstitle)
  i+=1

 con.close()

 if len(result)!=0:
  return template('anonymous_result', search=search, result=result, page=page, preview=preview)
 else:
  return template('no_result', search=search)

################################################################################################
# Signed in mode
################################################################################################

# From here, signed-in user codes
# Parse keywords and make arrays for the result and store in history

@route('/signedin',method='get')
def home():
 s = bottle.request.environ.get('beaker.session')
 if 'signed' in s and s['signed'] == cre:
  s['signed'] = cre

  family_name=s['family_name']
  name=s['name']
  picture=s['picture']
  gender=s['gender']
  email=s['email']
  s.save()

  return template('main', family_name=family_name, name=name, picture=picture, gender=gender, email=email)
 else:
  redirect('/error_signed_out_user')

@route('/signedin',method='post')
def get_parse():
 s = bottle.request.environ.get('beaker.session')
 if 'signed' in s and s['signed'] == cre:
  s['signed'] = cre

  family_name=s['family_name']
  name=s['name']
  picture=s['picture']
  gender=s['gender']
  email=s['email']
  s.save()

 else:
  redirect('/error_signed_out_user')

 check = request.forms.get('check')
 if check == 'Sign Out':
  redirect('/signout')
 if check == 'Anonymous Mode':
  redirect('/signout_anonymous')
 # Get keywords string
 search = request.forms.get('keywords')

 # Make keywords lower case then get array of words
 rawkeywords = search.lower()
 keywords = rawkeywords.split(' ')
 keyword = keywords[0]
 search = keyword
 
 # Select data from database
 con = lite.connect("dbFile.db")
 cur = con.cursor()
 cur.execute("SELECT inverted_index.word, inverted_index.doc, pagerank.value FROM inverted_index, pagerank WHERE inverted_index.word=? and inverted_index.doc_id = pagerank.doc_id", (keyword,))
 data = cur.fetchall()

 # With queried data, sort with the pagerank value, high goes top
 temp_url = []
 temp_rank = []

 for lines in data:
  temp_url.append(lines[1])
  temp_rank.append(int(lines[2]))

 temp = dict(zip(temp_url,temp_rank))
 result=sorted(temp.items(), key=operator.itemgetter(1), reverse=True)
 
 preview = []
 i = 0

 # Get title of webpages
 for lines in result:
  if i>9:
   break
  source = urllib2.urlopen(lines[0])
  bs = BeautifulSoup(source)
  bstitle = bs.find('title').text
  preview.append(bstitle)
  i+=1

 con.close()
 if len(result)!=0:
  return template('result', search=search, family_name=family_name, name=name, picture=picture, gender=gender, email=email, result=result, page=0, preview=preview)
 else:
  return template('signed_no_result', search=search, family_name=family_name, name=name, picture=picture, gender=gender, email=email)

@route('/signedin/<new>')
def get_parse2(new):
 s = bottle.request.environ.get('beaker.session')
 if 'signed' in s and s['signed'] == cre:
  s['signed'] = cre

  family_name=s['family_name']
  name=s['name']
  picture=s['picture']
  gender=s['gender']
  email=s['email']
  s.save()

 else:
  redirect('/error_signed_out_user')
 new_url = new.split('=')
 keyword = new_url[0]
 search = keyword
 page = new_url[1]
 
 # Select data from database
 con = lite.connect("dbFile.db")
 cur = con.cursor()
 cur.execute("SELECT inverted_index.word, inverted_index.doc, pagerank.value FROM inverted_index, pagerank WHERE inverted_index.word=? and inverted_index.doc_id = pagerank.doc_id", (keyword,))
 data = cur.fetchall()

 # With queried data, sort with the pagerank value, high goes top
 temp_url = []
 temp_rank = []

 for lines in data:
  temp_url.append(lines[1])
  temp_rank.append(int(lines[2]))

 temp = dict(zip(temp_url,temp_rank))
 result=sorted(temp.items(), key=operator.itemgetter(1), reverse=True)

 preview = []
 i = 0
 fr = int(page)
 to = int(page)+10

 # Get title of webpages
 for lines in result:
  if i<to and i>=fr:
   source = urllib2.urlopen(lines[0])
   bs = BeautifulSoup(source)
   bstitle = bs.find('title').text
   preview.append(bstitle)
  i+=1

 con.close()

 if len(result)!=0:
  return template('result', search=search, family_name=family_name, name=name, picture=picture, gender=gender, email=email, result=result, page=page, preview=preview)
 else:
  return template('signed_no_result', search=search, family_name=family_name, name=name, picture=picture, gender=gender, email=email)


cre='my_secret'
run(host='0.0.0.0', app=app, port=80, debug=True)
