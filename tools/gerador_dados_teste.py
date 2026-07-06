"""
Script para gerar arquivos JSON de teste para validação do RepositorioJSON.

Gera cenários válidos e inválidos para cobrir todos os casos de erro tratados
pela classe RepositorioJSON:
- Cenários válidos
- Arquivos com sintaxe JSON inválida
- Estrutura não é uma lista
- Lista vazia
- Cenários com chaves faltando
- Tipos de dados incorretos

Uso:
    python gerador_dados_teste.py --gerar     # Gera os arquivos de teste
    python gerador_dados_teste.py --limpar    # Remove os arquivos de teste
    python gerador_dados_teste.py --listar    # Lista os arquivos de teste
"""

import json
import random
import argparse
from pathlib import Path
from typing import Dict, List, Any


CURSOS_VALIDOS = [
    "DEFAULT",
    "T_QUIMICA",
    "T_INFORMATICA",
    "T_AGROPECUARIA",
    "T_ALIMENTOS",
    "T_MEIO_AMBIENTE",
    "T_ZOOTECNIA",
    "CT_ALIMENTOS",
    "E_COMPUTACAO",
]

DIFICULDADES = [1, 2, 3, 4, 5]
TIPOS_ANEXO = ["IMAGEM", "VIDEO", "AUDIO"]
RISCOS = ["FISICO", "QUIMICO", "BIOLOGICO", "ERGONOMICO", "ACIDENTE"]
FATORES_INSEGURANCA = ["ATO_INSEGURO", "CONDICAO_INSEGURA"]
DECISOES = ["ADVERTIR", "INTERDITAR", "IGNORAR"]
EXTENSOES_MIDIA = {
    "IMAGEM": ["jpg", "png", "gif"],
    "VIDEO": ["mp4", "avi", "mov"],
    "AUDIO": ["mp3", "wav", "ogg"]
}


def criar_cenario_valido(id_cenario: int) -> Dict[str, Any]:
    """Cria um cenário completamente válido de acordo com ESTRUTURA_JSON.md."""
    
    if random.choice([True, False]):
        cursos = [random.choice(CURSOS_VALIDOS)]
    else:
        cursos = random.sample(CURSOS_VALIDOS[1:], k=random.randint(1, 3))  # Exclui DEFAULT
    
    riscos = random.sample(RISCOS, k=random.randint(1, 3))
    
    fatores = random.sample(FATORES_INSEGURANCA, k=random.randint(1, 2))
    
    decisoes_diferentes = random.sample(DECISOES, k=2)
    
    anexos = []
    for i in range(random.randint(0, 3)):
        tipo_anexo = random.choice(TIPOS_ANEXO)
        extensao = random.choice(EXTENSOES_MIDIA[tipo_anexo])
        
        anexos.append({
            "id_anexo": 100 * id_cenario + i,  # ID inteiro único
            "tipo": tipo_anexo,
            "caminho_arquivo": f"midia/{tipo_anexo.lower()}/cenario_{id_cenario}_anexo_{i}.{extensao}"
        })
    
    return {
        "id_cenario": id_cenario, 
        "titulo": f"Inspeção: Cenário de Risco {id_cenario}",
        "dificuldade": random.choice(DIFICULDADES),  
        "relatorio": {
            "atividade": f"Atividade de manipulação de materiais {id_cenario}",
            "local": f"Setor {random.choice(['A', 'B', 'C', 'D', 'E'])}",
            "envolvidos": [f"Funcionário {i}" for i in range(1, random.randint(2, 4))],
            "texto_descricao": f"Descrição detalhada do cenário {id_cenario}. Observou-se situação potencial de risco durante inspeção de rotina.",
            "riscos": riscos,  
            "fatores_inseguranca": fatores,  
            "decisao_administrativa": {
                "decisao_otima": decisoes_diferentes[0],  # NUNCA igual à decisao_boa
                "decisao_boa": decisoes_diferentes[1]
            },
            "curso": cursos 
        },
        "anexos": anexos
    }


def arquivo_json_invalido() -> str:
    """Cria um arquivo JSON com sintaxe inválida."""
    return '{"chave": "valor",,, "outro": }'


def arquivo_nao_lista() -> str:
    """Cria um arquivo JSON que não é uma lista na raiz."""
    
    dados = {
        "id_cenario": "cenario_1",
        "titulo": "Cenário único"
    }
    return json.dumps(dados)


def arquivo_lista_vazia() -> str:
    """Cria um arquivo JSON com lista vazia."""
    return json.dumps([])


