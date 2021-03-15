import time, threading
import pygame, JSON4JSON
from pynput import keyboard
import pynput, random


class SoundThing:
	def __init__(self, preset):
		self.preset = preset
		self.sounds = {}
		pygame.mixer.pre_init()
		pygame.mixer.init()
		pygame.mixer.set_num_channels(24)
		pygame.init()
	#block - if the sound (from the path) is already playing, don't play it.
	#takeover - if the sound (from the path) is already playing, restart it
	#balance - between -1 (left) and 1 (right)
	def play_sound(self, path, balance=0, block=False, takeover=False):
		if path not in self.sounds:
			self.sounds[path] = pygame.mixer.Sound(path)
		thread = threading.Thread(target=self._play_sound, args=(path, balance, block, takeover,))
		thread.start()
	def get_panning(self, balance):
		left = .5
		right = .5
		right = abs(-1 - balance) / 2
		left = abs(1 - balance) / 2
		return (left, right)
	def _play_sound(self, path, balance, block, takeover):
		channel = pygame.mixer.find_channel(True)
		channel.set_volume(*self.get_panning(balance))
		sound = self.sounds[path]
		channel.play(sound)


class Main:
	def __init__(self):
		j4j = JSON4JSON.JSON4JSON()
		j4j.load("config.json", "rules.json")
		self.config = j4j.data
		self.listener = keyboard.Listener(on_press=self.on_key_down, on_release=self.on_key_up)
		self.listener.start()
		j4j.data = {}
		j4j.load(self.config["preset"] + "/preset.json", "./presetRules.json")
		self.preset = j4j.data
		self.events = {}
		for event in self.preset['events']: self.events[event['keyName']] = event
		self.sound = SoundThing(self.preset)
		self.lastKey = ""
		balancemap = """
		`1234567890-=
		~!@#$%^&*()_+
		  qwertyuiop[]\\
		  QWERTYUIOP{}|
		  asdfghjkl;'
		  ASDFGHJKL:"
		   zxcvbnm,./
		   ZXCVBNM<>?
		"""
		self.balanceMap = {}
		for line in balancemap.split("\n"):
			for c,i in zip(line, range(len(line))):
				if c != " ":
					self.balanceMap[c] = {"b":(i - 15/2)/(15/2), "o":False}
		self.main_loop()

	def main_loop(self):
		while True:
			time.sleep(.1)
			pass
	
	def get_sound_path(self, file):
		return self.config['preset'] + "/" + str(file)
	
	def _on_key(self, key, direction="down"):
		if type(key) == pynput.keyboard.KeyCode:
			balance = 0
			self.lastKey = key.char
			try:
				balance = self.balanceMap[key.char]['b']
				onOff = self.balanceMap[key.char]['o']
				if direction == 'down':
					if self.balanceMap[key.char]['o'] == True: return
					self.balanceMap[key.char]['o'] = True
				elif direction == "up":
					self.balanceMap[key.char]['o'] = False
			except: print("oopsie woopsie", key.char)
			if len(self.preset[direction + "Sounds"]) > 0:
				self.sound.play_sound(self.get_sound_path(random.choice(self.preset[direction + "Sounds"])), balance=balance)
		elif type(key) == pynput.keyboard.Key:
			if key._name_ not in self.events and "ALL" in self.events: key._name_ = "ALL"
			if key._name_ in self.events and (self.events[key._name_]['repeat'] == False and self.lastKey == key._name_) == False:
				event = self.events[key._name_]
				selectFrom = direction + "Sounds"
				if len(event[selectFrom]) > 0:
					self.sound.play_sound(self.get_sound_path(random.choice( event[selectFrom] )), balance=event['panning'])
			elif key._name_ not in self.events and self.config['logMissingKeys']:
				print(key._name_)
			self.lastKey = key._name_

	def on_key_down(self, key):
		self._on_key(key)
	def on_key_up(self, key):
		self._on_key(key, direction="up")


if __name__ == "__main__":
	Main()



'''
#for testing purposes
def _test():
	ST = SoundThing(None)
	ST.path = './Presets/1/return-new.mp3'

	for x in range(10):
		ST.play_sound(ST.path, balance=1-(x/5))
		time.sleep(.2)

	time.sleep(5)

'''


