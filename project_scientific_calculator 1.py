from tkinter import *
from tkinter import ttk
import math
import re

# ----------------- CONFIG -----------------
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 520

# ----------------- SAFE MATH -----------------
safe_math = {
    'sin': lambda x: math.sin(math.radians(x)),
    'cos': lambda x: math.cos(math.radians(x)),
    'tan': lambda x: math.tan(math.radians(x)),
    'log': math.log10,
    'ln': math.log,
    'sqrt': math.sqrt,
    'cbrt': lambda x: x ** (1/3),
    'pi': math.pi,
    'e': math.e,
    'fact': lambda x: math.factorial(int(x)),
    'abs':abs
}

# ----------------- MAIN WINDOW (ONLY ONE) -----------------
root = Tk()
root.title("PYTHON CALCULATOR")
root.option_add("*Button.Font", ("Arial", 16, "bold"))
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.configure(bg="black")
root.minsize(900, 420)

# ----------------- NOTEBOOK / TABS -----------------
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

calc_tab = Frame(notebook, bg="black")

notebook.add(calc_tab, text="Calculator")


# ----------------- STATE -----------------
expr = ""
history_list = []

button_bg = "#1a1a1a"
button_fg = "white"
sci_bg = "#333333"

# ----------------- HELPERS: preprocess sqrt9 -> sqrt(9), cbrt27 -> cbrt(27) -----------------
def preprocess_functions_no_paren(s: str) -> str:
    # convert unicode √ and ∛ to names (if present)
    s = s.replace("√", "sqrt").replace("∛", "cbrt")
    # convert sqrt9 or cbrt27 into sqrt(9), cbrt(27)
    # handle numbers, decimal numbers, and expressions in parentheses are left intact
    s = re.sub(r"(sqrt|cbrt)(\s*)(\d+(\.\d+)?)", r"\1(\3)", s)
    return s

# ----------------- INPUT / DISPLAY -----------------
display_var = StringVar()
entry = Entry(calc_tab, textvariable=display_var, font=("Arial", 20),
              bg="black", fg="white", insertbackground="white", justify=RIGHT)
entry.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

# backspace button top-right of calculator area
def backspace():
    global expr
    if expr:
        expr = expr[:-1]
        display_var.set(expr)
# Button size used across the calculator (ensure these come BEFORE button creation)
BTN_W = 10
BTN_H = 2
Button(calc_tab, text='⌫', bg="#990000", fg="white", font=("Arial", 14),
       command=backspace, width=BTN_W, height=BTN_H).grid(row=1, column=5, padx=4, pady=4, sticky="nsew")


# ----------------- HISTORY (inside calc_tab, right side) -----------------
history_label = Label(calc_tab, text="History", fg="white", bg="black", font=("Arial", 30 ,"bold"))
history_label.grid(row=0, column=6, padx=10, sticky="nw")

history_box = Listbox(calc_tab, height=18, width=28, bg="#111111",
                      fg="white", font=("Arial", 10))
history_box.grid(row=1, column=6, rowspan=8, padx=8, pady=(10,0), sticky="n")




def add_history(item: str):
    history_list.append(item)
    history_box.insert(END, item)
    history_box.see(END)

# ----------------- CORE FUNCTIONS -----------------
def press(key):
    """Insert the raw text for buttons into the expression (numbers and function tokens)."""
    global expr
    # convert numbers to string consistently
    expr += str(key)
    display_var.set(expr)

def clear_all():
    global expr
    expr = ""
    display_var.set("")

def handle_factorial(exp):
    while "!" in exp:
        idx = exp.index("!")
        num = ""
        i = idx - 1
        while i >= 0 and exp[i].isdigit():
            num = exp[i] + num
            i -= 1
        exp = exp.replace(num + "!", f"fact({num})")
    return exp

