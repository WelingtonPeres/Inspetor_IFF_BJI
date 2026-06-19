import pytest
from dataclasses import replace
from unittest.mock import patch

from infrastructure.dtos.dados_cenario import DadosCenarioDTO, DadosAnexoDTO
from infrastructure.factory.fabrica_de_relatorios import FabricaDeRelatorios
from core.model.anexo import AnexoImagem, AnexoVideo, AnexoAudio

@pytest.fixture
def dto_cenario_perfeito() -> DadosCenarioDTO:
    """Cria um DTO impecável, simulando um JSON perfeito."""
    return DadosCenarioDTO(
        id_cenario=1,
        titulo="Laboratório de Química",
        dificuldade=3,
        atividade="Manuseio de Ácidos",
        local="Bloco C",
        texto_descricao="Alunos sem EPI.",
        envolvidos=["Alunos"],
        cursos=["Química"],
        riscos=["QUIMICO", "ACIDENTE"],
        fatores_inseguranca=["ATO_INSEGURO"],
        decisao_otima="INTERDITAR",
        decisao_boa="ADVERTIR",
        anexos=[
            DadosAnexoDTO(id_anexo=101, tipo="IMAGEM", caminho_arquivo="foto.png")
        ]
    )
    
def test_fabrica_deve_construir_relatorio_com_sucesso(dto_cenario_perfeito):

    lista_bruta = [dto_cenario_perfeito]
    
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    assert len(pilha_resultado) == 1
    relatorio = pilha_resultado[0]
    
    assert relatorio.id_cenario == 1
    assert relatorio.titulo == "Laboratório de Química"
    assert relatorio.folha_gabarito.decisao_otima == "INTERDITAR"
    
    anexos = relatorio.obter_anexos()
    assert len(anexos) == 1
    assert anexos[0].get_tipo_midia() == "IMAGEM"
    
def test_fabrica_deve_contruir_mais_de_um_relatorio(dto_cenario_perfeito):

    lista_bruta = [dto_cenario_perfeito, dto_cenario_perfeito]
    
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    assert len(pilha_resultado) == 2
    
def test_fabrica_deve_construir_relatorio_sem_anexos(dto_cenario_perfeito):
    
    dto_sem_anexos = DadosCenarioDTO(
        id_cenario=1,
        titulo="Laboratório de Química",
        dificuldade=3,
        atividade="Manuseio de Ácidos",
        local="Bloco C",
        texto_descricao="Alunos sem EPI.",
        envolvidos=["Alunos"],
        cursos=["Química"],
        riscos=["QUIMICO", "ACIDENTE"],
        fatores_inseguranca=["ATO_INSEGURO"],
        decisao_otima="INTERDITAR",
        decisao_boa="ADVERTIR",
        anexos=[
            # Lista vazia de anexos
        ]
    )
    
    lista_bruta = [dto_sem_anexos]
    
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    assert len(pilha_resultado) == 1
    relatorio = pilha_resultado[0]
    assert relatorio.possui_anexos() is False

def test_fabrica_deve_ignorar_cenario_com_regras_invalidas():

    dto_invalido = DadosCenarioDTO(
        id_cenario=2, 
        titulo="Erro Intencional", 
        dificuldade=99, # Dificuldade fora do 1-5
        atividade="Teste", 
        local="Teste", 
        texto_descricao="",
        envolvidos=["Teste"], 
        cursos=["Teste"], 
        riscos=["QUIMICO"], 
        fatores_inseguranca=[],
        decisao_otima="IGNORAR", 
        decisao_boa="IGNORAR", 
        anexos=[]
    )
    
    lista_bruta = [dto_invalido]
    
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    assert len(pilha_resultado) == 0


def test_fabrica_deve_processar_lote_misto_ignorando_invalidos(dto_cenario_perfeito):
    """
    Teste de Resiliência em Lote: Valida que um cenário inválido no meio de uma lista não interrompe o processamento.
    """
    # Cria o cenário inválido mantendo todos os outros campos do DTO perfeito
    dto_invalido = replace(dto_cenario_perfeito, id_cenario=2, titulo="Cenário Inválido", dificuldade=99)
    
    lista_bruta = [dto_cenario_perfeito, dto_invalido, dto_cenario_perfeito]
    
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    assert len(pilha_resultado) == 2
    assert pilha_resultado[0].id_cenario == 1
    assert pilha_resultado[1].id_cenario == 1
    
    
