#!/usr/bin/env python3

from fritzconnection import FritzConnection
from fritzconnection.lib.fritzcall import FritzCall, Call
from dotenv import load_dotenv
from pydub import AudioSegment
from libs.monitoring import endedCall
from libs.message import conversion as conv
import urllib.request
import xmltodict, json
import sys, os, time
import smbclient
import signal
import time

## Get environment variables from the .env file which will be ignored by git
load_dotenv()
env_user = os.environ.get('FRITZ_USERNAME')
env_pass = os.environ.get('FRITZ_PASSWORD')
env_ip = os.environ.get('FRITZ_IP')
env_voicebox = os.environ.get('FRITZ_VOICEBOX_PATH', '/fritz.nas/FRITZ/voicebox/')
env_tam = os.environ.get('FRITZ_TAM', '0').split(', ')
env_MARK_MESSAGE_READ = eval(os.environ.get('MARK_MESSAGE_READ', 'True'))
env_delete_message = eval(os.environ.get('DELETE_MESSAGE', 'False'))

# CONSTANTS
RECORDINGS_DIR = "/recordings"

# classes
class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    self.kill_now = True

# Build the url to download the message via smb
def build_download_url(mid, tam=0):
    recording = "rec." + str(tam) + r"." + str(mid).zfill(3)
    url = os.path.join("//",env_ip,env_voicebox,"rec",recording)
    return url

def download_speex_file(smb_url):
    smbclient.register_session(server=env_ip, username=env_user, password=env_pass, auth_protocol="ntlm")
    fd = smbclient.open_file(smb_url, mode="rb")
    return fd

def get_message_list(url):
    """ Get and and convert the xml formatted list of messages into a dictionary. """
    with urllib.request.urlopen(url) as f:
        doc = f.read()
        # Convert the xml formatted message list to dict
        messages = xmltodict.parse(doc)
        return messages

def get_last_call():
    """ Get the last Call. """
    try:
        fc = FritzCall(address=env_ip,password=env_pass)
    except:
        print("Couldn't connect to Box")
    missed_calls = fc.get_missed_calls(False,1,1)

    if len(missed_calls) > 0:
        return missed_calls[0]
    else:
        return False

def fritzab2matrix(tam):
    ### CHECK AND GET MESSAGES FROM FRITZBOX ###
    ############################################

    ## Connect to the FritzBox in the LAN
    # We don't use tls because the self-signed cert of the box leads to a malfunction in urllib later on.
    fc = FritzConnection(address=env_ip, user=env_user, password=env_pass, use_tls=False)

    ## Get info about messages from the main answering machine
    message_list = fc.call_action("X_AVM-DE_TAM1", "GetMessageList", NewIndex=tam)
    message_list_url = message_list['NewURL']

    l = get_message_list(message_list_url)
    if l['Root'] == None or l['Root']['Message'] == None:
        return False
    else:
        messages = l['Root']['Message']
        if type(messages) is not list:
            m = []
            m.append(messages)
            messages = m

    for a in messages:

        # format the information regarding the message
        msg_info = a['Date'] + " - " + str(a['Number'])
        if a['Name']:
            msg_info += " (" + a['Name'] + ") "

        # format the string for sound file's meta information
        msg_tags = {'title': msg_info, 'artist': 'Answerting Machine' ,'album': "TAM" + a['Tam'], 'comment': 'Message of a telephone answering machine'}

        # Select only new messages
        message_new = bool(int(a['New']))

        if message_new == True:
            # Download and convert the speex files to wav
            smb_url = build_download_url(a['Index'])
            speex_fd = download_speex_file(smb_url)
            # create wav file
            conv.speex_convert(speex_fd, os.path.join(RECORDINGS_DIR,"message{}.wav".format(tam)))

            # Convert wav to ogg
            msg = AudioSegment.from_wav(os.path.join(RECORDINGS_DIR,"message{}.wav".format(tam)))
            msg.export(os.path.join(RECORDINGS_DIR,"message{}.ogg".format(tam)), format="ogg", tags=msg_tags)

            # Show that message is new
            print("** " + msg_info)

            # Mark processed messages as 'read'
            if env_MARK_MESSAGE_READ == True:
                fc.call_action("X_AVM-DE_TAM1", "MarkMessage", NewIndex=tam, NewMessageIndex=int(a['Index']), NewMarkedAsRead=1)

            # Delete processed messages
            if env_delete_message == True:
                fc.call_action("X_AVM-DE_TAM1", "DeleteMessage", NewIndex=tam, NewMessageIndex=int(a['Index']))

        else:
            # Show that message is already read
            print("__ " + msg_info)

    tam_no = a['Called']

def multitam(tams):
    for tam in tams:
        print("Check TAM {}.".format(tam))
        fritzab2matrix(tam)

if __name__ == "__main__":
    # create graceful killer
    killer = GracefulKiller()
    multitam(env_tam)
    ### Monitor the FritzBox and trigger the main script whenever a call disconnects ###
    ###################################################################################
    endedCall(multitam, env_tam, killer, env_ip)
