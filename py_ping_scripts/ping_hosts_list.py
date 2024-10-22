#removed os lib import
import subprocess

ips = {'Google':'google.com', 'Yahoo': 'yahoo.com',
       'DuckDuckGo': 'duckduckgo.com'}

host_names = ['google.com', 'yahoo.com', 'duckduckgo.com']

def ping_host():
    for name, value in ips.items():
        process = subprocess.call(['ping', '-c', '5', value])
        if process == 0:
            print ("ping to", name, "OK")
        elif process == 2:
            print ("no response from", name)
        else:
            print ("ping to", name, "failed!")
            
ping = ping_host()
ping
