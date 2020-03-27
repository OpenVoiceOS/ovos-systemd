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

## Mycroft as user service

### Unit Files
Unit files for user services can be installed in a couple of [different places](https://www.freedesktop.org/software/systemd/man/systemd.unit.html#User%20Unit%20Search%20Path). I believe there is no right or wrong here, but going to pick one; ~/.config/systemd/user/

So for now, to manually install these unit files for testing, copy them to that place;
`cp user/* ~/.config/systemd/user/`

We can then enable them to be auto started when the user logs in;
`systemctl --user enable mycroft.service mycroft-messagebus.service mycroft-audio.service mycroft-voice.service mycroft-skills.service mycroft-enclosure.service`

To start them manually now without a reboot, just run;
`systemctl --user start mycroft.service`
All different sub unit files will automatically be started as well. If for whatever reason one of the sub units need to be sarted/stopped/restarted that can be done with similar command (example);
`systemctl --user restart mycroft-voice.service`

If you restart your system now then Mycroft will be started automatically once you log in (the default for Picroft). After your last session is closed, your user's systemd instances (and with it, our Mycroft services) will shutdown. 

You can make your user's systemd instances independent from your user's sessions (so that our Mycroft services starts at boot time even if you don't log in and also keeps running until a shutdown/reboot) with the following command;
`sudo loginctl enable-linger $USER`

## Mycroft as system service

### Unit Files

<To Do>


## Thing to discuss / Way forward
Above installation steps can be added/changed within the setup bash script. However a couple of things I want to discuss about the best way forward.
- Do we want to install these systemd units only for the user?
- Or do we want to offer them to be installed as systemwide services as well? (requires root)
- Do we want to include the enable-linger for the user unit files? (requires root)

Above unit files do automaticaly restart themselfs if the terminiate, however with Systemd we could implement Notify/Watchdog support. However this requires some changes to mycroft-core.

## Notifying systemd when the Service is Ready.
Our mycroft.service dummy unit is used to start mycroft-messagebus.service. All other units are only being started if the messagebus is started. However currently there is no way for systemd to know the mycroft-message bus is actually started properly. 

You can notify systemd once it has completed its initialization of a program. This allows systemd to delay starting these sub units until mycroft-messagebus service is really ready.

These notification is done using so called "[sd_notify](https://www.freedesktop.org/software/systemd/man/sd_notify.html)" system calls. We can use that with a simple additional requirements from "python-systemd". When mycroft-messagebus is fully started and ready we can let systemd know by;
`import systemd.daemon
systemd.daemon.notify('READY=1')`

We can then convert our simple unit files by changing them to "Type=notify" and all our unit files will only be started after the message-bus is ready to rock and role.

This is only a small thing as mycroft already restarts connection to the message-bus if it fails or not ready, however changing to Type=notify also opens the path to using proper Watchdog polling.

I have linked to watchdog info before, so if there is interest for it we can start that process as well. I think using systemd with notify and watchdog supports make the whole system very robust as;
- Different services are automatically be restarted if they stopped petting the dog
- If for some reason failed services keep restarting/failing we can auto reboot a device to get it back online automatically
- With hardware watchdog support, we can auto reboot if the whole system hangs.


Open for feedback. I am no expert to it also, so just want to open the disccusion about what path should be the best.


