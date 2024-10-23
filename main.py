import tkinter as tk
from keyboard import add_hotkey
import json

class QMKLayoutViewer:
    def __init__(self, layout_file):
        self.root = tk.Tk()
        self.root.title("QMK Layout Viewer")
        
        # Make window stay on top with partial transparency
        self.root.attributes('-topmost', True, '-alpha', 0.8)
        self.root.configure(bg='black')
        
        # Create main frame
        self.frame = tk.Frame(self.root, bg='black', padx=10, pady=10)
        self.frame.pack()
        
        # Layer indicator
        self.layer_label = tk.Label(
            self.frame,
            text="Layer 0 (Base)",
            font=("Arial", 12, "bold"),
            bg='black',
            fg='white',
            pady=5
        )
        self.layer_label.pack()
        
        # Create keyboard layout frame
        self.layout_frame = tk.Frame(self.frame, bg='black')
        self.layout_frame.pack()
        
        # Load layout data
        with open(layout_file, 'r') as f:
            self.layout_data = json.load(f)
        
        # Initialize
        self.current_layer = 0
        self.key_buttons = []
        
        # Create the grid layout (assuming 34-key layout like ferris sweep)
        self.rows = 3
        self.cols = 12  # Including thumb keys
        
        # Create initial layout
        self.create_layout()
        
        # Bind hotkeys for layer switching (0-9)
        for i in range(min(10, len(self.layout_data['layers']))):
            add_hotkey(f'ctrl+{i}', lambda x=i: self.switch_layer(x))
        
        # Make window draggable
        self.frame.bind('<Button-1>', self.start_drag)
        self.frame.bind('<B1-Motion>', self.drag)
        
        # Right click to exit
        self.frame.bind('<Button-3>', lambda e: self.root.quit())

    def translate_keycode(self, keycode):
        # Dictionary for QMK keycode translation
        qmk_to_label = {
            'TRNS': '▽',  # Transparent key
            'NO': 'N/A',    # No key
            'BSPC': '⌫',
            'SPC': '␣',
            'ENT': '⏎',
            'ESC': 'Esc',
            'TAB': '⇥',
            'UP': '↑',
            'DOWN': '↓',
            'LEFT': '←',
            'RGHT': '→',
            'PGUP': 'PgUp',
            'PGDN': 'PgDn',
            'HOME': 'Home',
            'END': 'End',
            'DEL': 'Del',
            'COMM': ',',
            'DOT': '.',
            'SLSH': '/',
            'SCLN': ';',
            'EXLM': '!',
            'COLN': ':',
            'QUOT': '"',
            'GRV': '`',
            'TILD': '~',
            'BSLS': '\\',
            'PIPE': '|',
            'LBRC': '[',
            'RBRC': ']',
            'LPRN': '(',
            'RPRN': ')',
            'LCBR': '{',
            'RCBR': '}',
            'MINS': '-',
            'EQL': '=',
            'PLUS': '+',
            'ASTR': '*',
            'PERC': '%',
            'CIRC': '^',
            'DQT': '"',
            'HASH': '#',
            'DLR': '$',
            'AT': '@',
            'GRTR': '>',
            'LESS': '<',
            'AMPR': '&',
            'QUES': '?',
            'COLON': ':',
            'PERC': '%',
            'LT': '<',
            'GT': '>',
            'MS_U': '↑',
            'MS_D': '↓',
            'MS_L': '←',
            'MS_R': '→',
            'WH_U': '⟳',
            'WH_D': '⟲',
            'BTN1': 'B1',
            'BTN2': 'B2',
        }
        
        # Handle special cases
        if keycode.startswith('KC_'):
            # Regular keycode
            simple_key = keycode[3:]
            if simple_key in qmk_to_label:
                return qmk_to_label[simple_key]
            return simple_key
        elif keycode.startswith('LT('):
            # Layer tap
            layer = keycode[keycode.find('(')+1:keycode.find(',')]
            key = keycode[keycode.find('KC_')+3:keycode.find(')')]
            if key in qmk_to_label:
                key = qmk_to_label[key]
            return f"{key}\nL{layer}"
        elif keycode.startswith('LSFT_T('):
            # Mod tap shift
            key = keycode[keycode.find('KC_')+3:keycode.find(')')]
            if key in qmk_to_label:
                key = qmk_to_label[key]
            return f"{key}\n⇧"
        elif keycode.startswith('LCTL_T('):
            # Mod tap control
            key = keycode[keycode.find('KC_')+3:keycode.find(')')]
            if key in qmk_to_label:
                key = qmk_to_label[key]
            return f"{key}\n⌃"
        elif keycode.startswith('LALT_T('):
            # Mod tap alt
            key = keycode[keycode.find('KC_')+3:keycode.find(')')]
            if key in qmk_to_label:
                key = qmk_to_label[key]
            return f"{key}\n⌥"
        return keycode
    
    def __create_button(self, label):
        bg_color = '#333333'
        if label == "N/A":
            bg_color = "#2c3254"
        return tk.Label(
            self.layout_frame,
            text=label,
            width=6,
            height=2,
            relief='raised',
            bg=bg_color,
            fg='white',
            font=('Arial', 8)
        )

    def create_layout(self):
        # Clear existing layout
        for button in self.key_buttons:
            button.destroy()
        self.key_buttons = []
        
        layer = self.layout_data['layers'][self.current_layer]
        
        # Create 3x10 grid for main keys
        for row in range(3):
            for col in range(5):
                idx = row * 10 + col
                if idx < len(layer):
                    key = layer[idx]
                    label = self.translate_keycode(key)
                    
                    btn = self.__create_button(label)
                    btn.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
                    self.key_buttons.append(btn)

            for col in range(5,10):
                idx = row * 10 + col
                if idx < len(layer):
                    key = layer[idx]
                    label = self.translate_keycode(key)
                    
                    btn = self.__create_button(label)
                    btn.grid(row=row, column=col+1, padx=1, pady=1, sticky='nsew')
                    self.key_buttons.append(btn)
        
        btn = tk.Label(
            self.layout_frame,
                        text="",
                        bg='black',
                        font=('Arial', 8)
                    )
        
        btn.grid(row=0, column=5, padx=5, pady=1, sticky='nsew')
        self.key_buttons.append(btn)
        # Add thumb keys
        for i in range(4):
            if 30 + i < len(layer):
                key = layer[30 + i]
                label = self.translate_keycode(key)
                
                btn = self.__create_button(label)
                if i > 1:
                    btn.grid(row=3, column=3+i+1, padx=1, pady=1, sticky='nsew')
                else:
                    btn.grid(row=3, column=3+i, padx=1, pady=1, sticky='nsew')
                self.key_buttons.append(btn)

    def switch_layer(self, layer):
        if layer < len(self.layout_data['layers']):
            self.current_layer = layer
            self.layer_label.config(text=f"Layer {layer}")
            self.create_layout()

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # You'll need to specify your layout file path here
    app = QMKLayoutViewer('colemak-aurora-sweep.json')
    app.run()