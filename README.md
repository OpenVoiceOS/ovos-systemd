## WARNING: Work in progress
This repository is a work in progress. For these to run properly, you need to run the following mycroft-core version till this get PR-ed and merged into the main repository;
https://github.com/forslund/mycroft-core/tree/service-hooks

# mycroft-systemd
Many Linux distributions use systemd to manage the system's services (or *daemons*), for example to automatically start certain services in the correct order when the system boots.

Systemd supports both system and user services. System services run in the system's own systemd instance and provide functionalities for the whole system and all users. User services, on the other hand, run in a separate systemd instance tied to a specific user.

There is one main (dummy) mycroft.service unit that handles the different sub unit files for;
- message-bus
- audio
- voice
- skills
- enclosure

![image](https://www.j1nx.nl/wp-content/uploads/2020/02/systemd-flow.png)

Starting the mycroft.service unit will start all different sub units. All sub units can be restarted without interfering with the others. This system could replace the "./start-mycroft.sh all" script.

## Getting the sources
This repository is setup to be pulled into the "mycroft-core" directory. It is assumed that mycroft-core is installed within the users home directory ( /home/<USER>/mycroft-core ) according their documentation. If you have it installed somewhere else, you will need to adjust the paths within the different files for this to work.

So to install:
`cd ~/mycroft-core`
`git clone https://github.com/j1nx/mycroft-systemd.git`

## Running Mycroft as user systemd service (Recommended for Desktop installations)

### Unit Files
Unit files for user services can be installed in a couple of [different places](https://www.freedesktop.org/software/systemd/man/systemd.unit.html#User%20Unit%20Search%20Path). I believe there is no right or wrong here, but going to pick one; ~/.config/systemd/user/

So to install these unit files, copy them to that place;
`cp mycroft-systemd/user/* ~/.config/systemd/user/`

We can then enable them to be auto started when the user logs in;
`systemctl --user enable mycroft.service`

To start them manually now without a reboot, just run;
`systemctl --user start mycroft.service`

All different sub unit files will automatically be started as well. If for whatever reason one of the sub units need to be started, stopped or restarted that can be done with similar command (example);
`systemctl --user restart mycroft-voice.service`

If you restart your system now then Mycroft will be started automatically once you log in. After your last session is closed, your user's systemd instances (and with it, our Mycroft services) will shutdown. 

This way Mycroft is ONLY started and therefor listening when you are logged in. For most desktops that is what you would want. If however you want to start Mycroft automatically regardless of being logged in, you can do that by; 

`sudo loginctl enable-linger <USER>`

Change the <USER> in above command to the username of the user running mycroft. Now Mycroft will be started regardless of the user being logged in or not. This is basically the same as installing the system service files described in the next section.

## Running Mycroft as system systemd service (Recommended for Headless installations)

### Unit Files
System service files are installed within the /etc/systemd/system/ directory and therefor require root access to be installed.
`sudo cp mycroft-systemd/system/* /etc/systemd/system`

We can then enable them to be started at boot by;
`sudo systemctl enable mycroft.service`

To start them manually now without a reboot, just run;
`sudo systemctl start mycroft.service`

## Notifying systemd when the Service is Ready.
Our mycroft.service dummy unit is used to start mycroft-messagebus.service. All other units are only being started if the messagebus is started. The python startup wrappers are used to report back to systemd when the service is READY. 
This allows systemd to ONLY start the other service until mycroft-messagebus service is fully up on running.

These notifications is done using so called "[sd_notify](https://www.freedesktop.org/software/systemd/man/sd_notify.html)" system calls.

The same goes for stopping.

## Automatically restarting of services
The systemd service files automatically restarting the service by the following conditions;
- On failure. (service failed/quited/errored out/etc)
- If it haven't received the READY notify within at least one minute.
- If while running doesn't receive a petting the watchdog message within 30 seconds (service hangs)
And gives up after it has restarted itself at least 4 times within the last 5 minnutes.

## Watchdog
The included service files make use of a software based Watchdog. If the service wrapper is not letting systemd now in time that it is still a happy bunny (or dog) which basically means it "hangs", systemd will restart the service. Again if this happes more than 4 times within 5 minutes, something more is going on and it will give up in the end. Most of the times a reboot of the device will fix things. This can be automated by commenting out the "StartLimitAction=reboot-force" line within the systemd service files.

You can compliment the software Watchdog with a hardware based Watchdog. This will force reboot your device if the whole system hangs. MOre information on that in the following blog post;
http://0pointer.de/blog/projects/watchdog.html

