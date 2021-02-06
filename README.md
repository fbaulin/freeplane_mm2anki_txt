# freeplane_mm2anki_txt
## Summary
Basic python script to transform freeplane mindmaps to txt, that can be easily imported to anki. Using only standard python libs. Currently only text file output is supported, so you'll need anki on your pc to import data. After importing you can syncronize your library or export the apkg deck.

## Basic operation
Program takes mind map and turns the nodes with details into anki flash cards. You can choose wich nodes you don't want to import by applying specific node styles (default is floating) or adding a prefix to node name (default is :ex). You can add prefixes to prevent ambiguity front question by defining style of node (default is subtopic) or adding prefix to node name (default is :). In that card question will be prefixed by the parent node name.

Basic sequence is:
1. Make a mindmap and format it; for instance 'mymap.mm'.
2. Run program with parameters (parameters go first in a group after '-') and arguments (after parameters in order filename, exclude condition, join condition). To parse mymap.mm in which nodes are marked with styles ("subtopic" for adding parental node name to question and floating for excluded nodes)
    `python mm2txt.py -s "C:\mind maps\mymap.mm"`
3. As result you get txt file in the directory of input file. The fronts and backs are separated by tab. Use anki desktop application to import as text file (don't forget to specify the deck, where you want to add new cards, and tab as separator).
Now you have your deck in anki - you can either sync or just export apkg.

## Mind map format
Input is a freemind xml-stile *.mm file.

## Output text file format
Text file. Each line contains a card, fronts and backs are separated by tabs.

## Appendix - docstring from code
 Example:
    python mm2txt.py [-id] filename [exclude_condition [join_condition]]

    outputs file with filename_deck.txt is in same directory as the source mindmap
    (import in anki as text file with tab separated cards and html support)

    OPTIONS: 
    -t  text mode of parsing
    -s  style mode of parsing
    -i  inverse cards
    -d  doublicate inversed cards
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