import pygame, sys,random,os,json,math
import Config
from Unit import *
from System import *
class Scene_Base(object):
	def __init__(self,Screen):
		self.Screen = Screen
		self.display = True
		self.nextScene = None
	def update(self):
		pass
	def quitgame(self):
		self.display = False
		self.nextScene = quitgame(self.Screen)
class quitgame(Scene_Base):
	def __init__(self,Screen):
		pygame.quit()
		quit()
class Title(Scene_Base):
	def __init__(self,Screen):
		Scene_Base.__init__(self,Screen)
		pygame.mixer.music.load(Config.PATH+'/musices/Title.mp3')
		pygame.mixer.music.play(-1,0.0)
		self.StartButton = Button(320,400,Screen)
		self.StartButton.setIconWithImage(Config.PATH+'/images/Start_ic.png',Config.PATH+'/images/Start_ac.png')
		self.StartButton.setAction(self.gameMenu)
		self.RankButton = Button(320,455,Screen)
		self.RankButton.setIconWithImage(Config.PATH+'/images/Rank_ic.png',Config.PATH+'/images/Rank_ac.png')
		self.RankButton.setAction(self.rankScene)
		self.EndButton = Button(320,510,Screen)
		self.EndButton.setIconWithImage(Config.PATH+'/images/End_ic.png',Config.PATH+'/images/End_ac.png')
		self.EndButton.setAction(self.quitgame)
		self.TitleImage = pygame.image.load(Config.TitleImage)
	def update(self):
		for event in pygame.event.get():#偵測是否關閉
			if event.type == 12:
				self.quitgame()
	#畫面初始化
		self.Screen.fill(Config.WHITE)
	#背景
		self.Screen.blit(self.TitleImage, (0, 0))
	#按鈕
		self.StartButton.update()
		self.RankButton.update()
		self.EndButton.update()
		#版本號
		VersionText = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		textSurf, textRect = text_objects(Config.VERSION, VersionText,Config.WHITE)
		self.Screen.blit(textSurf, (self.TitleImage.get_rect()[2]-textRect[2]-10, self.TitleImage.get_rect()[3] - textRect[3]))
	#鼠標
		mouse = pygame.mouse.get_pos()
		AimCursor = pygame.image.load(Config.NormalCursorImage)
		AimCursor_rect = AimCursor.get_rect()
		AimCursor_rect.center = mouse
		self.Screen.blit(AimCursor, AimCursor_rect)
		pygame.display.update()
	def gameMenu(self):
		self.display = False
		self.nextScene = gameMenu(self.Screen)
	def rankScene(self):
		self.display = False
		self.nextScene = rankScene(self.Screen)
class gameMenu(Scene_Base):
	def __init__(self,Screen):
		Scene_Base.__init__(self,Screen)
		self.GameList = []
		for game in self.readGameList():
			newGame = gameFrame(50,50+160*len(self.GameList),self.Screen,game)
			newGame.setAction(self.gameStart)
			self.GameList.append(newGame)
		self.rankData = self.readGameList()
		self.returnButton = Button(590,530,Screen)
		self.returnButton.setIconWithImage(Config.PATH+'/images/Return_ic.png',Config.PATH+'/images/Return_ac.png')
		self.returnButton.setAction(self.Title)
		pygame.time.delay(200)
	def update(self):
		for event in pygame.event.get():#偵測是否關閉
			if event.type == 12:
				quitgame()
	#畫面初始化
		self.Screen.fill(Config.BLACK)
	#按鈕
		for game in self.GameList:
			game.update()
		self.returnButton.update()
	#鼠標
		mouse = pygame.mouse.get_pos()
		AimCursor = pygame.image.load(Config.NormalCursorImage)
		AimCursor_rect = AimCursor.get_rect()
		AimCursor_rect.center = mouse
		self.Screen.blit(AimCursor, AimCursor_rect)
		pygame.display.update()
	def readGameList(self):
		path = "data/gameList"
		data = []
		for f in os.listdir(path):
			with open(path+"/"+f) as json_data:
				data.append(json.load(json_data))
		return data
	def gameStart(self,arg):
		self.display = False
		self.nextScene = gameStart(self.Screen,arg)
	def Title(self):
		self.display = False
		self.nextScene = Title(self.Screen)
