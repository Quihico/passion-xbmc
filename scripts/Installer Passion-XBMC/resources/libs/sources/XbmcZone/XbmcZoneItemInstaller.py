"""
ItemInstaller: this module allows download and install an item
"""

# Modules general
import os
import sys
import httplib
import urllib2
from traceback import print_exc

# Modules custom
import Item
import CONF
#import extractor
from utilities import *
try:
    from ItemInstaller import ArchItemInstaller, cancelRequest
except:
    print_exc()

httplib.HTTPConnection.debuglevel = 1

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


class XbmcZoneItemInstaller(ArchItemInstaller):
    """
    Download an item on XBMC Zone Web server and install it
    """

    def __init__( self , name, type, filename, downloadurl ):
        ArchItemInstaller.__init__( self, name, type )
        self.downloadurl = downloadurl
        self.filename    = filename

#        #get base url for download
#        self.baseurl = "http://xbmczone.com/download.asp?id="
        
        #TODO: support progress bar display

    def downloadItem( self, msgFunc=None,progressBar=None ):
        """
        Download an item form the server
        Returns the status of the download attemos : OK | ERROR
        """
        percent = 0
        totalpercent = 0
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.name ), _( 123 ) % totalpercent )
        try:            
            print "HTTPInstaller::downloadItem - Downloading item %s" % self.name
            
            # Get download link
                               
            #fileURL  = self.baseurl + str(self.itemId)
            
            # Download file (to cache dir) and get destination directory
            status, downloadArchivePath = self._downloadFile( self.downloadurl, self.CACHEDIR, progressBar=progressBar )
        
        except Exception, e:
            #print "Exception during downlaodItem"
            #print e
            #print sys.exc_info()
            print_exc()
            downloadArchivePath = None
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.name ), _( 134 ) )
        return status, downloadArchivePath



    def getFileSize(self, sourceurl):
        """
        get the size of the file (in octets)
        !!!ISSUE!!!: +1 on nb of download just calling this method with Passion-XBMC URL
        """
        file_size = 0
        try:
            connection  = urllib2.urlopen(sourceurl)
            headers     = connection.info()
            file_size   = int( headers['Content-Length'] )
            connection.close()
        except Exception, e:
            print "Exception during getFileSize"
            print e
            print sys.exc_info()
            print_exc()
        return file_size
#
#    def getFileName(self, sourceurl):
#        """
#        get the size of the file name
#        """
#        file_name = ""
#        try:
#            connection  = urllib2.urlopen(sourceurl)
#            headers     = connection.info()
#            file_name   = headers['Content-Disposition'].split('"')[1]
#            connection.close()
#        except Exception, e:
#            print "Exception during getFileName"
#            print e
#            print sys.exc_info()
#            print_exc()
#        return file_name
    


#    def _downloadFile(self, url, destinationDir,msgFunc=None,progressBar=None):
    def _downloadFile(self, url, destinationDir, progressBar=None):
        """
        Download a file at a specific URL and send event to registerd UI if requested
        Returns the status of the download attemos : OK | ERROR
        """
        print("_downloadFile with url = " + url)
        print("_downloadFile with destination directory = " + destinationDir)
        destination = None
        #destination = os.path.join( destinationDir, filename )
        #noErrorOK  = True # When noErrorOK == True -> no error/Exception occured
        status     = "OK" # Status of download :[OK | ERROR | CANCELED]
        
        try:
            # -- Downloading
            print("_downloadFile - Trying to retrieve the file")
            block_size          = 4096
            percent_downloaded  = 0
            num_blocks          = 0
            file_size           = None
            
            req = urllib2.Request(url) # Note: downloading item with passion XBMC URL (for download count) even when there is an external URL
            req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3')
            connection  = urllib2.urlopen(req)           # Open connection
