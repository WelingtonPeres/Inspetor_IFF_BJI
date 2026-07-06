import pytest
from core.model.folha_de_gabarito import FolhaDeGabarito
from core.model.folha_de_resposta import FolhaDeResposta
from core.services.diagnostico_de_resposta import DiagnosticoDeResposta
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


@pytest.fixture
def diagnostico_servico():
    """Instância do serviço a ser testado."""
    return DiagnosticoDeResposta()


@pytest.fixture
def gabarito_simples():
    """Gabarito básico: 3 riscos, Ato e Condição, decisão ótima INTERDITAR."""
    return FolhaDeGabarito(
        riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
        fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
        decisao_otima="INTERDITAR",
        decisao_boa="ADVERTIR"
    )


@pytest.fixture
def gabarito_sem_fatores():
    """Gabarito com listas vazias: nenhum risco, nenhum fator."""
    return FolhaDeGabarito(
        riscos=[],
        fatores_inseguranca=[],
        decisao_otima="IGNORAR",
        decisao_boa="ADVERTIR"
    )


@pytest.fixture
def gabarito_apenas_ato():
    """Gabarito com apenas Ato Inseguro, sem Condição Insegura."""
    return FolhaDeGabarito(
        riscos=["FISICO"],
        fatores_inseguranca=["ATO_INSEGURO"],
        decisao_otima="ADVERTIR",
        decisao_boa="IGNORAR"
    )


@pytest.fixture
def gabarito_apenas_condicao():
    """Gabarito com apenas Condição Insegura, sem Ato Inseguro."""
    return FolhaDeGabarito(
        riscos=["ERGONOMICO"],
        fatores_inseguranca=["CONDICAO_INSEGURA"],
        decisao_otima="INTERDITAR",
        decisao_boa="IGNORAR"
    )


class TesteSuite1CaminhoFeliz:
    """
    Testa se o sistema funciona perfeitamente quando o jogador faz 
    exatamente o esperado.
    """

    def test_diagnostico_perfeito(self, diagnostico_servico, gabarito_simples):
        """
        Jogador marca todos os riscos exatos do gabarito, marca os fatores 
        exatos do gabarito e toma a decisão ótima.        
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="INTERDITAR",
            tempo_gasto_segundos=45.5
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert isinstance(resultado, DiagnosticoPontuacaoDTO)
        assert resultado.qnt_riscos_corretos_marcados == 3
        assert resultado.qnt_riscos_gabarito == 3
        assert resultado.qnt_riscos_marcados == 3
        assert resultado.estado_ato is True
        assert resultado.estado_condicao is True
        assert resultado.status_decisao_jogador == "OTIMA"
        assert resultado.tempo_resposta_segundos == 45.5

    def test_diagnostico_cenario_seguro_perfeito(self, diagnostico_servico, gabarito_sem_fatores):
        """
        Gabarito não tem nenhum risco nem fator de insegurança, e o jogador 
        sabiamente entrega a folha em branco com a decisão ótima de 
        IGNORAR.
        """
        resposta = FolhaDeResposta(
            riscos=[],
            fatores_inseguranca=[],
            decisao_tomada="IGNORAR",
            tempo_gasto_segundos=12.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_sem_fatores, resposta)
        
        assert resultado.qnt_riscos_corretos_marcados == 0
        assert resultado.qnt_riscos_gabarito == 0
        assert resultado.qnt_riscos_marcados == 0
        assert resultado.estado_ato is True  
        assert resultado.estado_condicao is True  
        assert resultado.status_decisao_jogador == "OTIMA"


class TesteSuite2MatematicaDosRiscos:
    """
    Testa a capacidade do `set()` de calcular interseções, excessos e faltas 
    através da operação de conjuntos.
    """

    def test_riscos_acerto_parcial_sem_falso_positivo(self, diagnostico_servico, gabarito_simples):
        """
        Jogador marca 2 riscos corretamente, mas o gabarito pedia 4 riscos. 
        Verifica a omissão de 2 riscos.
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="ADVERTIR",
            tempo_gasto_segundos=30.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.qnt_riscos_corretos_marcados == 2
        assert resultado.qnt_riscos_marcados == 2
        assert resultado.qnt_riscos_gabarito == 3

    def test_riscos_excesso_de_zelo_com_falso_positivo(self, diagnostico_servico, gabarito_simples):
        """
        Jogador marca os 3 riscos corretos do gabarito, mas inventa mais 2 
        riscos que não existiam na cena.
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO", "ACIDENTE", "ERGONOMICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="INTERDITAR",
            tempo_gasto_segundos=55.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.qnt_riscos_corretos_marcados == 3
        assert resultado.qnt_riscos_marcados == 5
        assert resultado.qnt_riscos_gabarito == 3
        
        assert resultado.qnt_riscos_marcados - resultado.qnt_riscos_corretos_marcados == 2

    def test_riscos_desalinhamento_completo(self, diagnostico_servico, gabarito_simples):
        """
        Gabarito pede Físico, Químico, Biológico. 
        Jogador marca Acidente, Ergonômico. 
        Nenhuma sobreposição (acertos = 0).
        """
        resposta = FolhaDeResposta(
            riscos=["ACIDENTE", "ERGONOMICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="INTERDITAR",
            tempo_gasto_segundos=20.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.qnt_riscos_corretos_marcados == 0
        assert resultado.qnt_riscos_marcados == 2
        assert resultado.qnt_riscos_gabarito == 3

    def test_riscos_duplicados_na_resposta_ignorados(self, diagnostico_servico, gabarito_simples):
        """
        Jogador (por um bug na UI) envia lista com ["FISICO", "FISICO", "QUIMICO"].
        O uso de `set()` deve transformar duplicatas em uma única marcação.
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "FISICO", "QUIMICO"],
            fatores_inseguranca=["ATO_INSEGURO"],
            decisao_tomada="ADVERTIR",
            tempo_gasto_segundos=25.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.qnt_riscos_corretos_marcados == 2
        assert resultado.qnt_riscos_marcados == 2  # set() eliminou duplicatas


