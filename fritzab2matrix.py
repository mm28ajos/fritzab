

from fritzconnection import FritzConnection
from dotenv import load_dotenv
from pydub import AudioSegment
import urllib.request
import xmltodict
import sys, os
import smbclient
import ctypes
import wave



## Get environment variables from the .env file which will be ignored by git
load_dotenv()
env_user = os.environ.get('FRITZ_USERNAME')
env_pass = os.environ.get('FRITZ_PASSWORD')
env_ip = os.environ.get('FRITZ_IP')

### CHECK AND GET MESSAGES FROM FRITZBOX ###
############################################

## Connect to the FritzBox in the LAN
# We don't use tls because the self-signed cert of the box leads to a malfunction in urllib later on.
fc = FritzConnection(address=env_ip, user=env_user, password=env_pass, use_tls=False)



## Get info about messages from the main answering machine
message_list = fc.call_action("X_AVM-DE_TAM1", "GetMessageList", NewIndex=0)
message_list_url = message_list['NewURL']


### Convert fb speex format to wav ###
######################################
# c&p that from https://git.savannah.nongnu.org/cgit/fbvbconv-py.git/tree/fbvbconv.py

speexlib = ctypes.cdll.LoadLibrary("libspeex.so.1")
SPEEX_SET_SAMPLING_RATE = 24
SPEEX_GET_FRAME_SIZE = 3

class SpeexMode(ctypes.c_void_p):
    pass
class Speex(ctypes.c_void_p):
    pass
class SpeexBits(ctypes.Structure):
    _fields_ = [
        ('chars', ctypes.c_char_p),
        ('nbBits', ctypes.c_int),
        ('charPtr', ctypes.c_int),
        ('bitPtr', ctypes.c_int),
        ('owner', ctypes.c_int),
        ('overflow', ctypes.c_int),
        ('but_size', ctypes.c_int),
        ('reserved1', ctypes.c_int),
        ('reserved2', ctypes.c_void_p)
    ]

speex_lib_get_mode = speexlib.speex_lib_get_mode
speex_lib_get_mode.restype = SpeexMode
speex_decoder_init = speexlib.speex_decoder_init
speex_decoder_init.restype = Speex
speex_decoder_ctl = speexlib.speex_decoder_ctl
speex_bits_init = speexlib.speex_bits_init
speex_bits_read_from = speexlib.speex_bits_read_from
speex_decode_int = speexlib.speex_decode_int
speex_bits_remaining = speexlib.speex_bits_remaining
speex_bits_destroy = speexlib.speex_bits_destroy


def speex_convert(inp, outp):
#    rec = open(inp, 'rb').read()
    rec = inp.read()
    wav = wave.open(outp, 'wb')
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(8000)

    mode = speex_lib_get_mode(0)
    speex = speex_decoder_init(mode)
    speex_decoder_ctl(speex, SPEEX_SET_SAMPLING_RATE, ctypes.byref(ctypes.c_int(8000)))
    bits = SpeexBits()
    speex_bits_init(ctypes.byref(bits))
    frame_size = ctypes.c_int()
    speex_decoder_ctl(speex, SPEEX_GET_FRAME_SIZE, ctypes.byref(frame_size))

    output = ctypes.create_string_buffer(2000)
    offs = 0
    while offs < len(rec):
        nbytes = rec[offs]
        offs += 1
        if nbytes != 0x26:
            continue
        buf = ctypes.create_string_buffer(rec[offs:offs + nbytes])
        offs += nbytes
        speex_bits_read_from(ctypes.byref(bits), buf, ctypes.c_int(nbytes))
        # this loop looks strange, but its like in roger router and seems to work
        for i in range(2):
            rc = speex_decode_int(speex, ctypes.byref(bits), output)
            if rc == -1:
                break
            elif rc == -2:
                print("Decoding error: corrupted stream?");
                break
            if speex_bits_remaining(ctypes.byref(bits)) < 0:
                print("Decoding overflow: corrupted stream?");
                break
        wav.writeframes(output[0:2 * frame_size.value])

    wav.close()
    speex_bits_destroy(ctypes.byref(bits))



# Build the url to download the message via smb
# smb://192.168.1.1/fritz.nas/FRITZ/voicebox/rec

def build_download_url(mid, tam=0):
    url = r"//" + env_ip + r"/fritz.nas/FRITZ/voicebox/rec/rec." + str(tam) + r"." + str(mid).zfill(3)
    return url

def download_speex_file(smb_url):
    smbclient.register_session(server=env_ip, username=env_user, password=env_pass, auth_protocol="ntlm")
    fd = smbclient.open_file(smb_url, mode="rb")
    return fd
    

with urllib.request.urlopen(message_list_url) as f:
    doc = f.read()
    # Convert the xml formatted message list to dict
    messages = xmltodict.parse(doc)


for a in messages['Root']['Message']:

    msg_info = a['Date'] + " " + a['Number'] + " (" + a['Name'] + ") " 
    
    # Select only new messages
    message_new = bool(int(a['New']))
    
    # Select only messages longer than 5 sec
    # No. Unfortunaetly the MessageList excludingly puts 0:01 into Duration tag.
    
    if message_new == True:

        smb_url = build_download_url(a['Index'])
        speex_fd = download_speex_file(smb_url)
        speex_convert(speex_fd, "/tmp/message.wav")
        # Convert wav to ogg
        msg = AudioSegment.from_wav("/tmp/message.wav")
        
        # Only convert and upload if message is longer than 5 seconds.
        if msg.duration_seconds > 5.0:
            msg.export("/tmp/message.ogg", format="ogg")

            ### POST MESSAGES TO MATRIX PRIVATE CHAT ###
            ############################################
            
            # Formatting message
            
            # Send message and file to Matrix Room
            command = "python3 matrix-commander.py -a /tmp/message.ogg -m '{}'".format(msg_info)
#            os.system(command)
            
        else:
            # Mark MessageInfo as too short 
            msg_info += " < 6 sec (not posted)"
        print("** " + msg_info)
        
        # Mark processed messages as 'read'
        fc.call_action("X_AVM-DE_TAM1", "MarkMessage", NewIndex=0, NewMessageIndex=int(a['Index']), NewMarkedAsRead=1)                

        
            
    else:
        print("__ " + msg_info)
        continue

    continue








        



        



