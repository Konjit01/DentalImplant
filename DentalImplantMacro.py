################################################################################
# Optimazation of dental implant planning tool using MeVisLab Python Script    #
################################################################################

# MeVis module import
from mevis import *

#Other imports
import math
import numpy
import time 

#Global varilables
totalNumOfImplants = 0
calculatingRight   = 0
implantPsnStatus   = []
PI_RAD             = 3.14
IBL      = 0.5
jawType            = ctx.field("selectJaw").value

######################################
# Making all implants parallel       #
######################################

def makeAllImplantsParallel():
  selectedImplant = int(ctx.field("SelectedImplant").value)
  noOfImplants    = getMarkerList().size()
  bypass = "SoBypass" + str(selectedImplant) + ".bypass"
  new    =  "SoBypass" + str(selectedImplant)
  transfmanipReference = ctx.field(ctx.field(new + ".baseIn0").connectedField().parent().childAtIndex(2).connectedField().parent().name + ".baseIn0").connectedField().parent().name
  i = 1
  for index in xrange(getMarkerList().size()):
    bypass = "SoBypass" + str(i) + ".bypass"
    if i <= noOfImplants:
      #print("In the make parallel")
      marker     = getMarkerList().getMarker(index)
      marker_ptr = [marker.x, marker.y, marker.z]
      list       = [marker.x, marker.y, marker.z]
      transfmanipName = ctx.field(ctx.field("SoBypass" + str(index+1) + ".baseIn0").connectedField().parent().childAtIndex(2).connectedField().parent().name + ".baseIn0").connectedField().parent().name
      ctx.field(transfmanipName.__str__() + ".rotation").value = ctx.field(transfmanipReference +  ".rotation").value
      rotation_value = ctx.field(transfmanipReference +  ".rotation").value
      rot_rad = rotation_value[3]
      if(index+1 == selectedImplant):
        ctx.field("Surface3DEditor.posXYZ").value = [marker.x, marker.y+math.cos(rot_rad)*marker.y +  marker.z+math.sin(rot_rad)*marker.z]
      else:
        rad_list =  ctx.field(transfmanipName.__str__() + ".rotation").value
        rad_value = rad_list[3]
        ctx.field("Surface3DEditor.posXYZ").value = [marker.x, marker.y+math.cos(rad_value)*marker.y +  marker.z+math.sin(rad_value)*marker.z]
       ctx.field(transfmanipName.__str__() + ".translation").value = ctx.field(transfmanipReference + ".translation").value     
     
      i+=1
  return

############################################
# Remove implant of selected marker        #
############################################
def removeImplatAtMArker():
  
  selectedImplant = int(ctx.field("SelectedImplant").value)
  jaw             = ctx.field("selectJaw").value
  marker          = getMarkerList().getMarker(selectedImplant-1)
  bypass          = "SoBypass"           + str(selectedImplant) + ".bypass"
  cylinder        = "SoCylinder"         + str(selectedImplant )
  transManip      = "SoTransformerManip" + str(selectedImplant ) 
  
  #getting the marker
  #getMarkerList().getMarker(selectedImplant-1)
  ctx.field("Surface3DEditor.index").value
  #ctx.field("Surface3DEditor.delete").touch()
  #resetting parameter
  ctx.field(cylinder + ".radius").value   = 1.75
  if jaw == "MAXILLA":
    ctx.field(cylinder + ".height").value = 12
  if jaw == "MANDIBLE":
    ctx.field(cylinder + ".height").value = 13
  ctx.field(bypass).value = False
  return

###################################
# Removes all implants            #
###################################
def removeAllImplants():
  i = 1
  global totalNumOfImplants
  jawType = ctx.field("selectJaw").value
  #print("Inside the remove implants", totalNumOfImplants)
  while i <= 12:
    bypass = "SoBypass" + str(i) + ".bypass"
    ctx.field(bypass).value = False
    i+=1
 
  totalNumOfImplants = 0
  ctx.field("CalculateVolumeAtMarker1.markerVec" ).value = [0,0,0]
  ctx.field("Surface3DEditor.deleteAll").touch()
  initImplantHeight(jawType)
  return

###################################
# Optimization implants parts     #
###################################
def getMarkerList():
  return ctx.field("ImplantMarker.outXMarkerList").object()

def getMarkerAtIndex(index):
  for x in xrange(getMarkerList().size()):
    #if x == index:
      #print(getMarkerList().getMarker(x), "At index", x )
    if index == x:
      markerptr = getMarkerList().getMarker(x) 
  return  getMarkerList().getMarker(x)
      
def initImplantHeight(jawType):
  i=1
  while(i <= 12):
    cylinder = "SoCylinder" + str(i)
    if(jawType == "MAXILLA"):
      ctx.field(cylinder + ".height").value = 12
      ctx.field(cylinder + ".radius").value = 1.75
    if(jawType == "MANDIBLE"): 
      ctx.field(cylinder + ".height").value = 13
      ctx.field(cylinder + ".radius").value = 1.75
    i+=1
  return

def returnPtrWemInfo(val):
  wemInfo = "WEMInfo" + str(val) 
  return ctx.field(wemInfo + ".outputCurveData").object()

