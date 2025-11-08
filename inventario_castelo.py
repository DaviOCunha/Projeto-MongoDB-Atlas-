import tkinter as tk
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet
from pymongo import MongoClient

key = Fernet.generate_key()
fernet = Fernet(key)

client = MongoClient("mongodb+srv://root:123@cluster0.1f9tlxf.mongodb.net/?appName=Cluster0")
db = client["castelo_db"]
collection = db["inventario"]

def criptografar_texto(texto):
    return fernet.encrypt(texto.encode()).decode()

def descriptografar_texto(texto):
    try:
        return fernet.decrypt(texto.encode()).decode()
    except Exception:
        return "[Descrição criptografada - chave incorreta ou inacessível]"

def salvar_item():
    item = entry_item.get().strip()
    descricao = text_descricao.get("1.0", tk.END).strip()
    raridade = combo_raridade.get()
    confidencial = var_confidencial.get()
    if not item or not raridade:
        messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
        return
    if confidencial:
        descricao = criptografar_texto(descricao)
    if collection.find_one({"item": item}):
        messagebox.showerror("Erro", "Já existe um item com esse nome.")
        return
    collection.insert_one({
        "item": item,
        "description": descricao,
        "rarity": raridade,
        "confidencial": confidencial
    })
    limpar_campos()
    atualizar_lista()
    messagebox.showinfo("Sucesso", "Item salvo com sucesso!")

def atualizar_item():
    selecionado = lista.focus()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um item para editar.")
        return
    item_antigo = lista.item(selecionado)["values"][0]
    novo_item = entry_item.get().strip()
    nova_raridade = combo_raridade.get()
    nova_descricao = text_descricao.get("1.0", tk.END).strip()
    novo_conf = var_confidencial.get()
    if not novo_item or not nova_raridade:
        messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
        return
    if novo_conf:
        nova_descricao = criptografar_texto(nova_descricao)
    collection.update_one(
        {"item": item_antigo},
        {"$set": {
            "item": novo_item,
            "description": nova_descricao,
            "rarity": nova_raridade,
            "confidencial": novo_conf
        }}
    )
    limpar_campos()
    atualizar_lista()
    messagebox.showinfo("Atualizado", f"Item '{item_antigo}' atualizado com sucesso!")

def excluir_item():
    selecionado = lista.focus()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um item para excluir.")
        return
    item_nome = lista.item(selecionado)["values"][0]
    if messagebox.askyesno("Confirmação", f"Deseja excluir '{item_nome}'?"):
        collection.delete_one({"item": item_nome})
        atualizar_lista()
        messagebox.showinfo("Excluído", f"Item '{item_nome}' removido!")

def ver_item():
    selecionado = lista.focus()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um item.")
        return
    item_nome = lista.item(selecionado)["values"][0]
    doc = collection.find_one({"item": item_nome})
    descricao = doc["description"]
    if doc["confidencial"]:
        descricao = descriptografar_texto(descricao)
    messagebox.showinfo(f"Item: {item_nome}",
                        f"Raridade: {doc['rarity']}\n\nDescrição:\n{descricao}")

def carregar_para_edicao():
    selecionado = lista.focus()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um item para editar.")
        return
    item_nome = lista.item(selecionado)["values"][0]
    doc = collection.find_one({"item": item_nome})
    entry_item.delete(0, tk.END)
    entry_item.insert(0, doc["item"])
    combo_raridade.set(doc["rarity"])
    desc = doc["description"]
    if doc["confidencial"]:
        desc = descriptografar_texto(desc)
    text_descricao.delete("1.0", tk.END)
    text_descricao.insert("1.0", desc)
    var_confidencial.set(doc["confidencial"])

def limpar_campos():
    entry_item.delete(0, tk.END)
    text_descricao.delete("1.0", tk.END)
    combo_raridade.set("")
    var_confidencial.set(False)

