from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from notifypy import Notify
import pyautogui as gui
import subprocess
import pyvolume
import re

output = ''
volume_shift = 10
key_output = ''

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print('Running on IP:', s.getsockname()[0])
s.close()

def index(request):
    context = {'output': output, 'key_output': key_output}
    return render(request, template_name='simple_page/index.html', context=context)

def submit(request):
    global output
    try:
        output = subprocess.check_output(request.POST['msg'].split(' '), text=True)
    except:
        output = 'Command failed'

    # notification = Notify()
    # notification.title = "Message Recieved"
    # notification.message = request.POST['msg']
    # notification.send(block=False)
    return HttpResponseRedirect(reverse('index'))

def playpause(request):
    subprocess.run('playerctl play-pause'.split(' '))
    return HttpResponseRedirect(reverse('index'))

def change_volume(request, add):
    current = int(re.search(r'(\d+)%', subprocess.check_output('amixer sget Master'.split(' '), text=True)).group(1))
    if add > 0:
        pyvolume.custom(min(max(current + volume_shift, 0), 100))
    else:
        pyvolume.custom(min(max(current - volume_shift, 0), 100))
    return HttpResponseRedirect(reverse('index'))

def key(request):
    global key_output
    key = request.POST['key']
    key_output = ''
    if key in gui.KEY_NAMES:
        gui.press(key)
    elif key == 'help':
        key_output = f"{gui.KEY_NAMES}"
    else:
        gui.write(key)
    return HttpResponseRedirect(reverse('index'))

def arrow(request, key):
    gui.press(key)
    return HttpResponseRedirect(reverse('index'))
