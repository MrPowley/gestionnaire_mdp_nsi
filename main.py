import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno, showerror
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter.simpledialog import askstring
import os
import cryptocode
import hashlib
from profilehooks import profile

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
    title text,
    username text,
    password text,
    url text
    )
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
    def ajouter_mdp(self, title: str, username: str, password: str, url: str) -> None:
        self.cursor.execute(
            """insert into MDP(title, username, password, url) values(?, ?, ?, ?)""", (title, username, password, url))
        self.db.commit()

    # Fonction pour suprimer un mdp par son ID
    def supprimer_mdp_id(self, id: int) -> None:
        self.cursor.execute("""delete from MDP where id = ?""", (id, ))
        self.db.commit()

    # Fonction pour rechercher un mdp par son titre (Pas utilisée)
    def rechercher_titre(self, title: str) -> tuple:
        self.cursor.execute("""select * from MDP where title = ?""", (title, ))
        return self.cursor.fetchall()

    # Fonction pour rechercher un mdp par le nom d'utilisateur (Pas utilisée)
    def rechercher_username(self, username: str) -> tuple:
        self.cursor.execute(
            """select * from MDP where username = ?""", (username, ))
        return self.cursor.fetchall()

    # Fonction pour rechercher un mdp par son url (Pas utilisée)
    def rechercher_url(self, url: str) -> tuple:
        self.cursor.execute("""select * from MDP where url = ?""", (url, ))
        return self.cursor.fetchall()

    # Fonction pour lister tout les mdp
    def afficher_tout(self) -> list:
        self.cursor.execute("""select * from MDP order by title""")
        return self.cursor.fetchall()

    # Fonction pour récuperer le hash du mdp maitre
    def afficher_hash_mdp_maitre(self):
        self.cursor.execute("""select * from Maitre""")
        return self.cursor.fetchone()

    # Fonction pour choisir le mdp maitre
    def choisir_mdp_maitre(self, hash):
        self.cursor.execute(
            """insert into Maitre(password_hash) values(?)""", (hash,))
        self.db.commit()

    # Fonction pour modififier un mdp déjà dans la base
    def changer_mdp(self, id: int, title: str, username: str, password: str, url: str):
        self.cursor.execute(
            """update MDP set title = ?, username = ?, password = ?, url = ? where id = ?""", (title, username, password, url, id))
        self.db.commit()

