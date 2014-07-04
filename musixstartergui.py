#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# musixstartergui.py
#
#       Copyright 2009 ariel <ariel@musix.org.ar>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#
#
#
#       Last Updated: Jul 04 2014, Jose VV
#       Based on previous work by Ariel
#
#

import sys
from PyQt4 import QtCore, QtGui


class ExecutionController():
    """
    Esta clase esta pensada para ser reutilizada desde otras interfaces
    El atributo listaApps es un diccionario de objetos que hereden AbstractApplicationControl
    """

    def __init__(self, apps):
        self.apps = apps

    def execute(self):
        """
        Este metodo ejecuta musixstarter con todos los parametros
        """
        musixstarter_cmd = "/usr/bin/musixstarter "
        for name, application in self.apps.iteritems():
            app_cmd = application.return_cmd()
            if app_cmd is not None:
                musixstarter_cmd += app_cmd + " "

        #execute command
        print str(musixstarter_cmd)
        import os

        #os.system(str(musixstarter_cmd))


class ApplicationObject():
    """
    Representa una aplicacion que sera lanzada desde musixstarter
    Tiene como atributos el nombre, el parametro de musixstarter, y una descripcion opcional
    """

    def __init__(self, name, param, description=""):
        self.name = name
        self.param = param
        self.description = description


class AbstractApplicationControl(object):
    def __init__(self, application):
        super(AbstractApplicationControl, self).__init__()
        self.application = application

    def build_control(self):
        raise Exception("Abstract class")

    def return_cmd(self):
        raise Exception("Abstract class")


class ApplicationControlSimple(AbstractApplicationControl, QtGui.QWidget):
    """
    Representa un control simple para lanzar una aplicacion.
    Aparece como un QGroupBox que solo incluye un checkbox para marcar si se inicia o no la aplicacion
    """

    def __init__(self, application, main_widget):
        super(ApplicationControlSimple, self).__init__(application)
        self.groupBox = QtGui.QGroupBox()
        self.check = QtGui.QCheckBox(self.groupBox)
        self.mainWidget = main_widget

    def build_control(self):
        self.groupBox.setTitle(self.application.name)
        self.groupBox.setObjectName("groupBox_" + self.application.name)
        self.groupBox.setToolTip(self.application.description)
        self.check.setGeometry(QtCore.QRect(10, 15, 300, 30))
        self.check.setObjectName("check_" + self.application.name)
        self.check.setText("Arrancar " + self.application.name)

        return self.groupBox

    def return_cmd(self):
        if self.check.isChecked():
            return self.application.param
        else:
            return None


class ApplicationControlWithFile(ApplicationControlSimple):
    """
    incluye una caja de texto y un boton para seleccionar un fichero de configuracion
    """

    def __init__(self, application, main_widget):
        super(ApplicationControlWithFile, self).__init__(application, main_widget)
        self.groupBox = ApplicationControlSimple.build_control(self)
        self.txtFileConfig = QtGui.QLineEdit(self.groupBox)
        self.btFile = QtGui.QPushButton(self.groupBox)

    def build_control(self):
        self.txtFileConfig.setGeometry(QtCore.QRect(10, 45, 200, 25))
        self.txtFileConfig.setObjectName("txtFileConfig_" + self.application.name)
        self.btFile.setGeometry(QtCore.QRect(210, 45, 25, 25))
        self.btFile.setObjectName("btFile_" + self.application.name)
        self.btFile.setText("...")
        self.btFile.clicked.connect(self.file_config_dialog)

        return self.groupBox

    def return_cmd(self):
        if self.check.isChecked():
            if str(self.txtFileConfig.text()).strip() != "":
                return self.application.param + "=" + str(self.txtFileConfig.text()).strip()
            else:
                return self.application.param
        else:
            return None

    def file_config_dialog(self):
        fd = QtGui.QFileDialog(self.mainWidget)
        file_name = fd.getOpenFileName()
        self.txtFileConfig.setText(file_name)