# Smart function: if expression empty or ends with operator insert name (no paren).
# If expression contains a number (single value), evaluate then apply func.
def smart_func(func_name):
    global expr
    if expr == "" or expr[-1] in "+-*/%(":
        # insert function name (without '(') — user can type bracket or number
        # but many users prefer function with no auto-bracket per your request
        press(func_name)
        return
    # try to evaluate current expr and apply
    try:
        # Prepare expression for evaluation
        expr_eval = preprocess_functions_no_paren(expr)
        val = eval(expr_eval, {"__builtins__": {}}, safe_math)
        fval = float(val)
        res = safe_math[func_name](fval)
        # format result nicely
        if abs(res - round(res)) < 1e-12:
            res = int(round(res))
        else:
            res = round(res, 12)
        add_history(f"{func_name}({val}) = {res}")
        expr = str(res)
        display_var.set(expr)
    except Exception:
        # fallback: insert function name text
        press(func_name)

def equal():
    global expr
    try:
        expr2 = handle_factorial(preprocess_functions_no_paren(expr))
        result = eval(expr2, {"__builtins__": {}}, safe_math)

        # Evaluate in safe environment
        result = eval(expr2, {"__builtins__": {}}, safe_math)
        # prettify result
        if isinstance(result, float) and abs(result - round(result)) < 1e-12:
            result = int(round(result))
        elif isinstance(result, float):
            result = round(result, 12)
        result_str = str(result)
        display_var.set(result_str)
        add_history(expr + " = " + result_str)
        expr = result_str
    except Exception:
        display_var.set("error")
        expr = ""

# ----------------- KEYBOARD SUPPORT -----------------
def key_event(event):
    global expr
    char = event.char
    key = event.keysym
    if char.isdigit():
        press(char)
    elif char in "+-*/.%":
        press(char)
    elif char in "()":
        press(char)
    elif key == "Return":
        equal()
    elif key == "BackSpace":
        backspace()
    elif key == "Escape":
        clear_all()
    elif char == "^":
        press("**")

root.bind("<Key>", key_event)

# ----------------- BUTTONS LAYOUT -----------------
# Make bigger buttons: width/height and use grid sticky to stretch
BTN_W = 10
BTN_H = 2

# Row 1: scientific names (we insert function names without auto-paren)
Button(calc_tab, text='sin', bg=sci_bg, fg=button_fg, command=lambda: press("sin"), width=BTN_W, height=BTN_H).grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='cos', bg=sci_bg, fg=button_fg, command=lambda: press("cos"), width=BTN_W, height=BTN_H).grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='tan', bg=sci_bg, fg=button_fg, command=lambda: press("tan"), width=BTN_W, height=BTN_H).grid(row=1, column=2, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='log', bg=sci_bg, fg=button_fg, command=lambda: press("log"), width=BTN_W, height=BTN_H).grid(row=1, column=3, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='ln', bg=sci_bg, fg=button_fg, command=lambda: press("ln"), width=BTN_W, height=BTN_H).grid(row=1, column=4, padx=4, pady=4, sticky="nsew")

# Row 2
Button(calc_tab, text='√', bg=sci_bg, fg=button_fg, command=lambda: smart_func("sqrt"), width=BTN_W, height=BTN_H).grid(row=2, column=0, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='x²', bg=sci_bg, fg=button_fg, command=lambda: press("**2"), width=BTN_W, height=BTN_H).grid(row=2, column=1, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='^', bg=sci_bg, fg=button_fg, command=lambda: press("**"), width=BTN_W, height=BTN_H).grid(row=2, column=2, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='π', bg=sci_bg, fg=button_fg, command=lambda: press("pi"), width=BTN_W, height=BTN_H).grid(row=2, column=3, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='e', bg=sci_bg, fg=button_fg, command=lambda: press("e"), width=BTN_W, height=BTN_H).grid(row=2, column=4, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='∛', bg=sci_bg, fg=button_fg, command=lambda: smart_func("cbrt"), width=BTN_W, height=BTN_H).grid(row=2, column=5, padx=4, pady=4, sticky="nsew")

