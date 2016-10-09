# -- coding: utf-8 --	

from flask import Flask, request, render_template
import urllib2
from bs4 import BeautifulSoup
import os
import random


mainWikiURL = "https://en.wikipedia.org%s"
template_wikiURL = "/wiki/%s"
# Wikipedia page URL: mainWikiURL % template_wikiURL % search_terms_like_this

serverURL = "http://aguimaraesduarte.pythonanywhere.com/links/%s"
# to be updated if necessary

currentPage = ""
previousPage = ""

visitedPages = {} # dictionary
visitedLinks = [] # list

counter = 0 # in order to "refresh" the index.html page

# getLinksFromURL: get all links inside body of Wikipedia article.
# @param URL: full Wikipedia page URL
# @return links: list of wikiURLs ('/wiki/<page>') found in the main body
def getLinksFromURL(URL):
	#print "Getting links from %s" % URL
	response = urllib2.urlopen(URL)

	#html = BeautifulSoup(response, "html.parser")
	html = BeautifulSoup(response.read().decode('utf-8', 'ignore'), "html.parser")

	links = []
	content = html.find_all('div', {'class': 'mw-content-ltr'})[0]
	for link in content.find_all('a'):
		href = link['href']
		try:
			title = link['title']
		except:
			title =[]
		if (href.startswith('/wiki/')) and (":" not in href) and (href not in links):
			term = href.split("#")[0]
			term = urllib2.quote(term,':/') # keep all the %CE codes
			links.append((term,title)) # remove trailing "#" if it has one

	return links

# transformTerms: convert spaces into underscores for Wikipedia URL.
# @param searchString: input string with spaces
# @return searchString where eventual spaces have been replaced with underscores
def transformTerms(searchString):
	return "_".join(searchString.split()) # Something_like_this

# getLinksFromSearchString: convert input search terms as a string into
# a potentially valid Wikipedia URL, and get the list of links in that page.
# @param searchString: input search terms as string
# return links from getLinksFromURL(URL)
# If error (not a valid Wikipedia URL), then return error string as single element list)
def getLinksFromSearchString(searchString):
	searchURL = template_wikiURL % searchString
	URL = mainWikiURL % searchURL
	try:
		return getLinksFromURL(URL)
	except Exception, e:
		return ["%s is not a valid search term" % searchString]

# htmlList: from a list of links from a Wikipedia page (using terms from <searchString>),
# create and return html code for an organized table of said links.
# @param listOfLinks: list of parital Wikipedia links as strings
# @param searchString: input search terms as string
# @return html: html code for the table
# If error (only one link <=> invalid Wikipedia URL), then special handling needed
def htmlList(listOfLinks, searchString):
	html_template = """
	<table>
	%s
	%s
	</table>"""

	if len(listOfLinks)==1:
		html_header = "<tr><th>%s: 0 links</th></tr>" % searchString
		html_entry = "<tr><td>%s</td></tr>" % listOfLinks[0][0]
		html = html_template % (html_header, html_entry)
		return html
	else:
		href = mainWikiURL % template_wikiURL % searchString
		html_header = "<tr><th><a href='%s'>%s</a>: %d links</th></tr>" % (href, searchString, len(listOfLinks))
		html_entries_template = "<tr><td><a href='%s'>%s</a></tr></td>"
		html_entries = ""
		for link in listOfLinks:
			linkHref = link[0].split("/wiki/")[1]
			try:
				linkTitle = link[1]
			except:
				linkTitle = ''
			# linkText = urllib2.unquote(linkHref)
			html_entries += html_entries_template % (linkHref,linkTitle)
		html = html_template % (html_header, html_entries)
		return html

# updateVisited: update the visitedPages dictionary with visited links.
def updateVisited():
	if previousPage not in visitedPages:
		if previousPage != "":
			visitedPages[previousPage] = [currentPage]
		else:
			visitedPages[currentPage] = []
	else:
		if currentPage not in visitedPages[previousPage]:
			visitedPages[previousPage].append(currentPage)

# dictToDot: transform dictionary d into a dot string that is saved into graph.txt.
# graph.txt is converted into a graph.png image using command line dot function.
# @param d: input directed dictionary
# @return dot: string of connected graph for debugging purposes
def dictToDot(d):
	dot = "digraph g {\n"
	dot += "\trankdir=LR;\n"
	for key in d.keys():
		for value in d[key]:
			dot += '\t"' + key + '" -> "' + value + '";\n'
	dot += "}"
	file = open("static/graph.txt", "w")
	file.write(dot)
	file.close()
	os.system('dot -Tpng static/graph.txt > static/graph.png')
	return dot

############################# Flask stuff

app = Flask(__name__)

@app.route("/")
def home():
	global visitedPages
	global visitedLinks
	global currentPage
	global previousPage

	visitedPages = {} # dictionary
	visitedLinks = [] # list
	currentPage = ""
	previousPage = ""

	global counter
	counter = 0

	return render_template('index.html')
	#return app.send_static_file("index.html")

@app.route("/links/", methods=['POST'])
def post_links():
	searchString = request.form["searchString"]
	return links(searchString)

@app.route("/links/<searchString>")
def links(searchString):
	global currentPage
	global previousPage
	global counter

	html = """
	<html>
	<body>
	<header>
	<img src=%s></img>
	</header>
	<br>
	%s
	%s
	</body>
	</html>
	"""

	# transform into wiki format
	currentPage = transformTerms(searchString)
	# get list of links
	listOfLinks = getLinksFromSearchString(currentPage)
	# create html table
	table = htmlList(listOfLinks, currentPage)
	# update visited links and dictionary
	updateVisited()
	visitedLinks.append(currentPage)
	dot = dictToDot(visitedPages)
	# update previous page
	previousPage = currentPage
	# assemble final html
	imageURL = "/static/graph.png?r=%s" % random.randint(0,10000)
	returnHtml = html % (imageURL, " --> ".join(visitedLinks), table)
	# update counter for index.html to refresh
	counter += 1

	return returnHtml

app.run() # kickstart your flask server
