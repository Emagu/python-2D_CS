import pygame,Config
class Button(object):
	def __init__(self,x,y,displaySurface):
		self.ds = displaySurface
		self.x = x
		self.y = y
	def setIcon(self,w,h,ic,ac):
		self.w = w
		self.h = h
		self.ic = ic
		self.ac = ac
		self.IconType = "Icon"
	def setIconWithImage(self,IC_image,AC_image):
		self.ic = pygame.image.load(IC_image)
		self.ac = pygame.image.load(AC_image)
		self.w = self.ic.get_rect()[2]
		self.h = self.ic.get_rect()[3]
		self.IconType = "Image"
	def setAction(self,action):
		self.Action = action
	def setFont(self,msg,font,size=20):
		self.msg = msg
		self.font = font
		self.size = size
	def update(self):
		mouse = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()
		if self.x + self.w > mouse[0] > self.x and self.y + self.h > mouse[1] > self.y:
			if self.IconType == "Icon":
				pygame.draw.rect(self.ds,self.ac,(self.x,self.y,self.w,self.h))
			else:
				self.ds.blit(self.ac, (self.x, self.y))
			if click[0] == 1 and self.Action != None:
				self.Action()
		else:
			if self.IconType == "Icon":
				pygame.draw.rect(self.ds,self.ic,(self.x,self.y,self.w,self.h))
			else:
				self.ds.blit(self.ic, (self.x, self.y))
		if self.IconType == "Icon":
			buttonText = pygame.font.Font(self.font,self.size)
			textSurf, textRect = text_objects(self.msg, buttonText,WHITE)
			textRect.center = (self.x + self.w / 2, self.y + self.h /2 )
			self.ds.blit(textSurf, textRect)
class gameFrame(Button):
	def __init__(self,x,y,displaySurface,data):
		Button.__init__(self,x,y,displaySurface)
		self.data = data
		self.ic = pygame.image.load(Config.PATH+"/"+data["IconImage"])
		self.ac = pygame.image.load(Config.PATH+"/"+data["IconImage"])
		self.w = 700
		self.h = 150
		self.frame = pygame.Surface((self.w,self.h))
		pygame.draw.rect(self.frame, Config.WHITE, (0, 0, self.w, self.h),5)
		#標題文字
		TitleTextSurface,TitleTextRect = text_objects(data["Title"],pygame.font.Font(Config.Font,30),Config.WHITE)
		TitleTextRect.x = 250
		TitleTextRect.y = 10
		self.frame.blit(TitleTextSurface,TitleTextRect)
		#說明
		InfoTextSurface,InfoTextRect = text_objects(data["Description"],pygame.font.Font(Config.Font,20),Config.WHITE)
		InfoTextRect.x = 250
		InfoTextRect.y = 45
		self.frame.blit(InfoTextSurface,InfoTextRect)
		#解鎖狀況(等有圖改用圖)
		if data["Lock"]=="False":
			LockTextSurface,LockTextRect = text_objects("已解鎖",pygame.font.Font(Config.Font,20),Config.WHITE)
			LockTextRect.x = 250
			LockTextRect.y = 70
			self.frame.blit(LockTextSurface,LockTextRect)
		else:
			LockTextSurface,LockTextRect = text_objects("待解鎖",pygame.font.Font(Config.Font,20),Config.WHITE)
			LockTextRect.x = 250
			LockTextRect.y = 70
			self.frame.blit(LockTextSurface,LockTextRect)
		self.IconWidth = self.ic.get_rect()[2]
		self.IconHeight = self.ic.get_rect()[3]
		self.IconType = "Image"
	def setAction(self,action):
		self.Action = action
	def update(self):
		mouse = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()
		if self.x + self.w > mouse[0] > self.x and self.y + self.h > mouse[1] > self.y:
			self.frame.blit(self.ac, (10,10))
			self.ds.blit(self.frame,(self.x,self.y))
			if click[0]==1:
				if self.Action != None and self.data["Lock"]=="False":
					self.Action(self.data)
		else:
			self.frame.blit(self.ac, (10,10))
			self.ds.blit(self.frame,(self.x,self.y))
class Camera(object):
	def __init__(self, S_W, S_H, width, height):
		self.rect = pygame.Rect(0, 0, width, height)
		self.sw = S_W
		self.sh = S_H
	def apply(self, target):
		return target.rect.move(self.rect.topleft)
	def update(self, target):
		target_rect = target.rect
		l, t, _, _ = target_rect
		_, _, w, h = self.rect
		l, t, _, _ = -l+self.sw/2, -t+self.sh/2, w, h
		if(self.rect.x<0):tmp=self.rect.x
		else:tmp=0
		l = min(tmp,l)                            # stop scrolling at the left edge
		l = max(-(self.rect.width-self.sw), l)   # stop scrolling at the right edge
		t = max(-(self.rect.height-self.sh), t) # stop scrolling at the bottom
		t = min(0, t) 
		self.rect = pygame.Rect(l, t, w, h)
def text_objects(text, font, color):
	textSurface = font.render(text, True, color)
	return textSurface, textSurface.get_rect()
