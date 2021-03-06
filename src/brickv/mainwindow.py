# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2009-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2014 Matthias Bolte <matthias@tinkerforge.com>

mainwindow.py: New/Removed Bricks are handled here and plugins shown if clicked

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

from PyQt4.QtCore import pyqtSignal, QAbstractTableModel, QVariant, Qt, QTimer
from PyQt4.QtGui import QApplication, QMainWindow, QMessageBox, QIcon, \
                        QPushButton, QWidget, QHBoxLayout, QVBoxLayout, \
                        QLabel, QFrame, QSpacerItem, QSizePolicy, \
                        QStandardItemModel, QStandardItem, QToolButton, \
                        QLineEdit
from brickv.ui_mainwindow import Ui_MainWindow
from brickv.plugin_system.plugin_manager import PluginManager
from brickv.bindings.ip_connection import IPConnection
from brickv.flashing import FlashingWindow
from brickv.advanced import AdvancedWindow
from brickv.async_call import async_start_thread, async_next_session
from brickv.bindings.brick_master import BrickMaster
from brickv.program_path import get_program_path
from brickv import config
from brickv import infos

import os
import signal
import sys
import time

HOST_HISTORY_SIZE = 5

class MainTableModel(QAbstractTableModel):
    def __init__(self, header, data, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.header = header
        self.data = data

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.data[index.row()][index.column()])

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.DisplayRole:
            self.data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header[col])
        return QVariant()

