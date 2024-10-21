import sqlite3
import tkinter as tk
from tkinter import ttk
import os

PWD = os.getcwd()

class Base:
    def __init__(self):
        self.nom_db = "mdp"
        self.db_path = os.path.join(PWD, self.nom_db + ".db")

        self.connecter()
        self.cursor.execute("""create table if not exists MDP(
    id integer primary key autoincrement unique,
    title text,
    username text,
    password text,
    url text
    )
    """)

    def connecter(self) -> None:
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()
        self.db.commit()

    def deconnecter(self) -> None:
        self.db.close()

    def ajouter_mdp(self, title: str, username: str, password: str, url: str) -> None:
        print(title, username, password, url)
        self.cursor.execute("""insert into MDP(title, username, password, url) values(?, ?, ?, ?)""", (title, username, password, url))
        print(6)
        self.db.commit()
        print(7)

    def supprimer_mdp_titre(self, title: str) -> None:
        self.cursor.execute("""delete from MDP where title = ?""", (title, ))
        self.db.commit()

    def rechercher_titre(self, title: str) -> tuple:
        self.cursor.execute("""select * from MDP where title = ?""", (title, ))
        return self.cursor.fetchall()

    def rechercher_username(self, username: str) -> tuple:
        self.cursor.execute("""select * from MDP where username = ?""", (username, ))
        return self.cursor.fetchall()

    def rechercher_url(self, url: str) -> tuple:
        self.cursor.execute("""select * from MDP where url = ?""", (url, ))
        return self.cursor.fetchall()

    def afficher_tout(self) -> list:
        self.cursor.execute("""select * from MDP order by title""")
        return self.cursor.fetchall()

class Main:
    def __init__(self):
        # Initialisation de la base de mdp
        self.db = Base()

        # Initialisation de la fenêtre
        self.root = tk.Tk()
        self.root.title("Gestionnaire de Mots De Passe 2000")

        self.root.geometry("300x200")

        s = ttk.Style()
        s.configure('red.TFrame', background='#FF0000')
        s.configure('green.TFrame', background='#00FF00')
        s.configure('blue.TFrame', background='#0000FF')



        self.toolbar_frame = ttk.Frame(self.root, style="red.TFrame")
        self.password_list_frame = ttk.Frame(self.root, style="green.TFrame")
        self.password_info_frame = ttk.Frame(self.root, style="blue.TFrame")

        self.toolbar_frame.pack(side="top", fill="x")
        self.password_list_frame.pack(fill="both", expand=True, side="left")
        self.password_info_frame.pack(fill="both", expand=True, side="right")

        self.add_password_button = ttk.Button(self.toolbar_frame, text="Ajouter MDP", command=self.add_password_popup)
        self.add_password_button.pack(side="left",padx=2, pady=2)

        self.root.mainloop()

    def add_password_save(self):
        self.db.ajouter_mdp(self.password_title_var.get(), self.password_username_var.get(), self.password_password_var.get(), self.password_url_var.get())
        self.popup.destroy()

    def add_password_popup(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Ajouter un MDP")

        # Titre
        self.password_title_label = ttk.Label(self.popup, text="Titre")
        self.password_title_var = tk.StringVar()
        self.password_title_entry = ttk.Entry(self.popup, textvariable=self.password_title_var)

        # Username
        self.password_username_label = ttk.Label(self.popup, text="Username")
        self.password_username_var = tk.StringVar()
        self.password_username_entry = ttk.Entry(self.popup, textvariable=self.password_username_var)

        # Password
        self.password_password_label = ttk.Label(self.popup, text="Password")
        self.password_password_var = tk.StringVar()
        self.password_password_entry = ttk.Entry(self.popup, textvariable=self.password_password_var)

        # URL
        self.password_url_label = ttk.Label(self.popup, text="URL")
        self.password_url_var = tk.StringVar()
        self.password_url_entry = ttk.Entry(self.popup, textvariable=self.password_url_var)

        # Buttons
        self.password_cancel_button = ...
        self.password_save_button = ttk.Button(self.popup, text="Enregistrer", command=self.add_password_save)


        self.password_title_label.grid(row=0, column=0, padx=2, pady=5)
        self.password_title_entry.grid(row=0, column=1, padx=2, pady=5)

        self.password_username_label.grid(row=1, column=0, padx=2, pady=5)
        self.password_username_entry.grid(row=1, column=1, padx=2, pady=5)

        self.password_password_label.grid(row=2, column=0, padx=2, pady=5)
        self.password_password_entry.grid(row=2, column=1, padx=2, pady=5)

        self.password_url_label.grid(row=3, column=0, padx=2, pady=5)
        self.password_url_entry.grid(row=3, column=1, padx=2, pady=5)

        self.password_save_button.grid(row=4, column=0, padx=20, pady=5)


main = Main()

db = Base()
print(db.afficher_tout())












