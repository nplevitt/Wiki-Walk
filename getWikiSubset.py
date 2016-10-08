# THIS IS NOT FOR IMPLEMENTATION THIS IS A TEST

from flask import Flask, request
import urllib2
from bs4 import BeautifulSoup
import urllib
import pandas as pd
# from python-graph import *
from itertools import chain
import time
import random
from collections import Counter






mainWikiURL = "https://en.wikipedia.org%s"
template_wikiURL = "/wiki/%s"

def getLinks(URL):
    #print "Getting links from %s" % URL
    response = urllib2.urlopen(URL)
    html = BeautifulSoup(response, "html.parser")

    links = []
    content = html.find_all('div', {'class': 'mw-content-ltr'})[0]
    for link in content.find_all('a'):
        href = link['href']
        if (href.startswith('/wiki/')) and (":" not in href) and (href not in links):
            links.append(href.split('/')[2])
    return html, links


def transformTerms(searchString):
    return "_".join(searchString.split()) # Something_like_this

# transformSearchTermsToSearchURL: convert input search terms as a string into
# a potentially valid Wikipedia URL, and get the list of links in that page.
# @param searchString: input search terms as string
# return links from getLinks(URL)
# If error (not a valid Wikipedia URL), then return error string as single element list)

def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None


def transformSearchTermsToSearchURL(searchString):
    wikiURL = transformTerms(searchString)
    searchURL = template_wikiURL % wikiURL
    URL = mainWikiURL % searchURL
    try:
        return getLinks(URL)
    except Exception, e:
        return ["%s is not a valid search term" % searchString]


def look_back(names, indx, num_children):
    path = [names[indx]]
    while indx > 0:
        indx = (indx - 1) / num_children
        path.append(names[indx])
    return path

def get_shortest_path(start_paths, end_paths):
    paths = []
    for start in start_paths:
        for end in end_paths:
            intersect = [(i in start) for i in end]
            try:
                split_element = end[intersect.index(True)]
                part_1 = start[0:start.index(split_element)]
                part_2 = end[0:end.index(split_element)]
                part_2.reverse()
                paths.append(part_1 + [split_element] + part_2)
            except ValueError:
                pass
    return paths


def get_all_paths(names, start_node, end_node, num_children):
    start_points = [i for i, x in enumerate(names) if x == start_node]
    end_points = [i for i, x in enumerate(names) if x == end_node]
    start_paths = []
    end_paths = []

    for start in start_points:
        start_paths.append(look_back(names, start, num_children))

    for end in end_points:
        end_paths.append(look_back(names, end, num_children))

    all_paths = get_shortest_path(start_paths, end_paths)
    return all_paths

def get_connected(root, limit=100, per_page=5):
    list_of_hit = []
    list_of_names = [root]
    count = 0
    while len(list_of_hit) < limit:
        if list_of_names[count] not in list_of_hit:
            terms = list_of_names[count]
            URL = mainWikiURL % template_wikiURL % terms
            print 'Getting Links From %s' % URL
            try:
                html, links = getLinks(URL)
                name_cnt = 0
                for link in links:
                    if link not in list_of_hit:
                        if name_cnt < per_page:
                            tmp_URL = mainWikiURL % template_wikiURL % link
                            tmp_html, tmp_links = getLinks(tmp_URL)
                            if terms in tmp_links:
                                list_of_names.extend([link])
                                name_cnt += 1
                if name_cnt < per_page:
                    list_of_names.extend(['abcdefg']*(per_page - name_cnt))
            except:
                list_of_names.extend(['abcdefg']*per_page)
            list_of_hit.append(terms)
            print 'Starting Iteration %d' % len(list_of_hit)
        count += 1

    return list_of_names



def get_connected_w_dict(root, limit=100, per_page=5):
    list_of_hit = []
    list_of_names = [root]
    count = 0
    list_of_links = dict()
    while len(set(list_of_hit)) < limit:
        if (list_of_names[count] not in list_of_hit) or (list_of_names[count] == 'abcdefg'):
            terms = list_of_names[count]
            URL = mainWikiURL % template_wikiURL % terms
            print 'Getting Links From %s' % URL
            name_cnt = 0
            try:
                html, links = getLinks(URL)
                for link in links:
                    if link not in list_of_hit:
                        if name_cnt < per_page:
                            if link in list_of_links.keys():
                                tmp_links = list_of_links[link]
                            else:
                                tmp_URL = mainWikiURL % template_wikiURL % link
                                tmp_html, tmp_links = getLinks(tmp_URL)
                                list_of_links[link] = tmp_links
                            if terms in tmp_links:
                                list_of_names.extend([link])
                                name_cnt += 1
                if name_cnt < per_page:
                    list_of_names.extend(['abcdefg']*(per_page - name_cnt))
            except:
                list_of_names.extend(['abcdefg']*(per_page - name_cnt))
            list_of_hit.append(terms)
            print 'Starting Iteration %d' % len(list_of_hit)
        else:
            list_of_names.extend(['abcdefg'] * per_page)

        count += 1

    return list_of_names, list_of_hit


