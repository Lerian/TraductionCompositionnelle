#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.sax
import sys


# pour exécuter :
# python methodeCompo.py acabit_fr.xml

def main(argv) :

    if len(argv) != 1:
        print "Usage : methodeCompo.py acabit_fr.xml"
        sys.exit()
    
    termes = content_handler(argv[0])
    
    print "MWTs:"
    print"-------------------------"
    print termes.mwts.keys()[0]
    print termes.mwts[termes.mwts.keys()[0]]


################################################################################
# XML Sax Parser for ACABIT xml file
################################################################################
class content_handler(xml.sax.ContentHandler):
    #-T-----------------------------------------------------------------------T-
    def __init__(self, path):
        # Tree for pushing/poping tags, attrs
        self.tree = []
        
        # Buffer for xml element
        self.buffer = ''

        # Container for the MWT list
        self.mwts = {}
        self.current_base = ""
        self.current_base_freq = 0
        self.current_modif = ""
        self.current_modif_freq = 0
        self.current_term = ""
        
        self.current_freq = 0
        self.isBase = False
        self.isModif = False
        
        self.mwtFound = False

        # Construct and launch the parser
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(path)
    #-B-----------------------------------------------------------------------B-
        
    #-T-----------------------------------------------------------------------T-
    def startElement(self, name, attrs):
        self.tree.append((name, attrs))
        
        if name != 'SETCAND':
            if "freq" in attrs.getNames():
                self.current_freq = int(attrs.getValue("freq"))
                #print "%d %s" % (self.current_freq, name)
        
        if name == 'BASE':
            self.isBase = True

        elif name == 'MODIF' or name == 'COORD' or name == 'ENUM':
            self.isModif = True
    #-B-----------------------------------------------------------------------B-
        
    #-T-----------------------------------------------------------------------T-
    def characters(self, data):
        self.buffer += data.strip()
    #-B-----------------------------------------------------------------------B-
        
    #-T-----------------------------------------------------------------------T-
    def endElement(self, name):
        tag, attrs = self.tree.pop()
        
        if tag == 'CAND':
            
            if self.mwtFound:
                if self.current_base != "":
                    # ajouter la base
                    self.mwts[self.current_base] = (self.current_base_freq, self.current_base.split())
                elif self.current_modif != "":
                    # ajouter la modif
                    self.mwts[self.current_modif] = (self.current_modif_freq, self.current_modif.split())
                self.mwtFound = False
        
            self.current_base = ""
            self.current_base_freq = 0
            self.current_modif = ""
            self.current_modif_freq = 0
            self.current_term = ""
            self.isBase = False
            self.isModif = False
        
        elif tag == 'BASE':
            self.isBase = False

        elif tag == 'MODIF' or tag == 'COORD' or tag == 'ENUM':
            self.isModif = False

        elif tag == 'TERM':
            if self.isBase:
                if self.current_freq > self.current_base_freq:
                    self.current_base_freq = self.current_freq
                    self.current_base = self.buffer
                    self.mwtFound = True
            elif self.isModif:
                if self.current_freq > self.current_modif_freq:
                    self.current_modif_freq = self.current_freq
                    self.current_modif = self.buffer
                    self.mwtFound = True
            else:
                print "Le TERM %s n'est ni une base, ni une modif" % self.buffer

        # Flush the buffer
        self.buffer = ''
    #-B-----------------------------------------------------------------------B-
################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
