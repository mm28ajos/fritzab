#! /usr/bin/python3

from fritzconnection import FritzConnection
from dotenv import load_dotenv
from pydub import AudioSegment
from libs.monitoring import endedCall
from libs.message import conversion as conv
import urllib.request
import xmltodict
import sys, os
import smbclient



## Get environment variables from the .env file which will be ignored by git
load_dotenv()
env_user = os.environ.get('FRITZ_USERNAME')
env_pass = os.environ.get('FRITZ_PASSWORD')
env_ip = os.environ.get('FRITZ_IP')
env_tmp = os.environ.get('TEMP_DIR')
if env_tmp is None:
    env_tmp = "/tmp"

def main():

    ### CHECK AND GET MESSAGES FROM FRITZBOX ###
    ############################################

    ## Connect to the FritzBox in the LAN
    # We don't use tls because the self-signed cert of the box leads to a malfunction in urllib later on.
    fc = FritzConnection(address=env_ip, user=env_user, password=env_pass, use_tls=False)



    ## Get info about messages from the main answering machine
    message_list = fc.call_action("X_AVM-DE_TAM1", "GetMessageList", NewIndex=0)
    message_list_url = message_list['NewURL']


    # Build the url to download the message via smb
    def build_download_url(mid, tam=0):
        url = r"//" + env_ip + r"/fritz.nas/FRITZ/voicebox/rec/rec." + str(tam) + r"." + str(mid).zfill(3)
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


    for a in get_message_list(message_list_url)['Root']['Message']:
        
        # format the information regarding the message
        msg_info = a['Date'] + " - " + a['Number']
        if len(a['Name']) > 1:
            msg_info += " (" + a['Name'] + ") "
            
        # format the string for sound file's meta information
        msg_tags = {'title': msg_info, 'artist': 'Answerting Machine' ,'album': "TAM" + a['Tam'], 'comment': 'Message of a telephone answering machine'}
    
        # Select only new messages
        message_new = bool(int(a['New']))
    
        if message_new == True:

            # Download and convert the speex files to wav
            smb_url = build_download_url(a['Index'])
            speex_fd = download_speex_file(smb_url)
            conv.speex_convert(speex_fd, os.path.join(env_tmp,"message.wav"))
            # Convert wav to ogg
            msg = AudioSegment.from_wav(os.path.join(env_tmp,"message.wav"))
        
            # Only if message is longer than 5 seconds ...
            if msg.duration_seconds > 5.0:
                # ... export to ogg ...
                msg.export(os.path.join(env_tmp,"message.ogg"), format="ogg", tags=msg_tags)

                # ... and send message and file to Matrix Room
                command = "python3 matrix-commander.py -a " + os.path.join(env_tmp,"message.ogg") + " -m '{}'".format(msg_info)
                os.system(command)
            
            else:
                # Mark MessageInfo as too short for the log
                msg_info += " < 6 sec (not posted)"

            # Show that message is new
            print("** " + msg_info)
        
            # Mark processed messages as 'read'
            fc.call_action("X_AVM-DE_TAM1", "MarkMessage", NewIndex=0, NewMessageIndex=int(a['Index']), NewMarkedAsRead=1)
            
        else:
            # Show that message is already read
            print("__ " + msg_info)

            # ## For testing purposes only
#            if a['Date'].endswith('20:53'):
#                fc.call_action("X_AVM-DE_TAM1", "MarkMessage", NewIndex=0, NewMessageIndex=int(a['Index']), NewMarkedAsRead=0)          
      
            continue

        continue
    ### Monitor the FritzBox and trigger the main script whenever a call disconnects ###
    ###################################################################################
    endedCall(main, env_ip)



if __name__ == "__main__":
    try:
        print("I enter the main loop ...")
        while main():
            pass
        else:
            print("I left the main loop!")
        
    except:
        print("An erroneous error happened!")



        



        