# Classe du programme principal/interface
class Main:
    def __init__(self):
        # Affiche une fenêtre pour choisir un base
        self.choose_db_popup()

    # Fonction pour afficher une fenêtre de choix
    def choose_db_popup(self):
        # Création de la fenêtre
        self.database_popup = tk.Tk()
        self.database_popup.title("Choisir une base")

        # Titre
        self.password_title_label = ttk.Label(
            self.database_popup, text="Que voulez vous faire ?")
        self.password_title_label.grid(row=0, column=0, columnspan=4)

        # Buttons
        self.database_open_button = ttk.Button(
            self.database_popup, text="Ouvrir une base", command=self.open_db)
        self.database_open_button.grid(row=1, column=0)

        self.database_create_button = ttk.Button(
            self.database_popup, text="Créer une base", command=self.create_db)
        self.database_create_button.grid(row=1, column=1)

        self.database_popup.mainloop()

    # Fonction d'initialisation de la base
    def init_base(self, db_path=os.path.join(PWD, "mdp.db")):
        self.db = Base(db_path=db_path)

    # Fonction pour ouvrir une base
    def open_db(self):
        # définition des types de fichiers acceptés
        filetypes = (
            ('Database file', '*.db'),
            ('All files', '*.*')
        )
        # Demande d'ouvrir un fichier et on gade le chemin d'accès
        self.db_path = askopenfilename(
            title='Ouvrir une base', initialdir=PWD, filetypes=filetypes)
        # Si l'utilisateur à choisi un fichier
        if self.db_path:
            # On demande le mdp maitre et on calcule son hash
            self.master_password_hash = hash_string(askstring(
                title="Base de mots de passe", prompt="Veuillez entrer le MDP Maitre"))
            # On initialise la base avec le chemin choisi
            self.init_base(self.db_path)
            # On récupère le hash du mdp maitre de la base
            self.db_master_password = self.db.afficher_hash_mdp_maitre()[1]

            # On compar le mdp saisi et le mdp de la base
            if self.master_password_hash == self.db_master_password:
                # On retire la fenêtre et on affiche le menu principal
                self.database_popup.destroy()
                self.main_menu()
                return
            # On affiche une erreur si le mdp est mauvais
            showerror("MDP", "Mauvais mot de passe Maitre")
            return

    # Fonction pour créer une base (Quasiment la même chose que pour ouvrir)
    def create_db(self):
        filetypes = (
            ('Data Base File', '*.db'),
            ('All files', '*.*')
        )
        file = asksaveasfile(title='Créer une base', initialdir=PWD,
                             filetypes=filetypes, defaultextension=filetypes)
        if file:
            self.db_path = file.name
            self.init_base(self.db_path)

            # On demande 2 fois le mdp pour avoir une confirmation
            self.master_password_hash_1 = hash_string(askstring(
                title="Base", prompt="Veuillez entrer un nouveau MDP Maitre"))
            self.master_password_hash_2 = hash_string(askstring(
                title="Base de mots de passe", prompt="Veuillez confirmer le MDP Maitre"))

            if self.master_password_hash_1 == self.master_password_hash_2:
                # On enregistre le mdp maitre dans la base et on affiche le menu principal
                self.master_password_hash = self.master_password_hash_1
                self.db.choisir_mdp_maitre(self.master_password_hash)
                self.database_popup.destroy()
                self.main_menu()
                return

            showerror("MDP", "Les 2 mots de passe ne correspondent pas")
            return

        showerror("Base", "Vous n'avez pas choisi de fichier valide")
        print(1)
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
        self.root.title("Gestionnaire de Mots De Passe 2000")
        self.root.geometry("400x200")

        # Configuration d'un style pour changer une couleur
        s = ttk.Style()
        s.configure('toolbar.TFrame', background='#d3d3d3')

        # Barre d'outil
        self.toolbar_frame = ttk.Frame(self.root, style="toolbar.TFrame")

        # Zone de liste de mdp
        self.password_list_frame = ttk.Frame(
            self.root)  # , style="green.TFrame"
        # Canvas de liste de mdp (Le widget Canvas est l'un es 2 seuls qui permet d'être défillé)
        # on définit la scrollregion pour permettre d'afficher une barre de défilement, ou non, en fonction du nombre de mdp dans la liste
        self.password_list_canvas = tk.Canvas(self.password_list_frame, scrollregion=(0, 0, 0, len(
            self.get_passwords())*35), height=self.password_list_frame.winfo_height(), width=50)
        # Zone d'information du mdp selectionné
        self.password_info_frame = ttk.Frame(
            self.root)  # , style="blue.TFrame"

        # Affichage des zones
        self.toolbar_frame.pack(side="top", fill="x")
        self.password_list_frame.pack(fill="both", expand=True, side="left")
        self.password_list_canvas.pack(fill="both", expand=True, side="left")
        self.password_info_frame.pack(
            fill="both", side="right")  # expand=True,

        # On lie la molette au canvas pour pouvoir défiller
        self.password_list_canvas.bind(
            "<MouseWheel>", lambda e: self.password_list_canvas.yview_scroll(int(-e.delta/60), "units"))
        # Barre de défilement
        self.scrollbar = ttk.Scrollbar(
            self.password_list_canvas, orient="vertical", command=self.password_list_canvas.yview)

        self.scrollbar.bind(
            "<MouseWheel>", lambda e: self.password_list_canvas.yview_scroll(int(-e.delta/60), "units"))

        self.password_list_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")

        # Bouton de la barre d'outil pour ajouter un mdp
        self.add_password_button = ttk.Button(
            self.toolbar_frame, text="Ajouter MDP", command=self.add_password_popup)
        self.add_password_button.pack(side="left", padx=2, pady=2)
        # Bouton de la barre d'outil pour choisir la base
        self.choose_db_button = ttk.Button(
            self.toolbar_frame, text="Choisir la base", command=self.choose_db_popup)
        self.choose_db_button.pack(side="left", padx=2, pady=2)

        # Barre de recherche et menu
        self.filtres = ["Id", "Titre", "Utilisateur", "MDP", "URL", "Tout"]
        self.filter_value = tk.StringVar(self.toolbar_frame)
        self.filter_value.set("Titre")
        print(self.filter_value.get())
        
        self.filtre_recherche = ttk.OptionMenu(self.toolbar_frame, self.filter_value, "Titre", *self.filtres)
        self.filtre_recherche.pack(side="left", padx=2, pady=2)

        self.barre_recherche = ttk.Entry(self.toolbar_frame)
        self.barre_recherche.pack(side="left", padx=2, pady=2)
        self.barre_recherche.bind("<Return>", self.update_password_list)

        # On affiche les mdp dans la zone
        self.show_passwords()

        self.root.mainloop()

    def decode_password(self, encoded_password):
        return list(filter(None, cryptocode.decrypt(encoded_password.split("%")[1], "azerty123").split("%")))

    def encode_password(self, decoded_password):
        password = ""
        for item in decoded_password[1:]:
            password += str(item) + "%"
        password = decoded_password[0] + "%" + cryptocode.encrypt(password, "azerty123")
        return password
    
    # Fonction pour afficher les mdp dans la zone de liste
    def show_passwords(self):
        if hasattr(self, 'filtered_passwords'):
            password_list = self.filtered_passwords
        else:
            password_list = [self.decode_password(password) for password in self.get_passwords()]

        # Pour chaque mdp, on récupère son indice et sa valeur
        for y_coeff, decoded_password in enumerate(password_list):
            self.password = decoded_password
            # On créé un bouton qui seriva a afficher les infos du mdp
            button_password = ttk.Button(
                self.password_list_frame, text=self.password[1], command=lambda password=decoded_password: self.show_password_infos(password)) # On utilise on fonction lambda car on veut garder en mémoire le mdp à chaque itération de la boucle pour pouvoir intéragir avec, si on utilise pas une fonction lambda, le mdp enregistré sera le dernier de la boucle
            x = self.password_list_canvas.winfo_reqwidth()  # On récupère la largeur de la zone de liste pour y mettre les boutons
            button_password.bind(
            "<MouseWheel>", lambda e: self.password_list_canvas.yview_scroll(int(-e.delta/60), "units"))
            button_password_window = self.password_list_canvas.create_window(
                x, y_coeff*35+20, window=button_password) # On créé un fenêtre\widget de bouton dans le canvas en utilise l'indice du mdp comme coeficient de sa coordonée y (pour les espacer)

    # Fonction pour récuperer tout les mdp
    def get_passwords(self):
        return self.db.afficher_tout()

    # Fonction pour maj la liste de mdp
    @profile
    def update_password_list(self, e = None):
        # On supprime l'ancienne liste
        self.password_list_frame.destroy()
        self.password_list_canvas.destroy()
        self.scrollbar.destroy()

        passwords = self.get_passwords()

        match self.filter_value.get():
            case "Id":
                filter = 0
            case "Titre":
                filter = 1
            case "Utilisateur":
                filter = 2
            case "MDP":
                filter = 3
            case "URL":
                filter = 4
            case "Tout":
                filter = None

        self.filtered_passwords = []

        for password in passwords:
            password = self.decode_password(password)
            recherche = self.barre_recherche.get().lower()

            if recherche:
                if filter is not None:
                    if recherche in str(password[filter]).lower():
                        self.filtered_passwords.append(password)
                else:
                    if any(recherche in str(item).lower() for item in password):
                        self.filtered_passwords.append(password)
            else:
                self.filtered_passwords.append(password)
                # afficher tout


        # On la recréé avec les nouveaux mdp
        self.password_list_frame = ttk.Frame(self.root)
        self.password_list_canvas = tk.Canvas(self.password_list_frame, scrollregion=(0, 0, 0, len(self.filtered_passwords)*35), height=self.password_list_frame.winfo_height(), width=50)

        self.password_list_frame.pack(fill="both", expand=True, side="left")
        self.password_list_canvas.pack(fill="both", expand=True, side="left")

        self.password_list_canvas.bind(
            "<MouseWheel>", lambda e: self.password_list_canvas.yview_scroll(int(-e.delta/60), "units"))
        self.scrollbar = ttk.Scrollbar(
            self.password_list_canvas, orient="vertical", command=self.password_list_canvas.yview)

        self.scrollbar.bind(
            "<MouseWheel>", lambda e: self.password_list_canvas.yview_scroll(int(-e.delta/60), "units"))

        self.password_list_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")

        self.show_passwords()

    # Fonction pour afficher les infos d'un mdp
    def show_password_infos(self, password):
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
            self.password_info_frame, text="User : ")
        self.password_info_username_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_info_username_entry = ttk.Entry(self.password_info_frame)
        self.password_info_username_entry.grid(row=1, column=1, padx=5, pady=5)
        self.password_info_username_entry.insert(0, password[2])

        self.password_info_password_label = ttk.Label(
            self.password_info_frame, text="MDP : ")
        self.password_info_password_label.grid(row=2, column=0, padx=5, pady=5)
        self.password_info_password_entry = ttk.Entry(self.password_info_frame)
        self.password_info_password_entry.grid(row=2, column=1, padx=5, pady=5)
        self.password_info_password_entry.insert(0, password[3])

        self.password_info_url_label = ttk.Label(
            self.password_info_frame, text="URL : ")
        self.password_info_url_label.grid(row=3, column=0, padx=5, pady=5)
        self.password_info_url_entry = ttk.Entry(self.password_info_frame)
        self.password_info_url_entry.grid(row=3, column=1, padx=5, pady=5)
        self.password_info_url_entry.insert(0, password[4])

        # Boutons pour enregistrer les modifications
        self.password_info_save_button = ttk.Button(
            self.password_info_frame, text="Sauvegarder", command=lambda password=password: self.update_password_info(password))
        self.password_info_save_button.grid(row=4, column=0, padx=10, pady=10)
        # Bouton pour supprimer le mdp
        self.password_info_delete_button = ttk.Button(
            self.password_info_frame, text="Supprimer", command=lambda password=password: self.delete_password(password))
        self.password_info_delete_button.grid(
            row=4, column=1, padx=10, pady=10)

    # Fontion pour supprimer un mdp
    def delete_password(self, password):
        # Affiche un avertissement
        reponse = askyesno(
            "Supprimer", "Êtes vous sur de vouloir supprimer le mot de passe ?")
        if reponse:
            # Supprime le mdp et maj la liste
            self.db.supprimer_mdp_id(password[0])
            self.update_password_list()

    # Fonctions pour maj les infos d'un mdp dans la base
    def update_password_info(self, password):
        password = [password[0], self.password_info_title_entry.get(), self.password_info_username_entry.get(), self.password_info_password_entry.get(), self.password_info_url_entry.get()]

        # Change les infos du mdp en utilisant son id
        self.db.changer_mdp(password[0], self.password_title_var_encoded, self.password_username_var_encoded,
                            self.password_password_var_encoded, self.password_url_var_encoded)
        self.update_password_list()

    # Affiche une fenêtre pour ajouter un mdp
    def add_password_popup(self):
        # On utilise TopLevel car sa créé une fenêtre enfant, au premier plan
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Ajouter un MDP")
        self.popup.bind("<Return>", self.add_password_save)

        # Titre
        self.password_title_label = ttk.Label(self.popup, text="Titre")
        self.password_title_entry = ttk.Entry(self.popup)
        self.password_title_entry.focus_set()

        # Nom d'utilisateur
        self.password_username_label = ttk.Label(self.popup, text="Username")
        self.password_username_entry = ttk.Entry(self.popup)

        # MDP
        self.password_password_label = ttk.Label(self.popup, text="Password")
        self.password_password_entry = ttk.Entry(self.popup)

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
    def add_password_save(self, _):
        # Récupère et encode les infos du mdp
        self.password_title_var_encoded = cryptocode.encrypt(
            self.password_title_entry.get(), self.master_password_hash)
        self.password_username_var_encoded = cryptocode.encrypt(
            self.password_username_entry.get(), self.master_password_hash)
        self.password_password_var_encoded = cryptocode.encrypt(
            self.password_password_entry.get(), self.master_password_hash)
        self.password_url_var_encoded = cryptocode.encrypt(
            self.password_url_entry.get(), self.master_password_hash)

        # Ajoute le mdp à la base et supprime la fenêtre
        self.db.ajouter_mdp(self.password_title_var_encoded, self.password_username_var_encoded,
                            self.password_password_var_encoded, self.password_url_var_encoded)
        self.popup.destroy()
        self.update_password_list()



main = Main()
