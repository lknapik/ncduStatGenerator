import time
import re
import math
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
import sys

curTime = time.time()

logScale = 3

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class Project:
    def __init__(self, name):
        self.name = name
        self.oldest = 0
        self.numberFiles = 0
        self.depth = 0
        self.totalSize = 0
        self.ageData = [0,0,0,0,0,0,0,0,0]
        self.sizeData = [0,0,0,0,0,0,0,0,0]

    def addData(self, index):
        self.ageData[index] += 1

    def addASize(self, index, size):
        self.sizeData[index] += int(size)

    def printData(self):
        return("Name: {}\nOldest File: {}\nNumber of Files: {}\nMax Depth: {}\nTotal Size: {}\nAge Data: {}\nSize Data: {}\n".format(self.name, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.oldest)), self.numberFiles, self.depth, sizeof_fmt(self.totalSize) ,self.ageData, self.sizeData))


def getAgeBucket(fileTime):
    #1 day = 86400

    timeDelta = curTime - int(fileTime)
    fileAge = int(timeDelta / 86400)

    #0 = 1 day old
    #1-2 = 3 days old
    #3-8 = 9 days old
    #ect...
    return int(math.log(fileAge, logScale))


def genAgePlot(name, bucketData):
    objects = ('<1 day', '3 days', '9 days', '27', '81', '243', '729', '2187', '6561')
    y_pos = np.arange(len(objects))


    plt.bar(y_pos, bucketData, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.yscale('log')
    plt.title(name + " Age")

    plt.savefig('plots/'+name+'_quantity')

    plt.clf()

def genSizePlot(name, sizeData):
    objects = ('<1 day', '3 days', '9 days', '27', '81', '243', '729', '2187', '6561')
    y_pos = np.arange(len(objects))


    plt.bar(y_pos, sizeData, align='center', alpha=0.5, color='red')
    plt.xticks(y_pos, objects)
    plt.yscale('log')
    plt.title(name + " Size")

    plt.savefig('plots/'+name+'_size')

    plt.clf()

def createFileStruct(filename):
    if os.path.exists(filename.split(".")[0]):
        shutil.rmtree(filename.split(".")[0]) #clean dir

    os.makedirs(filename.split(".")[0]+'/plots')

    os.chdir(os.getcwd()+"/"+filename.split(".")[0])



def genHTMLFile(allProjects):
    with open("index.html", 'w') as fp:
        fp.write("<html>\n<table width=100%>\n")

        for i in range(len(allProjects)):
            curProject = allProjects[i]
            fp.write("<tr>\n")

            fp.write("<td> <img src=plots/"+curProject.name+"_quantity.png> </td>\n")
            fp.write("<td> <img src=plots/"+curProject.name+"_size.png> </td>\n")
            
            fp.write("<td><table style='font-size:150%'>\n")
            fp.write("<tr><td>Project Name: "+curProject.name+"</td></tr>\n")
            fp.write("<tr><td>Oldest File: "+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(curProject.oldest)))+"</td></tr>\n")
            fp.write("<tr><td>Number of Files: "+str(curProject.numberFiles)+"</td></tr>\n")
            fp.write("<tr><td>Total Project Size: "+sizeof_fmt(curProject.totalSize)+"</td></tr>\n")
            fp.write("<tr><td>Max Folder Depth: "+str(curProject.depth)+"</td></tr>\n")
            fp.write("</table></td>\n")


            fp.write("</tr>")

        fp.write("</table>\n</html>")

def main(filename):
    stack = []

    allProjects = []
    #of format changes in past [1 day, 3 day, 9 day, 27 day, 81, 243, 729, 2187]
    with open(filename, 'r', encoding='cp1252') as fp:

        createFileStruct(filename)

        fp.readline() #move through ncdu stat line
        #fp.readline() #move though /home/data line

        for line in fp:
            if line[0] == '[': #if dir
                dirName = line[10:].split('"', 1)
                stack.append(dirName[0])

                if len(stack) == 2:
                    #New project
                    allProjects.append(Project(dirName[0]))
                    curProject = allProjects[len(allProjects)-1]

                if (len(stack) >= 2) and (len(stack) > curProject.depth):
                    curProject.depth = len(stack)-2
                
            else: #if file
                fileTime = re.search('\"atime\":([0-9]+)', line).group(1)

                try:
                    aSize = re.search('\"asize\":([0-9]+)', line).group(1)
                except(AttributeError):
                    aSize = 0

                if (curProject.oldest > int(fileTime)) or (curProject.oldest == 0):
                    curProject.oldest = int(fileTime)
  
            
                bucket = getAgeBucket(fileTime)

                allProjects[len(allProjects)-1].addData(bucket)
                allProjects[len(allProjects)-1].addASize(bucket, aSize)

                curProject.numberFiles += 1
                curProject.totalSize += int(aSize)


            if line[-3] == ']': #if close dir
                stack.pop()
                endOfLine = -4
                while(line[endOfLine] == ']'): #repeat until all dirs closed
                    stack.pop()
                    endOfLine -= 1


            if len(stack) == 1:
                if(len(allProjects) == 0):
                    print("Top Level")
                else:
                    currentProject = allProjects[len(allProjects)-1]
                    print(currentProject.printData())
                    genAgePlot(currentProject.name, currentProject.ageData)
                    genSizePlot(currentProject.name, currentProject.sizeData)


        genHTMLFile(allProjects)


    

main("vol7.ncdu")
#main("smallTest.txt")
