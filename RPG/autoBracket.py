import numpy as np
import cv2
import glob,os
import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
from math import ceil

class testClass:
	def testPrint():
		print("hi")

		
numRounds=3
teamSize=1
numPartis=3
startFlag=True
topFlag=True
horzLineDist=50
vertLineDist=(70*numPartis)
topPoints=list()
class autoBracket:
	def __init__(self,nr,ts,np):
		global numRounds
		global numPartis
		global teamSize
		teamSize=ts
		numRounds=nr
		numPartis=np
		
	def createBracket(self):
		global csvFile
		global startFlag
		global topFlag
		global horzLineDist
		global numPartis
		if not os.path.exists("bracket"):
			print("none")
			exit()
		os.chdir("bracket")
		prod=1
		horzLineDist=ceil((prod*((numPartis)**(numRounds-2)))*(vertLineDist-1)/2)
		horzLineDist=int(horzLineDist*3/4)
		if horzLineDist<75:
			horzLineDist=75
		hsum=0
		bsum=0
		hld=horzLineDist
		for i in range(0,numRounds):
			bsum+=hld
			hld=hld/1.3
		for j in range(numRounds-1,1,-1):
			hsum+=int(prod*((numPartis)**(j-1))*(vertLineDist))
			print("JFDSF"+str(hsum)+" "+str(prod)+" "+str(j))
		h=int(hsum+(numPartis-2)*(150*teamSize+2*(horzLineDist)))+vertLineDist+100
		w=int(bsum)*2+150*(teamSize)+200
		brack=np.ones((h,w,3),np.uint8)*255
		point=[int(w/2),int(h/2)]
		startFlag=True
		topFlag=True
		self.drawBrackHorz(point[0],point[1],brack,-1,numRounds,horzLineDist)
		startFlag=True
		topFlag=True
		self.drawBrackHorz(point[0],point[1],brack,1,numRounds,horzLineDist)
		if numPartis>2:
			topFlag=True
			startFlag=True
			self.drawBrackVert(point[0],point[1],brack,1,numRounds,horzLineDist)
		if numPartis>3:
			topFlag=True
			startFlag=True
			self.drawBrackVert(point[0],point[1],brack,-1,numRounds,horzLineDist)
		h,w,_=brack.shape
		a = np.ones((h,w,1), np.uint8)*255
		b,g,r=cv2.split(brack)
		rgba=[b,g,r,a]
		bracket=cv2.merge(rgba,4)
		print(bracket.shape)
		cv2.imwrite("bracket.png",bracket)
		
		fp=self.populateHorzBracket()
		if numPartis>2:
			self.populateVertBracket(fp)
		
	def populateHorzBracket(self):
		point=topPoints[0]
		point[0]-=50*teamSize
		point[1]-=25
		cnt=1
		bracket=cv2.imread("bracket.png",cv2.IMREAD_UNCHANGED)
		print("StartHorz")
		fp=open("bracket.csv","r+")
		for line in fp:
			splitString=line.split(',')
			pic=cv2.imread(splitString[0].rstrip(),cv2.IMREAD_UNCHANGED)
			print(splitString[0])
			alphS=pic[:,:,3]/255.0
			alphL=1.0-alphS
			for c in range(0,3):
				bracket[point[1]:point[1]+50, point[0]:point[0]+50,c]=(alphS*pic[:,:,c]+alphL*bracket[point[1]:point[1]+50, point[0]:point[0]+50,c])
			if cnt%teamSize==0:
				point[1]+=int((vertLineDist)/(numPartis-1))
				point[0]-=(50*(teamSize-1))
			else:
				point[0]+=50
			if cnt%(numPartis**(numRounds-1)*teamSize)==0:
				point=topPoints[1]
				point[1]-=25
				print("switch")
			if cnt%(2*(numPartis**(numRounds-1)*teamSize))==0:
				cv2.imwrite("bracket.png",bracket)
				print("EXIT")
				return fp
			cnt+=1
		cv2.imwrite("bracket.png",bracket)

	def populateVertBracket(self,fp):
		point=topPoints[2]
		point[0]-=25
		cnt=1
		bracket=cv2.imread("bracket.png",cv2.IMREAD_UNCHANGED)
		print("StartVERT")
		if not(fp):
			return
		for line in fp:
			splitString=line.split(',')
			pic=cv2.imread(splitString[0].rstrip(),cv2.IMREAD_UNCHANGED)
			print(splitString[0])
			alphS=pic[:,:,3]/255.0
			alphL=1.0-alphS
			for c in range(0,3):
				bracket[point[1]:point[1]+50, point[0]:point[0]+50,c]=(alphS*pic[:,:,c]+alphL*bracket[point[1]:point[1]+50, point[0]:point[0]+50,c])
			alphS=0
			alphL=0
			if cnt%teamSize==0:
				point[0]+=int((vertLineDist)/(numPartis-1))
				point[1]-=(50*(teamSize-1))#*dir)
			else:
				point[1]+=50
			if cnt%(numPartis**(numRounds-1)*teamSize)==0:
				break
			cnt+=1
		cv2.imwrite("bracket.png",bracket)

	def drawBrackHorz(self,x,y,brack,dir,r,hLD):
		global startFlag
		global numRounds
		global teamSize
		global numPartis
		global topPoints
		global topFlag
		point=[x,y]
		if startFlag:
			print("start")
			point[0]+=int(hLD*dir/2)
			self.drawLineHorz(point,int(1*hLD),dir,brack)
			hLD=int(hLD/1.3)
			startFlag=False
			r-=1
		prod=1
		for i in range(r,1):
			prod*=i
		vertDist=int(prod*((numPartis)**(r-1))*(vertLineDist))
		print("VERT="+str(vertDist)+" r="+str(r)+" blocks="+str(ceil(((3*r-1)/2)**(r-1))))
		point[1]+=int(vertDist/2)
		self.drawLineVert(point,vertDist,-1,brack)
		hLD=int(hLD/1.3)
		print("r="+str(r)+" hld="+str(hLD))
		for i in range(0,numPartis):
			self.drawLineHorz(point,hLD,dir,brack)
			if(r>1):
				self.drawBrackHorz(point[0],point[1],brack,dir,r-1,hLD)
			elif(topFlag):
				topPoints.append(point[:])
				print(topPoints)
				print(point)
				topFlag=False
			point[0]-=hLD*dir
			print("r="+str(r)+" hld="+str(hLD))
			point[1]+=int((vertDist)/(numPartis-1))
		return
		
	def drawBrackVert(self,x,y,brack,dir,r,hLD):
		global startFlag
		global numRounds
		global teamSize
		global numPartis
		global topPoints
		global topFlag
		point=[x,y]
		if startFlag:
			print("start")
			point[1]+=int(hLD*dir/2)
			self.drawLineVert(point,int(1*hLD),dir,brack)
			hLD=int(hLD/1.3)
			startFlag=False
			r-=1
		prod=1
		for i in range(r,1):
			prod*=i
		vertDist=int(prod*((numPartis)**(r-1))*(vertLineDist))
		print("VERT="+str(vertDist)+" r="+str(r)+" blocks="+str(ceil(((3*r-1)/2)**(r-1))))
		point[0]+=int(vertDist/2)
		self.drawLineHorz(point,vertDist,-1,brack)
		hLD=int(hLD/1.3)
		print("r="+str(r)+" x="+str(point[0]))
		for i in range(0,numPartis):
			self.drawLineVert(point,hLD,dir,brack)
			if(r>1):
				self.drawBrackVert(point[0],point[1],brack,dir,r-1,hLD)
			elif(i==0 and topFlag):
				print(topPoints)
				print(point)
				topPoints.append(point[:])
				topFlag=False
			point[1]-=hLD*dir
			point[0]+=int((vertDist)/(numPartis-1))
		return

	def drawLineHorz(self,point,dist,dir,brack):
		cv2.line(brack,(point[0],point[1]),(point[0]+dist*dir,point[1]),(0,0,0),4)
		point[0]+=dist*dir

	def drawLineVert(self,point,dist,dir,brack):
		cv2.line(brack,(point[0],point[1]),(point[0],point[1]+dist*dir),(0,0,0),4)
		point[1]+=dist*dir

# if not os.path.exists("bracket"):
	# exit()
# os.chdir("bracket")
# csvFile=open("bracket.csv","r+")
# a=autoBracket(numRounds,teamSize,numPartis)
# a.createBracket()