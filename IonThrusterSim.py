# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 19:56:26 2021

@author: Intel
"""

import pygame
import copy
import math
import random
import numpy

class Particle:
    def __init__(self,posX,posY,velX,velY,radius,color):
        self.posX=posX
        self.posY=posY
        self.velX=velX
        self.velY=velY
        self.radius=radius
        self.color=color
        self.charged=False
        
    def draw(self,targetSurface):
        pygame.draw.circle(targetSurface,self.color,(self.posX,self.posY),self.radius)
        if self.charged:
            pygame.draw.rect(targetSurface,(0,0,0),[self.posX-self.radius//2,self.posY,self.radius,1])
            pygame.draw.rect(targetSurface,(0,0,0),[self.posX,self.posY-self.radius//2,1,self.radius])
        
    def update(self,otherAtoms,counter):
        rng=random.Random()
        if self.charged:
            for atom in otherAtoms:
                if not atom.charged:
                    continue
                r=math.sqrt((self.posX-atom.posX)**2+(self.posY-atom.posY)**2)
                dX=self.posX-atom.posX
                dY=self.posY-atom.posY
                if dX==0 and dY==0:
                    continue
                if dX > 0:
                    self.velX+=math.floor(dX*normalizer/r**3)
                elif dX < 0:
                    self.velX-=math.floor(abs(dX)*normalizer/r**3)
                if dY > 0:
                    self.velY+=math.floor(dY*normalizer/r**3)
                elif dY < 0:
                    self.velY-=math.floor(abs(dY)*normalizer/r**3)
        eps=0.8
        
        if self.posX>=startHorizontal and not self.charged:
            if rng.randrange(1,100,1)>95:
                self.charged=True
                self.color=(255,0,0)
                
                
        if self.posX+self.velX<=0:
            self.velX*=-1
            
        if self.posX+self.velX>=startHorizontal+horizontalWidth and self.charged:
            if self.posX<startHorizontal+horizontalWidth:
                counter.value+=1
            self.velX=100
            
        if self.posX+self.velX>=startHorizontal+horizontalWidth+tailLength:
            return True
            
        hitHorizontal=(self.posX+self.velX>=0 and self.posX+self.velX<=startHorizontal-tiltedOffset and \
                       (self.posY+self.velY>=lowerBound-tiltedOffset-particleRadius or self.posY+self.velY<=upperBound+tiltedOffset+particleRadius)) or \
            (self.posX+self.velX>=startHorizontal and self.posX+self.velX<=startHorizontal+horizontalWidth and \
             (self.posY+self.velY<=upperBound+particleRadius or self.posY+self.velY>=lowerBound-particleRadius))
                
        hitTilted=self.posX+self.velX>startHorizontal-tiltedOffset-particleRadius and self.posX+self.velX<startHorizontal+particleRadius and \
            (self.posY+self.velY<=-1*self.posX+upperBound+tiltedOffset+startHorizontal-tiltedOffset+particleRadius or \
             self.posY+self.velY>=self.posX+lowerBound-tiltedOffset-startHorizontal+tiltedOffset-particleRadius)
                
        t=((self.posY>=upperBound and self.posY<=upperBound+tiltedOffset) or (self.posY>=lowerBound-tiltedOffset and self.posY<=lowerBound)) \
            and self.posX<=startHorizontal
             
        
        if hitHorizontal:
            self.velY*=-1
            
        if hitTilted:
            (self.velX,self.velY)=(math.floor(math.sqrt(self.velX**2+self.velY**2)),0)
            
            
        if(self.velX>20):
            self.velX=math.floor(eps*self.velX)
        if(self.velY>20):
            self.velY=math.floor(eps*self.velY)
            
        self.posX+=self.velX
        self.posY+=self.velY
        
        bugHorizontal=(self.posX>=0 and self.posX<=startHorizontal-tiltedOffset and \
                       (self.posY>=lowerBound-tiltedOffset or self.posY<=upperBound+tiltedOffset)) or \
            (self.posX>=startHorizontal and self.posX<=startHorizontal+horizontalWidth and \
             (self.posY<=upperBound or self.posY>=lowerBound))
                
        bugTilted=self.posX>startHorizontal-tiltedOffset and self.posX<startHorizontal and \
            (self.posY<=-1*self.posX+upperBound+tiltedOffset+startHorizontal-tiltedOffset or \
             self.posY>=self.posX+lowerBound-tiltedOffset-startHorizontal+tiltedOffset)
                
        if bugTilted:
            (self.velX,self.velY)=(math.floor(math.sqrt(self.velX**2+self.velY**2)),0)
                
        if bugHorizontal:
            self.posX=rng.randrange(randomStartX,randomEndX,1)
            self.posY=rng.randrange(randomStartY,randomEndY,1)
            self.velX=startVelX
            self.velY=rng.randrange(-10,10,1)
            self.charged=False
            self.color=(0,100,0)
        
        return False
            
                
class Button:
    def __init__(self,posX,posY,source):
        self.posX=posX
        self.posY=posY
        self.image=pygame.image.load(source)
        
    def draw(self,targetSurface):
        targetSurface.blit(self.image,(self.posX,self.posY))
        
    

class ControlPanel:
    def __init__(self,posX,posY):
        self.posX=posX
        self.posY=posY
        self.buttonStart=Button(posX+100,posY+100,"buttonStart.png")
        self.increaseDensity=Button(posX+100,posY+200,"reduceDensity.png")
        self.reduceDensity=Button(posX+400,posY+200,"increaseDensity.png")
        self.exit=Button(posX+100,posY+300,"exit.png")
        self.buttons=[]
        self.buttons.append(self.buttonStart)
        self.buttons.append(self.increaseDensity)
        self.buttons.append(self.reduceDensity)
        self.buttons.append(self.exit)
        
    def draw(self,targetSurface):
        for button in self.buttons:
            button.draw(targetSurface)

   
class Counter:
    def __init__(self):
        self.value=0
        

class Rocket:
    def __init__(self,atoms):
        self.atoms=copy.copy(atoms)
        self.counter=Counter()
        self.tiltedBar1=pygame.image.load("tilt.png")
        self.tiltedBar1=pygame.transform.rotate(self.tiltedBar1,-45)
        self.tiltedBar2=pygame.image.load("tilt.png")
        self.tiltedBar2=pygame.transform.rotate(self.tiltedBar2,45)
        
    def draw(self,targetSurface):
        for atom in self.atoms:
            atom.draw(targetSurface)
        pygame.draw.rect(targetSurface,barColor,[0,upperBound+tiltedOffset,startHorizontal-tiltedOffset+5,wallWidth])
        pygame.draw.rect(targetSurface,barColor,[0,upperBound+tiltedOffset+tunnelWidth,startHorizontal-tiltedOffset+5,wallWidth])
        pygame.draw.rect(targetSurface,barColor,[startHorizontal,upperBound,horizontalWidth,wallWidth])
        pygame.draw.rect(targetSurface,barColor,[startHorizontal,lowerBound,horizontalWidth,wallWidth])
        pygame.draw.rect(targetSurface,electrodeColor,[startHorizontal+horizontalWidth,upperBound,electrodeWidth,lowerBound-upperBound])
        pygame.draw.rect(targetSurface,electrodeColor,[startHorizontal+horizontalWidth+10,upperBound,electrodeWidth,lowerBound-upperBound])
        targetSurface.blit(self.tiltedBar1,(startHorizontal-tiltedOffset,upperBound+tiltedOffset+tunnelWidth))
        targetSurface.blit(self.tiltedBar2,(startHorizontal-tiltedOffset,upperBound))
        
        
    def update(self,otherAtoms):
        for atom in self.atoms:
            if atom.update(otherAtoms,self.counter):
                self.atoms.remove(atom)
                
        
neutralColor=(0,100,0)
chargedColor=(255,0,0)
particleRadius=10
startVelX=40
upperBound=500
lowerBound=900
startHorizontal=400
horizontalWidth=1000
startTilted=0
bgColor=(82,219,255)
barColor=(255,255,255)
electrodeColor=(255,0,0)
tailLength=300
normalizer=15000
wallWidth=5
electrodeWidth=5
tunnelWidth=100
tiltedOffset=(lowerBound-upperBound-tunnelWidth)//2
randomStartX=10
randomEndX=startHorizontal-tiltedOffset
randomStartY=upperBound+tiltedOffset+10
randomEndY=lowerBound-tiltedOffset-10

def main():
    pygame.init()
    pygame.display.set_caption("Јонски погон симулатор")
    surfaceSizeX=1800
    surfaceSizeY=950
    mainSurface=pygame.display.set_mode((surfaceSizeX,surfaceSizeY))
    clock=pygame.time.Clock()
    fps=20
    density=1
    thrust=0
    rng=random.Random()
    jupiter=pygame.image.load("jupiter.png")
    font = pygame.font.SysFont('Comic Sans MS', 30)
    controlPanel=ControlPanel(500,50)
    atoms=[]
    for i in range(density):
        atoms.append(Particle(rng.randrange(randomStartX,randomEndX,1),rng.randrange(randomStartY,randomEndY,1),startVelX,rng.randrange(-10,10,1),particleRadius,neutralColor))
    i=0
    rocket=Rocket(atoms)
    temps=copy.copy(atoms)
    while True:
        event=pygame.event.poll()
        if event.type==pygame.QUIT:
            break
        if event.type==pygame.MOUSEBUTTONDOWN:
            x=event.pos[0]
            y=event.pos[1]
            if (x>=600 and x<=855 and y>=254 and y<=290):
                density-=1
            elif (x>=900 and x<=1148 and y>=253 and y<=286):
                density+=1
            elif (x>=600 and x<=700 and y>=352 and y<=387):
                break
            elif (x>=600 and x<=752 and y>=152 and y<=187):
                density=0
                rocket.atoms=[]
                temps=[]
            
        i+=1
        if i==fps:
            thrust=rocket.counter.value
            rocket.counter.value=0
            i=0
        result = font.render("Излезен број на јони во секунда: "+str(thrust), False, (255, 255, 255))
        densityText=font.render(str(density),False,(255,255,255))
        mainSurface.fill((0,0,0))
        mainSurface.blit(jupiter,(100,100))
        controlPanel.draw(mainSurface)
        if rng.randrange(1,101,1)>75:
            for j in range(density):
                newAtom=Particle(rng.randrange(randomStartX,randomEndX,1),rng.randrange(randomStartY,randomEndY,1),startVelX,rng.randrange(-10,10,1),particleRadius,neutralColor)
                rocket.atoms.append(newAtom)
                temps.append(newAtom)
        mainSurface.blit(result,(800,150))
        mainSurface.blit(densityText,(865,245))
        rocket.draw(mainSurface)
        rocket.update(temps)
        temps=copy.copy(rocket.atoms)
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
    
main()