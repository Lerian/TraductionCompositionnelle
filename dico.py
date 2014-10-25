#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs

# pour exécuter :
# python dico.py dicfrenelda-utf8.txt dico.txt

def main(argv) :

    if len(argv) != 1:
        print "Usage : dico.py dicfrenelda-utf8.txt"
        sys.exit()
    newdico = Dico(argv[0])
    firstKey=newdico.FrEn.keys()[0]
    print firstKey
    print newdico.FrEn[firstKey]



def add_translation(dic, key,value):
    if not dic.has_key(key):
        dic[key] = [value]
    else:
      dic[key].append(value)




class Dico():
    #-T-----------------------------------------------------------------------T-
  def __init__(self,ifilePath):
    self.FrEn = {}
    self.EnFr = {}
    self.filePath = ifilePath
    self.remplirDicos()
    print "Dictionnaire extrait"
    print "%d clés FR-EN" % len(self.FrEn.keys())
    print "%d clés EN-FR" % len(self.EnFr.keys())

  def remplirDicos(self):
    fichier = codecs.open(self.filePath, "r", encoding='utf-8')
    for line in fichier.readlines():
      lineTab = line.split(";")
      add_translation(self.FrEn, lineTab[0],lineTab[3])
      add_translation(self.EnFr, lineTab[3],lineTab[0])
    fichier.close()

  def nettoyageDico(self,inputFilePath, outputFilePath):
    fichier = codecs.open(inputFilePath, "r", encoding='utf-8')
    out = open(outputFilePath,"w")
    for line in fichier.readlines():
      lineTab = line.split(";")
      out.write(lineTab[0]+";"+lineTab[2]+";"+lineTab[3]+"\n ")
    fichier.close()
    out.close()
  
  def simplificationDicoFR(self, filterSet):
    for x in self.FrEn.keys():
      if x not in filterSet:
        del self.FrEn[x]
    print "Dictionnaire simplifié"
    print "%d clés FR-EN" % len(self.FrEn.keys())

if __name__ == "__main__":
  main(sys.argv[1:])
