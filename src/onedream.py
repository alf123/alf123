import os, errno
from configobj import ConfigObj

def getPid():
    config = ConfigObj('./cindy.pid')
    print pid
    return config['pid']

from win32com.client import GetObject
def get_proclist():
    WMI = GetObject('winmgmts:')
    processes = WMI.InstancesOf('Win32_Process')
    return [process.Properties_('ProcessID').Value for process in processes]

pid = 672#str(os.getpid())
setPid(pid)


print (pid in get_proclist())
