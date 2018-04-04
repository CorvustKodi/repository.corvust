
import requests, zipfile, os, StringIO, shutil, time
import xml.dom.minidom
import hashlib

sourceURL = 'https://github.com/corvustkodi/%s/archive/master.zip'
tmp_location = "tmp"
# List of Git sources
sources = ['script.slurpee']

def md5(fname):
	md5f = open(fname+'.md5','wt')
	hash_md5 = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	md5f.write(hash_md5.hexdigest())
	md5f.close()

if os.path.exists(tmp_location):
	shutil.rmtree(tmp_location, ignore_errors=True)
	time.sleep(2)

os.mkdir(tmp_location)

addonsDoc = xml.dom.minidom.getDOMImplementation().createDocument(None,'addons',None)
addonsNode = addonsDoc.documentElement

for source in sources:
	# Retrieve the zip file for the add-on
	r = requests.get((sourceURL % source), stream=True)
	if not r.ok:
		print 'Error downloading %s' % (sourceURL % source)
		exit()
	z = zipfile.ZipFile(StringIO.StringIO(r.content))
	z.extractall(tmp_location)
	z.close()
	os.rename(os.path.join(tmp_location,source+'-master'),os.path.join(tmp_location,source))
	# Extract the addon.xml so we can read the version, and append to addons.xml.
	a = open(os.path.join(tmp_location,source,'addon.xml'),'rt')
	try:
		doc = xml.dom.minidom.parse(a)
	except Exception as details:
		print details
		exit()
	a.close()
	aNode = doc.getElementsByTagName('addon')[0]
	v = aNode.attributes['version'].value
	addonsNode.appendChild(aNode)
	# Build the new zip file name
	newName = source + '-'+v

	if not os.path.exists(source):
		os.mkdir(source)
	# Look for any existing files in the add-on directory
	oldFiles = os.listdir(source)
	isUpToDate = False
	for f in oldFiles:
		if f != newName+'.zip' and f != newName+'.md5':
			os.remove(os.path.join(source,f))
		else:
			isUpToDate = True
	
	if not isUpToDate:
		shutil.make_archive(os.path.join(source,newName), 'zip', tmp_location)
		md5(os.path.join(source,newName+'.zip'))
	if os.path.exists(tmp_location):
		shutil.rmtree(tmp_location, ignore_errors=True)
		time.sleep(2)

f = open('addons.xml','wt')
f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
f.write(addonsNode.toprettyxml(encoding='utf-8'))
f.close()
addonsDoc.unlink()
md5('addons.xml')