#                try:
#                    headers = connection.info()# Get Headers
#                    print "headers:"
#                    print headers
#                    file_name   = headers['Content-Disposition'].split('"')[1]
#                except Exception, e:
#                    file_name = "unknownfilename.rar"
#                    print("_downloadFile - Exception retrieving header")
#                    print(str(e))

            
            print "_downloadFile - file name : %s "%self.filename
            destination = os.path.join( destinationDir, self.filename )
            print 'destination'
            print destination
            
            # Get file size from the external URL header
            file_size = self.getFileSize(url)

            print "_downloadFile - file size : %d Octet(s)"%file_size

            file = open(destination,'w+b')        # Get ready for writing file
            print "File opened"
            # Ask for display of progress bar
            try:
                if (progressBar != None):
                    progressBar.update(percent_downloaded)
            except Exception, e:        
                print("_downloadFile - Exception calling UI callback for download")
                print(str(e))
                print progressBar
                
            ###########
            # Download
            ###########
            print "Starting download"
            while 1:
                if (progressBar != None):
                    if progressBar.iscanceled():
                        print "Downloaded STOPPED by the user"
                        status = "CANCELED"
                        break
                try:
                    cur_block  = connection.read(block_size)
                    if not cur_block:
                        break
                    file.write(cur_block)
                    # Increment for next block
                    num_blocks = num_blocks + 1
                except Exception, e:        
                    print("_downloadFile - Exception during reading of the remote file and writing it locally")
                    print(str(e))
                    print ("error during reading of the remote file and writing it locally: " + str(sys.exc_info()[0]))
                    print_exc()
                    #noErrorOK  = False
                    status = "ERROR"
                    # End of writing: Closing the connection and the file
                    #connection.close()
                    #file.close()
                    #raise e
                try:
                    # Compute percent of download in progress
                    New_percent_downloaded = min((num_blocks*block_size*100)/file_size, 100)
                    #print "_downloadFile - Percent = %d"%New_percent_downloaded
                except Exception, e:        
                    print("_downloadFile - Exception computing percentage downloaded")
                    print(str(e))
                    #noErrorOK  = False
                    New_percent_downloaded = 0
                    status = "ERROR"
                    # End of writing: Closing the connection and the file
                    #connection.close()
                    #file.close()
                    #raise e
                # We send an update only when percent number increases
                if (New_percent_downloaded > percent_downloaded):
                    percent_downloaded = New_percent_downloaded
                    #print ("_downloadFile - Downloaded %d %%"%percent_downloaded)
                    # Call UI callback in order to update download progress info
                    if (progressBar != None):
                        progressBar.update(percent_downloaded)


            # Closing the file
            file.close()
            # End of writing: Closing the connection and the file
            connection.close()
        except Exception, e:
            status = "ERROR"
            print("Exception while source retrieving")
            print(str(e))
            print ("error while source retrieving: " + str(sys.exc_info()[0]))
            print_exc()
            print("_downloadFile ENDED with ERROR")

#            # Prepare message to the UI
#            msgType = "Error"
#            msgTite = _ ( 144 )
#            msg1    = file_name
#            msg2    = ""
#            msg3    = ""

        print("_downloadFile ENDED")

#        if status == "OK":
#            # Prepare message to the UI
#            msgType = "OK"
#            msgTite = _( 137 )
#            msg1    = file_name
#            msg2    = _( 134 )
#            msg3    = ""
#        elif status == "CANCELED":
#            # Prepare message to the UI
#            msgType = "OK"
#            msgTite = _ ( 124 )
#            msg1    = file_name
#            msg2    = _ ( 125 )
#            msg3    = ""
#        else:
#            print "_downloadFile - An error has occured"
#            destination = None
#
#            # Prepare message to the UI
#            msgType = "Error"
#            msgTite = _ ( 144 )
#            msg1    = file_name
#            msg2    = ""
#            msg3    = ""
                            
#        # Close/Reset progress bar
#        if (progressBar != None):
#            progressBar.close()
        
#        # Send the message to the UI
#        try:
#            if (msgFunc != None):
#                msgFunc(msgType, msgTite, msg1,msg2, msg3)
#        except Exception, e:        
#            print("_downloadFile - Exception calling UI callback for message")
#            print(str(e))
#            print msgFunc
                
        return status, destination
        
