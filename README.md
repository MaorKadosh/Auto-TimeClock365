# auto-timeclock365
Is a script that meant to save time by automaticly "punch in" working hours, by automatically punch-in daily in certin hour (using crontab) and saves the after work.


# Background story
My working place salery team change its worker monthly hours time card calaculation system, in accordingly that system change consume alot more time and work.
from 5 minute a month to 20, from few keyboard clicks to few hounderds, meaning I proactivly needs to interact with the system.

# Prerequisites (any machine that runs crontab)
1. Virtual machine (Debain-server) 1 core, 1GB Ram, 8-10GB storage.
2. xvfb - virtual graphic environment in order to run Firefox in cli environment.
3. Firefox - the script uses firefox cause it just the best broswer.
4. Crontab - using ‘crontab -e’, to set the actual time the script will work. 

# Note
This script works only on https://live.timeclock.com/login on its hebrew version.

# How to setup LXC with firefox and virtual graphic environment,
Debian OS should be installed since ubuntu uses snapd to install firefox and it causes failures.
```apt install xvfb

#after installation
Xvfb :99 -ac &
export DISPLAY=:99    

#Then install firefox
apt install firefox-ers

# ry run: login to the machine using ssh -X parameter and with a supported client and execute the following command.

firefox  

#After few seconds you should see firefox on you environment.```
