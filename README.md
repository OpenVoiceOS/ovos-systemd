# mycroft-systemd

**Work in progress.** These unit files need the [`service-hooks`](https://github.com/forslund/mycroft-core/tree/service-hooks) branch of mycroft-core until that branch merges into the main repository.

This repository holds systemd unit files and Python startup wrappers for the Mycroft voice assistant stack. The units let systemd manage the assistant's services (message bus, audio, voice, skills, and enclosure) as a group.

Systemd supports both system services and user services. A system service runs in the system's own systemd instance and serves the whole machine. A user service runs in a separate systemd instance tied to one user account.

A main `mycroft.service` unit starts the sub-units:

- message-bus
- audio
- voice
- skills
- enclosure

![Diagram of the systemd unit flow for the Mycroft services](https://www.j1nx.nl/wp-content/uploads/2020/02/systemd-flow.png)

Starting `mycroft.service` starts all the sub-units. Each sub-unit can restart on its own, without stopping the others. This setup replaces the `./start-mycroft.sh all` script.

## Getting the sources

This repository is meant to sit inside the `mycroft-core` directory. It assumes `mycroft-core` is installed at `~/mycroft-core`. If your installation lives elsewhere, adjust the paths in the unit files to match.

To install:

```sh
cd ~/mycroft-core
git clone https://github.com/j1nx/mycroft-systemd.git
```

## Running Mycroft as a user systemd service

Use this method for desktop installations.

### Unit files

User unit files can go in any of the [locations systemd searches](https://www.freedesktop.org/software/systemd/man/systemd.unit.html#User%20Unit%20Search%20Path). This repository uses `~/.config/systemd/user/`.

Copy the unit files there:

```sh
cp mycroft-systemd/user/* ~/.config/systemd/user/
```

Enable them to start automatically at login:

```sh
systemctl --user enable mycroft.service
```

Start them now, without a reboot:

```sh
systemctl --user start mycroft.service
```

All the sub-units start automatically with `mycroft.service`. To start, stop, or restart one sub-unit on its own, run a command like:

```sh
systemctl --user restart mycroft-voice.service
```

After a reboot, Mycroft starts automatically once you log in. When your last session closes, the user systemd instance (and the Mycroft services with it) shuts down. This way, Mycroft only runs while you are logged in, which fits most desktop setups.

To start Mycroft regardless of login state, enable lingering for the user:

```sh
sudo loginctl enable-linger <USER>
```

Replace `<USER>` with the account that runs Mycroft. This has the same effect as installing the system service files described in the next section.

## Running Mycroft as a system systemd service

Use this method for headless installations.

### Unit files

System service files live in `/etc/systemd/system/` and need root access to install:

```sh
sudo cp mycroft-systemd/system/* /etc/systemd/system
```

Enable them to start at boot:

```sh
sudo systemctl enable mycroft.service
```

Start them now, without a reboot:

```sh
sudo systemctl start mycroft.service
```

## Notifying systemd when a service is ready

The `mycroft.service` unit starts `mycroft-messagebus.service` first. Every other unit waits for the message bus to report ready before it starts. The Python startup wrappers send this ready signal to systemd using [`sd_notify`](https://www.freedesktop.org/software/systemd/man/sd_notify.html) calls. The same mechanism reports when a service stops.

## Automatic restarts

A unit restarts itself when:

- the service fails, quits, or errors out
- the service does not send its ready notification within one minute
- the service does not send a watchdog message within 30 seconds (the service hangs)

A unit stops trying to restart after 4 attempts within 5 minutes.

## Watchdog

Each unit uses a software watchdog. If the service wrapper does not tell systemd in time that the service is still running, systemd treats the service as hung and restarts it. After 4 restarts within 5 minutes, systemd gives up, and the device usually needs a reboot to recover. To automate this recovery, comment out the `StartLimitAction=reboot-force` line in the unit files.

You can pair the software watchdog with a hardware watchdog, which forces a reboot if the whole system hangs. Read more in this [blog post on watchdogs](http://0pointer.de/blog/projects/watchdog.html).
