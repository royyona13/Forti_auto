import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path


HOSTNAME_PATTERN = r'(hostname:\s*")F81F-CB\d+("\s*)'


def find_old_switch_name(text):
    """
    Finds the old switch name automatically from this section:

    switch-controller_managed-switch:
        - S108FFTV25012639:
    """

    match = re.search(
        r'switch-controller_managed-switch:\s*\n\s*-\s*([A-Za-z0-9_-]+):',
        text
    )

    if not match:
        raise ValueError("Could not find old switch name automatically")

    return match.group(1)


def build_new_config(text, cb_number, new_switch_name):
    cb_number = cb_number.strip()
    new_switch_name = new_switch_name.strip()

    if not cb_number:
        raise ValueError("Enter CB number, for example: 50")

    if not new_switch_name:
        raise ValueError("Enter new switch name")

    old_switch_name = find_old_switch_name(text)

    text, hostname_count = re.subn(
        HOSTNAME_PATTERN,
        rf'\g<1>F81F-CB{cb_number}\2',
        text,
        count=1
    )

    text, switch_count = re.subn(
        re.escape(old_switch_name),
        new_switch_name,
        text
    )

    return text, hostname_count, switch_count, old_switch_name


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Forti Config Generator")
        self.geometry("760x380")
        self.minsize(720, 360)
        self.resizable(True, False)
        self.configure(bg="#f3f7fb")

        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.cb_number = tk.StringVar()
        self.switch_name = tk.StringVar()
        self.status_text = tk.StringVar(value="Select a YAML file to begin.")

        self._configure_style()

        self.build_gui()

    def _configure_style(self):
        style = ttk.Style(self)

        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")

        background = "#f3f7fb"
        surface = "#ffffff"
        text = "#0f1724"
        muted = "#58606a"
        accent = "#0f766e"
        accent_active = "#0d5e56"
        border = "#d8e0ea"

        base_font = ("DejaVu Sans", 12)
        title_font = ("DejaVu Sans", 18, "bold")

        style.configure(".", background=background, foreground=text, font=base_font)
        style.configure("App.TFrame", background=background, padding=20)
        style.configure("Card.TFrame", background=surface, relief="solid", borderwidth=1)
        style.configure("Title.TLabel", background=background, foreground=text, font=title_font)
        style.configure("App.TLabel", background=background, foreground=text)
        style.configure("Hint.TLabel", background=background, foreground=muted)
        style.configure("Status.TLabel", background=background, foreground=accent)
        style.configure("App.TEntry", fieldbackground=surface, foreground=text, insertcolor=text, padding=8)
        style.configure("Secondary.TButton", background="#e2e8f0", foreground=text, padding=(12, 8))
        style.map(
            "Secondary.TButton",
            background=[("active", "#cbd5e1"), ("pressed", "#b6c2d0")],
            foreground=[("disabled", "#94a3b8")]
        )
        style.configure("Accent.TButton", background=accent, foreground="#ffffff", padding=(14, 10), borderwidth=0)
        style.map(
            "Accent.TButton",
            background=[("active", accent_active), ("pressed", "#0b4f4b")],
            foreground=[("disabled", "#e5e7eb")]
        )
        style.configure("Card.TLabel", background=surface, foreground=text)
        style.configure("Card.Hint.TLabel", background=surface, foreground=muted)
        style.configure("Card.Status.TLabel", background=surface, foreground=accent)
        style.configure("Card.TEntry", fieldbackground="#ffffff", foreground=text, insertcolor=text, padding=8)
        style.map("Card.TEntry", fieldbackground=[("focus", "#ffffff")], bordercolor=[("focus", border)])

    def build_gui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        main = ttk.Frame(self, style="App.TFrame")
        main.grid(row=0, column=0, sticky="nsew")

        card = ttk.Frame(main, style="Card.TFrame", padding=16)
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Forti Config Replacer", style="Title.TLabel").grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 8)
        )

        ttk.Label(card, text="Original YAML file:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 6))

        ttk.Entry(card, textvariable=self.input_file, style="Card.TEntry").grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(10, 10),
            pady=(0, 6)
        )

        ttk.Button(
            card,
            text="Choose File",
            style="Secondary.TButton",
            command=self.choose_input_file
        ).grid(row=1, column=2, sticky="ew", pady=(0, 6))

        ttk.Label(card, text="New CB number:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 6))

        ttk.Entry(card, textvariable=self.cb_number, width=18, style="Card.TEntry").grid(
            row=2,
            column=1,
            sticky="w",
            padx=(10, 10),
            pady=(0, 6)
        )

        ttk.Label(
            card,
            text='Example: 50 creates hostname "F81F-CB50"',
            style="Card.Hint.TLabel",
            wraplength=190
        ).grid(row=2, column=2, sticky="w", pady=(0, 6))

        ttk.Label(card, text="New switch name:", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 6))

        ttk.Entry(card, textvariable=self.switch_name, style="Card.TEntry").grid(
            row=3,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(10, 0),
            pady=(0, 6)
        )

        ttk.Label(card, text="New output file:", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=(0, 6))

        ttk.Entry(card, textvariable=self.output_file, style="Card.TEntry").grid(
            row=4,
            column=1,
            sticky="ew",
            padx=(10, 10),
            pady=(0, 6)
        )

        ttk.Button(
            card,
            text="Save As",
            style="Secondary.TButton",
            command=self.choose_output_file
        ).grid(row=4, column=2, sticky="ew", pady=(0, 6))

        ttk.Separator(card, orient="horizontal").grid(
            row=5,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(10, 10)
        )

        ttk.Button(
            card,
            text="Create New Config",
            style="Accent.TButton",
            command=self.create_new_config,
            width=25
        ).grid(row=6, column=0, columnspan=3, sticky="ew")

        ttk.Label(card, textvariable=self.status_text, style="Card.Status.TLabel").grid(
            row=7,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(10, 0)
        )

        card.rowconfigure(8, weight=1)

    def choose_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Choose Forti YAML config file",
            filetypes=[
                ("YAML files", "*.yaml *.yml"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.input_file.set(file_path)

            original_path = Path(file_path)
            new_file = original_path.with_name(
                original_path.stem + "_new" + original_path.suffix
            )

            self.output_file.set(str(new_file))
            self.status_text.set("Input file selected. Review the output path and create the new config.")

    def choose_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save new config file",
            defaultextension=".yaml",
            filetypes=[
                ("YAML files", "*.yaml *.yml"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.output_file.set(file_path)
            self.status_text.set("Output file selected.")

    def create_new_config(self):
        try:
            input_value = self.input_file.get().strip()
            output_value = self.output_file.get().strip()

            if not input_value:
                raise ValueError("Please choose the original YAML file first")

            if not output_value:
                raise ValueError("Please choose where to save the new file")

            input_path = Path(input_value)
            output_path = Path(output_value)

            if not input_path.exists():
                raise ValueError("Please choose the original YAML file first")

            if input_path.resolve() == output_path.resolve():
                raise ValueError("The new file must be different from the original file")

            original_text = input_path.read_text(encoding="utf-8")

            new_text, hostname_count, switch_count, old_switch_name = build_new_config(
                original_text,
                self.cb_number.get(),
                self.switch_name.get()
            )

            output_path.write_text(new_text, encoding="utf-8")
            self.status_text.set(f"Created new config: {output_path.name}")

            messagebox.showinfo(
                "Done",
                f"New config created successfully.\n\n"
                f"Old switch detected: {old_switch_name}\n"
                f"New switch name: {self.switch_name.get()}\n\n"
                f"Forti hostname changes: {hostname_count}\n"
                f"Switch name changes: {switch_count}\n\n"
                f"Saved to:\n{output_path}"
            )

        except Exception as error:
            messagebox.showerror("Error", str(error))


if __name__ == "__main__":
    app = App()
    app.mainloop()