class gameStart(Scene_Base):
	def __init__(self,Screen,arg):
		Scene_Base.__init__(self,Screen)
		#參數初始化
		self.arg = arg
		self.BlockArray = []
		self.SOURCE = 0
		self.TIME = pygame.time.get_ticks()//1000
		self.DISTANCE = 0
		self.LEVEL=arg["EnemyWeapon"]#arg0~2
		self.ENEMYS = []
		self.PAUSE = False
		self.PLAYER = Player(0,arg["BlockFloat"]-12,Config.WEAPON[int(arg["Weapon"])])
		self.BlackGroundImage = pygame.image.load(arg["BackGroundImage"])
		self.entities = pygame.sprite.Group()
		self.BULLETS = pygame.sprite.Group()
		#BGM播放
		pygame.mixer.music.load(arg["BGM"])
		pygame.mixer.music.play(-1,0.0)
		#磚塊生成
		last_block = random.randrange(1,6)
		BG_rect = self.BlackGroundImage.get_rect()
		block_num = arg["BlockNumber"]
		block_w = arg["BlockImageWidth"]
		block_h = arg["BlockImageHeight"]
		for i in range(0,block_num,1):
			last_block = last_block + random.randrange(-1,2)
			if last_block > 6:
				last_block = 6
			elif last_block < 1:
				last_block = 1
			for j in range(0,last_block,1):    
				p = Platform(i*block_w, 500 - j*block_h,arg["BlockImage"])
				self.entities.add(p)
		self.sceneWidth =  block_num*block_w
		self.camera = Camera(BG_rect[2],BG_rect[3], self.sceneWidth, BG_rect[3])
	def update(self):
		#勝負判定
		if self.SOURCE >= self.arg["KillToWin"] and self.arg["KillToWin"] != 0:#擊殺獲勝       
			self.classComplete()
		elif self.DISTANCE >= self.arg["DistanceToWin"] and self.arg["DistanceToWin"] != 0:#距離獲勝                
			self.classComplete()
		elif pygame.time.get_ticks() // 1000 - self.TIME >= self.arg["HoldToWin"] and self.arg["HoldToWin"] != 0:#堅持獲勝                
			print(self.TIME)
			self.classComplete()
		elif self.PLAYER.hp <= 0:
			self.classEnd()
		else:
			#偵測是否關閉
			for event in pygame.event.get():
				if event.type == 12:
					self.quitgame()
			#畫面初始化
			self.Screen.fill(Config.WHITE)
			self.Screen.blit(self.BlackGroundImage, (0, 0))
		#準心更新
			mouse = pygame.mouse.get_pos()
			AimCursor = pygame.image.load(Config.AimCursorImage)
			AimCursor_rect = AimCursor.get_rect()
			AimCursor_rect.center = mouse
			self.PLAYER.SeekCheck(mouse[0])
			#開火偵測
			click = pygame.mouse.get_pressed()
			if click[0] == 1:
				bullet = self.PLAYER.Fire(mouse)
				if bullet != False:
					self.BULLETS.add(bullet)
			else:
				self.PLAYER.FireBreak()
		#角色操作
			pressed = pygame.key.get_pressed()
			if pressed[pygame.K_a]:
				if(self.PLAYER.rect.x+self.camera.rect.x>=10):#左側lock
					self.PLAYER.MoveLeft()
			if pressed[pygame.K_d]:
				if self.PLAYER.rect.x < self.sceneWidth - 20:
					self.PLAYER.MoveRight()
			if pressed[pygame.K_r]:
				self.PLAYER.Reload()
			if pressed[pygame.K_SPACE]:
				grenade = self.PLAYER.ThrowGrenade(mouse)
				if grenade != False:
					self.BULLETS.add(grenade)
			if pressed[pygame.K_s]:
				if self.PLAYER.reload_actioned and self.PLAYER.fire_actioned:
					self.PLAYER.defense_actioning = True
			else:
				self.PLAYER.defense_actioning = False
			#新增敵人
			if (random.randint(0,100)<2 and len(self.ENEMYS)<15 and self.PLAYER.rect.x>0):
				pos,weapon=random.choice([-600,800]),random.choice(range(0,self.LEVEL+1))
				enemy = Enemy(self.PLAYER.rect.x+pos,Config.BlockFloat-12,Config.WEAPON[weapon])
				self.ENEMYS.append(enemy)
			#AI
			self.AI()
			self.camera.update(self.PLAYER)
			for e in self.entities:
				e.update(self.BULLETS)
				self.Screen.blit(e.image, self.camera.apply(e))
			for b in self.BULLETS:
				b.update()
				self.Screen.blit(b.image, self.camera.apply(b))
		#角色更新
			self.PLAYER.update(self.camera,self.entities,self.BULLETS)
			self.PLAYER.draw(self.Screen,self.camera)
			#敵人更新
			for i, enemy in enumerate(self.ENEMYS, start=0):
				enemy.update(self.camera,self.entities,self.BULLETS)
				enemy.draw(self.Screen,self.camera)
			#玩家彈匣描繪
			for i in range(0,self.PLAYER.magazine,1):
				self.Screen.blit(pygame.image.load(Config.PATH+self.PLAYER.weapon.Ammo), (200 + 9 * i, 550))
		#分數描繪
			PAST = pygame.time.get_ticks() // 1000 - self.TIME#經過時間
			if self.PLAYER.rect.x // 32 > self.DISTANCE:
				self.DISTANCE = self.PLAYER.rect.x // 32	
			SourceText = pygame.font.Font(Config.Font,30)
			SourceSurf, SourceRect = text_objects("擊殺人數:" + str(self.SOURCE), SourceText,Config.WHITE)
			SourceRect.topleft = (0,550)
			
			TIMEText = pygame.font.Font(Config.Font,20)
			TIMESurf, TIMERect = text_objects("時間:" + str(PAST // 60) + ":" + str(PAST % 60), TIMEText,Config.WHITE)
			TIMERect.topleft = (700,550)
			
			DISTANCEText = pygame.font.Font(Config.Font,20)
			DISTANCESurf, DISTANCERect = text_objects("距離" + str(self.DISTANCE) + 'M', DISTANCEText,Config.WHITE)
			DISTANCERect.topleft = (700,570)

			self.Screen.blit(SourceSurf, SourceRect)
			self.Screen.blit(TIMESurf, TIMERect)
			self.Screen.blit(DISTANCESurf, DISTANCERect)
			self.Screen.blit(AimCursor, AimCursor_rect)
			
			pygame.display.update()
	def AI(self):
		for bot in self.ENEMYS:
			if  self.PLAYER.rect.x - bot.rect.x > 800:
				self.ENEMYS.remove(bot)
				break
			if not bot.dead and bot.hp <= 0:
				bot.dead = True
				self.SOURCE += 1
			if bot.hp > 0:
				bot.lastAction += 1
				if self.PLAYER.rect.x > bot.rect.x:
					bot.direction = False
				else:
					bot.direction = True
				if bot.action == 1:
					if type(bot.weapon) == Config.SMG:
						bot.lastAction += 5
					else:
						bot.lastAction += 50
					if bot.magazine > 0:
						bot.FireBreak()
						bullet = bot.Fire((self.PLAYER.rect.x,self.PLAYER.rect.y))
						if bullet != False:
							self.BULLETS.add(bullet)	
					else:
						bot.Reload()
				elif bot.action == 2:
					bot.lastAction += 1
					if bot.direction:
						bot.MoveLeft()
					else:
						bot.MoveRight()
				if bot.lastAction >= bot.actionRate:#決定行為
					bot.lastAction=0
					i = random.randint(0,100)
					fire,move=0,0
					if abs(self.PLAYER.rect.x - bot.rect.x) <= bot.weapon.LimitRange:
						fire,move = 20,60
					else:
						fire,move = 0,60
					if i<fire:
						bot.action = 1
					elif i<move and abs(self.PLAYER.rect.x - bot.rect.x)>80:
						bot.action = 2
					else:
						bot.action = 0
	def classEnd(self):
		self.display = False
		self.arg["Source"] = str(self.SOURCE)
		if self.SOURCE > self.arg["HightSource"]:
			self.arg["HightSource"] = self.SOURCE
		past = pygame.time.get_ticks() // 1000 - self.TIME
		self.arg["Time"] = str(past // 60) + "分" + str(past % 60)+"秒" 
		if past > self.arg["HightTimeValue"]:
			self.arg["HightTimeValue"] = past
			self.arg["HightTime"] = self.arg["Time"]
		self.arg["Distance"] = str(self.DISTANCE)
		if self.DISTANCE > self.arg["HightDistance"]:
			self.arg["HightDistance"] = self.DISTANCE
		self.nextScene = classEnd(self.Screen,self.arg)
	def classComplete(self):
		self.display = False
		self.arg["Source"] = str(self.SOURCE)
		if self.SOURCE > self.arg["HightSource"]:
			self.arg["HightSource"] = self.SOURCE
		past = pygame.time.get_ticks() // 1000 - self.TIME
		self.arg["Time"] = str(past // 60) + "分" + str(past % 60)+"秒"
		if past > self.arg["HightTimeValue"]:
			self.arg["HightTimeValue"] = past
			self.arg["HightTime"] = self.arg["Time"]
		self.arg["Distance"] = str(self.DISTANCE)
		if self.DISTANCE > self.arg["HightDistance"]:
			self.arg["HightDistance"] = self.DISTANCE
		if self.arg["Level"] == 3:
			self.nextScene = gameEnd(self.Screen,self.arg)
		else:
			self.nextScene = classComplete(self.Screen,self.arg)
class classEnd(Scene_Base):
	def __init__(self,Screen,arg):
		Scene_Base.__init__(self,Screen)
		self.arg = arg
		self.FPS_Delayer = 3 #減慢幾倍FPS
		self.FPS_Click = 0 #減慢用計數器
		#灰階畫面
		width, height = Screen.get_size()
		for x in range(width):
			for y in range(height):
				red, green, blue, alpha = Screen.get_at((x, y))
				average = (red + green + blue) // 3
				gs_color = (average, average, average, alpha)
				self.Screen.set_at((x, y), gs_color)
		self.grayScreen = self.Screen.copy()
		#輸出字串輸出幾個文字
		self.LevelStringCount = 1#關卡
		self.SourceStringCount = 0#得分
		self.TimeStringCount = 0#時間
		self.DistanceStringCount = 0#距離
		self.InfoStringCount = 0#說明
		self.messageComplete = False
		#倒數回到選單
		self.ReCountToMenu = 10
		self.ReCountStartTime = pygame.time.get_ticks()
	def update(self):
		self.Screen.fill(Config.WHITE)
		self.Screen.blit(self.grayScreen, (0, 0))
		#偵測是否關閉
		for event in pygame.event.get():
			if event.type == 12:
				self.quitgame()
		if (True in pygame.mouse.get_pressed()) or (True in pygame.key.get_pressed())and self.messageComplete:
			self.gameMenu()
		#文字處理
		LevelString = "任務:"+ self.arg["Title"]
		LevelText = pygame.font.Font(Config.Font,30)
		LevelSurf, LevelRect = text_objects(LevelString[0:self.LevelStringCount], LevelText,Config.YELLOW)
		LevelRect.topleft = (0,300)
		
		SourceString = "擊殺數:"+ self.arg["Source"]
		SourceText = pygame.font.Font(Config.Font,25)
		SourceSurf, SourceRect = text_objects(SourceString[0:self.SourceStringCount], SourceText,Config.YELLOW)
		SourceRect.topleft = (0,350)
		
		TimeString = "經過時間:"+ self.arg["Time"]
		TimeText = pygame.font.Font(Config.Font,25)
		TimeSurf, TimeRect = text_objects(TimeString[0:self.TimeStringCount], TimeText,Config.YELLOW)
		TimeRect.topleft = (0,390)
		
		DistanceString = "移動距離:"+ self.arg["Distance"] + "M"
		DistanceText = pygame.font.Font(Config.Font,25)
		DistanceSurf, DistanceRect = text_objects(DistanceString[0:self.DistanceStringCount], DistanceText,Config.YELLOW)
		DistanceRect.topleft = (0,430)
		
		InfoString = "很可惜在此飲恨了"
		InfoText = pygame.font.Font(Config.Font,25)
		InfoSurf, InfoRect = text_objects(InfoString[0:self.InfoStringCount], InfoText,Config.YELLOW)
		InfoRect.topleft = (0,470)
		
		ReCounterText = pygame.font.Font(Config.Font,25)
		ReCounterSurf, ReCounterRect = text_objects("請點擊任意鍵，或於"+str(self.ReCountToMenu)+"秒後跳轉回遊戲選單", ReCounterText,Config.YELLOW)
		ReCounterRect.center = (int(self.Screen.get_size()[0]/2),int(self.Screen.get_size()[1]*0.9))
		if self.FPS_Click == self.FPS_Delayer:
			self.FPS_Click = 0
			if len(LevelString) > self.LevelStringCount: 
				self.LevelStringCount += 1
			elif len(SourceString) > self.SourceStringCount: 
				self.SourceStringCount += 1
			elif len(TimeString) > self.TimeStringCount: 
				self.TimeStringCount += 1
			elif len(DistanceString) > self.DistanceStringCount: 
				self.DistanceStringCount += 1
			elif len(InfoString) > self.InfoStringCount: 
				self.InfoStringCount += 1
			elif not self.messageComplete:
				self.messageComplete = True
				self.ReCountStartTime = pygame.time.get_ticks()
		else:
			self.FPS_Click += 1
		#貼圖
		self.Screen.blit(LevelSurf, LevelRect)
		self.Screen.blit(SourceSurf, SourceRect)
		self.Screen.blit(TimeSurf, TimeRect)
		self.Screen.blit(DistanceSurf, DistanceRect)
		self.Screen.blit(InfoSurf, InfoRect)
		if self.messageComplete:
			self.Screen.blit(ReCounterSurf, ReCounterRect)
			if (pygame.time.get_ticks() - self.ReCountStartTime >= 1000):
				self.ReCountStartTime = pygame.time.get_ticks()
				self.ReCountToMenu -= 1
				if self.ReCountToMenu < 0:
					self.gameMenu()
		pygame.display.update()
	def gameMenu(self):
		self.display = False
		self.nextScene = gameMenu(self.Screen)
class classComplete(Scene_Base):
	def __init__(self,Screen,arg):
		Scene_Base.__init__(self,Screen)
		self.arg = arg
		self.EndScreen = self.Screen.copy()
		self.FPS_Delayer = 3 #減慢幾倍FPS
		self.FPS_Click = 0 #減慢用計數器
		#輸出字串輸出幾個文字
		self.LevelStringCount = 1#關卡
		self.SourceStringCount = 0#得分
		self.TimeStringCount = 0#時間
		self.DistanceStringCount = 0#距離
		self.InfoStringCount = 0#說明
		self.messageComplete = False
		#倒數回到選單
		self.ReCountToMenu = 10
		self.ReCountStartTime = pygame.time.get_ticks()
		#覆寫檔案
		with open('data/gameList/'+str(self.arg["Level"])+".json", 'w') as f:
			json.dump(self.arg, f, ensure_ascii=False)
		
		with open('data/gameList/'+str(self.arg["Level"]+1)+'.json') as json_data:
			nextLevel = json.load(json_data)
			nextLevel["Lock"] = "False"
			with open('data/gameList/'+str(self.arg["Level"]+1)+".json", 'w') as f:
				json.dump(nextLevel, f, ensure_ascii=False)
	def update(self):
		self.Screen.fill(Config.WHITE)
		self.Screen.blit(self.EndScreen, (0, 0))
		#偵測是否關閉
		for event in pygame.event.get():
			if event.type == 12:
				self.quitgame()
		if (True in pygame.mouse.get_pressed()) or (True in pygame.key.get_pressed())and self.messageComplete:
			self.gameMenu()
		#文字處理
		LevelString = "任務:"+ self.arg["Title"]
		LevelText = pygame.font.Font(Config.Font,30)
		LevelSurf, LevelRect = text_objects(LevelString[0:self.LevelStringCount], LevelText,Config.YELLOW)
		LevelRect.topleft = (0,300)
		
		SourceString = "擊殺數:"+ self.arg["Source"]
		SourceText = pygame.font.Font(Config.Font,25)
		SourceSurf, SourceRect = text_objects(SourceString[0:self.SourceStringCount], SourceText,Config.YELLOW)
		SourceRect.topleft = (0,350)
		
		TimeString = "經過時間:"+ self.arg["Time"]
		TimeText = pygame.font.Font(Config.Font,25)
		TimeSurf, TimeRect = text_objects(TimeString[0:self.TimeStringCount], TimeText,Config.YELLOW)
		TimeRect.topleft = (0,390)
		
		DistanceString = "移動距離:"+ self.arg["Distance"] + "M"
		DistanceText = pygame.font.Font(Config.Font,25)
		DistanceSurf, DistanceRect = text_objects(DistanceString[0:self.DistanceStringCount], DistanceText,Config.YELLOW)
		DistanceRect.topleft = (0,430)
		
		InfoString = "恭喜完成任務!下一個關卡已解鎖!"
		InfoText = pygame.font.Font(Config.Font,25)
		InfoSurf, InfoRect = text_objects(InfoString[0:self.InfoStringCount], InfoText,Config.YELLOW)
		InfoRect.topleft = (0,470)
		
		ReCounterText = pygame.font.Font(Config.Font,25)
		ReCounterSurf, ReCounterRect = text_objects("請點擊任意鍵，或於"+str(self.ReCountToMenu)+"秒後跳轉回遊戲選單", ReCounterText,Config.YELLOW)
		ReCounterRect.center = (int(self.Screen.get_size()[0]/2),int(self.Screen.get_size()[1]*0.9))
		if self.FPS_Click == self.FPS_Delayer:
			self.FPS_Click = 0
			if len(LevelString) > self.LevelStringCount: 
				self.LevelStringCount += 1
			elif len(SourceString) > self.SourceStringCount: 
				self.SourceStringCount += 1
			elif len(TimeString) > self.TimeStringCount: 
				self.TimeStringCount += 1
			elif len(DistanceString) > self.DistanceStringCount: 
				self.DistanceStringCount += 1
			elif len(InfoString) > self.InfoStringCount: 
				self.InfoStringCount += 1
			elif not self.messageComplete:
				self.messageComplete = True
				self.ReCountStartTime = pygame.time.get_ticks()
		else:
			self.FPS_Click += 1
		#貼圖
		self.Screen.blit(LevelSurf, LevelRect)
		self.Screen.blit(SourceSurf, SourceRect)
		self.Screen.blit(TimeSurf, TimeRect)
		self.Screen.blit(DistanceSurf, DistanceRect)
		self.Screen.blit(InfoSurf, InfoRect)
		if self.messageComplete:
			self.Screen.blit(ReCounterSurf, ReCounterRect)
			if (pygame.time.get_ticks() - self.ReCountStartTime >= 1000):
				self.ReCountStartTime = pygame.time.get_ticks()
				self.ReCountToMenu -= 1
				if self.ReCountToMenu < 0:
					self.gameMenu()
		pygame.display.update()
	def gameMenu(self):
		self.display = False
		self.nextScene = gameMenu(self.Screen)
class gameEnd(Scene_Base):
	def __init__(self,Screen,arg):
		Scene_Base.__init__(self,Screen)
		self.Textoffect_Y = 0
		#覆寫檔案
		with open('data/gameList/'+str(arg["Level"])+".json", 'w') as f:
			json.dump(arg, f, ensure_ascii=False)
	def update(self):
		#畫面初始化
		self.Screen.fill(Config.BLACK)
		for event in pygame.event.get():#偵測是否關閉
			if event.type == 12:
				quitgame()
		ThankText = pygame.font.Font(Config.Font,30)
		ThankSurf, ThankRect = text_objects("感謝您的遊玩", ThankText,Config.WHITE)
		ThankRect.topleft = ((self.Screen.get_rect()[2] - ThankRect[2]) / 2,500 - self.Textoffect_Y)
		
		TributeText = pygame.font.Font(Config.Font,30)
		TributeSurf, TributeRect = text_objects("本遊戲向經典遊戲'Font Line'致敬", TributeText,Config.WHITE)
		TributeRect.topleft = ((self.Screen.get_rect()[2] - TributeRect[2]) / 2,550 - self.Textoffect_Y)
		
		CodeText = pygame.font.Font(Config.Font,20)
		CodeSurf, CodeRect = text_objects("程式結構:陳政瑋", CodeText,Config.WHITE)
		
		CodeRect.topleft = ((self.Screen.get_rect()[2] - CodeRect[2]) / 2,600 - self.Textoffect_Y)
		
		AlgorithmText = pygame.font.Font(Config.Font,20)
		AlgorithmSurf, AlgorithmRect = text_objects("演算法:黃智斌", AlgorithmText,Config.WHITE)
		AlgorithmRect.topleft = ((self.Screen.get_rect()[2] - AlgorithmRect[2]) / 2,650 - self.Textoffect_Y)
		
		PlanText = pygame.font.Font(Config.Font,20)
		PlanSurf, PlanRect = text_objects("遊戲企劃:陳政瑋", PlanText,Config.WHITE)
		PlanRect.topleft = ((self.Screen.get_rect()[2] - PlanRect[2]) / 2,700 - self.Textoffect_Y)
		
		GameText = pygame.font.Font(Config.Font,20)
		GameSurf, GameRect = text_objects("遊戲策試:黃智斌", GameText,Config.WHITE)
		GameRect.topleft = ((self.Screen.get_rect()[2] - GameRect[2]) / 2,750 - self.Textoffect_Y)
		
		ArtText = pygame.font.Font(Config.Font,20)
		ArtSurf, ArtRect = text_objects("美術設計:王維豪", ArtText,Config.WHITE)
		ArtRect.topleft = ((self.Screen.get_rect()[2] - ArtRect[2]) / 2,800 - self.Textoffect_Y)
		
		self.Screen.blit(ThankSurf, ThankRect)
		self.Screen.blit(TributeSurf, TributeRect)
		self.Screen.blit(CodeSurf, CodeRect)
		self.Screen.blit(AlgorithmSurf, AlgorithmRect)
		self.Screen.blit(PlanSurf, PlanRect)
		self.Screen.blit(GameSurf, GameRect)
		self.Screen.blit(ArtSurf, ArtRect)
		if self.Textoffect_Y >= 800:
			self.Title()
		self.Textoffect_Y += 1
		pygame.display.update()
	def Title(self):
		self.display = False
		self.nextScene = Title(self.Screen)
class rankScene(Scene_Base):
	def __init__(self,Screen):
		Scene_Base.__init__(self,Screen)
		self.rankData = self.readGameList()
		self.returnButton = Button(100,500,Screen)
		self.returnButton.setIconWithImage(Config.PATH+'/images/Return_ic.png',Config.PATH+'/images/Return_ac.png')
		self.returnButton.setAction(self.Title)
	def update(self):
		for event in pygame.event.get():#偵測是否關閉
			if event.type == 12:
				self.quitgame()
		#畫面初始化
		self.Screen.fill(Config.BLACK)
		G1_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',30)
		G1_Surf, G1_Rect = text_objects("第一關:"+self.rankData[0]["Title"], G1_Text,Config.WHITE)
		self.Screen.blit(G1_Surf, (100,30))
		
		G1_Kill_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G1_Kill_Surf, G1_Kill_Rect = text_objects("最高擊殺數:"+str(self.rankData[0]["HightSource"])+"人", G1_Kill_Text,Config.WHITE)
		self.Screen.blit(G1_Kill_Surf, (100,70))
		
		G1_dist_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G1_dist_Surf, G1_dist_Rect = text_objects("最遠移動距離:"+str(self.rankData[0]["HightDistance"])+"M", G1_dist_Text,Config.WHITE)
		self.Screen.blit(G1_dist_Surf, (100,100))
		
		G1_time_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G1_time_Surf, G1_time_Rect = text_objects("最久存活時間:"+self.rankData[0]["HightTime"], G1_time_Text,Config.WHITE)
		self.Screen.blit(G1_time_Surf, (100,130))
		
		G2_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',30)
		G2_Surf, G2_Rect = text_objects("第二關:"+self.rankData[1]["Title"], G2_Text,Config.WHITE)
		self.Screen.blit(G2_Surf, (100,180))
		
		G2_Kill_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G2_Kill_Surf, G2_Kill_Rect = text_objects("最高擊殺數:"+str(self.rankData[1]["HightSource"])+"人", G2_Kill_Text,Config.WHITE)
		self.Screen.blit(G2_Kill_Surf, (100,220))
		
		G2_dist_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G2_dist_Surf, G2_dist_Rect = text_objects("最遠移動距離:"+str(self.rankData[1]["HightDistance"])+"M", G2_dist_Text,Config.WHITE)
		self.Screen.blit(G2_dist_Surf, (100,250))
		
		G2_time_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G2_time_Surf, G2_time_Rect = text_objects("最久存活時間:"+self.rankData[1]["HightTime"], G2_time_Text,Config.WHITE)
		self.Screen.blit(G2_time_Surf, (100,280))
		
		G3_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',30)
		G3_Surf, G3_Rect = text_objects("第三關:"+self.rankData[2]["Title"], G3_Text,Config.WHITE)
		self.Screen.blit(G3_Surf, (100,330))
		
		G3_Kill_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G3_Kill_Surf, G3_Kill_Rect = text_objects("最高擊殺數:"+str(self.rankData[2]["HightSource"])+"人", G3_Kill_Text,Config.WHITE)
		self.Screen.blit(G3_Kill_Surf, (100,360))
		
		G3_dist_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G3_dist_Surf, G3_dist_Rect = text_objects("最遠移動距離:"+str(self.rankData[2]["HightDistance"])+"M", G3_dist_Text,Config.WHITE)
		self.Screen.blit(G3_dist_Surf, (100,390))
		
		G3_time_Text = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
		G3_time_Surf, G3_time_Rect = text_objects("最久存活時間:"+self.rankData[2]["HightTime"], G3_time_Text,Config.WHITE)
		self.Screen.blit(G3_time_Surf, (100,420))
		self.returnButton.update()
		mouse = pygame.mouse.get_pos()
		AimCursor = pygame.image.load(Config.NormalCursorImage)
		AimCursor_rect = AimCursor.get_rect()
		AimCursor_rect.center = mouse
		self.Screen.blit(AimCursor, AimCursor_rect)
		pygame.display.update()
	def readGameList(self):
		path = "data/gameList"
		data = []
		for f in os.listdir(path):
			with open(path+"/"+f) as json_data:
				data.append(json.load(json_data))
		return data
	def Title(self):
		self.display = False
		self.nextScene = Title(self.Screen)
def main():
	global fpsClock,DISPLAYSURF
	pygame.init()
	pygame.mixer.init()
	pygame.mouse.set_visible(False)
	fpsClock = pygame.time.Clock()
	TitleImage = pygame.image.load(Config.TitleImage)
	DISPLAYSURF = pygame.display.set_mode((TitleImage.get_rect()[2], TitleImage.get_rect()[3]), 0, 32)
	pygame.display.set_caption('2D-CS')
	now_scene = Title(DISPLAYSURF)
	while True:
		if now_scene.display:
			now_scene.update()
		else:
			now_scene = now_scene.nextScene
		fpsClock.tick(Config.FPS)
if __name__ == '__main__':
	main()