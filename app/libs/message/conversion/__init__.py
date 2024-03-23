
import wave, ctypes


### Convert fb speex format to wav ###
######################################
"""
This piece of code is just copied & pasted from https://git.savannah.nongnu.org/cgit/fbvbconv-py.git/tree/fbvbconv.py
which has kindly managed to convert the messages of the answering machine of fritzboxes from a specially configured Speex format to a wave file. All appreciation to the author(s).
"""

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
