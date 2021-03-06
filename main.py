# coding: utf-8

import random
import console
import os.path
import sys
import re

from scene import *

nm = ''
cls = 0
if not os.path.exists('save'):
	nm = console.input_alert('Player name')
	gdr = console.alert('Gender',button1='Male',button2='Female',hide_cancel_button=True)
	cls = console.alert('Choose a class',button1=['Shaman','Shrine Maiden'][gdr],button3='None',button2='Warrior',hide_cancel_button=True)
	level = 1
	hp = 10
	xp = 0
	yen = 0
	familiar = None
	tainted = False
	expansions = 0
else:
	with open('save', 'r') as f:
		nm = f.readline().strip()
		gdr = f.readline().strip()
		cls = f.readline().strip()
		level = int(f.readline().strip())
		hp = int(f.readline().strip())
		xp = int(f.readline().strip())
		yen = int(f.readline().strip())
		familiar = f.readline().strip()
		tainted = f.readline().strip()
		expansions = int(f.readline().strip())
		class tmp(object):
			def __init__(self, attack):
				self.attack = attack
		if familiar == 'None':
			familiar = None
		else:
			familiar = tmp(int(familiar))
		if tainted == 'True': tainted = True
		else: tainted = False

locations = []
enemies = []
moves = []

class Move(object):
	def __init__(self, name, type, attack):
		self.name = name
		self.type = type
		self.attack = attack
		moves.append(self)

class Special(object):
	def __init__(self, name, attack):
		self.name = name
		self.type = 'holy'
		self.attack = attack
		moves.append(self)

class Enemy(object):
	def __init__(self, name, hp, xp, yy):
		self.name = name
		self.hp = hp
		self.attack = 0
		self.xp_yeild = xp
		self.yen_yeild = yy
		enemies.append(self)

class Boss(object):
	def __init__(self, name, hp, atk):
		self.name = name
		self.hp = hp
		self.attack = atk
		self.xp_yeild = 1000
		self.yen_yeild = 10000

class Location(object):
	def __init__(self, boss, text):
		self.boss = boss
		self.text = text
		locations.append(self)

class Player(object):
	defending = False
	def __init__(self, name, gender, cls, level, hp, xppt, yen, familiar, tainted, expansions):
		self.name = name
		self.gender = int(gender)
		self._class = int(cls)
		self._level = int(level)
		self.hp = int(hp)
		self.lvlup = self._level*15
		self._xp = int(xppt)
		self.money = int(yen)
		self.familiar = familiar
		self.tainted = tainted
		self.expansions = expansions
	def save(self):
		with open('save', 'w') as f:
			f.truncate()
			f.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format(self.name, self.gender, self._class, self._level, self.hp, self._xp, self.money))
			if self.familiar:
				f.write(str(self.familiar.attack)+'\n')
			else:
				f.write('None\n')
			f.write(str(self.tainted) or 'False')
			f.write('\n{}'.format(self.expansions))
	def level_up(self):
		self._level += 1
		self.hp += self._level*10
		if self.familiar: self.familiar.attack += self._level*2
		if self._class != 2 and self._level == 10: self._class += 3
		elif self._class != 2 and self._level == 15: self._class += 2
		if self._level == 10 and not self.tainted:
			sp = Special('Pray',82)
			for move in moves:
				if move.type == 'magic':
					moves.remove(move)
		elif self._level == 11 and not self.tainted:
			sp = Special('Lightning',115)
		elif self._level == 12 and not self.tainted:
			sp = Special('Holy Fire',128)
		elif self._level == 13 and not self.tainted:
			sp = Special('Plague',151)
		elif self._level == 14 and not self.tainted:
			sp = Special('Death Angel',174)
		elif self._level == 15 and not self.tainted:
			sp = Special('God\'s Wrath',222)
		self.save()
	def add_xp(self, xppt):
		self._xp += xppt
		if self._xp == self.lvlup:
			self.level_up()
		elif self._xp > self.lvlup:
			xppt = self.lvlup - self._xp
			self.level_up()
			self.add_xp(xppt)
		self.save()
	def gain_money(self, yen):
		self.money += yen
		self.save()
	def pay(self, yen):
		self.money -= yen
		self.save()
user = Player(nm, gdr, cls, level, hp, xp, yen, familiar, tainted, expansions)
user.save()



# bosses (or any special enemy that can only be found a certain way)
rg = Boss('Ryuugami',1000,100)
gd = Boss('Gashadokuro',500,50)

