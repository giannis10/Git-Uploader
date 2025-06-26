import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os

class GitGUIApp:
    def __init__(self, master):
        self.master = master
        master.title("Εύκολος Git Ανεβάτης")
        master.geometry("700x550")
        master.resizable(False, False)

        # Μεταβλητές
        self.project_path = tk.StringVar()
        self.repo_url = tk.StringVar()
        self.commit_message = tk.StringVar(value="Main commit") # Προεπιλεγμένο μήνυμα

        # --- Στοιχεία GUI ---

        # Επιλογή Φακέλου Έργου
        tk.Label(master, text="Φάκελος Έργου:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.project_path, width=50, state="readonly").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(master, text="Αναζήτηση", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # URL Απομακρυσμένου Repository
        tk.Label(master, text="URL Απομακρυσμένου Repo:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.repo_url, width=50).grid(row=1, column=1, padx=5, pady=5)

        # Μήνυμα Commit
        tk.Label(master, text="Μήνυμα Commit:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(master, textvariable=self.commit_message, width=50).grid(row=2, column=1, padx=5, pady=5)

        # Κουμπιά Λειτουργιών Git
        button_frame = tk.Frame(master)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        tk.Button(button_frame, text="1. Αρχικοποίηση Git", command=self.init_git, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="2. Προσθήκη Όλων", command=self.add_all, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="3. Commit", command=self.commit_files, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="4. Ορισμός Remote URL", command=self.set_remote, width=17).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="5. Push στο Git", command=self.push_to_git, width=17).pack(side=tk.LEFT, padx=5)
        
        # Διαχωριστικό
        tk.Frame(master, height=2, bd=1, relief=tk.SUNKEN).grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")

        # Κονσόλα Εξόδου
        tk.Label(master, text="Έξοδος Κονσόλας:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.output_console = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=15, bg="#333", fg="lightgreen", font=("Consolas", 10))
        self.output_console.grid(row=6, column=0, columnspan=3, padx=10, pady=5)
        self.output_console.config(state="disabled") # Κάντε το μόνο για ανάγνωση

        # Κουμπί Εκκαθάρισης Κονσόλας
        tk.Button(master, text="Εκκαθάριση Κονσόλας", command=self.clear_console).grid(row=7, column=0, columnspan=3, pady=5)

        self.print_to_console("Καλώς ήρθατε στον Εύκολο Git Ανεβάτη!\n")
        self.print_to_console("Ακολουθήστε τα βήματα 1-5 για να ανεβάσετε το έργο σας.\n")
        self.print_to_console("Βεβαιωθείτε ότι το Git είναι εγκατεστημένο και διαθέσιμο στο PATH του συστήματός σας.\n")


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
        if not project_path:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε πρώτα ένα φάκελο έργου.")
            return False

        original_dir = os.getcwd()
        try:
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
            
            # Εκτυπώνουμε πάντα το STDERR για debugging, αλλά η επιτυχία κρίνεται από τον returncode
            if stderr:
                self.print_to_console("STDERR:\n" + stderr)

            # Ελέγχουμε τον κωδικό επιστροφής της εντολής Git
            if process.returncode != 0:
                messagebox.showerror("Σφάλμα Git", f"Προέκυψε σφάλμα κατά τη λειτουργία του Git (Κωδικός: {process.returncode}). Ελέγξτε την κονσόλα για λεπτομέρειες.")
                return False # Η εντολή απέτυχε
            
            return True # Η εντολή εκτελέστηκε επιτυχώς (returncode 0)
            
        except FileNotFoundError:
            messagebox.showerror("Σφάλμα", "Η εντομή Git δεν βρέθηκε. Βεβαιωθείτε ότι το Git είναι εγκατεστημένο και στο PATH του συστήματός σας.")
            self.print_to_console("Σφάλμα: Η εντομή Git δεν βρέθηκε. Βεβαιωθείτε ότι το Git είναι εγκατεστημένο.\n")
            return False
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Προέκυψε ένα απροσδόκητο σφάλμα: {e}")
            self.print_to_console(f"Απροσδόκητο σφάλμα: {e}\n")
            return False
        finally:
            # Πάντα επιστρέφουμε στον αρχικό κατάλογο, ανεξάρτητα από το αποτέλεσμα
            os.chdir(original_dir)

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
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε πρώτα ένα φάκελο έργου.")
            return False

        self.print_to_console(f"\n--- Ορισμός remote origin σε: {repo_url} ---\n")

        # Ελέγχουμε αν υπάρχει ήδη origin και το αφαιρούμε αν χρειάζεται
        # Η run_git_command είναι τώρα πιο έξυπνη, αλλά αυτός ο έλεγχος είναι χρήσιμος
        # για την εμπειρία χρήστη
        temp_dir = os.getcwd()
        os.chdir(project_path)
        check_remote_process = subprocess.run(["git", "remote"], capture_output=True, text=True, encoding='utf-8')
        os.chdir(temp_dir) # Πάντα επιστρέφουμε άμεσα

        if "origin" in check_remote_process.stdout:
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
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε πρώτα ένα φάκελο έργου.")
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
            self.print_to_console("Σφάλμα: Η εντολή Git δεν βρέθηκε. Βεβαιωθείτε ότι το Git είναι εγκατεστημένο.\n")
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
            # Αυτό το μήνυμα θα εμφανιστεί μόνο αν το run_git_command επιστρέψει False
            self.print_to_console("Αποτυχία push στο Git repository. Ελέγξτε την κονσόλα για σφάλματα.\n")


# Εκτέλεση κύριας εφαρμογής
if __name__ == "__main__":
    root = tk.Tk()
    app = GitGUIApp(root)
    root.mainloop()