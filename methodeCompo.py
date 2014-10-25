#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.sax
import sys
from dico import Dico
import itertools
import codecs

# pour exécuter :
# python methodeCompo.py acabit_fr.xml dicfrenelda-utf8.txt acabit_en.xml

def main(argv) :

    if len(argv) != 3:
        print "Usage : methodeCompo.py acabit_fr.xml dicfrenelda-utf8.txt acabit_en.xml"
        sys.exit()
    
    terms_fr = fr_content_handler(argv[0])
    dico = Dico(argv[1])
    
    # Suppression des entrées FR inutiles dans le dictionnaire
    french_words = set()
    for key in terms_fr.mwts.keys():
        for x in terms_fr.mwts[key][2]:
            french_words.add(x)
    dico.simplificationDicoFR(french_words)
    french_words.clear()

    terms_en = en_content_handler(argv[2])
    writer = output_writer("outputs")

    print "%d termes complexes à traduire" % len(terms_fr.mwts.keys())
    
    # tri des MWTs entièrement traduisibles et identification des modifications à faire via la morphologie
    
    translatable_terms = {}
    untranslatable_terms = {}
    
    morphology_candidats = []

    for key in terms_fr.mwts.keys():
        missing_trad = False
        if terms_fr.mwts[key][1] == "NA":
            morphology_candidats.append(key)
        for subword in terms_fr.mwts[key][2]:
            if subword not in dico.FrEn:
                missing_trad = True
        if missing_trad:
            untranslatable_terms[key] = terms_fr.mwts[key]
        else:
            translatable_terms[key] = terms_fr.mwts[key]

    print "%d termes complexes directement traduisibles" % len(translatable_terms.keys())
    print "%d termes complexes non directement traduisibles" % len(untranslatable_terms.keys())

    print "%d termes complexes à transformer via la morphologie" % len(morphology_candidats)
    
    # génération des nouveaux MWTs via la méthode basée sur la morphologie
    
    

    # Suppression des MWTs FR de plus de 2 mots pleins
    stopwords = read_stopwords()
    for key in translatable_terms.keys():
        plain_words_count = len(translatable_terms[key][2])
        for word in translatable_terms[key][2]:
            if word in stopwords:
                plain_words_count -= 1
        if plain_words_count > 2:
            del translatable_terms[key]
    
    print "%d termes complexes de 2 mots pleins max à traduire" % len(translatable_terms.keys())
    
    # Ajout de la traduction vide pour les stopwords
    
    for stop in stopwords:
        if dico.FrEn.has_key(stop):
            dico.FrEn[stop].append('')
    
    # traduction mot à mot FR-EN
    translated_terms = {}

    for key in translatable_terms.keys():
        translated_terms[key] = {}
        for subword in translatable_terms[key][2]:
            translated_terms[key][subword] = dico.FrEn[subword]
    
    #translations = {}
    
    print "Début de la génération des traductions"
    fichier_trads = open("outputs/Translations_direct","w")
    trads_number = len(translated_terms.keys())
    
    idxTrad = {}
    for x in terms_en.mwts.keys():
        if idxTrad.has_key(x[0].upper()):
            idxTrad[x[0].upper()].append(x)
        else:
            idxTrad[x[0].upper()] = [x]
    
    #translated_terms = {'cancer du sein': {'cancer':['cancer', 'pouet'],'du':[''],'sein':['breast']}}
    #print translated_terms.keys()[10]
    mwts_without_trad = 0
    for i, key in enumerate(translated_terms.keys()[:]): # pour tous les mwt
        msg = "%s :\n" % key
        fichier_trads.write(msg.encode('utf8'))
        #print "Trad %d/%d : %s" % (i+1,trads_number,key)
        sys.stdout.flush()
        sys.stdout.write("\r%d/%d : %s                      " % (i+1,trads_number,key))
        sys.stdout.flush()
        subtrads = []
        for subword in translated_terms[key].keys():    # pour tous les sous mots fr
            subtrads.append(translated_terms[key][subword])
        #print subtrads
        trads = []
        freqs = {}
        for t in itertools.product(*subtrads):
            for p in itertools.permutations(t, len(translated_terms[key].keys())):
                #print p
                trad = ''
                for word in p:
                    if word != '':
                        trad = trad+word+" "
                trad = trad.strip()
                #trad = ''.join(trad)
                #print trad
                #print type(trad)
                if len(trad) > 0:
                    if idxTrad.has_key(trad[0].upper()):
                        if trad in idxTrad[trad[0].upper()] and trad not in trads:
                            trads.append(trad)
                            if freqs.has_key(terms_en.mwts[trad][0]):
                                freqs[terms_en.mwts[trad][0]].append(trad)
                            else:
                                freqs[terms_en.mwts[trad][0]] = [trad]
        #translations[key] = trads
        #print trads
        keys = freqs.keys()
        keys.sort()
        keys.reverse()
        for k in keys:
            msg = ""
            for w in freqs[k]:
                msg = msg+"\t%d %s\n" % (k,w)
            fichier_trads.write(msg.encode('utf8'))
        if len(keys) == 0:
            mwts_without_trad += 1
        #print "\tDone"
    
    # écriture des traductions dans un fichier
    fichier_trads.close()
    
    print "\n%d termes complexes avec une traduction proposée" % (trads_number-mwts_without_trad)


