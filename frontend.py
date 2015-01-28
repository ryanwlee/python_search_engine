#Coded by Tingcheng Cui(998742491) Oct 12,2014
from bottle import Bottle, run, get, template, route, request
from collections import OrderedDict

app=Bottle()
count={}
@app.route('/', Method='GET')
def search():
    return '''
	<p><font size="40">:)</font></p>
	<p><font size="20">CSC326 BEST COURSE A+ PLZ SEARCH ENGINE</font></p>
        <form action="/word_search" method="get">
            keywords: <input name="keywords" type="text" />
            <input value="search" type="submit" />
        </form>
	<form action="/query" method="get">
            <input value="history" type="submit" />
        </form>
    '''

@app.route('/word_search', method='GET')
def word_search():
	dic={}
	keywords = request.query.keywords      #retieve keywords 
    	print keywords				#background debug
	word_list = keywords.split(" ")		#split keywords in to list
	for i in range (0,len(word_list)):	#loop over list
		if word_list[i] in dic:		#if word in list increment count
			dic[word_list[i]]=dic[word_list[i]]+1
		else:
			dic[word_list[i]]=1	#else create word
    	

	for i in range (0,len(word_list)):	#update history
		if word_list[i] in count:	#if exist increment
			count[word_list[i]]=count[word_list[i]]+1
		else:				#if not exist, create
			count[word_list[i]]=1
	
	rtn="<table id=\"results\">"		#output table
	for i in range (0,len(dic)):
		rtn=rtn+"<tr><td>"+dic.keys()[i]+"</td><td>"+str(dic.values()[i])+"</td></tr>"
	rtn=rtn+"</table>"
	print rtn
	return rtn
	


@app.route('/query', method='GET')
def query():
	order_count= OrderedDict(sorted(count.items(), key=lambda x: x[1])) #sort history dic
	rtn="<table id=\"history\">"
	if len(order_count)>20:	#decide how many output
		lenth=20
	else:
		lenth=len(order_count)
	for i in range (0,lenth): #create output for history
		j=len(order_count)-i-1
		rtn=rtn+"<tr><td>"+order_count.keys()[j]+"</td><td>"+str(order_count.values()[j])+"</td></tr>"
	rtn=rtn+"</table>"
	print rtn
	return rtn


run(app, host='localhost', port=8080, debut=True)
