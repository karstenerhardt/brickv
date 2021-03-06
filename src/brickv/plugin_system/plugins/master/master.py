# -*- coding: utf-8 -*-  
"""
Master Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>

master.py: Master Plugin implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.brick_master import BrickMaster

from PyQt4.QtCore import QTimer

from brickv.plugin_system.plugins.master.ui_master import Ui_Master

from brickv.plugin_system.plugins.master.extension_type import ExtensionType
from brickv.plugin_system.plugins.master.chibi import Chibi
from brickv.plugin_system.plugins.master.rs485 import RS485
from brickv.plugin_system.plugins.master.wifi import Wifi
from brickv.plugin_system.plugins.master.ethernet import Ethernet

from brickv.async_call import async_call
        
class Master(PluginBase, Ui_Master):
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Master Brick', version)
        
        self.setupUi(self)

        self.master = BrickMaster(uid, ipcon)
        self.device = self.master
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)

        self.extension_type = None

        self.extensions = []
        self.num_extensions = 0

        self.extension_label.setText("None Present")
        
        # Chibi widget
        if self.version >= (1, 1, 0):
            self.extension_type_button.pressed.connect(self.extension_pressed)
            async_call(self.master.is_chibi_present, None, self.is_chibi_present_async, self.increase_error_count)
        else:
            self.extension_type_button.setEnabled(False)
            
        # RS485 widget
        if self.version >= (1, 2, 0):
            async_call(self.master.is_rs485_present, None, self.is_rs485_present_async, self.increase_error_count)
                
        # Wifi widget
        if self.version >= (1, 3, 0):
            async_call(self.master.is_wifi_present, None, self.is_wifi_present_async, self.increase_error_count)
        
        # Ethernet widget
        if self.version >= (2, 1, 0):
            async_call(self.master.is_ethernet_present, None, self.is_ethernet_present_async, self.increase_error_count)

    def is_ethernet_present_async(self, present):
        if present:
            ethernet = Ethernet(self)
            self.extensions.append(ethernet)
            self.extension_layout.addWidget(ethernet)
            self.num_extensions += 1
            self.extension_label.setText("" + str(self.num_extensions) + " Present")

    def is_wifi_present_async(self, present):
        if present:
            wifi = Wifi(self)
            self.extensions.append(wifi)
            self.extension_layout.addWidget(wifi)
            self.num_extensions += 1
            self.extension_label.setText("" + str(self.num_extensions) + " Present")
            
    def is_rs485_present_async(self, present):
        if present:
            rs485 = RS485(self)
            self.extensions.append(rs485)
            self.extension_layout.addWidget(rs485)
            self.num_extensions += 1
            self.extension_label.setText("" + str(self.num_extensions) + " Present")
            
    def is_chibi_present_async(self, present):
        if present:
            chibi = Chibi(self)
            self.extensions.append(chibi)
            self.extension_layout.addWidget(chibi)
            self.num_extensions += 1
            self.extension_label.setText("" + str(self.num_extensions) + " Present")

    def start(self):
        self.update_timer.start(1000)

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        for extension in self.extensions:
            extension.destroy()

        if self.extension_type:
            self.extension_type.close()

    def has_reset_device(self):
        return self.version >= (1, 2, 1)

    def reset_device(self):
        if self.has_reset_device():
            self.master.reset()

    def is_brick(self):
        return True

    def is_hardware_version_relevant(self, hardware_version):
        return True

    def get_url_part(self):
        return 'master'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickMaster.DEVICE_IDENTIFIER
    
    def update_data(self):
        async_call(self.master.get_stack_voltage, None, self.stack_voltage_update, self.increase_error_count)
        async_call(self.master.get_stack_current, None, self.stack_current_update, self.increase_error_count)
        
        for extension in self.extensions:
            extension.update_data()
        
    def stack_voltage_update(self, sv):
        sv_str = "%gV"  % round(sv/1000.0, 1)
        self.stack_voltage_label.setText(sv_str)
        
    def stack_current_update(self, sc):
        if sc < 999:
            sc_str = "%gmA" % sc
        else:
            sc_str = "%gA" % round(sc/1000.0, 1)   
        self.stack_current_label.setText(sc_str)
        
    def extension_pressed(self):
        if self.extension_type is None:
            self.extension_type = ExtensionType(self)

        self.extension_type.show()