################################################################################
# Fonction de lecture des fichiers contenant les stopwords
################################################################################
def read_stopwords():
    stops = []
    fichier = codecs.open("stopwords/stopword.txt", "r", encoding='utf-8')
    for line in fichier:
        if line not in stops:
            stops.append(line.strip('\n'))
    fichier.close()
    fichier = codecs.open("stopwords/other_stopword.txt", "r", encoding='utf-8')
    for line in fichier:
        if line not in stops:
            stops.append(line.strip('\n'))
    fichier.close()
    
    return stops

################################################################################
# Writer storing results in files
################################################################################
class output_writer():
    def __init__(self, path):
        # path to the directory where the files will be stored
        self.path = path
    
    def writeMWTs(self, mwts):
        output = open(self.path+"/MWTs","w")
        
        output.write("Number of MWTs: %d\n" % len(mwts.keys()))
        output.write("===============================\n\n")
        
        for key in mwts.keys():
            msg = "%s : %d\n" % (key, mwts[key][0])
            output.write(msg.encode('utf8'))
            for sub in mwts[key][1]:
                msg = "\t%s\n" % sub
                output.write(msg.encode('utf8'))
            output.write("------------------------\n")
        
        output.close()
        
    def writeMWTsWithoutHapax(self, mwts):
        output = open(self.path+"/MWTsWithoutHapax","w")
        
        output.write("Number of MWTs: %d\n" % len(mwts.keys()))
        output.write("===============================\n\n")
        
        for key in mwts.keys():
            msg = "%s : %d\n" % (key, mwts[key][0])
            output.write(msg.encode('utf8'))
            for sub in mwts[key][1]:
                msg = "\t%s\n" % sub
                output.write(msg.encode('utf8'))
            output.write("------------------------\n")
        
        output.close()
        
    def writeTranslatableTerms(self, mwts):
        output = open(self.path+"/TranslatableMWTs","w")
        
        output.write("Number of MWTs: %d\n" % len(mwts.keys()))
        output.write("===============================\n\n")
        
        for key in mwts.keys():
            msg = "%s : %d\n" % (key, mwts[key][0])
            output.write(msg.encode('utf8'))
            for sub in mwts[key][1]:
                msg = "\t%s\n" % sub
                output.write(msg.encode('utf8'))
            output.write("------------------------\n")
        
        output.close()
        
    def writeUntranslatableTerms(self, mwts):
        output = open(self.path+"/UntranslatableMWTs","w")
        
        output.write("Number of MWTs: %d\n" % len(mwts.keys()))
        output.write("===============================\n\n")
        
        for key in mwts.keys():
            msg = "%s : %d\n" % (key, mwts[key][0])
            output.write(msg.encode('utf8'))
            for sub in mwts[key][1]:
                msg = "\t%s\n" % sub
                output.write(msg.encode('utf8'))
            output.write("------------------------\n")
        
        output.close()
        
    def writeTranslatedTerms(self, translated_MWTs):
        output = open(self.path+"/TranslatedMWTs","w")
        
        output.write("Number of MWTs: %d\n" % len(translated_MWTs.keys()))
        output.write("===============================\n\n")
        
        for key in translated_MWTs.keys():
            msg = "%s :\n" % key
            output.write(msg.encode('utf8'))
            for sub in translated_MWTs[key].keys():
                msg = "\t%s\n" % sub
                output.write(msg.encode('utf8'))
                for trad in translated_MWTs[key][sub]:
                    msg = "\t\t%s\n" % trad
                    output.write(msg.encode('utf8'))
            output.write("------------------------\n")
        
        output.close()


