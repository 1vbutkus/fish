import os.path
from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

pygame.mixer.init()

_dirPath = os.path.abspath(os.path.dirname(__file__))
_alarmFilePath = os.path.join(_dirPath, 'emergency006.wav')
assert os.path.isfile(_alarmFilePath), f'AlarmFileNotCount: {_alarmFilePath}'


def alarm():
    pygame.mixer.music.load(_alarmFilePath)
    pygame.mixer.music.play()
    print("Alarm!")


def __dummy__():
    alarm()
