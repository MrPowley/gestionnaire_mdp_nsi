import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno, showerror
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter.simpledialog import askstring
import os
import cryptocode
import hashlib
import webbrowser
import threading
# from profilehooks import profile

# Chemin d'accès du dossier parent
PWD = os.getcwd()

# Fonction pour calculer le SHA-256 d'une chaine de caractère


def hash_string(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

# Classe de la base de mdp


class Base:
    def __init__(self, db_path):
        self.db_path = db_path

        self.connecter()
        # Création de la table de mdp
        self.cursor.execute("""create table if not exists MDP(
    id integer primary key autoincrement unique,
    hash text)
    """)
        # Création de la table du mdp maitre
        self.cursor.execute("""create table if not exists Maitre(
    id integer primary key autoincrement unique,
    password_hash text
    )
    """)

    # Fonction pour se connecter à la base et initialiser le curseur
    def connecter(self) -> None:
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()
        self.db.commit()

    # Fonction pour se déconnecter de la base (Pas utilisée)
    def deconnecter(self) -> None:
        self.db.close()

    # Fonction pour ajouter un mdp à la base
    def ajouter_mdp(self, id, hash: str) -> None:
        self.cursor.execute(
            """insert into MDP(id, hash) values(?, ?)""", (id, hash))
        self.db.commit()

    # Fonction pour suprimer un mdp par son ID
    def supprimer_mdp_id(self, id: int) -> None:
        self.cursor.execute("""delete from MDP where id = ?""", (id, ))
        self.db.commit()

    # Fonction pour lister tout les mdp
    def afficher_tout(self) -> list:
        self.cursor.execute("""select * from MDP order by id""")
        self.db.commit()
        return self.cursor.fetchall()

    # Fonction pour récuperer le hash du mdp maitre
    def afficher_hash_mdp_maitre(self):
        self.cursor.execute("""select * from Maitre""")
        self.db.commit()
        return self.cursor.fetchone()

    # Fonction pour choisir le mdp maitre
    def choisir_mdp_maitre(self, hash):
        self.cursor.execute(
            """insert into Maitre(password_hash) values(?)""", (hash,))
        self.db.commit()

    # Fonction pour modififier un mdp déjà dans la base
    def changer_mdp(self, id: int, hash: str):
        self.cursor.execute(
            """update MDP set hash = ? where id = ?""", (hash, id))
        self.db.commit()

    def get_id_of_last_password(self) -> int:
        self.cursor.execute(
            """select id from MDP order by id desc"""
        )
        self.db.commit()
        if not (last_id := self.cursor.fetchone()):  # [0] car sqlite renvoie un tuple
            last_id = (0,)
        return last_id[0]


# Classe du programme principal/interface
# TODO Séparer interface et logique
class Main:
    def __init__(self):
        # On accèpte uniquement les .db ou alors tout les types de fichiers, au cas ou
        self.filetypes = (
            ('Database file', '*.db'),
            ('All files', '*.*')
        )

        # Affiche une fenêtre pour choisir un base
        self.choose_db()

    # Fonction pour afficher une fenêtre de choix
    def choose_db(self):
        # Création de la fenêtre
        self.database_popup = tk.Tk()
        self.database_popup.title("Choisir une base")

        self.popup_label = tk.Label(
            self.database_popup, text="Que voulez vous faire ?", font=("Segoe UI", 16))
        # On utilise un columnspan plus large car sinon le texte ne serai pas centré par rapport aux boutons
        self.popup_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.database_open_button = ttk.Button(
            self.database_popup, text="Ouvrir une base", command=self.open_db)
        self.database_open_button.grid(row=1, column=0, padx=10, pady=10)

        self.database_create_button = ttk.Button(
            self.database_popup, text="Créer une base", command=self.create_db)
        self.database_create_button.grid(row=1, column=2, padx=10, pady=10)

        self.database_popup.mainloop()

    # Fonction d'initialisation de la base
    def init_base(self, db_path):
        self.db = Base(db_path=db_path)

    def open_db(self):

        db_path = askopenfilename(
            title='Ouvrir une base', initialdir=PWD, filetypes=self.filetypes)

        if not db_path:
            return

        master_password = askstring(
            title="Base de mots de passe",
            prompt="Veuillez entrer le MDP Maitre",
            initialvalue="",
            show="*")

        if not master_password:
            return

        self.master_password_hash = hash_string(master_password)

        self.init_base(db_path)

        if self.master_password_hash != self.db.afficher_hash_mdp_maitre()[1]:
            showerror("MDP", "Mauvais mot de passe Maitre")
            return

        self.database_popup.destroy()
        self.main_menu()
        return

    # Fonction pour créer une base (Quasiment la même chose que pour ouvrir)

    def create_db(self):

        db_path = asksaveasfile(title='Créer une base', initialdir=PWD,
                                filetypes=self.filetypes, defaultextension=self.filetypes).name

        self.init_base(db_path)

        # On demande 2 fois le mdp pour avoir une confirmation
        master_password_hash_1 = hash_string(askstring(
            title="Base", prompt="Veuillez entrer un nouveau MDP Maitre", show="*"))
        master_password_hash_2 = hash_string(askstring(
            title="Base de mots de passe", prompt="Veuillez confirmer le MDP Maitre", show="*"))

        if master_password_hash_1 != master_password_hash_2:
            showerror("MDP", "Les 2 mots de passe ne correspondent pas")
            return

        # On enregistre le mdp maitre dans la base et on affiche le menu principal
        self.master_password_hash = master_password_hash_1
        self.db.choisir_mdp_maitre(self.master_password_hash)

        self.database_popup.destroy()
        self.main_menu()
        return

    # Fonction de la fenêtre principale
    def main_menu(self):
        # la fonction pourra être appelée plusieurs fois au cours du code, donc on s'assure de la supprimer avant de la ré-afficher
        try:
            self.root.destroy()
        except AttributeError:
            pass

        # Initialisation de la fenêtre
        self.root = tk.Tk()
        self.root.title("Gestionnaire de Mots De Passe 3000")
        self.root.geometry("550x300")

        # Configuration d'un style pour changer une couleur
        s = ttk.Style()
        s.configure('toolbar.TFrame', background='#d3d3d3')

        # Barre d'outil
        self.toolbar_frame = ttk.Frame(self.root, style="toolbar.TFrame")
        self.toolbar_frame.pack(side="top", fill="x")

        self.draw_treeview()

        self.scrollbar.configure(command=self.password_treeview.yview)

        self.password_info_frame = ttk.Frame(
            self.root)  # , style="blue.TFrame"

        # Affichage des zones

        self.password_info_frame.pack(
            fill="both", side="right")  # expand=True,

        # Barre d'outils
        self.add_password_button = ttk.Button(
            self.toolbar_frame, text="Ajouter MDP", command=self.add_password_popup)
        self.add_password_button.pack(side="left", padx=2, pady=2)

        self.choose_db_button = ttk.Button(
            self.toolbar_frame, text="Choisir la base", command=self.choose_db)
        self.choose_db_button.pack(side="left", padx=2, pady=2)

        # Barre de recherche et menu
        self.filtres = ["Id", "Titre", "Utilisateur", "MDP", "URL", "Tout"]
        self.filter_value = tk.StringVar(self.toolbar_frame)
        self.filter_value.set("Titre")
        self.filtre_recherche = ttk.OptionMenu(
            self.toolbar_frame, self.filter_value, "Titre", *self.filtres)
        self.filtre_recherche.pack(side="left", padx=2, pady=2)

        self.barre_recherche = ttk.Entry(self.toolbar_frame)
        self.barre_recherche.pack(side="left", padx=2, pady=2)
        self.barre_recherche.bind("<Return>", self.fill_treeview)

        # On décode les mots de passe tout de suite
        self.get_passwords()

        # On affiche les mdp dans la zone
        self.fill_treeview()
        self.root.mainloop()

    def draw_treeview(self):
        # On créé toute la partie gauche de l'interface, à savoir le treeview, la scrollbar, dans une frame adaptée
        self.password_treeview_frame = ttk.Frame(self.root)
        self.scrollbar = ttk.Scrollbar(self.password_treeview_frame)

        # Le style est pour enlever la bordure
        self.style = ttk.Style()
        self.style.layout(
            'Edge.Treeview',
            [('Edge.Treeview.treearea', {'sticky': 'nsew'})],
        )
        self.style.configure('Edge.Treeview', highlightthickness=0, bd=0)

        self.password_treeview = ttk.Treeview(
            self.password_treeview_frame, yscrollcommand=self.scrollbar.set, show="tree", style='Edge.Treeview')

        # On utilise des tags sur les éléments du treeview pour les couleurs
        self.password_treeview.tag_configure(
            "lignepair", background="lightgray")
        self.password_treeview.tag_configure("ligneimpair", background="white")

        self.password_treeview_frame.pack(
            fill="both", expand=True, side="left")
        self.password_treeview.pack(fill="both", expand=True, side="left")
        self.scrollbar.pack(side="right", fill="y")

        # Au relachement du clic gauche
        self.password_treeview.bind(
            "<ButtonRelease-1>", self.show_password_infos)

    # Fonction pour maj la liste de mdp
    # @profile
    def fill_treeview(self, e=None):

        filter = self.filter_value.get()
        if filter == "Id":
            filter = 0
        elif filter == "Titre":
            filter = 1
        elif filter == "Utilisateur":
            filter = 2
        elif filter == "MDP":
            filter = 3
        elif filter == "URL":
            filter = 4
        elif filter == "Tout":
            filter = None

        self.filtered_passwords = []

        self.password_treeview.delete(*self.password_treeview.get_children())

        for password in self.password_list:
            recherche = self.barre_recherche.get().lower()

            if not recherche:
                self.filtered_passwords.append(password)
                self.add_password_to_list(password)
            else:
                if filter is not None:
                    if recherche in str(password[filter]).lower():
                        self.filtered_passwords.append(password)
                        self.add_password_to_list(password)
                else:
                    if any(recherche in str(item).lower() for item in password):
                        self.filtered_passwords.append(password)
                        self.add_password_to_list(password)

    def decode_password(self, encoded_password):
        id = encoded_password[0]
        decoded_password_list = cryptocode.decrypt(
            encoded_password[1], self.master_password_hash).split("%")[:-1]
        return [id] + decoded_password_list

    def encode_password(self, decoded_password, id=None):
        password = ""
        for item in decoded_password:
            password += str(item) + "%"
        password = [id] + \
            [cryptocode.encrypt(password, self.master_password_hash)]
        return password

    def color_password(self, index):
        if index % 2 == 0:
            return "lignepair"
        else:
            return "ligneimpair"

    def re_color_password_list(self):
        for i, password in enumerate(self.password_treeview.get_children()):
            tag = self.color_password(i+1)
            self.password_treeview.item(password, tag=tag)

    def add_password_to_list(self, password):

        password_number = len(self.password_treeview.get_children()) + 1
        tag = self.color_password(password_number)

        self.password = password
        # On créé un bouton qui seriva a afficher les infos du mdp
        self.password_treeview.insert(
            "", "end", text=password[1], tag=tag, values=password)

    def remove_password_from_list(self):

        password = self.password_treeview.selection()[0]
        self.password_treeview.delete(password)
        self.re_color_password_list()

    def edit_password_in_list(self, password):
        selection = self.password_treeview.selection()[0]
        self.password_treeview.item(
            selection, text=password[1], values=password)

    def get_passwords(self):
        passwords = self.db.afficher_tout()
        self.password_list = []

        def decoder():
            for password in passwords:
                decoded = self.decode_password(password)
                self.password_list.append(decoded)
                self.add_password_to_list(decoded)

        threading.Thread(target=decoder, daemon=True).start()

    def add_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        return

    def open_url(self, url):
        webbrowser.open(url)

    # Fonction pour afficher les infos d'un mdp
    def show_password_infos(self, e=None):

        current_password = self.password_treeview.focus()
        password = self.password_treeview.item(current_password)["values"]
        if not password:
            return

        # On supprime l'ancienne pour afficher les nouvelles infos
        self.password_info_frame.destroy()
        self.password_info_frame = ttk.Frame(
            self.root)  # , style="blue.TFrame"
        self.password_info_frame.pack(
            fill="both", side="right")  # expand=True,

        # Affiche Un texte et une zone de texte associée qui contiendra la valeur du mdp
        self.password_info_title_label = ttk.Label(
            self.password_info_frame, text="Titre : ")
        self.password_info_title_label.grid(row=0, column=0, padx=5, pady=5)

        self.password_info_title_entry = ttk.Entry(self.password_info_frame,)
        self.password_info_title_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_info_title_entry.insert(0, password[1])

        self.password_info_username_label = ttk.Label(
            self.password_info_frame, text="Nom d'Utilisateur : ")
        self.password_info_username_label.grid(row=1, column=0, padx=5, pady=5)

        self.password_info_username_entry = ttk.Entry(self.password_info_frame)
        self.password_info_username_entry.grid(row=1, column=1, padx=5, pady=5)
        self.password_info_username_entry.insert(0, password[2])

        self.username_copy_button = ttk.Button(
            self.password_info_frame, text="Copier", command=lambda: self.add_to_clipboard(password[2]))
        self.username_copy_button.grid(row=1, column=2, padx=5, pady=5)

        self.password_info_password_label = ttk.Label(
            self.password_info_frame, text="Mot De Passe : ")
        self.password_info_password_label.grid(row=2, column=0, padx=5, pady=5)

        self.password_info_password_entry = ttk.Entry(self.password_info_frame)
        self.password_info_password_entry.grid(row=2, column=1, padx=5, pady=5)
        self.password_info_password_entry.insert(0, password[3])

        self.password_copy_button = ttk.Button(
            self.password_info_frame, text="Copier", command=lambda: self.add_to_clipboard(password[3]))
        self.password_copy_button.grid(row=2, column=2, padx=5, pady=5)

        self.password_info_url_label = ttk.Label(
            self.password_info_frame, text="URL : ")
        self.password_info_url_label.grid(row=3, column=0, padx=5, pady=5)

        self.password_info_url_entry = ttk.Entry(self.password_info_frame)
        self.password_info_url_entry.grid(row=3, column=1, padx=5, pady=5)
        self.password_info_url_entry.insert(0, password[4])

        self.url_copy_button = ttk.Button(
            self.password_info_frame, text="Ouvrir", command=lambda: self.open_url(password[4]))
        self.url_copy_button.grid(row=3, column=2, padx=5, pady=5)

        # Boutons pour enregistrer les modifications
        self.password_info_save_button = ttk.Button(
            self.password_info_frame, text="Sauvegarder", command=lambda password=password: self.update_password_info(password))
        self.password_info_save_button.grid(row=4, column=0, padx=10, pady=10)
        # Bouton pour supprimer le mdp
        self.password_info_delete_button = ttk.Button(
            self.password_info_frame, text="Supprimer", command=lambda password=password: self.delete_password(password))
        self.password_info_delete_button.grid(
            row=4, column=1, padx=10, pady=10)

    # Fonctions pour maj les infos d'un mdp dans la base
    def update_password_info(self, password):
        id = password[0]
        password = [self.password_info_title_entry.get(), self.password_info_username_entry.get(
        ), self.password_info_password_entry.get(), self.password_info_url_entry.get()]
        encoded_password = self.encode_password(password, id)
        # Change les infos du mdp en utilisant son id
        self.db.changer_mdp(encoded_password[0], encoded_password[1])
        self.edit_password_in_list([id] + password)

    # Fontion pour supprimer un mdp
    def delete_password(self, password):
        # Affiche un avertissement
        reponse = askyesno(
            "Supprimer", "Êtes vous sur de vouloir supprimer le mot de passe ?")
        if reponse:
            # Supprime le mdp et maj la liste
            self.db.supprimer_mdp_id(password[0])
            self.remove_password_from_list()
            self.re_color_password_list()

    # Affiche une fenêtre pour ajouter un mdp

    def add_password_popup(self):
        # On utilise TopLevel car sa créé une fenêtre enfant, au premier plan
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Ajouter un Mot De Passe")
        self.popup.bind("<Return>", self.add_password_save)

        # Titre
        self.password_title_label = ttk.Label(self.popup, text="Titre")
        self.password_title_entry = ttk.Entry(self.popup)
        self.password_title_entry.focus_set()

        # Nom d'utilisateur
        self.password_username_label = ttk.Label(self.popup, text="Nom d'Utilisateur")
        self.password_username_entry = ttk.Entry(self.popup)

        # MDP
        self.password_password_label = ttk.Label(self.popup, text="Mot De Passe")
        self.password_password_entry = ttk.Entry(self.popup, show="*")

        # URL
        self.password_url_label = ttk.Label(self.popup, text="URL")
        self.password_url_entry = ttk.Entry(self.popup)

        # Buttons
        self.password_save_button = ttk.Button(
            self.popup, text="Enregistrer", command=self.add_password_save)

        # Affichage des widgets
        self.password_title_label.grid(row=0, column=0, padx=2, pady=5)
        self.password_title_entry.grid(row=0, column=1, padx=2, pady=5)

        self.password_username_label.grid(row=1, column=0, padx=2, pady=5)
        self.password_username_entry.grid(row=1, column=1, padx=2, pady=5)

        self.password_password_label.grid(row=2, column=0, padx=2, pady=5)
        self.password_password_entry.grid(row=2, column=1, padx=2, pady=5)

        self.password_url_label.grid(row=3, column=0, padx=2, pady=5)
        self.password_url_entry.grid(row=3, column=1, padx=2, pady=5)

        self.password_save_button.grid(row=4, column=0, padx=20, pady=5)

    # Fonction pour enregistrer le mdp entré
    def add_password_save(self, _=None):
        # Récupère et encode les infos du mdp
        password_title = self.password_title_entry.get()
        password_username = self.password_username_entry.get()
        password_password = self.password_password_entry.get()
        password_url = self.password_url_entry.get()
        # Pour éviter de réassigner un id déjà utilisé, si on supprime un mdp
        password_id = self.db.get_id_of_last_password() + 1

        decoded_password = [password_id, password_title,
                            password_username, password_password, password_url]
        for item in decoded_password[1:-1]:
            if not item:
                self.popup.focus()
                return showerror("MDP", "Vous devez remplir les champs obligatoires (Titre, Nom d'Utilisateur, Mot De Passe)"), self.popup.focus()

        encoded_password = self.encode_password(
            decoded_password[1:], decoded_password[0])
        self.db.ajouter_mdp(encoded_password[0], encoded_password[1])

        self.popup.destroy()
        # Ajout au treeview
        self.password_list.append(decoded_password)
        self.add_password_to_list(decoded_password)


main = Main()