################################################################################

################################################################################
# XML Sax Parser for ACABIT xml file
################################################################################
class fr_content_handler(xml.sax.ContentHandler):
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
        self.current_type = ""
        
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
                self.current_type = name
                #print "%d %s" % (self.current_freq, name)
        
        if name == 'BASE':
            if self.current_freq > 1:
                self.isBase = True

        elif name in ['MODIF','COORD', 'ATTR']:
            if self.current_freq > 1:
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
                    self.mwts[self.current_base.strip()] = (self.current_base_freq, self.current_type, self.current_base.split())
                elif self.current_modif != "":
                    # ajouter la modif
                    self.mwts[self.current_modif.strip()] = (self.current_modif_freq, self.current_type, self.current_modif.split())
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

        elif tag in ['MODIF','COORD','ATTR']:
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
                if self.current_freq > 1:
                    print "Le TERM %s n'est ni une base, ni une modif" % self.buffer

        # Flush the buffer
        self.buffer = ''
    #-B-----------------------------------------------------------------------B-
    
    
class en_content_handler(xml.sax.ContentHandler):
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
        self.current_type = ""
        
        
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
                self.current_type = name
        
        if name == 'BASE':
            self.isBase = True

        elif name in ['MODIF','COORD', 'ATTR']:
            self.isModif = True
    #-B-----------------------------------------------------------------------B-
        
    #-T-----------------------------------------------------------------------T-
    def characters(self, data):
        self.buffer += data.strip()
    #-B-----------------------------------------------------------------------B-
        
    #-T-----------------------------------------------------------------------T-
    def endElement(self, name):
        tag, attrs = self.tree.pop()
        
        if tag == 'BASE':
            if self.mwtFound:
                if self.current_base != "":
                    # ajouter la base
                    self.mwts[self.current_base.strip()] = (self.current_base_freq, self.current_type, self.current_base.split())
                self.mwtFound = False
                self.current_base = ""
                self.current_base_freq = 0
                self.current_term = ""
            self.isBase = False

        elif tag in ['MODIF','COORD','ATTR']:
            if self.mwtFound:
                if self.current_modif != "":
                    # ajouter la modif
                    self.mwts[self.current_modif.strip()] = (self.current_modif_freq, self.current_type, self.current_modif.split())
                self.mwtFound = False
                self.current_modif = ""
                self.current_modif_freq = 0
                self.current_term = ""
            self.isModif = False

        elif tag == 'TERM':
            if self.isBase:
                #if self.current_freq > self.current_base_freq:
                self.current_base_freq = self.current_freq
                self.current_base = self.buffer
                self.mwtFound = True
            elif self.isModif:
                #if self.current_freq > self.current_modif_freq:
                self.current_modif_freq = self.current_freq
                self.current_modif = self.buffer
                self.mwtFound = True
            else:
                if self.current_freq > 1:
                    print "Le TERM %s n'est ni une base, ni une modif" % self.buffer

        # Flush the buffer
        self.buffer = ''
################################################################################



if __name__ == "__main__":
    main(sys.argv[1:])