def findAllPtsOnCircum(xPoint, yPoint, zPoint, radius):
  STEP = 0.0174533
  rad = 0
  numOfPoints = 0
  fileIObject = open("Nodes", 'w') 
  while(  rad <= 6.28):
    xDist =  radius*math.cos(rad) + xPoint
    yDist =  radius*math.sin(rad) + yPoint
    rad = rad + STEP
    numOfPoints+=1
    point = [xDist, yDist, zPoint]
    #print("xPoints", xDist, "yPoints", yDist )
    fileIObject.write(str(point) + "\n")
  #print("The number of points on the Cirum:", numOfPoints)
  return 

def getWEMObject():
  return ctx.field("WEMIsoSurface.outWEM").object()

def switchToBottomCyl():
  i = 1
  while i <= 12:
    baseSwitch = "BaseSwitch" + str(i)
    ctx.field(baseSwitch+ ".currentInput").value = 1
    i+=1

def getWEMInfoPtr():
  return ctx.field("SurfInfo.outputCurveData").object()

def MLWrapperCalls():
   #WEMMLWrappers
   WEMID   = getWEMObject().getId() # 218
   WEMName = getWEMObject().getName() # wem_245
   numOfPatches = getWEMObject().getNumWEMPatches() # numOfPatches = 1
   #Returns a pointer to the WEMPatch at the given POSITION in the internal list. 
   WEMPtr = getWEMObject().getWEMPatchAt(0) #MLWEMPatchWrapper (MLWEMPatchWrapper at: 0x38aa65f0)
   getWEM = getWEMObject().getWEMPatchById( 218 )
   #Returns a list with all WEMPatches. 
   getWEMList = getWEMObject().getWEMPatches() #MLWEMPatchWrapper (MLWEMPatchWrapper at: 0x23f92810
   #Returns whether the WEM is valid.
   #The WEM is valid if at least one member WEMPatch is non-NULL and contains a non-zero amount of faces and nodes.
   isValid = getWEMObject().isValid()
   getWEMObject().saveWEMSurface("qt/Desktop/wem")
   
   #MLWEMPatchWrapper
   description = WEMPtr.getDescription()
   #Accessing the properties of the WEMNodes of this WEMPatch. 
   numOfNodes = WEMPtr.getNumNodes() # = 31504
   #A class that wraps WEMPrimitiveValueList objects for use in scripting. 
   getMaxValue = getWEMInfoPtr()
   primitiveLUTValuesPtr = WEMPtr.createOrGetPrimitiveValueList('u')
   isLUTValuesValid = primitiveLUTValuesPtr.isValid()
   maxValueSurfaceInfo = ctx.field("SurfInfo.minPrimitiveValueList").value
   maxValue = primitiveLUTValuesPtr.getValues()
   minValue = primitiveLUTValuesPtr.getMinValue()
   #LUTValues = primitiveLUTValues().isValid()
   
    return
  
def getWEMConvertorObject(val):
  wemConvertor = "SoWEMConvertInventor" + str(val)
  #print("Cheking", wemConvertor)
  return ctx.field(wemConvertor + ".outWEM").object()

def getWEMConvertSideObject(val):
  wemConvertor = "WEMConvertor" + str(val)
  return ctx.field(wemConvertor + ".outWEM").object()

def getWEMNerveObject():
  nerveWEMObject = ctx.field("NerveInventorToWEM.outWEM").object()
  return nerveWEMObject

def outputSurfaceDistances():
  wemPatch = getWEMPatch()
  fileName = getFileName()
  if wemPatch and fileName:
    writeDistancesToFile(wemPatch, fileName)

def writeDistancesToFile(wemPatch, fileName):
  pvlName ="LUT"
  pvl = wemPatch.getPrimitiveValueList(pvlName)
  if pvl:    
    distancesAtPositions = []    
    distanceValues = pvl.getValues()
    for i in xrange(wemPatch.getNumNodes()):
      distanceValue = distanceValues[i]
      #print("In the function writeDistancesToFile", distanceValue)
      nodePosition  = wemPatch.getNodePositionAt(i)
      distancesAtPositions.append( (distanceValue, nodePosition) )
    writeDistancesPositionsToFile(distancesAtPositions, fileName)
  else:
    print "Unknown PVL:", pvlName

def writeDistancesPositionsToFile(distancesAtPositions):
  with open("Nodes", 'w') as fileIObject:
    fileIObject.write("{}\n".format(distancesAtPositions))

def getWEMPatch():
  wem = ctx.field("inWEM").object()
  wemPatch = None
  if wem:
    wemPatch = wem.getWEMPatchAt(0)
  return wemPatch
  
def getNerveWEMPatch():
  return ctx.field("NerveInventorToWEM.outWEM").object()
  
def getFileName():
  return ctx.field("file").value

def switchBetweenSideAndBottom(val):
  i = 1
  while(i <= 12):
    baseSwitch = "BaseSwitch" + str(i)
    if val == 0:
      ctx.field( baseSwitch + ".currentInput").value = 0
    if val == 1:
      ctx.field( baseSwitch + ".currentInput").value = 1
    i=+1
  return

