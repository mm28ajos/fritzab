#!/usr/bin/env python3

from fritzconnection import FritzConnection
from fritzconnection.lib.fritzcall import FritzCall, Call
from dotenv import load_dotenv
from pydub import AudioSegment
from libs.monitoring import endedCall
from libs.message import conversion as conv
import urllib.request
import xmltodict, json
import sys, os
import smbclient



## Get environment variables from the .env file which will be ignored by git
load_dotenv()
env_user = os.environ.get('FRITZ_USERNAME')
env_pass = os.environ.get('FRITZ_PASSWORD')
env_ip = os.environ.get('FRITZ_IP')
env_voicebox = os.environ.get('FRITZ_VOICEBOX_PATH')
env_tam = json.loads(os.environ.get('FRITZ_TAM'))
env_call_watch = eval(os.environ.get('FRITZ_CALL_WATCH'))
env_tmp = os.environ.get('TEMP_DIR')

if env_call_watch is None:
    env_call_watch = False
elif env_call_watch:
    at_least_one_new_message = False


if env_voicebox is None:
    env_voicebox = "/fritz.nas/FRITZ/voicebox/"

if env_tam is None:
    env_tam = {
        "0" : "!MxRrNGhFuQwnIeEWnX:ismus.net"
        }
#print(env_tam)

if env_tmp is None:
    env_tmp = "/tmp"



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

def lastcall2matrix(tam,tam_no):
    # Call Watch to Matrix
    if env_call_watch and not at_least_one_new_message:
        c = get_last_call()
        if c:
            c_msg = "{} - {} ({})".format(c.Date, c.Caller, c.Name)
        else:
            return False
        
        # ... and send message and file to Matrix Room
        ## if Number of a TAM and the last call match
        if tam_no == c.CalledNumber:
            cmd = "python3 matrix-commander.py --room {} -m '{}'".format(env_tam[tam],c_msg)
            os.system(cmd)
        
    else:
        print("Call Watch is off.")



def fritzab2matrix(tam):

    ### CHECK AND GET MESSAGES FROM FRITZBOX ###
    ############################################

    ## Connect to the FritzBox in the LAN
    # We don't use tls because the self-signed cert of the box leads to a malfunction in urllib later on.
    fc = FritzConnection(address=env_ip, user=env_user, password=env_pass, use_tls=False)
    at_least_one_new_message = False


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
        msg_info = a['Date'] + " - " + a['Number']
        if a['Name']:
            msg_info += " (" + a['Name'] + ") "
            
        # format the string for sound file's meta information
        msg_tags = {'title': msg_info, 'artist': 'Answerting Machine' ,'album': "TAM" + a['Tam'], 'comment': 'Message of a telephone answering machine'}
    
        # Select only new messages
        message_new = bool(int(a['New']))
    
        if message_new == True:
            at_least_one_new_message = True
            # Download and convert the speex files to wav
            smb_url = build_download_url(a['Index'])
            speex_fd = download_speex_file(smb_url)
            conv.speex_convert(speex_fd, os.path.join(env_tmp,"message{}.wav".format(tam)))
            # Convert wav to ogg
            msg = AudioSegment.from_wav(os.path.join(env_tmp,"message{}.wav".format(tam)))
        
            # Only if message is longer than 5 seconds ...
            if msg.duration_seconds > 5.0:
                # ... export to ogg ...
                msg.export(os.path.join(env_tmp,"message{}.ogg".format(tam)), format="ogg", tags=msg_tags)

                # ... and send message and file to Matrix Room
                command = "python3 matrix-commander.py --room {} -a ".format(env_tam[tam]) + os.path.join(env_tmp,"message{}.ogg".format(tam)) + " -m '{}'".format(msg_info)
                os.system(command)
            
            else:
                # Mark MessageInfo as too short for the log
                msg_info += " < 6 sec (not posted)"

            # Show that message is new
            print("** " + msg_info)
        
            # Mark processed messages as 'read'
            fc.call_action("X_AVM-DE_TAM1", "MarkMessage", NewIndex=tam, NewMessageIndex=int(a['Index']), NewMarkedAsRead=1)
            
        else:
            # Show that message is already read
            print("__ " + msg_info)

    tam_no = a['Called']
    lastcall2matrix(tam,tam_no)

        

def multitam(tams):
    for tam in tams.keys():
        print("Check TAM {}.".format(tam))
        fritzab2matrix(tam)




if __name__ == "__main__":

    
    multitam(env_tam)
    ### Monitor the FritzBox and trigger the main script whenever a call disconnects ###
    ###################################################################################
    endedCall(multitam,env_tam, env_ip)

        




        



        
