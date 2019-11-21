#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
# from tkinter import END, SEL, INSERT
from tkinter import END
import owncloud
from pathlib import Path
from owncloud import HTTPResponseError
from six.moves.urllib import parse

user = "User"
password = "password"
server = "http://server.io"

API_PATH = "ocs/v1.php/apps/files_sharing/api/v1"


def total_size(list_):
    return sum([i["size"] for i in list_])


class OcExplorer(tk.Tk):

    def __init__(self, master=None):
        tk.Tk.__init__(self, master)
        # self.racine = master

        self.withdraw()

        self.folder_path = "/"
        self.previous_folder_path = []
        self.folder_name = ""

        self.folder_list = []
        self.file_list = []

        self.directory = Path.home()
        # print(self.directory)

        self.oc = owncloud.Client(server)
        self._login()

        self.title("Dossiers Ownloud")

        self.place_widgets()

        self._populate_list()

        self._alt_center(0)
        self.deiconify()

    def place_widgets(self):
        self.frame = tk.Frame(self)
        self.lb = tk.Listbox(self.frame, width=60, height=8,
                             font=("Helvetica", 12))
        self.frame.pack(fill="both", expand=1, padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical")
        self.scrollbar.config(command=self.lb.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.lb.config(yscrollcommand=self.scrollbar.set)

        self.lb.pack(side="left", fill="both", expand=1)

        # Frame for files :
        self.frame2 = tk.Frame(self)
        self.lb2 = tk.Listbox(self.frame2, width=60, height=8,
                              font=("Helvetica", 12))
        self.frame2.pack(fill="both", expand=1, padx=10)

        self.scrollbar2 = tk.Scrollbar(self.frame2, orient="vertical")
        self.scrollbar2.config(command=self.lb2.yview)
        self.scrollbar2.pack(side="right", fill="y")

        self.lb2.config(yscrollcommand=self.scrollbar2.set)

        self.lb2.pack(side="left", fill="both", expand=1)

        # Buttons
        self.bottom_bar = tk.Frame(self)
        self.bottom_bar.pack(side='bottom')
        self.b1 = tk.Button(self.bottom_bar, text="Précédent",
                            command=self._up,
                            bd=0, font=("Helvetica", 12, "bold"),
                            width=14, height=2)  # noqa:E501
        self.b2 = tk.Button(self.bottom_bar, text="Ajouter le chemin",
                            command=self._select,
                            bd=0, font=("Helvetica", 12, "bold"),
                            width=14, height=2)
        self.b3 = tk.Button(self.bottom_bar, text="Télécharger",
                            command=self._download_all,
                            bd=0, font=("Helvetica", 12, "bold"),
                            width=14, height=2)

        self.b1.pack(side="left", padx=30)
        # self.b2.pack(side="left", padx=30)
        self.b3.pack(side="left", padx=30)

        self.lb.bind('<Double-Button-1>', self.double_click)

        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        mode="determinate")
        self.progress.pack(fill='x', padx=10, pady=(10, 0))

        self.total_var = tk.IntVar(value=0)
        self.progress2 = ttk.Progressbar(self, orient="horizontal",
                                         mode="determinate",
                                         variable=self.total_var)
        self.progress2.pack(fill='x', padx=10, pady=(10, 0))

    def double_click(self, event):
        widget = event.widget
        selection = widget.curselection()
        index = selection[0]
        # value = widget.get(selection[0])
        # print("selection:", selection, ": '%s'" % value)
        self.previous_folder_path.append(self.folder_path)
        self.folder_path = self.folder_list[index]["path"]

        print(self.folder_path)
        self.folder_list = []
        self.lb.delete(0, tk.END)

        self.file_list = []
        self.lb2.delete(0, tk.END)

        # print('double mouse click event')
        self._populate_list()

    def _login(self):
        self.oc.login(user, password)
        print("Logged in !")

    def _up(self):
        self.folder_list = []
        self.lb.delete(0, tk.END)

        self.file_list = []
        self.lb2.delete(0, tk.END)

        try:
            self.folder_path = self.previous_folder_path.pop()
        except IndexError:
            pass
        self._populate_list()

    def _select(self):
        try:
            sel = self.lb.curselection()[0]
            s = self.folder_list[sel]["path"]
        except IndexError:
            s = self.folder_path

        # print(f"Cloud dir = {self.cloud_dir}")
        self.master.new_dir = s[1:] if s.startswith("/") else s
        # self.master.destroy()
        self.destroy()

    def _download_all(self):
        self.directory = filedialog.askdirectory(initialdir=Path.home(),
                                                 title='Please select a directory')  # noqa:E501
        self.progress["value"] = 0
        self.progress2["maximum"] = total_size(self.file_list)
        print(f"Total size is : {total_size(self.file_list)}")
        for i in self.file_list:
            print(i["name"], i["path"], i["size"])
            # self.oc.get_file(i["path"])
            self.progress["value"] = 0
            self.progress["maximum"] = i["size"]
            local_file = os.path.join(self.directory,
                                      os.path.basename(i["path"]))
            self._get_file(i["path"], local_file)

    # This code comes from pyocclient
    # https://github.com/owncloud/pyocclient
    # and has been modified to implement progressbar
    def _get_file(self, remote_path, local_file=None):
        """Downloads a remote file

        :param remote_path: path to the remote file
        :param local_file: optional path to the local file. If none specified,
            the file will be downloaded into the current directory
        :returns: True if the operation succeeded, False otherwise
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        remote_path = owncloud.Client._normalize_path(remote_path)
        res = self.oc._session.get(
            self.oc._webdav_url + parse.quote(
                self.oc._encode_string(remote_path)),
            stream=True
        )
        if res.status_code == 200:
            if local_file is None:
                # use downloaded file name from Content-Disposition
                # local_file = res.headers['content-disposition']
                local_file = os.path.basename(remote_path)

            file_handle = open(local_file, 'wb', 8192)
            for index, chunk in enumerate(res.iter_content(8192), 1):
                file_handle.write(chunk)
                self.progress["value"] = index * 8192
                self.total_var.set(self.total_var.get() + 8192)
                self.update()
            file_handle.close()
            return True
        elif res.status_code >= 400:
            raise HTTPResponseError(res)
        return False

    def _populate_list(self):
        list_dir = self.oc.list(self.folder_path, depth=1)
        for item in list_dir:
            if item.is_dir():
                name = item.get_name()
                # full_path = file.get_path() + '/' + newName
                full_path = item.get_path()
                self.folder_list.append({'path': full_path, 'name': name})
            else:
                # if not file.is_dir():
                name = item.get_name()
                full_path = item.get_path() + '/' + name
                size = item.get_size()
                # full_path = file.get_path()
                print(name)
                self.file_list.append({'path': full_path,
                                       'name': name,
                                       'size': size})

        [self.lb.insert(END, item["name"]) for item in self.folder_list]
        [self.lb2.insert(END, item["name"]) for item in self.file_list]

    def _alt_center(self, pad):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + pad
        y = (self.winfo_screenheight() // 2) - (height // 2) + pad
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))


# MAIN PROGRAM here :
app = OcExplorer()
app.mainloop()
