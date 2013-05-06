'''
Mediasite presentation downloader script.

This script downloads video and slides of a mediasite presentation, and puts them in appropriate folders.

Requires requests python library, as well as mplayer tool.

Created on Apr 9, 2013
Last Update: 6 May 2013
@author: abiusx
@version: 1.1
'''
import requests,re,os,glob,sys
if (__name__!="__main__"):
    exit();
def file_put_contents(filename,data):
    f = open(filename, 'w',"utf-8")
    f.write(data)
    f.close()
def file_get_contents(filename):
    try:
        return open(filename).read()
    except (IOError):
        return "";
if (len(sys.argv)>=2):
    url=sys.argv[1]
else:
    url = raw_input ("Enter mediasite video url:")

#url = "http://ini.mediasite.com/mediasite/Viewer/?peid=89c7ab797d7c4c7abfec6ad77a6ad35f1d";
print ("Processing "+url)

response= requests.get(url);
data=response.text



title=re.search("<title>(.*?)<\/title>",data,re.S).group(1).strip()
fileTitle=title.replace(":","_").replace(" ","_").replace("__","_")
print "Presentation title: <%s>"%title;


manifestUrl=re.search("<script src=\"(.*?manifest.js.*?)\"",data).group(1)
print ("Found manifest URL: "+manifestUrl);
response=requests.get(manifestUrl);
data=response.text

videoUrl=re.search("Manifest.VideoUrl=\"(.*?)\";",data).group(1);
#print videoUrl
slideBaseUrl=re.search("Manifest.SlideBaseUrl=\"(.*?)\";",data).group(1)
#print slideBaseUrl
slideFileFormat=re.search("Manifest.SlideImageFileNameTemplate=\"(.*?)\";",data).group(1)
slideFileFormatPython=slideFileFormat[0:slideFileFormat.index("{")]+"%"+slideFileFormat[slideFileFormat.index("}")-1]+"d"+slideFileFormat[slideFileFormat.index("}")+1:];
#print slideFileFormat
#print slideFileFormatPython
slideCount=int(re.search("Manifest.Slides = new Array\((\d*)\);",data).group(1))
print "\nFound %s slides."%slideCount
slideTimes=[]
slideNames=[]
slideFileNames=[]
for i in range(0,slideCount):
    slideTimes.append(int(re.search("Manifest.Slides\["+str(i)+"\] = new Slide\(\"\",(\d*),\"\"\);",data).group(1)))
    slideNames.append((slideFileFormatPython % (i+1)).replace(" ","0"))
    timeSeconds=(slideTimes[-1]/1000)
    timeString=("_min%dsec%2d"%(timeSeconds/60,timeSeconds%60)).replace(" ","0");
    slideFileNames.append(slideNames[-1][0:slideNames[-1].index(".")]+timeString+slideNames[-1][slideNames[-1].index("."):])
#print slideFileNames

#everything set, start downloading
folder=fileTitle
try:
    os.mkdir(folder);
except OSError:
    pass;

videoDownloadCommand=None
if (not glob.glob(folder+"/*.avi")): #no video downloaded yet
    print "\nIMPORTANT: You should initiate the following command to download the video of this presentation, because it takes a long time. You need the mplayer tool for that. If you don't, I will try to do it after downloading slides."
    folderAbs=os.path.abspath(folder);
    videoDownloadCommand="mplayer -dumpstream -dumpfile '%s' '%s'"%(folderAbs+"/"+fileTitle+".avi",videoUrl);
    print (videoDownloadCommand);
state=0;
r=file_get_contents(folder+"/_state");
if (r):
    state=int(r);
    print "Found terminated session, resuming from slide number %d ..." % (state+1)
for i in range (state,slideCount):
    file_put_contents(folder+"/_state", str(i))
    print "Downloading slide %d: " % (i+1) + slideFileNames[i]
    data=requests.get(slideBaseUrl+slideNames[i]).content
    file_put_contents(folder+"/"+slideFileNames[i], data)

print "\nFinished Downloading Slides\n"

if (not glob.glob(folder+"/*.avi")): #no video downloaded yet
    print ("trying to download the presentation video, this might take a while depending on your connection speed:")
    print (videoDownloadCommand);
    os.system(videoDownloadCommand)
else:
    print ("seems you have downloaded the video, so all is done. Goodbye.")