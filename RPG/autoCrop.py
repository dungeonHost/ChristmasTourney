import numpy as np
import cv2
import glob,os
import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk

lIndex=0
pics=dict()
def pickImage(pictures,fullPic):
	root=tk.Tk()
	top=Frame(root)
	index=0
	butts=dict()
	images=dict()
	picToKeep=list()
	label=list()
	global lIndex
	
	h,w,_=fullPic.shape
	fpic=fullPic
	if(w<h and w>400):
		fpic=cv2.resize(fullPic,(400,int(400*(h/w))))
	elif(h>400):
		fpic=cv2.resize(fullPic,(int(400*(w/h)),400))
	cv2.imshow("fullPic",fpic)
	lIndex=0
	labelText=["pick evo1 sprite","pick evo2 sprite","pick evo3 sprite","pick evo1 blast","pick evo2 blast","pick evo3 blast","pick any extra images"]
	label.append(Label(root,justify=LEFT,text=labelText[0]))
	label[0].grid(row=0,column=0)
	#label[0].pack(side=LEFT)
	for pic in pictures:
		pic=cv2.resize(pic,(60,60))
		im=Image.fromarray(pic)
		images[index]=ImageTk.PhotoImage(im)
		butts[index]=Button(root,justify=LEFT)
		butts[index].config(image=images[index],width="60",height="60",command=lambda a=index: imageSelect(a,pictures,picToKeep,labelText,label,root))
		butts[index].grid(row=1+int(index/12),column=int(index%12))
		#butts[index].pack(side=LEFT)
		index+=1
	none=Button(root,justify=LEFT)
	none.config(text="NONE",width="10",height="3",command=lambda a=-1: imageSelect(a,pictures,picToKeep,labelText,label,root))
	none.grid(row=2,column=index-2)
	#none.pack(side=LEFT)
	back=Button(root,justify=LEFT)
	back.config(text="GoBack",width="10",height="3",command=lambda a=-2: imageSelect(a,pictures,picToKeep,labelText,label,root))
	back.grid(row=2,column=index-1)
	#back.pack(side=LEFT)
	root.mainloop()
	cv2.destroyAllWindows()
	return picToKeep
	
def imageSelect(index,pictures,picToKeep,labelText,label,root):
	global lIndex
	global pics
	lIndex+=1
	if(index>=0):
		print("INDEX="+str(index))
		picToKeep.append(pictures[index])
		#cv2.imshow("HI",pictures[index])
		#cv2.waitKey(0)
		im=cv2.resize(picToKeep[len(picToKeep)-1],(50,50))
		pic=Image.fromarray(im)
		pics[lIndex]=ImageTk.PhotoImage(pic)
		label.append(Label(root,justify=RIGHT))
		label[len(label)-1].config(image=pics[lIndex])
		label[len(label)-1].grid(row=9,column=lIndex)
	elif(index==-2):
		lIndex-=1
		print("LINDEX+"+str(lIndex)+" LEN="+str(len(label)))
		if label[len(label)-1].cget("image")!='':
			del picToKeep[-1]
		label[len(label)-1].destroy()
		del label[-1]
		lIndex-=1
		if(lIndex<7):
			label[0].config(text=labelText[lIndex])
	elif(index==-1):
		label.append(Label(root,justify=RIGHT))
		label[len(label)-1].config(text="NotFound")
		label[len(label)-1].grid(row=9,column=lIndex)
		picToKeep.append((np.ones((50,50,4),np.uint8)*255))
	if(lIndex<7):
		label[0].config(text=labelText[lIndex])
	elif(index==-1):
		root.destroy()

#def closeWindow()

