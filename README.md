# FritzAB2Matrix

A fork of this [repo](https://git.ismus.net/homer77/FritzAB2Matrix) which removes the sendig of the voice message via matrix and adds some tweaks. __FritzAB2Matrix__ reads out the answering machine (_TAM_) of a _Fritz!Box_ in your LAN.

## Features
 * Set _MARK\_MESSAGE\_READ_=False if you do not want to mark voice messages retrieved to be marked as read.
 * Set _DELETE\_MESSAGE__=True if you do want to delete voice messages retrieved.

## Installation
If you like to test this repository you are recommended to use one of the following two options.
### Necessary preparations for both cases
 * Create a new user (e.g. "fritzab") in your _Fritz!Box_. **Don't use your default admin account!**
   * This user needs only the privileges regarding voice messages and to read from box's storage.
   * As you only need to access the _FRITZ/voicebox/rec/_ path you should remove the right to read and write everything and add only this path and only with reading privilege.
     * __Beware!__ If you use a USB device as expanded storage for your _Fritz!Box_ and allowed the TAM to use it for storing more messages you will need another path (e.g. _Storage-01/FRITZ/voicebox/rec/_). You also have to add the FRITZ_VOICEBOX_PATH variable in your _.env_ file (see below) according to that difference.
 * You have to activate __Call Monitoring__ on your _Fritz!Box_ by using one of the connected phones and call `#96*5*`.
   * Call monitoring watches the box and the __FritzAB2Matrix__ is triggered every time a call disconnects.
   * If you cannot activate Call Monitoring the only way to use __FritzAB2MAtrix__  will be to have a cron job call it regularly. 

### virtualenv
 * Create a new folder wherever you like in your home directory.
   * Make it a virtual environment by `python3 -m venv <new folder>` and `source <new folder>/bin/activate`.
   * `cd <new folder>`
 * Clone the repo.
 * Inside the repo run `pip install --upgrade pip && pip install -r requirements.txt`
 * Create an `.env` file with your favourite editor:
 ```
FRITZ_USERNAME="fritzab2matrix"
FRITZ_PASSWORD="S0meSecretPa5sw02d"
FRITZ_IP="192.168.178.1" 
# optional, default values are set automatically
# FRITZ_VOICEBOX_PATH="fritz.nas/FRITZ/voicebox"
# MARK_MESSAGE_READ="True"
# DELETE_MESSAGE="False"
# FRITZ_TAM="0"
 ```
__.env__

 *
    * Adjust it according to your data.
 * After all that you can finally run `./fritzab2.py` and your TAM messages should be downloaded automatically once recorded to /tmp/rec.
### Docker
Provided you have docker and docker-compose installed on your system:
 * Clone the repo and cd into it.
 * Create the above mentioned `.env` file.
 * Run `docker-compose -f docker/docker-compose.yml build` and watch docker work some minutes.
 * After that slightly edit the `docker-compose.yml`
   * and add
```
  
   volumes:
      - /some/path/recordings:/recordings
```

### Special Thx
Gratitude to all people that enabled that project by their passionate work and will to share it!
Especially to
 * https://git.ismus.net/homer77/FritzAB2Matrix 
 * https://github.com/kbr/fritzconnection
 * https://github.com/8go/matrix-commander
 * https://github.com/poljar/matrix-nio/
 * https://github.com/jiaaro/pydub/
 * https://git.savannah.nongnu.org/cgit/fbvbconv-py.git/
 
 
