# Project Description

The goal of this project is to create a measure a relationship in terms of degrees of separation between certain terms in Wikipedia. The degrees of separation between wikipedia search terms would be calculated by counting the number of links that would need to be clicked, starting with a link contained in the first article, until the second search term is reached. This calculation would be a proxy for "how closely related" those two search terms are. There are two main options that the user can select. The first is to build a path from one wikipedia article to another, starting with a selected term. The second is to find a path between two terms that the user selects. Each part of the project presents its own algorithmic, data storage, and data retrieval challenges that will be further discussed. The first option is called "Build a Path" and the second is called "Find a Path".

# Executive Summary


# Data Acquisition

## Overview

For this project we require Wikipedia data. More specifically, we require all of the wikipedia search terms or article titles, and a list of all of the link contained in each article. The wikipedia english language dump is 15 GB compressed, so we have to be creative in our solution to acquire either a subset of articles or a different methodology to get this data. We propose several solutions, their tests, and drawbacks.

1. The english language static **html dump:** "A copy of all pages from all Wikipedia wikis, in HTML form." (14.3 GB as a .7z file)

2. **Pywikibot:** Python library that provides functionality to automate work on Wikipedia sites.

3. **SQL interconnectedness files**, provided by Wikipedia. Files contain metadata on which articles contain which links.

4. **CURL the urls** for the article that is chosen on the fly, get the list of links from a parsed HTML, and provide a choice of new articles to explore and build a navigation path.

5. Build a fully connected tree of from a **subset of articles**, limiting search options to terms included in the subset, and navigate the tree of parents(terms) and children(links in the term article) to find the shortest path.




To begin analyzing the degrees of separation between two terms found in wikipedia, we first need to acquire data. For doing this, there are several options, some of which include a full data-dump of the English language wikipedia articles, utilizing a python bot to download 5,000 articles, CURL wikipedia each time a search term is entered, or build a small collection of interconnected articles and use that as the basis for analysis. Another option that was discussed was to utilize some of the .sql files that Wikipedia provides which contain all of the inter-relationships between articles. To test this possible solution, we used a subset of articles from the Philippines and got that to work, but again the sheer size of the file for the english language wikipedia made it impossible to keep exploring this solution.

The data acquisition part of this project has proven challenging given that a full English language Wikipedia dump is too large (15GB compressed) to store on an application like PythonAnywhere. One alternative to a full dump was to obtain a subset of articles, which could be problematic since we are trying to find relationships between multiple search terms, and if the search term happens to not be included in the subset, there would be no way to calculate the degrees of separation between the terms.

Another alternative to a full article dump is to use some of the wikipedia python bots that have been created and open-sourced to get up to 5,000 articles at once. There was a third alternative, which was to utilize XML dumps from the article contents which are easily sub-settable by topic or by popularity, but since the XML file contain plain-text only from the article, we would not be able to see which links are embedded in the article.

## Solution for List of Links (1st step for acquiring data)

Given the difficulty of dealing with a data dump and the difficulty of using the python bot to extract information, we will be implementing a script that does a request to a given URL and brings back the html, to be parsed using BeautifulSoup.


After the retrieval of the text, we look at all of the pieces of html containing a "class: mw-content-ltr"

For example:

      '"<div class="mw-content-ltr" dir="ltr" id="mw-content-text" lang="en"><div class="hatnote" role="note">This article is about artificial satellites. For natural satellites, also known as moons, see <a href="/wiki/Natural_satellite" title="Natural satellite">Natural satellite</a>"'


Once we obtain a link object, we look for the "<a>" anchor to get the actual part of the text which contains the "<href>" , we store that link and its name in a python list to be utilized when the html is rendered. At this stage of the search for a list of links in the article body, it is necessary to check for a valid link. To do so, we use string properties to check whether the URL string starts with 'wiki/' and check for invalid characters.


### Linked List

As a first solution to store the data of which links are in the article of the selected search term, we store article names and links in a linked list. We propose the linked list solution since it provides with a way to begin with a node (which is the first search term as input from the user) and a pointer, which will reference the next node on the list. The next node on the list will then contain the name of the article that was clicked from that first list, and so on.

This data structure provides enough flexibility in that insertion at the final index is fast. Given that no additions are expected to be made to an index in the middle of the list (given its chronological nature), there is no need to insert or update pointers within the list. Another useful characteristic of the linked list is that to perform a search, the program checks at each node starting from the first node and returns the first instance of where a match is found.

This linked list still provides challenges in the sense that in order to visualize the user's steps through the links, there needs to be a method to check for previously clicked-on links.



## Solution for Degrees of Separation and Shortest Path

Secondly, to obtain the nearest path to get from one search term to another, it is not sufficient to get a list of links for each article on the fly.

## Journey through shortest path

## Data types for Storing hierarchical data
Once we have the list of links from an article, we need to be able to store the term for which we began our search, and its first ten links in the article. Then, for those ten, we need to store its first ten links and so on and so forth.



## Flask and Selenium

To provide the "journey" functionality, Selenium python bindings were utilized. These bindings provide API access to web-drivers or web browsers.




https://docs.python.org/3/tutorial/datastructures.html