def arquivo_cenario_incompleto_raiz(id_cenario: int) -> str:
    """Cria um arquivo com cenários faltando chaves raiz."""
    cenario = criar_cenario_valido(id_cenario)
    
    chaves_raiz = ["id_cenario", "titulo", "dificuldade", "relatorio", "anexos"]
    chave_removida = random.choice(chaves_raiz)
    del cenario[chave_removida]
    
    return json.dumps([cenario])


def arquivo_relatorio_tipo_invalido(id_cenario: int) -> str:
    """Cria um arquivo com 'relatorio' não sendo um dicionário."""
    cenario = criar_cenario_valido(id_cenario)
    cenario["relatorio"] = "isto deve ser um dicionario"
    return json.dumps([cenario])


def arquivo_relatorio_chave_faltando(id_cenario: int) -> str:
    """Cria um arquivo com uma chave faltando no 'relatorio'."""
    
    cenario = criar_cenario_valido(id_cenario)
    chaves_relatorio = ["atividade", 
                        "local", 
                        "envolvidos", 
                        "texto_descricao", 
                        "riscos", 
                        "fatores_inseguranca", 
                        "decisao_administrativa", 
                        "curso"]
    
    
    chave_removida = random.choice(chaves_relatorio)
    
    del cenario["relatorio"][chave_removida]
    return json.dumps([cenario])


def arquivo_decisao_administrativa_invalida(id_cenario: int) -> str:
    """Cria um arquivo com 'decisao_administrativa' não sendo um dicionário."""
    cenario = criar_cenario_valido(id_cenario)
    cenario["relatorio"]["decisao_administrativa"] = ["lista", "em", "vez", "de", "dict"]
    return json.dumps([cenario])


def arquivo_decisao_chave_faltando(id_cenario: int) -> str:
    """Cria um arquivo com uma chave faltando em 'decisao_administrativa'."""
    cenario = criar_cenario_valido(id_cenario)
    if random.choice([True, False]):
        del cenario["relatorio"]["decisao_administrativa"]["decisao_otima"]
    else:
        del cenario["relatorio"]["decisao_administrativa"]["decisao_boa"]
    return json.dumps([cenario])


def arquivo_anexos_tipo_invalido(id_cenario: int) -> str:
    """Cria um arquivo com 'anexos' não sendo uma lista."""
    cenario = criar_cenario_valido(id_cenario)
    cenario["anexos"] = {"id": "anexo_invalido"}
    return json.dumps([cenario])


def arquivo_anexo_tipo_invalido(id_cenario: int) -> str:
    """Cria um arquivo com um anexo não sendo um dicionário (inválido)."""
    cenario = criar_cenario_valido(id_cenario)
    cenario["anexos"] = ["IMAGEM", "string em vez de dict"]
    return json.dumps([cenario])


def arquivo_anexo_chave_faltando(id_cenario: int) -> str:
    """Cria um arquivo com uma chave faltando em anexo."""
    cenario = criar_cenario_valido(id_cenario)
    
    anexo_valido = {
        "id_anexo": 1001,
        "tipo": "IMAGEM",
        "caminho_arquivo": "midia/imagem/anexo_teste.png"
    }
    
    cenario["anexos"] = [anexo_valido]
    
    chaves_anexo = ["id_anexo", "tipo", "caminho_arquivo"]
    chave_removida = random.choice(chaves_anexo)
    del cenario["anexos"][0][chave_removida]
    
    return json.dumps([cenario])


def arquivo_cenario_tipo_invalido() -> str:
    """Cria um arquivo com um item da lista que não é dicionário."""
    return json.dumps(["string em vez de dict", "outro string"])


def arquivo_multiplos_cenarios_validos(quantidade: int = 3) -> str:
    """Cria um arquivo com múltiplos cenários válidos."""
    cenarios = []
    
    # Garante uma distribuição de cursos
    cursos_lista = ["DEFAULT", "T_QUIMICA", "T_AGROPECUARIA", "T_ALIMENTOS", "T_MEIO_AMBIENTE"]
    
    for i in range(quantidade):
        cenario = criar_cenario_valido(i)
        # Força um curso específico para garantir diversidade
        cenario["relatorio"]["curso"] = [cursos_lista[i % len(cursos_lista)]]
        cenarios.append(cenario)
    
    return json.dumps(cenarios)


