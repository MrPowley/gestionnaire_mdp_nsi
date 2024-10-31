import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno, showerror
from tkinter.filedialog import askopenfilename, asksaveasfile 
from tkinter.simpledialog import askstring
import os
import cryptocode
import hashlib

PWD = os.getcwd()

def hash_string(string):
    """
    Return a SHA-256 hash of the given string
    """
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

class Base:
    def __init__(self, db_path):
        self.db_path = db_path

        self.connecter()
        self.cursor.execute("""create table if not exists MDP(
    id integer primary key autoincrement unique,
    title text,
    username text,
    password text,
    url text
    )
    """)
        self.cursor.execute("""create table if not exists Maitre(
    id integer primary key autoincrement unique,
    password_hash text
    )
    """)

    def connecter(self) -> None:
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()
        self.db.commit()

    def deconnecter(self) -> None:
        self.db.close()

    def ajouter_mdp(self, title: str, username: str, password: str, url: str) -> None:
        self.cursor.execute("""insert into MDP(title, username, password, url) values(?, ?, ?, ?)""", (title, username, password, url))
        self.db.commit()

    def supprimer_mdp_id(self, id: int) -> None:
        self.cursor.execute("""delete from MDP where id = ?""", (id, ))
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
    
    def afficher_hash_mdp_maitre(self):
        self.cursor.execute("""select * from Maitre""")
        return self.cursor.fetchone()
    
    def choisir_mdp_maitre(self, hash):
        self.cursor.execute("""insert into Maitre(password_hash) values(?)""", (hash,))
        self.db.commit()