# Row 3 - numbers and operators
Button(calc_tab, text='7', bg=button_bg, fg=button_fg, command=lambda: press("7"), width=BTN_W, height=BTN_H).grid(row=3, column=0, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='8', bg=button_bg, fg=button_fg, command=lambda: press("8"), width=BTN_W, height=BTN_H).grid(row=3, column=1, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='9', bg=button_bg, fg=button_fg, command=lambda: press("9"), width=BTN_W, height=BTN_H).grid(row=3, column=2, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='/', bg=button_bg, fg=button_fg, command=lambda: press("/"), width=BTN_W, height=BTN_H).grid(row=3, column=3, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='(', bg=sci_bg, fg=button_fg, command=lambda: press("("), width=BTN_W, height=BTN_H).grid(row=3, column=4, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='!', bg=sci_bg, fg=button_fg,command=lambda: press("!"), width=BTN_W, height=BTN_H).grid(row=3, column=5, padx=4, pady=4, sticky="nsew")

# Row 4
Button(calc_tab, text='4', bg=button_bg, fg=button_fg, command=lambda: press("4"), width=BTN_W, height=BTN_H).grid(row=4, column=0, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='5', bg=button_bg, fg=button_fg, command=lambda: press("5"), width=BTN_W, height=BTN_H).grid(row=4, column=1, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='6', bg=button_bg, fg=button_fg, command=lambda: press("6"), width=BTN_W, height=BTN_H).grid(row=4, column=2, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='*', bg=button_bg, fg=button_fg, command=lambda: press("*"), width=BTN_W, height=BTN_H).grid(row=4, column=3, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text=')', bg=sci_bg, fg=button_fg, command=lambda: press(")"), width=BTN_W, height=BTN_H).grid(row=4, column=4, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='[', bg=sci_bg, fg=button_fg,command=lambda: press("["), width=BTN_W, height=BTN_H).grid(row=4, column=5, padx=4, pady=4, sticky="nsew")

# Row 5
Button(calc_tab, text='1', bg=button_bg, fg=button_fg, command=lambda: press("1"), width=BTN_W, height=BTN_H).grid(row=5, column=0, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='2', bg=button_bg, fg=button_fg, command=lambda: press("2"), width=BTN_W, height=BTN_H).grid(row=5, column=1, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='3', bg=button_bg, fg=button_fg, command=lambda: press("3"), width=BTN_W, height=BTN_H).grid(row=5, column=2, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='-', bg=button_bg, fg=button_fg, command=lambda: press("-"), width=BTN_W, height=BTN_H).grid(row=5, column=3, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='%', bg=sci_bg, fg=button_fg, command=lambda: press("%"), width=BTN_W, height=BTN_H).grid(row=5, column=4, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text=']', bg=sci_bg, fg=button_fg,command=lambda: press("]"), width=BTN_W, height=BTN_H).grid(row=5, column=5, padx=4, pady=4, sticky="nsew")

# Row 6
Button(calc_tab, text='0', bg=button_bg, fg=button_fg, command=lambda: press("0"), width=BTN_W, height=BTN_H).grid(row=6, column=0, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='.', bg=button_bg, fg=button_fg, command=lambda: press("."), width=BTN_W, height=BTN_H).grid(row=6, column=1, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='Clear', bg="#990000", fg="white", command=clear_all, width=BTN_W, height=BTN_H).grid(row=6, column=2, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='+', bg=button_bg, fg=button_fg, command=lambda: press("+"), width=BTN_W, height=BTN_H).grid(row=6, column=3, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='=', bg="#007700", fg="white", command=equal, width=BTN_W, height=BTN_H).grid(row=6, column=4, padx=4, pady=4, sticky="nsew")
Button(calc_tab, text='00', bg=sci_bg, fg=button_fg,command=lambda: press("00"), width=BTN_W, height=BTN_H).grid(row=6, column=5, padx=4, pady=4, sticky="nsew")

# ----------------- MAKE GRID EXPAND NICELY -----------------
# Give weight to rows/columns so sticky="nsew" stretches buttons
for r in range(0, 8):
    calc_tab.rowconfigure(r, weight=1)
# columns 0..5 are calculator; column 6 is history
for c in range(0, 7):
    calc_tab.columnconfigure(c, weight=1)

root.mainloop()
