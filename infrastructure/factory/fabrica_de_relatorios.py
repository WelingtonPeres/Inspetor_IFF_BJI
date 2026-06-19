import logging
from typing import List, Dict, Any

from core.model.relatorio import Relatorio

logger = logging.getLogger(__name__)
from core.model.folha_de_gabarito import FolhaDeGabarito
from core.model.anexo import Anexo, AnexoImagem, AnexoVideo, AnexoAudio
from infrastructure.dtos.dados_cenario import DadosCenarioDTO, DadosAnexoDTO

class FabricaDeRelatorios:
    """
    O seu único trabalho é traduzir dados externos em Entidades do Domínio.
    """

    @staticmethod
    def construir_pilha(dados_brutos: List[DadosCenarioDTO]) -> List[Relatorio]:
        """
        Recebe uma lista inteira de cenários lidos do JSON e devolve uma pilha pronta de objetos Relatorio.
        
        Args:
            dados_brutos: Lista de objetos DadosCenarioDTO extraídos dos arquivos JSON, cada um representando um cenário completo.
        
        Returns:
            List[Relatorio]: Lista de objetos Relatorio instanciados com os dados dos cenários.
        """
        
        pilha_relatorios = []
        
        for dado in dados_brutos:
            
            relatorio_instanciado = FabricaDeRelatorios.__instanciar_relatorio_unico(dado)
            
            if relatorio_instanciado is not None:
                pilha_relatorios.append(relatorio_instanciado)
            
        return pilha_relatorios

    @staticmethod
    def __instanciar_relatorio_unico(dado_bruto: DadosCenarioDTO) -> Relatorio | None:
        """
        Mapeia os campos do objeto bruto para o construtor blindado do Relatorio.
        
        Args:
            dado_bruto: Objeto DadosCenarioDTO representando um cenário completo, incluindo gabarito e anexos.
            
        Return: 
            Relatorio: instanciado com os dados do cenário, ou None em caso de falha na construção.
        """
        try:
            
            folha_gabarito = FolhaDeGabarito(
                riscos=dado_bruto.riscos,
                fatores_inseguranca=dado_bruto.fatores_inseguranca,
                decisao_otima=dado_bruto.decisao_otima,
                decisao_boa=dado_bruto.decisao_boa
            )
            
            relatorio = Relatorio(
                id_cenario=dado_bruto.id_cenario,
                titulo=dado_bruto.titulo,
                atividade=dado_bruto.atividade,
                local=dado_bruto.local,
                texto_descricao=dado_bruto.texto_descricao,
                envolvidos=dado_bruto.envolvidos,
                cursos=dado_bruto.cursos,
                dificuldade=dado_bruto.dificuldade,
                gabarito=folha_gabarito
            )
            
        except ValueError as e:
            logger.error("Falha ao construir relatório para o cenário '%s': %s", dado_bruto.titulo, e)
            return None
            
        except Exception as e:
            logger.error("Erro inesperado ao construir relatório para o cenário '%s': %s", dado_bruto.titulo, e)
            return None
        
        try:
            if dado_bruto.anexos is not None:
                
                anexos_construidos = FabricaDeRelatorios.__extrair_instanciar_anexos(dado_bruto.anexos)
                
                if anexos_construidos is not None:
                    for anexo in anexos_construidos:
                        relatorio.adicionar_anexo(anexo)

        except Exception as e:
            logger.error("Erro inesperado ao construir anexos para o cenário '%s': %s", dado_bruto.titulo, e)
        
        return relatorio 

    @staticmethod
    def __extrair_instanciar_anexos(dados_anexos: List[DadosAnexoDTO]) -> List[Anexo] | None:
        """
        Analisa a lista de anexos e aplica o Polimorfismo, decidindo se cria uma AnexoImagem ou AnexoVideo com base na chave 'tipo'.
        
        Args:
            dados_anexos: Lista de objetos DadosAnexoDTO, cada um contendo as informações
                necessárias para construir um anexo específico (imagem, vídeo ou áudio).
            
        Returns:
            List[Anexo]: Lista de objetos Anexo construídos a partir dos dados fornecidos. 
            None: Pode ser vazia se ocorrerem erros.
        """
        anexos_construidos = []
        
        try: 
            for dado_anexo in dados_anexos:
                tipo = dado_anexo.tipo.upper()
                
                if tipo == "IMAGEM":
                    anexo = AnexoImagem(
                        id_anexo=dado_anexo.id_anexo,
                        caminho_arquivo=dado_anexo.caminho_arquivo
                    )
                    anexos_construidos.append(anexo)
                    
                elif tipo == "VIDEO":
                    anexo = AnexoVideo(
                        id_anexo=dado_anexo.id_anexo,
                        caminho_arquivo=dado_anexo.caminho_arquivo
                    )
                    anexos_construidos.append(anexo)
                    
                elif tipo == "AUDIO":
                    anexo = AnexoAudio(
                        id_anexo=dado_anexo.id_anexo,
                        caminho_arquivo=dado_anexo.caminho_arquivo
                    )
                    anexos_construidos.append(anexo)
                else:
                    logger.warning("Tipo de anexo desconhecido '%s' para o arquivo '%s'. Anexo ignorado.", dado_anexo.tipo, dado_anexo.caminho_arquivo)
        
        except ValueError as e:
            logger.error("Falha ao construir anexo: %s", e)
            return anexos_construidos

        return anexos_construidos