#########################################################
# Implant Radius Optimization
##########################################################
def radiusOptumazation(cylinder, getSideSurface, wemSurface):
 
  implantRadius = ctx.field(cylinder   + ".radius").value
  surfacePatch  = getWEMObject().getWEMPatchAt(0)

  wem           = ctx.field(wemSurface + ".outWEM").object() 
  wemPatch = None
  if wem:
    wemPatch = wem.getWEMPatchAt(0)
    pvlName = "LUT"
    pvl     = wemPatch.getPrimitiveValueList(pvlName)
    if pvl:    
      distancesAtPositions = []    
      distanceValues       = pvl.getValues()
      countNegetiveDistValue = 0
      distAvgValue           = 0
      distSumValue           = 0
      for i in xrange(wemPatch.getNumNodes()):
        distanceValue = distanceValues[i]
        distSumValue += distanceValue
        nodePosition  = wemPatch.getNodePositionAt(i)
        if( distanceValue < 0):
          isNodeInside = surfacePatch.isPointInside(nodePosition)
          if isNodeInside == False:
            countNegetiveDistValue+=1
        distancesAtPositions.append( (distanceValue, nodePosition) )
      distAvgValue = distSumValue/wemPatch.getNumNodes()
      #print("avarage value:",  distAvgValue)
      #print("negative value and outside the selectJaw surfaces:", countNegetiveDistValue)
  return distAvgValue

##################################################################################################
#Returns an array that contains the radian values in which all top part of the implant is inside #
##################################################################################################
def checkIfImplantTopIsInside(index, bypass, marker, transfmanipName, cylinder, getSurfacePatch):
  jawType = ctx.field("selectJaw").value
  implantHeight   = ctx.field(cylinder+ ".height").value
  implantRadius   = ctx.field(cylinder+ ".radius").value
  nodesPostions   = []
  implantTopPatch = getWEMConvertorObject(index).getWEMPatchAt(0)
  radListUpperJaw = [1.20, 1.2217, 1.23, 1.25, 1.28, 1.3,  1.35] 
  radListLowerJaw = [1.4137, 1.4312, 1.4486, 1.4661, 1.4835, 1.5010, 1.5184, 1.5359 ]
  WEMInfoBottom      = "WEMInfo" + str(index)  
  center = ctx.field(WEMInfoBottom+ ".globalCenter").value 
 
  if jawType == "MAXILLA":
    radList  = radListUpperJaw
  if jawType == "MANDIBLE":
    radList  = radListLowerJaw
  for j in xrange( len(radList) ): 
    countOutsideNode     = 0
    countInsideNode      = 0
    if jawType ==  "MAXILLA":
      implantRotation = [1, 0, 0, PI_RAD + radList[j]]
    if jawType == "MANDIBLE":
      implantRotation = [1, 0, 0, PI_RAD - radList[j]]
    MLAB.processInventorQueue() 
    radValue   = implantRotation[3]
    #determines implant bottom position
    xBottomPos = marker.x
    yBottomPos = marker.y - math.cos(radValue)*(implantHeight)*IBL
    zBottomPos = marker.z - math.sin(radValue)*(implantHeight)*IBL
    implantBottomPosXYZ = [xBottomPos, yBottomPos, zBottomPos]
    #insert implant
    ctx.field(transfmanipName+    ".translation").value = implantBottomPosXYZ
    ctx.field(transfmanipName+    ".rotation").value    = implantRotation
    ctx.field(bypass).value = True
    
    for i in xrange(implantTopPatch.getNumNodes()-1 ):
      nodePostion  = implantTopPatch.getNodePositionAt(i)
      isNodeInside = getSurfacePatch.isPointInside(nodePostion)
      if isNodeInside == False: #there is a node outside the selectJaw surface 
        countOutsideNode+=1
    nodesPostions.append((countOutsideNode, radList[j]))
    
  ctx.field("SelectedImplant").value = index
  ctx.field("ImplantHeight").value   = implantHeight
  ctx.field("ImplantRadius").value   = implantRadius
 
  #print("Implant Height: ",   implantHeight, "mm")
  if(implantHeight == 7 ): ctx.field("implantStatus").value     =  "It might not be in its best position."
  return nodesPostions

###################################################################
# Checks if an implant is in contact with the canal nerve
###################################################################
def checkForCanalNerve(index, radValue, marker, transfmanipName, cylinder):
  #jawType = ctx.field("selectJaw").value
  implantTopPatch = getWEMConvertorObject(index).getWEMPatchAt(0)
  implantHeight   = ctx.field(cylinder+ ".height").value
  countInsideNode = 0
  for i in xrange(implantTopPatch.getNumNodes()):
    nodePostion = implantTopPatch.getNodePositionAt(i)
    nerve = getNerveWEMPatch().getNumWEMPatches()
    for i in xrange(getNerveWEMPatch().getNumWEMPatches()):
      getNervePatch = getNerveWEMPatch().getWEMPatchAt(i)
      isNodeInside  = getNervePatch.isPointInside(nodePostion)
      if(isNodeInside == True):
        countInsideNode+=1
  #print("Print it anyway", countInsideNode)    
  if(countInsideNode > 0):
    #print("SUCCESS", countInsideNode)
    implantHeight-=2
    ctx.field(cylinder+ ".height").value = implantHeight
  ctx.field("SelectedImplant").value = index
  ctx.field("ImplantHeight").value   = implantHeight
  xBottomPos = marker.x
  yBottomPos = marker.y - math.cos(radValue)*(implantHeight)*IBL
  zBottomPos = marker.z - math.sin(radValue)*(implantHeight)*IBL
  implantBottomPosXYZ = [xBottomPos, yBottomPos, zBottomPos]
  #insert implant
  ctx.field(transfmanipName+    ".translation").value = implantBottomPosXYZ
  #print("Height after nerve",   ctx.field(cylinder+ ".height").value, implantHeight)
  return
  
