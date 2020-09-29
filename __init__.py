# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
import locale
import os
#import resources


#support for multiple languages
translator = QTranslator(QCoreApplication.instance())
localeCode = QLocale.system().name()
if localeCode:
    translator.load("calcarea_" + localeCode + ".qm",  os.path.dirname(__file__))
    QCoreApplication.instance().installTranslator(translator)

def name():
    return QCoreApplication.translate("init","CalcArea Plugin")

def description():
    return QCoreApplication.translate("init","Calculate the Area while editing.")

def icon():
	return "CalcArea.png"

def version():
    return "1.2.2"

def qgisMinimumVersion():
  return "2.0"

#def category():
#  return "Database"

def classFactory(iface):
    from calcareaMain import calcareaMain
    return calcareaMain(iface)
