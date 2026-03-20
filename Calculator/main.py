import tkinter as tk

# Set up our color palette
bg_color = "#202020"         
display_bg = "#333333"       
text_color = "#FFFFFF"       
btn_normal = "#3B3B3B"      
btn_operator = "#323232"     
btn_equals = "#0067C0"       
btn_hover = "#505050"        

# Hover effects for a better feel
def on_enter(e):
    if e.widget['text'] == '=':
        e.widget['background'] = '#1976D2'
    else:
        e.widget['background'] = btn_hover

def on_leave(e):
    if e.widget['text'] == '=':
        e.widget['background'] = btn_equals
    else:
        e.widget['background'] = btn_normal

# Basic calculator functions
def press_key(value):
    calc_display.insert(tk.END, value)

def clear_display():
    calc_display.delete(0, tk.END)

def calculate_result():
    try:
        # Note: eval is fine for personal projects, 
        # but consider 'ast.literal_eval' for production security!.
        result = eval(calc_display.get())
        calc_display.delete(0, tk.END)
        calc_display.insert(0, result)
    except Exception:
        calc_display.delete(0, tk.END)
        calc_display.insert(0, "Error")

# Main window setup
app = tk.Tk()
app.title("Calculator")
app.geometry("350x520")
app.configure(bg=bg_color)

# The main input display
calc_display = tk.Entry(app, font=("Segoe UI", 32), bg=display_bg, fg=text_color, 
                 borderwidth=0, justify="right", insertbackground="white")
calc_display.pack(fill="x", padx=20, pady=(30, 20), ipady=10)

# Frame to hold all the buttons
keypad_frame = tk.Frame(app, bg=bg_color)
keypad_frame.pack(expand=True, fill="both", padx=15, pady=10)

# Button layout mapping
keypad_layout = [
    ('7', '8', '9', '/'),
    ('4', '5', '6', '*'),
    ('1', '2', '3', '-'),
    ('0', '.', '=', '+')
]

# Build the grid
for row in keypad_layout:
    row_frame = tk.Frame(keypad_frame, bg=bg_color)
    row_frame.pack(expand=True, fill="both")
    
    for char in row:
        current_bg = btn_normal
        if char in ['/', '*', '-', '+']: 
            current_bg = btn_operator
        if char == '=': 
            current_bg = btn_equals

        # Assign function based on what button it is
        action = lambda x=char: calculate_result() if x == '=' else press_key(x)
        
        btn = tk.Button(row_frame, text=char, font=("Segoe UI Semibold", 14),
                        bg=current_bg, fg=text_color, activebackground=btn_hover,
                        activeforeground=text_color, relief="flat", bd=0,
                        command=action)
        
        btn.pack(side="left", expand=True, fill="both", padx=2, pady=2)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

# Clear button
btn_clear = tk.Button(app, text="CLEAR", font=("Segoe UI Bold", 12),
                      bg="#C42B1C", fg=text_color, activebackground="#A82318",
                      relief="flat", bd=0, command=clear_display)
btn_clear.pack(fill="x", padx=17, pady=(0, 10), ipady=8)

# Custom Watermark 😉
watermark = tk.Label(app, text="</> by BugHunterJunior", font=("Consolas", 9), 
                     bg=bg_color, fg="#3FFA00")
watermark.pack(side="bottom", pady=(0, 10))

app.mainloop()