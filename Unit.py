import pygame,math,random,Config
#動畫部位
class MySprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #extend the base Sprite class
        self.master_image = None
        self.frame = 0
        self.old_frame = -1
        self.frame_width = 1
        self.frame_height = 1
        self.first_frame = 0
        self.last_frame = 0
        self.columns = 1
        self.last_time = 0
        self.direction = False
        self.master_image = None
        self.Type = None
    #X property
    def _getx(self): return self.rect.x
    def _setx(self,value): self.rect.x = value
    X = property(_getx,_setx)
    #Y property
    def _gety(self): return self.rect.y
    def _sety(self,value): self.rect.y = value
    Y = property(_gety,_sety)
    #position property
    def _getpos(self): return self.rect.topleft
    def _setpos(self,pos): self.rect.topleft = pos
    position = property(_getpos,_setpos)
    def load(self, filename, width, height, columns):
        self.master_image = pygame.image.load(filename).convert_alpha()
        self.frame_width = width
        self.frame_height = height
        self.rect = pygame.Rect(0,0,width,height)
        self.columns = columns
        rect = self.master_image.get_rect()
        self.last_frame = (rect.width // width) * (rect.height // height) - 1
    def update(self):
        try:
            if self.master_image != None:
                frame_x = (self.frame % self.columns) * self.frame_width
                frame_y = (self.frame // self.columns) * self.frame_height
                rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
                self.image =  pygame.transform.flip(self.master_image.subsurface(rect), self.direction,False)
        except:
            print(self.frame)
            print(self.Type)
class Bullet(MySprite):
    def __init__(self,Side,ShootPostion,weapon,TargetPostion,ShootPostion_adj=None):
        MySprite.__init__(self) #extend the base Sprite class
        if ShootPostion_adj != None:
            x_distance = ShootPostion_adj[0]-TargetPostion[0]
            y_distance = ShootPostion_adj[1]-TargetPostion[1]
        else:
            x_distance = ShootPostion[0]-TargetPostion[0]
            y_distance = ShootPostion[1]-TargetPostion[1]
        self.image = pygame.Surface((4, 4))
        pygame.draw.circle(self.image, Config.BLUE, (2, 2), 2, 0)
        self.rect = self.image.get_rect()
        distance = math.sqrt(math.pow(x_distance,2) + math.pow(y_distance,2))+1
        self.speed = (x_distance/distance*weapon.BulletSpeed,y_distance/distance*weapon.BulletSpeed)
        self.damage = weapon.Damage    
        self.limit_dis = weapon.LimitRange
        self.postion = ShootPostion
        self.rect.center = ShootPostion
        self.old_pos = [ShootPostion[0],ShootPostion[1]]
        self.Type = "Bullet"
        self.Side = Side
        
    def update(self):
        self.postion[0] -= self.speed[0]
        self.postion[1] -= self.speed[1]
        self.rect.center = self.postion
        if math.sqrt(math.pow(self.position[0]-self.old_pos[0],2)+math.pow(self.position[1]-self.old_pos[1],2))>=self.limit_dis:
            self.kill()
class Grenade(MySprite):
    def __init__(self,postion,postion_adj,move,Side):
        MySprite.__init__(self) #extend the base Sprite class
        self.damage = 100
        x_distance = postion_adj[0]-move[0]
        y_distance = postion_adj[1]-move[1]
        distance = math.sqrt(math.pow(x_distance,2) + math.pow(y_distance,2))
        self.speed = [x_distance/distance*10,y_distance/distance*10]
        self.image = pygame.image.load("images/Grenade.png")
        self.rect = self.image.get_rect()
        self.postion = postion
        self.rect.center = postion
        self.Type = "Grenade"
        self.reciprocal = 500
        self.reciprocal_time = 0
        self.overFire = False
        self.onFloat = False
        self.Side = Side
    def update(self):
        if self.onFloat:
            if pygame.time.get_ticks() > self.reciprocal_time + self.reciprocal:
                self.overFire = True
        else:
            self.speed[1] -= Config.Gspeed
            self.postion[0] -= self.speed[0]
            self.postion[1] -= self.speed[1]
            self.rect.center = self.postion
    def Fire(self,bullet):
        ScrapNum = 25
        pygame.mixer.Sound(Config.PATH +'/musices/Grenade.wav').play()
        for i in range(0,ScrapNum,1):
            bullet.add(Bullet(self.Side,[self.rect.x,self.rect.y],Config.Grenade(),[self.rect.x-math.cos(25*i),self.rect.y+math.sin(25*i)]))
class Shield(MySprite):
    def __init__(self):
        MySprite.__init__(self) #extend the base Sprite class
        self.image = pygame.Surface((4, 30))
        pygame.draw.rect(self.image, Config.BLUE, (0, 0, 4, 30))
        self.rect = self.image.get_rect()
    def update(self):
        pass
class Platform(MySprite):
    def __init__(self, x, y,BlockImage):
        MySprite.__init__(self)
        self.image = pygame.image.load(Config.BlockImage)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
    def update(self,bullets):
        attacker = None
        attacker = pygame.sprite.spritecollideany(self, bullets)
        if attacker != None:
            if attacker.Type == "Bullet":
                bullets.remove(attacker)
            else:
                if not attacker.onFloat:
                    attacker.onFloat = True
                    attacker.reciprocal_time = pygame.time.get_ticks()
                    attacker.rect.bottom = self.rect.top + 1
                elif attacker.overFire:
                    attacker.Fire(bullets)
                    bullets.remove(attacker)
class Unit(object):
    def __init__(self,x,y,weapon):
        self.direction = False #False 面右
        self.magazine = weapon.Magazine #彈匣量
        self.hp = 100
        self.weapon = weapon
        #火控
        self.lastFire = 0#最後射擊時間
        self.shootRate = weapon.ShootRate    #射擊間隔(MS)
        self.fire_actioned = True
        self.AutoFire = weapon.AutoFire
        self.FireBreaked = True
        self.ThrowFire = 0
        self.Throwing = False
        #換彈
        self.reload_actioned = True
        self.reloadMid = False
        self.reloadTicks = 0
        #防禦
        self.defense_actioning = False
        self.defense_hold = False#維持
        self.defense_actioned = False#動作完成
        #座標
        self.rect = pygame.Rect(x, y, 32, 32)#絕對座標
        self.rect_adj = pygame.Rect(x, y, 32, 32) #畫面座標
        self.move_speed = weapon.MoveSpeed #移動速度
        self.xVel = 0 #加速度
        self.yVel = 0 #加速度
        #部位
        self.Foot = MySprite()
        self.Foot.load(self.FootFrame, 17, 12, 4)
        self.Foot.direction = self.direction
        self.Body = MySprite()
        self.Body.load(self.FireFrame, 10, 20, 1)
        self.Body.Type = "Fire"
        self.Body.first_frame = self.weapon.ID * self.Body.columns
        self.Body.direction = self.direction
        self.Hand = MySprite()
        self.Hand.load(self.HandFrame, 27, 8, 3)
        self.Hand.first_frame = self.weapon.ID * self.Hand.columns
        self.Hand.frame = self.Hand.first_frame
        self.Body.direction = self.direction
        self.DefenseBody = MySprite()
        self.DefenseBody.load(self.DefenseFrame, 40, 35, 6)
        self.DefenseBody.direction = self.direction
        self.Shield = Shield()
    def MoveRight(self):
        if not self.defense_actioning and self.hp > 0:
            self.xVel += self.move_speed
            #腳
            if self.direction:
                self.Foot.frame -= 1
            else:
                self.Foot.frame += 1
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.first_frame
            elif self.Foot.frame < self.Foot.first_frame:
                self.Foot.frame = self.Foot.last_frame
    def MoveLeft(self):
        if not self.defense_actioning and self.hp > 0:
            self.xVel -= self.move_speed
            #腳
            if self.direction:
                self.Foot.frame += 1
            else:
                self.Foot.frame -= 1
            self.Foot.X -= self.move_speed
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.first_frame
            elif self.Foot.frame < self.Foot.first_frame:
                self.Foot.frame = self.Foot.last_frame
    def SeekCheck(self,x):
        if self.hp > 0:
            if x < self.rect_adj.x + 20:#左
                self.direction = True
            else:#右
                self.direction = False
    def getShootPosition(self):
        if self.hp > 0:
            if not self.direction:
                return [self.rect.x + 20,self.rect.y-7]
            else:
                return [self.rect.x - 10,self.rect.y-7]
    def FireBreak(self):
        self.FireBreaked = True
    def fireUpdate(self):        
        self.Hand.frame += 1
        if self.Hand.frame == self.Hand.first_frame+self.weapon.FireAction:
            self.Hand.frame = self.Hand.first_frame
            self.fire_actioned = True
    def Reload(self):
        if self.reload_actioned and self.fire_actioned and not self.defense_actioning and not self.Throwing and self.hp > 0:
            self.reload_actioned = False
            self.reloadMid = False
            postion = self.Body.position
            self.Body.load(self.ReloadFrame, 23, 20, 6)
            self.Body.Type = "Reload"
            self.Body.first_frame = self.weapon.ID * self.Body.columns
            self.Body.last_frame = self.Body.first_frame + self.Body.columns - 1
            self.Body.frame = self.Body.first_frame
            self.Body.position = postion
            pygame.mixer.Sound(Config.PATH + self.weapon.ReloadSound).play()
    def reloadUpdate(self):
        if not self.reloadMid:
            self.Body.frame += 1
        else:
            self.Body.frame -= 1
        if self.Body.frame == self.Body.first_frame+self.weapon.ReloadAction:
            if not self.reloadMid:
                self.reloadMid = True
                self.Body.frame -= 1
        if self.Body.frame < self.Body.first_frame:
            pygame.mixer.Sound(Config.PATH + self.weapon.ReloadSound).play()
            self.magazine = self.weapon.Magazine #彈匣量
            self.reload_actioned = True
            self.Body.load(self.FireFrame, 10, 20, 1)
            self.Body.Type = "Fire"
            self.Body.first_frame = 0
            self.Body.frame = 0
    def defenseUpdaet(self):
        if self.defense_actioning and self.hp > 0:#維持
            self.defense_hold = True
            if self.DefenseBody.frame < self.DefenseBody.last_frame:#尚未舉滿
                self.DefenseBody.frame += 1
        else:
            if self.DefenseBody.frame > self.DefenseBody.first_frame:
                self.DefenseBody.frame -= 1
            else:
                self.defense_hold = False
    def ThrowGrenade(self,TargetPosition):
        ticks = pygame.time.get_ticks()
        if self.hp > 0:
            if ticks > self.ThrowFire + 500 and self.reload_actioned and self.fire_actioned and not self.defense_actioning:
                self.ThrowFire = ticks
                self.Throwing = True
                self.Body.load(self.ThrowFrame, 19, 20, 5)
                self.Body.Type = "Throw"
                self.Body.frame = 0
                self.Body.first_frame = 0
                pygame.mixer.Sound(Config.PATH +'/musices/GreTh.wav').play()
                return Grenade(self.getShootPosition(),self.rect_adj,TargetPosition,self.Side)
        return False
    def throwUpdate(self):        
        self.Body.frame += 1
        if self.Body.frame > self.Body.last_frame:
            self.Throwing = False
            self.Body.load(self.FireFrame, 10, 20, 1)
            self.Body.Type = "Fire"
            self.Body.first_frame = 0
            self.Body.frame = self.Body.first_frame
    def update(self,camera,entities,bullet):
        self.Foot.direction = self.direction
        self.Body.direction = self.direction
        self.Hand.direction = self.direction
        self.DefenseBody.direction = self.direction
        self.collisionBlock(entities)
        self.collisionBullet(bullet)
        self.rect_adj = camera.apply(self)
        if self.hp > 0:
            #腳
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.first_frame
            elif self.Foot.frame < self.Foot.first_frame:
                self.Foot.frame = self.Foot.last_frame
            if self.direction:
                self.Foot.X = self.rect.x
            else:
                self.Foot.X = self.rect.x - 4
            self.Foot.Y = self.rect.y
            #身
            if self.defense_actioning or self.defense_hold:
                self.DefenseBody.first_frame = self.Foot.frame * self.DefenseBody.columns
                self.DefenseBody.last_frame = self.DefenseBody.first_frame + self.DefenseBody.columns - 1
                if self.DefenseBody.frame > self.DefenseBody.last_frame:
                    self.DefenseBody.frame = self.DefenseBody.first_frame
                elif self.DefenseBody.frame < self.DefenseBody.first_frame:
                    self.DefenseBody.frame = self.DefenseBody.last_frame
                if self.direction:
                    self.DefenseBody.X = self.rect.x - 14
                    self.Shield.X = self.rect.x - 5
                else:
                    self.DefenseBody.X = self.rect.x - 10
                    self.Shield.X = self.rect.x + 18
                self.DefenseBody.Y = self.rect.y - 23
                self.Shield.Y = self.rect.y - 19
                self.defenseUpdaet()
            else:
                if not self.reload_actioned:
                    self.reloadUpdate()
                elif not self.fire_actioned:
                    self.fireUpdate()
                elif self.Throwing:
                    self.throwUpdate()
                if self.Body.Type == "Reload":
                    if self.direction:
                        self.Body.X = self.rect.x - 9
                    else:
                        self.Body.X = self.rect.x
                elif self.Body.Type == "Throw":
                    if self.direction:
                        self.Body.X = self.rect.x
                    else:
                        self.Body.X = self.rect.x - 5
                else:
                    if self.direction:
                        self.Body.X = self.rect.x + 3
                        self.Hand.X = self.rect.x - 15
                    else:
                        self.Body.X = self.rect.x
                        self.Hand.X = self.rect.x + 1
            self.Hand.Y = self.rect.y - 11
            self.Body.Y = self.rect.y - 20
        else:
            self.Foot.load(self.DieFrame,40,35,7)
            self.Foot.frame += 1
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.last_frame
            self.Foot.X = self.rect.x - 3
            self.Foot.Y = self.rect.y - 23
    def draw(self,screen,camera):        
        if self.hp > 0:
            if not self.defense_actioning and not self.defense_hold:
                self.Foot.update()
                self.Body.update()
                self.Hand.update()
                screen.blit(self.Foot.image, camera.apply(self.Foot))
                screen.blit(self.Body.image, camera.apply(self.Body))
                if self.Body.Type == "Fire":
                    screen.blit(self.Hand.image, camera.apply(self.Hand))
            else:
                self.DefenseBody.update()
                screen.blit(self.DefenseBody.image, camera.apply(self.DefenseBody))
            #血框
            pygame.draw.rect(screen, Config.WHITE, (int(camera.apply(self).x - 8), int(camera.apply(self).y - 29),40,5),1)
            #血條
            pygame.draw.rect(screen, Config.RED, (int(camera.apply(self).x - 7), int(camera.apply(self).y - 28),int(38*(self.hp/100)),3),0)
        else:
            self.Foot.update()
            screen.blit(self.Foot.image, camera.apply(self.Foot))
    def collisionBlock(self,target):
        onFloat = False
        #移動碰撞
        self.Foot.rect.x += self.xVel
        self.rect.x += self.xVel
        attacker = None
        attacker = pygame.sprite.spritecollideany(self.Foot, target)
        if attacker != None:
            self.rect.y -= Config.BlockHeight
        self.xVel = 0
        #踩空設定
        self.Foot.rect.y += 2
        attacker = None
        attacker = pygame.sprite.spritecollideany(self.Foot, target)
        if attacker != None:
            onFloat = True
        if not onFloat:
            self.rect.y += Config.BlockHeight
    def collisionBullet(self,target):
        if self.hp > 0:
            #盾牌碰撞
            if self.defense_actioning or self.defense_hold:
                attacker = None
                attacker = pygame.sprite.spritecollideany(self.Shield, target)
                if attacker != None:
                    print(attacker.rect,self.Shield.rect)
                    #self.hp -= attacker.damage
                    pygame.mixer.Sound(Config.PATH+'/musices/defense.wav').play()
                    target.remove(attacker)
            #腿部碰撞
            attacker = None
            attacker = pygame.sprite.spritecollideany(self.Foot, target)
            if attacker != None:
                if attacker.Side != self.Side and attacker.Type == "Bullet":
                    print(attacker.rect,self.Foot.rect,self.Shield.rect)
                    self.hp -= attacker.damage
                    pygame.mixer.Sound(Config.PATH+'/musices/Hit.wav').play()
                    target.remove(attacker)
            #身體碰撞
            attacker = None
            attacker = pygame.sprite.spritecollideany(self.Body, target)
            if attacker != None:
                if attacker.Side != self.Side and attacker.Type == "Bullet":
                    print(attacker.rect,self.Body.rect,self.Shield.rect)
                    self.hp -= attacker.damage
                    pygame.mixer.Sound(Config.PATH+'/musices/Hit.wav').play()
                    target.remove(attacker)
class Enemy(Unit):
    def __init__(self,x,y,weapon):
        #勢力參數
        self.Side = 1
        #ai動作參數
        self.action=0#0 pass 1 fire 2 move
        self.lastAction=0
        self.actionRate=30#ai動作間隔
        #圖形
        self.FireFrame = Config.PATH+"/images/Body_e.png"
        self.FootFrame = Config.PATH+"/images/Foot_e.png"
        self.ReloadFrame = Config.PATH+"/images/Reload_e.png"
        self.ThrowFrame = Config.PATH+"/images/Throw_e.png"
        self.DieFrame = Config.PATH+"/images/Die_e.png"
        self.HandFrame = Config.PATH+"/images/Hand_e.png"
        self.DefenseFrame = Config.PATH+"/images/Defense_e.png"
        #初始化
        Unit.__init__(self,x,y,weapon)
    def Fire(self,PlayerPosition):
        ticks = pygame.time.get_ticks()
        if self.hp > 0:
            if self.magazine > 0:
                if ticks > self.lastFire + self.shootRate and self.FireBreaked and self.reload_actioned and not self.defense_actioning and not self.Throwing :
                    self.magazine -= 1
                    self.fire_actioned = False
                    pygame.mixer.Sound(Config.PATH + self.weapon.FireSound).play()
                    self.lastFire = ticks
                    if not self.AutoFire:
                        self.FireBreaked = False
                    #Side,ShootPostion,weapon,TargetPostion,ShootPostion_adj=None
                    return Bullet(self.Side,self.getShootPosition(),self.weapon,PlayerPosition)
            else:
                self.Reload()
        return False
class Player(Unit):
    def __init__(self,x,y,weapon):
        #勢力參數
        self.Side = 0
        #圖形
        self.FireFrame = Config.PATH+"/images/Body.png"
        self.FootFrame = Config.PATH+"/images/Foot.png"
        self.ReloadFrame = Config.PATH+"/images/Reload.png"
        self.ThrowFrame = Config.PATH+"/images/Throw.png"
        self.DieFrame = Config.PATH+"/images/Die.png"
        self.HandFrame = Config.PATH+"/images/Hand.png"
        self.DefenseFrame = Config.PATH+"/images/Defense.png"
        #初始化
        Unit.__init__(self,x,y,weapon)
    def Fire(self,TargetPosition):
        ticks = pygame.time.get_ticks()
        if self.hp > 0:
            if self.magazine > 0:
                if ticks > self.lastFire + self.shootRate and self.FireBreaked and self.reload_actioned and not self.defense_actioning and not self.Throwing :
                    self.magazine -= 1
                    self.fire_actioned = False
                    pygame.mixer.Sound(Config.PATH + self.weapon.FireSound).play()
                    self.lastFire = ticks
                    if not self.AutoFire:
                        self.FireBreaked = False
                    #Side,ShootPostion,weapon,TargetPostion,ShootPostion_adj=None
                    return Bullet(self.Side,self.getShootPosition(),self.weapon,TargetPosition,self.rect_adj)
            else:
                self.Reload()
        return False
