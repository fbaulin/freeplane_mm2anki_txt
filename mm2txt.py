""" freeplane mindmaps to anki flashcards """
import csv
import re
import sys
from xml.etree import ElementTree as et


PARSE_MODE = 'STYLE'                            # parsing mode TEXT or STYLE
EXCLUDE_CONDITION = 'defaultstyle.floating'     # names of the style or node texts preference
JOIN_UPSTREAM = 'styles.subtopic'               # name of the style or node text prefix
TXT_TEMPLATE = '<div align="left">{0}</div>	<div align="left">{1}</div>'


def auto_init(filename):
    with open(filename,'r') as f:
        txt = f.read()
        global PARSE_MODE
        global EXCLUDE_CONDITION
        global JOIN_UPSTREAM
        if len(re.findall('TEXT=":ex ', txt)) >= 6 or (len(re.findall('TEXT=": ', txt)) >= 3 and 
        len(re.findall('="styles.subtopic"', txt)) <= 3 and 
        len(re.findall('="defaultstyle.floating"', txt)) <= 3):
            PARSE_MODE = 'TEXT'
            EXCLUDE_CONDITION = ':ex'
            JOIN_UPSTREAM = ':'
        else:
            PARSE_MODE = 'STYLE'
            EXCLUDE_CONDITION = 'defaultstyle.floating'
            JOIN_UPSTREAM = 'styles.subtopic'
        print('Automatic setup: \n\tmode: {}\n\texluding rule: {}\n\textra upstream node: {}'.format(PARSE_MODE,EXCLUDE_CONDITION,JOIN_UPSTREAM))

def node_keep(nodes):
    if PARSE_MODE == 'STYLE': 
        attr = 'LOCALIZED_STYLE_REF'
    elif PARSE_MODE == 'TEXT': 
        attr = 'TEXT'
    else: 
        raise ValueError(f'PARSE_MODE is {PARSE_MODE}, but should be STYLE or TEXT')
    if isinstance(nodes, list):
        return [node for node in nodes if nodes.attrib.get(attr, None) != EXCLUDE_CONDITION]
    return nodes.attrib.get(attr, None) != EXCLUDE_CONDITION

def node_front_cat(root, node):
    if PARSE_MODE == 'STYLE': 
        filt = lambda n: n.attrib.get('LOCALIZED_STYLE_REF', None) == JOIN_UPSTREAM
    elif PARSE_MODE == 'TEXT':
        filt = lambda n: n.attrib.get('TEXT', None).startswith(JOIN_UPSTREAM)
    else: 
        raise ValueError(f'PARSE_MODE is {PARSE_MODE}, but should be STYLE or TEXT')
    text = [node.attrib.get('TEXT', None)]
    while filt(node):
        node = root.find('.//node[@ID="{}"]/..'.format(node.attrib['ID']))
        text.insert(0, node.attrib['TEXT'])
    if PARSE_MODE == 'STYLE':
        return ': '.join(text)
    else: 
        return ''.join(text)

def node_back_cat_byte(node):
    body = et.tostring(node.find('.//body'), method="html")
    breg = re.sub('\n {0,}','',body[6:-8].decode("utf-8"))
    return breg

def node_back_cat(node):
    lines = [subnode.text for subnode in node.findall('./richcontent[@TYPE="DETAILS"]/html//p')]
    lines = '<br>'.join(map(lambda l: re.sub('\n {0,}','',l), lines))
    return lines

def xml_decoder(filename):
    tree=et.parse(filename)
    root=tree.getroot()
    nodes_with_details=[node for node in root.findall('.//node/richcontent[@TYPE="DETAILS"]/..') if node_keep(node)]
    fronts = [None]*len(nodes_with_details)
    backs = [None]*len(nodes_with_details)
    for i, node in enumerate(nodes_with_details):
        # fronts[i] = node.attrib.get('TEXT','NO_TEXT')
        fronts[i] = node_front_cat(root, node)
        backs[i] = node_back_cat(node)
    return zip(fronts, backs)

def csv_encoder(filename, deck_pairs):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        for row in deck_pairs:
            writer.writerow(row)

def txt_encoder(filename, deck_pairs):
    with open(filename,'w', encoding="utf-8") as f:
        for a, b in deck_pairs:
            print(TXT_TEMPLATE.format(a,b), file=f)

def main(filename='default.mm', parse_mode=None):
    # if filename is 
    if parse_mode is None:
        auto_init(filename)
    deck = xml_decoder(filename)
    txt_encoder(filename+'_deck.txt', deck)
    print(*deck, sep='\n')
    return 0

if __name__ == "__main__":
    n_args = len(sys.argv)-1
    if n_args==1:
        status=main(sys.argv[1])
    else:
        status=main()
    sys.exit(status)
