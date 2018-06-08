import time
import xml.etree.cElementTree as etree
import xml.dom.minidom as dom

inputfile = open("simplecubease.xml", "r")
inputdata = dom.parse(inputfile)
inputfile.close()

root = etree.Element("scene")

root.set("version", "0.5.0")

# Set up cameras

for camera in inputdata.getElementsByTagName("CAMERAOBJECT") :
	# Go into camera
	camera_name = camera.getAttribute("NODE_NAME")
	camera_type = camera.getAttribute("CAMERA_TYPE")
	curr_camera = etree.SubElement(root, "sensor")
	curr_camera.set("type", "perspective") # by default it's gonna be perspective

	# Go into transform
	transf_camera = etree.SubElement(curr_camera, "transform")
	transf_camera.set("name", "toWorld")
	if(camera_type=="Target"):
		lookat_camera = etree.SubElement(transf_camera, "lookat")
		origin = "INVALID ORIGIN"
		target = "INVALID TARGET"
		for node in camera.getElementsByTagName("NODE_TM"):
			node_name = node.getAttribute("NODE_NAME")
			if node_name==camera_name :
				origin = node.getAttribute("TM_POS")
			elif node_name==camera_name+".Target" :
				target = node.getAttribute("TM_POS")
			else :
				print("UNKNOWN CAMERA NODE :\ncamera : "+camera_name+"\nnode : "+node_name)
		if origin == "INVALID ORIGIN" or target == "INVALID TARGET":
			print("INVALID ORIGIN OR TARGET for camera "+camera_name)

		lookat_camera.set("origin", origin)
		lookat_camera.set("target", target)
	elif(camera_type=="Free"):
		transl_camera = etree.SubElement(transf_camera, "translate")
		print("FREE CAMERA UNFINISHED")
	else:
		print("Camera type unknown : "+camera_type)
	# The default fov is 60 for max, and in the ase the fov is just the factor to multiply 60
	fov = 60 * float(camera.getElementsByTagName("CAMERA_SETTINGS")[0].getAttribute("CAMERA_FOV"))
	camera_fov = etree.SubElement(curr_camera, "float")
	camera_fov.set("name", "fov")
	camera_fov.set("value", str(fov))
	# Max expresses the the vertical fov
	camera_fov_axis = etree.SubElement(curr_camera, "string")
	camera_fov_axis.set("name", "fovAxis")
	camera_fov_axis.set("value", "y")








tree = etree.ElementTree(root)
tree.write("simplecubemitsuba.xml")


xmlstr = dom.parse("simplecubemitsuba.xml")

# print(xmlstr.toprettyxml())
outputfile = open("simplecubemitsuba.xml", "w")
outputfile.write(xmlstr.toprettyxml())

# time.sleep(1)
