#!/usr/bin/python

# System imports

# Panda Engine imports
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from pandac.PandaModules import *
from panda3d.bullet import *
from direct.task.Task import Task
from direct.interval.IntervalGlobal import *

# Game imports

#----------------------------------------------------------------------#
# Blender Tagging:
# levelName = The level name duh
# levelDesc = short description
# ground = makes collision plane; Type = t-mesh
# box = static cube/box
# physic_box = dynamic cube
# physic_sensor = switches, doors, traps/hidden paths should glow up your gun or aura
# light = create light (may need sub tag for light type, but for now its just pointlights)
# pickup = pickable object
# exit = exit point
# start = spawn point
# wall = basic wall visual
# col_wall = collision shape
# physic_lift = physics based object that moves up or down
# physic_door
# complex_object
# size = Boxes have sizes s,m,l

# Make a proper bitmask list
# 0x01 = w/e...

class LevelBuilder():

    def __init__(self, _level):

    	self.level = _level
        self.eventMgr = self.level.game.eventMgr

    	# Object types in levels
    	self.objectTypes = {"ground": self.buildGround,
                            "box": self.buildBox,
                            "light": self.buildLight,
    						"pickup": self.buildPickupObject,
                            "exit": self.buildExitPoint,
                            "start": self.buildStartPoint,
    						"wall": self.buildWall,
                            "col_wall": self.buildColWall,
                            "physic_box": self.buildPhysicBox,
                            "physic_fuse": self.buildPhysicFuse,
                            "physic_sensor": self.buildPhysicSensor,
                            "level_name": self.setLevelName,
                            "level_desc": self.setLevelDesc,
                            "physic_lift": self.buildLift,
                            "physic_door":self.buildPhysicDoor,
                            "complex_object": self.buildComplexObject
                            }



    ## Event Method
    def parseEggFile(self, _levelFileName):
    	 # parse the level for setup

        self.levelModel = loader.loadModel(_levelFileName)

        # Find all objects
        self.objects = self.levelModel.findAllMatches('**')

        for object in self.objects:
            for type in self.objectTypes:
                if object.hasTag(type):
                    self.buildLevel(object, type, self.levelModel)
                    #print type, object

    def buildLevel(self, _object, _type, _levelRoot):
    	## Actual Level construction
        self.objectTypes[_type](_object, _levelRoot)

    def setLevelName(self, _object, _levelRoot):
        self.level.levelName = _object.getTag("level_name")

    def setLevelDesc(self, _object, _levelRoot):
        self.level.levelDesc = _object.getTag("level_desc")

    ## Builder Methods
    def buildGround(self, _object, _levelRoot):

        groundType = _object.getTag("type")

        if groundType == "t-mesh":

            tmpMesh = BulletTriangleMesh()
            node = _object.node()

            if node.isGeomNode():
                tmpMesh.addGeom(node.getGeom(0))
            else:
                return

            body = BulletRigidBodyNode(_object.getTag("ground"))
            body.addShape(BulletTriangleMeshShape(tmpMesh, dynamic=False))
            body.setMass(0)

            np = self.level.game.physicsParentNode.attachNewNode(body)
            np.setCollideMask(BitMask32.allOn())
            np.setScale(_object.getScale(_levelRoot))
            np.setPos(_object.getPos(_levelRoot))
            np.setHpr(_object.getHpr(_levelRoot))

            self.level.game.physicsMgr.physicsWorld.attachRigidBody(body)

            ## Set the visual
            _object.reparentTo(self.level.game.levelParentNode)
            _object.setPos(_object.getPos(_levelRoot))
            _object.setScale(_object.getScale(_levelRoot))
            _object.setHpr(_object.getHpr(_levelRoot))

            self.level.avoidObjects.append(_object.getTag("ground"))

        else:
            shape = BulletPlaneShape(Vec3(0, 0, 0.1), 1)
            node = BulletRigidBodyNode(_object.getTag("ground"))
            node.addShape(shape)
            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setPos(0, 0, -1)
            np.setCollideMask(BitMask32.allOn())


            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)
            _object.reparentTo(self.level.game.levelParentNode)
            _object.setPos(0, 0, 0)
            #_object.setDepthOffset(1)

            self.level.avoidObjects.append(_object.getTag("ground"))

    # These are static boxes.
    def buildBox(self, _object, _levelRoot):
        size = _object.getTag("size")

        if size == "s":
            shape = BulletBoxShape(Vec3(.2, .2, .2))
            node = BulletRigidBodyNode('box')
            node.addShape(shape)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos(_levelRoot))
            np.setHpr(_object.getHpr())
            _object.reparentTo(self.level.game.levelParentNode)
            _object.setScale(.2, .2, .2)
            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)

        if size == "m":
            shape = BulletBoxShape(Vec3(.5, .5, .5))
            node = BulletRigidBodyNode('box')
            node.addShape(shape)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos(_levelRoot))
            np.setHpr(_object.getHpr())
            _object.reparentTo(self.level.game.levelParentNode)
            _object.setScale(.5, .5, .5)
            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)

        if size == "l":
            shape = BulletBoxShape(Vec3(1, 1, 1))
            node = BulletRigidBodyNode('box')
            node.addShape(shape)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos(_levelRoot))
            np.setHpr(_object.getHpr())
            _object.reparentTo(self.level.game.levelParentNode)
            _object.setScale(1, 1, 1)
            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)


    def buildPhysicBox(self, _object, _levelRoot):
        # Make this more custom. for custom sizes.. or make a new method for handling those types
        # Large 1,1,1  Medium .5,.5,.5  Small .1,.1,.1

        # Get object size
        size = _object.getTag("size")

        if size == "s":
            shape = BulletBoxShape(Vec3(.2, .2, .2))
            node = BulletRigidBodyNode(_object.getTag("physic_box")+str(self.level.physicObjCount))
            node.addShape(shape)

            if _object.getTag("mass"):
                node.setMass(int(_object.getTag("mass")))
            else:
                node.setMass(1)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos())

            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)

            ## Set the visual
            _object.reparentTo(np)
            _object.setPos(0, 0, 0)
            _object.setScale(.2)
            _object.setHpr(0, 0, 0)

            ## Add the physic_box to the physicObjects list for gravity handling
            self.level.physicObjects[_object.getTag("physic_box")+str(self.level.physicObjCount)] = np
            self.level.physicObjCount += 1

        if size == "m":
            shape = BulletBoxShape(Vec3(1, 1, 1))
            node = BulletRigidBodyNode(_object.getTag("physic_box")+str(self.level.physicObjCount))
            node.addShape(shape)

            if _object.getTag("mass"):
                node.setMass(int(_object.getTag("mass")))
            else:
                node.setMass(1)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos())

            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)

            ## Set the visual
            _object.reparentTo(np)
            _object.setPos(0, 0, 0)
            _object.setScale(1)
            _object.setHpr(0, 0, 0)

            ## Add the physic_box to the physicObjects list for gravity handling
            self.level.physicObjects[_object.getTag("physic_box")+str(self.level.physicObjCount)] = np
            self.level.physicObjCount += 1

        if size == "l":
            shape = BulletBoxShape(Vec3(2, 2, 2))
            node = BulletRigidBodyNode(_object.getTag("physic_box")+str(self.level.physicObjCount))
            node.addShape(shape)

            if _object.getTag("mass"):
                node.setMass(int(_object.getTag("mass")))
            else:
                node.setMass(1)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos())

            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)

            ## Set the visual
            _object.reparentTo(np)
            _object.setPos(0, 0, 0)
            _object.setScale(2)
            _object.setHpr(0, 0, 0)

            ## Add the physic_box to the physicObjects list for gravity handling
            self.level.physicObjects[_object.getTag("physic_box")+str(self.level.physicObjCount)] = np
            self.level.physicObjCount += 1

    def buildPhysicFuse(self, _object, _levelRoot):
        # This is game related object needed to complete a level.
        # Fuses are like keys that the player can only push or move via a device.
        # Make this more custom. for custom sizes.. or make a new method for handling those types
        # Large 1,1,1  Medium .5,.5,.5  Small .1,.1,.1

        # Get object size
        size = _object.getTag("size")

        if size == "s":
            shape = BulletBoxShape(Vec3(.2, .2, .2))
            node = BulletRigidBodyNode(_object.getTag("physic_fuse"))
            node.addShape(shape)

            if _object.getTag("mass"):
                node.setMass(int(_object.getTag("mass")))
            else:
                node.setMass(1)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos())

            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)

            ## Set the visual
            _object.reparentTo(np)
            _object.setPos(0, 0, 0)
            _object.setScale(.2)
            _object.setHpr(0, 0, 0)

            ## Add the physic_box to the physicObjects list for gravity handling
            self.level.physicObjects[_object.getTag("physic_fuse")] = np
            self.level.physicObjCount += 1

        if size == "m":
            shape = BulletBoxShape(Vec3(1, 1, 1))
            node = BulletRigidBodyNode(_object.getTag("physic_fuse"))
            node.addShape(shape)

            if _object.getTag("mass"):
                node.setMass(int(_object.getTag("mass")))
            else:
                node.setMass(1)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos())

            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)

            ## Set the visual
            _object.reparentTo(np)
            _object.setPos(0, 0, 0)
            _object.setScale(1)
            _object.setHpr(0, 0, 0)

            ## Add the physic_box to the physicObjects list for gravity handling
            self.level.physicObjects[_object.getTag("physic_fuse")] = np
            self.level.physicObjCount += 1

        if size == "l":
            shape = BulletBoxShape(Vec3(2, 2, 2))
            node = BulletRigidBodyNode(_object.getTag("physic_fuse"))
            node.addShape(shape)

            if _object.getTag("mass"):
                node.setMass(int(_object.getTag("mass")))
            else:
                node.setMass(1)

            np = self.level.game.physicsParentNode.attachNewNode(node)
            np.setCollideMask(BitMask32.allOn())
            np.setPos(_object.getPos())

            self.level.game.physicsMgr.physicsWorld.attachRigidBody(node)

            ## Set the visual
            _object.reparentTo(np)
            _object.setPos(0, 0, 0)
            _object.setScale(2)
            _object.setHpr(0, 0, 0)

            ## Add the physic_box to the physicObjects list for gravity handling
            self.level.physicObjects[_object.getTag("physic_fuse")] = np
            self.level.physicObjCount += 1

    def buildPhysicSensor(self, _object, _levelRoot):
        tmpMesh = BulletTriangleMesh()
        node = _object.node()

        if node.isGeomNode():
            tmpMesh.addGeom(node.getGeom(0))
        else:
            return
        # Should be a ghost
        body = BulletGhostNode(_object.getTag("physic_sensor"))
        body.addShape(BulletTriangleMeshShape(tmpMesh, dynamic=False))
        #body.setMass(0)

        np = self.level.game.physicsParentNode.attachNewNode(body)
        np.setCollideMask(BitMask32(0x0f))
        np.setScale(_object.getScale(_levelRoot))
        np.setPos(_object.getPos(_levelRoot))
        np.setHpr(_object.getHpr(_levelRoot))

        self.level.game.physicsMgr.physicsWorld.attachGhost(body)

        ## Set the visual depending on type
        if _object.getTag("type") == "switch":
            _object.reparentTo(self.level.game.levelParentNode)
            _object.setPos(_object.getPos(_levelRoot))
            _object.setScale(_object.getScale(_levelRoot))
            _object.setHpr(_object.getHpr(_levelRoot))

        self.level.physicSensors[_object.getTag("physic_sensor")] = Sensor(self, _object.getTag("physic_sensor"), _object, np)



    def buildLight(self, _object, _levelRoot):

        if _object.getTag("light") == "point":
            plight = PointLight('plights')
            colorString = _object.getTag('color').split(',')
            color = VBase4(float(colorString[0]), float(colorString[1]), float(colorString[2]), 1)
            plight.setColor(color)
            #plight.setShadowCaster(True, 512, 512)
            plight.setAttenuation(Point3(0, 0.1, 0.05))
            plnp = render.attachNewNode(plight)
            plnp.setPos(_object.getPos())
            render.setLight(plnp)

        if _object.getTag("light") == "direct":
            dlight = DirectionalLight('dlight')
            colorString = _object.getTag('color').split(',')
            color = VBase4(float(colorString[0]), float(colorString[1]), float(colorString[2]), 1)
            dlight.setColor(color)
            #dlight.setShadowCaster(True, 512, 512)
            #dlight.getLens().setFilmSize(1024, 1024)
            dlight.getLens().setNearFar(40, 400)
            dlnp = render.attachNewNode(dlight)
            #dlnp.setHpr(_object.getHpr(_levelRoot))
            dlnp.setPos(_object.getPos(_levelRoot))
            dlnp.lookAt(0, 0, 0)
            render.setLight(dlnp)
            print "DIRECT LIGHT: ", _object.getHpr()

    # Something the player can put in his/her bag.
    def buildPickupObject(self, _object, _levelRoot):
    	tmpMesh = BulletTriangleMesh()
        node = _object.node()

        if node.isGeomNode():
            tmpMesh.addGeom(node.getGeom(0))
        else:
            return
        # Should be a ghost
        body = BulletGhostNode(_object.getTag("physic_sensor")+str(int(len(self.level.physicSensors))))
        body.addShape(BulletTriangleMeshShape(tmpMesh, dynamic=False))
        #body.setMass(0)

        np = self.level.game.physicsParentNode.attachNewNode(body)
        np.setCollideMask(BitMask32(0x0f))
        np.setScale(_object.getScale(_levelRoot))
        np.setPos(_object.getPos(_levelRoot))
        np.setHpr(_object.getHpr(_levelRoot))

        self.level.game.physicsMgr.physicsWorld.attachGhost(body)

        ## Set the visual depending on type
        if _object.getTag("type") == "switch":
            _object.reparentTo(self.level.game.levelParentNode)
            _object.setPos(_object.getPos(_levelRoot))
            _object.setScale(_object.getScale(_levelRoot))
            _object.setHpr(_object.getHpr(_levelRoot))

        #self.level.physicSensors[(_object.getTag("physic_sensor")+str(int(len(self.level.physicSensors))))] = Sensor(self, _object.getTag("physic_sensor"), _object)

        #self.level.avoidObjects.append(_object.getTag("coin"))

    def buildExitPoint(self, _object, _levelRoot):
    	pass

    def buildStartPoint(self, _object, _levelRoot):
    	self.level.spawnPoint = _object.getPos(_levelRoot)


    def buildWall(self, _object, _levelRoot):
        _object.reparentTo(self.level.game.levelParentNode)
        _object.setPos(_object.getPos(_levelRoot))
        _object.setScale(_object.getScale(_levelRoot))
        _object.setHpr(_object.getHpr(_levelRoot))
        if _object.getTag("two_face"):
            _object.setTwoSided(True)

    def buildColWall(self, _object, _levelRoot):

        tmpMesh = BulletTriangleMesh()
        node = _object.node()

        if node.isGeomNode():
            tmpMesh.addGeom(node.getGeom(0))
        else:
            return

        body = BulletRigidBodyNode(_object.getTag("col_wall"))
        body.addShape(BulletTriangleMeshShape(tmpMesh, dynamic=False))
        body.setMass(0)

        np = self.level.game.physicsParentNode.attachNewNode(body)
        np.setCollideMask(BitMask32.allOn())
        np.setScale(_object.getScale(_levelRoot))
        np.setPos(_object.getPos(_levelRoot))
        np.setHpr(_object.getHpr(_levelRoot))

        self.level.game.physicsMgr.physicsWorld.attachRigidBody(body)

    def buildLift(self, _object, _levelRoot):

        tmpMesh = BulletTriangleMesh()
        node = _object.node()

        if node.isGeomNode():
            tmpMesh.addGeom(node.getGeom(0))
        else:
            return

        ## Would be cool to have it breakable... if you hit it from the side.. it could go out of its forced alignment field.. of epic ness  :P
        body = BulletRigidBodyNode(_object.getTag("physic_lift"))
        body.addShape(BulletTriangleMeshShape(tmpMesh, dynamic=False))
        body.setMass(0)

        np = self.level.game.physicsParentNode.attachNewNode(body)
        np.setCollideMask(BitMask32.allOn())
        np.setScale(_object.getScale(_levelRoot))
        np.setPos(_object.getPos(_levelRoot))
        np.setHpr(_object.getHpr(_levelRoot))

        ## Set the visual
        ## The visual of the lift should be parented to the physics part so that they move
        _object.reparentTo(np)#self.level.game.levelParentNode)
        _object.setPos(0, 0, -0.2)
        #_object.setScale(_object.getScale(_levelRoot))
        #_object.setHpr(_object.getHpr(_levelRoot))

        self.level.game.physicsMgr.physicsWorld.attachRigidBody(body)

        self.level.physicLifts[_object.getTag("physic_lift")] = Lift(_object.getTag("physic_lift"), np, _object)


    def buildPhysicDoor(self, _object, _levelRoot):

        tmpMesh = BulletTriangleMesh()
        node = _object.node()

        if node.isGeomNode():
            tmpMesh.addGeom(node.getGeom(0))
        else:
            return

        body = BulletRigidBodyNode(_object.getTag("physic_door"))
        body.addShape(BulletTriangleMeshShape(tmpMesh, dynamic=False))
        body.setMass(0)

        np = self.level.game.physicsParentNode.attachNewNode(body)
        np.setCollideMask(BitMask32.allOn())
        np.setScale(_object.getScale(_levelRoot))
        np.setPos(_object.getPos(_levelRoot))
        np.setHpr(_object.getHpr(_levelRoot))

        ## Set the visual
        ## The visual of the lift should be parented to the physics part so that they move
        _object.reparentTo(np)#self.level.game.levelParentNode)
        _object.setPos(0, 0, 0)
        _object.setScale(1)
        _object.setHpr(0, 0, 0)

        self.level.game.physicsMgr.physicsWorld.attachRigidBody(body)

        self.level.physicDoors[_object.getTag("physic_door")] = Door(self, _object.getTag("physic_door"), np, _object)

        self.level.avoidObjects.append(_object.getTag("physic_door"))

    def buildComplexObject(self, _object, _levelRoot):
        tmpMesh = BulletTriangleMesh()
        node = _object.node()

        if node.isGeomNode():
            tmpMesh.addGeom(node.getGeom(0))
        else:
            return

        body = BulletRigidBodyNode(_object.getTag("complex_object"))
        body.addShape(BulletTriangleMeshShape(tmpMesh, dynamic=False))
        body.setMass(0)

        np = self.level.game.physicsParentNode.attachNewNode(body)
        np.setCollideMask(BitMask32.allOn())
        np.setScale(_object.getScale(_levelRoot))
        np.setPos(_object.getPos(_levelRoot))
        np.setHpr(_object.getHpr(_levelRoot))

        self.level.game.physicsMgr.physicsWorld.attachRigidBody(body)

        ## Set the visual
        _object.reparentTo(self.level.game.levelParentNode)
        _object.setPos(_object.getPos(_levelRoot))
        _object.setScale(_object.getScale(_levelRoot))
        _object.setHpr(_object.getHpr(_levelRoot))

        self.level.avoidObjects.append(_object.getTag("complex_object"))





