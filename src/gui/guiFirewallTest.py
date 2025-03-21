#!/usr/bin/python

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from tkinter import filedialog
import os
import containers
import json
import re
import threading
import webbrowser
import textwrap

# TODO - Standardize variable and function names - use English names.
# TODO - Leave all print and graphical messages in English - buttons, labels, etc...
# TODO - Refactor the code - remove duplicate code, see what can be improved, perhaps with the concept of object-oriented programming.
# TODO - Remove variables and code that are not being used - there may be useless code, especially since the change from label to treeview.
# TODO - Configuration tab - see if it is necessary and what to put there (e.g., location where rules should be loaded in the container; whether or not to display the container ID column, whether or not to start the servers, list iptables mangle rules, maybe list or not iptables nat or filter rules - now interface list filter and nat rules by default).
# TODO - Create a help for the user.
# TODO - When performing tests, check for errors such as testing a closed port on the server, the interface could warn about this (leave it, but warn).
# TODO - Verify the message flow, such as, it arrived at the server but did not return, indicate this in the interface.
# TODO - Think about how to show the execution logs, which go to the text console, to the interface, this helps a lot in showing problems and the test flow.
# TODO - Think about how to show "packet" details - JSON objects returned by client/server in tests.
# TODO - In the container.py file - when starting a server on a port already in use by another program other than server.py, verify if it can really kill that process.
# TODO - Think about how to access some real services, such as HTTP, SSH, MYSQL, etc., and how to show this in the interface, currently outside of client.py/server.py only ICMP can be accessed externally.
# TODO - Think about tests of malformed packets such as those from nmap or scapy.
# TODO - Suggest tests that may be common in corporate environments.
# TODO - Suggest tests based on the services running in the environment.
# TODO - Suggest tests based on the tests proposed by the user, such as: if they asked host1 to access HTTP on host3, do the opposite as well.
# TODO - Perhaps it would be nice to have options to wait for test success considering DNAT, that is, to have an option that when enabled waits for the flow to go through a DNAT, otherwise the test would be considered failed!
# TODO - The scroll of the firewall tests is not working properly and is cutting off the last column of the tree.
# TODO - Check if scroll is needed in other areas of the program (vertical and horizontal).
# TODO - Is it interesting to have a button to save firewall rules on the host? the user can do ctrl+c and ctrl+v - remembering that the rules are already saved in the container.
# TODO - if only the host or all hosts in the scenario are turned off, there is no problem for the interface, but if GNS3 is turned off and the same scenario is turned on again, the interface becomes inconsistent, even the host update button does not work properly! Also, the rules deployed in the firewall are lost.
# TODO - when saving and opening tests - do not reference the container ID, only the names and perhaps IPs (I think IPs are unavoidable for now), and when the rules are opened, the interface must relate or re-relate the hostname with the container_id, and perhaps the IPs (it would be nice not to relate with the IPs, because in the scenario the user could create or change the hostname to another IP and the test would continue to work).
# TODO - the combobox of "Edit firewall rules on host" should not show multiple lines for the same host (it shows one per host IP), but rather only one name.


