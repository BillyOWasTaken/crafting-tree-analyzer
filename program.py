import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
import sympy as sp



base_materials = set()
craftables = dict()

def build_tree(target, graph):
 
    if target in craftables:
        for ingredient, coeff in craftables[target].items():
            graph.add_edge(target, ingredient)
            if ingredient in craftables:
                build_tree(ingredient, graph)

def hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    pos = {}

    def _hierarchy_pos(G, root, left, right, vert_loc):
        pos[root] = ((left + right) / 2, vert_loc)
        children = list(G.successors(root))
        if children:
            dx = (right - left) / len(children)
            nextx = left
            for child in children:
                _hierarchy_pos(G, child, nextx, nextx + dx, vert_loc - vert_gap)
                nextx += dx

    _hierarchy_pos(G, root, 0, width, vert_loc)
    return pos


def visualize_tree(target):
    if target not in craftables:
        messagebox.showerror("Error", "Target must be a craftable item.")
        return

    G = nx.DiGraph()
    build_tree(target, G)

    pos = hierarchy_pos(G, target)

    plt.figure(figsize=(10, 6))
    nx.draw_networkx(G, pos, arrows=False, node_size=1500, node_color="lightblue")
    plt.title(f"Crafting Tree for '{target}'")
    plt.show()


def add_base_material():
    name = base_entry.get().strip()
    if not name:
        return
    base_materials.add(name)
    base_entry.delete(0, tk.END)
    update_lists()

def add_craftable():
    name = craftable_entry.get().strip()
    recipe_text = recipe_entry.get().strip()

    if not name or not recipe_text:
        return

    recipe = {}
    for part in recipe_text.split(","):
        ing, qty = part.split(":")
        ing = ing.strip()
        qty = int(qty.strip())

        if ing not in base_materials and ing not in craftables:
            messagebox.showerror(
                "Invalid Ingredient",
                f"'{ing}' is not a base material or craftable item."
            )
            return

        recipe[ing] = qty

    craftables[name] = recipe
    craftable_entry.delete(0, tk.END)
    recipe_entry.delete(0, tk.END)
    update_lists()

def update_lists():
    base_list.configure(text="Base Materials:\n" + "\n".join(base_materials))
    craft_list.configure(
        text="Craftable Items:\n" +
        "\n".join(f"{k}: {v}" for k, v in craftables.items())
    )

def visualize():
    target = target_entry.get().strip()
    visualize_tree(target)

def calculate_total_requirements(target):
    if target not in craftables:
        messagebox.showerror("Error", "Target must be a craftable item.")
        return

    total_requirements = {}

    def dfs(item, multiplier):
        if item in base_materials:
            total_requirements[item] = total_requirements.get(item, 0) + multiplier
        elif item in craftables:
            for ingredient, qty in craftables[item].items():
                dfs(ingredient, multiplier * qty)

    dfs(target, 1)

    result = "Total Base Material Requirements:\n" + "\n".join(f"{k}: {v}" for k, v in total_requirements.items())
    messagebox.showinfo("Analysis Result", result)

def detect_resource_exploits(target):
    if target not in craftables:
        messagebox.showerror("Error", "Target must be a craftable item.")
        return

    equations = []
    variables = set()

    def build_equations(item, multiplier):
        if item in base_materials:
            variables.add(item)
            return {item: multiplier}
        elif item in craftables:
            equation = {}
            for ingredient, qty in craftables[item].items():
                sub_eq = build_equations(ingredient, multiplier * qty)
                for k, v in sub_eq.items():
                    equation[k] = equation.get(k, 0) + v
            return equation

    target_eq = build_equations(target, 1)
    equations.append((target_eq, 1))

    sp_vars = {v: sp.symbols(v) for v in variables}
    sp_eqs = [
        sp.Eq(sum(coeff * sp_vars[var] for var, coeff in eq.items()), rhs)
        for eq, rhs in equations
    ]

    solutions = sp.linsolve(sp_eqs, *sp_vars.values())

    if len(solutions) > 1:
        messagebox.showwarning("Resource Exploit Detected", "Multiple distinct solutions exist for crafting the target item.")
    else:
        messagebox.showinfo("Analysis Result", "No resource exploits detected.")

# UI Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Crafting Tree Visualizer")
app.geometry("700x600")

frame = ctk.CTkFrame(app)
frame.pack(padx=20, pady=20, fill="both", expand=True)

# Base Materials
ctk.CTkLabel(frame, text="Add Base Material").pack()
base_entry = ctk.CTkEntry(frame)
base_entry.pack()
ctk.CTkButton(frame, text="Add Base", command=add_base_material).pack(pady=5)

# Craftables
ctk.CTkLabel(frame, text="Add Craftable Item").pack(pady=(15, 0))
craftable_entry = ctk.CTkEntry(frame, placeholder_text="Item name")
craftable_entry.pack()

recipe_entry = ctk.CTkEntry(
    frame, placeholder_text="example recipe: wood:2, iron:1"
)
recipe_entry.pack()

ctk.CTkButton(frame, text="Add Craftable", command=add_craftable).pack(pady=5)

# Visualization
ctk.CTkLabel(frame, text="Visualize Crafting Tree").pack(pady=(20, 0))
target_entry = ctk.CTkEntry(frame, placeholder_text="Target item")
target_entry.pack()

ctk.CTkButton(frame, text="Visualize Tree", command=visualize).pack(pady=10)

# Analysis
ctk.CTkButton(frame, text="Calculate Requirements", command=lambda: calculate_total_requirements(target_entry.get().strip())).pack(pady=5)
ctk.CTkButton(frame, text="Detect Exploits", command=lambda: detect_resource_exploits(target_entry.get().strip())).pack(pady=5)

# Lists
base_list = ctk.CTkLabel(frame, text="Base Materials:")
base_list.pack(pady=5)

craft_list = ctk.CTkLabel(frame, text="Craftable Items:")
craft_list.pack(pady=5)

app.mainloop()
