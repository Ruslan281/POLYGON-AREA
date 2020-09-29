from PyQt4 import QtCore, QtGui
from qgis.gui import *
from qgis.core import *


import resources, math, copy

from mainWindow import *




class calcareaMain( QtGui.QWidget):
    def __init__(self,iface):

        QtGui.QWidget.__init__(self)

       
        self.iface = iface
        self.mc = self.iface.mapCanvas()    

        self.layer = QgsVectorLayer()

        self.maptool = QgsMapTool(self.mc)     
        self.grafArea = QgsDistanceArea()
        self.DialogDock = QtGui.QDockWidget()
        self.Dialog = QtGui.QDialog()
        self.cpoint_list = []
        self.end = False


      
    def initGui(self):

        self.actionCalcArea = QtGui.QAction( QtGui.QIcon(":/plugins/CalcArea/CalcArea.png"),  QtCore.QCoreApplication.translate("calcareaMain", "Calculate the Area while editing. Best with Plugin Improved Polygon Capturing."),  self.iface.mainWindow() )
        QtCore.QObject.connect(self.actionCalcArea, QtCore.SIGNAL("triggered()"), self.showMainWindow)

        self.iface.addToolBarIcon( self.actionCalcArea )
        self.iface.addPluginToVectorMenu(QtCore.QCoreApplication.translate("calcareaMain",  "Calculate area while editing"),  self.actionCalcArea)


  
    def showMainWindow(self):


        if not self.mc.mapUnits() == 0:
            QtGui.QMessageBox.critical(None, QtCore.QCoreApplication.translate("calcareaMain","Wrong Units!"),QtCore.QCoreApplication.translate("calcareaMain",'The Plugin needs metrical Units!'))
            return

        if self.iface.mainWindow().findChild(QtGui.QDockWidget,'CalcArea DialogDock') == None:

            self.Dialog = CalcAreaDialog()
            self.DialogDock = QtGui.QDockWidget('Calc Area', self.iface.mainWindow())
            self.DialogDock.setWidget(self.Dialog)

            self.DialogDock.setObjectName('CalcArea DialogDock')
            self.Dialog.setObjectName('CalcArea Dialog')

        else:
            return

        self.iface.mainWindow().addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.DialogDock)
        self.DialogDock.show()

       
        self.DialogDock.installEventFilter(self)




       
        QtCore.QObject.connect(self.mc, QtCore.SIGNAL("mapToolSet (QgsMapTool *, QgsMapTool *)"), self.digklick)

        
        QtCore.QObject.connect(self.iface, QtCore.SIGNAL("currentLayerChanged (QgsMapLayer *)"), self.switch_layer)

        
        self.maptool = self.mc.mapTool()

      
        if self.mc.mapTool().isEditTool():
            self.digklick(self.mc.mapTool().isEditTool(), None)

        self.switch_layer(self.mc.currentLayer())

       
        self.iface.mapCanvas().viewport().installEventFilter( self)


   
    def unload(self):


       
        self.Dialog = None
        self.iface.mainWindow().removeDockWidget(self.DialogDock)
        self.DialogDock = None

      
        self.iface.removePluginMenu(u"&CalcArea", self.actionCalcArea)
        self.iface.removeToolBarIcon(self.actionCalcArea)


    
    def area(self,feat):

        self.Dialog.lblQuadratmeter.setText(str(round(self.grafArea.measureArea(feat),2)) + ' m²'.decode('utf8'))
        self.Dialog.lblHektar.setText(str(round(self.grafArea.measureArea(feat)/10000,2)) + ' ha'.decode('utf8'))
        self.Dialog.lblQuadratkilometer.setText(str(round(self.grafArea.measureArea(feat)/1000000,2)) + ' km²'.decode('utf8'))


        self.Dialog.lblMeter.setText(str(round(self.grafArea.measurePerimeter(feat),2)) + ' m'.decode('utf8'))
        self.Dialog.lblKilometer.setText(str(round(self.grafArea.measurePerimeter(feat)/1000,2)) + ' km'.decode('utf8'))


  
    def seppl(self,id,feat):
        self.area(feat)
        self.cpoint_list = []   


   
    def kasperl(self,id):
        seli = QgsFeatureRequest(id)
        feat = QgsFeature()
        iti = self.layer.getFeatures(seli)
        iti.nextFeature(feat)
        self.area(feat.geometry())
        self.cpoint_list = []    


   
    def switch_feature(self):
        features = self.layer.selectedFeatures()

        if not features == None:
            if len (features) == 1:
                self.area(features[0].geometry())
            if len (features) > 1:
                self.layer.removeSelection()




    
    def switch_layer(self,layer):

        
        if layer == None:
            return

        
        if layer.type() == 0 and layer.geometryType() == 2 and not layer.isReadOnly():
            self.layer = layer
            self.Dialog.lblLayer_area.setText('Layer: ' + self.layer.name())
            self.Dialog.lblLayer_perimeter.setText('Layer: ' + self.layer.name())

            QtCore.QObject.connect(self.layer, QtCore.SIGNAL('geometryChanged (QgsFeatureId, QgsGeometry &)'), self.seppl)
            QtCore.QObject.connect(self.layer, QtCore.SIGNAL('featureAdded (QgsFeatureId)'), self.kasperl)
            QtCore.QObject.connect(self.layer, QtCore.SIGNAL("selectionChanged ()"), self.switch_feature)


        else:   
            self.layer = None
            self.Dialog.lblLayer_area.setText('Layer: ')
            self.Dialog.lblLayer_perimeter.setText('Layer: ')
            



    
    def digklick(self,Aktion,Aktion_neu):

        Aktion = self.mc.mapTool()
        self.maptool = Aktion

        
        if Aktion.action() == None :
            self.Aufzeichnen = False
            self.Dialog.lblQuadratmeter.setText('')
            self.Dialog.lblHektar.setText('')
            self.Dialog.lblQuadratkilometer.setText('')
            self.Dialog.lblMeter.setText('')
            self.Dialog.lblKilometer.setText('')
            QtCore.QObject.disconnect(self.mc, QtCore.SIGNAL('xyCoordinates ( const QgsPoint &) '), self.temp_vertex)

        elif Aktion.action().objectName().find('AddFeature') > -1 :   

            QtCore.QObject.connect(self.mc, QtCore.SIGNAL('xyCoordinates ( const QgsPoint &) '), self.temp_vertex)

        elif Aktion.action().objectName().find('NodeTool') > -1 :   

            QtCore.QObject.disconnect(self.mc, QtCore.SIGNAL('xyCoordinates ( const QgsPoint &) '), self.temp_vertex)


        else:   
            self.Aufzeichnen = False
            self.Dialog.lblQuadratmeter.setText('')
            self.Dialog.lblHektar.setText('')
            self.Dialog.lblQuadratkilometer.setText('')
            self.Dialog.lblMeter.setText('')
            self.Dialog.lblKilometer.setText('')
            QtCore.QObject.disconnect(self.mc, QtCore.SIGNAL('xyCoordinates ( const QgsPoint &) '), self.temp_vertex)
            



    
    def temp_vertex(self,point):


        b = []
        b = self.cpoint_list[:]
        b.append(point) 


        if len(b) > 2:  
             self.area(QgsGeometry().fromPolygon([b]))



    
    def eventFilter(self,affe,event):

        if not event == None:


            if event.type() == QtCore.QEvent.Close: 

                QtCore.QObject.disconnect(self.mc, QtCore.SIGNAL("mapToolSet (QgsMapTool *,QgsMapTool *)"), self.digklick)
                QtCore.QObject.disconnect(self.iface, QtCore.SIGNAL("currentLayerChanged (QgsMapLayer *)"), self.switch_layer)
                QtCore.QObject.disconnect(self.mc, QtCore.SIGNAL('xyCoordinates ( const QgsPoint &) '), self.temp_vertex)

                if not self.layer == None:
                    QtCore.QObject.disconnect(self.layer, QtCore.SIGNAL('geometryChanged (QgsFeatureId, QgsGeometry &)'), self.seppl)  
                    QtCore.QObject.disconnect(self.layer, QtCore.SIGNAL('featureAdded (QgsFeatureId)'), self.kasperl)
                    QtCore.QObject.disconnect(self.layer, QtCore.SIGNAL("selectionChanged ()"), self.switch_feature)

                
                self.DialogDock.removeEventFilter(self)
                self.iface.mapCanvas().viewport().removeEventFilter( self)

                
                self.Dialog = None  
                self.iface.mainWindow().removeDockWidget(self.DialogDock)   
                self.DialogDock = None  

                return True

            elif event.type() == QtCore.QEvent.MouseButtonPress: 
                X_ = event.posF().x()
                Y_ = event.posF().y()
                transi = self.mc.getCoordinateTransform()

                
                if self.maptool.action().objectName().find('NodeTool') > -1 :   
                    self.layer.removeSelection()
                    shift=self.mc.mapUnitsPerPixel()
                    wahlRect = QgsRectangle(transi.toMapCoordinatesF(X_-5,Y_-5),transi.toMapCoordinatesF(X_+5,Y_+5))
                    self.layer.select(wahlRect,False)
                    return False    
                else:
                    if event.button() == QtCore.Qt.LeftButton:
                        self.cpoint_list.append(QgsPoint(transi.toMapCoordinatesF(X_,Y_)))
                        return False    
                    elif event.button() == QtCore.Qt.RightButton:
                        self.cpoint_list= []
                        return False
            else:   
                return False



class CalcAreaDialog(QtGui.QDialog,Ui_frmMainWindow):
    def __init__(self):

        
        QtGui.QDialog.__init__(self)
        Ui_frmMainWindow.__init__(self)

        self.setupUi(self)   
