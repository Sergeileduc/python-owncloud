#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import configparser
import owncloud  # pip install pyocclient
from urllib.error import HTTPError
import importlib
import sys
import os

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

smallify_path = '/Documents/scripts/Windows/smallify.bat'

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

    # try:
    #     folder = raw_input()
    # except Exception as e:
    #     folder = input()

    try:
        folder_path = '/'
        folder_name = ''
        user_input = 0
        while True:
            list_dir = oc.list(folder_path, depth=1)
            print("==========================================================")
            print("Contenu de : " + folder_path)
            print("Dossiers")
            print("..........................................................")
            i = 1
            folder_list = []
            for file in list_dir:
                if file.is_dir():
                    name = file.get_name()
                    # path = file.get_path() + '/' + newName
                    path = file.get_path()
                    folder_list.append((path, name))
                    # print(newName)
                    print(str(i) + "-\t" + path)
                    i += 1
            print("==========================================================")
            print("Fichiers")
            print("..........................................................")
            for file in list_dir:
                if not file.is_dir():
                    newName = file.get_name()
                    path = file.get_path() + '/' + newName
                    # path = file.get_path()
                    print(newName)
            print("==========================================================")
            choice = input("tapez un chiffre pour naviguer dans "
                           "le dossier, ou 'd' pour télécharger.\n")
            if choice != 'd':
                try:
                    folder_path = folder_list[int(choice)-1][0]
                    folder_name = folder_list[int(choice)-1][1]
                except IndexError:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("Mauvaise valeur")

            else:
                break

        try:
            os.mkdir(folder_name)
        except OSError:
            pass

        os.chdir(folder_name)

        oc.get_file(smallify_path)

        for file in list_dir:
            if not file.is_dir():
                newName = file.get_name()
                path = file.get_path() + '/' + newName
                oc.get_file(path)

    except HTTPError as e:
        print(e.code)
    except owncloud.owncloud.HTTPResponseError as e:
        print("Dossier non valide")

    input("Pressez une touche pour quitter\n")
