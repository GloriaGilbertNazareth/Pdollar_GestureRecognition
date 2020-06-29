#!/usr/bin/python

#author: Gloria Gilbert Nazareth
#UFID: 8221-8035
#Assignmmet 1: P$ recognizer

import math
import time
from array import array
import os.path
from os import path
import os
import sys

###### class Point
class Point:
	def __init__(self, x, y, id):
		self.x = x
		self.y = y
		self.id = id

numTemplates = 0 # counter for cloud points length
numberOfPoints = 32 # used for resampling
origin = Point(0,0,0) # point representing the origin



#calculating euclidean distance
def euclDistance(point1, point2):
	distanceX = point1.x - point2.x
	distanceY = point1.y - point2.y
	return math.sqrt((distanceX*distanceX)+(distanceY*distanceY))

#calculating pathlength for points belonging to the same stroke
def pathLength(points):
	distance = 0.0
	for i in range(1, len(points)):
			if(points[i].id == points[i-1].id):
				distance = distance + euclDistance(points[i], points[i-1])
	return distance

######resampling the points based on same stroke id
def resample(points, numberOfPoints):
	#print("nmbert of piints"+str(numberOfPoints));
	intervalLength = pathLength(points)/(numberOfPoints-1)
	distance = 0.0
	newpoints = []
	newpoints.append(points[0])
	c=1
	for p in points: # ignoring first point(zeroth index) as it is already included in newpoints
		try:
			if(points[c].id == points[c-1].id):
				interDistance = euclDistance(points[c-1], points[c])
				if((distance + interDistance )>= intervalLength):
					qx = points[c-1].x + ((intervalLength - distance)/interDistance) * (points[c].x - points[c-1].x)
					qy = points[c-1].y + ((intervalLength - distance)/interDistance) * (points[c].y - points[c-1].y)
					p = Point(qx, qy, points[c].id) 
					newpoints.append(p)
					points.insert(c,p)
					distance =0.0
				else:
					distance = distance + interDistance
			c=c+1	
		except:
			break	
	#print("len new points" + str(len(newpoints)));
	if(len(newpoints) == numberOfPoints-1):
		newpoints.append(Point(points[len(points)-1].x, points[len(points)-1].y, points[len(points)-1].id))
	return newpoints

			
#scaling the points to create a smaller and modified point set
def scale(points):
	minX = float('inf')
	maxX = minX *(-1)
	minY = minX
	maxY = minX *(-1)
	for point in points:
		minX = min(minX, point.x)
		maxX = max(maxX, point.x)
		minY = min(minY, point.y)
		maxY = max(maxY, point.y)
	size = max(maxX - minX, maxY - minY)
	newpoints =  []
	for point in points:
		qx = (point.x - minX)/size
		qy = (point.y - minY)/size
		newpoints.append(Point(qx, qy, point.id))
	return newpoints


#calculating the centroid for a pointset
def centroid(points):
	x = 0.0
	y = 0.0
	for point in points:
		x = x + point.x
		y = y + point.y
	x = x/len(points)
	y = y/len(points)
	return Point(x, y, 0)

#translating the points with respect to the origin and centroid
def translateTo(points,origin):
	c = centroid(points)
	newpoints = []
	for point in points:
		qx = point.x + origin.x - c.x
		qy = point.y + origin.y - c.y
		newpoints.append(Point(qx,qy, point.id))
	return newpoints;


###### class result
class Result:
	def __self__(self, name, score, time):
		self.name = name
		self.score =score
		self.time = time

###### class PointCloud
class PointCloud:
	def __init__(self, name, points, flag):
		self.name = name
		if flag ==0:
			self.points = resample(points, numberOfPoints)
			self.points = scale(self.points)
			self.points = translateTo(self.points, origin)
		else:
			self.points =points

def cloudDistance(points1, points2, start):
	matched =[]
	for i in range(0, len(points1)):
		matched.append(False)
	sumDistance = 0
	i = start
	while True:
		index =-1
		minDistance = float('inf')
		for j in  range(0,len(matched)):
			if matched[j] ==False:
				#print(str(i) +" "+ str(len(points1))+" "+ str(j)+" "+ str(len(points2)))
				d = euclDistance(points1[i], points2[j])
				if d<minDistance:
					minDistance = d
					index = j

		matched[index] = True
		weight = 1-((i-start + len(points1)) % len(points1))/len(points1)
		sumDistance = sumDistance + (weight * minDistance)
		i= (i+1) % min(len(points1),len(points2))
		if(i==start):
			break
	return sumDistance

#matching the points in the event file with that in gesture cloud points greedily
def greedyCloudMatch(points, cloudPoint):
	e = 0.5
	step = int(math.floor(len(points)**(1.0-e)))
	minDistance = float('inf')
	i=0
	while i<len(points):
		#print(str(len(points))+" " + str(len(cloudPoint.points)))
		distance1 = cloudDistance(points, cloudPoint.points, i)
		distance2 = cloudDistance(cloudPoint.points, points, i)
		minDistance = min(minDistance, min(distance1, distance2))
		i= i+step
	return minDistance




