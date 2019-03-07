#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import configparser
import owncloud  # pip install pyocclient
# import urllib.request as urllib2  # Python3
from urllib.error import HTTPError
import requests.exceptions
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
    try:
        oc.login(cfg.username, cfg.password)
    except requests.exceptions.MissingSchema:
        print("Erreur.\n"
              "Veuillez configurer owncloud.cfg avec une url correcte")
        input("Pressez une touche pour quitter")
        sys.exit(1)
    except owncloud.owncloud.HTTPResponseError as e:
        print("Erreur.\n"
              "Veuillez configurer owncloud.cfg avec utilisateur "
              "et mot de passe valide")
        # print(e)
        input("Pressez une touche pour quitter")
        sys.exit(1)

    print ('--------------------------------------------------------------')
    print ('      Entrez (ou collez) le chemin vers le dossier Owncloud: ')
    print ('      Exemple : DC Comics/New 52/Groupe Batman/Batman')
    print ('--------------------------------------------------------------')

    # try:
    #     folder = raw_input()
    # except Exception as e:
    #     folder = input()

    try:
        print ('-------------------------------------------------------------')
        print (r'         ____                      __                __')
        print (r'        / __ \_      ______  _____/ /___  __  ______/ /')
        print (r'       / / / / | /| / / __ \/ ___/ / __ \/ / / / __  /')
        print (r'      / /_/ /| |/ |/ / / / / /__/ / /_/ / /_/ / /_/ /')
        print (r'      \____/ |__/|__/_/ /_/\___/_/\____/\__,_/\__,_/  ' +
               oc.get_version()+'')
        print ('                                              ')
        print ('-------------------------------------------------------------')
    except Exception:
        sys.exit(1)

    try:
        folder_path = '/'
        folder_name = ''
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
                    # full_path = file.get_path() + '/' + newName
                    full_path = file.get_path()
                    folder_list.append((full_path, name))
                    # print(newName)
                    print(str(i) + "-\t" + full_path)
                    i += 1
            print("==========================================================")
            print("Fichiers")
            print("..........................................................")
            for file in list_dir:
                if not file.is_dir():
                    newName = file.get_name()
                    full_path = file.get_path() + '/' + newName
                    shared = 'no'
                    if oc.is_shared(full_path):
                        shared = 'yes'
                    print(newName + '\t' + 'Partage : ' + shared)
            print("==========================================================")
            choice = input("tapez un chiffre pour naviguer dans "
                           "le dossier, "
                           "ou 'y' pour créer les liens de partage.\n")
            if choice != 'y':
                try:
                    folder_path = folder_list[int(choice)-1][0]
                    folder_name = folder_list[int(choice)-1][1]
                except IndexError:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("Mauvaise valeur")

            else:
                break

        list_dir = oc.list(folder_path)
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
