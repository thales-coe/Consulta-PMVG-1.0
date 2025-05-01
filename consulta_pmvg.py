import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import re
import webbrowser
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Dependências:
# pip install pandas openpyxl xlrd requests beautifulsoup4

# Configura pasta de dados
if getattr(sys, 'frozen', False):
    base_folder = os.path.dirname(sys.executable)
else:
    base_folder = os.path.join(os.path.expanduser("~"), "Documents")
BASE_DIR = os.path.join(base_folder, "ConsultaPMVGData")
os.makedirs(BASE_DIR, exist_ok=True)

ICMS_RATES = {
    'AC': 17, 'AL': 18, 'AP': 18, 'AM': 18, 'BA': 18, 'CE': 18,
    'DF': 18, 'ES': 17, 'GO': 18, 'MA': 18, 'MT': 17, 'MS': 17,
    'MG': 18, 'PA': 18, 'PB': 18, 'PR': 18, 'PE': 18, 'PI': 18,
    'RJ': 20, 'RN': 18, 'RS': 18, 'RO': 17, 'RR': 18, 'SC': 17,
    'SP': 18, 'SE': 18, 'TO': 18
}

def detect_header_row(path):
    df0 = pd.read_excel(path, header=None, nrows=100,
                        engine='xlrd' if path.lower().endswith('.xls') else 'openpyxl')
    for idx, row in df0.iterrows():
        headers = [str(x).strip().upper() for x in row]
        if 'PRODUTO' in headers and 'APRESENTAÇÃO' in headers:
            return idx
    raise RuntimeError("Linha de cabeçalho não encontrada.")

def normalize_df(df):
    mapping = {}
    for col in df.columns:
        name = str(col).strip().upper()
        if 'PRODUTO' in name:
            mapping[col] = 'Nome do Produto'
        elif 'APRESENTAÇÃO' in name:
            mapping[col] = 'Apresentação'
        elif 'LABORATÓRIO' in name or 'MARCA' in name:
            mapping[col] = 'Marca'
    df = df.rename(columns=mapping)
    df = df.loc[:, ~df.columns.duplicated()]
    price_cols = [c for c in df.columns if 'PMVG' in c.upper() or 'PMC' in c.upper()]
    for c in price_cols:
        df[c] = pd.to_numeric
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import re
import webbrowser
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Dependências:
# pip install pandas openpyxl xlrd requests beautifulsoup4

# Configura pasta de dados
if getattr(sys, 'frozen', False):
    base_folder = os.path.dirname(sys.executable)
else:
    base_folder = os.path.join(os.path.expanduser("~"), "Documents")
BASE_DIR = os.path.join(base_folder, "ConsultaPMVGData")
os.makedirs(BASE_DIR, exist_ok=True)

ICMS_RATES = {
    'AC': 17, 'AL': 18, 'AP': 18, 'AM': 18, 'BA': 18, 'CE': 18,
    'DF': 18, 'ES': 17, 'GO': 18, 'MA': 18, 'MT': 17, 'MS': 17,
    'MG': 18, 'PA': 18, 'PB': 18, 'PR': 18, 'PE': 18, 'PI': 18,
    'RJ': 20, 'RN': 18, 'RS': 18, 'RO': 17, 'RR': 18, 'SC': 17,
    'SP': 18, 'SE': 18, 'TO': 18
}

def detect_header_row(path):
    df0 = pd.read_excel(path, header=None, nrows=100,
                        engine='xlrd' if path.lower().endswith('.xls') else 'openpyxl')
    for idx, row in df0.iterrows():
        headers = [str(x).strip().upper() for x in row]
        if 'PRODUTO' in headers and 'APRESENTAÇÃO' in headers:
            return idx
    raise RuntimeError("Linha de cabeçalho não encontrada.")

def normalize_df(df):
    mapping = {}
    for col in df.columns:
        name = str(col).strip().upper()
        if 'PRODUTO' in name:
            mapping[col] = 'Nome do Produto'
        elif 'APRESENTAÇÃO' in name:
            mapping[col] = 'Apresentação'
        elif 'LABORATÓRIO' in name or 'MARCA' in name:
            mapping[col] = 'Marca'
    df = df.rename(columns=mapping)
    df = df.loc[:, ~df.columns.duplicated()]
    price_cols = [c for c in df.columns if 'PMVG' in c.upper() or 'PMC' in c.upper()]
    for c in price_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df[['Nome do Produto', 'Marca', 'Apresentação'] + price_cols]

def load_base(path):
    hdr = detect_header_row(path)
    eng = 'xlrd' if path.lower().endswith('.xls') else 'openpyxl'
    df = pd.read_excel(path, header=hdr, engine=eng)
    df = df.loc[:, ~df.columns.duplicated()]
    return normalize_df(df)