def splitImage(fileName,im):
	global csvFile
	repeat=1
	white=0
	count=0
	while(repeat==1):
		w,h,l=im.shape
		im[0:w,0:white]=255
		im[0:white,0:h]=255
		imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
		ret, im_th = cv2.threshold(imgray, 254, 255, cv2.THRESH_BINARY_INV)
		im_floodfill=im_th.copy()
		h,w=im_th.shape[:2]
		mask=np.zeros((h+2,w+2),np.uint8)
		
		b,g,r,a=cv2.split(im)
		whiteImg=np.ones(im.shape,np.uint8)
		whiteImg[:,:]=(255,255,255,0)
		whiteMask=cv2.bitwise_and(whiteImg,whiteImg,mask=a)
		whiteMask=cv2.bitwise_not(whiteMask)
		b,g,r,a=cv2.split(whiteMask)
		a[:]=0
		whiteMask=cv2.merge((b,g,r,a),4)
		cv2.addWeighted(whiteMask,1,im,1,0,im)
		#make background transparent
		cv2.floodFill(im_floodfill,mask,(0,0),255)
		im_floodfill_inv = cv2.bitwise_not(im_floodfill)
		im_out = im_th | im_floodfill_inv
		im_out2=cv2.bitwise_and(im,im,mask=mask[:-2,:-2])
		im2=np.copy(im)
		dst=cv2.add(im2,im_out2)
		w,h,l=im.shape
		if(l==3):
			b,g,r=cv2.split(im)
			rgba=[b,g,r,im_out]
			a=im_out
		else:
			b,g,r,a=cv2.split(im)
			if(h*w-np.count_nonzero(a)<=50):
				rgba=[b,g,r,im_out]#im_out]
			else:
				rgba=[b,g,r,a]
		dst2=cv2.merge(rgba,4)
		# for y in range(0,h):
			# for x in range(0,w):
				# if a[x, y] == 0:
					# dst2[x, y] = (255, 255, 255, 0)
		#a=cv2.bitwise_not(a)
		#dst2=cv2.bitwise_or(dst2,dst2,mask=a)
		im=dst2
		w,h,_=im.shape
		
		im[0:w,0:white]=(255,255,255,0)
		im[0:white,0:h]=(255,255,255,0)
		ret, thresh = cv2.threshold(im_out, 254, 255, cv2.THRESH_BINARY)
		im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		im3=np.copy(im2)
		cv2.drawContours(im3,contours,-1,255,3)
		if(len(contours)>4 or count>5):
			repeat=0
		else:
			white+=5
			count+=1
	r=0 
	g=0 
	b=0
	i=0
	im2=np.copy(im)
	largestSquares=list();
	imSquares=cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	cv2.drawContours(imSquares,contours,-1,(0,255,0),3)
	for c in contours:
		if(len(largestSquares)<25):
			largestSquares.append(cv2.boundingRect(c))
			largestSquares.sort(key=lambda ls:ls[2]*ls[3])
		else:
			x,y,w,h = cv2.boundingRect(c)
			a=(w)*(h)
			for index, ls in enumerate(largestSquares):
				xl,yl,wl,hl=ls
				al=(wl)*(hl)
				if a>al:
					largestSquares[index]=cv2.boundingRect(c)
					largestSquares.sort(key=lambda ls:ls[2]*ls[3])
					break
		x,y,w,h = cv2.boundingRect(c)
		a=(w)*(h)
		if x>2 and y>2:
			imSquares[y+2:y-2+h,x+2:x-2+w]=0
			cv2.floodFill(im_floodfill,mask,(0,0),255)
		i+=1
	index=0
	os.chdir(fileName[:-4])
	
	ret, thresh = cv2.threshold(imSquares, 254, 255, cv2.THRESH_BINARY)
	im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	largeSquares=list();
	
	for c in contours:
		if(len(largeSquares)<10):
			largeSquares.append(cv2.boundingRect(c))
			largeSquares.sort(key=lambda ls:ls[2]*ls[3])
		else:
			x,y,w,h = cv2.boundingRect(c)
			a=(w)*(h)
			for index, ls in enumerate(largeSquares):
				xl,yl,wl,hl=ls
				al=(wl)*(hl)
				if a>al:
					largeSquares[index]=cv2.boundingRect(c)
					largeSquares.sort(key=lambda ls:ls[2]*ls[3])
					break
	
	for l in largeSquares:
		largestSquares.append(l)
	largestSquares.sort(key=lambda ls:ls[2]*ls[3])
	crop_imgs=list()
	for ls in largestSquares:
		xl,yl,wl,hl=ls
		cv2.rectangle(im3,(xl,yl),(xl+wl,yl+hl),(255,255,0),2)
		font = cv2.FONT_HERSHEY_SIMPLEX
		crop=im[yl:yl+hl,xl:xl+wl]
		crop_imgs.append(crop)
		#crop=im[yl-2:yl+hl+2,xl-2:xl+wl+2]
		crop=cv2.copyMakeBorder(crop,40,40,40,40,cv2.BORDER_CONSTANT,value=(255,255,255,1))
		#cv2.imshow("hi",crop)
		#cv2.waitKey(0)
		bwCrop=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
		ret, thresh = cv2.threshold(bwCrop, 240, 255, cv2.THRESH_BINARY)
		im2, cont, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		cont.sort(key=lambda c:cv2.contourArea(c),reverse=True)
		i=0
		for c in cont:
			if(i==1):
				mask=np.zeros_like(bwCrop)
				cv2.drawContours(mask,cont,i,255,-1,lineType=8)
				out=np.zeros_like(crop)
				out[mask==255]=crop[mask==255]
				#cv2.drawContours(out,cont,i,(0,0,0,255),2,lineType=8)
				w,h,_=out.shape
				out=out[35:w-35,35:h-35]
				crop_imgs.append(out)
				break
			i+=1
				#cv2.imshow("hi",mask)
				#cv2.waitKey(0)
	return crop_imgs
	# picToKeep=pickImage(crop_imgs,im)
	# index=0
	# csvStr=""
	# for pic in picToKeep:
		# cv2.imwrite("sprite"+str(index)+".png",pic)
		# if(index<3):
			# r_im=cv2.resize(pic,(50,50))
			# os.chdir("../bracket")
			# cv2.imwrite(fileName[:-4]+str(index)+".png",r_im)
			# csvStr+=fileName[:-4]+str(index)+".png,"
			# os.chdir("../"+fileName[:-4])
			# #cv2.imshow(fileName[:-4],pic)
			# cv2.waitKey(0)
		# index+=1
	# csvStr+="\n"
	# csvFile.write(csvStr)
	# cv2.imwrite(fileName,im)
	# os.chdir("../bracket")
	# cv2.imwrite(fileName,im)
	# cv2.waitKey(0)

if not os.path.exists("bracket"):
	os.mkdir("bracket")
csvFile=open("bracket/bracket.csv","w+")
index=0
for pic in glob.glob("*.png"):
	if(index<1):
		if not os.path.exists(pic[:-4]):
			os.mkdir(pic[:-4])
		im=cv2.imread(pic,cv2.IMREAD_UNCHANGED)
		splitImage(pic,im)
		os.chdir("..")
		#index+=1
csvFile.close()