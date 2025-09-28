import os
from bigfix_universal_remote_qna.services.config_initializer import ConfigInitializer
from bigfix_universal_remote_qna.services.security_manager import SecurityManager
from bigfix_universal_remote_qna.services.ssh_manager import SSHManager
from bigfix_universal_remote_qna.services.qna_command_builder import QnACommandBuilder
from bigfix_universal_remote_qna.services.profile_manager import ProfileManager
from bigfix_universal_remote_qna.services.recent_queries_manager import RecentQueriesManager
from bigfix_universal_remote_qna.models.connection_profile import ConnectionProfile
from bigfix_universal_remote_qna.models.os_type import OSType

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
import threading
import tkinter.simpledialog as simpledialog
import tkinter.filedialog as filedialog
import tkinter.scrolledtext as scrolledtext


class QnARemoteDebugger:
    def __init__(self, root):
        self.root = root
        self.root.title("BigFix Universal Remote QnA")
        
        # Initialize configuration
        self.config_manager = ConfigInitializer.initialize_config()
        
        # Initialize managers
        self.security_manager = SecurityManager()
        self.ssh_manager = SSHManager()
        self.command_builder = QnACommandBuilder()
                
        self.profile_manager = ProfileManager(
            self.config_manager, 
            self.security_manager,
            profiles_file=os.path.expanduser("~/.bigfix_profiles.json")
        )
        
        self.queries_manager = RecentQueriesManager(self.config_manager)
        
        # Initialize UI variables
        self._init_ui_variables()
        
        # Apply initial configuration
        self._apply_initial_config()
        
        # Setup UI
        self.setup_ui()
        
        # Load and apply saved settings
        self._load_saved_settings()
    
    def _init_ui_variables(self):
        """Initialize all UI variables"""
        self.profile_var = tk.StringVar()
        self.host_var = tk.StringVar()
        self.port_var = tk.StringVar(value="22")
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.save_passwords_var = tk.BooleanVar()
        self.os_var = tk.StringVar(value=OSType.WINDOWS.value)
        self.qna_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Disconnected")
        self.recent_query_var = tk.StringVar()
    
    def _apply_initial_config(self):
        """Apply initial configuration from ConfigManager"""
        # Set window geometry
        geometry = self.config_manager.get_setting("window_geometry")
        self.root.geometry(geometry)
        
        # Set save passwords preference
        save_passwords = self.config_manager.get_setting("save_passwords")
        self.save_passwords_var.set(save_passwords)
        
        # Set initial QnA path based on default OS
        qna_path = self.config_manager.get_setting("qna_path_windows")
        self.qna_path_var.set(qna_path)
    
    def setup_ui(self):
        """Setup the user interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        self._setup_connection_frame(main_frame)
        self._setup_query_frame(main_frame)
        self._setup_results_frame(main_frame)
        self._setup_status_bar(main_frame)
        
        # Configure grid weights
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=2)
    
    def _setup_connection_frame(self, parent):
        """Setup connection settings frame"""
        conn_frame = ttk.LabelFrame(parent, text="Connection Settings", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        
        # Profile management
        self._add_form_field(conn_frame, 0, "Profile:", self.profile_var, combo=True)
        self.profile_combo = conn_frame.grid_slaves(row=0, column=1)[0]
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_change)
        
        ttk.Button(conn_frame, text="Save Profile", command=self.save_profile).grid(
            row=0, column=2, padx=(5, 5))
        ttk.Button(conn_frame, text="Delete Profile", command=self.delete_profile).grid(
            row=0, column=3, padx=(0, 10))
        
        # Connection fields
        self._add_form_field(conn_frame, 1, "Host(IP):", self.host_var)
        self._add_form_field(conn_frame, 1, "Port:", self.port_var, column=2, width=10)
        self._add_form_field(conn_frame, 2, "Username:", self.username_var)
        self._add_form_field(conn_frame, 2, "Password:", self.password_var, column=2, show="*")
        
        ttk.Checkbutton(conn_frame, text="Save passwords (encrypted)", 
                       variable=self.save_passwords_var, 
                       command=self._save_password_preference).grid(
            row=3, column=1, sticky=tk.W, pady=(5, 0))
        
        # OS and QnA path
        self._add_form_field(conn_frame, 4, "Target OS:", self.os_var, 
                           combo=True, values=[e.value for e in OSType])
        os_combo = conn_frame.grid_slaves(row=4, column=1)[0]
        os_combo.bind('<<ComboboxSelected>>', self.on_os_change)
        
        self._add_form_field(conn_frame, 5, "QnA Path:", self.qna_path_var, columnspan=2)
        
        # Connection buttons
        self._setup_connection_buttons(conn_frame)
    
    def _add_form_field(self, parent, row, label, variable, column=0, width=None, 
                       combo=False, values=None, show=None, columnspan=1):
        """Helper method to add form fields"""
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky=tk.W, padx=(0, 5))
        
        if combo:
            widget = ttk.Combobox(parent, textvariable=variable, values=values or [], 
                                state="readonly" if values else "normal")
        else:
            widget = ttk.Entry(parent, textvariable=variable, show=show, width=width)
        
        widget.grid(row=row, column=column+1, columnspan=columnspan, 
                   sticky=(tk.W, tk.E), padx=(0, 10))
        
        return widget
    
    def _setup_connection_buttons(self, parent):
        """Setup connection control buttons"""
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=(10, 0))
        
        self.connect_btn = ttk.Button(btn_frame, text="Connect", command=self.connect_ssh)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(btn_frame, text="Disconnect", 
                                       command=self.disconnect_ssh, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="Test QnA Path", command=self.test_qna_path).pack(
            side=tk.LEFT, padx=(0, 5))

        self.status_label = ttk.Label(btn_frame, textvariable=self.status_var, foreground="red")
        self.status_label.pack(side=tk.RIGHT)

    def _show_about_dialog(self, event=None):
        """Show about dialog with general information"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About BigFix Universal Remote QnA")
        about_window.geometry("400x250")
        about_window.resizable(False, False)
        
        # Center the about window
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title_label = ttk.Label(main_frame, text="BigFix Universal Remote QnA", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Version
        ttk.Label(main_frame, text="Version 1.0.0", 
                 font=('Arial', 10)).pack(pady=(0, 10))
        
        # Description
        desc_text = ("A cross-platform tool for executing BigFix QnA queries\n"
                    "remotely via SSH on Windows, Linux, and macOS systems.")
        ttk.Label(main_frame, text=desc_text, 
                 font=('Arial', 9), justify=tk.CENTER, wraplength=350).pack(pady=(0, 20))

        # Developer info
        dev_frame = ttk.Frame(main_frame)
        dev_frame.pack(side=tk.BOTTOM, anchor='se', pady=(0, 2), padx=(0, 2), fill=tk.X, expand=False)

        dev_by_label = ttk.Label(dev_frame, text="Developer info", font=('Arial', 8), foreground='blue', cursor='hand2')
        dev_by_label.pack(side=tk.LEFT)
        dev_by_label.bind('<Button-1>', self._show_developer_dialog)

    def _show_developer_dialog(self, event=None):
        """Show developer information dialog"""           
        dev_window = tk.Toplevel(self.root)
        dev_window.title("Developer Information")
        dev_window.geometry("350x150")
        dev_window.resizable(False, False)

        dev_window.transient(self.root)
        dev_window.grab_set()   
 
        dev_frame = ttk.Frame(dev_window, padding="15")
        dev_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(dev_frame, text="Name:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(dev_frame, text="Yashwanth Kumar Bhuvanagiri", font=('Arial', 9)).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        ttk.Label(dev_frame, text="Email:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        email_label = ttk.Label(dev_frame, text="yb91374@gmail.com", 
                               font=('Arial', 9), foreground='blue', cursor='hand2')
        email_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        email_label.bind('<Button-1>', lambda event: self._open_email())

        ttk.Label(dev_frame, text="GitHub:", font=('Arial', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W)
        
        github_label = ttk.Label(dev_frame, text="Yashwanthkumar11/bigfix-universal-remote-qna", 
                                font=('Arial', 9), foreground='blue', cursor='hand2')
        github_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        github_label.bind('<Button-1>', self._open_github)
        
        # Close button
        ttk.Button(dev_frame, text="Close", 
                  command=dev_window.destroy).grid(row=3, column=0, columnspan=2, pady=(10, 0))
    
    def _open_email(self, event=None):
        import webbrowser
        webbrowser.open("https://mail.google.com/mail/?view=cm&fs=1&to=yb91374@gmail.com")

    def _open_github(self, event=None):
        """Open GitHub repository"""
        import webbrowser
        webbrowser.open("https://github.com/Yashwanthkumar11/bigfix-universal-remote-qna")

    def _setup_query_frame(self, parent):
        """Setup query input frame"""
        query_frame = ttk.LabelFrame(parent, text="Relevance Query", padding="5")
        query_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        query_frame.columnconfigure(0, weight=1)
        query_frame.rowconfigure(0, weight=1)
        
        self.query_text = scrolledtext.ScrolledText(query_frame, height=8, width=80)
        self.query_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self._setup_query_buttons(query_frame)
    
    def _setup_query_buttons(self, parent):
        """Setup query control buttons"""
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        buttons = [
            ("Execute Query", self.execute_query),
            ("Clear Query", self.clear_query),
            ("Load Query", self.load_query),
            ("Save Query", self.save_query)
        ]
        
        for text, command in buttons:
            ttk.Button(btn_frame, text=text, command=command).pack(side=tk.LEFT, padx=(0, 5))
        
        # Recent queries
        ttk.Label(btn_frame, text="Recent:").pack(side=tk.LEFT, padx=(10, 5))
        self.recent_combo = ttk.Combobox(btn_frame, textvariable=self.recent_query_var, width=30)
        self.recent_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.recent_combo.bind('<<ComboboxSelected>>', self.load_recent_query)
    
    def _setup_results_frame(self, parent):
        """Setup results display frame"""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="5")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def _setup_status_bar(self, parent):
        """Setup status bar with developer attribution"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # Version info
        ttk.Label(status_frame, text="v1.0.0", 
                 font=('Arial', 8), foreground='gray').grid(row=0, column=1)

        # About link
        about_link = ttk.Label(status_frame, text="About", font=('Arial', 8), foreground='blue', cursor='hand2')
        about_link.grid(row=0, column=2, sticky=tk.E)
        about_link.bind('<Button-1>', self._show_about_dialog)


    def _load_saved_settings(self):
        """Load and apply saved settings"""
        # Update UI dropdowns
        self._update_profiles_dropdown()
        self._update_recent_queries_dropdown()
        
        # Load last used connection
        last_connection_index = self.config_manager.get_setting("last_used_connection_index")
        profiles = self.profile_manager.get_all_profiles()
        
        if profiles and 0 <= last_connection_index < len(profiles):
            profile = profiles[last_connection_index]
            self._load_profile_data(profile)
    
    def _update_profiles_dropdown(self):
        """Update profiles dropdown"""
        profiles = self.profile_manager.get_all_profiles()
        profile_names = [profile.name for profile in profiles]
        self.profile_combo['values'] = profile_names
    
    def _update_recent_queries_dropdown(self):
        """Update recent queries dropdown"""
        recent_queries = self.queries_manager.get_recent_queries()
        self.recent_combo['values'] = recent_queries
    
    def _save_password_preference(self):
        """Save password preference setting"""
        self.config_manager.set_setting("save_passwords", self.save_passwords_var.get())
    
    def _get_qna_path_for_os(self, os_type: str) -> str:
        """Get QnA path for specified OS"""
        setting_key = f"qna_path_{os_type}"
        return self.config_manager.get_setting(setting_key)
    
    def on_os_change(self, event=None):
        """Handle OS selection change"""
        selected_os = self.os_var.get()
        qna_path = self._get_qna_path_for_os(selected_os)
        self.qna_path_var.set(qna_path)
    
    def save_profile(self):
        """Save current connection as profile"""
        host = self.host_var.get().strip()
        username = self.username_var.get().strip()
        
        if not host or not username:
            messagebox.showerror("Error", "Host and username are required")
            return
        
        profile_name = simpledialog.askstring(
            "Profile Name", 
            f"Enter name for profile (default: {username}@{host}):",
            initialvalue=f"{username}@{host}"
        )
        
        if not profile_name:
            return
        
        profile = ConnectionProfile(
            name=profile_name,
            host=host,
            port=int(self.port_var.get()),
            username=username,
            os=self.os_var.get(),
            qna_path=self.qna_path_var.get()
        )
        
        # Handle password encryption
        if self.save_passwords_var.get() and self.password_var.get():
            key = self.security_manager.generate_key(f"{username}@{host}")
            profile.password = self.security_manager.encrypt_password(
                self.password_var.get(), key
            )
        
        if self.profile_manager.save_profile(profile):
            self._update_profiles_dropdown()
            messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully")
    
    def delete_profile(self):
        """Delete selected profile"""
        profile_name = self.profile_var.get()
        if not profile_name:
            messagebox.showerror("Error", "Please select a profile to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete profile '{profile_name}'?"):
            self.profile_manager.delete_profile(profile_name)
            self._update_profiles_dropdown()
            self._clear_connection_fields()
            messagebox.showinfo("Success", f"Profile '{profile_name}' deleted")
    
    def on_profile_change(self, event=None):
        """Handle profile selection change"""
        profile_name = self.profile_var.get()
        profile = self.profile_manager.get_profile_by_name(profile_name)
        
        if profile:
            self._load_profile_data(profile)
            # Save as last used connection
            profiles = self.profile_manager.get_all_profiles()
            for i, p in enumerate(profiles):
                if p.name == profile_name:
                    self.config_manager.set_setting("last_used_connection_index", i)
                    break
    
    def _load_profile_data(self, profile: ConnectionProfile):
        """Load profile data into UI"""
        self.host_var.set(profile.host)
        self.port_var.set(str(profile.port))
        self.username_var.set(profile.username)
        self.os_var.set(profile.os)
        self.qna_path_var.set(profile.qna_path)
        self.profile_var.set(profile.name)
        
        # Decrypt password if available
        if profile.password:
            key = self.security_manager.generate_key(f"{profile.username}@{profile.host}")
            decrypted_password = self.security_manager.decrypt_password(profile.password, key)
            self.password_var.set(decrypted_password)
        else:
            self.password_var.set('')
    
    def _clear_connection_fields(self):
        """Clear all connection fields"""
        for var in [self.profile_var, self.host_var, self.username_var, self.password_var]:
            var.set('')
        self.port_var.set('22')
        self.os_var.set(OSType.WINDOWS.value)
        qna_path = self._get_qna_path_for_os(OSType.WINDOWS.value)
        self.qna_path_var.set(qna_path)
    
    def connect_ssh(self):
        """Establish SSH connection"""
        def connect_thread():
            try:
                profile = ConnectionProfile(
                    name="temp",
                    host=self.host_var.get().strip(),
                    port=int(self.port_var.get()),
                    username=self.username_var.get().strip(),
                    password=self.password_var.get()
                )
                
                if not profile.host or not profile.username or not profile.password:
                    messagebox.showerror("Error", "Please fill in all connection fields")
                    return
                
                self._update_status("Connecting...")
                
                if self.ssh_manager.connect(profile):
                    self._update_status("Connected", "green")
                    self._toggle_connection_buttons(True)
                    self._log_message(f"Successfully connected to {profile.host}")
                
            except Exception as e:
                self._update_status("Connection Failed", "red")
                messagebox.showerror("Connection Error", str(e))
                self._log_message(f"Connection failed: {str(e)}")
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def disconnect_ssh(self):
        """Disconnect SSH connection"""
        self.ssh_manager.disconnect()
        self._update_status("Disconnected", "red")
        self._toggle_connection_buttons(False)
        self._log_message("Disconnected from remote host")
    
    def _update_status(self, status: str, color: str = "black"):
        """Update connection status"""
        self.status_var.set(status)
        if hasattr(self, 'status_label'):
            self.status_label.configure(foreground= color)
        self.root.update()
    
    def _toggle_connection_buttons(self, connected: bool):
        """Toggle connection button states"""
        self.connect_btn.configure(state=tk.DISABLED if connected else tk.NORMAL)
        self.disconnect_btn.configure(state=tk.NORMAL if connected else tk.DISABLED)
    
    def test_qna_path(self):
        """Test if QnA path exists"""
        if not self.ssh_manager.connected:
            messagebox.showerror("Error", "Please connect to a remote machine first")
            return
        
        def test_thread():
            try:
                qna_path = self.qna_path_var.get().strip()
                os_type = self.os_var.get()
                
                if self.ssh_manager.test_file_exists(qna_path, os_type):
                    messagebox.showinfo("Success", f"QnA found at: {qna_path}")
                    self._log_message(f"QnA path verified: {qna_path}")
                else:
                    messagebox.showerror("Error", f"QnA not found at: {qna_path}")
                    self._log_message(f"QnA path not found: {qna_path}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to test QnA path: {str(e)}")
                self._log_message(f"Error testing QnA path: {str(e)}")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def execute_query(self):
        """Execute relevance query"""
        if not self.ssh_manager.connected:
            messagebox.showerror("Error", "Please connect to a remote machine first")
            return
        
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showerror("Error", "Please enter a relevance query")
            return
        
        # Add to recent queries
        self.queries_manager.add_query(query)
        self._update_recent_queries_dropdown()
        
        def execute_thread():
            try:
                self._log_message("Executing query...")
                self._log_message("=" * 50)
                
                qna_path = self.qna_path_var.get().strip()
                os_type = self.os_var.get()
                
                command = self.command_builder.build_command(query, qna_path, os_type)
                result = self.ssh_manager.execute_command(command, timeout=60)
                
                # Display results
                output = f"Query: {query}\n\n"
                output += f"Exit Code: {result['exit_code']}\n\n"
                
                if result['output']:
                    output += f"Output:\n{result['output']}\n"
                
                if result['error']:
                    output += f"Error:\n{result['error']}\n"
                
                self._log_message(output)
                self._log_message("=" * 50)
                
            except Exception as e:
                self._log_message(f"Error executing query: {str(e)}")
        
        threading.Thread(target=execute_thread, daemon=True).start()
    
    def clear_query(self):
        """Clear query text"""
        self.query_text.delete("1.0", tk.END)
    
    def load_query(self):
        """Load query from file"""
        try:
            filename = filedialog.askopenfilename(
                title="Load Query",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.query_text.delete("1.0", tk.END)
                    self.query_text.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load query: {str(e)}")
    
    def save_query(self):
        """Save query to file"""
        try:
            query = self.query_text.get("1.0", tk.END).strip()
            if not query:
                messagebox.showwarning("Warning", "No query to save")
                return
            
            filename = filedialog.asksaveasfilename(
                title="Save Query",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(query)
                messagebox.showinfo("Success", "Query saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save query: {str(e)}")
    
    def load_recent_query(self, event=None):
        """Load selected recent query"""
        query = self.recent_query_var.get()
        if query:
            self.query_text.delete("1.0", tk.END)
            self.query_text.insert("1.0", query)
    
    def _log_message(self, message: str):
        """Add message to results area"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def on_closing(self):
        """Handle application closing"""
        # Save current window geometry
        self.config_manager.set_setting("window_geometry", self.root.geometry())
        
        # Disconnect SSH if connected
        if self.ssh_manager.connected:
            self.ssh_manager.disconnect()
        
        self.root.destroy()