def extract_base_date(path):
    m = re.search(r'gov_(\d{8})', path)
    if m:
        return datetime.strptime(m.group(1), '%Y%m%d')
    return datetime.fromtimestamp(os.path.getmtime(path))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Consulta PMVG 1.0")
        self.geometry("600x500")
        self.resizable(False, False)

        try:
            self.base_path, self.base_date = self.download_latest_base_progress()
        except Exception as e:
            messagebox.showerror("Erro ao baixar base", str(e))
            self.destroy()
            return

        self.df = None
        self.state = None
        self.med = None
        self.brand = None
        self.pres = None
        self.full_meds = []

        self.init_welcome()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def download_latest_base_progress(self):
        url_base = "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url_base, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        link_tag = None
        for a in soup.find_all("a", class_="govbr-card-content", href=True):
            titulo = a.find("span", class_="titulo")
            if titulo and re.search(r"PMVG\s*-\s*xls", titulo.get_text(strip=True), re.I):
                link_tag = a
                break
        if not link_tag:
            raise RuntimeError("Link da base PMVG - xls não encontrado.")
        file_url = link_tag["href"]
        if not file_url.startswith("http"):
            file_url = "https://www.gov.br" + file_url
        file_url = file_url.split("/@@")[0]
        filename = os.path.basename(file_url)
        local_path = os.path.join(BASE_DIR, filename)
        # se já existe, retorna data
        if os.path.exists(local_path):
            return local_path, extract_base_date(local_path)
        # cria janela modal
        prog = tk.Toplevel(self)
        prog.title("Baixando base")
        prog.geometry("450x120")
        prog.resizable(False, False)
        ttk.Label(prog, text="Baixando base mais recente...").pack(pady=(20,5))
        bar = ttk.Progressbar(prog, orient="horizontal", length=400, mode="determinate")
        bar.pack(pady=(5,10))
        prog.transient(self); prog.grab_set(); self.update_idletasks()
        # stream download
        r = requests.get(file_url, headers=headers, stream=True)
        r.raise_for_status()
        total = int(r.headers.get('content-length',0))
        bar['maximum'] = total
        chunk = 1024*10
        done = 0
        with open(local_path,'wb') as f:
            for data in r.iter_content(chunk_size=chunk):
                if not data: continue
                f.write(data)
                done += len(data)
                bar['value'] = done
                prog.update_idletasks()
        prog.destroy()
        return local_path, extract_base_date(local_path)

    def init_welcome(self):
        self.clear()
        ttk.Label(self,
            text=("Este é um projeto Open Source, "
                  "voltado a consulta em tempo real do Preço Máximo de Venda ao Governo conforme definido pela CMED/ANVISA"),
            wraplength=560, justify="center", font=("Arial",12)
        ).pack(pady=(20,10))
        dt = self.base_date.strftime("%d/%m/%Y")
        ttk.Label(self, text=f"Usando base CMED de {dt}",
                  font=("Arial",12), wraplength=560, justify="center"
        ).pack(pady=(5,10))
        link="https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos"
        lbl=tk.Label(self,text=link,fg="blue",cursor="hand2")
        lbl.pack(); lbl.bind("<Button-1>",lambda e:webbrowser.open_new(link))
        ttk.Button(self, text="Avançar", command=self.load_and_state).pack(pady=20)
        ttk.Label(self, text="Licença: CC BY-SA | Desenvolvido por Thales Coelho",
                  font=("Arial",9), foreground="gray"
        ).pack(side='bottom', pady=10)

    def load_and_state(self):
        self.clear()
        lbl = ttk.Label(self, text="Carregando base...", font=("Arial",12))
        lbl.pack(side='bottom', fill='x', pady=5)
        pb = ttk.Progressbar(self, mode='indeterminate')
        pb.pack(side='bottom', fill='x', padx=20, pady=5)
        pb.start(); self.update_idletasks()
        try:
            self.df = load_base(self.base_path)
        except Exception as e:
            pb.stop()
            messagebox.showerror("Erro ao carregar base",str(e))
            return
        pb.stop(); lbl.destroy(); pb.destroy()
        self.init_state()

    def init_state(self):
        self.clear()
        ttk.Label(self, text="Selecione o estado:", font=("Arial",12)).pack(pady=10)
        self.state_var = tk.StringVar()
        cb = ttk.Combobox(self, textvariable=self.state_var,
                          values=[f"{st} ({ICMS_RATES[st]}%)" for st in ICMS_RATES],
                          state="readonly")
        cb.pack(fill='x', padx=20)
        ttk.Button(self, text="Avançar", command=self.advance_state).pack(pady=20)

    def advance_state(self):
        sel = self.state_var.get().split()[0]
        if sel in ICMS_RATES:
            self.state = sel
            self.init_med()
        else:
            messagebox.showwarning("Atenção","Selecione um estado válido.")

    def init_med(self):
        self.clear()
        ttk.Label(self, text="Digite o medicamento (mín 3 caracteres):",
                  font=("Arial",12)).pack(pady=10)
        self.full_meds = sorted(self.df['Nome do Produto'].dropna().unique())
        self.med_var = tk.StringVar()
        self.med_entry = ttk.Entry(self, textvariable=self.med_var)
        self.med_entry.pack(fill='x', padx=20)
        self.med_entry.bind('<KeyRelease>', self.update_med_list)
        self.med_listbox = tk.Listbox(self, height=5)
        self.med_listbox.pack_forget()
        self.med_listbox.bind('<<ListboxSelect>>', self.on_med_select)
        ttk.Button(self, text="Avançar", command=self.advance_med).pack(pady=20)

    def update_med_list(self, event):
        text = self.med_var.get().strip().lower()
        if text:
            filt = [m for m in self.full_meds if text in m.lower()]
        else:
            filt = []
        if filt:
            self.med_listbox.delete(0, tk.END)
            for m in filt[:10]:
                self.med_listbox.insert(tk.END, m)
            self.med_listbox.pack(fill='x', padx=20)
        else:
            self.med_listbox.pack_forget()

    def on_med_select(self, event):
        sel = self.med_listbox.curselection()
        if sel:
            val = self.med_listbox.get(sel[0])
            self.med_var.set(val)
        self.med_listbox.pack_forget()

    def advance_med(self):
        m = self.med_var.get().strip()
        if len(m) < 3:
            messagebox.showwarning("Atenção","Digite pelo menos 3 caracteres.")
            return
        matches = [x for x in self.full_meds if m.lower() in x.lower()]
        if not matches:
            messagebox.showwarning("Atenção","Nenhum medicamento encontrado.")
            return
        self.med = matches[0]
        brands = sorted(self.df.loc[self.df['Nome do Produto']==self.med,
                                     'Marca'].dropna().unique())
        if not brands:
            messagebox.showwarning("Atenção","Nenhuma marca encontrada.")
            return
        self.brands = brands
        self.init_brand()

    def init_brand(self):
        self.clear()
        ttk.Label(self, text=f"Medicamento: {self.med}", font=("Arial",12)).pack(pady=10)
        ttk.Label(self, text="Selecione a marca:", font=("Arial",12)).pack(pady=10)
        self.brand_var = tk.StringVar()
        cb = ttk.Combobox(self, textvariable=self.brand_var,
                          values=self.brands, state="readonly")
        cb.pack(fill='x', padx=20)
        ttk.Button(self, text="Avançar", command=self.advance_brand).pack(pady=20)

    def advance_brand(self):
        b = self.brand_var.get()
        if not b:
            messagebox.showwarning("Atenção","Selecione uma marca.")
            return
        pres = sorted(self.df.loc[
            (self.df['Nome do Produto']==self.med)&
            (self.df['Marca']==b),
            'Apresentação'
        ].dropna().unique())
        if not pres:
            messagebox.showwarning("Atenção","Nenhuma apresentação encontrada.")
            return
        self.pres_list = pres
        self.init_pres()

    def init_pres(self):
        self.clear()
        ttk.Label(self, text=f"Medicamento: {self.med}", font=("Arial",12)).pack(pady=5)
        ttk.Label(self, text=f"Marca: {self.brand_var.get()}", font=("Arial",12)).pack(pady=5)
        ttk.Label(self, text="Selecione a apresentação:", font=("Arial",12)).pack(pady=10)
        self.pres_var = tk.StringVar()
        cb = ttk.Combobox(self, textvariable=self.pres_var,
                          values=self.pres_list, state="readonly")
        cb.pack(fill='x', padx=20)
        ttk.Button(self, text="Mostrar preço", command=self.advance_pres).pack(pady=20)

    def advance_pres(self):
        p = self.pres_var.get()
        if not p:
            messagebox.showwarning("Atenção","Selecione uma apresentação.")
            return
        self.pres = p
        self.show_price()

    def show_price(self):
        row = self.df[
            (self.df['Nome do Produto']==self.med)&
            (self.df['Marca']==self.brand_var.get())&
            (self.df['Apresentação']==self.pres)
        ]
        if row.empty:
            messagebox.showerror("Erro","Dados não encontrados.")
            return
        price_col = [c for c in row.columns if 'PMVG' in c.upper() or 'PMC' in c.upper()][0]
        price = row[price_col].iloc[0]
        icms = ICMS_RATES[self.state]
        final = price * (1 + icms/100)
        self.clear()
        ttk.Label(self, text=f"Preço s/ ICMS: R$ {price:,.2f}", font=("Arial",12)).pack(pady=10)
        ttk.Label(self, text=f"Preço c/ ICMS ({icms}%): R$ {final:,.2f}", font=("Arial",12)).pack(pady=10)
        ttk.Button(self, text="Nova consulta", command=self.init_welcome).pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
