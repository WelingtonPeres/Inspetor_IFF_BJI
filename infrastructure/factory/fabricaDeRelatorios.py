from typing import List, Dict, Any

from core.model.relatorio import Relatorio, FolhaDeGabarito
from core.model.anexo import Anexo, AnexoImagem, AnexoVideo

class FabricaDeRelatorios:
    """
    Pertence à camada de Infraestrutura. O seu único trabalho é traduzir dados externos em Entidades do Domínio.
    """

    @staticmethod
    def construir_pilha(dados_brutos: List[Dict]) -> List[Relatorio]:
        """
        Recebe uma lista inteira de cenários lidos do JSON e devolve uma pilha pronta de objetos Relatorio.
        
        Args:
            dados_brutos: Lista de dicionários extraídos dos arquivos JSON, cada um representando um cenário completo.
        """
        
        pilha_relatorios = []
        
        for dado in dados_brutos:
            
            relatorio_instanciado = FabricaDeRelatorios.__instanciar_relatorio_unico(dado)
            pilha_relatorios.append(relatorio_instanciado)
            
        return pilha_relatorios

    @staticmethod
    def __instanciar_relatorio_unico(dado_bruto: Dict) -> Relatorio:
        """
        Mapeia os campos do dicionário bruto para o construtor blindado do Relatorio.
        """
        
        try:
        
            info_relatorio = dado_bruto.get("relatorio", {})
            info_decisao = info_relatorio.get("decisao_administrativa", {})
            
            gabarito = FolhaDeGabarito(
                riscos=info_relatorio.get("riscos", []),
                fatores_inseguranca=info_relatorio.get("fatores_inseguranca", []),
                decisao_otima=info_decisao.get("acao_otima", "IGNORAR"),
                decisao_boa=info_decisao.get("acao_boa", "IGNORAR")
            )
            
            novo_relatorio = Relatorio(
                id_cenario=dado_bruto.get("id_cenario", 0), 
                titulo=dado_bruto.get("titulo", "Sem Título"),
                dificuldade=dado_bruto.get("dificuldade", 1),
                atividade=info_relatorio.get("atividade", "Não informada"),
                local=info_relatorio.get("local", "Não informado"),
                texto_descricao=info_relatorio.get("texto_descricao", ""),
                lista_envolvidos=info_relatorio.get("envolvidos", []), 
                cursos=info_relatorio.get("cursos", []),
                gabarito=gabarito # Passando o objeto!
            )
        
            # Instanciação dos Anexos
            dados_anexos = dado_bruto.get("anexos", [])
            lista_anexos_instanciados = FabricaDeRelatorios.__extrair_instanciar_anexos(dados_anexos)
            
            for anexo in lista_anexos_instanciados:
                novo_relatorio.adicionar_anexo(anexo)
                
        except Exception as e:
            print(f"[Erro] Falha ao instanciar relatório: {e}")
            # Em caso de erro, a fábrica opta por retornar None ao invés de lançar uma exceção, para evitar crashes no jogo.
            return None 
        
        return novo_relatorio

    @staticmethod
    def __extrair_instanciar_anexos(dados_anexos: List[Dict]) -> List[Anexo]:
        """
        Analisa a lista de anexos e aplica o Polimorfismo, decidindo se cria uma AnexoImagem ou AnexoVideo com base na chave 'tipo'.
        """
        anexos_construidos = []
        
        for dado_anexo in dados_anexos:
            
            tipo_midia = dado_anexo.get("tipo", "").upper()
            id_anexo = dado_anexo.get("id_anexo", 0)
            caminho = dado_anexo.get("caminho_arquivo", "")
            descricao = dado_anexo.get("descricao_acessibilidade", "")
            
            if tipo_midia == "IMAGEM":
                novo_anexo = AnexoImagem(id_anexo, caminho, descricao)
                anexos_construidos.append(novo_anexo)
                
            elif tipo_midia == "VIDEO":
                novo_anexo = AnexoVideo(id_anexo, caminho, descricao)
                anexos_construidos.append(novo_anexo)
                
            else:
                # Se o JSON vier com um erro de tipagem no anexo, 
                # a fábrica ignora-o para não causar um crash no jogo.
                print(f"[Aviso] Tipo de anexo desconhecido ignorado: {tipo_midia}")
                
        return anexos_construidos