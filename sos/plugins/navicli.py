# Copyright (C) 2008 EMC Corporation. Keith Kearnan <kearnan_keith@emc.com>
# Copyright (C) 2014 Red Hat, Inc., Bryn M. Reeves <bmr@redhat.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from sos.plugins import Plugin, RedHatPlugin, os
from sos.utilities import is_executable


# Just for completeness sake.
from six.moves import input


class Navicli(Plugin, RedHatPlugin):
    """ EMC Navicli
    """

    plugin_name = 'navicli'
    profiles = ('storage', 'hardware')

    option_list = [
        ("ipaddrs", "list of CLARiiON SP IP Addresses separated by spaces", "", "")
    ]

    def check_enabled(self):
        return is_executable("navicli")

    def get_navicli_config(self):
        """ EMC Navisphere Host Agent NAVICLI specific information - files
        """
        self.add_copy_spec([
            "/etc/Navisphere/agent.config",
            "/etc/Navisphere/Navimon.cfg",
            "/etc/Navisphere/Quietmode.cfg",
            "/etc/Navisphere/messages/[a-z]*",
            "/etc/Navisphere/log/[a-z]*"
        ])

    def get_navicli_SP_info(self, SP_address):
        """ EMC Navisphere Host Agent NAVICLI specific
        information - CLARiiON - commands
        """
        self.add_cmd_output([
            "navicli -h %s getall" % SP_address,
            "navicli -h %s getsptime -spa" % SP_address,
            "navicli -h %s getsptime -spb" % SP_address,
            "navicli -h %s getlog" % SP_address,
            "navicli -h %s getdisk" % SP_address,
            "navicli -h %s getcache" % SP_address,
            "navicli -h %s getlun" % SP_address,
            "navicli -h %s getlun -rg -type -default -owner -crus "
            "-capacity" % SP_address,
            "navicli -h %s lunmapinfo" % SP_address,
            "navicli -h %s getcrus" % SP_address,
            "navicli -h %s port -list -all" % SP_address,
            "navicli -h %s storagegroup -list" % SP_address,
            "navicli -h %s spportspeed -get" % SP_address
        ])

    def setup(self):
        self.get_navicli_config()
        ipaddr_list = self.get_option_as_list("ipaddrs", delimiter = " ")
        CLARiiON_IP_address_list = []

        if len(ipaddr_list) == 0:
            if not self.batch:
                CLARiiON_IP_address_list = []
                CLARiiON_IP_loop = "stay_in"
                while CLARiiON_IP_loop == "stay_in":
                    try:
                        ans = input("CLARiiON SP IP Address or [Enter] to exit: ")
                    except:
                        return
                    if self.check_ext_prog("navicli -h %s getsptime" % (ans,)):
                        CLARiiON_IP_address_list.append(ans)
                    else:
                        if ans != "":
                            print("The IP address you entered, %s, is not to an "
                                  "active CLARiiON SP." % ans)
                        if ans == "":
                            CLARiiON_IP_loop = "get_out"
            else:
                self._log_warn("No CLARiiON SP IP Address specified as plugin option and in batch mode: skipping")
        else:
            for SP_address in ipaddr_list:
                if self.check_ext_prog("navicli -h %s getsptime" % (SP_address,)):
                    CLARiiON_IP_address_list.append(SP_address)
                else:
                    self._log_warn("IP address %s is not an active CLARiiON SP." % SP_address)

        # Sort and dedup the list of CLARiiON IP Addresses
        CLARiiON_IP_address_list.sort()
        for SP_address in CLARiiON_IP_address_list:
            if CLARiiON_IP_address_list.count(SP_address) > 1:
                CLARiiON_IP_address_list.remove(SP_address)
        for SP_address in CLARiiON_IP_address_list:
            if SP_address != "":
                print(" Gathering NAVICLI information for %s..." %
                      SP_address)
                self.get_navicli_SP_info(SP_address)

# vim: set et ts=4 sw=4 :
