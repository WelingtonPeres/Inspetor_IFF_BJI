import pytest

from core.model.relatorio import Relatorio
from core.model.folha_de_gabarito import FolhaDeGabarito
from core.model.folha_de_resposta import FolhaDeResposta
from core.model.anexo import AnexoImagem, AnexoVideo, AnexoAudio

@pytest.fixture
def gabarito_simples():
    """Fixture: Fornece um gabarito válido exigido pelo construtor do Relatório."""
    return FolhaDeGabarito(
        riscos=["FISICO"], 
        fatores_inseguranca=["CONDICAO_INSEGURA"], 
        decisao_otima="INTERDITAR", 
        decisao_boa="ADVERTIR"
    )

@pytest.fixture
def respostas_simples():
    """Fixture: Fornece uma resposta válida para testes de integração."""
    return FolhaDeResposta(
        riscos=["FISICO"], 
        fatores_inseguranca=["CONDICAO_INSEGURA"],
        decisao_tomada="INTERDITAR",
        tempo_gasto_segundos=120
    )

@pytest.fixture
def anexo_img():
    """Fixture: Fornece uma instância pronta de AnexoImagem."""
    return AnexoImagem(id_anexo=101, caminho_arquivo="/assets/foto_fio_desencapado.png")

@pytest.fixture
def anexo_vid():
    """Fixture: Fornece uma instância pronta de AnexoVideo."""
    return AnexoVideo(id_anexo=102, caminho_arquivo="/assets/video_maquina.mp4")

@pytest.fixture
def anexo_audio():
    """Fixture: Fornece uma instância pronta de AnexoAudio."""
    return AnexoAudio(id_anexo=103, caminho_arquivo="/assets/audio_depoimento.wav")

# Testes de Unidade para a Entidade Relatório com foco em Instanciação, Validação de Atributos e Polimorfismo dos Anexos

def test_instanciar_relatorio_caminho_feliz(gabarito_simples):
    """Garante que um Relatório válido é criado e os atributos são atribuídos corretamente."""
    
    relatorio = Relatorio(
        id_cenario=1,
        titulo="Laboratório de Química",
        atividade="Aula Prática",
        local="Bloco B",
        texto_descricao="Teste de criação",
        envolvidos=["Professor"],
        cursos=["Engenharia"],
        dificuldade=3,
        gabarito=gabarito_simples
    )
    
    # Asserts de estado inicial
    assert relatorio.id_cenario == 1
    assert relatorio.dificuldade == 3
    assert relatorio.possui_anexos() is False
    assert relatorio.folha_gabarito is gabarito_simples # Verifica se é a exata mesma instância na memória
    

def test_relatorio_bloqueia_dificuldade_abaixo_do_minimo(gabarito_simples):
    """Dificuldade 0 não pode existir."""
    
    with pytest.raises(ValueError, match="A dificuldade deve ser um inteiro entre 1 e 5"):
        
        Relatorio(
            id_cenario=1, 
            titulo="Teste", 
            atividade="Teste", 
            local="Teste", 
            texto_descricao="Teste", 
            envolvidos=["Teste"], 
            cursos=["Teste"], 
            dificuldade=0,
            gabarito=gabarito_simples
        )

def test_relatorio_bloqueia_dificuldade_acima_do_maximo(gabarito_simples):
    """Análise de Valor Limite: Dificuldade 6 não pode existir."""
    with pytest.raises(ValueError, match="A dificuldade deve ser um inteiro entre 1 e 5"):
        
        Relatorio(
            id_cenario=1, 
            titulo="Teste", 
            atividade="Teste", 
            local="Teste", 
            texto_descricao="Teste", 
            envolvidos=["Teste"], 
            cursos=["Teste"], 
            dificuldade=6,
            gabarito=gabarito_simples
        )
        
def test_relatorio_bloqueia_riscos_invalidos():
    """Gabarito com riscos inválidos deve ser rejeitado."""
    with pytest.raises(ValueError):
        
        FolhaDeGabarito(
            riscos=["RISCO_DESCONOCIDO"],
            fatores_inseguranca=["CONDICAO_INSEGURA"],
            decisao_otima="INTERDITAR",
            decisao_boa="ADVERTIR"
        )
        
def test_relatorio_corrige_riscos_mal_formados():
    """Garante que o sistema sanitiza letras minúsculas e remove acentos."""
    
    gabarito = FolhaDeGabarito(
        riscos=["FíSICO", "químico"], # Enviando dados sujos
        fatores_inseguranca=["CONDICAO_INSEGURA"],
        decisao_otima="INTERDITAR",
        decisao_boa="ADVERTIR"
    )
    
    assert gabarito.riscos == ["FISICO", "QUIMICO"]

# Testes de Unidade para a Entidade Anexo e sua integração com o Relatório

def test_anexo_audio_get_tipo_midia(anexo_audio):
    """
    T4: Garante que AnexoAudio retorna o tipo de mídia AUDIO.
    """
    assert anexo_audio.get_tipo_midia() == "AUDIO"


def test_folha_de_gabarito_rejeita_decisoes_iguais():
    """
    T5: Valida que decisão ótima e decisão boa iguais são rejeitadas.
    Restrição Crítica documentada na ESTRUTURA_JSON.md §5.4.
    """
    with pytest.raises(ValueError, match="não podem ser iguais"):
        FolhaDeGabarito(
            riscos=["FISICO"],
            fatores_inseguranca=["CONDICAO_INSEGURA"],
            decisao_otima="INTERDITAR",
            decisao_boa="INTERDITAR"
        )