def arquivo_mixed_validos_invalidos() -> str:
    """Cria um arquivo com cenários válidos e inválidos misturados."""
    cenarios = []
    
    cenarios.append(criar_cenario_valido(0))
    
    cenario_invalido = criar_cenario_valido(1)
    del cenario_invalido["relatorio"]
    cenarios.append(cenario_invalido)
    
    cenarios.append(criar_cenario_valido(2))
    
    return json.dumps(cenarios)


def gerar_arquivos_teste(diretorio_saida: str = None):
    """
    Gera todos os arquivos JSON de teste com prefixo 'teste_'.
    Separa em duas pastas: test_valido/ e test_invalido/
    
    Args:
        diretorio_saida: Caminho do diretório raiz onde salvar os arquivos.
                        Padrão: resources/data
    """
    if diretorio_saida is None:
        diretorio_base = Path(__file__).parent.parent / "resources" / "data"
    else:
        diretorio_base = Path(diretorio_saida)
    
    diretorio_valido = diretorio_base / "test_valido"
    diretorio_invalido = diretorio_base / "test_invalido"
    
    diretorio_valido.mkdir(parents=True, exist_ok=True)
    diretorio_invalido.mkdir(parents=True, exist_ok=True)
    
    casos_validos = [
        ("teste_valido_simples.json", lambda: arquivo_multiplos_cenarios_validos(1)),
        ("teste_valido_multiplos.json", lambda: arquivo_multiplos_cenarios_validos(5)),
    ]
    
    casos_invalidos = [
        ("teste_invalido_sintaxe_json.json", lambda: arquivo_json_invalido()),
        ("teste_invalido_nao_lista.json", lambda: arquivo_nao_lista()),
        ("teste_invalido_lista_vazia.json", lambda: arquivo_lista_vazia()),
        ("teste_invalido_cenario_tipo_invalido.json", lambda: arquivo_cenario_tipo_invalido()),
        ("teste_invalido_chave_raiz_faltando_1.json", lambda: arquivo_cenario_incompleto_raiz(1)),
        ("teste_invalido_chave_raiz_faltando_2.json", lambda: arquivo_cenario_incompleto_raiz(2)),
        ("teste_invalido_relatorio_tipo_invalido.json", lambda: arquivo_relatorio_tipo_invalido(1)),
        ("teste_invalido_relatorio_chave_faltando_1.json", lambda: arquivo_relatorio_chave_faltando(1)),
        ("teste_invalido_relatorio_chave_faltando_2.json", lambda: arquivo_relatorio_chave_faltando(2)),
        ("teste_invalido_decisao_tipo_invalido.json", lambda: arquivo_decisao_administrativa_invalida(1)),
        ("teste_invalido_decisao_chave_faltando.json", lambda: arquivo_decisao_chave_faltando(1)),
        ("teste_invalido_anexos_tipo_invalido.json", lambda: arquivo_anexos_tipo_invalido(1)),
        ("teste_invalido_anexo_tipo_invalido.json", lambda: arquivo_anexo_tipo_invalido(1)),
        ("teste_invalido_anexo_chave_faltando.json", lambda: arquivo_anexo_chave_faltando(1)),
        ("teste_misto_validos_invalidos.json", lambda: arquivo_mixed_validos_invalidos()),
    ]
    
    print("=" * 60)
    print("Gerando arquivos VÁLIDOS...")
    print("=" * 60)
    for nome_arquivo, gerador_funcao in casos_validos:
        caminho_arquivo = diretorio_valido / nome_arquivo
        conteudo = gerador_funcao()
        
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)
        
        print(f"  ✓ {nome_arquivo}")
    
    print(f"\nTotal de {len(casos_validos)} arquivos VÁLIDOS em: {diretorio_valido}")
    
    print("\n" + "=" * 60)
    print("Gerando arquivos INVÁLIDOS...")
    print("=" * 60)
    for nome_arquivo, gerador_funcao in casos_invalidos:
        caminho_arquivo = diretorio_invalido / nome_arquivo
        conteudo = gerador_funcao()
        
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)
        
        print(f"  ✓ {nome_arquivo}")
    
    print(f"\nTotal de {len(casos_invalidos)} arquivos INVÁLIDOS em: {diretorio_invalido}")
    print("\n" + "=" * 60)
    print(f"✓ SUCESSO: {len(casos_validos) + len(casos_invalidos)} arquivos gerados!")
    print("=" * 60)


