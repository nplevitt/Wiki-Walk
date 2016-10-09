
with open('Microorganism_Graph.txt', 'r') as f:
    graph = f.read().split('\t')

node_picks = list(set([e for e in graph if e != 'abcdefg']))
html_list = """"""
for element in node_picks:
    html_list = html_list + '<option value="%s">%s</option>' % (element, element)

with open('html_select.txt', 'w') as f:
    f.write(html_list)