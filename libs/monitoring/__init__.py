import queue
from fritzconnection.core.fritzmonitor import FritzMonitor

### Monitor the calls of a fritzbox continously ###
###################################################

def watch_disconnect(monitor, event_queue, func, tams, healthcheck_interval=10):
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
            if 'DISCONNECT;0' in event:
                print("Incoming call stopped. Check the TAM.\n")
                func(tams)

            elif 'DISCONNECT;1' in event:
                print("Outgoing call stopped. Do nothing.\n")

            else:
                print("Unknown event.\n")




def endedCall(func, tams, fritz_ip='192.168.1.1'):
    """ 
    Call this to trigger a given function if a call is disconnected 
    """
    try:
        # as a context manager FritzMonitor will shut down the monitor thread
        with FritzMonitor(address=fritz_ip) as monitor:
            event_queue = monitor.start()
            watch_disconnect(monitor, event_queue, func, tams)
    except (OSError, KeyboardInterrupt) as err:
        print(err)