def radianValueForLargestDist(index, bypass, marker, selectedRadian, transfmanipName, cylinder):
 
  distValueAtRadian    =  []
  avgValueAtRadianSide =  []
  jawType       = ctx.field("selectJaw").value
  implantRadius = ctx.field(cylinder+ ".radius").value
  implantHeight = ctx.field(cylinder+ ".height").value
  wemSurface         = "WEMSurfaceDistance" + str(index)
  WEMInfoBottom      = "WEMInfo" + str(index) 
  implantSidePatch   = getWEMConvertorObject(index).getWEMPatchAt(0)
  for j in xrange(len(selectedRadian)): 
    if jawType == "MAXILLA":
      implantRotation  = [1, 0, 0, PI_RAD + selectedRadian[j]]
      MLAB.processInventorQueue()  
    if jawType == "MANDIBLE":
      implantRotation = [1, 0, 0, PI_RAD - selectedRadian[j]]
      MLAB.processInventorQueue() 
    radValue   = implantRotation[3]
    
    xBottomPos =  marker.x
    yBottomPos =  marker.y - math.cos(radValue)*(implantHeight)*IBL
    zBottomPos =  marker.z - math.sin(radValue)*(implantHeight)*IBL
    implantBottomPosXYZ = [xBottomPos, yBottomPos, zBottomPos]
    ctx.field(transfmanipName+ ".translation").value = implantBottomPosXYZ
    ctx.field(transfmanipName+ ".rotation").value    = implantRotation
    ctx.field(bypass).value = True
    #numOfImplantNodes   = ctx.field(WEMInfoBottom +".globalNumNodes").value - 1
    countNodeTouchNerve = 0
    wem                 = ctx.field(wemSurface+    ".outWEM").object() 
    implantBottomCenter = ctx.field(WEMInfoBottom+ ".globalCenter").value
    wemPatch = None
    if wem:
      wemPatch = wem.getWEMPatchAt(0)
    pvlName = "LUT"
    pvl     = wemPatch.getPrimitiveValueList(pvlName)
    if pvl:    
      distancesAtPositions  = []    
      distanceValues        = pvl.getValues()
      distSum = 0
      distAvgValue = 0
      for i in xrange(wemPatch.getNumNodes()):
        distanceValue = distanceValues[i]
        #distSum += distanceValue
        nodePosition  = wemPatch.getNodePositionAt(i)
        if(nodePosition == implantBottomCenter):
          distancesAtPositions.append( (distanceValue, nodePosition) )
      #distAvgValue = distSum/wemPatch.getNumNodes()
      distValueAtRadian.append((distanceValue, selectedRadian[j]))
  sortedAvgValues  = sorted(distValueAtRadian)
  #print("Shorest distance", distValueAtRadian)
  
  if(len(sortedAvgValues)>=1):
    largestAvgValue = sortedAvgValues[len(sortedAvgValues)-1]
    largestAvgValueIndex = distValueAtRadian.index(largestAvgValue)
    radValueOpt =  selectedRadian[largestAvgValueIndex]
    if(largestAvgValue <= 0.5):
      
      implantOptimumAngle   = [1, 0, 0, radValueOpt]
      MLAB.processInventorQueue()
      if jawType ==  "MAXILLA":
        implantOptimumAngle  = [1, 0, 0, PI_RAD + radValueOpt]
      if jawType == "MANDIBLE":
        implantOptimumAngle  = [1, 0, 0, PI_RAD - radValueOpt]
      xBottomPos = marker.x
      yBottomPos = marker.y - math.cos(radValueOpt)*(implantHeight)*IBL
      zBottomPos = marker.z - math.sin(radValueOpt)*(implantHeight)*IBL
      ctx.field(transfmanipName+ ".rotation").value    = implantOptimumAngle
      ctx.field(cylinder + ".height").value            = implantHeight
     
    else:
      implantOptimumAngle = [1,0,0, radValueOpt]
      MLAB.processInventorQueue()
      if jawType ==  "MAXILLA":
        implantOptimumAngle  = [1, 0, 0, PI_RAD + radValueOpt]
      if jawType == "MANDIBLE":
        implantOptimumAngle  = [1, 0, 0, PI_RAD - radValueOpt]
      xBottomPos = marker.x
      yBottomPos = marker.y - math.cos(radValueOpt)*(implantHeight)*IBL
      zBottomPos = marker.z - math.sin(radValueOpt)*(implantHeight)*IBL
      ctx.field(transfmanipName+ ".rotation").value    = implantOptimumAngle
      ctx.field(cylinder + ".height").value            = implantHeight
  return radValueOpt

def checkIfImplantSideIsInside(surfacePatch, implantTopPatch):
  count = 0
  if surfacePatch and implantTopPatch:
    for i in xrange(implantTopPatch.getNumNodes()):
      nodePostion  = implantTopPatch.getNodePositionAt(i)
      isNodeInside = surfacePatch.isPointInside(nodePostion)
      if isNodeInside == False:
        count+=1
  return count

def calculateAbsoluteDist(vec):
  distSquare = vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]
  result = math.sqrt(distSquare)
  return result
  
def checkMarkerStatus(marker1, marker2):
  x1,y1,z1 = marker1.x, marker1.y, marker1.z
  x2,y2,z2 = marker2.x, marker2.y, marker2.z
  vec1       = [ x1, y1, z1]
  vec2       = [ x2, y2, z2]
  resultVec  = [x1 - x2, y1- y2, z1 - z2]
  value = calculateAbsoluteDist(resultVec)
  return value