class GestureRecognizer:
	def main(command):
		pointClouds = []
		#print("Command:" +command)
		command = command.replace("'","")
		command = command.replace("]","")
		command = command.replace(",","")
		command = command.replace("[","")
		#print("Command:" +command)

		if path.exists("cloudPointFile.txt"): #checking if file exists and reading cloudpoints from it
			cloudPointFile = open("cloudPointFile.txt", "r+") 
			points =[]
			name =""
			data = cloudPointFile.readlines()
			for i in range(0, len(data)):
				if data[i] =="":
					break
				if ":" in data[i]:
					if len(points) != 0:
						pointClouds.append(PointCloud(name,points,1))
					ids = data[i].split(":")
					name = ids[1]
					points =[]
				if "," in data[i]:
					pointCordinate = data[i].split(",")
					x = pointCordinate[0].replace('\x00', '').strip()
					y =  pointCordinate[1].replace('\x00', '').strip()
					strokeId =  pointCordinate[2].replace('\x00', '').strip()
					points.append(Point(float(x), float(y), float(strokeId)))
			if name!="":
				pointClouds.append(PointCloud(name,points,1))
		#opening the file if it doesn't exist	
		cloudPointFile = open("cloudPointFile.txt", "w+") 

		for i in range(0,len(pointClouds)):
				s = "id:"+ str(pointClouds[i].name)
				cloudPointFile.write(s)
				for j in range(0,len(pointClouds[i].points)):
					s = str(round(pointClouds[i].points[j].x,5)) +","+ str(round(pointClouds[i].points[j].y,5)) +"," + str(pointClouds[i].points[j].id)+"\n"
					cloudPointFile.write(s)
			
		#command =""
		#command = raw_input("Enter the command to be followed:")
		if "-t" in command:
			words = command.split();
			try:
				gestureFile = open(words[2],"r")
			except IOError, e:
				print("File Not Found! Please enter an existing file")
				exit()
			print("Saving gesture as cloud point....")

			gestureFile = open(words[2],"r")
			data = gestureFile.readlines();
			name = data[0]
			points = []
			count = 0
			for i in range(1, len(data)):
				if "BEGIN" in data[i]:
					count = count+1
				elif "END" in data[i]:
					continue
				else:
					cordinates = data[i].split(",");
					points.append(Point(int(cordinates[0]), int(cordinates[1]),count));
			pointClouds.append(PointCloud(name,points,0))
			print("Gesture saved successfully!")
			for i in range(len(pointClouds)-1,len(pointClouds)):
				s = "id:"+ str(pointClouds[i].name)
				cloudPointFile.write(s)
				for j in range(0,len(pointClouds[i].points)):
					s = str(round(pointClouds[i].points[j].x,5)) +","+ str(round(pointClouds[i].points[j].y,5)) +"," + str(pointClouds[i].points[j].id)+"\n"
					cloudPointFile.write(s)
			cloudPointFile.close()

		elif "-r" in command:
			cloudPointFile.close()
			os.remove("cloudPointFile.txt")
			print("All the gestures in the cloudPointFile have been deleted!")
		elif command == "./pdollar.py":
			cloudPointFile.close()

			print("****************Help screen*****************\n Input the following in the terminal to run the program. \n" 
				"Input one of the following commands to perform the respective operation: \n \t 1. ./pdollar.py -t <gestureFileName> -> to add gestures to cloudpoints"+
				"\n\t 2. ./pdollar.py <eventFileName> -> to recognize gestures\n\t 3. ./pdollar.py -r -> tp remove all existing cloud points and delete the cloudPointFile.txt"+
				"\n\t 4. ./pdollar.py to view this message again.\n Thank you!")


		else:
			cloudPointFile.close()
			words = command.split();
			try:
				eventFile = open(words[1],"r")
			except IOError, e:
				print("File Not Found! Please enter an existing file")
				exit()
			print("Recognizing gesture.....")		

			data = eventFile.readlines();
			name = data[0]
			points = []
			count = 0
			for i in range(1, len(data)):
				if "MOUSEDOWN" in data[i]:
					count = count+1
				elif "MOUSEUP" in data[i]:
					continue
				elif "RECOGNIZE" in data[i]:
					startTime = time.time()
					index =-1
					minDistance = float('inf')
					query = PointCloud("",points,0); 
					for i in range(0,len(pointClouds)):
						distance = greedyCloudMatch(query.points, pointClouds[i])
						if distance < minDistance:
							minDistance = distance
							index =i
					endTime = time.time()
					#print("index::::"+str(index))
					if index==-1:
						print("Oops!!! No match Found\n" + "score: 0.0 " + "\ntime: "+ str(round(endTime-startTime,5))+" secs")
					else:
						score =1.0
						if minDistance > 1.0:
							score=1.0/minDistance
						print("Gesture Recognized!!! \nGesture: " + pointClouds[index].name + "score: "+ str(score) + " \ntime: "+ str(round(endTime-startTime,5)) +" secs")
					points = []	
				else:
					cordinates = data[i].split(",");
					points.append(Point(int(cordinates[0]), int(cordinates[1]),count));

	if __name__ == "__main__":
		main(str(sys.argv))