# num_children = 5
# list_of_names, list_of_hit = get_connected_w_dict('Microorganism',
#                                      limit=50, per_page=num_children)
#
# with open('Microorganism_Graph.txt', 'w') as f:
#     f.write('\t'.join(list_of_names))
#
# start_node = list(set(list_of_names))[random.randint(0, len(set(list_of_names))-1)]
# end_node = list(set(list_of_names))[random.randint(0, len(set(list_of_names))-1)]

# paths = get_all_paths(list_of_names, start_node, end_node, num_children)
# path_lengths = [len(p) for p in paths]
# shortest_path = paths[path_lengths.index(min(path_lengths))]
# print "There were a total of %d paths from %s to %s " % (len(paths), start_node, end_node)
# print "The shortest path is:"
# print ' --> '.join(shortest_path)


#
# # # num_children = 5
# # # list_of_names, graph = link_iterative('New_York_Park_Association', limit=10, per_page=num_children)
# start_node = list(set(list_of_names))[random.randint(0, len(set(list_of_names))-1)]
# end_node = list(set(list_of_names))[random.randint(0, len(set(list_of_names))-1)]
#
# paths = get_all_paths(list_of_names, start_node, end_node, num_children)
# path_lengths = [len(p) for p in paths]
# shortest_path = paths[path_lengths.index(min(path_lengths))]

#
# # # # # # print 'All paths from %s to %s: '  % (start_node, end_node)
# # # # # # for p in paths:
# # # # # #     print ' --> '.join(p)
#

# #
#
# # OLD CODE

# for name in set(list_of_names):
#     if name not in graph.keys():
#         graph[name] = []
#
# starts_to_pick_from = graph.keys()
# ends_to_pick_from = list(set(list_of_names))
#
# start_node = starts_to_pick_from[random.randint(0, len(starts_to_pick_from)-1)]
# end_node = starts_to_pick_from[random.randint(0, len(starts_to_pick_from)-1)]

# def look_back(names, indx, goal, num_children):
#     path = [names[indx]]
#     while indx > -1:
#         indx = (indx - 1) / num_children
#         path.append(names[indx])
#         if names[indx] == goal:
#             return path
#     return path

# def look_forward(names, indx, goal, num_children):
#     path = [names[indx]]
#     counter = 1
#     while indx < len(names):
#         tmp_indx = indx * num_children + counter
#         if names[tmp_indx] == goal:
#             path.append()

# # end_node = ends_to_pick_from[random.randint(0, len(ends_to_pick_from)-1)]
#
# path = find_path(graph, start_node, end_node)
# print 'Path from %s to %s is:' % (start_node, end_node)
# print path

#
# def link_iterative(root, limit=100, per_page=5):
#     list_of_hit = []
#     list_of_names = [root]
#     list_of_links = []
#     graph = dict()
#     count = 0
#     name_indx = 0
#     while len(graph) < limit:
#         if list_of_names[count] not in list_of_hit:
#             # time.sleep(random.randint(1,3))
#             terms = list_of_names[count]
#             URL = mainWikiURL % template_wikiURL % terms
#             print 'Getting Links From %s' % URL
#             try:
#                 html, links = getLinks(URL)
#                 list_of_names.extend(list(set(links[0:per_page])))
#                 # list_of_links.append(set(links[0:per_page]))
#             except:
#                 list_of_names.extend(['']*per_page)
#             list_of_hit.append(terms)
#             graph[terms] = set(links[0:per_page])
#             print 'Starting Iteration %d' % len(graph)
#         count += 1
#
#     return list_of_names, graph


# def get_full_connect(root, limit=100, per_page=5):
#     list_of_hit = []
#     list_of_names = [root]
#     count = 0
#     while len(list_of_hit) < limit:
#         if list_of_names[count] not in list_of_hit:
#             terms = list_of_names[count]
#             URL = mainWikiURL % template_wikiURL % terms
#             print 'Getting Links From %s' % URL
#             try:
#                 html, links = getLinks(URL)
#                 tmp_cnt = 0
#                 tmp_names = []
#                 name_indx = 0
#                 while (name_indx < per_page) & (tmp_cnt < len(links)):
#                     tmp_terms = links[name_indx]
#                     if tmp_terms not in tmp_names:
#                         tmp_names.append(tmp_terms)
#                         tmp_URL = mainWikiURL % template_wikiURL % tmp_terms
#                         inside_html, inside_links = getLinks(tmp_URL)
#                         if terms in inside_links:
#                             list_of_names.extend([tmp_terms])
#                             name_indx += 1
#                     tmp_cnt += 1
#             except:
#                 list_of_names.extend(['']*per_page)
#             list_of_hit.append(terms)
#             print 'Starting Iteration %d' % len(list_of_hit)
#         print list_of_names
#         count += 1
#
#     return list_of_names