### Physic objects ###
class Lift():

    def __init__(self, _name, _np, _object):
        self.name = _name
        self.object = _object
        self.np = _np

    def registerEvent(self):
        pass

    def handleLift(self):
        if self.liftState != True:
            duration = 2.0
            pos = lift.getPos() + (0, 0, 7)
            startPos = lift.getPos()
            liftPosInterval = LerpPosInterval(lift, duration, pos, startPos)
            liftPosInterval.start()
            self.liftState = _state

class Door():

    def __init__(self, _builder, _name, _np, _object):
        self.builder = _builder
        self.name = _name
        self.object = _object
        self.np = _np
        self.state = _object.getTag("state")
        self.rotateAxisString = _object.getTag("rotate") # Needs a split ',' ('y', 44)
        rot = self.rotateAxisString.split(',')


        self.startHpr = self.np.getHpr()
        self.expectedHpr = self.startHpr + self.getRotationAxis(rot)
        self.currentHpr = Vec3(0, 0, 0)

        if _object.hasTag("accept_command"):
            self.registerEvent()

    def getRotationAxis(self, _rot):
        if _rot[0] == "x":
            print "x"
        elif _rot[0] == "y":
            return Vec3(0, 0, float(_rot[1]))
        elif _rot[0] == "z":
            print "z"

    def registerEvent(self):
        self.builder.level.game.eventMgr.registerEvent(self.object.getTag("accept_command"), self.handle)

    def handle(self):

        if self.state != True:
            # open
            self.currentHpr = self.np.getHpr()

            if self.currentHpr <= self.expectedHpr:
                pos = self.expectedHpr
                startPos = self.np.getHpr()

            duration = 2.0
            doorHprInterval = LerpHprInterval(self.np, duration, pos, startPos)
            doorHprInterval.start()
            self.state = True
        else:
            # close
            self.currentHpr = self.np.getHpr()

            if self.currentHpr >= self.startHpr:
                pos = self.startHpr
                startPos = self.np.getHpr()

            duration = 2.0
            doorHprInterval = LerpHprInterval(self.np, duration, pos, startPos)
            doorHprInterval.start()
            self.state = False