# enemies
en = Enemy('Toire no Hanako-san',20,2,50)
en = Enemy('Kuchisake Onna',20,2,500)
en = Enemy('Dodomeki',20,4,1000)
en = Enemy('Corrupt Koma Inu',30,10,750)
en = Enemy('Eritategoromo',10,2,1500)
en = Enemy('Nopperabou',25,5,1500)
en = Enemy('Kejourou',25,25,500)
en = Enemy('Ubagabi',30,15,100)

# locations
lc = Location(None, 'The building is very cold!')
lc = Location(None, 'The place feels empty, but I know there\'re others here!')
lc = Location(gd, 'You go outside and your ears start ringing profusely!')


# moves
mv = Move('Punch','melee',1)
mv = Move('Kick','melee',1)
mv = Move('Swordplay','melee',5)
mv = Move('Higuchi Inu','magic',15)
mv = Move('Mizu','magic',10)
if user.familiar:
	mv = Move('Summon','magic',user.familiar.attack)

if os.path.exists('exploration'):
	for l in locations:
		for s in open('exploration','r').read().split('\n'):
			if l.text == s:
				locations.remove(l)


class game(Scene):
	enemy = None
	movelist = []
	show_movelist = False
	mv_dictionaries = []
	shop_items = []
	status = ''
	in_battle = False
	shopping = False
	
	def list_moves(self):
		if user._level >= 10 and user._level <= 15:
			self.setup()
		fill(0,1,1)
		stroke(0,0,0)
		stroke_weight(4)
		rect(0,0,200,self.mv_dictionaries[0]['y']+(25/2))
		for move in self.mv_dictionaries:
			text(move['move'].name,'Courier New',25,move['x'],move['y'],6)

	def battle(self):
		background(0,1,1)
		if self.enemy is None:
			self.enemy = random.choice(enemies)
			self.enemy.hp += (user._level*5)
			self.enemy.attack = (2*user._level)+(user._level-1)
			self.enh = self.enemy.hp
			user.hp = hp + (user.expansions*10)
		stroke(0,0,0)
		tint(0,0,0)
		stroke_weight(4)
		text('Attack','Courier New',25,5,75,6)
		text('Defend','Courier New',25,130,75,6)
		text(user.name,'Courier New',25,25,25+(25/2),6)
		text(str(user.hp),'Courier New',25,5+(len(user.name)*25),25+10,6)
		text(self.enemy.name,'Courier New',25,5,self.h-25,6)
		text(str(self.enemy.hp),'Courier New',25,25,self.h-55,6)
		no_fill()
		rect(0,0,self.w,100)
		rect(0,self.h-100,self.w,100)
		
		if self.show_movelist:
			self.list_moves()
		if self.enemy.hp <= 0:
			self.enemy.hp = self.enh
			user.add_xp(self.enemy.xp_yeild)
			user.gain_money(self.enemy.yen_yeild)
			self.enemy = None
			self.in_battle = False
			user.save()
		if user.hp <= 0:
			with open('death.txt','w') as f:
				f.write('{} was killed by {} at level {}'.format(user.name, self.enemy.name, user._level))
			if os.path.exists('exploration'):
				os.remove('exploration')
			os.remove('save')
			self.stop()
	
	def attack(self, move):
		self.enemy.hp -= move.attack+(2*(user._level-1))
		if self.enemy.hp <= 0 or user.hp <= 0:
			return
		user.hp -= self.enemy.attack
		if user.defending:
			user.hp -= self.enemy.attack/2
			user.defending = False
		if move.type == 'magic' and not user.tainted:
			user.tainted = True
			user.save()
	
	def shop(self):
		fill(0,1,1)
		rect(-4,-4,self.w+8,self.h+8)
		self.shop_items = ['HP Expansion ¥5000','Sell HP ¥-5000','Back']
		text('¥'+str(user.money),'Courier New',50,5,25,6)
		y = 30
		for item in self.shop_items:
			text(item,'Courier New',25,self.w/2,self.h-y,5)
			y += 30

	def setup(self):
		self.w, self.h = self.size
		magic = []
		other = []
		for move in moves:
			if move.type == 'magic': magic.append(move)
			else: other.append(move)
		if cls == 0: self.movelist = magic
		elif cls == 1: self.movelist = other
		else: self.movelist = moves
		y = 30
		for move in range(0, ((user._level/3)+1)*3):
			try:
				if self.movelist[move].name != 'Summon':
					self.mv_dictionaries.append({'x': 5, 'y': self.h-y, 'move': self.movelist[move]})
					y += 30
			except:
				pass
		for move in self.movelist:
			if move.name == 'Summon':
				self.mv_dictionaries.append({'x': 5, 'y': self.h-y, 'move': move})
				break

	def draw(self):
		background(0,1,1)
		tint(0,0,0)
		stroke(0,0,0)
		stroke_weight(4)
		text('Battle','Courier New',25,self.w/2,self.h-30,5)
		text('Shop','Courier New',25,self.w/2,self.h-60,5)
		text('Explore','Courier New',25,self.w/2,self.h-90,5)
		text('Challenge Ryuugami','Courier New',25,self.w/2,self.h-120,5)
		cls = ''
		if user.gender == 0: cls = ['Shaman','Priest']
		else: cls = ['Shrine Maiden','Priestess']
		cls = [cls[0],'Warrior','No-Class',cls[1],'Samurai','Kami','Emperor']
		text(cls[user._class],'Courier New',25,5,25,6)
		text(self.status,'Courier New',125/12,self.w,55,4)
		if self.in_battle: self.battle()
		if self.shopping: self.shop()
		fill(0,1,0)
		try:
			ratio = float(user._xp)/float(user.lvlup)
			rect(0,0,self.w*ratio,10)
		except: pass
	
	def touch_ended(self, touch):
		x, y = touch.location
		
		if y >= self.h-100 and self.in_battle and not self.show_movelist:
			tmp = [True,True,True]
			for i in range(0, 7):
				tmp.append(False)
			tmp = random.choice(tmp)
			if tmp:
				self.in_battle = False
				if not user.familiar:
					mv = Move('Summon','magic',self.enemy.attack)
					self.setup()
				user.familiar = self.enemy
				self.status = 'Successfully captured {}!'.format(self.enemy.name)
				self.enemy = None
				self.in_battle = False
				user.save()
			else:
				user.hp -= self.enemy.attack
		
		if x >= (self.w/2)-75 and x <= (self.w/2)+75 and y >= self.h-55 and y <= self.h-30 and not self.in_battle and not self.shopping:
			self.in_battle = True
		elif x <= self.w and y >= self.h-85 and y <= self.h-60 and not self.in_battle and not self.shopping:
			self.shopping = True
		elif x <= self.w and y >= self.h-115 and y <= self.h-90 and not self.in_battle and not self.shopping:
			try:
				loc = random.choice(locations)
				self.status = loc.text
				locations.remove(loc)
				spots = ''
				if os.path.exists('exploration'):
					with open('exploration', 'r') as f:
						spots = f.read()
				with open('exploration', 'w') as f:
					f.truncate()
					f.write('{}\n{}'.format(loc.text,spots))
				if loc.boss:
					def tmp():
						self.enemy = loc.boss
						self.enh = self.enemy.hp
						self.in_battle = True
					self.delay(5, tmp)
			except:
				self.status = 'You have already explored the school.'
		elif x <= self.w and y >= self.h-135 and y <= self.h-120 and not self.in_battle and not self.shopping:
			self.enemy = rg
			self.enh = rg.hp
			self.in_battle = True
		
		if self.shopping:
			sy = 30
			for item in self.shop_items:
				if y >= self.h-sy-(25/2) and y <= self.h-sy+(25/2):
					price = re.search((r'[0-9-]+'),item)
					if price:
						price = price.group()
					if not price:
						self.shopping = False
						return
					if(user.money >= int(price)):
						user.pay(int(price))
						if re.search((r'HP Expansion'), item):
							user.expansions += 1
							user.save()
						elif re.search((r'Sell HP'), item):
							user.expansions -= 1
							user.save()
					sy += 30
		
		if x >= 200 or y >= self.mv_dictionaries[0]['y']+(25/2) and self.show_movelist:
			self.show_movelist = False
		for move in self.mv_dictionaries:
			if x <= 200 and y <= move['y']+(25/2) and y >= move['y']-(25/2) and self.show_movelist:
				self.attack(move['move'])
				self.show_movelist = False
		
		if x >= 0 and x <= 120 and y <= 100 and y >= 50+(25/2) and not self.show_movelist:
			self.show_movelist = True
		elif x >= 120 and x <= self.w and y <= 100 and y >= 50+(25/2) and not self.show_movelist:
			user.defending = True

run(game(), PORTRAIT)
