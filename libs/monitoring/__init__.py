import queue
from fritzconnection.core.fritzmonitor import FritzMonitor

### Monitor the calls of a fritzbox continously ###
###################################################

def watch_disconnect(monitor, event_queue, func, healthcheck_interval=10):
    while True:
        try:
            event = event_queue.get(timeout=healthcheck_interval)
        except queue.Empty:
            # check health:
            if not monitor.is_alive:
                raise OSError("Error: fritzmonitor connection failed")
        else:
            # do event processing here:
            print(event)
            if 'DISCONNECT' in event:
                print("Anruf beendet. Jetzt den AB checken.\n")
                func()



def endedCall(func, fritz_ip='192.168.1.1'):
    """ 
    Call this to trigger a given function if a call is disconnected 
    """
    try:
        # as a context manager FritzMonitor will shut down the monitor thread
        with FritzMonitor(address=fritz_ip) as monitor:
            event_queue = monitor.start()
            watch_disconnect(monitor, event_queue, func)
    except (OSError, KeyboardInterrupt) as err:
        print(err)


