
with open('Full_Graph_400.txt', 'r') as f:
    graph = f.read().split('\t')

node_picks = set([e for e in graph if e != 'abcdefg'])
html_list = """"""
for element in sorted(node_picks):
    html_list = html_list + '<option value="%s">%s</option>\n' % (element, element)

with open('html_select_full.txt', 'w') as f:
    f.write(html_list)