def insertImplantAtMarker():

  global totalNumOfImplants
  global implantPsnStatus
  jawType         = ctx.field("selectJaw").value
  getSurfacePatch = ctx.field("WEMIsoSurface.outWEM").object().getWEMPatchAt(0)
  i                     = 1 #important to keep the order of the implants from the .mlab file
  
  implantStatus         = ""
  allImplantsPositioned = []
  markerStatusAtIndex   = []
  
  if totalNumOfImplants < 12:
    for index in xrange( getMarkerList().size() ):
      if index <= getMarkerList().size():
        bypass = "SoBypass" + str(index + 1) + ".bypass"  #bool value with the corresponding SoBypass(index + 1)
        if ctx.field(bypass).value == False:
          marker = getMarkerList().getMarker(index)       #getting the pointer to the list that holds the point for index = index
          if( getMarkerList().size() > 0 ):               #for checking distance between two implants.
            marker2  = getMarkerAtIndex(index + 1)
            retValue = checkMarkerStatus(marker, marker2)
            if retValue < 5 and index < getMarkerList().size() - 1 :
              ctx.field("markerStatus").value = "The distance b/n 2 markers should greater than 5 mm."
            else:
              x, y, z = marker.x, marker.y, marker.z
              change = [x, y, z]
              ctx.field("CalculateVolumeAtMarker1.markerVec").value       = change
              MLAB.processInventorQueue()
              ctx.field("markerStatus").value = ""
              ctx.field("CalculateVolumeAtMarker1.planeClip4").value  = [0, 0, 1, 1.5708]
              MLAB.processInventorQueue()
              ctx.field("CalculateVolumeAtMarker1.planeClip3").value  = [0, 0, 1, 1.5708]
              MLAB.processInventorQueue()
              #checking if there is enough amount of bone volume or NOT!!!
              xExtent = ctx.field("CalculateVolumeAtMarker1.lengthXDrn").value 
              yExtent = ctx.field("CalculateVolumeAtMarker1.lengthYDrn").value
              zExtent = ctx.field("CalculateVolumeAtMarker1.lengthZDrn").value
              #print("Check if the values are:", xExtent, yExtent, zExtent)
              center        = ctx.field("CalculateVolumeAtMarker1.center").value
              optimizedYPos =   ctx.field("centerDecomposed.y").value
         
              volume = ctx.field("CalculateVolumeAtMarker1.calculatedVolume").value
              #print("The Volume is:", volume)
              if volume < MIN_BONE_VOL: 
                ctx.field("markerStatus").value = "No enough bone volume WARN!!"
              ctx.field("markerStatus").value   = "Enough bone volume."
              connectedField  = ctx.field("SoBypass" + str(index+1) + ".baseIn0")
              baseSwitch      = "BaseSwitch" + str(index + 1)#to switch from bottom to side implant
              #Corressponding SoTransformManip and SoCylinder from .mlab
              transfmanipName = ctx.field(connectedField.connectedField().parent().childAtIndex(2).connectedField().parent().name + ".baseIn0").connectedField().parent().name
              cylinder        = connectedField.connectedField().parent().childAtIndex(1).connectedField().parent().childAtIndex(2).connectedField().parent().name
              selectedRadian  = []
              #initial height and radius values of implant                
              implantHeight   = ctx.field(cylinder + ".height").value
              implantRadius   = ctx.field(cylinder + ".radius").value
              isInside        = True
              ctx.field(baseSwitch+ ".currentInput").value = 0
              #centroid  = ctx.field("CalculateWEMCentroid.centroid").value
              #COVx,  COVy, COVz     = centroid.x,  centroid.y,  centroid.z
              while implantHeight >= 7: #the height of implant cannot be less than 7 mm 
                ctx.field(cylinder+ ".height").value = implantHeight
                nodeRadPair = checkIfImplantTopIsInside(index + 1, bypass, marker, transfmanipName, cylinder, getSurfacePatch)
                #print("All radian values", nodeRadPair)
                for i in xrange(len(nodeRadPair)): #selecting with those their angle is 
                  if nodeRadPair[i][0] == 0:
                    selectedRadian.append(nodeRadPair[i][1])
                if(len(selectedRadian) == 0):
                  implantHeight-=0.5
                else:
                  optRadianValue = radianValueForLargestDist(index + 1, bypass, marker, selectedRadian, transfmanipName, cylinder)
                  break
              if(len(selectedRadian) == 0 ): #no selected radian value
                implantStatus = "No supporting bone avialable!"
                implantStatus  = "Implant might not be in its best position!!!"
                implantPsnStatus.append((index + 1, implantStatus)) 
              elif( implantHeight == 7 ): 
                implantStatus  = "Implant might not be in its best position!!!"
                implantPsnStatus.append((index + 1, implantStatus)) 
              else: 
                implantStatus  = "Implant is in its optimum postion!!!."
                implantPsnStatus.append((index + 1, implantStatus)) 
              #radius opt 
              implantRadius = ctx.field(cylinder+ ".radius").value
              ctx.field(baseSwitch+ ".currentInput").value = 1  
              sidePatch = getWEMConvertSideObject(index + 1).getWEMPatchAt(0)
              while(implantRadius >= 1.5):
                ctx.field(cylinder+ ".radius").value = implantRadius
                ctx.field("ImplantRadius").value = ctx.field(cylinder+ ".radius").value
                nodeRadPair1 = checkIfImplantSideIsInside(getSurfacePatch, sidePatch)
                if nodeRadPair1 > 11:
                  #print("Node outside", nodeRadPair1)
                  implantRadius-=0.1
                else:
                  break
             
              if jawType == "MANDIBLE" and implantHeight > 7:
                checkForCanalNerve(index + 1, optRadianValue, marker, transfmanipName, cylinder)
              
            ctx.field("implantStatus").value = implantPsnStatus[index][1]
            totalNumOfImplants += 1
      else:
        ctx.field(bypass).value = False
      i += 1
  else:
    ctx.field("markerStatus").value = "You have reached the limit!"
  #print("Implant status", implantPsnStatus)
  return totalNumOfImplants

