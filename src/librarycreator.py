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

def write_xmlstring_to_file(xmlstring: str, outfilename: str):
    """Write a given XML string to a file in the target directory"""
    outfile = path.join(targetdir, outfilename)
    with open(outfile, 'a') as out:
        out.write(xmlstring)

def create_b64string(path: Path):
    """Create a b64 string from a given file"""
    with open(path, 'rb') as f:
        encodedSVG = b64encode(f.read())
        return encodedSVG.decode()

def create_jsonstring(b64string: str, title: str):
    return f"""{{"data": "data:image/svg+xml;base64,{b64string}", "w": 64, "h": 64, "title": "{title}"}}"""

# clean up previous instances of library files
for f in listdir(targetdir):
    remove(path.join(targetdir, f))

# Download and unzip latest release of tactical signs
zipurl = 'https://github.com/jonas-koeritz/Taktische-Zeichen/releases/latest/download/release.zip'
with urlopen(zipurl) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(signdir)

# Assumed directory structure for library building: taktischezeichen/svg/ holds
# several folders, each folder contains one or more svg files representing a #
# tactical sign, the subdir "Schadenskonten" has 3 subdirs, 'weiß', 'gelb' and
# 'rot'

special_subdirs = ['gelb', 'rot', 'weiß']

for cwd, dirs, files in walk(path.join(signdir, 'svg'), topdown=True):
    jsonstringlist = []
    outfilename = ''
    title = ''
    for file in files:
        if any(x in cwd for x in special_subdirs):
            outfilename = cwd.lower().split('/')[-2] + '.xml'
            title = cwd.lower().split('/')[-1] + '_' + file.split('.')[0]
        else:
            outfilename = cwd.lower().split('/')[-1] + '.xml'
            title = file.split('.')[0]

        b64string = create_b64string(path.join(cwd, file))
        jsonstringlist.append(create_jsonstring(b64string, title))

    xmlstring = f"""<mxlibrary>[{','.join(jsonstringlist)}]</mxlibrary>\n"""

    if outfilename:
        write_xmlstring_to_file(xmlstring, outfilename)

# clean up previously used sign files
rmtree(signdir)
