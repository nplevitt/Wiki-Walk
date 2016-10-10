# -- coding: utf-8 --

from flask import Flask, request, render_template, redirect
import urllib2
from bs4 import BeautifulSoup
import os
import random
from getWikiSubset import *
from journey import *

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
	global currentPage

	response = urllib2.urlopen(URL)
	html = BeautifulSoup(response, "html.parser")
	title = html.find_all('h1', {'id': 'firstHeading'})[0].text
	currentPage = title

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
			term = urllib2.quote(term,':/') # keep all the %xx URL codes
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
	except:
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
			dot += '\t"' + key.encode('ascii', errors='ignore') + '" -> "' + value.encode('ascii', errors='ignore') + '";\n'
	dot += "}"
	file = open("static/graph.txt", "w")
	file.write(dot)
	file.close()
	os.system('dot -Tpng static/graph.txt > static/graph.png')
	return dot

def dictToDotPath(path):
    dot = "digraph g {\n"
    dot += "\trankdir=LR;\n"
    for i in range(len(path)-1):
        dot += '\t"' + urllib2.unquote(path[i]) + '" -> "' + urllib2.unquote(path[i+1]) + '";\n'
    dot += "}"
    file = open("static/path_graph.txt", "w")
    file.write(dot)
    file.close()
    os.system('dot -Tpng static/path_graph.txt > static/path_graph.png')
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

	return render_template('combined_page.html')

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
	<head>
	<br>
    <form action="/">
    Click here to go back to the beginning <input type="submit" value="Go back" class="tfbutton">
    </head>
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
	trSearchString = transformTerms(searchString)
	# get list of links
	listOfLinks = getLinksFromSearchString(trSearchString)
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

@app.route("/get_path", methods =['GET'])
def path_home():
    return render_template('get_path.html')

@app.route("/show_path", methods = ['GET', 'POST'])
def render_path():
    html = """
    <html>
    <body>
    <header>
    The Shortest Path From %s To %s Is:
    <img src=%s></img>
    </header>
    <br>
    <form action="/take_journey" method="post">
    <input type="submit" value="Take The Journey" class="tfbutton">
    <br>
    <br>
    </body>
    </html>
    """
    response = redirect('/take_journey')
    start_node = request.cookies.get('start_node') # get cookie called 'ID'
    end_node = request.cookies.get('end_node') # get cookie called 'ID'
    response.set_cookie('start_node', value=start_node)
    response.set_cookie('end_node', value=end_node)

    with open('trees/Full_Graph_400.txt', 'r') as f:
        graph = f.read().split('\t')

    paths = get_all_paths(graph, start_node, end_node, 5)
    path_lengths = [len(p) for p in paths]
    shortest_path = paths[path_lengths.index(min(path_lengths))]
    dictToDotPath(shortest_path)
    imageURL = "/static/path_graph.png?r=%s" % random.randint(0, 10000)

    return html % (urllib2.unquote(start_node), urllib2.unquote(end_node), imageURL)

@app.route("/set_nodes", methods = ['GET', 'POST'])
def set_nodes():
    start_node = request.form['startlocation']
    end_node = request.form['endlocation']
    response = redirect('/show_path')
    response.set_cookie('start_node', value=start_node)
    response.set_cookie('end_node', value=end_node)
    return response

@app.route("/take_journey", methods = ['GET', 'POST'])
def take_journey():
    html = """
    <html>
    <body>
    <header>
    Thank You For Taking The Journey From %s To %s \n
    Click Below To Do It Again
    <form action="/start_over" method="post">
    <input type="submit" value="Take Another Journey" class="tfbutton">
    </header>
    </body>
    </html>
    """

    start_node = request.cookies.get('start_node') # get cookie called 'ID'
    end_node = request.cookies.get('end_node') # get cookie called 'ID'
    takeJourney(start_node, end_node)

    return html % (urllib2.unquote(start_node), urllib2.unquote(end_node))

@app.route("/start_over", methods = ['GET', 'POST'])
def start_over():
    response = redirect('/get_path')
    return response

app.run() # kickstart your flask server
