# -*- coding: cp1252 -*-
"""
ARTE Plus7 video plugin for XBMC 

Place in Q:\plugins\video\artePLUS7

13-10-07 Version Alpha Release by Lolol (cf. http://xbmc.org/forum/showthread.php?t=29100)
    - Creation
29-11-08 Version Alpha2 by Temhil and Seb
    - Fixed issue with icons
    - Fixed issue wit video loading using createVideoURL which create a UNRl from the video preview URL
    - Replaced default URL by French one instead of German
02-12-08 Version Beta1 by Temhil
    - Added proxy support for people wiht not an PI address in the area supported by Arte website
      Proxy has to be defined in arteplus7.cfg as follow:
      [server]
      proxy_address = http://<IP-adress>
    - Updated getVideoURL in order to use proxy AND load real video URL in wmv container
    - Added video language support, it has to be defined (fr = fench / de = German) as follow 
      [user_pref]
      videos_language = fr
    - Conf file is generated automatically during 1st startup:
      -> default video language is French
      -> default proxy is empty (no proxy)
07-12-08 Version Beta1.1 by Seb
    - Corrected progress bar update issue
07-12-08 Version Beta2 by Temhil
    - Improved algorithm with proxy use, no proxy is use only for a video (not all of them)
    - few UI improvment
"""
import xml.dom.minidom, urllib, os, string, traceback, time, re
import xbmc, xbmcgui, xbmcplugin
import traceback
import urllib2
import ConfigParser


# Set directories
RootDir  = os.getcwd().replace( ";", "" ) # Create a path with valid format
cacheDir = os.path.join(RootDir, "cache")

