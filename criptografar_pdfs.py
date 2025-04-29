import os
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pikepdf
import re
import PyPDF2
from io import StringIO

class PDFProtectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Protetor de PDF - Informatec")
        self.root.geometry("750x600")
        self.root.resizable(False, False)

        self.root.iconbitmap(r"C:\Reviant\Documentos\Codes\Python\Proteger PDF\icone.ico")
        
        # Configuração do estilo
        self.setup_style()
        
        # Variáveis de controle
        self.nome_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.senha_email_var = tk.StringVar()
        self.assunto_var = tk.StringVar()
        self.mensagem_var = tk.StringVar()
        self.cc_var = tk.StringVar()
        self.anexo_nome_var = tk.StringVar()
        self.diretorio_var = tk.StringVar()
        
        # Contadores para exibição
        self.sucessos_var = tk.StringVar(value="Sucessos: 0")
        self.erros_var = tk.StringVar(value="Erros: 0")
        self.avisos_var = tk.StringVar(value="Avisos: 0")
        
        self.setup_ui()
    
    def setup_style(self):
        """Configura os estilos da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores
        bg_color = "#f0f0f0"
        primary_color = "#2c3e50"
        secondary_color = "#3498db"
        accent_color = "#e74c3c"
        warning_color = "#f39c12"
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=5)
        style.configure('TEntry', font=('Helvetica', 10), padding=5)
        style.configure('TLabelFrame', background=bg_color, font=('Helvetica', 11, 'bold'))
        
        # Configuração específica para botões
        style.map('TButton',
                  foreground=[('active', 'white'), ('!disabled', 'white')],
                  background=[('active', secondary_color), ('!disabled', primary_color)])
        
        self.root.configure(background=bg_color)
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="Protetor de PDF", font=('Helvetica', 16, 'bold'), 
                 foreground="#2c3e50").pack(side=tk.LEFT)
        
        # Campos de entrada
        fields_frame = ttk.LabelFrame(main_frame, text=" Configurações ", padding="15")
        fields_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Grid de configuração para os campos
        fields_frame.columnconfigure(1, weight=1)
        
        # Lista de campos
        campos = [
            ("Nome*:", self.nome_var),
            ("Usuário Informatec*:", self.email_var),
            ("Senha do e-mail*:", self.senha_email_var, True),
            ("Assunto*:", self.assunto_var),
            ("Mensagem*:", self.mensagem_var),
            ("C/Cópia Oculta:", self.cc_var),
            ("Nome Anexo*:", self.anexo_nome_var)
        ]
        
        for i, (label, var, *opts) in enumerate(campos):
            ttk.Label(fields_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            show = "*" if opts and opts[0] else None
            ttk.Entry(fields_frame, textvariable=var, width=40, show=show).grid(
                row=i, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Diretório
        dir_frame = ttk.Frame(fields_frame)
        dir_frame.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=5)
        ttk.Label(dir_frame, text="Diretório dos PDFs*:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(dir_frame, textvariable=self.diretorio_var, width=30).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(dir_frame, text="Procurar", command=self.selecionar_diretorio, 
                  style='TButton').pack(side=tk.LEFT, padx=5)
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="Processar e Enviar", command=self.processar,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Sair", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # Contadores
        counters_frame = ttk.Frame(main_frame)
        counters_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(counters_frame, textvariable=self.sucessos_var, 
                 font=('Helvetica', 10, 'bold'), foreground="green").pack(side=tk.LEFT, padx=10)
        ttk.Label(counters_frame, textvariable=self.erros_var, 
                 font=('Helvetica', 10, 'bold'), foreground="red").pack(side=tk.LEFT, padx=10)
        ttk.Label(counters_frame, textvariable=self.avisos_var,
                 font=('Helvetica', 10, 'bold'), foreground="#f39c12").pack(side=tk.LEFT, padx=10)
        
        # Barra de status
        status_frame = ttk.Frame(main_frame, height=25)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar(value="Pronto para processar")
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, 
                 anchor=tk.W, font=('Helvetica', 9), background="#e0e0e0").pack(fill=tk.X)
        
        # Configurar estilo para o botão de ação principal
        style = ttk.Style()
        style.configure('Accent.TButton', background="#27ae60", foreground="white")
        style.map('Accent.TButton',
                 background=[('active', '#2ecc71'), ('!disabled', '#27ae60')])
        
    def selecionar_diretorio(self):
        diretorio = filedialog.askdirectory()
        if diretorio:
            self.diretorio_var.set(diretorio)
            self.atualizar_status(f"Diretório selecionado: {diretorio}")
    
    def atualizar_status(self, mensagem):
        self.status_var.set(mensagem)
        self.root.update()
    
    def get_log_filename(self):
        """Gera um nome de arquivo de log com data e hora no formato brasileiro"""
        now = datetime.now()
        return f"registro_de_eventos_{now.strftime('%d%m%Y_%H%M%S')}.txt"
    
    def escrever_log(self, mensagem, log_file):
        """Escreve uma mensagem no arquivo de log especificado"""
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        log_entry = f'[{timestamp}] {mensagem}\n'
        log_file.write(log_entry)
    
    def validar_matricula(self, matricula):
        """Verifica se a matrícula contém apenas números"""
        return matricula.isdigit()
    
    def validar_email(self, email):
        """Valida o formato do e-mail"""
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)
    
    def limpar_cpf(self, cpf):
        """Remove caracteres não numéricos do CPF e pega os 6 primeiros dígitos"""
        numeros = ''.join(filter(str.isdigit, cpf))
        return numeros[:6] if len(numeros) >= 6 else numeros
    
    def extrair_primeiro_ultimo_nome(self, nome_completo):
        """Extrai o primeiro e último nome de um nome completo"""
        partes = nome_completo.split()
        if len(partes) >= 2:
            return f"{partes[0]} {partes[-1]}"
        return nome_completo
    
    def verificar_nome_no_pdf(self, pdf_path, nome_completo):
        """Verifica se o primeiro e último nome estão contidos no texto do PDF, 
        com até 10 palavras de separação"""
        try:
            # Extrai primeiro e último nome
            partes = nome_completo.split()
            if len(partes) < 2:
                return False  # Não tem sobrenome
                
            primeiro_nome = partes[0].lower()
            ultimo_nome = partes[-1].lower()
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                texto_pdf = ""
                for page in reader.pages:
                    texto_pdf += page.extract_text() or ""
                
                texto_pdf = texto_pdf.lower()
                
                # Procura o padrão: primeiro nome + até 10 palavras + último nome
                padrao = re.compile(
                    r'\b' + re.escape(primeiro_nome) + 
                    r'(?:\W+\w+){0,10}\W+' + re.escape(ultimo_nome) + r'\b',
                    re.IGNORECASE
                )
                
                return bool(padrao.search(texto_pdf))
                
        except Exception as e:
            print(f"Erro ao verificar nome no PDF: {str(e)}")
            return False
    
    def proteger_pdf(self, arquivo_origem, senha, arquivo_destino):
        """Protege um arquivo PDF com senha"""
        try:
            pdf = pikepdf.open(arquivo_origem)
            pdf.save(arquivo_destino, encryption=pikepdf.Encryption(
                owner=senha, 
                user=senha, 
                R=4
            ))
            return True
        except Exception as e:
            print(f"Erro ao proteger PDF: {str(e)}")
            return False
    
    def enviar_email_gmail(self, destinatario, bcc, assunto, mensagem, anexo=None):
        """Envia um e-mail com anexo usando Gmail com CCO (BCC)"""
        try:
            # Configuração do e-mail
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_var.get()}@informatecservicos.com.br"
            msg['To'] = destinatario
            msg['Subject'] = assunto
            
            # Corpo do e-mail
            msg.attach(MIMEText(mensagem, 'plain'))
            
            # Anexo
            if anexo and os.path.exists(anexo):
                with open(anexo, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(anexo))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(anexo)}"'
                msg.attach(part)
            
            # Conexão com o servidor SMTP do Gmail
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.login(f"{self.email_var.get()}@informatecservicos.com.br", self.senha_email_var.get())
                
                # Lista de destinatários (incluindo BCC)
                destinatarios = [destinatario]
                if bcc:
                    # Permite múltiplos e-mails separados por vírgula ou ponto e vírgula
                    bcc_emails = [e.strip() for e in re.split(r'[;,]', bcc) if e.strip()]
                    destinatarios.extend(bcc_emails)

                
                server.sendmail(self.email_var.get(), destinatarios, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Erro ao enviar e-mail: {str(e)}")
            return False
    
    def validar_campos_obrigatorios(self):
        """Valida se todos os campos obrigatórios foram preenchidos"""
        campos = [
            ("Nome", self.nome_var.get()),
            ("Usuário Informatec", self.email_var.get()),
            ("Senha do e-mail", self.senha_email_var.get()),
            ("Assunto", self.assunto_var.get()),
            ("Mensagem", self.mensagem_var.get()),
            ("Nome Anexo", self.anexo_nome_var.get()),
            ("Diretório", self.diretorio_var.get())
        ]
        
        faltantes = [nome for nome, valor in campos if not valor]
        
        if faltantes:
            messagebox.showerror(
                "Campos obrigatórios faltando",
                f"Por favor, preencha os seguintes campos obrigatórios:\n\n- " + "\n- ".join(faltantes)
            )
            return False
        return True
    
    def processar(self):
        """Processa todos os PDFs conforme o CSV"""
        if not self.validar_campos_obrigatorios():
            return
            
        diretorio = self.diretorio_var.get()
        csv_path = os.path.join(diretorio, 'dados_aleatorios.csv')
        
        if not os.path.exists(csv_path):
            messagebox.showerror("Erro", f"Arquivo CSV não encontrado em {csv_path}!")
            return
        
        # Cria a pasta para PDFs processados
        pasta_processados = os.path.join(diretorio, "pdfs processados")
        if not os.path.exists(pasta_processados):
            os.makedirs(pasta_processados)
        
        # Cria um novo arquivo de log para este processamento
        log_filename = self.get_log_filename()
        sucessos = 0
        erros = 0
        avisos = 0
        
        try:
            with open(log_filename, 'w', encoding='utf-8') as log_file:
                self.escrever_log("=== INÍCIO DO PROCESSAMENTO ===", log_file)
                self.atualizar_status("Processando...")
                self.sucessos_var.set("Sucessos: 0")
                self.erros_var.set("Erros: 0")
                self.avisos_var.set("Avisos: 0")
                
                # Processa o CSV
                arquivos_processados = []
                arquivos_csv = []
                
                with open(csv_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    for linha, row in enumerate(reader, 1):
                        if len(row) < 5:
                            msg = f'AVISO: Linha {linha} do CSV incompleta - ignorada'
                            self.escrever_log(msg, log_file)
                            self.atualizar_status(msg)
                            avisos += 1
                            self.avisos_var.set(f"Avisos: {avisos}")
                            continue
                        
                        matricula, nome_completo, cpf, email, arquivo_origem = row[:5]
                        
                        # Validações dos dados do CSV
                        if not self.validar_matricula(matricula):
                            msg = f'ERRO: Matrícula inválida na linha {linha} - "{matricula}" (deve conter apenas números)'
                            self.escrever_log(msg, log_file)
                            self.atualizar_status(msg)
                            erros += 1
                            self.erros_var.set(f"Erros: {erros}")
                            continue
                        
                        if not self.validar_email(email):
                            msg = f'ERRO: E-mail inválido na linha {linha} - "{email}"'
                            self.escrever_log(msg, log_file)
                            self.atualizar_status(msg)
                            erros += 1
                            self.erros_var.set(f"Erros: {erros}")
                            continue
                        
                        arquivos_csv.append(arquivo_origem)
                        
                        # Verifica se o arquivo existe
                        arquivo_origem_path = os.path.join(diretorio, arquivo_origem)
                        if not os.path.exists(arquivo_origem_path):
                            msg = f'ERRO: PDF não encontrado - {arquivo_origem} (linha {linha} do CSV)'
                            self.escrever_log(msg, log_file)
                            self.atualizar_status(msg)
                            erros += 1
                            self.erros_var.set(f"Erros: {erros}")
                            continue
                        
                        # Verifica se o primeiro e último nome estão no PDF
                        if not self.verificar_nome_no_pdf(arquivo_origem_path, nome_completo):
                            nome_verificar = self.extrair_primeiro_ultimo_nome(nome_completo)
                            msg = f'AVISO: Nome "{nome_verificar}" não encontrado no PDF - {arquivo_origem} (linha {linha})'
                            self.escrever_log(msg, log_file)
                            self.atualizar_status(msg)
                            avisos += 1
                            self.avisos_var.set(f"Avisos: {avisos}")
                            continue
                        
                        # Prepara os dados
                        senha = self.limpar_cpf(cpf)
                        if not senha or len(senha) < 6:
                            msg = f'ERRO: CPF inválido para {nome_completo} - "{cpf}" (linha {linha}) - necessário pelo menos 6 dígitos'
                            self.escrever_log(msg, log_file)
                            self.atualizar_status(msg)
                            erros += 1
                            self.erros_var.set(f"Erros: {erros}")
                            continue
                        
                        nome_anexo = f"{self.anexo_nome_var.get()}_{matricula}.pdf"
                        arquivo_destino_path = os.path.join(pasta_processados, nome_anexo)
                        
                        # Primeiro protege o PDF
                        if self.proteger_pdf(arquivo_origem_path, senha, arquivo_destino_path):
                            # Se protegeu com sucesso, envia o e-mail
                            mensagem_personalizada = f"Olá, {nome_completo},\n\n{self.mensagem_var.get()}\n\nAtenciosamente,\n{self.nome_var.get()}"
                            
                            if self.enviar_email_gmail(email, self.cc_var.get(), self.assunto_var.get(), 
                                                   mensagem_personalizada, arquivo_destino_path):
                                msg = f'SUCESSO: PDF protegido e enviado para {email} - {nome_anexo}'
                                self.escrever_log(msg, log_file)
                                self.atualizar_status(msg)
                                sucessos += 1
                                self.sucessos_var.set(f"Sucessos: {sucessos}")
                                arquivos_processados.append(arquivo_origem)
                            else:
                                msg = f'ERRO: Falha ao enviar e-mail para {email}'
                                self.escrever_log(msg, log_file)
                                self.atualizar_status(msg)
                                erros += 1
                                self.erros_var.set(f"Erros: {erros}")
                                # Remove o PDF protegido se o envio falhou
                                if os.path.exists(arquivo_destino_path):
                                    os.remove(arquivo_destino_path)
                        else:
                            msg = f'ERRO: Falha ao proteger PDF - {arquivo_origem}'
                            self.escrever_log(msg, log_file)
                            self.atualizar_status(msg)
                            erros += 1
                            self.erros_var.set(f"Erros: {erros}")
                
                # Verifica PDFs no diretório que não estão no CSV
                pdfs_diretorio = [f for f in os.listdir(diretorio) if f.lower().endswith('.pdf')]
                for arquivo in pdfs_diretorio:
                    if arquivo not in arquivos_csv:
                        msg = f'AVISO: PDF não processado - {arquivo} (não listado no CSV)'
                        self.escrever_log(msg, log_file)
                        self.atualizar_status(msg)
                        avisos += 1
                        self.avisos_var.set(f"Avisos: {avisos}")
                
                # Resumo
                resumo = f"\nRESUMO: {sucessos} PDFs processados com sucesso | {erros} erros encontrados | {avisos} avisos"
                self.escrever_log(resumo, log_file)
                self.escrever_log("=== FIM DO PROCESSAMENTO ===", log_file)
                
                messagebox.showinfo("Concluído", 
                                 f"Processamento finalizado!\n\n"
                                 f"Sucessos: {sucessos}\n"
                                 f"Erros: {erros}\n"
                                 f"Avisos: {avisos}")
                self.atualizar_status(resumo)
                
        except Exception as e:
            erro_msg = f'ERRO CRÍTICO: {str(e)}'
            with open(log_filename, 'a', encoding='utf-8') as log_file:
                self.escrever_log(erro_msg, log_file)
            messagebox.showerror("Erro", f"Ocorreu um erro crítico: {str(e)}")
            self.atualizar_status("Erro durante o processamento")

def main():
    root = tk.Tk()
    
    # Define o ícone da aplicação (substitua pelo caminho do seu ícone)
    try:
        root.iconbitmap('icon.ico')  # Ou use um ícone padrão do sistema
    except:
        pass
    
    app = PDFProtectorApp(root)
    
    # Centraliza a janela na tela
    window_width = 750
    window_height = 650  # Aumentado para acomodar o contador de avisos
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    root.mainloop()

if __name__ == '__main__':
    main()