def test_folha_inspecao_listas_vazias():
    """
    T6: FolhaDeInspecao deve aceitar listas vazias de riscos e fatores.
    """
    gabarito = FolhaDeGabarito(
        riscos=[],
        fatores_inseguranca=[],
        decisao_otima="IGNORAR",
        decisao_boa="ADVERTIR"
    )
    assert gabarito.riscos == []
    assert gabarito.fatores_inseguranca == []
    assert gabarito.contar_riscos() == 0
    assert gabarito.contar_fatores() == 0


def test_anexos_revelam_tipo_de_midia_correto(anexo_img, anexo_vid):
    """Garante que as subclasses respondem corretamente ao polimorfismo."""
    
    assert anexo_img.get_tipo_midia() == "IMAGEM"
    assert anexo_vid.get_tipo_midia() == "VIDEO"
    assert anexo_img.id_anexo == 101

def test_relatorio_extrai_dto_com_anexos_corretamente(gabarito_simples, anexo_img, anexo_vid):
    """
    Testa se a extração para a UI converte as instâncias em dicionários sem quebrar o código.
    """

    relatorio = Relatorio(
        id_cenario=5, 
        titulo="Cenário UI", 
        atividade="...", 
        local="...", 
        texto_descricao="...", 
        envolvidos=["Aluno"], 
        cursos=["Teste"], 
        dificuldade=2, 
        gabarito=gabarito_simples
    )
    
    relatorio.adicionar_anexo(anexo_img)
    relatorio.adicionar_anexo(anexo_vid)
    
    assert relatorio.possui_anexos() is True

    dados_ui = relatorio.extrair_apresentacao_relatorio()

    # Verifica se os atributos normais vieram
    assert dados_ui["titulo"] == "Cenário UI"
    
    # Verifica a conversão dos anexos
    lista_anexos = dados_ui["anexos"]
    assert len(lista_anexos) == 2
    
    assert lista_anexos[0]["tipo_midia"] == "IMAGEM"
    assert lista_anexos[0]["caminho_arquivo"] == "/assets/foto_fio_desencapado.png"
    
    assert lista_anexos[1]["tipo_midia"] == "VIDEO"
    
# Teste de Intregração de Relatório com Folhas de Gabarito e Resposta

def test_relatorio_contem_folha_gabarito(gabarito_simples):
    """Garante que o Relatório armazena e expõe a Folha de Gabarito corretamente."""
    
    relatorio = Relatorio(
        id_cenario=10, 
        titulo="Cenário Gabarito", 
        atividade="...", 
        local="...", 
        texto_descricao="...", 
        envolvidos=["Aluno"], 
        cursos=["Teste"], 
        dificuldade=2, 
        gabarito=gabarito_simples
    )
    
    folha_resposta = FolhaDeResposta(
        riscos=["FISICO"],
        fatores_inseguranca=["CONDICAO_INSEGURA"],
        decisao_tomada="INTERDITAR",
        tempo_gasto_segundos=150
    )
    
    assert relatorio.folha_gabarito is gabarito_simples
    
    # Anexa a resposta do jogador e verifica se é armazenada corretamente
    relatorio.anexar_resposta_jogador(folha_resposta)
    assert relatorio.folha_resposta_jogador is folha_resposta
    
    # Verifica se os dados da resposta do jogador estão corretos
    assert relatorio.folha_resposta_jogador.riscos == ["FISICO"]
    assert relatorio.folha_resposta_jogador.fatores_inseguranca == ["CONDICAO_INSEGURA"]
    assert relatorio.folha_resposta_jogador.decisao_tomada == "INTERDITAR"
    assert relatorio.folha_resposta_jogador.tempo_gasto_segundos == 150


def test_relatorio_sem_resposta_lanca_excecao(gabarito_simples):
    """
    T1: Acessar folha_resposta_jogador sem anexar resposta deve lançar ValueError.
    """
    relatorio = Relatorio(
        id_cenario=1,
        titulo="Teste",
        atividade="Teste",
        local="Teste",
        texto_descricao="Teste",
        envolvidos=["Aluno"],
        cursos=["Teste"],
        dificuldade=2,
        gabarito=gabarito_simples
    )
    with pytest.raises(ValueError, match="não foi anexada"):
        _ = relatorio.folha_resposta_jogador


def test_extrair_apresentacao_sem_anexos(gabarito_simples):
    """
    T2: Relatório sem anexos deve retornar lista vazia em extrair_apresentacao_relatorio.
    """
    relatorio = Relatorio(
        id_cenario=1,
        titulo="Teste",
        atividade="Teste",
        local="Teste",
        texto_descricao="Teste",
        envolvidos=["Aluno"],
        cursos=["Teste"],
        dificuldade=2,
        gabarito=gabarito_simples
    )
    dados = relatorio.extrair_apresentacao_relatorio()
    assert dados["anexos"] == []


def test_relatorio_bloqueia_id_cenario_zero(gabarito_simples):
    """
    T3a: id_cenario=0 deve ser rejeitado com ValueError.
    """
    with pytest.raises(ValueError, match="id_cenario deve ser positivo"):
        Relatorio(
            id_cenario=0,
            titulo="Teste",
            atividade="Teste",
            local="Teste",
            texto_descricao="Teste",
            envolvidos=["Aluno"],
            cursos=["Teste"],
            dificuldade=2,
            gabarito=gabarito_simples
        )


def test_relatorio_bloqueia_id_cenario_negativo(gabarito_simples):
    """
    T3b: id_cenario=-1 deve ser rejeitado com ValueError.
    """
    with pytest.raises(ValueError, match="id_cenario deve ser positivo"):
        Relatorio(
            id_cenario=-1,
            titulo="Teste",
            atividade="Teste",
            local="Teste",
            texto_descricao="Teste",
            envolvidos=["Aluno"],
            cursos=["Teste"],
            dificuldade=2,
            gabarito=gabarito_simples
        )
    