class Sensor(DirectObject):

    def __init__(self, _builder, _name, _object, _np):
        self.builder = _builder
        self.name = _name
        self.object = _object
        self.np = _np
        self.type = _object.getTag("type")
        self.state = _object.getTag("state")
        self.needs = None

        # Tasks 
        self.priority = 70

        # Cmd if switch
        self.sendCommand = None

        if self.type == "switch":
            print "This is a switch"
            self.sendCommand = _object.getTag("send_command")
            self.needs = {}
            needs = _object.getTag("needs")
            needs = [x.strip() for x in needs.split(',')]

            # Set a state for each need
            for need in needs:
                self.needs[need] = False
            

        elif self.type == "lock":
            print "This is a lock"
            pr = self.priority ++ 1
            self.setUnlock = _object.getTag("set_unlock")
            self.needs = _object.getTag("needs")
            taskMgr.add(self.update, "sensor-update-"+str(self.name), priority=pr)
            print "sensor-update-"+str(self.name)

    def setControl(self, _command):
        pass

    def update(self, task):
        # Only if lock type
        # Check for overlapping nodes
        # If correct node found update switch connected to this lock

        sensor = self.np.node()
        for node in sensor.getOverlappingNodes():
            if "key" in node.getName():
                if node.getName() == self.needs:
                    #print node.getName(), self.needs
                    messenger.send("handle-lock", [self.name, self.setUnlock])

        return task.cont