###########################################
# Meausres the angle between two implants #
###########################################
def showAngleBetweenTwoImplants():
  PI = 3.141592653
  selectedImplantOne = ctx.field("SelectedImplant").value
  selectedImplantTwo = ctx.field("SelectedImplant2").value
  if(selectedImplantTwo >=1 and selectedImplantTwo <= 12):
  #bybass1 = "SoBypass" + str(selectedImplantOne) + ".bypass"
    bybass1 =  "SoBypass" + str(selectedImplantOne)
    transfmanipOne = ctx.field(ctx.field(bybass1 + ".baseIn0").connectedField().parent().childAtIndex(2).connectedField().parent().name + ".baseIn0").connectedField().parent().name
    bybass2 =  "SoBypass" + str(selectedImplantTwo)
    transfmanipTwo = ctx.field(ctx.field(bybass2 + ".baseIn0").connectedField().parent().childAtIndex(2).connectedField().parent().name + ".baseIn0").connectedField().parent().name
    rotation1 = ctx.field(transfmanipOne+ ".rotation").value
    rotation2 = ctx.field(transfmanipTwo+ ".rotation").value
    radValue  = rotation1[3] - rotation2[3]
    inDegree  = (radValue*180)/PI 
    if radValue < 0:
     inDegree = inDegree * -1
    ctx.field("radValue").value = inDegree
  return 

############################################
# GUI and View
############################################

def show(name):
  ctx.field("planningView.applyCameraOrientation").value  = name
  ctx.field("implantViewer.applyCameraOrientation").value = name
  return

def showPlaneChagned():
  ctx.field("ShowPlane.noBypass").value = 1 - ctx.field("display3DPlane").value
  return

def doNotShowPlane():
  ctx.field("ShowPlane.noBypass").value = 0 
  ctx.field("display3DPlane").value= 0
  return
  
def startXValue():
  ctx.field("cropImageInXYZ.x").value = ctx.field("startX").value
  return

def endXValue(field):
  ctx.field("cropImageInXYZ.sx").value = ctx.field("endX").value
  #ctx.addFieldListener()
  return

def startYValue(field):
  ctx.field("cropImageInXYZ.y").value = ctx.field("startY").value
  return

def endYValue(field):
  ctx.field("cropImageInXYZ.sy").value = ctx.field("endY").value
  return

def startZValue(field):
 ctx.field("cropImageInXYZ.z").value = ctx.field("startZ").value
 return

def endZValue(field):
 ctx.field("cropImageInXYZ.sz").value = ctx.field("endZ").value
 return

def applyCrop(field):
  ctx.field("cropImageInXYZ.apply").touch()
  return
  
def dirDataPathChanged(field):
  ctx.field("DicomModifyMultiFileVolumeExport.destinationDirectory").value = ctx.field("dirPathExportData").value
  return

def dirDataPathChanged(field):
  ctx.field("import.fullPath").value = ctx.field("dirPathImportData").value
  return 

def create3DTriggeredCrop(field): 
  ctx.field("Bypass.noBypass").value = 1
  ctx.field("import.dplImport").touch()
  return 

def exportDicomsToPath():
  #ctx.field("DicomModifyMultiFileVolumeExport.destinationDirectory").value = ctx.field("saveDICOMs").value
  ctx.field("DicomModifyMultiFileVolumeExport.export").touch()
  return

def doScreenshot():
  isIncrementalUpdate = ctx.field("renderer.incrementalUpdate").boolValue()
  ctx.field("renderer.incrementalUpdate").value = 0
  for i in range(50):
    MLAB.processInventorQueue()
  
  # do the screenshot:
  file = MLABFileManager.getUniqueFilename(MLABFileManager.getTmpDir(), "View3DTemp",".tif")
  ctx.control("viewer").createScreenshot(file)

  # ask user where to save it
  target = MLABFileDialog.getSaveFileName(MLAB.readKey("View3D","LastScreenshot"),"Image files (*.tif *.tiff *.png *.jpg)", "Save Screenshot");

  if target != "":
    if target.find(".") == -1:
      target += ".png"    
    MLABGraphic.convertImage(file, target)
    MLAB.writeKey("View3D","LastScreenshot", target)
    MLAB.writeRegistry()

  # remove tmp file
  MLABFileManager.remove(file)
  
  ctx.field("renderer.incrementalUpdate").value = isIncrementalUpdate
  return


def showImportProgress(field):
 ctx.field("status").value = ctx.field("import.progressInfo").value
 return
  
##############################
# Viewers parts              #
##############################
def selectViewerTypes():
 type = ctx.field("viewTypes").value

 if type == "AXIAL":
   show('CAMERA_AXIAL') 
 if type == "SAGITTAL":
   show('CAMERA_SAGITTAL')
 if type == "CORONAL" :  
   show('CAMERA_CORONAL')
 if type == "PROFILE" :
   show("CAMERA_HEAD_PROFILE")
 return

def progressChanged():
  progr = (ctx.field("WEMIsoSurface.progress").value + ctx.field("WEMSmooth.progress").value) / 2.0
  ctx.field("progress").value = progr
  return

