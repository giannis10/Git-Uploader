import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import json
import time # Χρησιμοποιείται για ένα μικρό delay για καλύτερη εμφάνιση μηνυμάτων

# Όνομα αρχείου για την αποθήκευση των προφίλ
PROFILES_FILE = "git_profiles.json"

class GitGUIApp:
    def __init__(self, master):
        self.master = master
        master.title("Εύκολος Git Ανεβάτης")
        master.geometry("750x760") # Αυξάνουμε το μέγεθος λόγω νέων στοιχείων και του νέου κουμπιού
        master.resizable(False, False)

        # Μεταβλητές
        self.project_path = tk.StringVar()
        self.repo_url = tk.StringVar()
        self.commit_message = tk.StringVar(value="Αρχικό commit")
        self.current_branch = tk.StringVar(value="main") # Μεταβλητή για το branch, με προεπιλογή 'main'
        
        # Μεταβλητές για τη διαχείριση προφίλ
        self.profiles = self.load_profiles()
        self.selected_profile_name = tk.StringVar()
        # Νέες μεταβλητές για την προσθήκη/επεξεργασία προφίλ
        self.new_profile_name = tk.StringVar()
        self.new_profile_email = tk.StringVar()
        self.new_profile_username = tk.StringVar()
        self.new_profile_default_branch = tk.StringVar(value="main") # Νέα μεταβλητή για default branch, με προεπιλογή 'main'

        # --- GUI Elements ---

        # Project Path Selection
        tk.Label(master, text="Φάκελος Έργου:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.project_path, width=60, state="readonly").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(master, text="Αναζήτηση", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # Remote Repository URL
        tk.Label(master, text="URL Απομακρυσμένου Repo:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.repo_url, width=60).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(master, text="Ορισμός Remote URL", command=self.set_remote).grid(row=1, column=2, padx=5, pady=5)

        # Commit Message
        tk.Label(master, text="Μήνυμα Commit:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.commit_message, width=60).grid(row=2, column=1, padx=5, pady=5, columnspan=2)

        # Current Branch (Νέο πεδίο)
        tk.Label(master, text="Τρέχον Branch:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.current_branch, width=60).grid(row=3, column=1, padx=5, pady=5, columnspan=2)
        
        # --- Profile Management Section ---
        profile_frame = tk.LabelFrame(master, text="Διαχείριση Προφίλ Git")
        profile_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        tk.Label(profile_frame, text="Επιλεγμένο Προφίλ:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        initial_profile_options = list(self.profiles.keys())
        if not initial_profile_options:
            initial_profile_options = ["-- Καθόλου Προφίλ --"]
            self.selected_profile_name.set(initial_profile_options[0])
        else:
            self.selected_profile_name.set(initial_profile_options[0])

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
        
        # Νέο πεδίο: Προεπιλεγμένο Branch για το προφίλ
        tk.Label(profile_frame, text="Προεπιλεγμένο Branch:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(profile_frame, textvariable=self.new_profile_default_branch, width=28).grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        # --- Git Operations Buttons (Individual) ---
        button_frame = tk.Frame(master)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10) # Ενημέρωση σειράς

        tk.Button(button_frame, text="1. Αρχικοποίηση Git", command=self.init_git, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="2. Προσθήκη Όλων", command=self.add_all, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="3. Commit", command=self.commit_files, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="4. Push στο Git", command=self.push_to_git, width=17).pack(side=tk.LEFT, padx=5) 

        # --- Νέο κουμπί "Εκτέλεση Όλων" (τοποθετείται κάτω από τα 4) ---
        tk.Button(master, text="Εκτέλεση Όλων", command=self.execute_all_git_operations, 
                  font=("Helvetica", 10, "bold"), bg="lightblue", fg="darkblue", width=40).grid(row=6, column=0, columnspan=3, pady=15) # Ενημέρωση σειράς

        # Separator
        tk.Frame(master, height=2, bd=1, relief=tk.SUNKEN).grid(row=7, column=0, columnspan=3, pady=10, sticky="ew") # Ενημέρωση σειράς

        # Output Console
        tk.Label(master, text="Έξοδος Κονσόλας:").grid(row=8, column=0, padx=10, pady=5, sticky="w") # Ενημέρωση σειράς
        self.output_console = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=15, bg="#333", fg="lightgreen", font=("Consolas", 10))
        self.output_console.grid(row=9, column=0, columnspan=3, padx=10, pady=5) # Ενημέρωση σειράς
        self.output_console.config(state="disabled") # Make it read-only

        # Clear Console Button
        tk.Button(master, text="Εκκαθάριση Κονσόλας", command=self.clear_console).grid(row=10, column=0, columnspan=3, pady=5) # Ενημέρωση σειράς

        self.print_to_console("Καλώς ήρθατε στον Εύκολο Git Ανεβάτη!\n")
        self.print_to_console("Βεβαιωθείτε ότι το Git είναι εγκατεστημένο και διαθέσιμο στο PATH του συστήματός σας.\n")
        self.print_to_console("Επιλέξτε ή προσθέστε ένα προφίλ Git και πατήστε 'Εφαρμογή Προφίλ' πριν τις λειτουργίες Commit/Push.\n")

    def load_profiles(self):
        """Φορτώνει τα προφίλ από το αρχείο JSON."""
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content:
                        profiles_data = json.loads(content)
                        # Ενημέρωση παλαιότερων προφίλ για να περιλαμβάνουν default_branch
                        for profile in profiles_data.values():
                            if 'default_branch' not in profile:
                                profile['default_branch'] = 'main' # Προεπιλεγμένη τιμή αν λείπει
                        return profiles_data
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
        default_branch = self.new_profile_default_branch.get().strip() # Παίρνουμε το default branch

        if not name or not email or not username or not default_branch:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ συμπληρώστε όλα τα πεδία για το νέο προφίλ (συμπεριλαμβανομένου του προεπιλεγμένου branch).")
            return

        if name in self.profiles:
            messagebox.showwarning("Προειδοποίηση", f"Το προφίλ '{name}' υπάρχει ήδη. Χρησιμοποιήστε διαφορετικό όνομα.")
            return

        # Αποθηκεύουμε και το default_branch στο προφίλ
        self.profiles[name] = {"email": email, "username": username, "default_branch": default_branch}
        self.save_profiles()
        self.update_profile_dropdown()
        self.selected_profile_name.set(name) # Επιλέξτε το νέο προφίλ
        self.new_profile_name.set("")
        self.new_profile_email.set("")
        self.new_profile_username.set("")
        self.new_profile_default_branch.set("main") # Επαναφορά στην προεπιλογή μετά την προσθήκη
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
            self.new_profile_default_branch.set("main") # Επαναφορά στην προεπιλογή


    def on_profile_selected(self, selected_name):
        """Καλείται όταν επιλεγεί ένα προφίλ από το dropdown."""
        if selected_name != "-- Καθόλου Προφίλ --":
            self.print_to_console(f"Επιλέχθηκε προφίλ: {selected_name}. Πατήστε 'Εφαρμογή Προφίλ' για να ορίσετε τα στοιχεία για αυτό το repository.\n")
            # Συμπλήρωση των πεδίων προσθήκης/επεξεργασίας με τα δεδομένα του επιλεγμένου προφίλ
            if selected_name in self.profiles:
                profile_data = self.profiles[selected_name]
                self.new_profile_name.set(selected_name)
                self.new_profile_email.set(profile_data.get('email', ''))
                self.new_profile_username.set(profile_data.get('username', ''))
                self.new_profile_default_branch.set(profile_data.get('default_branch', 'main'))
        else:
            self.print_to_console("Δεν υπάρχει επιλεγμένο προφίλ.\n")
            # Καθαρισμός πεδίων αν δεν υπάρχει επιλεγμένο προφίλ
            self.new_profile_name.set("")
            self.new_profile_email.set("")
            self.new_profile_username.set("")
            self.new_profile_default_branch.set("main") # Επαναφορά στην προεπιλογή

    def apply_selected_profile(self):
        """Εφαρμόζει το επιλεγμένο προφίλ στο τρέχον repository (local config)."""
        selected_name = self.selected_profile_name.get()
        if not selected_name or selected_name == "-- Καθόλου Προφίλ --":
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε ένα προφίλ για εφαρμογή.")
            return False # Επιστρέφουμε False για να δείξουμε αποτυχία

        profile_data = self.profiles.get(selected_name)
        if not profile_data:
            messagebox.showerror("Σφάλμα", "Το επιλεγμένο προφίλ δεν βρέθηκε.")
            return False # Επιστρέφουμε False

        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου πρώτα.")
            return False # Επιστρέφουμε False
        
        self.print_to_console(f"\n--- Εφαρμογή προφίλ '{selected_name}' στο τοπικό repository ---\n")
        
        # Ρύθμιση user.email
        # Χρησιμοποιούμε --local για να ορίσουμε το config μόνο για αυτό το repo
        if not self.run_git_command(["git", "config", "--local", "user.email", profile_data["email"]]):
            messagebox.showerror("Σφάλμα", "Αποτυχία ρύθμισης user.email.")
            return False # Επιστρέφουμε False
        
        # Ρύθμιση user.name
        if not self.run_git_command(["git", "config", "--local", "user.name", profile_data["username"]]):
            messagebox.showerror("Σφάλμα", "Αποτυχία ρύθμισης user.name.")
            return False # Επιστρέφουμε False

        # Ρύθμιση του πεδίου "Τρέχον Branch" με το προεπιλεγμένο branch του προφίλ
        default_branch = profile_data.get('default_branch', 'main') # Παίρνουμε το branch ή 'main' αν δεν υπάρχει
        self.current_branch.set(default_branch)
        self.print_to_console(f"Το προεπιλεγμένο branch του προφίλ ορίστηκε στο πεδίο 'Τρέχον Branch': {default_branch}.\n")
        
        messagebox.showinfo("Επιτυχία", f"Το προφίλ '{selected_name}' εφαρμόστηκε επιτυχώς στο τοπικό repository!")
        self.print_to_console(f"Το προφίλ '{selected_name}' εφαρμόστηκε: Email: {profile_data['email']}, Όνομα: {profile_data['username']}.\n")
        return True # Επιστρέφουμε True για επιτυχία

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
            self.print_to_console("Σφάλμα: Η εντολή Git δεν βρέθηκε.\n")
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
            self.detect_current_branch() # Καλούμε την ανίχνευση branch

    def detect_current_branch(self):
        """Ανιχνεύει το τρέχον Git branch του επιλεγμένου φακέλου έργου."""
        project_path = self.project_path.get()
        if not project_path:
            self.current_branch.set("main") # Επαναφορά σε main αν δεν υπάρχει φάκελος
            return
        
        original_dir = os.getcwd()
        try:
            os.chdir(project_path)
            # Ελέγχουμε αν είναι Git repository
            is_git_repo_process = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True, encoding='utf-8')
            if is_git_repo_process.returncode != 0:
                self.print_to_console("Προειδοποίηση: Ο επιλεγμένος φάκελος δεν είναι Git repository. Το branch ορίζεται σε 'main'.\n")
                self.current_branch.set("main")
                return

            branch_process = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                                            capture_output=True, text=True, encoding='utf-8')
            if branch_process.returncode == 0:
                detected_branch = branch_process.stdout.strip()
                self.current_branch.set(detected_branch)
                self.print_to_console(f"Ανιχνεύθηκε τρέχον branch: {detected_branch}\n")
            else:
                self.print_to_console("Προειδοποίηση: Δεν ήταν δυνατή η ανίχνευση του τρέχοντος branch, χρησιμοποιείται το 'main' ως προεπιλογή.\n")
                self.current_branch.set("main")
                if branch_process.stderr:
                    self.print_to_console("STDERR κατά την ανίχνευση branch:\n" + branch_process.stderr)

        except FileNotFoundError:
            self.print_to_console("Σφάλμα: Η εντολή Git δεν βρέθηκε κατά την ανίχνευση branch. Βεβαιωθείτε ότι το Git είναι εγκατεστημένο.\n")
            self.current_branch.set("main")
        except Exception as e:
            self.print_to_console(f"Απροσδόκητο σφάλμα κατά την ανίχνευση του branch: {e}\n")
            self.current_branch.set("main")
        finally:
            os.chdir(original_dir)


    def init_git(self):
        """Αρχικοποιεί ένα νέο Git repository."""
        self.print_to_console("\n--- Αρχικοποίηση Git Repository ---\n")
        if self.run_git_command(["git", "init"]):
            self.print_to_console("Git repository αρχικοποιήθηκε επιτυχώς.\n")
            messagebox.showinfo("Επιτυχία", "Git repository αρχικοποιήθηκε!")
            self.detect_current_branch() # Ενημέρωση branch μετά το init
            return True # Επιστρέφουμε True για επιτυχία
        return False # Επιστρέφουμε False για αποτυχία

    def add_all(self):
        """Προσθέτει όλα τα αρχεία στην περιοχή staging του Git."""
        if not self.ensure_git_initialized():
            messagebox.showerror("Σφάλμα", "Αποτυχία αρχικοποίησης git repository.")
            return False
        self.print_to_console("\n--- Προσθήκη όλων των αρχείων στην περιοχή staging ---\n")
        if self.run_git_command(["git", "add", "."]):
            self.print_to_console("Όλα τα αρχεία προστέθηκαν στην περιοχή staging.\n")
            messagebox.showinfo("Επιτυχία", "Όλα τα αρχεία προστέθηκαν στην περιοχή staging!")
            return True # Επιστρέφουμε True για επιτυχία
        return False # Επιστρέφουμε False για αποτυχία

    def commit_files(self):
        """Κάνει commit τα αρχεία που βρίσκονται σε staging με το καθορισμένο μήνυμα."""
        if not self.ensure_git_initialized():
            messagebox.showerror("Σφάλμα", "Αποτυχία αρχικοποίησης git repository.")
            return False
        message = self.commit_message.get()
        if not message:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ εισάγετε ένα μήνυμα commit.")
            return False # Επιστρέφουμε False

        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου πρώτα.")
            return False # Επιστρέφουμε False

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
            return False # Επιστρέφουμε False
            
        self.print_to_console(f"\n--- Commit με μήνυμα: '{message}' ---\n")
        if self.run_git_command(["git", "commit", "-m", message]):
            self.print_to_console(f"Τα αρχεία έγιναν commit επιτυχώς με μήνυμα: '{message}'.\n")
            messagebox.showinfo("Επιτυχία", "Τα αρχεία έγιναν commit επιτυχώς!")
            return True # Επιστρέφουμε True
        return False # Επιστρέφουμε False

    def set_remote(self):
        """Ορίζει το remote origin URL."""
        if not self.ensure_git_initialized():
            messagebox.showerror("Σφάλμα", "Αποτυχία αρχικοποίησης git repository.")
            return False
        repo_url = self.repo_url.get()
        if not repo_url:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ εισάγετε το URL του απομακρυσμένου repository.")
            return False # Επιστρέφουμε False
        
        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου πρώτα.")
            return False # Επιστρέφουμε False

        self.print_to_console(f"\n--- Ορισμός remote origin σε: {repo_url} ---\n")

        original_dir = os.getcwd()
        remote_exists = False
        try:
            os.chdir(project_path)
            check_remote_output = subprocess.check_output(["git", "remote"], text=True, encoding='utf-8').strip()
            remote_exists = "origin" in check_remote_output
        except subprocess.CalledProcessError as e:
            self.print_to_console(f"Προειδοποίηση: Δεν είναι έγκυρο Git repository για έλεγχο remote, ή σφάλμα: {e}\n")
            remote_exists = False
        except FileNotFoundError:
            messagebox.showerror("Σφάλμα", "Η εντολή Git δεν βρέθηκε.")
            self.print_to_console("Σφάλμα: Η εντολή Git δεν βρέθηκε.\n")
            return False
        finally:
            os.chdir(original_dir) 

        if remote_exists:
            self.print_to_console("Το remote 'origin' υπάρχει ήδη. Προσπάθεια αφαίρεσης και επαναπροσθήκης...\n")
            if not self.run_git_command(["git", "remote", "remove", "origin"]):
                messagebox.showerror("Σφάλμα Git", "Αποτυχία αφαίρεσης του υπάρχοντος remote 'origin'.")
                return False # Διακοπή αν αποτύχει η αφαίρεση
            self.print_to_console("Το υπάρχον 'origin' αφαιρέθηκε επιτυχώς.\n")
        
        if self.run_git_command(["git", "remote", "add", "origin", repo_url]):
            self.print_to_console("Το remote 'origin' προστέθηκε/επαναπροστέθηκε επιτυχώς.\n")
            messagebox.showinfo("Επιτυχία", "Το remote 'origin' ορίστηκε!")
            return True # Επιστρέφουμε True
        return False # Επιστρέφουμε False

    def push_to_git(self):
        """Κάνει push τις αλλαγές που έγιναν commit στο απομακρυσμένο repository."""
        if not self.ensure_git_initialized():
            messagebox.showerror("Σφάλμα", "Αποτυχία αρχικοποίησης git repository.")
            return False
        self.print_to_console("\n--- Push στο Git repository ---\n")
        
        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου πρώτα.")
            return False # Επιστρέφουμε False

        # Χρησιμοποιούμε το branch από το πεδίο current_branch
        branch_to_push = self.current_branch.get().strip()
        if not branch_to_push:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ εισάγετε το όνομα του branch για push.")
            return False # Επιστρέφουμε False

        self.print_to_console(f"Προσπάθεια push στο branch: {branch_to_push}\n")
        
        if self.run_git_command(["git", "push", "-u", "origin", branch_to_push]):
            self.print_to_console("Επιτυχής push στο Git repository!\n")
            messagebox.showinfo("Επιτυχία", "Το έργο ανέβηκε επιτυχώς στο Git!")
            return True # Επιστρέφουμε True
        return False # Επιστρέφουμε False

    # --- Νέα συνάρτηση για την εκτέλεση όλων των λειτουργιών ---
    def execute_all_git_operations(self):
        self.print_to_console("\n--- Έναρξη Εκτέλεσης Όλων των Λειτουργιών Git ---\n")
        if not self.ensure_git_initialized():
            messagebox.showerror("Σφάλμα", "Αποτυχία αρχικοποίησης git repository.")
            self.print_to_console("Διακόπηκε: Αποτυχία αρχικοποίησης git repository.\n")
            return
        # 0. Προϋποθέσεις
        project_path = self.project_path.get()
        repo_url = self.repo_url.get()
        selected_profile_name = self.selected_profile_name.get()

        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα φάκελο έργου.")
            self.print_to_console("Διακόπηκε: Δεν επιλέχθηκε φάκελος έργου.\n")
            return
        if not repo_url:
            messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε το URL του απομακρυσμένου repository.")
            self.print_to_console("Διακόπηκε: Δεν εισήχθη URL απομακρυσμένου repository.\n")
            return
        if not selected_profile_name or selected_profile_name == "-- Καθόλου Προφίλ --":
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα προφίλ Git από το dropdown.")
            self.print_to_console("Διακόπηκε: Δεν επιλέχθηκε προφίλ Git.\n")
            return

        # Εφαρμόζουμε το επιλεγμένο προφίλ (email, username, default_branch) για το project
        self.print_to_console("Εφαρμογή επιλεγμένου προφίλ...")
        # Η apply_selected_profile() καλείται εδώ, και μέσα της γίνεται και το set του current_branch
        if not self.apply_selected_profile(): 
            messagebox.showerror("Σφάλμα", "Αποτυχία εφαρμογής προφίλ. Διακόπτεται η εκτέλεση.")
            self.print_to_console("Διακόπηκε: Αποτυχία εφαρμογής προφίλ.\n")
            return

        # 1. Αρχικοποίηση Git
        self.print_to_console("\nΒήμα 1/5: Αρχικοποίηση Git...")
        if not self.init_git():
            messagebox.showerror("Σφάλμα", "Βήμα 1: Αποτυχία αρχικοποίησης Git. Διακόπτεται η εκτέλεση.")
            self.print_to_console("Διακόπηκε: Αποτυχία αρχικοποίησης Git.\n")
            return

        # 2. Προσθήκη Όλων των Αρχείων
        self.print_to_console("\nΒήμα 2/5: Προσθήκη όλων των αρχείων...")
        if not self.add_all():
            messagebox.showerror("Σφάλμα", "Βήμα 2: Αποτυχία προσθήκης αρχείων. Διακόπτεται η εκτέλεση.")
            self.print_to_console("Διακόπηκε: Αποτυχία προσθήκης αρχείων.\n")
            return

        # 3. Commit
        self.print_to_console("\nΒήμα 3/5: Δημιουργία Commit...")
        if not self.commit_files():
            messagebox.showerror("Σφάλμα", "Βήμα 3: Αποτυχία Commit. Διακόπτεται η εκτέλεση.")
            self.print_to_console("Διακόπηκε: Αποτυχία Commit.\n")
            return

        # 4. Ορισμός Remote URL
        self.print_to_console("\nΒήμα 4/5: Ορισμός Remote URL...")
        if not self.set_remote():
            messagebox.showerror("Σφάλμα", "Βήμα 4: Αποτυχία ορισμού Remote URL. Διακόπτεται η εκτέλεση.")
            self.print_to_console("Διακόπηκε: Αποτυχία ορισμού Remote URL.\n")
            return

        # 5. Push στο Git
        self.print_to_console("\nΒήμα 5/5: Push στο Git...")
        if not self.push_to_git():
            messagebox.showerror("Σφάλμα", "Βήμα 5: Αποτυχία Push στο Git. Διακόπτεται η εκτέλεση.")
            self.print_to_console("Διακόπηκε: Αποτυχία Push στο Git.\n")
            return

        self.print_to_console("\n--- Όλες οι λειτουργίες ολοκληρώθηκαν επιτυχώς! ---\n")
        messagebox.showinfo("Επιτυχία", "Όλες οι λειτουργίες Git ολοκληρώθηκαν επιτυχώς!")

    def ensure_git_initialized(self):
        """Ελέγχει αν υπάρχει .git στον φάκελο έργου και αν όχι, κάνει αυτόματα git init."""
        project_path = self.project_path.get()
        if not project_path:
            self.print_to_console("Σφάλμα: Δεν έχει επιλεχθεί φάκελος έργου για αρχικοποίηση git.\n")
            return False
        git_folder = os.path.join(project_path, ".git")
        if not os.path.exists(git_folder):
            self.print_to_console("Δεν βρέθηκε git repository. Γίνεται αυτόματη αρχικοποίηση...\n")
            return self.init_git()
        return True


# Εκτέλεση κύριας εφαρμογής
if __name__ == "__main__":
    root = tk.Tk()
    app = GitGUIApp(root)
    root.mainloop()