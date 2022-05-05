import pkgutil
from jinja2 import Template

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import Node
from mininet.term import makeTerm


class Snort(Node):
    
    PrivateDirs = ["/usr/local/etc/snort"]
    
    def __init__(self, name, snort_intf, snort_conf=None, snort_conf_defaults=None, **params):
        params.setdefault("privateDirs", [])
        params["privateDirs"].extend(self.PrivateDirs)
        super().__init__(name, **params)
        self.snort_intf = snort_intf
        self.snort_conf = snort_conf if snort_conf else "conf/snort.lua"
        self.snort_conf_defaults = snort_conf_defaults if snort_conf_defaults else "conf/snort_defaults.lua"
    
    def start_snort(self):
        conf = ""
        if self.snort_conf == "conf/snort.lua":
            conf = pkgutil.get_data(__name__, self.snort_conf).decode()
        else:
            with open(self.snort_conf, "r") as f:
                conf = f.read()
        self.cmd("""\
cat << 'EOF' > /usr/local/etc/snort/snort.lua
{}
EOF""".format(conf))
        
        conf_d = ""
        if self.snort_conf_defaults == "conf/snort_defaults.lua":
            conf_d= pkgutil.get_data(__name__, self.snort_conf_defaults).decode()
        else:
            with open(self.snort_conf_defaults, "r") as f:
                conf_d= f.read()
        self.cmd("""\
cat << 'EOF' > /usr/local/etc/snort/snort_defaults.lua
{}
EOF""".format(conf_d))
        
        self.cmd("ip link set dev {} promisc on".format(self.snort_intf))
        self.cmd("ethtool -K {} gro off lro off".format(self.snort_intf))
        # self.cmd("snort -c /usr/local/etc/snort/snort.lua -s 65535 -k none -l /var/log/snort -D -i {} -m 0x1b ".format(self.snort_intf))


class MininetExtention(Mininet):

    def __init__(self, **params):
        super().__init__(**params)
        self.snorts = []

    def addSnort(self, name, **params):
        """add Snort"""
        r = self.addHost(name=name, cls=Snort, **params)
        self.snorts.append(r)
        return r

    def start(self):
        """start mininet and Snort"""
        super().start()
        info('*** Start Snort:\n')
        for s in self.snorts:
            s.start_snort()
            info(s.name + " ")
        info("\n")


if __name__ == "__main__":
    pass