def atualizar_lista():
    lista.delete(*lista.get_children())
    for doc in collection.find():
        lista.insert("", tk.END, values=(
            doc["item"],
            doc["rarity"],
            "Sim" if doc["confidencial"] else "Não"
        ))

root = tk.Tk()
root.title("🏰 Inventário Criptografado — CRUD MongoDB")
root.geometry("780x620")
root.resizable(False, False)

bg, fg, accent = "#1e1e2e", "#f8f8f2", "#b689f0"
root.configure(bg=bg)

titulo = tk.Label(root, text="🏰 Inventário Criptografado 🕯️", bg=bg, fg=accent, font=('Garamond', 20, 'bold'))
titulo.pack(pady=15)

frame_form = tk.LabelFrame(root, text="Gerenciar Item", bg=bg, fg=accent, padx=10, pady=10, font=('Segoe UI', 10, 'bold'))
frame_form.pack(padx=10, pady=10, fill="x")

tk.Label(frame_form, text="Item:", bg=bg, fg=fg).grid(row=0, column=0, sticky="w")
entry_item = tk.Entry(frame_form, width=45, bg="#2b2b3c", fg="white", insertbackground="white", relief="flat")
entry_item.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Raridade:", bg=bg, fg=fg).grid(row=1, column=0, sticky="w")
combo_raridade = ttk.Combobox(frame_form, values=["COMUM", "RARO", "ÉPICO", "LENDÁRIO"], state="readonly", width=42)
combo_raridade.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Descrição:", bg=bg, fg=fg).grid(row=2, column=0, sticky="nw")
text_descricao = tk.Text(frame_form, width=55, height=5, bg="#2b2b3c", fg="white", insertbackground="white", relief="flat")
text_descricao.grid(row=2, column=1, padx=5, pady=5)

var_confidencial = tk.BooleanVar()
tk.Checkbutton(frame_form, text="Descrição confidencial (criptografar com Fernet)", variable=var_confidencial,
               bg=bg, fg=fg, selectcolor=bg, activebackground=bg).grid(row=3, column=1, sticky="w", pady=5)

frame_botoes = tk.Frame(frame_form, bg=bg)
frame_botoes.grid(row=4, column=1, pady=10, sticky="e")

def criar_botao(texto, comando, cor):
    btn = tk.Button(frame_botoes, text=texto, command=comando, bg=cor, fg="white",
                    activebackground="#6c3483", font=('Segoe UI', 10, 'bold'),
                    relief="flat", cursor="hand2", width=12, height=1)
    btn.bind("<Enter>", lambda e: btn.config(bg="#9b59b6"))
    btn.bind("<Leave>", lambda e: btn.config(bg=cor))
    return btn

botoes = [
    ("💾 Adicionar", salvar_item, "#8e44ad"),
    ("📋 Carregar", carregar_para_edicao, "#f39c12"),
    ("✏️ Atualizar", atualizar_item, "#27ae60"),
    ("🗑️ Excluir", excluir_item, "#c0392b"),
    ("🔍 Ver", ver_item, "#2980b9")
]

for i, (txt, cmd, cor) in enumerate(botoes):
    criar_botao(txt, cmd, cor).grid(row=0, column=i, padx=4)

frame_lista = tk.LabelFrame(root, text="Itens Registrados", bg=bg, fg=accent, font=('Segoe UI', 10, 'bold'))
frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

colunas = ("item", "raridade", "confidencial")
lista = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=10)
for col in colunas:
    lista.heading(col, text=col.capitalize())
    lista.column(col, anchor="center")
lista.pack(fill="both", expand=True)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#2b2b3c", fieldbackground="#2b2b3c", foreground="white", rowheight=26)
style.configure("Treeview.Heading", background=accent, foreground="white", font=('Segoe UI', 10, 'bold'))
style.map("Treeview", background=[("selected", "#6c3483")])

atualizar_lista()
root.mainloop()
