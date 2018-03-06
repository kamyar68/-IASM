# This tools provides and estimation of home range distance that can be used for activity space
# and neighborhood modeling. The tool relies on an implementation of jenks optimization method adopted from the source below.
# part of code from http://danieljlewis.org/files/2010/06/Jenks.pdf
# described at http://danieljlewis.org/2010/06/07/jenks-natural-breaks-algorithm-in-python/
# Developed in Aalto University, SoftGIS team
# contact: kamyar.hasanzadeh@gmail.com
# external reference (Hasanzadeh, 2017) accessible at: https://www.sciencedirect.com/science/article/pii/S0143622817304034
# version 1.0.1
# last modified 6.3.2018
# works with GUI # comments added
## -----------------------------------------------------------------------
# Importing required modules
import numpy
import arcpy
## specifying input and output files/parameteres
# a shapefile/feature class including all activity points
# the file must include a field with calculated distances to individuals' home location
fc=arcpy.GetParameterAsText(0)
# name of the distance field - string
fieldname=arcpy.GetParameterAsText(1)
# do you want to exclude distant points using a threshold? Boolean (true or false)
# if true, spacify the threshold in the next step 
applythreshold=arcpy.GetParameterAsText(2)
threshold=arcpy.GetParameter(3)
# make sure that the optimum distance includes at least n percent of points in dataset
# n is 80 (%)  by default as defined and described in (Hasanzadeh, 2017)- can be modified below
n=80
# copying the distance field to a working list for faster processing
dataList = [row.getValue (fieldname) for row in arcpy.SearchCursor (fc)]
dataList = [float(x) for x in dataList]
# minimum number of classes for jenks algrorithm
# the optmizer will identify the optimum number of classes
numClass=2
# applying threshold - if set to true
if applythreshold== 'true':
  list2=list()
  for x in dataList:
      if x<threshold:
          list2.append(x)
          
  dataList=list2
## jenks function begins here
def getJenksBreaks( dataList, numClass ):
  dataList.sort()
  mat1 = []
  for i in range(0,len(dataList)+1):
    temp = []
    for j in range(0,numClass+1):
      temp.append(0)
    mat1.append(temp)
  mat2 = []
  for i in range(0,len(dataList)+1):
    temp = []
    for j in range(0,numClass+1):
      temp.append(0)
    mat2.append(temp)
  for i in range(1,numClass+1):
    mat1[1][i] = 1
    mat2[1][i] = 0
    for j in range(2,len(dataList)+1):
      mat2[j][i] = float('inf')
  v = 0.0
  for l in range(2,len(dataList)+1):
    s1 = 0.0
    s2 = 0.0
    w = 0.0
    for m in range(1,l+1):
      i3 = l - m + 1
      val = float(dataList[i3-1])
      s2 += val * val
      s1 += val
      w += 1
      v = s2 - (s1 * s1) / w
      i4 = i3 - 1
      if i4 != 0:
        for j in range(2,numClass+1):
          if mat2[l][j] >= (v + mat2[i4][j - 1]):
            mat1[l][j] = i3
            mat2[l][j] = v + mat2[i4][j - 1]
    mat1[l][1] = 1
    mat2[l][1] = v
  k = len(dataList)
  kclass = []
  for i in range(0,numClass+1):
    kclass.append(0)
  kclass[numClass] = float(dataList[len(dataList) - 1])
  countNum = numClass
  while countNum >= 2:
    id = int((mat1[k][countNum]) - 2)
    kclass[countNum - 1] = dataList[id]
    k = int((mat1[k][countNum] - 1))
    countNum -= 1
  return kclass
  
## Goodness of Variance Fit function definition  
def getGVF( dataList, numClass ):
  """
  The Goodness of Variance Fit (GVF) is found by taking the 
  difference between the squared deviations
  from the array mean (SDAM) and the squared deviations from the 
  class means (SDCM), and dividing by the SDAM
  """
  breaks = getJenksBreaks(dataList, numClass)
  dataList.sort()
  listMean = sum(dataList)/len(dataList)
  print listMean
  SDAM = 0.0
  for i in range(0,len(dataList)):
    sqDev = (dataList[i] - listMean)**2
    SDAM += sqDev
  SDCM = 0.0
  for i in range(0,numClass):
    if breaks[i] == 0:
      classStart = 0
    else:
      classStart = dataList.index(breaks[i])
      classStart += 1
    classEnd = dataList.index(breaks[i+1])
    classList = dataList[classStart:classEnd+1]
    classMean = sum(classList)/len(classList)
    print classMean
    preSDCM = 0.0
    for j in range(0,len(classList)):
      sqDev2 = (classList[j] - classMean)**2
      preSDCM += sqDev2
    SDCM += preSDCM
  return (SDAM - SDCM)/SDAM
  
# written by Drew
# used after running getJenksBreaks()
def classify(value, breaks):
  for i in range(1, len(breaks)):
    if value < breaks[i]:
      return i
  return len(breaks) - 1
# starting values for optimization process
gvf=0.00
numClass=2
while gvf < 0.98:
    numClass=numClass+1
    gvf= getGVF( dataList, numClass )
print 'optimom number of classes is: '+str(numClass)
a = numpy.array(dataList)
# the following lines are make sure that the optimum distance includes at least n percent of points in dataset
# n is 80 (%)  by default as defined and described in (Hasanzadeh, 2017)
# value can be changed by changing value for n in parameter definition section 
n=80
p = numpy.percentile(a, n)
con='FALSE'
i=0
kclass=getJenksBreaks( dataList, numClass )
while con=='FALSE':
    if kclass[i]>= p:
        con='TRUE'
        D3=kclass[i]
    else:
        i=i+1

arcpy.AddMessage( "According to the criteria, the optimum neighborhood distance for this dataset is: " + str(D3) ) 
        
    
