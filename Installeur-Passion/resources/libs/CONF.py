
import os
import sys
import ConfigParser

#import xbmc
from xbmcgui import Dialog

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


DIALOG_BROWSE = Dialog().browse


def SetConfiguration ():
    """
    Definit les repertoires locaux de l'utilisateur
    """

    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "Setting Configuration".center( 85 ) )
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )

    ROOTDIR = os.getcwd().replace(';','')
    fichier = os.path.join(ROOTDIR, "resources", "conf.cfg")
    config = ConfigParser.ConfigParser()
    config.read(fichier)
    USRPath = False

    if os.name=='posix':

        #Linux Case
        logger.LOG( logger.LOG_DEBUG, "linux case" )

        if os.path.isdir(".xbmc") == True:

            # Linux normal case
            XBMC = ".xbmc"+os.sep
            config.set("InstallPath", "path", XBMC)
            USRXBMC = os.sep+'usr'+os.sep+'share'+os.sep+'xbmc'+os.sep
            #Set Linux normal ScraperDir
            ScraperDir  = os.path.join(USRXBMC, "system"+os.sep+"scrapers"+os.sep+"video")
            config.set("InstallPath", "ScraperDir", ScraperDir)
            #Set Linux PMIIIDir
            PMIIIDir = os.path.join(USRXBMC, "skin")
            config.set("InstallPath", "PMIIIDir",PMIIIDir)
            USRPath = True

        else:

            #Linux other case
            XBMC = DIALOG_BROWSE(0, "Choisissez le dossier d'installation d'XBMC","files")
            logger.LOG( logger.LOG_DEBUG, "linux other case, XBMC = %s", XBMC )
            config.set("InstallPath", "path", XBMC)
            #Set Linux other case ScraperDir
            ScraperDir  = os.path.join(XBMC, "system"+os.sep+"scrapers"+os.sep+"video")
            config.set("InstallPath", "ScraperDir", ScraperDir)


    else:

        # Xbox and Windows case
        logger.LOG( logger.LOG_DEBUG, "Xbox and Windows case" )

        if os.path.isdir("Q:"+os.sep) == True:

            # Xbox and Windows normal case
            XBMC = "Q:"+os.sep
            config.set("InstallPath", "path", XBMC)

        else:

            # Xbox and Windows other case
            XBMC = DIALOG_BROWSE(0, "Choisissez le dossier d'installation d'XBMC","files")
            logger.LOG( logger.LOG_DEBUG, "win other case, XBMC = %s", XBMC )
            config.set("InstallPath", "path", XBMC)

        #Set Win ScraperDir
        scraperDir  = os.path.join(XBMC, "system"+os.sep+"scrapers"+os.sep+"video")
        config.set("InstallPath", "ScraperDir", scraperDir)

    #Set ScraperType
    config.set("InstallPath", "USRPath", USRPath)

    #Set ThemesDir
    ThemesDir   = os.path.join(XBMC, "skin")
    config.set("InstallPath", "ThemesDir", ThemesDir)

    #Set ScriptsDir
    ScriptsDir   = os.path.join(XBMC, "scripts")
    config.set("InstallPath", "ScriptsDir", ScriptsDir)

    #Set PluginDir
    PluginDir   = os.path.join(XBMC, "plugins")
    config.set("InstallPath", "PluginDir", PluginDir)
    PluginMusDir   = os.path.join(XBMC, "plugins" + os.sep + "music")
    config.set("InstallPath", "PluginMusDir", PluginMusDir)
    PluginPictDir   = os.path.join(XBMC, "plugins" + os.sep + "pictures")
    config.set("InstallPath", "PluginPictDir", PluginPictDir)
    PluginProgDir   = os.path.join(XBMC, "plugins" + os.sep + "programs")
    config.set("InstallPath", "PluginProgDir", PluginProgDir)
    PluginVidDir   = os.path.join(XBMC, "plugins" + os.sep + "video")
    config.set("InstallPath", "PluginVidDir", PluginVidDir)
    
    #Set ImageDir
    #ImageDir = os.path.join(ROOTDIR, "images")
    ImageDir = os.path.join(ROOTDIR, "resources", "skins", "Default", "media")
    config.set("InstallPath", "ImageDir", ImageDir)

    #Set CacheDir
    CacheDir = os.path.join(ROOTDIR, "cache")
    config.set("InstallPath", "CacheDir", CacheDir)
    
    #Set UserDataDir
    #UserDataDir = xbmc.translatePath( "Q:\\userdata" )
    UserDataDir = os.path.join(XBMC, "userdata")
    config.set("InstallPath", "UserDataDir", UserDataDir)

    #Save configuration
    config.set("InstallPath", "pathok", True)
    config.write(open(fichier,'w'))
