#Modified by Tingcheng Cui(998742491) Oct 12,2014

# Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import thread
import urlparse
from collections import defaultdict
from BeautifulSoup import *
import pagerank
import re
import sqlite3 as lite
def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')


class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""
    
    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }
        self.lexicon = {}
        
        self.doclist = {}
        self.doctable = {}
        self.links = []
        self.pagerank = {}
        # thread.start_new_thread(self.load_everything,("1",self))
        self = load_everything(self)
        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame', 
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset', 
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass
    
   #modified start
    def get_inverted_index(self):
        inverted_index={}     
        lexiconsize=len(self.lexicon)
        docsize=len(self.doctable)
        for i in range (0, lexiconsize):
            tempset=set()
            for j in range (0 , docsize):
                temp=self.doctable.values()[j]
                for k in range (0 , len(temp)):
                    (x,y)=temp[k]
                    if x == self.lexicon.values()[i]:
                        tempset.add(self.doctable.keys()[j])
            inverted_index[self.lexicon.values()[i]]=tempset
        return inverted_index
                    
    def get_resolved_inverted_index(self):
        resolved_inverted_index = {}
        lexiconsize=len(self.lexicon)
        docsize=len(self.doctable)
        for i in range (0, lexiconsize):
            tempset=set()
            for j in range (0 , docsize):
                temp=self.doctable.values()[j]
                for k in range (0 , len(temp)):
                    (x,y)=temp[k]
                    if x == self.lexicon.values()[i]:
                        for url,urlid in self.doclist.items():
                            if urlid == self.doctable.keys()[j]:
                                tempset.add(url)
            resolved_inverted_index[self.lexicon.keys()[i]]=tempset
        return resolved_inverted_index
    
    def insert_document(self, url):
	# add url to document list doclist if not exist
	# increment count if exist
        if url in self.doclist:
            return self.doclist[url]
        else:
            self.doclist[url]=len(self.doclist)+1
            return self.doclist[url]
    
   
    def insert_word(self, word):
        # add word to lexicon if not exist
	# increment count if exist
        if word in self.lexicon:
            return self.lexicon[word]
        else:     
            self.lexicon[word]=len(self.lexicon)+1
            return self.lexicon[word]
    
    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]
        
        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word, 
        #          store it in the word id cache, and return the id.

        word_id = self.insert_word(word) #changed mock function to own function
        self._word_id_cache[word] = word_id
        return word_id
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        # TODO: just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.
        
        doc_id = self.insert_document(url) #changed mock function to own function
        self._doc_id_cache[url] = doc_id
        return doc_id
    #modified end 
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import 
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        # TODO
        self.links.append((from_doc_id, to_doc_id))
        return

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print "document title="+ repr(title_text)

        # TODO update document title for document id self._curr_doc_id
    
    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))
        print((dest_url, self._curr_doc_id, self._curr_url))
        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url
    
    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        self.doctable[self._curr_doc_id]=self._curr_words #a dict type pairs document ids and lexicons
        print "    num words="+ str(len(self._curr_words))

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))
        
    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def pagerank_db_update(self):
        con = lite.connect("dbFile.db")
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS pagerank(doc_id\
                    INTEGER, value FLOAT);')
        cur.execute('CREATE unique index IF NOT EXISTS doc on pagerank(doc_id)')
        for item in self.pagerank:
            command = 'INSERT OR REPLACE INTO pagerank VALUES('+str(item)+', '+str(self.pagerank[item])+');'
            print command
            cur.execute(command)
        con.commit()
        con.close()

    def index_db_update(self):
        index_dict = self.get_resolved_inverted_index()
        con = lite.connect("dbFile.db")
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS inverted_index(word\
                    TEXT, doc TEXT, doc_id INTEGER);')
        for item in index_dict:
            for doc in index_dict[item]:
                command = 'DELETE FROM inverted_index where word = \"'+str(item)+'\" and doc = \"'+str(doc)+'\" and doc_id = '+str(self.doclist[doc])+';'
                print command
                cur.execute(command)
                command = 'INSERT INTO inverted_index VALUES(\"'+str(item)+'\", \"'+str(doc)+'\", '+str(self.doclist[doc])+');'
                print command
                cur.execute(command)
        con.commit()
        con.close()
        
    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited
            
            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                print "    url="+repr(self._curr_url)

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()
        print(self.links)
        self.pagerank = pagerank.page_rank(self.links, num_iterations=20, initial_pr=1.0)
       # thread.start_new_thread(self.pagerank_db_update,("1",self))
       # thread.start_new_thread(self.index_db_update,("1",self))

        thread.start_new_thread(update_everything,("1",self))
        self.pagerank_db_update()
        self.index_db_update()
        
        
def load_everything(self):
    con = lite.connect("dbFile_raw.db")
    cur = con.cursor()
    self.lexicon = {} 
    self.doclist = {}
    self.doctable = {}
    self.links = []
    cur.execute('CREATE TABLE IF NOT EXISTS lexicon(word\
                TEXT, word_id INTEGER);')
    cur.execute('CREATE TABLE IF NOT EXISTS doclist(doc\
                TEXT, doc_id INTEGER);')
    cur.execute('CREATE TABLE IF NOT EXISTS doctable(doc_id\
                INTEGER, word_id INTEGER, font INTEGER);')
    cur.execute('CREATE TABLE IF NOT EXISTS links(from_id\
                INTEGER, do_id INTEGER);')
    
    a = cur.execute('select * from lexicon')
    for line in a:
        self.lexicon[line[0]] = line[1]
        
    a = cur.execute('select * from doclist')
    for line in a:
        self.doclist[line[0]] = line[1]
        
    a = cur.execute('select * from doctable')
    for line in a:
        if line[0] not in self.doctable:
            self.doctable[line[0]] = [(line[1], line[2])]
        else:
            self.doctable[line[0]].append((line[1], line[2]))
            
    a = cur.execute('select * from links')
    for line in a:
        self.links.append((line[0], line[1]))
    con.commit()
    con.close()
    return self
        
def update_everything(name, self):
    
    con = lite.connect("dbFile_raw.db")
    cur = con.cursor()
    
    a = cur.execute('delete from lexicon')
    a = cur.execute('delete from doclist')
    a = cur.execute('delete from doctable')
    a = cur.execute('delete from links')
    for item in self.lexicon:
        command = 'INSERT INTO lexicon VALUES(\"'+str(item)+'\", '+str(self.lexicon[item])+');'
        cur.execute(command)
    for item in self.doclist:
        command = 'INSERT INTO doclist VALUES(\"'+str(item)+'\", '+str(self.doclist[item])+');'
        cur.execute(command)
    for item in self.doctable:
        for n,m in self.doctable[item]:
            command = 'INSERT INTO doctable VALUES('+str(item)+', '\
                      +str(n)+ ','+str(m)+');'
            cur.execute(command)
    for item1,item2 in self.links:
        command = 'INSERT INTO links VALUES(\"'+str(item1)+'\", '+str(item2)+');'
        cur.execute(command)
    con.commit()
    con.close()   
if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)