def test_fabrica_deve_instanciar_diferentes_tipos_de_midia(dto_cenario_perfeito):
    """
    Teste de Polimorfismo: Valida que a fábrica instancia corretamente cada tipo de anexo.
    Princípio: O padrão Factory deve criar as classes concretas corretas com base no tipo.
    """
    dto_polimórfico = replace(
        dto_cenario_perfeito,
        id_cenario=3,
        titulo="Cenário Polimórfico",
        anexos=[
            DadosAnexoDTO(id_anexo=101, tipo="IMAGEM", caminho_arquivo="foto.png"),
            DadosAnexoDTO(id_anexo=102, tipo="VIDEO", caminho_arquivo="video.mp4"),
            DadosAnexoDTO(id_anexo=103, tipo="AUDIO", caminho_arquivo="audio.mp3")
        ]
    )
    
    lista_bruta = [dto_polimórfico]
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    assert len(pilha_resultado) == 1
    relatorio = pilha_resultado[0]
    anexos = relatorio.obter_anexos()
    
    assert len(anexos) == 3
    
    # Valida que cada um é uma instância da classe correta 
    assert isinstance(anexos[0], AnexoImagem), "Primeiro anexo deve ser AnexoImagem"
    assert isinstance(anexos[1], AnexoVideo), "Segundo anexo deve ser AnexoVideo"
    assert isinstance(anexos[2], AnexoAudio), "Terceiro anexo deve ser AnexoAudio"
    
    assert anexos[0].get_tipo_midia() == "IMAGEM"
    assert anexos[1].get_tipo_midia() == "VIDEO"
    assert anexos[2].get_tipo_midia() == "AUDIO"
    

def test_fabrica_deve_ignorar_anexos_com_tipos_desconhecidos(dto_cenario_perfeito):
    """
    Valida que tipos de anexo desconhecidos são ignorados, mas o cenário continua sendo construído com sucesso (graceful degradation).
    Princípio: O sistema não deve falhar por causa de dados malformados externamente.
    """
    dto_tipos_desconhecidos = replace(
        dto_cenario_perfeito,
        id_cenario=4,
        titulo="Cenário com Tipos Desconhecidos",
        anexos=[
            DadosAnexoDTO(id_anexo=201, tipo="PDF", caminho_arquivo="documento.pdf"),
            DadosAnexoDTO(id_anexo=202, tipo="HOLOGRAMA", caminho_arquivo="holo.hol")
        ]
    )
    
    lista_bruta = [dto_tipos_desconhecidos]
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    assert len(pilha_resultado) == 1
    relatorio = pilha_resultado[0]
    
    anexos = relatorio.obter_anexos()
    assert len(anexos) == 0
    assert relatorio.possui_anexos() is False
    
    # O relatório continua íntegro com seus dados de negócio
    assert relatorio.id_cenario == 4
    assert relatorio.titulo == "Cenário com Tipos Desconhecidos"
    

def test_fabrica_deve_rejeitar_cenario_com_riscos_invalidos_no_gabarito(dto_cenario_perfeito):
    """
    Valida que quando a FolhaDeGabarito rejeita dados inválidos, a fábrica captura a exceção e retorna None, resultando em um cenário não-construído.
    Princípio: A validação de negócio é delegada para as Entidades. A fábrica apenas traduz e trata falhas.
    """
    dto_riscos_invalidos = replace(
        dto_cenario_perfeito,
        id_cenario=5,
        titulo="Cenário com Riscos Inválidos",
        riscos=["FANTASMA", "MAGIA"]  # Riscos que não existem na LISTA_RISCOS_VALIDOS
    )
    
    lista_bruta = [dto_riscos_invalidos]
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    # Valida que o cenário foi rejeitado e a pilha está vazia
    assert len(pilha_resultado) == 0
    

def test_fabrica_deve_rejeitar_cenario_com_fatores_invalidos_no_gabarito(dto_cenario_perfeito):
    """
    Valida que fatores de insegurança inválidos também causam rejeição do cenário pela FolhaDeGabarito.
    Princípio: A validação de negócio é integral, qualquer campo inválido deve ser rejeitado.
    """
    dto_fatores_invalidos = replace(
        dto_cenario_perfeito,
        id_cenario=6,
        titulo="Cenário com Fatores Inválidos",
        fatores_inseguranca=["MALDIÇÃO", "NEUTRO"]  # Fatores que não existem na LISTA_FATORES_VALIDOS
    )
    
    lista_bruta = [dto_fatores_invalidos]
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    assert len(pilha_resultado) == 0
    

def test_fabrica_deve_rejeitar_cenario_com_decisoes_invalidas_no_gabarito(dto_cenario_perfeito):
    """
    Valida que decisões administrativas inválidas
    também causam rejeição do cenário pela FolhaDeGabarito.
    Princípio: Toda validação de domínio é delegada para as Entidades, nunca na Fábrica.
    """
    dto_decisao_otima_invalida = replace(
        dto_cenario_perfeito,
        id_cenario=7,
        titulo="Cenário com Decisão Ótima Inválida",
        decisao_otima="EXPLODIR"  # Decisão que não existe na LISTA_DECISOES_VALIDAS
    )
    
    lista_bruta = [dto_decisao_otima_invalida]
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    assert len(pilha_resultado) == 0


