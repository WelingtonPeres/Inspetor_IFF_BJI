# Guia de Instalação: Inspetor IFF-BJI

Este guia é para quem nunca mexeu com programação. Se você já tem Python e Git instalados e sabe o que é um terminal, pode pular direto para a [Instalação Rápida do README](../README.md#3-instalação-rápida).

Por padrão, o jogo roda em **Windows**, **Linux** e **macOS**. Toda a instalação leva em torno de 10 a 20 minutos, dependendo da velocidade da sua internet.

## 1. O que você vai instalar

O jogo é feito em **Python**, uma linguagem de programação. Para rodá-lo, o seu computador precisa de três coisas:

| Programa | O que faz |
|---|---|
| **Python 3.11 ou superior** | É a "linguagem" que o jogo usa para funcionar. |
| **Git** | É a ferramenta que baixa o código do jogo da internet. |
| **PySide6** | É a biblioteca que desenha a janela do jogo. Instalada junto com o restante, no passo 6. |

Não se preocupe se esses nomes soam estranhos. Você só precisa instalá-los uma vez.

## 2. Instalando o Python

### Windows

1. Acesse [python.org/downloads](https://www.python.org/downloads/) e clique no botão grande amarelo **"Download Python 3.X.X"**.
2. Execute o ficheiro baixado. Na primeira tela do instalador, marque a caixinha **"Add Python to PATH"** no canto inferior. Sem isso, o Windows não vai encontrar o Python depois.
3. Clique em **Install Now** e aguarde.
4. Para confirmar que deu certo, abra o **PowerShell** (aperte a tecla Windows, digite `powershell` e aperte Enter) e digite:
   ```powershell
   python --version
   ```
   A resposta deve ser algo como `Python 3.11.9` ou superior.

### Linux

A maioria das distribuições Linux já vem com Python instalado. Para confirmar, abra o terminal e digite:

```bash
python3 --version
```

Se a versão for 3.11 ou superior, pode pular para a seção 3. Se for mais antiga, instale pelo gerenciador de pacotes da sua distribuição. No Ubuntu ou Debian, por exemplo:

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### macOS

1. Acesse [python.org/downloads](https://www.python.org/downloads/) e baixe o instalador do **Python 3.11 ou superior**.
2. Execute o ficheiro `.pkg` baixado e siga as instruções.
3. Para confirmar, abra o **Terminal** (aplicativo que já vem instalado no macOS) e digite:
   ```bash
   python3 --version
   ```

## 3. Instalando o Git

### Windows

Baixe o instalador em [git-scm.com/download/win](https://git-scm.com/download/win) e siga as opções padrão. Quando o instalador perguntar sobre o "editor padrão", pode deixar em "Use Vim" se não souber o que escolher.

### Linux

```bash
sudo apt install git
```

No Fedora ou Red Hat:

```bash
sudo dnf install git
```

### macOS

O macOS mais recente já traz o Git pré-instalado. Para confirmar, abra o Terminal e digite:

```bash
git --version
```

Se não estiver instalado, o sistema vai pedir para instalar as **Command Line Tools**. Aceite e aguarde.

## 4. Abrindo o terminal certo

Você vai usar bastante o terminal nas próximas etapas. Ele é uma janela onde você digita comandos em texto, em vez de clicar com o mouse.

- **Windows:** aperte a tecla Windows, digite `powershell` e aperte Enter.
- **macOS:** abra o **Terminal** pelo Launchpad (busque por "Terminal").
- **Linux:** procure por "Terminal" no menu de aplicações, ou use o atalho `Ctrl + Alt + T`.

Quando o terminal abrir, você verá uma linha como `C:\Users\SeuNome>` no Windows, ou `seunome@computador:~$` no Linux e macOS. É aí que você digita os comandos a seguir.

## 5. Baixando o jogo

No terminal, escolha uma pasta para guardar o jogo (por exemplo, `Documentos`) e execute:

**Windows (PowerShell):**
```powershell
cd $HOME\Documents
git clone https://github.com/WelingtonPeres/Inspetor_IFF_BJI.git
```

**Linux e macOS:**
```bash
cd ~/Documents
git clone https://github.com/WelingtonPeres/Inspetor_IFF_BJI.git
```

Vai aparecer uma pasta chamada `Inspetor_IFF_BJI` com todos os ficheiros do jogo. Para confirmar, entre nela:

```bash
cd Inspetor_IFF_BJI
```

## 6. Criando o ambiente virtual

Um **ambiente virtual** é uma pasta isolada onde o Python guarda as bibliotecas que o jogo precisa, sem misturar com o resto do sistema. Isso evita conflitos quando você tiver outros projetos em Python.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux e macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Se funcionou, o começo da linha do terminal vai ganhar um `(venv)`, mostrando que o ambiente está ativo. Sempre que for rodar o jogo, lembre-se de ativar o ambiente antes.

> Dica: o PowerShell do Windows às vezes bloqueia scripts por padrão. Se aparecer um erro vermelho mencionando "execution of scripts is disabled", execute este comando uma única vez e tente de novo:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

## 7. Instalando as dependências

Com o `(venv)` ativo, ainda dentro da pasta do jogo, execute:

```bash
pip install -r requirements.txt
```

Esse comando lê o ficheiro `requirements.txt` e instala o PySide6, o jsonschema, o unidecode e o pytest. A primeira instalação pode demorar alguns minutos. Quando terminar sem erros, está pronto.

## 8. Rodando o jogo

No mesmo terminal, com o ambiente virtual ativo, execute:

```bash
python main.py
```

A janela do jogo deve abrir em alguns segundos. Na primeira execução, escolha um perfil e um curso para começar a campanha.

## 9. Atualizando o jogo para uma nova versão

Quando sair uma versão nova com correções ou cenários adicionais, entre na pasta do jogo e puxe as alterações:

```bash
git pull
pip install -r requirements.txt
```

Se aparecer algum erro depois de atualizar, apague o ambiente virtual e recrie:

**Windows:**
```powershell
deactivate
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux e macOS:**
```bash
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 10. Desinstalando

Para remover o jogo do seu computador, basta apagar a pasta `Inspetor_IFF_BJI` (e, se quiser, desinstalar o Python e o Git pelos métodos do seu sistema operacional).

## Problemas comuns

**"python não é reconhecido como um comando"** (Windows)
O Python não foi adicionado ao PATH. Reinstale o Python marcando a caixinha "Add Python to PATH" na primeira tela do instalador.

**"No module named PySide6"**
O ambiente virtual não está ativo, ou o `pip install` não foi executado. Confirme que o `(venv)` aparece no começo da linha do terminal e rode o `pip install -r requirements.txt` novamente.

**A janela abre e fecha imediatamente**
Abra o terminal e rode `python main.py` a partir dele. Quando o jogo fecha por erro, o terminal mostra a mensagem em vermelho. Copie e pesquise no Google, ou abra uma issue no repositório do projeto com o texto completo.

**"fatal: destination path already exists"**
Já existe uma pasta `Inspetor_IFF_BJI` no local. Apague a pasta ou escolha outro diretório.

**"Permission denied" ao ativar o venv no Linux/macOS**
Use `source venv/bin/activate` em vez de tentar executar o ficheiro diretamente.
