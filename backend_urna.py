# backend_urna.py
# Backend da urna: conta os votos, trata os comandos e conversa com o Arduino.
# Este arquivo NAO usa Tkinter. Quem cria a janela e o front_urna.py.

try:
    import serial          # biblioteca pyserial
except ImportError:
    serial = None          # sem pyserial o programa ainda abre (modo teste, sem Arduino)


# ---------------------------------------------------------------
# DADOS DA URNA
# ---------------------------------------------------------------

# Numero digitado na tela -> nome da opcao
candidatos = {
    "1": "Candidato 1",
    "2": "Candidato 2"
}

# Contagem de votos
votos = {
    "Candidato 1": 0,
    "Candidato 2": 0,
    "Voto NULO": 0
}

numero_digitado = ""            # numero que a pessoa esta digitando na tela
aquisicao_ativa = False         # True = votacao aberta
ultima_resposta = ""            # ultimo resultado (a tela usa para mostrar um aviso)

conexao = None                  # porta Serial aberta (None = sem conexao)
estado_comunicacao = "Desconectado"


# ---------------------------------------------------------------
# CONTAGEM (as mesmas funcoes das etapas anteriores)
# ---------------------------------------------------------------

def registrar_voto(opcao):
    """Soma 1 ao contador da opcao. Retorna True se contou, False se a opcao nao existe."""
    if opcao in votos:
        votos[opcao] += 1
        return True
    else:
        return False


def total_votos():
    """Soma os votos de todas as opcoes."""
    return sum(votos.values())


def zerar_votos():
    """Volta todos os contadores para zero (nova votacao)."""
    for opcao in votos:
        votos[opcao] = 0


# ---------------------------------------------------------------
# AS TRES ACOES DA URNA
# Cada uma devolve um codigo de resposta (texto) que tambem e enviado ao Arduino.
# ---------------------------------------------------------------

def digitar(digito):
    """Acrescenta um digito ao numero (maximo 2 digitos). So funciona com a aquisicao ativa."""
    global numero_digitado, ultima_resposta
    if not aquisicao_ativa:
        ultima_resposta = "PARADA"
        return
    if len(numero_digitado) < 2:
        numero_digitado = numero_digitado + digito


def confirmar():
    """Confirma o numero digitado. Se for de um candidato, conta o voto."""
    global numero_digitado
    numero = numero_digitado
    numero_digitado = ""
    if numero in candidatos:
        registrar_voto(candidatos[numero])
        return "CAND" + numero          # "CAND1" ou "CAND2"
    return "INVALIDO"                   # vazio ou numero que nao existe: nao conta


def anular():
    """Registra voto nulo e limpa o numero digitado."""
    global numero_digitado
    numero_digitado = ""
    registrar_voto("Voto NULO")
    return "NULO"


def cancelar():
    """Apaga o numero digitado. Nao registra voto."""
    global numero_digitado
    numero_digitado = ""
    return "CANCELADO"


def executar(comando):
    """Executa CONFIRMAR, ANULAR ou CANCELAR (vindo da tela ou do Arduino).
    Retorna o codigo de resposta, ou None se nao foi executado."""
    global ultima_resposta
    if not aquisicao_ativa:
        ultima_resposta = "PARADA"
        return None

    if comando == "CONFIRMAR":
        resposta = confirmar()
    elif comando == "ANULAR":
        resposta = anular()
    elif comando == "CANCELAR":
        resposta = cancelar()
    else:
        return None                     # comando desconhecido: ignora, nao altera nada

    ultima_resposta = resposta
    enviar_ao_arduino(resposta)         # o Arduino mostra o resultado no LCD e nos LEDs
    return resposta


# ---------------------------------------------------------------
# COMUNICACAO SERIAL
# ---------------------------------------------------------------

def conectar(porta, velocidade=9600):
    """Abre a porta Serial. Retorna True se conectou."""
    global conexao, estado_comunicacao
    if serial is None:
        estado_comunicacao = "Falha: pyserial nao instalado"
        return False
    try:
        conexao = serial.Serial(porta, velocidade, timeout=0.1)
        estado_comunicacao = "Conectado"
        return True
    except (serial.SerialException, OSError):
        conexao = None
        estado_comunicacao = "Falha: porta indisponivel"
        return False


def desconectar():
    """Fecha a porta Serial, se estiver aberta."""
    global conexao, estado_comunicacao
    if conexao is not None:
        try:
            conexao.close()
        except (serial.SerialException, OSError):
            pass
    conexao = None
    estado_comunicacao = "Desconectado"


def enviar_ao_arduino(codigo):
    """Envia uma linha de texto ao Arduino (ex.: 'CAND1')."""
    global conexao, estado_comunicacao
    if conexao is None:
        return
    try:
        conexao.write((codigo + "\n").encode())
    except (serial.SerialException, OSError):
        conexao = None
        estado_comunicacao = "Falha: Arduino desconectado"


def processar_mensagem(mensagem):
    """Recebe uma linha bruta do Arduino, limpa e executa se for um comando conhecido."""
    texto = mensagem.strip()
    return executar(texto)              # texto desconhecido nao faz nada


def ler_arduino():
    """Le as linhas que chegaram do Arduino, sem esperar por novas. Chamada varias vezes por segundo."""
    global conexao, estado_comunicacao
    if conexao is None:
        return
    try:
        while conexao.in_waiting > 0:
            linha = conexao.readline().decode("utf-8", errors="ignore")
            processar_mensagem(linha)
    except (serial.SerialException, OSError):
        conexao = None
        estado_comunicacao = "Falha: Arduino desconectado"


# ---------------------------------------------------------------
# INICIAR / INTERROMPER A AQUISICAO
# ---------------------------------------------------------------

def iniciar_aquisicao(porta):
    """Comeca uma nova votacao: zera tudo e tenta conectar ao Arduino.
    Se nao conseguir conectar, a votacao abre mesmo assim (modo teste, so pela tela)."""
    global aquisicao_ativa, numero_digitado, ultima_resposta
    zerar_votos()
    numero_digitado = ""
    ultima_resposta = ""
    conectar(porta)
    aquisicao_ativa = True


def parar_aquisicao():
    """Interrompe a votacao e fecha a porta Serial. Os votos continuam na tela."""
    global aquisicao_ativa, numero_digitado
    desconectar()
    aquisicao_ativa = False
    numero_digitado = ""