class FirewallGUI:
    """
        Class to work with firewall tester interface.
    """

    def __init__(self, root):
        """
            Start firewall tester interface with some variables, methods and create default frames.
        """
        self.root = root
        self.root.title("Firewall Tester")
        self.root.geometry("800x600")

        # Creating Notebook tab
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Criando as abas
        self.firewall_frame = ttk.Frame(self.notebook)
        self.hosts_frame = ttk.Frame(self.notebook)
        self.config_frame = ttk.Frame(self.notebook)
        self.regras_firewall = ttk.Frame(self.notebook)
        self.about_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.firewall_frame, text="Firewall Test")
        self.notebook.add(self.regras_firewall, text="Firewall Rules")
        self.notebook.add(self.hosts_frame, text="Hosts")
        self.notebook.add(self.config_frame, text="Settings")
        self.notebook.add(self.about_frame, text="About")

        # Frame under tabs
        frame_botton = ttk.Frame(self.root)
        frame_botton.pack(side=tk.BOTTOM, pady=6)
        
        # TODO - when updating host data, it may be necessary to change test data, especially container IDs and perhaps host IPs - just as it has to be done when loading tests from a file - think of a single solution for both problems - perhaps user intervention is needed.
        self.button_uptate_host = ttk.Button(frame_botton, text="Update Hosts", command=self.hosts_update)
        self.button_uptate_host.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.button_quit = ttk.Button(frame_botton, text="Exit", command=self.confirm_software_exit)
        self.button_quit.grid(row=0, column=6, padx=10, pady=10, sticky="nsew")
        
        frame_botton.grid_columnconfigure(0, weight=1)
        frame_botton.grid_columnconfigure(1, weight=1)
        frame_botton.grid_columnconfigure(2, weight=1)

        # file name path
        self.save_file_path = None

        # List to store tests
        self.tests = []

        # buttons list from hosts
        self.lista_btn_onOff = []

        # get data from containers and hosts
        self.containers_data = containers.extract_containerid_hostname_ips( )  # get hosts informations

        # creating tabs
        self.create_hosts_tab()
        self.create_firewall_tab()
        self.create_regras_firewall_tab()
        # restart servers on containers/hosts
        self.hosts_start_servers()
        self.create_about_tab()

    def create_about_tab(self):
        """
            Create tab about to present some informations about the software interface like: author, description, licence, etc.
        """
        top_frame = tk.Frame(self.about_frame)
        top_frame.pack(pady=10)

        # Developer Information
        lbl_title = ttk.Label(top_frame, text="About the Software", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=10)

        # Software Description
        description = "This software was developed with the goal of strengthening network security through practical and efficient firewall testing. More than just a testing tool, it stands out as a valuable educational resource, designed to simplify and enhance the learning process about firewalls. Through an intuitive and interactive interface, students can visualize and experiment with the creation and application of firewall rules, making it easier to understand complex concepts and promoting deeper and more effective learning."

        # Create a frame for the description
        description_frame = ttk.Frame(top_frame)
        description_frame.pack(pady=10, padx=20, fill="x") #fill x to ocuupy the entire width.

        # Simulate full justification using textwrap
        wrapped_text = textwrap.fill(description, width=70) #Was increased the width to spread out more

        # Get background color from parent frame
        bg_color = top_frame.cget("background")

        # Use tk.Text for display
        text_widget = tk.Text(description_frame, wrap="word", width=70, height=8, borderwidth=0, highlightthickness=0, background=bg_color) #was increased the height and width
        text_widget.insert("1.0", wrapped_text)
        text_widget.config(state="disabled")  # Make it read-only
        text_widget.pack(pady=10, padx=10, fill="x")

        # Developer
        lbl_developer_name_head = ttk.Label(top_frame, text="Developer:")
        lbl_developer_name_head.pack()
        lbl_developer_name = ttk.Label(top_frame, text=f"Prof. Luiz Arthur Feitosa dos Santos", font=("Arial", 12, "bold"))
        lbl_developer_name.pack()

        # Clickable Email
        #lbl_email_text = ttk.Label(top_frame, text="Email: ")
        #lbl_email_text.pack()

        lbl_email = ttk.Label(top_frame, text=f"luiz.arthur.feitosa.santos@gmail.com\n", foreground="blue", cursor="hand2")
        lbl_email.pack()
        lbl_email.bind("<Button-1>", lambda e: webbrowser.open_new_tab("mailto:luiz.arthur.feitosa.santos@gmail.com"))

        lbl_institution_head = ttk.Label(top_frame, text="Institution:")
        lbl_institution_head.pack()
        lbl_institution = ttk.Label(top_frame, text=f"UTFPR-CM\n", font=("Arial", 12, "bold"))
        lbl_institution.pack()

        # Clickable Project Link
        lbl_project_link_text = ttk.Label(top_frame, text="Project Link: ")
        lbl_project_link_text.pack()

        lbl_project_link = ttk.Label(top_frame, text=f"https://github.com/luizsantos/firewallTester\n", foreground="blue", cursor="hand2")
        lbl_project_link.pack()
        lbl_project_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester"))

        # Clickable License Link
        lbl_license_text = ttk.Label(top_frame, text="License: ")
        lbl_license_text.pack()

        lbl_license = ttk.Label(top_frame, text=f"GNU GPL v3\n", foreground="blue", cursor="hand2")
        lbl_license.pack()
        lbl_license.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.gnu.org/licenses/gpl-3.0.html"))

        # Help Button
        btn_help = ttk.Button(top_frame, text="Help", command=self.open_help)
        btn_help.pack(pady=20)

    
    def open_help(self):
        """
            Open a link in the web browser, to show help content.
        """
        webbrowser.open_new_tab("https://github.com/luizsantos/firewallTester")

    def create_hosts_tab(self):
        """
            Create Hosts tab, show informations about hosts and permit change some configurations like port and start/stop servers.
        """

        self.top_frame = tk.Frame(self.hosts_frame)
        self.top_frame.pack(pady=10)

        ttk.Label(self.top_frame, text="Network Containers Hosts:", font=("Arial", 12)).pack(padx=10)

        # Button to turn on all containers/servers
        ttk.Button(self.top_frame, text="Turn on servers", command=self.hosts_start_servers).pack(side=tk.LEFT, padx=10)

        # Frame for bottom buttons
        self.bottom_frame = tk.Frame(self.hosts_frame)
        self.bottom_frame.pack(pady=10)

        self.hosts_show_host_informations_in_host_tab()

    def create_regras_firewall_tab(self):
        """
            Create firewal rules tab, this permit create, list and edit firewall rules on the hosts.
        """
        # Top frame for title. 
        frame_titulo = tk.Frame(self.regras_firewall)
        frame_titulo.pack(fill=tk.X)

        ttk.Label(frame_titulo, text="Edit firewall rules on host:", font=("Arial", 12, "bold")).pack(padx=10)
        self.combobox_host_regra_firewall = ttk.Combobox(frame_titulo, values=self.hosts_display, width=25, state="readonly", style="TCombobox")
        self.combobox_host_regra_firewall.pack(pady=10)
        #self.combobox_host_regra_firewall.current(0)
        self.combobox_host_regra_firewall.set("")

        self.combobox_host_regra_firewall.bind("<<ComboboxSelected>>", self.selected_host_on_combobox_tab_firewall_rules)

        #label_titulo = tk.Label(frame_titulo, text="Editar regras de firewall", font=("Arial", 12, "bold"))
        #label_titulo.pack(pady=5)

        # Creating frame for the labels
        frame_regras = ttk.LabelFrame(self.regras_firewall, text="Rules to be applied to the firewall")
        frame_regras.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.text_regras = tk.Text(frame_regras, wrap=tk.NONE, height=10, undo=True)
        self.text_regras.grid(row=0, column=0, sticky="nsew")

        scroll_y_regras = tk.Scrollbar(frame_regras, orient=tk.VERTICAL, command=self.text_regras.yview)
        scroll_y_regras.grid(row=0, column=1, sticky="ns")
        self.text_regras.config(yscrollcommand=scroll_y_regras.set)

        scroll_x_regras = tk.Scrollbar(frame_regras, orient=tk.HORIZONTAL, command=self.text_regras.xview)
        scroll_x_regras.grid(row=1, column=0, sticky="ew")
        self.text_regras.config(xscrollcommand=scroll_x_regras.set)

        self.reset_firewall = tk.IntVar()
        checkbtn_zerar_regras = tk.Checkbutton(frame_regras, text="Automatically reset firewall rules – this should be in your script, but you can do it here.", variable=self.reset_firewall)
        checkbtn_zerar_regras.grid(row=2, column=0, sticky="w")

        frame_regras.grid_columnconfigure(0, weight=1)
        frame_regras.grid_rowconfigure(0, weight=1)

        # Creating frame for the active rules
        frame_ativas = ttk.LabelFrame(self.regras_firewall, text="Output ")
        frame_ativas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        #frame_ativas.pack_forget()  # Hide on the start

        def toggle_frame_output_on_rule_tab():
            """
                Change frame output to hide or show output text in firewall rule tab.
            """
            if frame_ativas.winfo_ismapped():
                frame_ativas.pack_forget()
                btn_ver_ativas.config(text="Show output")
            else:
                frame_ativas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                btn_ver_ativas.config(text="Hide output")

        def select_all_text_on_rules_text(event):
            """
                Selecte every texto inside texto firewall rule - for use with Ctrl+A
            """
            event.widget.tag_add("sel", "1.0", "end")
            return "break"

        self.text_ativas = tk.Text(frame_ativas, wrap=tk.NONE, height=10)
        self.text_ativas.grid(row=0, column=0, sticky="nsew")
        self.text_ativas.bind("<Control-a>", select_all_text_on_rules_text)

        self.text_regras.bind("<Control-a>", select_all_text_on_rules_text)

        scroll_y_ativas = tk.Scrollbar(frame_ativas, orient=tk.VERTICAL, command=self.text_ativas.yview)
        scroll_y_ativas.grid(row=0, column=1, sticky="ns")
        self.text_ativas.config(yscrollcommand=scroll_y_ativas.set)
        self.text_ativas.config(state=tk.NORMAL) # I don't know why, but if you don't activate and deactivate text_actives, select all doesn't work in text_rules
        #self.text_ativas.config(state=tk.DISABLED)

        scroll_x_ativas = tk.Scrollbar(frame_ativas, orient=tk.HORIZONTAL, command=self.text_ativas.xview)
        scroll_x_ativas.grid(row=1, column=0, sticky="ew")
        self.text_ativas.config(xscrollcommand=scroll_x_ativas.set)

        frame_ativas.grid_columnconfigure(0, weight=1)
        frame_ativas.grid_rowconfigure(0, weight=1)
        self.btn_listar_regras_firewall = tk.Button(frame_ativas, text="List firewall rules", command=self.list_firewall_rules_on_output)
        self.btn_listar_regras_firewall.grid(row=2, column=0)
        self.btn_listar_regras_firewall.config(state="disabled")

        # Creating buttons
        frame_botoes = tk.Frame(self.regras_firewall)
        frame_botoes.pack(pady=10)

        self.btn_carregar = tk.Button(frame_botoes, text="Retrieve firewall rules", command=self.load_firewall_rules)
        self.btn_carregar.pack(side=tk.LEFT, padx=10)
        self.btn_carregar.config(state="disabled")

        self.btn_aplicar = tk.Button(frame_botoes, text="Deploy firewall rules", command=self.apply_firewall_rules)
        self.btn_aplicar.pack(side=tk.LEFT, padx=10)
        self.btn_aplicar.config(state="disable")

        #self.btn_zerar = tk.Button(frame_botoes, text="Zerar Regras no firewall", command=self.zerar_regras_firewall)
        #self.btn_zerar.pack(side=tk.LEFT, padx=10)
        #self.btn_zerar.config(state="disable")

        btn_ver_ativas = tk.Button(frame_botoes, text="Hide output", command=toggle_frame_output_on_rule_tab)
        btn_ver_ativas.pack(side=tk.RIGHT, padx=10)

    def selected_host_on_combobox_tab_firewall_rules(self, src_ip):
        """
            Treats the selected host in the combobox
        """
        #print("selected_host_on_combobox_tab_firewall_rules")
        selected_index = self.combobox_host_regra_firewall.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = [self.containers_data[selected_index]["id"], self.containers_data[selected_index]["hostname"]]
            #print(f"container_data selected_index{selected_index} -  {self.containers_data[selected_index]}")
        else:
            container_id = "N/A"  # Caso nenhum container seja selecionado
        print(container_id)
        self.btn_carregar.config(state="normal")
        self.btn_aplicar.config(state="normal")
        self.btn_listar_regras_firewall.config(state="normal")
        #self.btn_zerar.config(state="normal")
        self.container_id_host_regras_firewall=container_id

    def list_firewall_rules_on_output(self):
        """
            List active firewall rules on the host and display in the output text on firewall rules tab. The container/host is selected in the combobox on the firewall rules tab.
        """
        print(f"List firewall rules for host {self.container_id_host_regras_firewall[1]}")
        
        self.text_ativas.delete(1.0, tk.END)

        command = ["docker", "exec", self.container_id_host_regras_firewall[0], "iptables", "-L", "-n", "-t", "nat"]
        result = containers.run_command(command)
        self.text_ativas.insert(tk.END, f"\n* Result of the command iptables -t nat -L on host {self.container_id_host_regras_firewall[1]}:\n\n")
        self.text_ativas.insert(tk.END, result.stdout)
        
        command = ["docker", "exec", self.container_id_host_regras_firewall[0], "iptables", "-L", "-n"]
        result = containers.run_command(command)
        self.text_ativas.insert(tk.END, f"\n* Result of the command iptables -L on host {self.container_id_host_regras_firewall[1]}:\n\n")
        self.text_ativas.insert(tk.END, result.stdout)

        self.text_ativas.see(tk.END) # rola o scroll para o final, para ver o texto mais recente!
        

    def load_firewall_rules(self):
        """
            Load firewall rules into container/host, this rules are present in the firewall rules texto component in the firewall rules tab. The container/host is selected in the combobox on the firewall rules tab.
        """
        print(f"Load firewall rules from hos {self.container_id_host_regras_firewall[1]}")

        resposta = messagebox.askyesno("Confirmation","This will overwrite the existing rules in the interface. Are you sure you want to continue?")
        # TODO - in UTPFR there was a problem when copying the file from the firewall to the container, it said it copied but didn't copy anything, it only copied when the file was touched - see this.
        if resposta:
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "cat", "/etc/firewall.sh"]
            result = containers.run_command(command)
            self.text_regras.delete(1.0, tk.END)
            self.text_regras.insert(tk.END, result.stdout)

    # TODO - would it be good to have a button to reset the firewall rules?

    def sento_to_host_file_to_execute_firewall_rules(self, file_rules, reset): # se for reset indica que o caminho é o arquivo de reset, caso contrário são regras
        """
            Send to save in the container/host the firewall rules in the firewall interface (tab firewall rules). The container/host is selected in the combobox on the firewall rules tab.

            Args:
                file_rules (string) - source file.
                reset - indicate if the firewall rules will be reseted or not by the interface.  If it is reset it indicates that the path is the reset file, otherwise it is rules.

        """
        print(f"Send and execute firewall rules on host {self.container_id_host_regras_firewall[1]}")
        
        if reset!=None:
            containers.copy_host2container(self.container_id_host_regras_firewall[0], file_rules, "/etc/firewall_reset.sh")
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "sh", "/etc/firewall_reset.sh"]
        else:
            containers.copy_host2container(self.container_id_host_regras_firewall[0], file_rules, "/etc/firewall.sh")
            command = ["docker", "exec", self.container_id_host_regras_firewall[0], "sh", "/etc/firewall.sh"]

        result = containers.run_command(command)

        self.text_ativas.delete(1.0, tk.END)
        if result.stderr:
            self.text_ativas.delete(1.0, tk.END)
            self.text_ativas.insert(tk.END, f"\n* Error applying firewall rules - check if there is something wrong with the rules on host {self.container_id_host_regras_firewall[1]}:\n\n")
            self.text_ativas.insert(tk.END, result.stderr)
            self.text_ativas.see(tk.END) # scroll to the end to see the most recent text!
            messagebox.showinfo("Warning", "Something went wrong while executing the rules, check the output!")
        else:
            self.list_firewall_rules_on_output()
            self.text_ativas.insert(tk.END, f"\n* Firewall status on host {self.container_id_host_regras_firewall[1]} after rules have been applied\n\n")
            self.text_ativas.see(tk.END) # scroll to the end to see the most recent text!


    def apply_firewall_rules(self):
        """
            Apply/execute rules firewall rules on host/container selected in the combobox on the firewall rules tab.
        """
        print(f"Apply rules on the firewall of host {self.container_id_host_regras_firewall[1]}")
        regras = self.text_regras.get("1.0", tk.END)
        file_rules="tmp/regras.sh"
        with open(file_rules, "w", encoding="utf-8") as arquivo:
            arquivo.write(regras)
        print(f"Rules saved in the file {file_rules}")
        if self.reset_firewall.get() == 1: # If the checkbox is checked, first reset the firewall, then apply the rules.
            self.sento_to_host_file_to_execute_firewall_rules("tmp/reset_firewall.sh", 1)
        
        self.sento_to_host_file_to_execute_firewall_rules(file_rules, None)
        
        if self.reset_firewall.get() == 1:
            self.text_ativas.insert(tk.END, f"\n>>Warning!<< The firewall rules of host {self.container_id_host_regras_firewall[1]} were reset via the interface, but this SHOULD be in your firewall commands because firewalls do not reset automatically in real life!\n\n")
            self.text_ativas.see(tk.END) # scroll to the end to see the most recent text!

    def reset_firewall_rules(self):
        """
            Resets the firewall rules for the host/container selected in the combobox on the firewall rules tab.
        """
        print(f"Reset firewall rules on host {self.container_id_host_regras_firewall[1]}")
        resposta = messagebox.askyesno("Warning","This action of resetting firewall rules does not exist by default, meaning this should be handled in your firewall rules. Are you sure you want to continue?")
        if resposta:
            self.sento_to_host_file_to_execute_firewall_rules("tmp/reset_firewall.sh", 1)

    # def selecionar_tudo(self, event=None):
    #     """Seleciona todo o texto."""
    #     self.text.tag_add("sel", "1.0", "end")
    #     return "break"  # Impede o comportamento padrão do atalho

    def edit_host_ports(self, container_id, hostname):
        """
            Opens a new window to edit host ports in the hosts tab.

            Args:
                container_id: Container ID.
                hostname: Hostname or container.
        """
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Ports for Container {container_id} - {hostname}:")
        popup.geometry("400x300")  

        portas = containers.get_port_from_container(container_id)
    
        ttk.Label(popup, text=f"Opened Ports from {hostname}", font=("Arial", 10)).pack(pady=5)

        # Create a Treeview to show network ports.
        colunas = ("Protocolo", "Porta")
        tabela_portas = ttk.Treeview(popup, columns=colunas, show="headings", selectmode="browse")
        tabela_portas.heading("Protocolo", text="Protocol")
        tabela_portas.heading("Porta", text="Port")
        tabela_portas.column("Protocolo", width=150, anchor=tk.CENTER)
        tabela_portas.column("Porta", width=100, anchor=tk.CENTER)
        tabela_portas.pack(pady=10)

        # Populate the Treeview with existing ports
        for protocolo, porta in portas:
            tabela_portas.insert("", tk.END, values=(protocolo, porta))

        # Create a frame to buttons
        frame_botoes = ttk.Frame(popup)
        frame_botoes.pack(pady=10)

        # Button to add line/port
        botao_adicionar = ttk.Button(frame_botoes, text="Add Port", command=lambda: self.add_line_treeview_host(tabela_portas))
        botao_adicionar.pack(side=tk.LEFT, padx=5)

        # Button to remove a line/port
        botao_remover = ttk.Button(frame_botoes, text="Delete Port ", command=lambda: self.delete_line_treeview_host(tabela_portas))
        botao_remover.pack(side=tk.LEFT, padx=5)

        ttk.Button(popup, text="Reload Ports", command=lambda: self.salvar_portas_em_arquivo(container_id, tabela_portas)).pack(pady=10)

        
    def add_line_treeview_host(self, ports_list):
        """
            Open a new window to add a port in a Treeview

            Args:
                ports_list: List of network ports.

        """
        popup = tk.Toplevel()
        popup.title("Add Port")
        popup.geometry("300x150")

        
        def add_port_on_host():
            """
                Validate and add the port.
            """
            protocolo = combo_protocolo.get().strip().upper()
            porta = entry_porta.get().strip()

            # Validate protocol
            if protocolo not in ["TCP", "UDP"]:
                messagebox.showerror("Error", "Invalid protocol! Choose TCP or UDP.")
                return

            # Validate port
            try:
                porta = int(porta)
                if porta < 1 or porta > 65535:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid port! Must be a number between 0 and 65535.")
                return

            # Checks if the protocol/port combination already exists in the table
            for linha in ports_list.get_children():
                valores = ports_list.item(linha, "values")
                if valores[0].upper() == protocolo and valores[1] == str(porta):
                    messagebox.showerror("Error", f"Port {porta}/{protocolo} already exists in the table!")
                    return

            # Add new port in the Treeview
            ports_list.insert("", tk.END, values=(protocolo, porta))
            popup.destroy()  # Close popup

        # Fields to select the protocol
        ttk.Label(popup, text="Protocol:").pack(pady=5)
        combo_protocolo = ttk.Combobox(popup, values=["TCP", "UDP"], state="readonly")
        combo_protocolo.set("TCP")  # Default value
        combo_protocolo.pack(pady=5)

        # Field to add port
        ttk.Label(popup, text="Port:").pack(pady=5)
        entry_porta = ttk.Entry(popup)
        entry_porta.pack(pady=5)

        # Button to add port
        ttk.Button(popup, text="Add", command=add_port_on_host).pack(pady=10)

    # Função para remover a linha selecionada
    def delete_line_treeview_host(self, ports_list):
        """
            Remove line/port from a host.
            
            Args:
                ports_list: List of network ports.
        """
        print("Delete")
        selecionado = ports_list.selection()
        if selecionado:  # Verifica se há algo selecionado
            ports_list.delete(selecionado)

    def salvar_portas_em_arquivo(self, containerId, ports_list, file_name="tmp_conf/portas.conf"):
        """
            Saves the ports and protocols of the Treeview in a file, in the format "port/protocol".

            Args:
                ports_table: The Treeview containing the columns "Protocol" and "Port".
                file_name: Name of the file where the data will be saved.
        """
        try:
            with open(file_name, "w") as arquivo:
                # Iterate through all rows of the Treeview
                for linha in ports_list.get_children():
                    # Get the line values (protocol and port)
                    valores = ports_list.item(linha, "values")
                    if len(valores) == 2:  # Check if there are two values ​​(protocol and port)
                        protocolo, porta = valores
                        # write in the file in the format "prot/protocol"
                        arquivo.write(f"{porta}/{protocolo}\n")
            print(f"Ports successfully saved in file {file_name}!")
        except Exception as e:
            print(f"Error saving ports: {e}")
        
        # reload the ports in the container, starting all services on each port.
        self.reload_ports(containerId, file_name)
        # restart server
        containers.start_server(containerId)

    def reload_ports(self, container_id, file_name):
        """
            Reload service ports in the container/host. It's made copying the file in the interface to the container.
            
            Args:
                container_id: container ID.
                file_name: File name.
        """
        print(f"Reload ports from {container_id}")

        containers.copy_ports2server(container_id, file_name)

    def create_firewall_tab(self):
        """
            Create the firewall tests tab.
        """
        ttk.Label(self.firewall_frame, text="Firewall Test", font=("Arial", 12)).pack(pady=10)

        # Frame for input fields
        frame_entrada = ttk.Frame(self.firewall_frame)
        #frame_entrada.pack(fill="x", padx=10, pady=5)
        frame_entrada.pack(pady=10)

        # List values in the Combobox (hostname + IP)
        if self.containers_data:
            self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        else: # If there are no elements it displays a message.
            self.hosts_display = ["HOSTS (0.0.0.0)", "HOSTS (0.0.0.0)"]
            messagebox.showerror("Warning", "Something seems to be wrong! \n Is GNS3 or the hosts turned on?")
        # Sort the list of hosts in ascending order.

        protocols = ["TCP", "UDP", "ICMP"]

        # setting style - so readonly doesn't turn gray
        style = ttk.Style()
        style.map("TCombobox", fieldbackground=[("readonly", "white")])
        # background color of the selected line - so as not to cover the test color


        # Inputs components
        ttk.Label(frame_entrada, text="Source IP:").grid(row=0, column=0)
        self.src_ip = ttk.Combobox(frame_entrada, values=self.hosts_display, width=25, state="readonly", style="TCombobox")
        self.src_ip.current(0)
        self.src_ip.grid(row=1, column=0)


        ttk.Label(frame_entrada, text="Destination IP:").grid(row=0, column=1)
        self.dst_ip = ttk.Combobox(frame_entrada, values=self.hosts_display, width=25)
        if len(self.containers_data) > 1: # checks if there is more than one element in the host list, if there isn't, you can't set the second one as default.
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

        self.dst_ip.grid(row=1, column=1)
        # Binds the selection event
        self.dst_ip["state"] = "normal"

        ttk.Label(frame_entrada, text="Protocol:").grid(row=0, column=2)
        self.protocol = ttk.Combobox(frame_entrada, values=protocols, width=6, state="readonly", style="TCombobox")
        self.protocol.current(0)
        self.protocol.grid(row=1, column=2)

        ttk.Label(frame_entrada, text="Src Port:").grid(row=0, column=3)
        self.src_port = ttk.Entry(frame_entrada, width=11)
        self.src_port.insert(0, "*")
        self.src_port.config(state="disabled")
        self.src_port.grid(row=1, column=3)

        ttk.Label(frame_entrada, text="Dst Port:").grid(row=0, column=4)
        self.dst_port = ttk.Entry(frame_entrada, width=11)
        self.dst_port.insert(0, "80")
        self.dst_port.grid(row=1, column=4)

        ttk.Label(frame_entrada, text="Expected success?").grid(row=0, column=5)
        self.expected = tk.StringVar(value="yes")
        ttk.Radiobutton(frame_entrada, text="Yes", variable=self.expected, value="yes").grid(row=1, column=5)
        ttk.Radiobutton(frame_entrada, text="No", variable=self.expected, value="no").grid(row=1, column=6)

        # Frame to display added tests
        self.tests_frame = ttk.Frame(self.firewall_frame)
        self.tests_frame.pack(fill="x", padx=10, pady=10)

        # Intermediate frame to center the buttons
        self.button_frame = tk.Frame(self.tests_frame)
        self.button_frame.pack(pady=10)  # Centraliza verticalmente

        button_size=15
        # Creating and adding buttons inside the intermediate frame
        self.button_tree_add = tk.Button(self.button_frame, text="Add", command=self.firewall_test_tree_add_line_test, width=button_size, underline=0)
        self.button_tree_add.pack(side="left", padx=5)
        self.root.bind("<Alt-a>", lambda event: self.firewall_test_tree_add_line_test())

        self.button_tree_edit = tk.Button(self.button_frame, text="Edit", command=self.firewall_test_tree_edit_line_test, width=button_size, underline=0)
        self.button_tree_edit.pack(side="left", padx=5)
        # # TODO - you have to think about when to enable and disable binds, because the way it is it works everywhere!
        #self.root.bind("<Alt-e>", lambda event: self.edit_entry())

        self.button_tree_del = tk.Button(self.button_frame, text="Delete", command=self.firewall_test_tree_delete_line_test, width=button_size, underline=0)
        self.button_tree_del.pack(side="left", padx=5)
        #self.root.bind("<Alt-d>", lambda event: self.delete_entry())

        self.button_tree_test = tk.Button(self.button_frame, text="Test Line", command=self.firewall_tests_run_test_line, width=button_size, underline=8)
        self.button_tree_test.pack(side="left", padx=5)
        #self.root.bind("<Alt-l>", lambda event: self.testar_linha_tree())

        self.button_tree_test_all = tk.Button(self.button_frame, text="Test All", command=self.firewall_tests_popup_for_run_all_tests_using_threads, width=button_size, underline=0)
        self.button_tree_test_all.pack(side="left", padx=5)
        #self.root.bind("<Alt-l>", lambda event: self.executar_todos_testes())


        # Frame to display the tests added in the treeview
        self.tests_frame_Tree = ttk.Frame(self.firewall_frame)
        self.tests_frame_Tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.hidden_data = {}  # Dictionary to store Container ID associated with Test ID
        self.entries = []
        visible_fields = ["#", "Container ID", "Source", "Destination", "Protocol", "Source Port", "Destination Port", "Expected", "Result", "flow", "data"]
        self.tree = ttk.Treeview(self.tests_frame_Tree, columns=visible_fields, show="headings")

        font = ("TkDefaultFont", 10)
        tk_font = tk.font.Font(font=font)

        self.tree.heading("#", text="#")
        self.tree.column("#", width=30, anchor="e", stretch=False)

        self.colunaContainerID=50 # leave it at zero for this column to disappear.
        self.tree.heading("Container ID", text="Container ID")
        self.tree.column("Container ID", width=self.colunaContainerID, stretch=False)

        self.tree.heading("Source", text="Source")
        self.tree.column("Source", width=250, stretch=False)

        self.tree.heading("Destination", text="Destination")
        self.tree.column("Destination", width=250, stretch=False)

        self.tree.heading("Protocol", text="Protocol")
        self.tree.column("Protocol", width=80, anchor="center", stretch=False)

        self.tree.heading("Source Port", text="Src Port")
        self.tree.column("Source Port", width=80, anchor="center", stretch=False)

        self.tree.heading("Destination Port", text="Dst Port")
        self.tree.column("Destination Port", width=80, anchor="center", stretch=False)

        self.tree.heading("Expected", text="Expected")
        self.tree.column("Expected", width=80, anchor="center", stretch=False)

        self.tree.heading("Result", text="Result")
        self.tree.column("Result", width=80, anchor="w", stretch=False)

        self.tree.heading("flow", text="Network Flow")
        self.tree.column("flow", width=200, anchor="w", stretch=False)

        self.tree.heading("data", text="Network Data")
        self.tree.column("data", minwidth=100, width=200, anchor="w", stretch=True)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # TODO - scroll is not adjusting when data exceeds the window size!
        scroll_tree = tk.Scrollbar(self.tests_frame_Tree, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=scroll_tree.set)
        scroll_tree.pack(side="bottom", fill="x")

        # Color definition
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.map("Treeview", background=[("selected", "#4a90e2")])
        self.tree.tag_configure("yes", background="lightgreen")
        self.tree.tag_configure("yesFail", background="lightblue")
        self.tree.tag_configure("no", background="salmon")
        self.tree.tag_configure("error", background="yellow")
        #self.tree.tag_configure("nat", background="lightblue")

        self.tree.bind("<<TreeviewSelect>>", self.firewall_test_tree_select_line_test)
        self.tree.bind("<Double-1>", self.firewall_test_tree_double_click_line_test)
        self.tree.bind('<Escape>', self.firewall_test_tree_select_line_test)

        btn_frame = tk.Frame(root)
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.button_tree_edit.config(state="disabled")
        self.button_tree_del.config(state="disabled")
        self.button_tree_test.config(state="disabled")
        if not self.tree.get_children():
            self.button_tree_test_all.config(state="disabled")

        # Frame Legend
        self.frame_legenda_testes = ttk.LabelFrame(self.firewall_frame, text="Legenda")
        self.frame_legenda_testes.pack(side="bottom", fill="x", padx=20, pady=15)
        self.frame_legenda_testes.pack_propagate(False)
        self.frame_legenda_testes.config(width=700, height=50)

        tk.Label(self.frame_legenda_testes, bg="lightgreen", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Test successfully completed - net flow allowed.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_legenda_testes, bg="lightblue", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Test successfully completed - net flow blocked.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_legenda_testes, bg="red", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Test failed.", font=("Arial", 10)).pack(side="left")

        tk.Label(self.frame_legenda_testes, bg="yellow", width=2, height=1, font=("Arial", 6)).pack(side="left", padx=5)
        tk.Label(self.frame_legenda_testes, text="Error (e.g., error in IP, GW, DNS, Server)", font=("Arial", 10)).pack(side="left")

        self.frame_botoes_salvar_testes = ttk.Frame(self.firewall_frame)
        self.frame_botoes_salvar_testes.pack(pady=10)

        self.button_save_tests = ttk.Button(self.frame_botoes_salvar_testes, text="Save Tests", command=self.firewall_tests_save_tests)
        self.button_save_tests.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.button_save_tests_as = ttk.Button(self.frame_botoes_salvar_testes, text="Save Tests As", command=self.firewall_tests_save_tests_as)
        self.button_save_tests_as.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        self.button_load_tests = ttk.Button(self.frame_botoes_salvar_testes, text="Open Tests", command=self.firewall_tests_open_test_file)
        self.button_load_tests.grid(row=0, column=5, padx=10, pady=10, sticky="nsew")

    def firewall_test_tree_select_line_test(self, event):
        """
            Method executed when a row of the firewall test table is executed (on tab firewall test ).
        """
        print("firewall_test_tree_select_line")
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            if item_values:
                #print(f"{item_values}")
                
                self.src_ip.set(item_values[2])

                self.dst_ip.delete(0, tk.END)
                self.dst_ip.insert(0, item_values[3])

                self.protocol.set(item_values[4])

                self.src_port.delete(0, tk.END)
                self.src_port.insert(0, item_values[5])

                self.dst_port.delete(0, tk.END)
                self.dst_port.insert(0, item_values[6])

                self.expected.set(item_values[7])

        if not self.tree.selection():
            self.button_tree_test.config(state="disabled")
        else:
            self.button_tree_test.config(state="normal")
            self.button_tree_test_all.config(state="normal")

        self.button_tree_add.config(state="normal")
        self.button_tree_edit.config(state="disable")
        self.button_tree_del.config(state="disable")
    
    def firewall_test_tree_double_click_line_test(self, event):
        """
            Treat double click in firewall teste tree
        """
        self.firewall_test_tree_select_line_test(event)
        self.firewall_tests_buttons_set_editing_state()


    def firewall_test_tree_add_line_test(self):
        """
            Add a line/test on treeview firewall tests.
        """
        print("add_line_on_tree_test_firewall")
        
        src_ip = self.src_ip.get()
        dst_ip = self.dst_ip.get()
        protocol = self.protocol.get()
        src_port = self.src_port.get()
        dst_port = self.dst_port.get()
        expected = self.expected.get()

        if self.firewall_tests_validate_entrys() != 0: return # test values

        # Gets the ID of the container selected in the Combobox
        selected_index = self.src_ip.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = self.containers_data[selected_index]["id"]
            print(f"container_data selected_index{selected_index} -  {self.containers_data[selected_index]}")
        else:
            container_id = "N/A"  # If no container is selected
        
        row_index = len(self.tree.get_children()) + 1 # tree line index

        values = [src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        for item in self.tree.get_children(): # avoid duplicate testing
            existing_values = self.tree.item(item, "values")
            #print(f"Values\n{values}\n{existing_values[2:]}")
            if tuple(values) == existing_values[2:]:
                #print(f"egual values - \n{values}\n{existing_values}")
                messagebox.showwarning("Warning", "This entry already exists in the table!")
                return

        values=[]
        self.tree.insert("", "end", values=[row_index, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "])
        self.tree.column("Container ID", width=self.colunaContainerID, stretch=False)
        
        self.firewall_tests_buttons_set_normal_state()

    def firewall_test_tree_edit_line_test(self):
        """
            Edit a row/test of an existing item/test in the firewall test Treeview. The test to be edited is the one currently selected in the treeview.
        """
        selected_item = self.tree.selection()
        print(f"Selected item {selected_item}")
        if not selected_item:
            messagebox.showwarning("Warning", "Select an item to edit!")
            return
        
        src_ip = self.src_ip.get()
        dst_ip = self.dst_ip.get()
        protocol = self.protocol.get()
        src_port = self.src_port.get()
        dst_port = self.dst_port.get()
        expected = self.expected.get()

        if self.firewall_tests_validate_entrys() != 0: return # Test values

        values = [src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        for item in self.tree.get_children(): # avoid duplicate TODO testing - put this in a method as it is duplicated in the code!
            existing_values = self.tree.item(item, "values")
            if tuple(values) == existing_values[2:]:
                messagebox.showwarning("Warning", "This entry already exists in the table!")
                return

        # Gets the ID of the container selected in the Combobox
        selected_index = self.src_ip.current()
        if selected_index >= 0 and selected_index < len(self.containers_data):
            container_id = self.containers_data[selected_index]["id"]
        else:
            container_id = "N/A"  # If no container is selected
        
        values=[self.tree.item(selected_item, "values")[0], container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, "-", " ", " "]

        self.tree.item(selected_item, values=values)
        self.tree.item(selected_item, tags="")  # return the color to default
        

        self.firewall_tests_buttons_set_normal_state()

    def firewall_tests_buttons_set_normal_state(self):
        """
            Defines the state of the firewall test buttons when adding a line/test. This is the normal state when using the Estes interface (startup state).
        """
        self.tree.selection_set(())
        self.button_tree_add.config(state="normal")
        self.button_tree_edit.config(state="disable")
        self.button_tree_del.config(state="disable")
        self.button_tree_test.config(state="disabled")
        self.button_tree_edit.config(text="Editar")
        if not self.tree.get_children():
            self.button_tree_test_all.config(state="disabled")
        else:
            self.button_tree_test_all.config(state="normal")
        
    def firewall_tests_buttons_set_editing_state(self):
        """
            Defines the state of the firewall test buttons when editing a line/test. 
            State used to prevent the user from running a test while the rule is malformed (under editing or deletion)
        """
        self.button_tree_edit.config(state="normal")
        self.button_tree_del.config(state="normal")
        self.button_tree_add.config(state="disabled")
        self.button_tree_test.config(state="disabled")
        self.button_tree_test_all.config(state="disabled")
        self.button_tree_edit.config(text="Save Edit")

    def firewall_test_tree_delete_line_test(self): # TODO - renumber lines when removing a test
        """
            Delete a row/test of an existing item/test in the firewall test Treeview. The test to be deleted is the one currently selected in the treeview.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select an item to delete!")
            return
        self.tree.delete(selected_item)

        self.firewall_tests_buttons_set_normal_state() 

    def validate_ip_or_domain(self, ip_or_domain):
        """
            Validate IP or domain. Method used, for example, to validate whether an IP or domain chosen or entered by the user is valid for test processing. Validate only IPv4 address not IPv6.

            Arg:
                ip_or_domain: IP or Domain to be validate.
        """
        # Regex to IP (IPv4)
        regex_ip = r'^\d+\.\d+\.\d+\.\d+$'
        
        # Regex do domain (ex: google.com, www.example.com)
        regex_dominio = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(regex_ip, ip_or_domain):
            return True
        elif re.match(regex_dominio, ip_or_domain):
            return True
        else:
            return False
    
    def firewall_tests_validate_entrys(self):
        """
            Checks if the IPs, domains and ports have the expected values. If all fields have been filled in, etc.
        """
        # Check if the required fields are filled in

        if not self.src_ip.get() or not self.dst_ip.get() or not self.protocol.get() or not self.dst_port.get():
            messagebox.showwarning("Mandatory fields", "Please fill in all mandatory fields.")
            return -1
        if not self.dst_port.get().isdigit():
            messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
            return -1
        try:
            porta = int(self.dst_port.get())
            if porta < 1 or porta > 65535:
                messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
                return -1
        except ValueError:
            messagebox.showwarning("Invalid port: conversion error.")
            return -1
        
        if self.dst_ip.get() not in self.hosts_display:
            if self.validate_ip_or_domain(self.dst_ip.get()) == False:
                messagebox.showwarning(f"Invalid address", "The address must either: \n1. Be on the list, \n2. Be an IP (8.8.8.8), \n3. Be a domain (www.google.com.br).")
                return -1
            else: # If it is outside the list of hosts in the scenario, for now it is only possible to perform ping tests.
                if self.protocol.get() != "ICMP":
                    messagebox.showwarning(f"Invalid protocol", "Unfortunately, in this version, only ICMP (ping) can be used to test external hosts.")
                    return -1
                
        return 0
        # TODO - if the destination is changed, in this version of the system, you can only use the ICMP protocol, you cannot use TCP or UDP, because the server (if it exists) will not recognize the message sent.
        # If all fields are filled in, call the firewall_test_tree_edit_line_test (old add_edit_test method)
        

    # def validar_e_adicionar_teste(self):
    #     """Valida os campos antes de chamar o método adicionar_editar_teste"""
    #     # Verifica se os campos obrigatórios estão preenchidos

    #     if not self.src_ip.get() or not self.dst_ip.get() or not self.protocol.get() or not self.dst_port.get():
    #         messagebox.showwarning("Mandatory fields", "Please fill in all mandatory fields.")
    #         return
    #     if not self.dst_port.get().isdigit():
    #         messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
    #         return
    #     try:
    #         porta = int(self.dst_port.get())
    #         if porta < 1 or porta > 65535:
    #             messagebox.showwarning("Mandatory fields", "The port must be a number between 1-65535.")
    #             return
    #     except ValueError:
    #         messagebox.showwarning("Invalid port: conversion error.")
    #         return
        
    #     if self.dst_ip.get() not in self.hosts_display:
    #         if self.validate_ip_or_domain(self.dst_ip.get()) == False:
    #             messagebox.showwarning(f"Invalid address", "The address must either: \n1. Be on the list, \n2. Be an IP (8.8.8.8), \n3. Be a domain (www.google.com.br).")
    #             return
    #         else: # se for fora da lista de hosts do cenário, por enquanto só é possível realizar testes de ping.
    #             if self.protocol.get() != "ICMP":
    #                 messagebox.showwarning(f"Invalid protocol", "Unfortunately, in this version, only ICMP (ping) can be used to test external hosts.")
    #                 return
    #     # TODO - se for alterado o destino, nesta versão do sistema só pode utilizar o protocolo icmp, não dá para utilizar tcp ou udp, pq o servidor (se existir) não vai reconhecer a mensagem enviada.
    #     # Se todos os campos estiverem preenchidos, chama o método adicionar_editar_teste
    #     self.adicionar_editar_teste()
    
    def firewall_tests_update_tree(self):
        """
            Updates the treeview of tests in the firewall, in firewall tests tab.
        """
        itens = self.tree.get_children()

        for item in itens:
            self.tree.item(item, tags="")  # Sets tags to an empty list
        # TODO - I don't know if it's interesting to do the results that demonstrate the test results - I don't think so!

    def extract_ip_parenthesized_from_string(self,string):
        """
            Extract IPs from a string, this method expects the IP to be in parentheses, which is the host format presented in the comboboxes of the firewall testing tab. 
            So the string will be something like: Host1 (10.0.0.1), the method will return only 10.0.0.1. Only IPv4.

            Args:
                string: String to be parsed for IP
        """
        match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', string)
        return match.group(1) if match else None
    
    def extract_ip_from_string(self, string):
        """
            Extract IPs from a string. Only IPv4.
            Args:
                string: String to be parsed for IP
        """
        match = re.search(r'\(?(\d+\.\d+\.\d+\.\d+)\)?', string)  
        return match.group(1) if match else None
    
    def extract_domain(self, string):
        """
            Extract domain from a string. This method expects two or more words separated by a dot - this method is not perfect.
            Args:
                string: String to be parsed for domain
        """
        match = re.search(r'\(?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\)?', string)
        return match.group(1) if match else None
    
    def extract_destination_host(self, destination):
        """
            Extract the target host.

            Args:
                dst_ip: destination, can be a IP, host (IP) or a domain.
        """
        temp_destination =  self.extract_ip_parenthesized_from_string(destination)
        print(f"temp_dst_ip {temp_destination}")

        if temp_destination != None:
            destination = temp_destination
        else:
            # without parentheses
            temp_destination = self.extract_ip_from_string(destination)
            if temp_destination != None:
                destination = temp_destination
            else:
                # dpmain
                temp_destination = self.extract_domain(destination)
                if temp_destination != None:
                    destination = temp_destination
                else:
                    # invalid
                    print(f"\033[33mCould not extract the destination IP in the interface:\n\tThe destination address must be an IP or domain, such as: 8.8.8.8 or www.google.com.\033[0m")
                    return None
        return destination    
    
    def firewall_tests_run_test_line(self):
        """
            Test only one row of the firewall test table. This row will be the currently selected row in the firewall test tree.
        """
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            print(f"Items to testing:: {values}")
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values
            
            # if you were unable to extract the destination IP entered by the user to
            dst_ip = self.extract_destination_host(dst_ip)
            if dst_ip == None: return
            
            print(f"Test executed - Container ID: {container_id}, Dados: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

            result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
                print(f"The return of the command on the host is {result_str}")
            except (json.JSONDecodeError, TypeError) as e:
                print("Error processing JSON received from host:", e)
                messagebox.showerror("Error", "Could not get a response from the hosts! \n Is GNS3 or the hosts turned on?")
                result = None
                return

            self.firewall_tests_analyse_results_update_tree(expected, result, values, selected_item)
            self.tree.selection_set(())
        

    def firewall_tests_analyse_results_update_tree(self, expected, result, values, selected_item):
        """
            Analyze the test result and update the table with the fields and colors that represent these results in the firewall test tree.

            Args:
                expected: result that was expected from the test.
                result: result obtained in the test.
                values: values ​​used and obtained in the test, such as source, destination, etc. are the columns of the firewall test treeview.
                selected_item: Test line used and which will have its values ​​and color updated in the firewall test table.
        """
        # TODO - check whether all cases have been covered
        # TODO - improve logic for checking user errors - such as testing a port that is not connected!
        print(values)
        update_values = list(values)
        tag = None

        if result["server_response"] == True: # if the server responded then put sent/receved, otherwise just Sent - TODO - there may be a case where it didn't even send, which would be the case of the error!
                    update_values[9] = "Sent/Receved" # The package was just sent and there was a response!
                    update_values[8] = "Pass"
        else:
                    update_values[9] = "Sent" # The package was just sent but there was no response!
                    update_values[8] = "Fail"

        network_data = result['client_ip']+':'+str(result['client_port'])+'->'+result['server_ip']+':'+str(result['server_port'])+'('+result['protocol']+')'+' - Server response? '+ str(result['server_response'])+ ' - Status: '+result['status_msg']
        update_values[-1] = network_data

        if (result["status"] != '0'):
            # an error occurred, such as the host network was not configured.
            print(f"\033[33mThere was an error with the host when sending the packet, such as a misconfigured network - IP, GW, etc.\033[0m")
            update_values[8] = "ERROR"
            update_values[9] = "Not Sent"
            tag = "error"
        elif (result["server_response"] == True and expected == "yes"):
            # test performed successfully and there was a response from the server.
            print(f"\033[32mThe SUCCESS test occurred as expected.\033[0m")
            tag = "yes"
        elif (result["server_response"] == False and expected == "no"):
            # # The packet sending test failed, but this was expected in the test, so this is a success!
            print(f"\033[32mThe FAIL test occurred as expected.\033[0m")
            tag = "yesFail"
        else: # TODO - I think the logic is wrong here (check the possible cases) - is that in client.py you had to remove status=1 because it said there was an error in a packet blocked by the firewall!
            print(f"\033[31mThe test did NOT occur as expected.\033[0m")
            tag = "no"


        if "dnat" in result: # dnat only happens if there is a response from the server so there is no need for result["server_response"] == True - this comes from server.py
                print("dnat")
                # there was DNAT
                dnat_data = result["dnat"]
                network_data = result['client_ip']+':'+str(result['client_port'])+'->'+dnat_data['ip']+':'+str(dnat_data['port'])+'('+result['protocol']+')'+' - Server response? '+ str(result['server_response'])+ ' - Status: '+result['status_msg']
                update_values[-1] = network_data
                update_values[9] = "Sent/Receved (DNAT)"
        
        # update the test line in the firewall test tree.
        self.tree.item(selected_item, values=update_values, tags=(tag,))
        
        
    
    def firewall_tests_popup_for_run_all_tests_using_threads(self):
        """
            Starts a window with a progress bar that executes all the tests in the firewall test tree. Threads are used for the progress bar to work.
        """
        print("Thread to execute all tests.")
        janela_popup = tk.Toplevel(self.root)
        janela_popup.title("Processing...")
        janela_popup.geometry("300x120")
        janela_popup.resizable(False, False)
        
        status_label = tk.Label(janela_popup, text="Starting...", font=("Arial", 10))
        status_label.pack(pady=10)

        progresso_var = tk.IntVar()
        barra_progresso = ttk.Progressbar(janela_popup, length=250, mode="determinate", variable=progresso_var)
        barra_progresso.pack(pady=5)

        self.tree.selection_set(())
        self.firewall_tests_update_tree()

        threading.Thread(target=self.firewall_tests_run_all_tests, args=(janela_popup, progresso_var, status_label), daemon=True).start()
    
    def firewall_tests_run_all_tests(self, popup_window, progress_bar, status_label):
        """
            Run a all tests in the firewall test treeview.

            Args:
                popup_window: Pop up window used to show tests progress.
                progress_bar: Progress bar used in the popup to show tests progresses.
                status_label: Label used in the popup to show the tests progress.
        """
        indice=0
        
        itens = self.tree.get_children()

        total_lista = len(itens)
        for teste in itens:
            values = self.tree.item(teste, "values")
            teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values
            print(f"Executing test - Container ID:  {container_id}, Data: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")
            
            # if you were unable to extract the destination IP entered by the user to
            dst_ip = self.extract_destination_host(dst_ip)
            if dst_ip == None: return

            print(f"Executing test - Container ID:  {container_id}, Data: {src_ip} -> {dst_ip} [{protocol}] {src_port}:{dst_port} (Expected: {expected})")

            result_str = containers.run_client_test(container_id, dst_ip, protocol.lower(), dst_port, "1", "2025", "0")

            try:
                result = json.loads(result_str)
            except (json.JSONDecodeError, TypeError) as e:
                print("Error processing the JSON received from the host:", e)
                messagebox.showerror("Error", "Unable to get a response from the hosts! \n Is GNS3 or the hosts running?")
                result = None
                return

            self.firewall_tests_analyse_results_update_tree(expected,result, values, teste)

            indice+=1
            porcentagem_concluida = (indice / total_lista) * 100
            progress_bar.set(porcentagem_concluida)  # Update progress bar
            status_label.config(text=f"Processing... {indice}/{total_lista}")
            

        status_label.config(text="Task completed!")
        progress_bar.set(100)  # Ensures the bar goes all the way to the end
        popup_window.destroy()


    def hosts_start_servers(self):
        """
            Start all the servers in the containers, use server.py for this.
        """
        print("start_servers")
        # TODO - check if there was an error when starting the server and in which container.
        for container in self.containers_data:
            container_id = container["id"]
            containers.start_server(container_id)

        for cid, btn, label_status in self.lista_btn_onOff:
            #print(f"cid/btn {cid} - {btn}")
                btn.config(image=self.power_icon, text="liga")
                status = self.host_check_server_on_off(container_id)
                label_status.config(text=f"Server Status: {status}", font=("Arial", 10))
        
    def hosts_update(self):
        """
            Updates all host/container data - checks for example if any container was created or deleted, if any network configuration changed, etc.
        """
        print("update_hosts")

        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        self.containers_data = containers.extract_containerid_hostname_ips( )  # get hosts information (hostname, interfaces, ips)

        self.hosts_show_host_informations_in_host_tab( )

        # List of values ​​displayed in Combobox (hostname + IP)
        if self.containers_data:
            self.hosts_display = [f"{c['hostname']} ({c['ip']})" for c in self.containers_data]
        else: # if there are no elements it displays a message
            self.hosts_display = ["HOSTS (0.0.0.0)", "HOSTS (0.0.0.0)"]
            messagebox.showerror("Error", "Unable to get a response from the hosts! \n Is GNS3 or the hosts running?")
        self.src_ip["values"] = self.hosts_display
        self.dst_ip["values"] = self.hosts_display
        self.src_ip.current(0)
        if len(self.containers_data) > 1: # checks if there is more than one element in the host list, if there isn't, you can't set the second one as default.
            self.dst_ip.current(1)
        else:
            self.dst_ip.current(0)

    def hosts_show_host_informations_in_host_tab(self):
        """
            Displays host information in the hosts tab.
        """
        print(f"self.containers_data: {self.containers_data}")
        cont = containers.getContainersHostNames()
        print(f"cont :  {json.dumps(cont, indent=4)}")
        self.lista_btn_onOff = []
        row_index = 0  # Starting line on the grid

        # Load the icons
        self.power_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  
        self.power_icon_off = tk.PhotoImage(file="img/system-shutdown-symbolic-off.png") 
        status_on_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png")  
        status_off_icon = tk.PhotoImage(file="img/system-shutdown-symbolic.png") 

        for host in cont:
            print(f"ID: {host['id']}")
            print(f"Nome: {host['nome']}")
            print(f"Hostname: {host['hostname']}")
            print("Interfaces:")

            status = self.host_check_server_on_off(host['id'])

            container_id = host["id"]
            container_name = host["nome"]
            hostname = host["hostname"]

            # Creating a frame for each host
            frame = ttk.Frame(self.bottom_frame)
            frame.grid(row=row_index, column=0, columnspan=3, sticky="w", padx=10, pady=5)

            # Button to edit host ports
            btn = ttk.Button(frame, text=f"{hostname}", command=lambda cid=container_id: self.edit_host_ports(cid, hostname))
            btn.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            # Label with container information
            lbl_container = ttk.Label(frame, text=f"Container: {container_id} - {container_name}", font=("Arial", 10))
            lbl_container.grid(row=0, column=1, padx=5, pady=2, sticky="w")

            row_index += 1  # Move to the next line

            if not host['interfaces']:
                # Creating a subframe to align interfaces and IPs together
                interface_frame = ttk.Frame(frame)
                interface_frame.grid(row=row_index, column=1, columnspan=2, sticky="w", padx=20)
                ip_index = 1
                lbl_interface = ttk.Label(interface_frame, text=f"Interface: None or Down", font=("Arial", 10, "bold"))
                lbl_interface.grid(row=0, column=0, sticky="w")

            else:
                for interface in host['interfaces']:
                    print(f"  - Interface: {interface['nome']}")
                    if_name = interface['nome']

                    # Creating a subframe to align interfaces and IPs together
                    interface_frame = ttk.Frame(frame)
                    interface_frame.grid(row=row_index, column=1, columnspan=2, sticky="w", padx=20)

                    # TODO - I noticed that the ip command shows the interface IPs even if this interface is turned off.
                    # Label with the interface name
                    lbl_interface = ttk.Label(interface_frame, text=f"Interface: {if_name}", font=("Arial", 10, "bold"))
                    lbl_interface.grid(row=0, column=0, sticky="w")

                    ip_index = 1
                    for ip in interface['ips']:
                        lbl_ip = ttk.Label(interface_frame, text=f"IP: {ip}", font=("Arial", 10))
                        lbl_ip.grid(row=ip_index, column=0, padx=20, sticky="w")
                        ip_index += 1

                    row_index += 2  # Move to the next line in the layout

            # Server status
            lbl_status = ttk.Label(interface_frame, text=f"Status from server: {status}", font=("Arial", 10))
            lbl_status.grid(row=ip_index, column=0, padx=5, sticky="w")

            # Power button with icon
            btn_toggle = ttk.Button(interface_frame, image=self.power_icon, command=lambda cid=container_id: self.host_toggle_server_and_button_between_onOff(cid, btn_toggle))
            btn_toggle.image = self.power_icon  # Keep the reference to avoid garbage collection
            btn_toggle.grid(row=ip_index, column=1, padx=10, pady=5, sticky="w")
            self.lista_btn_onOff.append((container_id, btn_toggle, lbl_status))
            row_index += 1  # Extra line to separate hosts

    def host_check_server_on_off(self, container_id):
        """
            Checks if the server is on or off (server is serve.py in each container/host).

            Args:
                container_id: Container ID.
        """
        print(f"Check if server is on or off at container {container_id}")
        cmd = 'docker exec '+ container_id+' ps ax | grep "/usr/local/bin/python ./server.py" | grep -v grep'
        result = containers.run_command_shell(cmd)
        if result !="":
            return "on"
        else:
            return "off"


    def host_toggle_server_and_button_between_onOff(self, container_id, button_on_off):
        """
            Toggles between on and off in the hosts tab (toggles the button)

            Args:
                container_id: Conteriner ID to start or stop server.
                button_on_off: Button on/off to be changed between on and off. 
        """
        print(f"Toggling server for container ID: {container_id}")  
        # Find the corresponding button in the list and change the image
        for cid, button_on_off, label_status in self.lista_btn_onOff:
            print(f"container_id/button {cid} - {button_on_off}")
            if cid == container_id:
                imagem_atual = button_on_off["image"][0]
                if imagem_atual == str(self.power_icon):
                    print("off")
                    label_status.config()
                    containers.stop_server(container_id)
                    button_on_off.config(image=self.power_icon_off)
                else:
                    print("on")
                    containers.start_server(container_id)
                    button_on_off.config(image=self.power_icon, text="liga")
                status = self.host_check_server_on_off(container_id)
                label_status.config(text=f"Server Status: {status}", font=("Arial", 10))
                break

                
    # TODO - the host tab should have a scroll, as there may be more hosts than fit on the tab!


    def firewall_tests_save_tests_as(self):
        """
            Opens a window to save the tests as to a JSON file.
        """
        file_path = filedialog.asksaveasfilename(
            title="Save test file",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:  # If the user cancels, do nothing
            return

        self.save_file_path = file_path

        #print(f"Saving in the file: {self.save_file_path}")
        self.firewall_tests_save_tests()

    def firewall_tests_save_tests(self):
        """
            Saves the Treeview data to a JSON file.
        """
        print("Saving tests...")
        if not self.save_file_path:
            self.firewall_tests_save_tests_as()
        else:
            items = self.tree.get_children()
            tests_data = []

            for item in items:
                values = self.tree.item(item, "values")
                if values:
                    # Recover the hidden Container ID
                    #teste_id = values[0]
                    #container_id = self.hidden_data.get(teste_id, "")  
                    teste_id, container_id, src_ip, dst_ip, protocol, src_port, dst_port, expected, result, dnat, observation = values

                    # Create the dictionary and add it to the list
                    tests_data.append({
                        "teste_id": teste_id,
                        "container_id": container_id,
                        "src_ip": src_ip,
                        "dst_ip": dst_ip,
                        "protocol": protocol,
                        "src_port": src_port,
                        "dst_port": dst_port,
                        "expected": expected,
                        "result": result,
                        "flow": dnat,
                        "data": observation
                    })

            # Write to JSON file
            with open(self.save_file_path, "w") as f:
                json.dump(tests_data, f, indent=4)

            print(f"Tests successfully saved in file: {self.save_file_path}")

    # TODO - When loading, you have to check if the source still has the same container ID - because if it is on different machines or in different GNS3 projects - the container ID will change!
    # TODO - I would also have to see if the IPs still match, because in class, the teacher usually gives the name of the machine and not the IP, so I would have to check if the IPs are the same, if they are not, I would have to update the IP, probably with user interaction if the host has more than one IP (choose which IP is for the test, especially if it is the destination - at the source this will not make much difference)
    
    def firewall_tests_load_tests_from_file(self):
        """
            Loads data from the JSON file into the Treeview.
        """
        print("Loading tests...")

        if os.path.exists(self.save_file_path):
            with open(self.save_file_path, "r") as f:
                try:
                    tests_data = json.load(f)
                except json.JSONDecodeError:
                    print("Error loading the JSON file.")
                    return

            # Add items to the Treeview
            for test in tests_data:
                item_id = self.tree.insert("", "end", values=[
                    test["teste_id"], test["container_id"], test["src_ip"], test["dst_ip"], test["protocol"],
                    test["src_port"], test["dst_port"], test["expected"], test["result"], test["flow"], test["data"]
                ])

                # Restore the hidden Container ID
                #self.hidden_data[test["teste_id"]] = test["container_id"]

                # Apply color according to the result
                #self.apply_row_color(item_id, test["result"])

            print("Tests successfully loaded!")
            self.firewall_tests_buttons_set_normal_state()
        else:
            print("No test files found.")

    def firewall_tests_open_test_file(self):
        """
            Opens a window to select a JSON file and load the tests.
        """
        file_path = filedialog.askopenfilename(
            title="Open test file",
            filetypes=[("JSON file", "*.json"), ("All files", "*.*")]
        )

        if not file_path:  # If the user cancels, it does nothing.
            return

        self.save_file_path = file_path

        print(f"Loading tests from file: {file_path}")

        self.firewall_tests_load_tests_from_file()
    

    def confirm_software_exit(self):
        """
            A window opens asking if you really want to exit the firewall tester program.
        """
        if messagebox.askyesno("Confirmation", "Do you really want to exit the program?"):
            self.root.destroy()

# Running the Firewall Tester application
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