class ApplicationControlWithComboBox(ApplicationControlSimple):
    """
    Incluye un desplegable QComboBox con opciones de configuracion prefijadas
    """

    def __init__(self, application, main_widget, label_items, items):
        super(ApplicationControlWithComboBox, self).__init__(application, main_widget)
        self.cmbEmulation = QtGui.QComboBox(self.groupBox)
        self.labelCombo = QtGui.QLabel(self.groupBox)
        self.items = items
        self.labelItems = label_items

    def build_control(self):
        self.groupBox = ApplicationControlSimple.build_control(self)

        self.labelCombo.setText(self.labelItems)
        self.labelCombo.setGeometry(QtCore.QRect(10, 45, 75, 30))
        self.cmbEmulation.setGeometry(QtCore.QRect(85, 45, 150, 30))
        self.cmbEmulation.setObjectName("cmbEmulation" + self.application.name)

        for item in self.items:
            self.cmbEmulation.addItem(item)

        return self.groupBox

    def return_cmd(self):
        if self.check.isChecked():
            return self.application.param + "=" + str(self.cmbEmulation.currentText()).strip()
        else:
            return None

    def file_config_dialog(self):
        fd = QtGui.QFileDialog(self.mainWidget)
        file_name = fd.getOpenFileName()
        self.txtFileConfig.setText(file_name)


class ApplicationControlJack(ApplicationControlWithFile):
    """
    Crea el control QGroupBox en el que se incluyen las distintas opciones de configuracion para Jack
    """

    def __init__(self, application, main_widget):
        super(ApplicationControlJack, self).__init__(application, main_widget)
        self.rbJackAlsa = QtGui.QRadioButton(self.groupBox)
        self.rbJackFile = QtGui.QRadioButton(self.groupBox)
        self.cbBufferSize = QtGui.QComboBox(self.groupBox)
        self.rbJackDuplex = QtGui.QRadioButton(self.groupBox)
        self.rbJackPlay = QtGui.QRadioButton(self.groupBox)

    def build_control(self):
        self.groupBox = ApplicationControlWithFile.build_control(self)
        self.check.setVisible(False)
        self.check.setDisabled(True)

        self.rbJackPlay.setGeometry(QtCore.QRect(10, 25, 200, 15))
        self.rbJackPlay.setText("Play")
        self.rbJackPlay.setChecked(True)

        self.rbJackDuplex.setGeometry(QtCore.QRect(10, 50, 200, 15))
        self.rbJackDuplex.setText("Duplex")
        self.cbBufferSize.setGeometry(QtCore.QRect(210, 45, 225, 25))
        self.cbBufferSize.addItems(["32", "64", "128", "256", "512", "1024", "2048", "4096"])
        self.cbBufferSize.setCurrentIndex(4)

        self.rbJackFile.setGeometry(QtCore.QRect(10, 75, 200, 15))
        self.rbJackFile.setText("User's preferences")
        self.txtFileConfig.move(210, 72)
        self.btFile.move(410, 72)

        self.rbJackAlsa.setGeometry(QtCore.QRect(10, 100, 200, 15))
        self.rbJackAlsa.setText("Use ALSA")

        return self.groupBox

    def return_cmd(self):
        if self.rbJackFile.isChecked():
            if str(self.txtFileConfig.text()).strip() != "":
                return "--jackdef=" + str(self.txtFileConfig.text()).strip()
            else:
                return "--jackdef"
        elif self.rbJackPlay.isChecked():
            return "--jackrep"
        elif self.rbJackDuplex.isChecked():
            return "--jaudio --jbuffsize=" + self.cbBufferSize.currentText()
        else:
            return ""


