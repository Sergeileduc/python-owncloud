#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import configparser
import owncloud  # pip install pyocclient
from urllib.error import HTTPError
import importlib
import requests.exceptions
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
            print(f'The section "{section}" does not exist')
        except configparser.NoOptionError:
            print(f'The value for "{key}" is missing')
        else:
            return True
        return False


cfg_forum = 'dctrad'

cfg_opts = ['host',
            'username',
            'password'
            ]


cfg = Settings('.owncloud.cfg')
if cfg.load(cfg_forum, cfg_opts):
    oc = owncloud.Client(cfg.host)
    try:
        oc.login(cfg.username, cfg.password)
    except requests.exceptions.MissingSchema:
        print("Erreur.")
        print("Veuillez configurer owncloud.cfg avec une url correcte")
    except owncloud.owncloud.HTTPResponseError:
        print("Erreur.")
        print(" Veuillez configurer owncloud.cfg "
              "avec utilisateur et mot de passe valide")
        # print(e)
        sys.exit(1)

    print('--------------------------------------------------------------')
    print('     Loged in Owncloud ')
    print('--------------------------------------------------------------')

    try:
        folder_path = '/'
        previous_folder_path = []
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
                    folder_list.append({'path': full_path, 'name': name})
                    print(f'{i:.<5d}{full_path:<s}')
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
            choice = input("Entrez un choix :\n"
                           "- un nombre pour naviguer dans un dossier\n"
                           "- 'u' pour remonter dans le dossier précédent\n"
                           "- 'd' pour télécharger le contenu.\n")
            if choice != 'd' and choice != 'u':
                try:
                    previous_folder_path.append(folder_path)
                    folder_path = folder_list[int(choice)-1]['path']
                    folder_name = folder_list[int(choice)-1]['name']
                except IndexError:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("Mauvaise valeur")
                except ValueError:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("Mauvaise valeur")

            elif choice == 'u':
                try:
                    folder_path = previous_folder_path.pop()
                except IndexError:
                    folder_path = '/'
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
                except OSError:
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
                        print(f"Download : {full_path}")
                        oc.get_file(full_path)
                    os.chdir(previous_dir)
                except Exception as e:
                    print(e)

    except HTTPError as e:
        print(e.code)
    except owncloud.owncloud.HTTPResponseError:
        print("Dossier non valide")

    input("Pressez une touche pour quitter\n")