def prefixNameExportChagned(field):
  ctx.field("DicomModifyMultiFileVolumeExport.destinationFileNameSuffix").value = ctx.field("prefixNameExport").value 
  return

def dirDataExportChanged(field):
  ctx.field("DicomModifyMultiFileVolumeExport.destinationDirectory").value = ctx.field("dirPathExportData").value
  return

def exportStatusChanged(field):
  ctx.field("statusExportDicom").value = ctx.field("DicomModifyMultiFileVolumeExport.status").value
  return

def namePatientLoadDICOM(field):
  ctx.field("namePatientLoad").value= ctx.field("FirstName.result").value
  return

def loadPatintSex(field):
  ctx.field("sexPatientLoad").value= ctx.field("DicomTagViewer.tagValue1").value
  return

def loadPatintAge(field):
  ctx.field("statusPatientAge").value = ctx.field("DateOfBirth.result").value
  return

def loadLastName(field): 
  ctx.field("lastNamePatientLoad").value = ctx.field("LastName.result").value
  return

def loadHospitalName(field):
  ctx.field("hostpitalName").value = ctx.field("NameHosp.result").value
  return

def loadPatientID(field):
  ctx.field("patientId").value = ctx.field("patientId.result").value
  return

def loadDocName(field):
  ctx.field("docName").value = ctx.field("drFullName.result").value
  return

def selectViewerTypesCrop(field):
  layoutModeValue = ctx.field("view").value
  
  if layoutModeValue == "LAYOUT_AXIAL": 
    ctx.field("SoOrthoView2D.layoutMode").value = 'LAYOUT_AXIAL'
  elif layoutModeValue == "LAYOUT_SAGITTAL":
    ctx.field("SoOrthoView2D.layoutMode").value = 'LAYOUT_SAGITTAL'
  elif layoutModeValue == "LAYOUT_CORONAL": 
    ctx.field("SoOrthoView2D.layoutMode").value = 'LAYOUT_CORONAL'
    show('LAYOUT_CORONAL')
  elif layoutModeValue == "LAYOUT_CUBE": 
    ctx.field("SoOrthoView2D.layoutMode").value = 'LAYOUT_CUBE'
  elif layoutModeValue == "LAYOUT_CUBE_EQUAL":
    ctx.field("SoOrthoView2D.layoutMode").value = 'LAYOUT_CUBE_EQUAL'
  elif layoutModeValue == "LAYOUT_CUBE_CUSTOMIZED":
    ctx.field("SoOrthoView2D.layoutMode").value = 'LAYOUT_CUBE_CUSTOMIZED'
  return

def measureOrPostions(field):
  type = ctx.field("Options").value
  if(type == "POSITION"):
    ctx.field("SoSwitch4.whichChild").value = 1
  if(type == "measure"):  
    ctx.field("SoSwitch4.whichChild").value = 0
  return

def deleteAllMarksMeasure(field):
  ctx.field("markToMeasure.deleteAll").touch()
  return
  
def planeAxialChagingValues(field):
  #ctx.field("MPR2.axial").touch()
  #ctx.field("MPR2.rotation").value  = [0, 0, 1, 1.57]
  return

def planeCronoalChagingValues():
  #ctx.field("MPR2.rotation").value  = [1, 0, 0, 1.57]
  return

def planeSaggintalChagingValues():
  #ctx.field("MPR2.rotation").value  = [0, 1, 0, 1.57]
  return

#Shows the positions
def maxXValueChanged():
  #print("X POSITION", ctx.field("markerPos.y").value) 
  return math.floor(ctx.field("getWorldInfo.voxelX").value) 

def maxYValueChanged():
  return  math.floor(ctx.field("getWorldInfo.voxelY").value)

def maxZValueChanged():
  return math.floor(ctx.field("getWorldInfo.voxelZ").value)

########################################
# File encryption and decryption       #
########################################
def encryption(privateInfo):
  BLOCK_SIZE = 16
  PADDING = '{'
  pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
  EncodingAES = lambda c, s: base64.b64decode(c.encrypt(pad(s)))
  secret = os.urandom(BLOCK_SIZE)
  print'encryption key:', secret
  cipher = AES.new(secret)
  encoded = EncodingAES(cipher, privateInfo)
  print 'Encrypted String', encoded
  
  
def derive_key_and_iv(password, salt, key_length, iv_length):
  d = d_i = ''
  while len(d) < key_length + iv_length:
    d_i = md5(d_i + password + salt).digest()
    d += d_i
  return d[:key_length], d[key_length:key_length+iv_length]

def encrypt(out_file, password, key_length=32):
    bs = AES.block_size
    salt = Random.new().read(bs - len('Salted__'))
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    out_file.write('Salted__' + salt)
    finished = False
    while not finished:
        chunk = 1024 * bs
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)
            finished = True
        out_file.write(cipher.encrypt(chunk))

def decrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = in_file.read(bs)[len('Salted__'):]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)



def applyCropToSelectedRegion(field):
  ctx.field("cropImageInXYZ.apply").touch()
  return

############################################
# Some settings and config to be refactored#
############################################
def sliceStepChanged(field):
  ctx.field("SoView2D1.sliceStep").value = ctx.field("sliceStep").value
  return

def startSliceValueChanged(field):
  ctx.field("SoView2D2.startSlice").value = ctx.field("SlicesSlider").value
  return

