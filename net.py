from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import Node


class Snort(Node):
    
    PrivateDirs = ["/usr/local/etc/snort"]
    
    def __init__(self, name, snort_intf, **params):
        params.setdefault("privateDirs", [])
        params["privateDirs"].extend(self.PrivateDirs)
        super().__init__(name, **params)
        self.snort_intf = snort_intf
    
    def start_snort(self):
        self.cmd("cp ./conf/snort.lua /usr/local/etc/snort/")
        self.cmd("cp ./conf/snort_defaults.lua /usr/local/etc/snort/")
        self.cmd("cp ./conf/file_magic.lua /usr/local/etc/snort/")
        
        self.cmd("ip link set dev {} promisc on".format(self.snort_intf))
        self.cmd("ethtool -K {} gro off lro off".format(self.snort_intf))
        self.cmd("snort -c /usr/local/etc/snort/snort.lua -s 65535 -k none -l /var/log/snort -D -i {} -m 0x1b ".format(self.snort_intf))


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
    setLogLevel("info")
    net = MininetExtention()
    
    net.addHost("h1", ip="192.168.1.1")
    net.addSnort("s1", ip="192.168.1.1", snort_intf="s1_h1")
    
    net.addLink("h1", "s1", 
                intfName1="h1_s1", intfName2="s1_h1")
    
    net.start()
    
    CLI(net)
    
    net.stop()
