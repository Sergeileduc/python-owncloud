#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import configparser
import owncloud  # pip install pyocclient

from urllib.error import HTTPError
import requests.exceptions
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

cfg = Settings('owncloud.cfg')
if cfg.load(cfg_forum, cfg_opts):
    # oc = owncloud.Client('http://dl.dctrad.fr')
    oc = owncloud.Client(cfg.host)

    print('--------------------------------------------------------------')
    print('     Loged in Owncloud ')
    print('--------------------------------------------------------------')
    print('Le script vous permet d\'uploader le CONTENU d\'un dossier local \n'
          'vers un dossier du Owncloud existant, pour le mettre à jour\n')
    print('Par exemple, vous pouvez uploader le CONTENU '
          '(avec toute l\'arborescence) d\'un dossier :\n'
          '"Groupe Superman (nouvelle version)"\n'
          'vers le dossier :\nOwncloud "Groupe Superman"')

    print('--------------------------------------------------------------')
    print('      Choix du dossier LOCAL dont le contenu sera uploadé')
    print('      Exemple : "./TODO/Groupe Superman Perso"')
    print('--------------------------------------------------------------')

    dir = os.getcwd()
    dir = os.path.normpath(dir)
    if os.path.exists(dir):
        print("yay")
        print(dir)
    while True:
        dir = os.path.normpath(dir)
        local_dirs = [d for d in os.listdir(dir)]
        i = 1
        for ld in local_dirs:
            # print(str(i) + "-\t" + ld)
            print('{:.<5d}{:<s}'.format(i, ld))
            i += 1

        choice = input("tapez un chiffre pour naviguer dans "
                       "le dossier, ou 'y' pour valider.\n")
        if choice != 'y':
            try:
                dir_name = local_dirs[int(choice)-1]
                dir = os.path.join(dir, dir_name)
                if os.path.exists(dir):
                    print("yay")
                    print(dir)
                else:
                    print(dir + " doesn't exist")
                    dir = os.getcwd()
            except IndexError:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("Mauvaise valeur")
        else:
            break

    local_dir = dir
    print("Dossier local : " + local_dir)

    try:
        oc.login(cfg.username, cfg.password)
    except requests.exceptions.MissingSchema:
        print("Erreur.\n"
              "Veuillez configurer owncloud.cfg avec une url correcte")
    except owncloud.owncloud.HTTPResponseError:
        print("Erreur.\n"
              " Veuillez configurer owncloud.cfg "
              "avec utilisateur et mot de passe valide")
        # print(e)
        sys.exit(1)

    print('--------------------------------------------------------------')
    print('      Choix du dossier Owncloud de destination: ')
    print('      Exemple : DC Comics/New 52/Groupe Superman')
    print('--------------------------------------------------------------')

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
                    # print(str(i) + "-\t" + full_path)
                    print('{:.<5d}{:<s}'.format(i, full_path))
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
                           "le dossier, ou 'y' pour valider.\n")
            if choice != 'y':
                try:
                    folder_path = folder_list[int(choice)-1][0]
                    folder_name = folder_list[int(choice)-1][1]
                except IndexError:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("Mauvaise valeur")

            else:
                break

        print("Dossier distant : " + folder_path)

        print('-------------------------------------------------------------')
        print('Vous allez uploader le contenu de :')
        print('\t' + local_dir)
        print('dans le dossier Owncloud :')
        print('\t' + folder_path)
        print('-------------------------------------------------------------')

        choice = input("Voulez-vous continuer (y/n) ?\n")
        if choice != 'y':
            sys.exit(1)

        # UPLOAD recap
        print('--------------------------------------------------------------')
        print('RECAPITULATIF')
        print('--------------------------------------------------------------')
        for root, dirs, files in os.walk(local_dir, topdown=True):
            for name in files:
                file_l_path = os.path.join(root, name)
                file_rel_path = os.path.relpath(file_l_path, start=local_dir)
                norm_path = os.path.normpath(file_rel_path)
                remote_path = \
                    os.path.join(folder_path, norm_path).replace('\\', '/')
                print("up : " + file_l_path + " in \t\t\t" + remote_path)

        choice = input("Voulez-vous continuer (y/n) ?\n")
        if choice != 'y':
            sys.exit(1)

        # UPLOAD real deal
        for root, dirs, files in os.walk(local_dir, topdown=True):
            for name in files:
                file_l_path = os.path.join(root, name)
                file_rel_path = os.path.relpath(file_l_path, start=local_dir)
                norm_path = os.path.normpath(file_rel_path)
                remote_path = \
                    os.path.join(folder_path, norm_path).replace('\\', '/')
                print("up : " + file_l_path + " in \t\t\t" + remote_path)

                try:
                    oc.put_file(remote_path, file_l_path)
                except Exception as e:
                    print(e)

    except HTTPError as e:
        print(e.code)
    except owncloud.owncloud.HTTPResponseError:
        print("Dossier non valide")

    input("Pressez une touche pour quitter")