def planeAngleChanged(field):
  ctx.field("OcclualPlane.rotation").value = [1, 0, 0, ctx.field("planeDegree").value]
  rotation = ctx.field("OcclusalPlaneManip.rotation").value
  ctx.field("planeDegree").value = rotation[3]
  return

def markerPositionValueChanges():
  posX = maxXValueChanged()
  posY = maxYValueChanged()
  posZ = maxZValueChanged()
  marker = [posX, posY, posZ]
  ctx.field("markerPos").value = marker
  return

def resetAngleValue():
  deleteAllMarks()
  ctx.field("SoPerspectiveCamera.orientation").value = [0, 0, 1, 0]
  ctx.field("Reformat0.resetMatrix").touch()
  ctx.field("SoCameraInteraction1.viewAll").touch()
  ctx.field("planningView.viewAll").touch()
  

def showMPRPlaneAtSelectedImplant():
  selectedImplant  = int(ctx.field("SelectedImplant").value)
  transManip       = "SoTransformerManip" + str(selectedImplant)
  implantRotation  = ctx.field(transManip + ".rotation").value
  xTranslation     = ctx.field(transManip + ".translation").value
  xRadian          = implantRotation[3]
  ctx.field("MPR.translation").value  = ctx.field(transManip + ".translation").value
  if(xTranslation < 0):
    ctx.field("MPR.rotation").value   = implantRotation
    ctx.field("RotationSlider2").value= 3.14 
  if(xTranslation > 0):
    ctx.field("MPR.rotation").value   = implantRotation
    ctx.field("RotationSlider2").value= 1.5708 - xRadian #+ 3.14
  return

def implantOrSurfaceEdit(field):
  type = ctx.field("selectPlanningMode").value
  if(type == "implant"):
    ctx.field("ChooseMarker.whichChild").value = 0
  if(type == "editSurface"):  
    ctx.field("ChooseMarker.whichChild").value = 1
  return

def displayOcclusalPlane():
  return

def displayAxisXYZ():
  ctx.field("showAxis.noBypass").value = 1 - ctx.field("showAxisXYZ").value
  return

def initVoxleValue():
  ctx.field("cropImageInXYZ.fullSize").touch()
  name = ctx.field("cropImageInXYZ.fullSize").name
  type = ctx.field("cropImageInXYZ.fullSize").getName()
  return

def loadDone():
  ctx.field("import.dplImport").touch()
  if(ctx.field("dirPath").value == "" ):
    ctx.field("status").value = "Select the DICOM files first"
  ctx.field("cropImageInXYZ.fullSize").touch()
  ctx.field("DateOfBirth.toggle1").value = "TRUE"
  ctx.field("DateOfBirth.toggle2").value = "TRUE"
  ctx.field("DateOfBirth.toggle3").value = "TRUE"
  initCropValue()
  iniHistogramAxis()
  ctx.field("SoCameraInteraction1.viewAll").touch()
  ctx.field("viewPass.noBypass").value   = False
  return 

def create3DTriggereDone():
 
  removeAllImplants()
  deleteAllMarks()
  resetAngleValue()
  nerveDeleteAllLeft()
  nerveDeleteAllRight()
  ctx.field("import.dplImport").touch()
  if(ctx.field("dirPath").value == "" ):
    ctx.field("status").value = "Select the DICOM files first"
  ctx.field("cropImageInXYZ.fullSize").touch()
  ctx.field("DateOfBirth.toggle1").value = "TRUE"
  ctx.field("DateOfBirth.toggle2").value = "TRUE"
  ctx.field("DateOfBirth.toggle3").value = "TRUE"
  initCropValue()
  iniHistogramAxis()
  ctx.field("SoCameraInteraction1.viewAll").touch()
  ctx.field("viewPass.noBypass").value   = False
  return 

def initCropValue():
  ctx.field("endX").value = ctx.field("DICOMInfo.sizeX").value
  ctx.field("endY").value = ctx.field("DICOMInfo.sizeY").value
  ctx.field("endZ").value = ctx.field("DICOMInfo.sizeZ").value
  return

def columnNumChanged(field):
  ctx.field("SoView2D1.numXSlices").value = ctx.field("numOfColumn").value
  #ctx.field("SoView2D1.numSlices").value = ctx.field("AxialSlice.startSlice").value
  return

def exportArcTriggered():
  patientDir = ctx.field("defaultExportDir").value #+ "/home/qt/" + ctx.field("FirstName.result").value
  if os.path.exists(patientDir) == False:
    os.mkdir(patientDir)
  
  ctx.field("CSOSave.fileName").value = ctx.field("dirPathNerveExport").value
  ctx.field("CSOSave.startTaskSynchronous").touch()

  return

def minXHistValueChanged():
  ctx.field("SoDiagram2D.minX").value = ctx.field("minX").value
  return
  
def maxXHistValueChanged():
  ctx.field("SoDiagram2D.maxX").value = ctx.field("maxX").value
  return

def minYHistValueChangd():
  ctx.field("SoDiagram2D.minY").value = ctx.field("minY").value
  return

def maxYHistValueChanged():
  ctx.field("SoDiagram2D.maxY").value = ctx.field("maxY").value
  return
 
def implantStatusChanged():
  #selectedImplant                  = ctx.field("SelectedImplant").value
  #ctx.field("implantStatus").value = implantPsnStatus[selectedImplant][0]
  return
  
def markerStatusChanged():
  return

def factorChanged():
  ctx.field("CalculateVolumeAtMarker1.radius").value = ctx.field("factor").value
  return
