""" freeplane mindmaps to anki flashcards """
import csv
import re
import sys
from xml.etree import ElementTree as et


PARSE_MODE = 'STYLE'                            # parsing mode TEXT or STYLE
EXCLUDE_CONDITION = 'defaultstyle.floating'     # names of the style or node texts preference
JOIN_UPSTREAM = 'styles.subtopic'               # name of the style or node text prefix
TXT_TEMPLATE = '<div align="left">{0}</div>\t<div align="left">{1}</div>'


def auto_mode_select(filename):
    with open(filename,'r') as f:
        txt = f.read()
        if len(re.findall('TEXT=":ex ', txt)) >= 6 or (len(re.findall('TEXT=": ', txt)) >= 3 and 
        len(re.findall('="styles.subtopic"', txt)) <= 3 and 
        len(re.findall('="defaultstyle.floating"', txt)) <= 3):
            mode = 'TEXT'
        else:
            mode = 'STYLE'
        print('Automatic mode selection')
        return mode

def parse_init(parse_mode='TEXT', join_condition=None, exclude_condition=None):
    if parse_mode not in ['TEXT', 'STYLE']:
        raise ValueError('Unsupported mode of parsing')
    global PARSE_MODE
    global EXCLUDE_CONDITION
    global JOIN_UPSTREAM
    PARSE_MODE = parse_mode
    if isinstance(join_condition, str):
        JOIN_UPSTREAM = join_condition
    else:
        JOIN_UPSTREAM = ':' if parse_mode == 'TEXT' else 'styles.subtopic'
    if isinstance(exclude_condition, str):
        EXCLUDE_CONDITION = exclude_condition
    else:
        EXCLUDE_CONDITION = ':ex' if parse_mode == 'TEXT' else 'defaultstyle.floating'
    print('Parse setup: \n\tmode: {}\n\texluding rule: {}\n\textra upstream node: {}'.format(PARSE_MODE,EXCLUDE_CONDITION,JOIN_UPSTREAM))



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

def main():
    """ Transform freeplane mindmaps to text for anki import
    example:
    python mm2txt.py [-idt] filename [exclude_condition [join_condition]]

    outputs file with filename_deck.txt is in same directory as the source mindmap
    (import in anki as text file with tab separated cards and html support)

    OPTIONS: 
    -t  text mode of parsing
    -s  style mode of parsing
    -i  inverse cards
    -d  doublicate inversed cards (works only with i)
    PARAMETERS:
    filename          - name of freeplane mindmap file
    exclude_condition - text prefix in node name (or style) of nodes you want to exclude from decks
                        (use only with manual selection of parsing mode with -t or -s). 
                        Lookup style names in the xml text of mindmap.
    join_condition    - text prefix in node name (or style) of nodes you want to join with parent node text
                        in order to support more info for insufficient 
                        (use only with manual selection of parsing mode with -t or -s).
                        Lookup style names in the xml text of mindmap.
    
    всем добра
    """
    filename = None
    parse_mode = None
    inverse = False
    doublicate = False
    join_condition = None
    exclude_condition = None

    n_args = len(sys.argv)-1
    if n_args >= 1:     # aditional args
        shell_args = sys.argv[1:]
        # options section
        if shell_args[0].startswith('-'):       # there are options
            options = shell_args.pop(0)[1:]     # extract options
            n_args -= 1                         # 1st arg was option
            if 't' in options or 's' in options:    # if parsing mode specified
                parse_mode = 'STYLE' if 's' in options else 'TEXT'  # set mode
            inverse = True if 'i' in options else False
            doublicate = True if 'd' in options else False
        filename = shell_args[0] if n_args > 0 else 'default.mm'
        exclude_condition = shell_args[1] if n_args > 1 else None
        join_condition = shell_args[2] if n_args > 2 else None
        
    else:
        print
        print(main.__doc__)
        return 1

    if parse_mode is None:
        parse_mode = auto_mode_select(filename)
    parse_init(parse_mode, join_condition, exclude_condition)
    deck = xml_decoder(filename)
    if inverse:
        deck = list(deck).extend(list(map(reversed,deck))) if doublicate else list(map(reversed,deck))
    txt_encoder(filename+'_deck.txt', deck)
    return 0


if __name__ == "__main__":
    status=main()
    sys.exit(status)
