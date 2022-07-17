# auto-timeclock365
The ultimate way to punch in your working ours in a breaze.

Is a script that meant to save time by automaticlly "punch in" working hours by automatically punch-in daily in certin hour (using crontab) and saves the after work.


# Background story
My working place salery team change its workers monthly hours time card calaculation system, in accordingly that system change consume alot more time and work from me.
from 5 minute a month to 20, from few keyboard clicks to few hounderds, meaning I proactivly needs to interact with the system.

# Prerequisites (any machine that runs crontab)
1. Virtual machine (Debain-server) 1 core, 1GB Ram, 8-10GB storage.  # plaese read the note we you shouldn't use ubuntu for this.
2. xvfb - virtual graphic environment in order to run Firefox in cli environment.
3. Firefox - the script uses firefox cause it just the best broswer.
4. Crontab - using ‘crontab -e’, to set the actual time the script will work. 

# Installation on the machine.
1. git clone to the destintaion folder
2. rename .env.example to .env.
3. in (edit) .env file add your username, password and edit OPERSTIONAL flag to False in order to dry run.
4. take the code for a spin.
5. set scheduled in my case crontab, you can run on windows as well using the task scheduler.

crontab example: This means that the crontab wil run the code from sunday to thursday every day on 18:35.
```
 m h  dom mon dow   command
35 18  *  *   0-4   cd /home/userdirectory/auto-timeclock365/; /usr/bin/python3 main.py
```


# Note
This script corrently works only on https://live.timeclock.com/login on its hebrew version.

# How to setup LXC with firefox and virtual graphic environment,
Debian OS should be used since ubuntu uses snapd to install firefox and it causes failures mustly on lxc containers.
```
apt install xvfb

#after installation
Xvfb :99 -ac &
export DISPLAY=:99    

#Then install firefox from debian repo.
apt install firefox-ers

# dry run: login to the machine using ssh -X parameter and with a supported client and execute the following command.

firefox  

#After few seconds you should see firefox on you environment.
```
