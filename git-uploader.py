import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import json

# Όνομα αρχείου για την αποθήκευση των προφίλ
PROFILES_FILE = "git_profiles.json"

class GitGUIApp:
    def __init__(self, master):
        self.master = master
        master.title("Εύκολος Git Ανεβάτης")
        master.geometry("750x650") # Αυξάνουμε το μέγεθος λόγω νέων στοιχείων
        master.resizable(False, False)

        # Μεταβλητές
        self.project_path = tk.StringVar()
        self.repo_url = tk.StringVar()
        self.commit_message = tk.StringVar(value="Αρχικό commit")
        
        # Μεταβλητές για τη διαχείριση προφίλ
        self.profiles = self.load_profiles()
        self.selected_profile_name = tk.StringVar()
        self.new_profile_name = tk.StringVar()
        self.new_profile_email = tk.StringVar()
        self.new_profile_username = tk.StringVar()

        # --- GUI Elements ---

        # Project Path Selection
        tk.Label(master, text="Φάκελος Έργου:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.project_path, width=60, state="readonly").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(master, text="Αναζήτηση", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # Remote Repository URL
        tk.Label(master, text="URL Απομακρυσμένου Repo:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.repo_url, width=60).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(master, text="Ορισμός Remote URL", command=self.set_remote).grid(row=1, column=2, padx=5, pady=5) # Κουμπί για set remote

        # Commit Message
        tk.Label(master, text="Μήνυμα Commit:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.commit_message, width=60).grid(row=2, column=1, padx=5, pady=5, columnspan=2)

        # --- Profile Management Section ---
        profile_frame = tk.LabelFrame(master, text="Διαχείριση Προφίλ Git")
        profile_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        tk.Label(profile_frame, text="Επιλεγμένο Προφίλ:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        # Βεβαιωθείτε ότι υπάρχει πάντα τουλάχιστον μία επιλογή για το OptionMenu
        initial_profile_options = list(self.profiles.keys())
        if not initial_profile_options:
            initial_profile_options = ["-- Καθόλου Προφίλ --"] # Προσθέτουμε μια dummy επιλογή
            self.selected_profile_name.set(initial_profile_options[0]) # Ορίζουμε την dummy ως επιλεγμένη
        else:
            self.selected_profile_name.set(initial_profile_options[0]) # Επιλέγουμε το πρώτο προφίλ αν υπάρχουν

        self.profile_dropdown = tk.OptionMenu(profile_frame, self.selected_profile_name, *initial_profile_options, command=self.on_profile_selected)
        self.profile_dropdown.config(width=25)
        self.profile_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        tk.Button(profile_frame, text="Εφαρμογή Προφίλ", command=self.apply_selected_profile).grid(row=0, column=2, padx=5, pady=2)
        tk.Button(profile_frame, text="Διαγραφή Προφίλ", command=self.delete_profile).grid(row=0, column=3, padx=5, pady=2)

        tk.Label(profile_frame, text="Όνομα Προφίλ:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(profile_frame, textvariable=self.new_profile_name, width=28).grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        tk.Button(profile_frame, text="Προσθήκη Νέου Προφίλ", command=self.add_profile).grid(row=1, column=2, padx=5, pady=2, columnspan=2)

        tk.Label(profile_frame, text="Email:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(profile_frame, textvariable=self.new_profile_email, width=28).grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(profile_frame, text="Όνομα Χρήστη:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(profile_frame, textvariable=self.new_profile_username, width=28).grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        # --- Git Operations Buttons ---
        button_frame = tk.Frame(master)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)

        tk.Button(button_frame, text="1. Αρχικοποίηση Git", command=self.init_git, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="2. Προσθήκη Όλων", command=self.add_all, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="3. Commit", command=self.commit_files, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="4. Push στο Git", command=self.push_to_git, width=17).pack(side=tk.LEFT, padx=5) 

        # Separator
        tk.Frame(master, height=2, bd=1, relief=tk.SUNKEN).grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")

        # Output Console
        tk.Label(master, text="Έξοδος Κονσόλας:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.output_console = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=15, bg="#333", fg="lightgreen", font=("Consolas", 10))
        self.output_console.grid(row=7, column=0, columnspan=3, padx=10, pady=5)
        self.output_console.config(state="disabled") # Make it read-only

        # Clear Console Button
        tk.Button(master, text="Εκκαθάριση Κονσόλας", command=self.clear_console).grid(row=8, column=0, columnspan=3, pady=5)

        self.print_to_console("Καλώς ήρθατε στον Εύκολο Git Ανεβάτη!\n")
        self.print_to_console("Βεβαιωθείτε ότι το Git είναι εγκατεστημένο και διαθέσιμο στο PATH του συστήματός σας.\n")
        self.print_to_console("Επιλέξτε ή προσθέστε ένα προφίλ Git και πατήστε 'Εφαρμογή Προφίλ' πριν τις λειτουργίες Commit/Push.\n")

    def load_profiles(self):
        """Φορτώνει τα προφίλ από το αρχείο JSON."""
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content: # Ελέγχουμε αν το αρχείο είναι κενό
                        return json.loads(content)
            except json.JSONDecodeError:
                self.print_to_console(f"Προειδοποίηση: Το αρχείο '{PROFILES_FILE}' περιέχει μη έγκυρο JSON. Δημιουργείται νέο κενό.\n")
            except Exception as e:
                self.print_to_console(f"Προειδοποίηση: Σφάλμα κατά τη φόρτωση προφίλ από '{PROFILES_FILE}': {e}. Δημιουργείται νέο κενό.\n")
        return {} # Επιστρέφει κενό dictionary αν το αρχείο δεν υπάρχει, είναι κενό ή έχει σφάλμα

    def save_profiles(self):
        """Αποθηκεύει τα προφίλ στο αρχείο JSON."""
        try:
            with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.print_to_console(f"Σφάλμα κατά την αποθήκευση προφίλ στο '{PROFILES_FILE}': {e}\n")


    def update_profile_dropdown(self):
        """Ενημερώνει την αναπτυσσόμενη λίστα προφίλ."""
        self.profile_dropdown['menu'].delete(0, 'end') # Καθαρίζουμε όλες τις υπάρχουσες επιλογές

        profile_keys = list(self.profiles.keys())
        if profile_keys:
            # Προσθέτουμε τις πραγματικές επιλογές αν υπάρχουν προφίλ
            for profile_name in profile_keys:
                self.profile_dropdown['menu'].add_command(label=profile_name, command=tk._setit(self.selected_profile_name, profile_name, self.on_profile_selected))
            
            # Αν η τρέχουσα επιλογή δεν είναι πλέον έγκυρη, επιλέξτε την πρώτη διαθέσιμη
            if self.selected_profile_name.get() not in profile_keys:
                self.selected_profile_name.set(profile_keys[0])
        else:
            # Αν δεν υπάρχουν προφίλ, προσθέτουμε μια dummy επιλογή και καθαρίζουμε την επιλογή
            self.profile_dropdown['menu'].add_command(label="-- Καθόλου Προφίλ --", command=tk._setit(self.selected_profile_name, "-- Καθόλου Προφίλ --"))
            self.selected_profile_name.set("-- Καθόλου Προφίλ --")


    def add_profile(self):
        """Προσθέτει ένα νέο προφίλ."""
        name = self.new_profile_name.get().strip()
        email = self.new_profile_email.get().strip()
        username = self.new_profile_username.get().strip()

        if not name or not email or not username:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ συμπληρώστε όλα τα πεδία για το νέο προφίλ.")
            return

        if name in self.profiles:
            messagebox.showwarning("Προειδοποίηση", f"Το προφίλ '{name}' υπάρχει ήδη. Χρησιμοποιήστε διαφορετικό όνομα.")
            return

        self.profiles[name] = {"email": email, "username": username}
        self.save_profiles()
        self.update_profile_dropdown()
        self.selected_profile_name.set(name) # Επιλέξτε το νέο προφίλ
        self.new_profile_name.set("")
        self.new_profile_email.set("")
        self.new_profile_username.set("")
        messagebox.showinfo("Επιτυχία", f"Το προφίλ '{name}' προστέθηκε επιτυχώς!")
        self.print_to_console(f"Προφίλ '{name}' προστέθηκε.\n")

    def delete_profile(self):
        """Διαγράφει το επιλεγμένο προφίλ."""
        selected_name = self.selected_profile_name.get()
        if not selected_name or selected_name == "-- Καθόλου Προφίλ --":
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε ένα έγκυρο προφίλ για διαγραφή.")
            return
        
        if messagebox.askyesno("Επιβεβαίωση Διαγραφής", f"Είστε σίγουροι ότι θέλετε να διαγράψετε το προφίλ '{selected_name}';"):
            del self.profiles[selected_name]
            self.save_profiles()
            self.update_profile_dropdown()
            messagebox.showinfo("Επιτυχία", f"Το προφίλ '{selected_name}' διαγράφηκε επιτυχώς!")
            self.print_to_console(f"Προφίλ '{selected_name}' διαγράφηκε.\n")
            # Επαναφέρετε τα πεδία εισαγωγής αν το διαγραμμένο ήταν το επιλεγμένο
            self.new_profile_name.set("")
            self.new_profile_email.set("")
            self.new_profile_username.set("")


    def on_profile_selected(self, selected_name):
        """Καλείται όταν επιλεγεί ένα προφίλ από το dropdown."""
        if selected_name != "-- Καθόλου Προφίλ --":
            self.print_to_console(f"Επιλέχθηκε προφίλ: {selected_name}. Πατήστε 'Εφαρμογή Προφίλ' για να ορίσετε τα στοιχεία για αυτό το repository.\n")
        else:
            self.print_to_console("Δεν υπάρχει επιλεγμένο προφίλ.\n")


    def apply_selected_profile(self):
        """Εφαρμόζει το επιλεγμένο προφίλ στο τρέχον repository (local config)."""
        selected_name = self.selected_profile_name.get()
        if not selected_name or selected_name == "-- Καθόλου Προφίλ --":
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε ένα προφίλ για εφαρμογή.")
            return

        profile_data = self.profiles.get(selected_name)
        if not profile_data:
            messagebox.showerror("Σφάλμα", "Το επιλεγμένο προφίλ δεν βρέθηκε.")
            return
        
        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου πρώτα.")
            return
        
        self.print_to_console(f"\n--- Εφαρμογή προφίλ '{selected_name}' στο τοπικό repository ---\n")
        
        # Ρύθμιση user.email
        # Χρησιμοποιούμε --local για να ορίσουμε το config μόνο για αυτό το repo
        if not self.run_git_command(["git", "config", "--local", "user.email", profile_data["email"]]):
            messagebox.showerror("Σφάλμα", "Αποτυχία ρύθμισης user.email.")
            return
        
        # Ρύθμιση user.name
        if not self.run_git_command(["git", "config", "--local", "user.name", profile_data["username"]]):
            messagebox.showerror("Σφάλμα", "Αποτυχία ρύθμισης user.name.")
            return
        
        messagebox.showinfo("Επιτυχία", f"Το προφίλ '{selected_name}' εφαρμόστηκε επιτυχώς στο τοπικό repository!")
        self.print_to_console(f"Το προφίλ '{selected_name}' εφαρμόστηκε: Email: {profile_data['email']}, Όνομα: {profile_data['username']}.\n")

    def print_to_console(self, text):
        """Προσθέτει κείμενο στην περιοχή εξόδου της κονσόλας."""
        self.output_console.config(state="normal") # Ενεργοποίηση για εγγραφή
        self.output_console.insert(tk.END, text)
        self.output_console.see(tk.END) # Κύλιση στο τέλος
        self.output_console.config(state="disabled") # Απενεργοποίηση ξανά

    def clear_console(self):
        """Εκκαθαρίζει την περιοχή εξόδου της κονσόλας."""
        self.output_console.config(state="normal")
        self.output_console.delete(1.0, tk.END)
        self.output_console.config(state="disabled")

    def run_git_command(self, command):
        """Εκτελεί μια εντολή Git και εκτυπώνει την έξοδό της, ελέγχοντας τον κωδικό επιστροφής."""
        project_path = self.project_path.get()
        # Επιτρέπουμε ορισμένες εντολές git config να τρέξουν χωρίς επιλεγμένο project path
        # εφόσον χειριζόμαστε τοπικά (project-specific) configs.
        if not project_path and (len(command) > 1 and command[1] != "config"): 
            self.print_to_console("Σφάλμα: Δεν έχει επιλεχθεί φάκελος έργου για την εκτέλεση της εντολής.\n")
            return False
        
        # Ειδικός χειρισμός για την περίπτωση που το project_path είναι κενό αλλά η εντολή είναι 'git init'
        # (αν και το init πρέπει να γίνεται σε φάκελο, οπότε ο έλεγχος παραμένει)
        # Αυτός ο έλεγχος είναι κυρίως για config commands.

        original_dir = os.getcwd()
        try:
            if project_path: # Μόνο αν υπάρχει project_path, πηγαίνουμε σε αυτόν τον κατάλογο
                os.chdir(project_path)
            
            self.print_to_console(f"\nΕκτέλεση: {' '.join(command)}\n")
            
            process = subprocess.Popen(command, 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       text=True, 
                                       encoding='utf-8')
            
            stdout, stderr = process.communicate()
            
            if stdout:
                self.print_to_console("STDOUT:\n" + stdout)
            
            if stderr:
                self.print_to_console("STDERR:\n" + stderr)

            if process.returncode != 0:
                messagebox.showerror("Σφάλμα Git", f"Προέκυψε σφάλμα κατά τη λειτουργία του Git (Κωδικός: {process.returncode}). Ελέγξτε την κονσόλα για λεπτομέρειες.")
                return False 
            
            return True 
            
        except FileNotFoundError:
            messagebox.showerror("Σφάλμα", "Η εντολή Git δεν βρέθηκε. Βεβαιωθείτε ότι το Git είναι εγκατεστημένο και στο PATH του συστήματός σας.")
            self.print_to_console("Σφάλμα: Η εντολή Git δεν βρέθηκε. Βεβαιωθείτε ότι το Git είναι εγκατεστημένο.\n")
            return False
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Προέκυψε ένα απροσδόκητο σφάλμα: {e}")
            self.print_to_console(f"Απροσδόκητο σφάλμα: {e}\n")
            return False
        finally:
            os.chdir(original_dir) # Πάντα επιστρέφουμε στον αρχικό κατάλογο


    def browse_folder(self):
        """Ανοίγει ένα παράθυρο διαλόγου για την επιλογή του φακέλου του έργου."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.project_path.set(folder_selected)
            self.print_to_console(f"Επιλέχθηκε φάκελος έργου: {folder_selected}\n")

    def init_git(self):
        """Αρχικοποιεί ένα νέο Git repository."""
        self.print_to_console("\n--- Αρχικοποίηση Git Repository ---\n")
        if self.run_git_command(["git", "init"]):
            self.print_to_console("Git repository αρχικοποιήθηκε επιτυχώς.\n")
            messagebox.showinfo("Επιτυχία", "Git repository αρχικοποιήθηκε!")

    def add_all(self):
        """Προσθέτει όλα τα αρχεία στην περιοχή staging του Git."""
        self.print_to_console("\n--- Προσθήκη όλων των αρχείων στην περιοχή staging ---\n")
        if self.run_git_command(["git", "add", "."]):
            self.print_to_console("Όλα τα αρχεία προστέθηκαν στην περιοχή staging.\n")
            messagebox.showinfo("Επιτυχία", "Όλα τα αρχεία προστέθηκαν στην περιοχή staging!")

    def commit_files(self):
        """Κάνει commit τα αρχεία που βρίσκονται σε staging με το καθορισμένο μήνυμα."""
        message = self.commit_message.get()
        if not message:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ εισάγετε ένα μήνυμα commit.")
            return

        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου πρώτα.")
            return

        # Ελέγχουμε αν έχουν οριστεί user.email και user.name για αυτό το repository
        original_dir = os.getcwd()
        os.chdir(project_path)
        # Χρησιμοποιούμε --local για να διαβάσουμε τοπικές ρυθμίσεις
        email_check_process = subprocess.run(["git", "config", "--local", "user.email"], capture_output=True, text=True, encoding='utf-8')
        name_check_process = subprocess.run(["git", "config", "--local", "user.name"], capture_output=True, text=True, encoding='utf-8')
        os.chdir(original_dir)

        if not email_check_process.stdout.strip() or not name_check_process.stdout.strip():
            messagebox.showwarning("Προειδοποίηση", "Δεν έχουν οριστεί email και όνομα χρήστη για αυτό το repository. Επιλέξτε και εφαρμόστε ένα προφίλ.")
            self.print_to_console("Προειδοποίηση: Δεν έχουν οριστεί email και όνομα χρήστη για αυτό το repository. Χρησιμοποιήστε την ενότητα 'Διαχείριση Προφίλ Git' για να εφαρμόσετε ένα προφίλ.\n")
            return
            
        self.print_to_console(f"\n--- Commit με μήνυμα: '{message}' ---\n")
        if self.run_git_command(["git", "commit", "-m", message]):
            self.print_to_console(f"Τα αρχεία έγιναν commit επιτυχώς με μήνυμα: '{message}'.\n")
            messagebox.showinfo("Επιτυχία", "Τα αρχεία έγιναν commit επιτυχώς!")

    def set_remote(self):
        """Ορίζει το remote origin URL."""
        repo_url = self.repo_url.get()
        if not repo_url:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ εισάγετε το URL του απομακρυσμένου repository.")
            return
        
        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου πρώτα.")
            return False

        self.print_to_console(f"\n--- Ορισμός remote origin σε: {repo_url} ---\n")

        # Ελέγχουμε αν υπάρχει ήδη origin
        original_dir = os.getcwd()
        try:
            os.chdir(project_path)
            # Χρησιμοποιούμε check_output για να πιάσουμε την έξοδο
            check_remote_output = subprocess.check_output(["git", "remote"], text=True, encoding='utf-8').strip()
            remote_exists = "origin" in check_remote_output
        except subprocess.CalledProcessError as e:
            # Αν το git remote αποτύχει (πχ. δεν είναι git repo ακόμα)
            self.print_to_console(f"Προειδοποίηση: Δεν είναι έγκυρο Git repository για έλεγχο remote: {e}\n")
            remote_exists = False
        except FileNotFoundError:
            messagebox.showerror("Σφάλμα", "Η εντολή Git δεν βρέθηκε.")
            self.print_to_console("Σφάλμα: Η εντολή Git δεν βρέθηκε.\n")
            return False
        finally:
            os.chdir(original_dir) # Πάντα επιστρέφουμε άμεσα

        if remote_exists:
            self.print_to_console("Το remote 'origin' υπάρχει ήδη. Προσπάθεια αφαίρεσης και επαναπροσθήκης...\n")
            if not self.run_git_command(["git", "remote", "remove", "origin"]):
                messagebox.showerror("Σφάλμα Git", "Αποτυχία αφαίρεσης του υπάρχοντος remote 'origin'.")
                return # Διακοπή αν αποτύχει η αφαίρεση
            self.print_to_console("Το υπάρχον 'origin' αφαιρέθηκε επιτυχώς.\n")
        
        if self.run_git_command(["git", "remote", "add", "origin", repo_url]):
            self.print_to_console("Το remote 'origin' προστέθηκε/επαναπροστέθηκε επιτυχώς.\n")
            messagebox.showinfo("Επιτυχία", "Το remote 'origin' ορίστηκε!")
        else:
            messagebox.showerror("Σφάλμα Git", "Αποτυχία ορισμού του remote 'origin'.")

    def push_to_git(self):
        """Κάνει push τις αλλαγές που έγιναν commit στο απομακρυσμένο repository."""
        self.print_to_console("\n--- Push στο Git repository ---\n")
        
        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου πρώτα.")
            return False

        current_branch = "master" # Προεπιλογή
        original_dir = os.getcwd()
        try:
            os.chdir(project_path)
            
            # Λήψη ονόματος τρέχοντος branch
            branch_process = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                                            capture_output=True, text=True, encoding='utf-8')
            if branch_process.returncode == 0:
                current_branch = branch_process.stdout.strip()
                self.print_to_console(f"Ανιχνεύθηκε τρέχον branch: {current_branch}\n")
            else:
                self.print_to_console("Προειδοποίηση: Δεν ήταν δυνατή η ανίχνευση του τρέχοντος branch, χρησιμοποιείται το 'master' ως προεπιλογή.\n")
                if branch_process.stderr:
                    self.print_to_console("STDERR κατά την ανίχνευση branch:\n" + branch_process.stderr)

        except FileNotFoundError:
            messagebox.showerror("Σφάλμα", "Η εντολή Git δεν βρέθηκε. Βεβαιωθείτε ότι το Git είναι εγκατεστημένο και στο PATH του συστήματός σας.")
            self.print_to_console("Σφάλμα: Η εντολή Git δεν βρέθηκε.\n")
            return
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Προέκυψε ένα απροσδόκητο σφάλμα κατά την ανίχνευση του branch: {e}")
            self.print_to_console(f"Απροσδόκητο σφάλμα κατά την ανίχνευση του branch: {e}\n")
            return
        finally:
            os.chdir(original_dir) # Επιστροφή στον αρχικό κατάλογο

        # Προχωρήστε με το push
        if self.run_git_command(["git", "push", "-u", "origin", current_branch]):
            self.print_to_console("Επιτυχής push στο Git repository!\n")
            messagebox.showinfo("Επιτυχία", "Το έργο ανέβηκε επιτυχώς στο Git!")
        else:
            self.print_to_console("Αποτυχία push στο Git repository. Ελέγξτε την κονσόλα για σφάλματα.\n")


# Εκτέλεση κύριας εφαρμογής
if __name__ == "__main__":
    root = tk.Tk()
    app = GitGUIApp(root)
    root.mainloop()