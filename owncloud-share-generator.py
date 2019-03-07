#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import configparser
import owncloud  # pip install pyocclient
# import urllib.request as urllib2  # Python3
from urllib.error import HTTPError
import importlib
import sys

importlib.reload(sys)


# Class for parsing config .cfg file
class Settings(object):

    def __init__(self, configfile):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(configfile)

    def load(self, section, opts):
        try:
            for key in opts:
                try:
                    setattr(self, key, self.config.get(section, key))
                except configparser.NoOptionError:
                    setattr(self, key, self.config.get('default', key))

        except configparser.NoSectionError:
            print('The section "%s" does not exist' % section)
        except configparser.NoOptionError:
            print('The value for "%s" is missing' % key)
        else:
            return True
        return False


cfg_forum = 'dctrad'

cfg_opts = ['host',
            'username',
            'password'
            ]

cfg = Settings('owncloud.cfg')
if cfg.load(cfg_forum, cfg_opts):
    # oc = owncloud.Client('http://dl.dctrad.fr')
    oc = owncloud.Client(cfg.host)
    # oc.login('Staff', 'staff123')
    oc.login(cfg.username, cfg.password)

    print ('--------------------------------------------------------------')
    print ('      Entrez (ou collez) le chemin vers le dossier Owncloud: ')
    print ('      Exemple : DC Comics/New 52/Groupe Batman/Batman')
    print ('--------------------------------------------------------------')

    try:
        folder = raw_input()
    except Exception as e:
        folder = input()

    try:
        list_dir = oc.list(folder)
        print ('-------------------------------------------------------------')
        print ('         ____                      __                __')
        print ('        / __ \_      ______  _____/ /___  __  ______/ /')
        print ('       / / / / | /| / / __ \/ ___/ / __ \/ / / / __  /')
        print ('      / /_/ /| |/ |/ / / / / /__/ / /_/ / /_/ / /_/ /')
        print ('      \____/ |__/|__/_/ /_/\___/_/\____/\__,_/\__,_/  ' +
               oc.get_version()+'')
        print ('                                              ')
        print ('-------------------------------------------------------------')

        for files in list_dir:
            newName = files.get_name()
            path = files.get_path() + '/' + newName

            try:
                if not oc.is_shared(path):
                    link_info = oc.share_file_with_link(files)
                    newName = newName.replace('.cbz', '')
                    newName = newName.replace('.cbr', '')
                    print ('[url='
                           + link_info.get_link()
                           + ']' + newName
                           + '[/url]')
            except owncloud.owncloud.HTTPResponseError as e:
                pass

        print ('-------------------------------------------------------------')
    except HTTPError as e:
        print(e.code)
    except owncloud.owncloud.HTTPResponseError as e:
        print("Dossier non valide")

    input("Pressez une touche pour quitter")
