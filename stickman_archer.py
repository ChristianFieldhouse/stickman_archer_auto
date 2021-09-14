import subprocess
import sys
import time
from datetime import datetime
#import threading
import os
from PIL import Image
import numpy as np
from scipy.optimize import minimize

bow = (470, 778) #(468, 683)
enemy0 = (1863, 683)
pause = (2229, 50) #(2082, 51)
restart = (1246, 933) #(1240, 777)
upgrades = [
    (834, 553),
    (1164, 553),
    (1500, 555),
]
# some rough facts:
grav = 580 #2 * (1080 - bow[1]) # takes ~ 1s to reach the bottom of the screen
velo = 1250 # takes ~3 seconds to go up then down
power = 500 # hopefully max


start = (1690, 700)
gas = (2050, 850)
brake = (380, 850)
twitter = (710, 733)

def threadclick(xy, t=300):
    x, y = xy
    #return subprocess.run(["adb", "shell",  "input", "tap", f"{x}", f"{y}"])
    threading.Thread(
        target=subprocess.run,
        args=(["adb", "shell", "input", "swipe", f"{x}", f"{y}", f"{x}", f"{y}", f"{t}"],),
    )

def click(xy, t=200):
    x, y = xy
    subprocess.run(["adb", "shell", "input", "swipe", f"{x}", f"{y}", f"{x}", f"{y}", f"{t}"])

def fire(angle, power=power, t=100):
    angle = np.pi * angle / 180
    subprocess.run(["adb", "shell", "input", "swipe", f"{1000}", f"{500}", f"{int(1000 - power*np.cos(angle))}", f"{int(500 + power*np.sin(angle))}", f"{t}"])

def spray(angles, power=power, t=30, d=100):
    #angles = np.linspace(angles[0] * np.pi/180, angles[1] * np.pi/180, n)
    #print("".join(
    #        f"input swipe 1000 500 {int(1000 - power*np.cos(angle))} {int(500 + power*np.sin(angle))} {t} & "
    #        for angle in angles
    #    )[:-3]
    #)
    angles = [np.pi * angle / 180 for angle in angles]
    #print(angles)
    print("spraying", len(angles))
    subprocess.run([
        "adb", "shell",
        "".join(
            f"(sleep {i*d/1000} && input swipe 1000 500 {int(1000 - power*np.cos(angle))} {int(500 + power*np.sin(angle))} {t}) & "
            for i, angle in enumerate(angles)
        )[:-3]
    ])


def find_angle(diff, v=velo, g=grav):
    a, b = diff # position relative to archer
    guess = 35 * np.pi/180
    def at_a(angle, v, g):
        t = a/(np.cos(angle) * v)
        y = v * np.sin(angle) * t - t**2 * g /2
        #print("for", angle, "at a, y is", y)
        return y
    def score(angle):
        return abs(at_a(angle, v=v, g=g) - b)
    theta = minimize(score, guess).x[0]
    return theta * 180/np.pi

def fire_at(positions, repeat=1):
    if not positions:
        return
    diffs = [
        (x - bow[0], bow[1] - y)
        for x, y in positions
    ]
    thetas = [
        find_angle(diff)
        for diff in diffs
    ]
    print(thetas)
    spray(thetas * repeat)

def redo():
    click(pause)
    click(restart)

def continuestart():
    while getstatus() != "start":
        click(continue_button)
    click(start)

def getscreen():
    os.system("adb exec-out screencap -p > shot.png")
    im = Image.open("shot.png")
    ar = np.array(im)
    return ar

def getstatus(show=False):
    """Probes exact pixel values to know which part
    of the app you're in. These would probably have to
    change for different devices."""
    getscreen()
    im = Image.open("shot.png")
    #print(im.getpixel(pause))
    if (im.getpixel(restart) == (181, 233,  97, 255)): #(242, 189,  71, 255)):
        return "dead"
    if (im.getpixel(pause) == (54,  62,  83, 255)): #(247, 221,  87, 255)):
        # in game, have to figure out where the enemies are:
        ar = np.array(im)
        bar_corners = (ar[1:, :-1, 0] != 106) & (ar[:-1, 1:, 0]!=106) &(ar[:-1, :-1, 0]!= 106) & (ar[1:, 1:, 0]== 106) & ((ar[1:, 1:, 1] == 229) | (ar[1:, 1:, 1] == 228)) & (ar[1:, 1:, 2] == 82)
        if show:
            Image.fromarray(bar_corners).show()
        #print(np.any(bar_corners))
        #print(np.where(bar_corners))
        return "gameplay", np.where(bar_corners)
    if (im.getpixel(twitter) == (76, 167, 225, 255)):
        return "continue"
    return "dunno"

def go_to_start():
    status = getstatus()
    if status == "start":
        click(start)
        return
    if status == "gameplay":
        redo()
        return
    continuestart()

def headshots():
    print("at start --------------")
    status = "gameplay"
    while (status != "died"):
        status = getstatus()
        try:
            status, enemies = status    
        except:
            # maybe dead
            click(restart) #upgrades[0])
        print(enemies)
        fire_at(
            ([(1000, bow[1] - x) for x in range(0, 500, 100)] if len(enemies) == 0 else [
                (
                    enemy[::-1][0] + 62,
                    enemy[::-1][1] - 160,
                )
                for enemy in list(zip(*enemies))
            ]) + [(1000, bow[1]) for x in range(3)],
            repeat=2,
        )
        #time.sleep(3)
    return exact_money

def just_spray():
    print("at start --------------")
    status = "gameplay"
    while True:
        status = getstatus()
        print(status)
        if status == "dead":
            click(restart) #upgrades[0])
        for _ in range(5):
            spray(list(range(10, 50, 5)), t=60,  d=100)
    return exact_money

def tryit():
    total_profit = 0
    go_to_start()
    while True:
        total_profit += moonlander_moon_clean()
        print("total profit about", total_profit)

#tryit()
