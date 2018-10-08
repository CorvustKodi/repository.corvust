
import requests, zipfile, os, StringIO, shutil, time
import xml.dom.minidom
import hashlib

sourceURL = 'https://github.com/corvustkodi/%s/archive/master.zip'
tmp_location = "tmp"
# List of Git sources
sources = ['script.slurpee']

def getVersionFromXml(xml_path,addonsNode):
	a = open(xml_path,'rt')
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
	return v

def md5(fname):
	md5f = open(fname+'.md5','wt')
	hash_md5 = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	md5f.write(hash_md5.hexdigest())
	md5f.close()

def processAddon(nameVersion,tmp_location,dest_location):
	# Look for any existing files in the add-on directory
	if not os.path.exists(dest_location):
		os.mkdir(dest_location)
	oldFiles = os.listdir(dest_location)
	isUpToDate = False
	for f in oldFiles:
		if f != nameVersion+'.zip' and f != nameVersion+'.zip.md5':
			os.remove(os.path.join(dest_location,f))
		else:
			isUpToDate = True

	if not isUpToDate:
		shutil.make_archive(os.path.join(dest_location,nameVersion), 'zip', tmp_location)
		md5(os.path.join(dest_location,nameVersion+'.zip'))
	if os.path.exists(tmp_location):
		shutil.rmtree(tmp_location, ignore_errors=True)
		time.sleep(2)

if os.path.exists(tmp_location):
	shutil.rmtree(tmp_location, ignore_errors=True)
	time.sleep(2)

addonsDoc = xml.dom.minidom.getDOMImplementation().createDocument(None,'addons',None)
addonsNode = addonsDoc.documentElement

# Now create the zip for the repo
repodir = 'repository.corvust'

if not os.path.exists(os.path.join(tmp_location,repodir)):
	if not os.path.exists(tmp_location):
		os.mkdir(tmp_location)
	os.mkdir(os.path.join(tmp_location,repodir))

ver = getVersionFromXml('addon.xml',addonsNode)
zipName =  repodir + '-' + ver

shutil.copyfile('addon.xml',os.path.join(tmp_location,repodir,'addon.xml'))
shutil.copyfile('changelog.txt',os.path.join(tmp_location,repodir,'changelog.txt'))
shutil.copyfile('icon.png',os.path.join(tmp_location,repodir,'icon.png'))

processAddon(zipName,tmp_location,repodir)

shutil.copyfile('addon.xml',os.path.join(repodir,'addon.xml'))
shutil.copyfile('changelog.txt',os.path.join(repodir,'changelog.txt'))
shutil.copyfile('icon.png',os.path.join(repodir,'icon.png'))

for source in sources:
	if not os.path.exists(tmp_location):
		os.mkdir(tmp_location)
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
	v = getVersionFromXml(os.path.join(tmp_location,source,'addon.xml'),addonsNode)
	newName = source + '-'+v

	processAddon(newName,tmp_location,source)

f = open('addons.xml','wt')
f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
f.write(addonsNode.toprettyxml(encoding='utf-8'))
f.close()
addonsDoc.unlink()
md5('addons.xml')


