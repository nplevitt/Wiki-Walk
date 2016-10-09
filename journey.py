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
from getWikiSubset import *
import time
from selenium import webdriver
from Tkinter import *
#

def highlight(element):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                              element, s)
    original_style = element.get_attribute('style')
    apply_style("background: yellow; border: 2px solid red;")


driver = webdriver.Chrome('/usr/local/bin/chromedriver')  # Optional argument, if not specified will search path.
mainWikiURL = "https://en.wikipedia.org%s"
template_wikiURL = "/wiki/%s"
#
with open('Microorganism_Graph.txt', 'r') as f:
    graph = f.read().split('\t')

node_picks = list(set([e for e in graph if e != 'abcdefg']))
start_node = end_node = node_picks[random.randint(0, len(node_picks)-1)]
while end_node == start_node:
    end_node = node_picks[random.randint(0, len(node_picks)-1)]

paths = get_all_paths(graph, start_node, end_node, 5)
path_lengths = [len(p) for p in paths]
shortest_path = paths[path_lengths.index(min(path_lengths))]

print shortest_path

start_URL = mainWikiURL % template_wikiURL % shortest_path[0]
driver.get(start_URL)
#
for step in shortest_path[1:]:
    time.sleep(2.5)
    element = driver.find_elements_by_xpath('//a[@href="%s"]' % template_wikiURL % step)[0]
    driver.execute_script("return arguments[0].scrollIntoView();", element)
    time.sleep(.5)
    highlight(element)
    time.sleep(2)
    try:
        element.click()
    except:
        driver.get(mainWikiURL % template_wikiURL % step)






# shortest_path = shortest_path[1:]
#
# shortest_path = ['Flag_of_Washington',
#                  'Roland_H._Hartley',
#                  'Republican_Party_(United_States)',
#                  'Donald_Trump',
#                  'Mike_Tyson_vs._Michael_Spinks',
#                  'Oprah_Winfrey']