def test_fabrica_deve_rejeitar_cenario_com_decisoes_iguais(dto_cenario_perfeito):
    """
    Valida que decisão ótima e decisão boa iguais são rejeitadas,
    conforme a Restrição Crítica documentada na ESTRUTURA_JSON.md §5.4.
    """
    dto_decisoes_iguais = replace(
        dto_cenario_perfeito,
        id_cenario=8,
        titulo="Cenário com Decisões Iguais",
        decisao_otima="INTERDITAR",
        decisao_boa="INTERDITAR"
    )

    lista_bruta = [dto_decisoes_iguais]
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)

    assert len(pilha_resultado) == 0


def test_fabrica_deve_capturar_erro_inesperado_na_construcao_de_relatorio(dto_cenario_perfeito):
    """
    Valida que exceções inesperadas durante a construção do Relatório
    são capturadas gracefully e o cenário é rejeitado (retorna None).
    Princípio: O sistema deve ser resiliente a erros inesperados e não quebrar a execução.
    """
    lista_bruta = [dto_cenario_perfeito]
    
    # Mock a FolhaDeGabarito para lançar uma exceção inesperada
    with patch('infrastructure.factory.fabrica_de_relatorios.FolhaDeGabarito') as mock_gabarito:
        mock_gabarito.side_effect = RuntimeError("Erro inesperado na fábrica de gabarito")
        
        pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
        assert len(pilha_resultado) == 0
        

def test_fabrica_deve_capturar_erro_inesperado_na_construcao_de_anexos(dto_cenario_perfeito):
    """
    Valida que exceções inesperadas durante a construção de anexos
    são capturadas gracefully. O relatório continua construído, mas sem anexos.
    Princípio: Falhas em anexos não devem impedir a construção do cenário principal.
    """
    lista_bruta = [dto_cenario_perfeito]
    
    with patch.object(FabricaDeRelatorios, '_FabricaDeRelatorios__extrair_instanciar_anexos') as mock_anexos:
        mock_anexos.side_effect = RuntimeError("Erro inesperado ao processar anexos")
        
        pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
        
        assert len(pilha_resultado) == 1
        relatorio = pilha_resultado[0]
        assert relatorio.id_cenario == 1
        
        assert relatorio.possui_anexos() is False


def test_fabrica_deve_processar_lote_completo_mesmo_com_erro_valor(dto_cenario_perfeito):
    """
    Valida que cenários com ValueError no meio do lote
    não interrompem o processamento dos restantes.
    Princípio: Erros de validação de domínio devem ser tolerados em lotes.
    """
    dto_valido_1 = dto_cenario_perfeito
    dto_com_erro = replace(
        dto_cenario_perfeito, 
        id_cenario=8, 
        titulo="Com erro", 
        dificuldade=99
    )
    dto_valido_2 = replace(
        dto_cenario_perfeito,
        id_cenario=9,
        titulo="Segundo válido"
    )
    
    lista_bruta = [dto_valido_1, dto_com_erro, dto_valido_2]
    pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
    
    # Deve retornar apenas os 2 válidos
    assert len(pilha_resultado) == 2
    assert pilha_resultado[0].id_cenario == 1
    assert pilha_resultado[1].id_cenario == 9


def test_fabrica_deve_capturar_valor_error_durante_construcao_de_anexos(dto_cenario_perfeito):
    """
    Valida que ValueError
    durante a construção de anexos é capturado e os anexos parcialmente construídos são retornados.
    Princípio: Graceful degradation, retornar o máximo possível mesmo com falhas parciais.
    """
    lista_bruta = [dto_cenario_perfeito]
    
    # Mock AnexoImagem para lançar ValueError na segunda chamada
    with patch('infrastructure.factory.fabrica_de_relatorios.AnexoImagem') as mock_imagem:
        mock_imagem.side_effect = ValueError("Erro ao validar anexo de imagem")
        
        pilha_resultado = FabricaDeRelatorios.construir_pilha(lista_bruta)
        
        # O relatório deve ser construído
        assert len(pilha_resultado) == 1
        relatorio = pilha_resultado[0]
        
        # Mas como o AnexoImagem falhou, os anexos não foram adicionados
        assert relatorio.possui_anexos() is False


def test_fabrica_lista_vazia():
    """
    T9: Lista vazia de DTOs deve retornar pilha vazia (garantia contra regressão).
    """
    assert FabricaDeRelatorios.construir_pilha([]) == []