class confManager:
    """
    Configuration Manager
    """
    def __init__(self,confFilePath):
        """
        Load configuration file, check it, and correct it if necessary
        """
        self.is_conf_valid   = True
        self.confFilePath    = confFilePath
        self.proxy_address   = ""
        self.videos_language = "fr"
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(confFilePath)


            # Check sections exist
            if (self.config.has_section("server") == False):
                self.config.add_section("server")
                self.is_conf_valid = False
            if (self.config.has_section("user_pref") == False):
                self.config.add_section("user_pref")
                self.is_conf_valid = False

            # - Read config from file and correct it if necessary
            if (self.config.has_option("server", "proxy_address") == False):
                self.config.set("server", "proxy_address", self.proxy_address)
                self.is_conf_valid = False
            else:
                self.proxy_address = self.config.get("server", "proxy_address")
                
            if (self.config.has_option("user_pref", "videos_language") == False):
                self.config.set("user_pref", "videos_language", self.videos_language)
                self.is_conf_valid = False
            else:
                self.videos_language = self.config.get("user_pref", "videos_language")
        
            if (self.is_conf_valid == False):
                # Update file
                print "cfg file format wasn't valid: correcting ..."
                cfgfile=open(self.confFilePath, 'w+')
                try:
                    self.config.write(cfgfile)
                    self.is_conf_valid = True
                except Exception, e:
                    print("Exception during cfg file update")
                    print(str(e))
                    print (str(sys.exc_info()[0]))
                    traceback.print_exc()
                cfgfile.close()
        
        except IOError:
            print "Error while loading conf file arteplus7.cfg"
            print (str(sys.exc_info()[0]))
            traceback.print_exc(file=sys.stdout)

    def setProxy(self,proxy_address):
        self.proxy_address   = proxy_address
        
        # Set proxy_address parameter
        self.config.set("server", "proxy_address", proxy_address)
    
        # Update file
        cfgfile=open(self.confFilePath, 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setProxy")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getProxy(self):
        return self.proxy_address
    
    def setVideosLang(self,videos_language):
        self.videos_language   = videos_language
        
        # Set videos_language parameter
        self.config.set("user_pref", "videos_language", videos_language)
    
        # Update file
        cfgfile=open(self.confFilePath, 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setVideosLang")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getVideosLang(self):
        return self.videos_language
    

class SearchParser:
    """
    Parse XML  from arte - code from seeqpod. seeqpod Borrowed this from GameTrailersRSSReader RSS Parser
    """
    def __init__(self):
        # Document Object Model of the XML document
        self.dom = None
        self.cfgMgr = confManager(os.path.join(RootDir,"arteplus7.cfg"))
        self.verifrep(cacheDir)
        if self.cfgMgr.getVideosLang() == 'de':
            # German videos
            video_feed_url = "http://plus7.arte.tv/de/streaming-home/1698112,templateId=renderCarouselXml,CmPage=1697480,CmPart=com.arte-tv.streaming.xml"
        else:
            # French videos
            video_feed_url = "http://plus7.arte.tv/fr/streaming-home/1698112,templateId=renderCarouselXml,CmPage=1697480,CmPart=com.arte-tv.streaming.xml"
                                           
    def verifrep(self, folder):
        """
        Check a folder exists and make it if necessary
        """
        try:
            #print("verifrep check if directory: " + folder + " exists")
            if not os.path.exists(folder):
                print("verifrep Impossible to find the directory - trying to create the directory: " + folder)
                os.makedirs(folder)
        except Exception, e:
            print("Exception while creating folder " + folder)
            print(str(e))

            
    def delFiles(self,folder):
        """
        Delete file form cache directory
        """
        for root, dirs, files in os.walk(folder , topdown=False):
            for name in files:
                print "Deleting %s ..."%name
                try:
                    os.remove(os.path.join(root, name))
                except Exception, e:
                    print e
                    
    def reset(self):                                           
        # Document Object Model of the XML document
        self.dom = None
    
    # feeds the xml document from given url to the parser
    def feed(self, url):
        self.dom = None
        #print url
        f = urllib.urlopen(url)
        xmlDocument = f.read()
        f.close()
        self.dom = xml.dom.minidom.parseString(xmlDocument)

    def loadVideo(self, videoPage):
        print "getVideoURL - videoPage = %s"%videoPage
        opener              = None
        videoUrl            = ""
        videoContainerUrl   = "" 
        proxy_address       = self.cfgMgr.getProxy()
                
        if proxy_address == "":
            print "getVideoURL - NO proxy defined"
            # create opener
            opener = urllib2.build_opener()
        else:
            print "getVideoURL - proxy DEFINED"
            print proxy_address
            
            # create the proxy handler
            proxy_handler = urllib2.ProxyHandler({'http':proxy_address})
            
            # create opener
            opener = urllib2.build_opener(proxy_handler)

        # install the opener
        urllib2.install_opener(opener)
        
        # Get the Web page with the video url container link
        req=urllib2.Request(videoPage)
        videoDoc=urllib2.urlopen(req).read()
        
        # Write in a file
        open(xbmc.makeLegalFilename(os.path.join(cacheDir, os.path.basename(videoPage))),"w").write(videoDoc)

        # Extract the URL of the video URL container file (wmv)
        match = re.search(r'availableFormats\[\d]\[\"format\"\] = \"WMV\";\n *?availableFormats\[\d\]\["quality\"] = \"HQ\";\n *?availableFormats\[\d]\[\"url\"] = "(.*?)\?obj', videoDoc)
        videoContainerUrl = ""
        if match:
            videoContainerUrl = match.group(1)
            
            # Get the video url container file
            videoUrlFile = urllib.urlopen(videoContainerUrl).read()
            #TODO: use urllib2 everywhere, using a mix or urlib and urllib2 is not very elegant
            
            # Write in a file
            open(xbmc.makeLegalFilename(os.path.join(cacheDir, os.path.basename(videoContainerUrl))),"w").write(videoUrlFile)
            
            # Extract the URL of the video (usually mms)
            matchVideoURL = re.search(r'<REF HREF=\"(.*?)\" />', videoUrlFile)
            if matchVideoURL:
                videoUrl = matchVideoURL.group(1)
                

        player_type = {0:xbmc.PLAYER_CORE_AUTO, 1:xbmc.PLAYER_CORE_MPLAYER, 2:xbmc.PLAYER_CORE_DVDPLAYER}[int(xbmcplugin.getSetting("player_type"))]
        xbmc.Player(player_type).play(videoUrl)
        xbmc.sleep(200)
        
        
        print "videoContainerUrl = %s"%videoContainerUrl
        print "videoUrl = %s"%videoUrl
        return videoUrl
       
    def downloadFile(self, source, destination):
        """
        Source MyCine (thanks!)
        Download IF NECESSARY a URL 'source' (string) to a URL 'target' (string)
        Source is downloaded only if target doesn't already exist
        """
        if os.path.exists(destination):
            pass
        else:
            try:
                #print("downloadJPG destination doesn't exist, try to retrieve")
                loc = urllib.URLopener()
                loc.retrieve(source, destination)
            except Exception, e:
                print("Exception while source retrieving")
                print(e)
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
                pass


    # parses the RSS document, for now it assumes that RSS document is valid
    def parse(self):
        self.delFiles(cacheDir)
        self.__parseItems()
    
    # parses RSS document items and returns an list containing RSSItem objects
    def __parseItems(self):
        items = self.dom.getElementsByTagName("video")
        self.urls={}
        self.thumbs={}
        self.titles={}
        self.index={}
        self.startDates={}
        self.speakingthumbs={}
        self.previewVideoUrl={}
        itemObjects = []
        i=0
        for item in items:
            i=i+1
            #print i
            elements = {}
            try:
                self.thumbs[i] = item.getElementsByTagName("previewPictureURL")[0].childNodes[0].data
                self.urls[i] = item.getElementsByTagName("targetURL")[0].childNodes[0].data
                self.startDates[i] = item.getElementsByTagName("startDate")[0].childNodes[0].data
                self.titles[i] = item.getElementsByTagName("title")[0].childNodes[0].data
                self.index[i] = item.getElementsByTagName("index")[0].childNodes[0].data
                self.previewVideoUrl[i] = item.getElementsByTagName("previewVideoURL")[0].childNodes[0].data
                
                index = self.index[i]
                localimg = xbmc.makeLegalFilename(os.path.join(cacheDir,self.index[i]+".jpg"))
                #localimg.replace('\\\\','\\')
                print "i = %d"%i
                print "self.thumbs[i] (URL) = %s"%self.thumbs[i]
                print "self.urls[i] = %s"%self.urls[i]
                print "localimg = %s"%localimg
                self.downloadFile(self.thumbs[i],localimg)

#                liz=xbmcgui.ListItem(index.zfill(2)+' - '+self.titles[i],'',localimg)
                liz=xbmcgui.ListItem(index.zfill(2)+' - '+self.titles[i], iconImage = localimg, thumbnailImage = localimg)
                print "Adding item %d"%i
                #ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=videoUrl,listitem=liz,isFolder=False,totalItems=len(items))
                u=sys.argv[0]+"?url="+urllib.quote_plus(self.urls[i])+"&loadvideo"
                ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True,totalItems=len(items))
            except:
                error=1
                print "Something was wrong during __parseItems!"
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
                
        #TODO: Use language localization
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="Liste des vid�os d'Arte+7" )
#        path_img = os.path.join(RootDir,"arteFanart.jpg")
#        fanart_color1 = "ffffff00"
#        fanart_color2 = ""
#        fanart_color3 = ""
#        try:
#            xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=path_img, color1=fanart_color1, color2=fanart_color2, color3=fanart_color3 )
#        except:
#            error=1
#            print "Something was wrong during setPluginFanart!"
#            print (str(sys.exc_info()[0]))
#            traceback.print_exc()
 
        return itemObjects


#Il faut parser les param�tres
stringparams = sys.argv[2] #les param�tres sont sur le 3ieme argument pass� au script
try:
    if stringparams[0]=="?":#pour enlever le ? si il est en d�but des param�tres
        stringparams=stringparams[1:]
except:
    pass
parametres={}
for param in stringparams.split("&"):#on d�coupe les param�tres sur le '&'
    try:
        cle,valeur=param.split("=")#on s�pare les couples cl�/valeur
    except:
        cle=param
        valeur=""
    parametres[cle]=valeur #on rempli le dictionnaire des param�tres
#voil�, 'parametres' contient les param�tres pars�s


s=SearchParser()
if "loadvideo" in parametres.keys():
    # Play video
    urlVideoPage=urllib.unquote_plus(parametres["url"])
    print "urlVideoPage: "
    print urlVideoPage
    s.loadVideo(urlVideoPage)
else:
    # Video list
    s.feed("http://plus7.arte.tv/fr/streaming-home/1698112,templateId=renderCarouselXml,CmPage=1697480,CmPart=com.arte-tv.streaming.xml")
    s.parse()
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