def limpar_arquivos_teste(diretorio_saida: str = None):
    """
    Remove todos os arquivos JSON de teste com prefixo 'teste_'.
    Limpa ambas as pastas: test_valido/ e test_invalido/
    
    Args:
        diretorio_saida: Caminho do diretório raiz onde estão os arquivos.
                        Padrão: resources/data
    """
    if diretorio_saida is None:
        diretorio_base = Path(__file__).parent.parent / "resources" / "data"
    else:
        diretorio_base = Path(diretorio_saida)
    
    diretorio_valido = diretorio_base / "test_valido"
    diretorio_invalido = diretorio_base / "test_invalido"
    
    arquivos_removidos = 0
    
    for diretorio in [diretorio_valido, diretorio_invalido]:
        if not diretorio.exists():
            continue
        
        for arquivo in diretorio.glob("teste_*.json"):
            arquivo.unlink()
            print(f"Arquivo removido: {arquivo}")
            arquivos_removidos += 1
    
    if arquivos_removidos == 0:
        print(f"Nenhum arquivo de teste encontrado")
    else:
        print(f"\n✓ Total de {arquivos_removidos} arquivos de teste removidos")


def listar_arquivos_teste(diretorio_saida: str = None):
    """
    Lista todos os arquivos JSON de teste com prefixo 'teste_'.
    Lista ambas as pastas: test_valido/ e test_invalido/
    
    Args:
        diretorio_saida: Caminho do diretório raiz onde estão os arquivos.
                        Padrão: resources/data
    """
    if diretorio_saida is None:
        diretorio_base = Path(__file__).parent.parent / "resources" / "data"
    else:
        diretorio_base = Path(diretorio_saida)
    
    diretorio_valido = diretorio_base / "test_valido"
    diretorio_invalido = diretorio_base / "test_invalido"
    
    print("\n" + "=" * 60)
    print("ARQUIVOS VÁLIDOS")
    print("=" * 60)
    
    arquivos_validos = list(diretorio_valido.glob("teste_*.json")) if diretorio_valido.exists() else []
    if not arquivos_validos:
        print("Nenhum arquivo válido encontrado")
    else:
        for i, arquivo in enumerate(sorted(arquivos_validos), 1):
            tamanho_kb = arquivo.stat().st_size / 1024
            print(f"  {i:2d}. {arquivo.name:<50} ({tamanho_kb:>7.2f} KB)")
    
    print("\n" + "=" * 60)
    print("ARQUIVOS INVÁLIDOS")
    print("=" * 60)
    
    arquivos_invalidos = list(diretorio_invalido.glob("teste_*.json")) if diretorio_invalido.exists() else []
    if not arquivos_invalidos:
        print("Nenhum arquivo inválido encontrado")
    else:
        for i, arquivo in enumerate(sorted(arquivos_invalidos), 1):
            tamanho_kb = arquivo.stat().st_size / 1024
            print(f"  {i:2d}. {arquivo.name:<50} ({tamanho_kb:>7.2f} KB)")
    
    total = len(arquivos_validos) + len(arquivos_invalidos)
    print("\n" + "=" * 60)
    print(f"Total de {len(arquivos_validos)} válidos + {len(arquivos_invalidos)} inválidos = {total} arquivos")
    print("=" * 60)


def main():
    """
    Interface de linha de comando para gerenciar arquivos de teste.
    """
    parser = argparse.ArgumentParser(
        description="Gerador de dados JSON para teste do RepositorioJSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python gerador_dados_teste.py --gerar      # Gera arquivos de teste
  python gerador_dados_teste.py --limpar     # Remove arquivos de teste
  python gerador_dados_teste.py --listar     # Lista arquivos de teste
  python gerador_dados_teste.py --dir ./data # Usa diretório customizado
        """
    )
    
    parser.add_argument(
        "--gerar",
        action="store_true",
        help="Gera os arquivos JSON de teste com prefixo 'teste_'"
    )
    
    parser.add_argument(
        "--limpar",
        action="store_true",
        help="Remove todos os arquivos JSON de teste"
    )
    
    parser.add_argument(
        "--listar",
        action="store_true",
        help="Lista todos os arquivos JSON de teste"
    )
    
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Diretório customizado para os arquivos (padrão: resources/data)"
    )
    
    args = parser.parse_args()
    
    if not (args.gerar or args.limpar or args.listar):
        args.gerar = True
    
    if args.gerar:
        print("Gerando arquivos de teste...\n")
        gerar_arquivos_teste(args.dir)
    
    if args.limpar:
        print("Limpando arquivos de teste...\n")
        limpar_arquivos_teste(args.dir)
    
    if args.listar:
        listar_arquivos_teste(args.dir)


if __name__ == "__main__":
    main()
