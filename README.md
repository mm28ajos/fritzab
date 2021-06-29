# FritzAB2Matrix

__FritzAB2Matrix__ reads out the answering machine (_TAM_) of a _Fritz!Box_ in your LAN and posts the messages into a private chat in the __matrix__ network. While you could let your _Fritz!Box_ send the messages by mail - unencrypted of course - the matrix chat is __e2e encrypted__. Which kindly acknowledges the privacy of any caller that leaves a message for you.

Uses the python based cmd-line-tool [matrix-commander](https://github.com/8go/matrix-commander) so the matrix-commander.py in this repo is just a copy of that file to ease testing.

## Installation
If you like to test this repository you are recommended to use one of the following two options.
### Necessary preparations for both cases
 * Create a new user (e.g. "fritzab") in your _Fritz!Box_. **Don't use your default admin account!**
   * This user needs only the privileges regarding voice messages and to read from box's storage.
   * As you only need to access the _FRITZ/voicebox/rec/_ path you should remove the right to read and write everything and add only this path and only with reading privilege.
 * You have to activate __Call Monitoring__ on your _Fritz!Box_ by using one of the connected phones and call `#96*5*`.
   * Call monitoring watches the box and the __FritzAB2Matrix__ is triggered every time a call disconnects.
   * If you cannot activate Call Monitoring the only way to use __FritzAB2MAtrix__  will be to have a cron job call it regularly. 

### virtualenv
 * Create a new folder wherever you like in your home directory.
   * Make it a virtual environment by `python3 -m venv <new folder>` and `source <new folder>/bin/activate`.
   * `cd <new folder>`
 * Clone the repo.
 * Inside the repo run `pip install --update pip && pip install -r requirements.txt`
 + Create an `.env` file with your favourite editor:
 ```
FRITZ_USERNAME="fritzab"
FRITZ_PASSWORD="SomeRand0mPa55word"
FRITZ_IP="192.168.178.1" 
FRITZ_TMP="/tmp"

 ```
    * Adjust it according to your data.
 * For matrix-commander.py to work you need to run it manually the first time by `python3 matrix-commander` and follow the emerging dialog by putting in your matrix account data.
 * After all that you can finally run `./fritzab2matrix.py` and your TAM messages should be posted in the chosen matrix chat.
### Docker
Provided you have docker and docker-compose installed on your system:
 * Clone the repo and cd into it.
 * Create the above mentioned `.env` file.
 * Run `docker-compose -f docker/docker-compose.yml build` and watch docker work some minutes.
 * After that slightly edit the `docker-compose.yml`
   * and add
   ```
   volumes:
      - ../.:/app
	  ```
   * so that your repo is used as volume for the `/app` folder. So everything you change in the repo's folder will affect the docker container.
 * For __matrix-commander.py__ to work you need to run it manually the first time by `python3 matrix-commander` and follow the emerging dialog by putting in your matrix account data.
   * With docker that means that you need to open an _interactive shell_ in the running container (`docker-compose -f docker/docker-compose.yml exec app /bin/bash` and run this command there.
   * Follow the appearing dialog and input your matrix account data.
 * After all that the running docker container should watch your box and your TAM messages should be posted in the chosen matrix chat.
   
### Special Thx
Gratitude to all people that enabled that project by their passionate work and will to share it!
Especially to
 * https://github.com/kbr/fritzconnection
 * https://github.com/8go/matrix-commander
 * https://github.com/poljar/matrix-nio/
 * https://github.com/jiaaro/pydub/
 * https://git.savannah.nongnu.org/cgit/fbvbconv-py.git/
 
 