class MusixstarterGui(QtGui.QMainWindow):
    """
    Esta es la clase principal, que crea la interfaz y la conecta con la clase ExecutionController,
    mediante objetos de tipo AbstractApplication
    """

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.bt_save = QtGui.QPushButton()
        self.bt_open = QtGui.QPushButton()
        self.bt_execute = QtGui.QPushButton()

        self.ly_apps_widget = QtGui.QWidget(self)
        self.ly_apps = QtGui.QGridLayout(self.ly_apps_widget)
        self.ly_jack_widget = QtGui.QWidget(self)
        self.ly_jack = QtGui.QGridLayout(self.ly_jack_widget)
        self.ly_buttons_widget = QtGui.QWidget(self)
        self.ly_buttons = QtGui.QVBoxLayout(self.ly_buttons_widget)

        self.current_row = 0
        self.current_col = 0

        self.apps = {}

        self.init_ui()

        self.add_buttons()
        self.add_jack()
        self.add_applications()

    def init_ui(self):
        self.setObjectName("musixstarter-gui")
        self.setWindowTitle("Musixstarter GUI")

        #size
        self.setGeometry(QtCore.QRect(0, 0, 808, 540))
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
        self.setFixedSize(self.size())

        self.ly_buttons_widget.setGeometry((QtCore.QRect(570, 30, 200, 120)))
        self.ly_buttons_widget.setObjectName("layoutButtonsWidget")
        self.ly_buttons.setObjectName("layoutButtons")

        self.ly_jack_widget.setGeometry(QtCore.QRect(20, 20, 520, 140))
        self.ly_jack_widget.setObjectName("layoutJackWidget")
        self.ly_jack.setObjectName("layoutJack")

        self.ly_apps_widget.setGeometry(QtCore.QRect(20, 150, 771, 371))
        self.ly_apps_widget.setObjectName("layoutAppsWidget")
        self.ly_apps.setObjectName("layoutApps")

        QtCore.QMetaObject.connectSlotsByName(self)

    def add_buttons(self):
        self.bt_execute.setObjectName("btExecute")
        self.bt_execute.setText("INICIAR")
        self.bt_execute.clicked.connect(self.execute)
        self.ly_buttons.addWidget(self.bt_execute)

        self.bt_open.setDisabled(True)
        self.bt_open.setObjectName("btAbrir")
        self.bt_open.setText("ABRIR")
        self.ly_buttons.addWidget(self.bt_open)

        self.bt_save.setEnabled(False)
        self.bt_save.setObjectName("btGuardar")
        self.bt_save.setText("GUARDAR")
        self.ly_buttons.addWidget(self.bt_save)

    def add_jack(self):
        control_jack = ApplicationControlJack(ApplicationObject("jack", "--rose"), self)
        self.ly_jack.addWidget(control_jack.build_control(), 20, 20)
        self.apps[control_jack.application.name] = control_jack

    def add_applications(self):
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("rosegarden", "--rose"), self))
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("ardour", "--ardour"), self))
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("jamin", "--jam"), self))
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("hydrogen", "--hydro"), self))
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("qsynth", "--qsynt"), self))
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("zynAddSubFX", "--zyn"), self))

        items = ["b3", "mini", "explorer", "memory", "hammond", "pro5", "prophet", "pro52", "pro10", "rhodes",
                 "rhodesbass", "obx", "obxa", "axxe", "odyssey", "2600", "poly", "mono", "juno", "dx", "vox", "solina",
                 "roadrunner"]
        self.add_app_controls(
            ApplicationControlWithComboBox(ApplicationObject("bristol", "--bri"), self, "Emulacion", items))

        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("jackRack", "--jrack"), self))
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("noteEdit", "--noteed"), self))
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("soundBlaster", "--sb"), self))
        self.add_app_controls(ApplicationControlWithFile(ApplicationObject("rakarrack", "--raka"), self))
        self.add_app_controls(ApplicationControlSimple(ApplicationObject("timidiy", "--tim"), self))

    def add_app_controls(self, app_control):
        self.ly_apps.addWidget(app_control.build_control(), self.current_row, self.current_col)
        self.apps[app_control.application.name] = app_control

        if self.current_col == 2:
            self.current_col = 0
            self.current_row += 1
        else:
            self.current_col += 1

    def execute(self):
        controller = ExecutionController(self.apps)
        controller.execute()

#INICIO DE LA APLICACION
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    gui = MusixstarterGui()
    gui.show()
    sys.exit(app.exec_())
