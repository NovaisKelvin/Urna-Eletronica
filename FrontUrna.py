# front_urna.py
# Interface Tkinter da urna. Usa as funcoes do backend_urna.py.
# Os dois arquivos precisam estar na mesma pasta.

import tkinter as tk
import backend_urna as backend

PORTA_PADRAO = "/dev/ttyACM0"

# Mensagem mostrada na tela para cada resposta do backend
MENSAGENS = {
    "CAND1": "Voto registrado: Candidato 1",
    "CAND2": "Voto registrado: Candidato 2",
    "NULO": "Voto nulo registrado",
    "CANCELADO": "Operacao cancelada",
    "INVALIDO": "Numero invalido: voto nao contado",
    "PARADA": "Inicie a aquisicao para votar",
    "": ""
}

janela = tk.Tk()
janela.title("Urna Eletronica")
janela.geometry("520x640")
janela.resizable(False, False)

# ---------------- Titulo ----------------
titulo = tk.Label(janela, text="Urna Eletronica", font=("Arial", 16, "bold"))
titulo.grid(row=0, column=1, columnspan=5, pady=10)

# ---------------- Campo do candidato ----------------
candidato = tk.Label(janela, text="Candidato:", font=("Arial", 11))
candidato.grid(row=1, column=0, padx=10, pady=10)

texto_numero = tk.StringVar()   # texto que aparece no campo
entry_candidato = tk.Entry(janela, textvariable=texto_numero, width=30,
                           font=("Arial", 12), state="readonly")
entry_candidato.grid(row=1, column=1, columnspan=3, padx=5, pady=10)


# ---------------- Funcoes dos botoes ----------------
def pressionar_digito(digito):
    backend.digitar(digito)
    atualizar_tela()


def pressionar(comando):
    backend.executar(comando)
    atualizar_tela()


def iniciar():
    porta = entry_porta.get().strip()
    backend.iniciar_aquisicao(porta)
    atualizar_tela()


def interromper():
    backend.parar_aquisicao()
    atualizar_tela()


def fechar():
    backend.parar_aquisicao()       # fecha a porta Serial antes de fechar a janela
    janela.destroy()


# ---------------- Teclado numerico ----------------
botoes = {
    "1": (2, 1), "2": (2, 2), "3": (2, 3),
    "4": (3, 1), "5": (3, 2), "6": (3, 3),
    "7": (4, 1), "8": (4, 2), "9": (4, 3),
    "0": (5, 2)
}

for numero, (linha, coluna) in botoes.items():
    # "n=numero" guarda o numero deste botao (sem isso, todos usariam o ultimo valor)
    botao = tk.Button(janela, text=numero, width=5, font=("Arial", 11),
                      command=lambda n=numero: pressionar_digito(n))
    botao.grid(row=linha, column=coluna, padx=4, pady=3)

botaoconfirmar = tk.Button(janela, text="Confirmar", bg="#28A745", fg="white", width=10,
                           command=lambda: pressionar("CONFIRMAR"))
botaoconfirmar.grid(row=6, column=1, pady=12)

botaonega = tk.Button(janela, text="Cancelar", bg="#FF0000", fg="white", width=10,
                      command=lambda: pressionar("CANCELAR"))
botaonega.grid(row=6, column=2, pady=12)

botaonullo = tk.Button(janela, text="Anular", bg="#363434", fg="white", width=10,
                       command=lambda: pressionar("ANULAR"))
botaonullo.grid(row=6, column=3, pady=12)

# ---------------- Aviso ----------------
label_aviso = tk.Label(janela, text="", font=("Arial", 11, "italic"))
label_aviso.grid(row=7, column=0, columnspan=5, pady=4)

# ---------------- Porta e aquisicao ----------------
label_porta = tk.Label(janela, text="Porta:", font=("Arial", 11))
label_porta.grid(row=8, column=0, padx=10, pady=6)

entry_porta = tk.Entry(janela, width=30, font=("Arial", 12))
entry_porta.insert(0, PORTA_PADRAO)
entry_porta.grid(row=8, column=1, columnspan=3, padx=5, pady=6)

botao_iniciar = tk.Button(janela, text="Iniciar", width=10, command=iniciar)
botao_iniciar.grid(row=9, column=1, pady=6)

botao_interromper = tk.Button(janela, text="Interromper", width=10, command=interromper)
botao_interromper.grid(row=9, column=2, pady=6)

# ---------------- Estados e resultados ----------------
label_aquisicao = tk.Label(janela, text="", font=("Arial", 11))
label_aquisicao.grid(row=10, column=0, columnspan=5)

label_comunicacao = tk.Label(janela, text="", font=("Arial", 11))
label_comunicacao.grid(row=11, column=0, columnspan=5)

label_c1 = tk.Label(janela, text="", font=("Arial", 12))
label_c1.grid(row=12, column=0, columnspan=5, pady=(10, 0))

label_c2 = tk.Label(janela, text="", font=("Arial", 12))
label_c2.grid(row=13, column=0, columnspan=5)

label_nulo = tk.Label(janela, text="", font=("Arial", 12))
label_nulo.grid(row=14, column=0, columnspan=5)

label_total = tk.Label(janela, text="", font=("Arial", 12, "bold"))
label_total.grid(row=15, column=0, columnspan=5)


# ---------------- Atualizacao da tela ----------------
def atualizar_tela():
    texto_numero.set(backend.numero_digitado)
    label_aviso.config(text=MENSAGENS.get(backend.ultima_resposta, ""))

    label_c1.config(text="Candidato 1: " + str(backend.votos["Candidato 1"]))
    label_c2.config(text="Candidato 2: " + str(backend.votos["Candidato 2"]))
    label_nulo.config(text="Voto NULO: " + str(backend.votos["Voto NULO"]))
    label_total.config(text="Total de votos: " + str(backend.total_votos()))

    label_comunicacao.config(text="Comunicacao: " + backend.estado_comunicacao)

    if backend.aquisicao_ativa:
        label_aquisicao.config(text="Aquisicao: ATIVA")
        botao_iniciar.config(state="disabled")
        botao_interromper.config(state="normal")
    else:
        label_aquisicao.config(text="Aquisicao: PARADA")
        botao_iniciar.config(state="normal")
        botao_interromper.config(state="disabled")


def ciclo():
    """Roda a cada 100 ms: le o Arduino e atualiza a tela, sem travar a janela."""
    backend.ler_arduino()
    atualizar_tela()
    janela.after(100, ciclo)


janela.protocol("WM_DELETE_WINDOW", fechar)   # ao clicar no X, chama fechar()
ciclo()
janela.mainloop()