class MainWindow(QMainWindow, Ui_MainWindow):
    qtcb_enumerate = pyqtSignal(str, str, 'char', type((0,)), type((0,)), int, int)
    qtcb_connected = pyqtSignal(int)
    qtcb_disconnected = pyqtSignal(int)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(get_program_path(), "brickv-icon.png")))
        signal.signal(signal.SIGINT, self.exit_brickv)
        signal.signal(signal.SIGTERM, self.exit_brickv)

        self.async_thread = async_start_thread(self)

        self.setWindowTitle("Brick Viewer " + config.BRICKV_VERSION)

        self.tree_view_model_labels = ['Name', 'UID', 'FW Version']
        self.tree_view_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_view_model)
        self.tree_view.doubleClicked.connect(self.item_double_clicked)
        self.set_tree_view_defaults()

        # Remove dummy tab
        self.tab_widget.removeTab(1)
        self.last_tab = 0

        self.name = '<unknown>'
        self.uid = '<unknown>'
        self.version = (0, 0, 0)

        self.disconnect_times = []

        self.qtcb_enumerate.connect(self.cb_enumerate)
        self.qtcb_connected.connect(self.cb_connected)
        self.qtcb_disconnected.connect(self.cb_disconnected)

        self.ipcon = IPConnection()
        self.ipcon.set_auto_reauthenticate(False)
        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE,
                                     self.qtcb_enumerate.emit)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED,
                                     self.qtcb_connected.emit)
        self.ipcon.register_callback(IPConnection.CALLBACK_DISCONNECTED,
                                     self.qtcb_disconnected.emit)

        self.flashing_window = None
        self.advanced_window = None
        self.delayed_refresh_updates_timer = QTimer()
        self.delayed_refresh_updates_timer.timeout.connect(self.delayed_refresh_updates)
        self.delayed_refresh_updates_timer.setInterval(500)
        self.reset_view()
        self.button_advanced.setDisabled(True)

        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.button_connect.pressed.connect(self.connect_pressed)
        self.button_flashing.pressed.connect(self.flashing_pressed)
        self.button_advanced.pressed.connect(self.advanced_pressed)
        self.plugin_manager = PluginManager()

        self.combo_host.addItem(config.get_host())
        self.combo_host.addItems(config.get_host_history(HOST_HISTORY_SIZE - 1))
        self.spinbox_port.setValue(config.get_port())

        self.last_host = self.combo_host.currentText()
        self.last_port = self.spinbox_port.value()

        self.checkbox_authentication.stateChanged.connect(self.authentication_state_changed)

        self.label_secret.hide()

        self.edit_secret.hide()
        self.edit_secret.setEchoMode(QLineEdit.Password)

        self.checkbox_secret_show.hide()
        self.checkbox_secret_show.stateChanged.connect(self.secret_show_state_changed)

        self.checkbox_remember_secret.hide()

        if config.get_use_authentication():
            self.checkbox_authentication.setCheckState(Qt.Checked)

        if config.get_remember_secret():
            self.edit_secret.setText(config.get_secret())
            self.checkbox_remember_secret.setCheckState(Qt.Checked)

        self.label_auto_reconnects.hide()
        self.auto_reconnects = 0

    def closeEvent(self, event):
        self.exit_brickv()

    def exit_brickv(self, signl=None, frme=None):
        try:
            uid = self.tab_widget.widget(self.last_tab)._uid
            infos.infos[uid].plugin.stop()
        except:
            pass

        host = str(self.combo_host.currentText())
        history = []

        for i in range(self.combo_host.count()):
            h = str(self.combo_host.itemText(i))

            if h != host and h not in history:
                history.append(h)

        config.set_host(host)
        config.set_host_history(history[:HOST_HISTORY_SIZE - 1])
        config.set_port(self.spinbox_port.value())
        config.set_use_authentication(self.checkbox_authentication.isChecked())

        remember_secret = self.checkbox_remember_secret.isChecked()

        config.set_remember_secret(remember_secret)

        if remember_secret:
            config.set_secret(str(self.edit_secret.text()))
        else:
            config.set_secret(config.DEFAULT_SECRET)

        self.reset_view()

        try:
            self.ipcon.disconnect()
        except:
            pass

        if signl != None and frme != None:
            print "Received SIGINT or SIGTERM, shutting down."
            sys.exit()

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    def authentication_state_changed(self, state):
        visible = state == Qt.Checked

        self.label_secret.setVisible(visible)
        self.edit_secret.setVisible(visible)
        self.checkbox_secret_show.setVisible(visible)
        self.checkbox_remember_secret.setVisible(visible)

    def secret_show_state_changed(self, state):
        if state == Qt.Checked:
            self.edit_secret.setEchoMode(QLineEdit.Normal)
        else:
            self.edit_secret.setEchoMode(QLineEdit.Password)

    def tab_changed(self, i):
        try:
            uid = self.tab_widget.widget(i)._uid
            infos.infos[uid].plugin.start()
        except:
            pass

        try:
            uid = self.tab_widget.widget(self.last_tab)._uid
            infos.infos[uid].plugin.stop()
        except:
            pass

        self.last_tab = i

    def reset_view(self):
        self.tab_widget.setCurrentIndex(0)

        keys_to_remove = []
        for key in infos.infos:
            if infos.infos[key].type in ('brick', 'bricklet'):
                try:
                    infos.infos[key].plugin.stop()
                except:
                    pass

                try:
                    infos.infos[key].plugin.destroy()
                except:
                    pass
                keys_to_remove.append(key)

        for key in keys_to_remove:
            try:
                infos.infos.pop(key)
            except:
                pass

        for i in reversed(range(1, self.tab_widget.count())):
            self.tab_widget.removeTab(i)

        self.update_tree_view()

    def do_disconnect(self):
        self.auto_reconnects = 0
        self.label_auto_reconnects.hide()

        self.reset_view()
        async_next_session()

        try:
            self.ipcon.disconnect()
        except:
            pass

    def do_authenticate(self, is_auto_reconnect):
        if not self.checkbox_authentication.isChecked():
            return True

        try:
            secret = str(self.edit_secret.text()).encode('ascii')
        except:
            self.do_disconnect()

            QMessageBox.critical(self, 'Connection',
                                 'Authentication secret cannot contain non-ASCII characters.',
                                 QMessageBox.Ok)
            return False

        self.ipcon.set_auto_reconnect(False) # don't auto-reconnect on authentication error

        try:
            self.ipcon.authenticate(secret)
        except:
            self.do_disconnect()

            if is_auto_reconnect:
                extra = ' after auto-reconnect'
            else:
                extra = ''

            QMessageBox.critical(self, 'Connection',
                                 'Could not authenticate' + extra + '. Check secret and ensure ' +
                                 'authentication for Brick Daemon is enabled.',
                                 QMessageBox.Ok)
            return False

        self.ipcon.set_auto_reconnect(True)

        return True

    def flashing_pressed(self):
        first = False

        if self.flashing_window is None:
            first = True
            self.flashing_window = FlashingWindow(self)

        self.update_flashing_window()
        self.flashing_window.show()
        self.flashing_window.refresh_updates_pressed()

    def advanced_pressed(self):
        if self.advanced_window is None:
            self.advanced_window = AdvancedWindow(self)

        self.update_advanced_window()
        self.advanced_window.show()

    def connect_pressed(self):
        if self.ipcon.get_connection_state() == IPConnection.CONNECTION_STATE_DISCONNECTED:
            try:
                self.last_host = self.combo_host.currentText()
                self.last_port = self.spinbox_port.value()
                self.button_connect.setDisabled(True)
                self.button_connect.setText("Connecting ...")
                self.button_connect.repaint()
                QApplication.processEvents()
                self.ipcon.connect(self.last_host, self.last_port)
            except:
                self.button_connect.setDisabled(False)
                self.button_connect.setText("Connect")
                QMessageBox.critical(self, 'Connection',
                                     'Could not connect. Please check host, check ' +
                                     'port and ensure that Brick Daemon is running.')
        else:
            self.do_disconnect()

    def item_double_clicked(self, index):
        text = str(index.data().toString())
        i = self.tab_for_uid(text)
        if i > 0:
            self.tab_widget.setCurrentIndex(i)

    def connected_uid_pressed(self, connected_uid):
        i = self.tab_for_uid(connected_uid)
        if i > 0:
            self.tab_widget.setCurrentIndex(i)

    def create_plugin_container(self, plugin, connected_uid, position):
        container = QWidget()
        container._uid = plugin.uid
        layout = QVBoxLayout(container)
        info = QHBoxLayout()

        # uid
        info.addWidget(QLabel('UID:'))
        label = QLabel('{0}'.format(plugin.uid))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse |
                                      Qt.TextSelectableByKeyboard)
        info.addWidget(label)

        info.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding))

        # connected uid
        if connected_uid != '0':
            info.addWidget(QLabel('Connected to:'))
            button = QToolButton()
            button.setText(connected_uid)
            button.pressed.connect(lambda: self.connected_uid_pressed(connected_uid))
            info.addWidget(button)

            info.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding))

        # position
        info.addWidget(QLabel('Position:'))
        info.addWidget(QLabel('{0}'.format(position.upper())))

        info.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding))

        # firmware version
        info.addWidget(QLabel('FW Version:'))
        info.addWidget(QLabel('{0}'.format(plugin.version_str)))

        info.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding))

        # timeouts
        info.addWidget(QLabel('Timeouts:'))
        label_timeouts = QLabel('0')
        info.addWidget(label_timeouts)

        layout.addLayout(info)

        if plugin.is_brick():
            button = QPushButton('Reset')
            if plugin.has_reset_device():
                button.clicked.connect(plugin.reset_device)
            else:
                button.setDisabled(True)
            info.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
            info.addWidget(button)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        plugin.label_timeouts = label_timeouts
        plugin.layout().setContentsMargins(0, 0, 0, 0)

        layout.addWidget(line)
        layout.addWidget(plugin)

        return container

    def tab_for_uid(self, uid):
        for i in range(1, self.tab_widget.count()):
            try:
                widget = self.tab_widget.widget(i)
                if widget._uid == uid:
                    return i
            except:
                pass

        return -1

    def cb_enumerate(self, uid, connected_uid, position,
                     hardware_version, firmware_version,
                     device_identifier, enumeration_type):
        if self.ipcon.get_connection_state() != IPConnection.CONNECTION_STATE_CONNECTED:
            # ignore enumerate callbacks that arrived after the connection got closed
            return

        if enumeration_type in [IPConnection.ENUMERATION_TYPE_AVAILABLE,
                                IPConnection.ENUMERATION_TYPE_CONNECTED]:
            if device_identifier == BrickMaster.DEVICE_IDENTIFIER:
                info = infos.BrickMasterInfo()
            elif position in ('a', 'b', 'c', 'd', 'A', 'B', 'C', 'D'):
                position = position.lower()
                info = infos.BrickletInfo()
            else:
                info = infos.BrickInfo()

            if uid in infos.infos:
                info = infos.infos[uid]
            else:
                infos.infos[uid] = info

            for device in infos.infos.values():
                if device.type == 'brick':
                    if info.type == 'bricklet':
                        if device.uid == connected_uid:
                            device.bricklets[position] = info
                if device.type == 'bricklet':
                    if info.type == 'brick':
                        if uid == device.connected_uid:
                            info.bricklets[device.position] = device

            info.uid = uid
            info.connected_uid = connected_uid
            info.position = position
            info.hardware_version = hardware_version
            info.firmware_version_installed = firmware_version
            info.device_identifier = device_identifier
            info.protocol_version = 2
            info.enumeration_type = enumeration_type

            for device in infos.infos.values():
                if device.type in ('brick', 'bricklet'):
                    if device.uid == uid and device.plugin != None:
                        return

            plugin = self.plugin_manager.get_plugin(device_identifier, self.ipcon,
                                                    uid, firmware_version)

            if plugin is not None:
                info.plugin = plugin
                if plugin.is_hardware_version_relevant(hardware_version):
                    info.name = '{0} {1}.{2}'.format(plugin.name,
                                                     hardware_version[0],
                                                     hardware_version[1])
                else:
                    info.name = plugin.name

                info.url_part = plugin.get_url_part()

                c = self.create_plugin_container(plugin, connected_uid, position)
                info.plugin_container = c
                self.tab_widget.addTab(c, info.name)
        elif enumeration_type == IPConnection.ENUMERATION_TYPE_DISCONNECTED:
            for device_info in infos.infos.values():
                if device_info.type in ('brick', 'bricklet'):
                    if device_info.uid == uid:
                        try:
                            self.tab_widget.setCurrentIndex(0)
                            if device_info.plugin:
                                try:
                                    device_info.plugin.stop()
                                except:
                                    pass

                                try:
                                    device_info.plugin.destroy()
                                except:
                                    pass

                            i = self.tab_for_uid(device_info.uid)
                            self.tab_widget.removeTab(i)
                        except:
                            pass

                if device_info.type == 'brick':
                    for port in device_info.bricklets:
                        if device_info.bricklets[port]:
                            if device_info.bricklets[port].uid == uid:
                                device_info.bricklets[port] = None

                try:
                    infos.infos.pop(uid)
                except:
                    pass

        self.update_tree_view()

    def cb_connected(self, connect_reason):
        self.disconnect_times = []

        self.update_ui_state()

        if connect_reason == IPConnection.CONNECT_REASON_REQUEST:
            self.auto_reconnects = 0
            self.label_auto_reconnects.hide()

            self.ipcon.set_auto_reconnect(True)

            index = self.combo_host.findText(self.last_host)
            if index >= 0:
                self.combo_host.removeItem(index)
            self.combo_host.insertItem(-1, self.last_host)
            self.combo_host.setCurrentIndex(0)

            while self.combo_host.count() > HOST_HISTORY_SIZE:
                self.combo_host.removeItem(self.combo_host.count() - 1)

            if not self.do_authenticate(False):
                return

            try:
                self.ipcon.enumerate()
            except:
                self.update_ui_state()
        elif connect_reason == IPConnection.CONNECT_REASON_AUTO_RECONNECT:
            self.auto_reconnects += 1
            self.label_auto_reconnects.setText('Auto-Reconnect Count: {0}'.format(self.auto_reconnects))
            self.label_auto_reconnects.show()

            if not self.do_authenticate(True):
                return

            try:
                self.ipcon.enumerate()
            except:
                self.update_ui_state()
        else:
            try:
                self.ipcon.enumerate()
            except:
                self.update_ui_state()

    def cb_disconnected(self, disconnect_reason):
        if disconnect_reason == IPConnection.DISCONNECT_REASON_REQUEST:
            self.auto_reconnects = 0
            self.label_auto_reconnects.hide()

        if disconnect_reason == IPConnection.DISCONNECT_REASON_REQUEST or not self.ipcon.get_auto_reconnect():
            self.update_ui_state()
        elif len(self.disconnect_times) >= 3 and self.disconnect_times[-3] < time.time() + 1:
            self.disconnect_times = []
            self.ipcon.set_auto_reconnect(False)
            self.update_ui_state()
            self.reset_view()

            QMessageBox.critical(self, 'Connection',
                                 'Stopped automatic reconnecting due to multiple connection errors in a row.',
                                 QMessageBox.Ok)
        else:
            self.disconnect_times.append(time.time())
            self.update_ui_state(IPConnection.CONNECTION_STATE_PENDING)

    def set_tree_view_defaults(self):
        self.tree_view_model.setHorizontalHeaderLabels(self.tree_view_model_labels)
        self.tree_view.expandAll()
        self.tree_view.setColumnWidth(0, 260)
        self.tree_view.setColumnWidth(1, 75)
        self.tree_view.setColumnWidth(2, 85)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.header().setSortIndicator(0, Qt.AscendingOrder)

    def update_ui_state(self, connection_state=None):
        # FIXME: need to call processEvents() otherwise get_connection_state()
        #        might return the wrong value
        QApplication.processEvents()

        if connection_state is None:
            connection_state = self.ipcon.get_connection_state()

        self.button_connect.setDisabled(False)
        self.button_flashing.setDisabled(False)

        if connection_state == IPConnection.CONNECTION_STATE_DISCONNECTED:
            self.button_connect.setText('Connect')
            self.combo_host.setDisabled(False)
            self.spinbox_port.setDisabled(False)
            self.checkbox_authentication.setDisabled(False)
            self.edit_secret.setDisabled(False)
            self.button_advanced.setDisabled(True)
        elif connection_state == IPConnection.CONNECTION_STATE_CONNECTED:
            self.button_connect.setText("Disconnect")
            self.combo_host.setDisabled(True)
            self.spinbox_port.setDisabled(True)
            self.checkbox_authentication.setDisabled(True)
            self.edit_secret.setDisabled(True)
            self.update_advanced_window(False)
        elif connection_state == IPConnection.CONNECTION_STATE_PENDING:
            self.button_connect.setText('Abort Pending Automatic Reconnect')
            self.combo_host.setDisabled(True)
            self.spinbox_port.setDisabled(True)
            self.checkbox_authentication.setDisabled(True)
            self.edit_secret.setDisabled(True)
            self.button_advanced.setDisabled(True)
            self.button_flashing.setDisabled(True)

        enable = connection_state == IPConnection.CONNECTION_STATE_CONNECTED
        for i in range(1, self.tab_widget.count()):
            self.tab_widget.setTabEnabled(i, enable)

        QApplication.processEvents()

    def update_tree_view(self):
        self.tree_view_model.clear()

        for device_info in sorted(infos.infos.values(), cmp=lambda x, y: cmp(x.name, y.name)):
            if device_info.type == 'brick':
                parent = [QStandardItem(device_info.name),
                          QStandardItem(device_info.uid),
                          QStandardItem('.'.join(map(str, device_info.firmware_version_installed)))]
                for item in parent:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                self.tree_view_model.appendRow(parent)
                for port in sorted(device_info.bricklets):
                    if device_info.bricklets[port] and device_info.bricklets[port].protocol_version == 2:
                        child = [QStandardItem(port.upper() + ': ' +device_info.bricklets[port].name),
                                 QStandardItem(device_info.bricklets[port].uid),
                                 QStandardItem('.'.join(map(str, device_info.bricklets[port].firmware_version_installed)))]
                        for item in child:
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        parent[0].appendRow(child)

        self.set_tree_view_defaults()
        self.update_flashing_window()
        self.update_advanced_window()
        self.delayed_refresh_updates_timer.start()

    def update_flashing_window(self):
        if self.flashing_window is not None:
            self.flashing_window.update_bricks()

    def update_advanced_window(self, update_window=True):
        has_brick = False

        for info in infos.infos.values():
            if info.type == 'brick':
                has_brick = True

        self.button_advanced.setEnabled(has_brick)

        if self.advanced_window is not None and update_window:
            self.advanced_window.update_bricks()

    def delayed_refresh_updates(self):
        self.delayed_refresh_updates_timer.stop()

        if self.flashing_window is not None and self.flashing_window.isVisible():
            self.flashing_window.refresh_updates_pressed()
