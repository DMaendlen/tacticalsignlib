#!/usr/bin/python3
"""Create draw.io libraries for tactical signs from Jonas Koeritz' github repo"""


from base64 import b64encode
from io import BytesIO
from os import listdir, path, remove, walk
from pathlib import Path
from shutil import rmtree
from urllib.request import urlopen
from zipfile import ZipFile

targetdir  = Path('../libfiles')
signdir = Path('taktischezeichen')

def write_xmlstring_to_file(xml: str, outfile: str):
    """Write a given XML string to a file in the target directory"""
    outfile = path.join(targetdir, outfile)
    with open(outfile, 'a', encoding='utf-8') as out:
        out.write(xml)

def create_b64string(filepath: Path):
    """Create a b64 string from a given file"""
    with open(filepath, 'rb') as readfile:
        return b64encode(readfile.read()).decode()

def create_jsonstring(b64: str, signtitle: str):
    """Create the json string expected by draw.io / diagrams.net with a given
    b64 representation of a file and a title, width and height are fixed to 64px
    (can be dynamically changed in the diagram)"""

    return f"""{{"data": "data:image/svg+xml;base64,{b64}", "w": 64, "h": 64, "title": "{signtitle}"}}"""

# clean up previous instances of library files
for f in listdir(targetdir):
    remove(path.join(targetdir, f))

# Download and unzip latest release of tactical signs
ZIPURL = 'https://github.com/jonas-koeritz/Taktische-Zeichen/releases/latest/download/release.zip'
with urlopen(ZIPURL) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
        zfile.extractall(signdir)

# Assumed directory structure for library building: taktischezeichen/svg/ holds
# several folders, each folder contains one or more svg files representing a #
# tactical sign, the subdir "Schadenskonten" has 3 subdirs, 'weiß', 'gelb' and
# 'rot'

special_subdirs = ['gelb', 'rot', 'weiß']

for cwd, dirs, files in walk(path.join(signdir, 'svg'), topdown=True):
    jsonstringlist = []
    OUTFILENAME = ''
    TITLE = ''
    for file in files:
        # handle subdirs to make sure we have 1 'Schadenskonten' XML file
        if any(x in cwd for x in special_subdirs):
            OUTFILENAME = cwd.lower().split('/')[-2] + '.xml'
            TITLE = cwd.lower().split('/')[-1] + '_' + file.split('.')[0]
        else:
            OUTFILENAME = cwd.lower().split('/')[-1] + '.xml'
            TITLE = file.split('.')[0]

        b64string = create_b64string(path.join(cwd, file))
        jsonstringlist.append(create_jsonstring(b64string, TITLE))

    xmlstring = f"""<mxlibrary>[{','.join(jsonstringlist)}]</mxlibrary>\n"""

    # ensure we only write stuff if we're not in the root directory containing no files
    if files:
        write_xmlstring_to_file(xmlstring, OUTFILENAME)

# clean up previously used sign files
rmtree(signdir)