class TesteSuite3FatoresDeInseguranca:
    """
    Testa a matriz de verdade (2×2) da verificação binária de 
    Ato e Condição através de comparações de igualdade.
    """

    def test_fatores_acerto_ato_e_erro_condicao(self, diagnostico_servico, gabarito_simples):
        """
        Jogador diagnostica perfeitamente o Ato Inseguro (presente),
        mas erra o estado da Condição Insegura (não marca quando deveria).
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=["ATO_INSEGURO"],  # Falta CONDICAO_INSEGURA
            decisao_tomada="INTERDITAR",
            tempo_gasto_segundos=40.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.estado_ato is True
        assert resultado.estado_condicao is False

    def test_fatores_erro_ato_e_acerto_condicao(self, diagnostico_servico, gabarito_simples):
        """
        Jogador erra o estado do Ato Inseguro (marca quando não deveria),
        mas diagnostica corretamente a Condição Insegura (presente).
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=["CONDICAO_INSEGURA"],  # Falta ATO_INSEGURO
            decisao_tomada="INTERDITAR",
            tempo_gasto_segundos=38.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.estado_ato is False
        assert resultado.estado_condicao is True

    def test_fatores_erro_por_omissao_total(self, diagnostico_servico, gabarito_simples):
        """
        Gabarito exigia Ato e Condição marcados, mas o jogador não marcou 
        nenhum (listas vazias).
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=[],  # Totalmente vazio
            decisao_tomada="ADVERTIR",
            tempo_gasto_segundos=15.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.estado_ato is False
        assert resultado.estado_condicao is False

    def test_fatores_erro_por_falso_positivo_total(self, diagnostico_servico, gabarito_sem_fatores):
        """
        Gabarito não possuía nenhum fator (listas vazias), mas o jogador 
        marcou Ato e Condição (ambos presentes na resposta).
        """
        resposta = FolhaDeResposta(
            riscos=[],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="ADVERTIR",
            tempo_gasto_segundos=20.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_sem_fatores, resposta)
        
        assert resultado.estado_ato is False
        assert resultado.estado_condicao is False


class TesteSuite4DecisaoAdministrativa:
    """
    Decisão Administrativa (Condicionais)
  
    """

    def test_decisao_mapeia_como_otima(self, diagnostico_servico, gabarito_simples):
        """
        String da resposta é exatamente igual à `decisao_otima` do gabarito 
        (INTERDITAR == INTERDITAR).
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="INTERDITAR",  # Igual à decisao_otima
            tempo_gasto_segundos=50.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.status_decisao_jogador == "OTIMA"

    def test_decisao_mapeia_como_boa(self, diagnostico_servico, gabarito_simples):
        """
        String da resposta é exatamente igual à `decisao_boa` do gabarito 
        (ADVERTIR == ADVERTIR).
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="ADVERTIR",  # Igual à decisao_boa
            tempo_gasto_segundos=48.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.status_decisao_jogador == "BOA"

    def test_decisao_mapeia_como_incorreta_acao_nao_mapeada(self, diagnostico_servico, gabarito_simples):
        """
        Resposta do jogador não bate com nenhuma das chaves de sucesso 
        (não é decisao_otima nem decisao_boa).
        """
        # gabarito_simples: decisao_otima="INTERDITAR", decisao_boa="ADVERTIR"
        # Resposta: "IGNORAR" (nenhuma das duas)
        
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="IGNORAR",  # Não corresponde a nenhuma chave
            tempo_gasto_segundos=35.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.status_decisao_jogador == "INCORRETA"

    def test_decisao_incorreta_em_branco(self, diagnostico_servico, gabarito_simples):
        """
        Resposta do jogador vem como uma string vazia `""` (hipotético erro de UI).
        Garante que o código não crasha e cai corretamente no estado "INCORRETA".
        """
        # A FolhaDeResposta valida a decisão, então usamos uma decisão válida
        # mas diferente da ótima/boa para simular "não mapeada"
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="IGNORAR",  # Válida, mas não mapeada ao gabarito
            tempo_gasto_segundos=5.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.status_decisao_jogador == "INCORRETA"


class TesteSuite5EdgeCases:
    """
    Edge Cases (Casos Extremos de DTO)
    
    Testa se o transporte final para o DTO preserva a integridade 
    de outras variáveis brutas em condições extremas.
    """

    def test_dto_transporta_tempo_corretamente(self, diagnostico_servico, gabarito_simples):
        """
        Verifica se o `tempo_gasto_segundos` (ex: `45.5`) entra e sai 
        ileso para o DTO, sem ser truncado ou convertido.
        """
        tempo_entrada = 45.5
        resposta = FolhaDeResposta(
            riscos=["FISICO", "QUIMICO", "BIOLOGICO"],
            fatores_inseguranca=["ATO_INSEGURO", "CONDICAO_INSEGURA"],
            decisao_tomada="INTERDITAR",
            tempo_gasto_segundos=tempo_entrada
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, resposta)
        
        assert resultado.tempo_resposta_segundos == tempo_entrada
        assert isinstance(resultado.tempo_resposta_segundos, float)

    def test_listas_completamente_vazias(self, diagnostico_servico, gabarito_sem_fatores):
        """
        Envia `[]` em todos os parâmetros de resposta e gabarito. 
        O código deve processar tudo sem dar erros de "Index out of bounds" 
        ou divisão por zero, devolvendo o DTO zerado perfeitamente.
        """
        resposta = FolhaDeResposta(
            riscos=[],
            fatores_inseguranca=[],
            decisao_tomada="IGNORAR",
            tempo_gasto_segundos=0.0
        )
        
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_sem_fatores, resposta)
        
        assert isinstance(resultado, DiagnosticoPontuacaoDTO)
        assert resultado.qnt_riscos_marcados == 0
        assert resultado.qnt_riscos_gabarito == 0
        assert resultado.qnt_riscos_corretos_marcados == 0
        assert resultado.estado_ato is True
        assert resultado.estado_condicao is True
        assert resultado.status_decisao_jogador == "OTIMA"
        assert resultado.tempo_resposta_segundos == 0.0


class TesteSuite6FixturesNaoUtilizadas:
    """
    Testes para fixtures existentes mas sem cobertura.
    """

    def test_diagnostico_apenas_ato(self, diagnostico_servico, gabarito_apenas_ato):
        """
        Gabarito com apenas ATO_INSEGURO, sem CONDICAO_INSEGURA.
        Jogador acerta Ato e não marca Condição → estado_ato True,
        estado_condicao True (condição ausente no gabarito, não marcada = correto).
        """
        resposta = FolhaDeResposta(
            riscos=["FISICO"],
            fatores_inseguranca=["ATO_INSEGURO"],
            decisao_tomada="ADVERTIR",
            tempo_gasto_segundos=30.0
        )
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_apenas_ato, resposta)
        assert resultado.estado_ato is True
        assert resultado.estado_condicao is True

    def test_diagnostico_apenas_condicao(self, diagnostico_servico, gabarito_apenas_condicao):
        """
        Gabarito com apenas CONDICAO_INSEGURA, sem ATO_INSEGURO.
        Jogador acerta Condição e não marca Ato → ambos True.
        """
        resposta = FolhaDeResposta(
            riscos=["ERGONOMICO"],
            fatores_inseguranca=["CONDICAO_INSEGURA"],
            decisao_tomada="INTERDITAR",
            tempo_gasto_segundos=40.0
        )
        resultado = diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_apenas_condicao, resposta)
        assert resultado.estado_ato is True
        assert resultado.estado_condicao is True


class TesteSuite7DiagnosticoNone:
    """
    T12: Garantir que gerar_diagnostico_pontuacao levanta ValueError
    quando recebe None em qualquer parâmetro.
    """

    def test_diagnostico_gabarito_none(self, diagnostico_servico):
        """gabarito=None deve levantar ValueError."""
        resposta = FolhaDeResposta(
            riscos=["FISICO"],
            fatores_inseguranca=["ATO_INSEGURO"],
            decisao_tomada="INTERDITAR",
            tempo_gasto_segundos=30.0
        )
        with pytest.raises(ValueError, match="DiagnosticoDeResposta"):
            diagnostico_servico.gerar_diagnostico_pontuacao(None, resposta)

    def test_diagnostico_respostas_none(self, diagnostico_servico, gabarito_simples):
        """respostas=None deve levantar ValueError."""
        with pytest.raises(ValueError, match="DiagnosticoDeResposta"):
            diagnostico_servico.gerar_diagnostico_pontuacao(gabarito_simples, None)
