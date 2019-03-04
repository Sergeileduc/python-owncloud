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
    print ('     Loged in Owncloud ')
    print ('--------------------------------------------------------------')

    # try:
    #     folder = raw_input()
    # except Exception as e:
    #     folder = input()

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
                    # full_path = file.get_path()
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
            os.chdir(folder_name)
        except OSError as e:
            print(e)
            print("mkdir error")
            pass

        list_dir = oc.list(folder_path, depth=15)
        for file in list_dir:
            if not file.is_dir():
                previous_dir = os.getcwd()
                newName = file.get_name()
                path = file.get_path()
                full_path = path + '/' + newName
                base_path = folder_path + '/'
                rel_path = path.replace(base_path, '')

                try:
                    if rel_path != path and not os.path.exists(rel_path):
                        os.makedirs(rel_path)
                except OSError as e:
                    # print(e)
                    # print("mkdir error")
                    pass
                try:
                    if rel_path != path:
                        os.chdir(rel_path)
                except OSError as e:
                    print(e)
                try:
                    if newName != ".DS_Store":
                        print("Download : " + full_path)
                        oc.get_file(full_path)
                    os.chdir(previous_dir)
                except Exception as e:
                    print(e)
                # try:
                #     os.mkdir(full_path)
                # except OSError:
                #     pass
                # oc.get_file(full_path)

    except HTTPError as e:
        print(e.code)
    except owncloud.owncloud.HTTPResponseError as e:
        print("Dossier non valide")

    input("Pressez une touche pour quitter\n")
