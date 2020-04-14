#!/usr/bin/env python
##########################################################################
# systemd_voice.py
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################
import sdnotify
from mycroft.client.speech.__main__ import main

n = sdnotify.SystemdNotifier()

def notify_ready():
    n.notify('READY=1')
    print('Startup of Mycroft Voice service complete')

def notify_stopping():
    n.notify('STOPPING=1')
    print('Stopping the Mycroft Voice service')

def pet_watchdog():
    n.notify('WATCHDOG=1')

main(ready_hook=notify_ready, stopping_hook=notify_stopping, watchdog=pet_watchdog)