class Main:
    def __init__(self):
        self.choose_db_popup()

    def main_menu(self):
        try:
            self.root.destroy()
        except AttributeError:
            pass
        # Initialisation de la fenêtre
        self.root = tk.Tk()
        self.root.title("Gestionnaire de Mots De Passe 2000")
        self.root.geometry("400x200")


        s = ttk.Style()
        s.configure('toolbar.TFrame', background='#d3d3d3')
        s.configure('green.TFrame', background='#00FF00')
        s.configure('blue.TFrame', background='#0000FF')



        self.toolbar_frame = ttk.Frame(self.root, style="toolbar.TFrame")
        self.password_list_frame = ttk.Frame(self.root) #, style="green.TFrame"
        self.password_list_canvas = tk.Canvas(self.password_list_frame, scrollregion= (0, 0, 0, len(self.get_passwords())*35), height=self.password_list_frame.winfo_height(), width=50)
        self.password_info_frame = ttk.Frame(self.root) #, style="blue.TFrame"

        self.toolbar_frame.pack(side="top", fill="x")
        self.password_list_frame.pack(fill="both", expand=True, side="left")
        self.password_list_canvas.pack(fill="both", expand=True, side="left")
        self.password_info_frame.pack(fill="both", side="right") # expand=True, 

        self.password_list_canvas.bind("<MouseWheel>", lambda e: self.password_list_canvas.yview_scroll(int(-e.delta/60), "units"))
        self.scrollbar = ttk.Scrollbar(self.password_list_canvas, orient="vertical", command=self.password_list_canvas.yview)
        self.password_list_canvas.configure(yscrollcommand= self.scrollbar.set)
        self.scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")


        self.add_password_button = ttk.Button(self.toolbar_frame, text="Ajouter MDP", command=self.add_password_popup)
        self.add_password_button.pack(side="left",padx=2, pady=2)

        self.choose_db_button = ttk.Button(self.toolbar_frame, text="Choisir la base", command=self.choose_db_popup)
        self.choose_db_button.pack(side="left",padx=2, pady=2)

        self.show_passwords()

        self.root.mainloop()

    def init_base(self, db_path = os.path.join(PWD, "mdp.db")):
        self.db = Base(db_path=db_path)

    def open_db(self):
        filetypes = (
            ('Database file', '*.db'),
            ('All files', '*.*')
            )
        self.db_path = askopenfilename(title='Ouvrir une base', initialdir=PWD, filetypes=filetypes)

        self.master_password_hash = hash_string(askstring(
            title="Base de mots de passe", prompt="Veuillez entrer le MDP Maitre"))
        self.init_base(self.db_path)
        self.db_master_password = self.db.afficher_hash_mdp_maitre()[1]
        
        if self.master_password_hash == self.db_master_password:
            self.database_popup.destroy()
            self.main_menu()
            return
        
        showerror("MDP", "Mauvais mot de passe Maitre")
        
    
    def create_db(self):
        filetypes = (
            ('Data Base File', '*.db'),
            ('All files', '*.*')
            )
        file = asksaveasfile(title='Créer une base', initialdir=PWD, filetypes=filetypes, defaultextension = filetypes)
        self.db_path = file.name
        self.init_base(self.db_path)

        self.master_password_hash_1 = hash_string(askstring(
            title="Base", prompt="Veuillez entrer un nouveau MDP Maitre"))
        self.master_password_hash_2 = hash_string(askstring(
            title="Base de mots de passe", prompt="Veuillez confirmer le MDP Maitre"))
        
        if self.master_password_hash_1 == self.master_password_hash_2:
            self.master_password_hash = self.master_password_hash_1
            self.db.choisir_mdp_maitre(self.master_password_hash)
            self.database_popup.destroy()
            self.main_menu()
            return
        
        showerror("MDP", "Les 2 mots de passe ne correspondent pas")
        


    def choose_db_popup(self):
        self.database_popup = tk.Tk()
        self.database_popup.title("Choisir une base")

        # Titre
        self.password_title_label = ttk.Label(self.database_popup, text="Que voulez vous choisir ?")
        self.password_title_label.grid(row=0, column=0, columnspan=4)

        # Buttons
        self.database_open_button = ttk.Button(self.database_popup, text="Ouvrir un base", command=self.open_db)
        self.database_open_button.grid(row=1, column=0)

        self.database_create_button = ttk.Button(self.database_popup, text="Créer une base", command=self.create_db)
        self.database_create_button.grid(row=1, column=1)



        self.database_popup.mainloop()


    def get_passwords(self):
        return self.db.afficher_tout()

    def update_password_list(self):
        self.password_list_frame.destroy()
        self.password_list_canvas.destroy()
        self.scrollbar.destroy()


        self.password_list_frame = ttk.Frame(self.root, style="green.TFrame")
        self.password_list_canvas = tk.Canvas(self.password_list_frame, scrollregion= (0, 0, 0, len(self.get_passwords())*35), height=self.password_list_frame.winfo_height(), width=50)

        self.password_list_frame.pack(fill="both", expand=True, side="left")
        self.password_list_canvas.pack(fill="both", expand=True, side="left")

        self.password_list_canvas.bind("<MouseWheel>", lambda e: self.password_list_canvas.yview_scroll(int(-e.delta/60), "units"))
        self.scrollbar = ttk.Scrollbar(self.password_list_canvas, orient="vertical", command=self.password_list_canvas.yview)
        self.password_list_canvas.configure(yscrollcommand= self.scrollbar.set)
        self.scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")

        self.show_passwords()
    
    def show_password_infos(self, password):
        self.password_info_frame.destroy()
        self.password_info_frame = ttk.Frame(self.root) #, style="blue.TFrame"
        self.password_info_frame.pack(fill="both", side="right") # expand=True,

        self.password_info_title_label = ttk.Label(self.password_info_frame, text="Titre : ")
        self.password_info_title_label.grid(row=0, column=0, padx=5, pady=5)
        self.password_info_title_entry = ttk.Entry(self.password_info_frame,)
        self.password_info_title_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_info_title_entry.insert(0, password[1])

        self.password_info_username_label = ttk.Label(self.password_info_frame, text="User : ")
        self.password_info_username_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_info_username_entry = ttk.Entry(self.password_info_frame)
        self.password_info_username_entry.grid(row=1, column=1, padx=5, pady=5)
        self.password_info_username_entry.insert(0, password[2])
    
        self.password_info_password_label = ttk.Label(self.password_info_frame, text="MDP : ")
        self.password_info_password_label.grid(row=2, column=0, padx=5, pady=5)
        self.password_info_password_entry = ttk.Entry(self.password_info_frame)
        self.password_info_password_entry.grid(row=2, column=1, padx=5, pady=5)
        self.password_info_password_entry.insert(0, password[3])

        self.password_info_url_label = ttk.Label(self.password_info_frame, text="URL : ")
        self.password_info_url_label.grid(row=3, column=0, padx=5, pady=5)
        self.password_info_url_entry = ttk.Entry(self.password_info_frame)
        self.password_info_url_entry.grid(row=3, column=1, padx=5, pady=5)
        self.password_info_url_entry.insert(0, password[4])

        self.password_info_save_button = ttk.Button(self.password_info_frame, text="Sauvegarder")
        self.password_info_save_button.grid(row=4, column=0, padx=10, pady=10)
        self.password_info_delete_button = ttk.Button(self.password_info_frame, text="Supprimer", command=lambda password=password: self.delete_password(password))
        self.password_info_delete_button.grid(row=4, column=1, padx=10, pady=10)

    def delete_password(self, password):
        reponse = askyesno("Supprimer", "Êtes vous sur de vouloir supprimer le mot de passe ?")
        if reponse:
            self.db.supprimer_mdp_id(password[0])
            self.update_password_list()

    def update_password_info(self):
        ...

    def show_passwords(self):
        for y_coeff, encoded_password in enumerate(self.get_passwords()):
            decoded_password = [encoded_password[0]] + [cryptocode.decrypt(encoded_items, self.master_password_hash) for encoded_items in encoded_password[1:]]
            self.password = decoded_password
            button_password = ttk.Button(self.password_list_frame, text=self.password[1], command=lambda password=decoded_password: self.show_password_infos(password))
            x = self.password_list_canvas.winfo_reqwidth() #( / 2)
            button_password_window = self.password_list_canvas.create_window(x, y_coeff*35+20, window=button_password)

    def add_password_save(self):
        self.password_title_var_encoded = cryptocode.encrypt(self.password_title_var.get(), self.master_password_hash)
        self.password_username_var_encoded = cryptocode.encrypt(self.password_username_var.get(), self.master_password_hash)
        self.password_password_var_encoded = cryptocode.encrypt(self.password_password_var.get(), self.master_password_hash)
        self.password_url_var_encoded = cryptocode.encrypt(self.password_url_var.get(), self.master_password_hash)

        self.db.ajouter_mdp(self.password_title_var_encoded, self.password_username_var_encoded, self.password_password_var_encoded, self.password_url_var_encoded)
        self.popup.destroy()
        self.update_password_list()

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

# base = Base("mdp3.db")
# print(base.choisir_mdp_maitre("dhuqzdqz"))
# print(base.afficher_hash_mdp_maitre())


