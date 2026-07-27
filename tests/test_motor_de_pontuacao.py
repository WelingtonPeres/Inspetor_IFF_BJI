import pytest
from core.model.relatorio import Relatorio
from core.model.folha_de_gabarito import FolhaDeGabarito
from core.model.anexo import AnexoImagem, AnexoVideo
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.services.motor_de_pontuacao import MotorDePontuacao


@pytest.fixture
def motor():
    return MotorDePontuacao()


@pytest.fixture
def gabarito_tipico():
    return FolhaDeGabarito(
        riscos=["FISICO", "QUIMICO"],
        fatores_inseguranca=["ATO_INSEGURO"],
        decisao_otima="INTERDITAR",
        decisao_boa="ADVERTIR"
    )


@pytest.fixture
def relatorio_tipico(gabarito_tipico):
    """
    Relatório com: 2 riscos, 1 fator (Ato), 1 imagem, 1 vídeo, 2 envolvidos, dificuldade=1
    """
    relatorio = Relatorio(
        id_cenario=1,
        titulo="Cenário Típico",
        atividade="Inspeção de Rotina",
        local="Setor A",
        texto_descricao="Inspeção padrão.",
        envolvidos=["João", "Maria"],
        cursos=["DEFALT"],
        dificuldade=1,
        gabarito=gabarito_tipico
    )
    relatorio.adicionar_anexo(AnexoImagem(1, "foto.png"))
    relatorio.adicionar_anexo(AnexoVideo(2, "video.mp4"))
    return relatorio


@pytest.fixture
def v_max_por_relatorio():
    """
    v_max individual do relatório_típico:
      BASE=1000
      + 2*250 (riscos)      = 500
      + 1*250 (fator)       = 250
      + 100   (imagem)      = 100
      + 300   (video)       = 300
      + 2*100 (envolvidos)  = 200
      = 2350
    """
    return 2350.0


@pytest.fixture
def dto_inspetor_perfeito():
    return DiagnosticoPontuacaoDTO(
        qnt_riscos_marcados=2,
        qnt_riscos_gabarito=2,
        qnt_riscos_corretos_marcados=2,
        estado_ato=True,
        estado_condicao=True,
        status_decisao_jogador="OTIMA",
        tempo_resposta_segundos=45.0
    )


@pytest.fixture
def dto_inspetor_negligente():
    return DiagnosticoPontuacaoDTO(
        qnt_riscos_marcados=0,
        qnt_riscos_gabarito=2,
        qnt_riscos_corretos_marcados=0,
        estado_ato=False,
        estado_condicao=False,
        status_decisao_jogador="INCORRETA",
        tempo_resposta_segundos=30.0
    )


@pytest.fixture
def dto_inspetor_desesperado():
    return DiagnosticoPontuacaoDTO(
        qnt_riscos_marcados=5,
        qnt_riscos_gabarito=1,
        qnt_riscos_corretos_marcados=1,
        estado_ato=True,
        estado_condicao=True,
        status_decisao_jogador="OTIMA",
        tempo_resposta_segundos=45.0
    )


@pytest.fixture
def dto_inspetor_lento():
    return DiagnosticoPontuacaoDTO(
        qnt_riscos_marcados=2,
        qnt_riscos_gabarito=2,
        qnt_riscos_corretos_marcados=2,
        estado_ato=True,
        estado_condicao=True,
        status_decisao_jogador="OTIMA",
        tempo_resposta_segundos=120.0
    )


class TestInspetorPerfeito:
    """
    Jogador acerta tudo em 45s (abaixo do ideal).
    Nota final deve ser exatamente v_max, condição de vitória True.
    """

    def test_nota_final_igual_v_max(self, motor, v_max_por_relatorio, dto_inspetor_perfeito):
        """Deve retornar exatamente v_max quando o jogador acerta tudo em tempo ideal."""
        
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_perfeito)
        assert nota == pytest.approx(v_max_por_relatorio)

    def test_condicao_vitoria_true(self, motor, v_max_por_relatorio, dto_inspetor_perfeito):
        """Vitória deve ser True quando nota atinge 100% do v_max."""
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_perfeito)
        assert motor.conferir_condicao_vitoria(nota, v_max_por_relatorio) is True


class TestInspetorNegligente:
    """
    Jogador não marca nada, erra tudo. Nota final = 0, vitória False.
    """

    def test_nota_final_zero(self, motor, v_max_por_relatorio, dto_inspetor_negligente):
        """Nota final deve ser 0 quando o jogador erra completamente."""
        
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_negligente)
        assert nota == pytest.approx(0.0)

    def test_condicao_vitoria_false(self, motor, v_max_por_relatorio, dto_inspetor_negligente):
        """Vitória deve ser False quando nota é 0."""
        
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_negligente)
        assert motor.conferir_condicao_vitoria(nota, v_max_por_relatorio) is False

    def test_nota_riscos_zero(self, motor, v_max_por_relatorio, dto_inspetor_negligente):
        """Pontuação de riscos deve ser 0 quando nenhum risco foi marcado."""
        
        nota = motor._calcular_pontuacao_riscos(
            v_max=v_max_por_relatorio,
            riscos_corretos_marcados=dto_inspetor_negligente.qnt_riscos_corretos_marcados,
            riscos_no_gabarito=dto_inspetor_negligente.qnt_riscos_gabarito,
            riscos_marcados=dto_inspetor_negligente.qnt_riscos_marcados
        )
        assert nota == pytest.approx(0.0)

    def test_nota_fatores_zero(self, motor, v_max_por_relatorio, dto_inspetor_negligente):
        """Pontuação de insegurança deve ser 0 quando Ato e Condição estão errados."""
        
        nota = motor._calcular_pontuacao_inseguranca(
            v_max=v_max_por_relatorio,
            acertou_ato=dto_inspetor_negligente.estado_ato,
            acertou_condicao=dto_inspetor_negligente.estado_condicao
        )
        assert nota == pytest.approx(0.0)

    def test_nota_decisao_zero(self, motor, v_max_por_relatorio, dto_inspetor_negligente):
        """Pontuação de decisão deve ser 0 quando a decisão é Incorreta."""
        
        nota = motor._calcular_pontuacao_decisao(v_max_por_relatorio, dto_inspetor_negligente.status_decisao_jogador)
        assert nota == pytest.approx(0.0)

class TestInspetorDesesperado:
    """
    1 risco real no gabarito, jogador marca 5 (1 correto + 4 falsos).
    Taxa de Descoberta = 100%, Taxa de Precisão = 20%.
    Nota de riscos severamente penalizada.
    """

    def test_taxa_descoberta_perfeita(self, dto_inspetor_desesperado):
        """Taxa de Descoberta deve ser 100% pois o único risco real foi encontrado."""
        
        td = (dto_inspetor_desesperado.qnt_riscos_corretos_marcados / dto_inspetor_desesperado.qnt_riscos_gabarito)
        assert td == pytest.approx(1.0)

    def test_taxa_precisao_penalizada(self, dto_inspetor_desesperado):
        """Taxa de Precisão deve ser 20% (1 correto de 5 marcados)."""
        
        tp = (dto_inspetor_desesperado.qnt_riscos_corretos_marcados / dto_inspetor_desesperado.qnt_riscos_marcados)
        assert tp == pytest.approx(0.2)

    def test_nota_riscos_penalizada(self, motor, v_max_por_relatorio, dto_inspetor_desesperado):
        """Nota de riscos deve ser inferior ao máximo possível devido aos falsos positivos."""
        
        nota_riscos = motor._calcular_pontuacao_riscos(
            v_max=v_max_por_relatorio,
            riscos_corretos_marcados=dto_inspetor_desesperado.qnt_riscos_corretos_marcados,
            riscos_no_gabarito=dto_inspetor_desesperado.qnt_riscos_gabarito,
            riscos_marcados=dto_inspetor_desesperado.qnt_riscos_marcados
        )
        
        nota_max_riscos = v_max_por_relatorio * motor.PESO_RISCOS
        
        assert nota_riscos < nota_max_riscos
        assert nota_riscos == pytest.approx(nota_max_riscos * 1.0 * 0.2)

    def test_nota_final_inferior_ao_maximo(self, motor, v_max_por_relatorio, dto_inspetor_desesperado):
        """Nota final deve ser menor que v_max devido à penalidade dos falsos alarmes."""
        
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_desesperado)
        assert nota < v_max_por_relatorio


class TestInspetorLento:
    """
    Jogador acerta tudo mas leva 120s (o dobro do ideal).
    Fator de tempo deve aplicar penalidade ou travar no LIMITE_MINIMO_RETENCAO.
    """

    def test_fator_tempo_no_limite_minimo(self, motor):
        """Fator de tempo deve ser LIMITE_MINIMO_RETENCAO para 120s (acima de 1.5x ideal)."""
        
        fator = motor._calcular_fator_tempo(120.0)
        assert fator == pytest.approx(MotorDePontuacao.LIMITE_MINIMO_RETENCAO)

    def test_nota_final_inferior_ao_maximo(self, motor, v_max_por_relatorio, dto_inspetor_lento):
        """Nota final deve ser menor que v_max devido à penalidade de tempo."""
        
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_lento)
        assert nota < v_max_por_relatorio

    def test_nota_final_igual_v_max_vezes_limite(self, motor, v_max_por_relatorio, dto_inspetor_lento):
        """Nota final deve ser exatamente v_max * LIMITE_MINIMO_RETENCAO (0.20)."""
        
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_lento)
        assert nota == pytest.approx(v_max_por_relatorio * MotorDePontuacao.LIMITE_MINIMO_RETENCAO)

    def test_condicao_vitoria_false(self, motor, v_max_por_relatorio, dto_inspetor_lento):
        """Vitória deve ser False quando a penalidade de tempo derruba a nota abaixo do limiar."""
        
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_lento)
        assert motor.conferir_condicao_vitoria(nota, v_max_por_relatorio) is False

class TestMetaDadosAusentes:
    """
    Testa calcular_meta_turno em condições adversas.
    """

    def test_lista_vazia_lanca_excecao(self, motor):
        """Lista vazia deve lançar AttributeError: não é permitido turno sem relatórios."""
        
        with pytest.raises(ValueError, match="Lista de Relatorios Vazio"):
            motor.calcular_meta_turno([])

    def test_lista_com_um_relatorio(self, motor, relatorio_tipico, v_max_por_relatorio):
        """Lista com um relatório válido deve retornar o v_max dele."""
        
        resultado = motor.calcular_meta_turno([relatorio_tipico])
        assert resultado == pytest.approx(v_max_por_relatorio)

    def test_lista_com_varios_relatorios(self, motor, relatorio_tipico, v_max_por_relatorio):
        """Lista com dois relatórios iguais deve somar o v_max de ambos."""
        
        resultado = motor.calcular_meta_turno([relatorio_tipico, relatorio_tipico])
        assert resultado == pytest.approx(v_max_por_relatorio * 2)

    def test_lista_com_relatorio_de_dificuldade_variavel(self, motor, gabarito_tipico):
        """Dificuldade diferente deve escalar o v_max proporcionalmente."""
        
        relatorio_facil = Relatorio(
            id_cenario=2, 
            titulo="Fácil", 
            atividade="A", 
            local="L",
            texto_descricao="", 
            envolvidos=["A"],
            cursos=["ST"], 
            dificuldade=1, 
            gabarito=gabarito_tipico
        )
        
        relatorio_dificil = Relatorio(
            id_cenario=3, 
            titulo="Difícil", 
            atividade="B", 
            local="L",
            texto_descricao="", 
            envolvidos=["B"],
            cursos=["ST"], 
            dificuldade=3, 
            gabarito=gabarito_tipico
        )
        
        resultado = motor.calcular_meta_turno([relatorio_facil, relatorio_dificil])
        v_max_sem_anexos = 1000 + 2 * 250 + 1 * 250 + 1 * 100
        esperado = v_max_sem_anexos * 1 + v_max_sem_anexos * 3
        
        assert resultado == pytest.approx(esperado)

    def test_relatorio_com_folha_gabarito_none_ignorado(self, motor):
        """Relatório com folha_gabarito=None deve ser ignorado (soma 0), sem quebrar o turno."""
        
        relatorio_quebrado = Relatorio(
            id_cenario=99,
            titulo="Quebrado",
            atividade="X",
            local="Y",
            texto_descricao="",
            envolvidos=["A"],
            cursos=["ST"],
            dificuldade=1,
            gabarito=None
        )
        
        resultado = motor.calcular_meta_turno([relatorio_quebrado])
        assert resultado == pytest.approx(0.0)

    def test_lista_mista_ignora_quebrados_e_soma_validos(self, motor, relatorio_tipico, v_max_por_relatorio):
        """Lista mista com relatórios válidos e quebrados deve somar apenas os válidos."""
        
        relatorio_quebrado = Relatorio(
            id_cenario=99,
            titulo="Quebrado",
            atividade="X",
            local="Y",
            texto_descricao="",
            envolvidos=["A"],
            cursos=["ST"], 
            dificuldade=1,
            gabarito=None
        )
        
        resultado = motor.calcular_meta_turno([relatorio_tipico, relatorio_quebrado, relatorio_tipico])
        assert resultado == pytest.approx(v_max_por_relatorio * 2)


class TestResilienciaAnexos:
    """
    Testa a resiliência do motor quando os anexos dos relatórios vêm corrompidos.
    """

    def test_relatorio_com_tipo_midia_desconhecido_ignorado(self, motor, gabarito_tipico, v_max_por_relatorio):
        """Anexo com tipo de mídia não mapeado (ex: DOCUMENTO) não deve quebrar nem adicionar bônus."""
        
        relatorio = Relatorio(
            id_cenario=10, 
            titulo="Documento", 
            atividade="A", 
            local="L",
            texto_descricao="", 
            envolvidos=["A"],
            cursos=["ST"], 
            dificuldade=1, 
            gabarito=gabarito_tipico
        )

        from core.model.anexo import Anexo

        class AnexoDocumento(Anexo):
            def get_tipo_midia(self) -> str:
                return "DOCUMENTO"

        relatorio.adicionar_anexo(AnexoDocumento(3, "doc.pdf"))
        resultado = motor.calcular_meta_turno([relatorio])
        v_max_sem_midia = 1000 + 2 * 250 + 1 * 250 + 1 * 100
        
        assert resultado == pytest.approx(v_max_sem_midia)

class TestCenarioFDivisaoPorZero:
    """
    Garante que _calcular_pontuacao_riscos não estoura ZeroDivisionError.
    """

    def test_riscos_corretos_zero_retorna_zero(self, motor, v_max_por_relatorio):
        """0 riscos corretos com gabarito > 0 deve retornar 0, sem divisão por zero."""
        
        nota = motor._calcular_pontuacao_riscos(
            v_max=v_max_por_relatorio,
            riscos_corretos_marcados=0,
            riscos_no_gabarito=5,
            riscos_marcados=0
        )
        
        assert nota == pytest.approx(0.0)

    def test_riscos_marcados_zero_retorna_zero(self, motor, v_max_por_relatorio):
        """0 riscos marcados com gabarito > 0 deve retornar 0: proteção contra ZeroDivisionError na taxa de precisão."""
        
        nota = motor._calcular_pontuacao_riscos(
            v_max=v_max_por_relatorio,
            riscos_corretos_marcados=0,
            riscos_no_gabarito=5,
            riscos_marcados=0
        )
        
        assert nota == pytest.approx(0.0)

    def test_gabarito_zero_e_jogador_marcou_zero_retorna_p_riscos_base(self, motor, v_max_por_relatorio):
        """Gabarito sem riscos e jogador sem marcações deve retornar o valor base de risco."""
        
        nota = motor._calcular_pontuacao_riscos(
            v_max=v_max_por_relatorio,
            riscos_corretos_marcados=0,
            riscos_no_gabarito=0,
            riscos_marcados=0
        )
        
        assert nota == pytest.approx(v_max_por_relatorio * MotorDePontuacao.PESO_RISCOS)

    def test_gabarito_zero_mas_jogador_marcou_algo_retorna_zero(self, motor, v_max_por_relatorio):
        """Gabarito sem riscos mas jogador marcou algo deve retornar 0 (falsos alarmes puros)."""
        
        nota = motor._calcular_pontuacao_riscos(
            v_max=v_max_por_relatorio,
            riscos_corretos_marcados=0,
            riscos_no_gabarito=0,
            riscos_marcados=3
        )
        
        assert nota == pytest.approx(0.0)

class TestMetodosInternos:
    """
    Testa individualmente os métodos privados do motor para garantir
    a matemática de cada componente isoladamente.
    """

    @pytest.mark.parametrize("ato,cond,esperado", [
        (True, True, 1.0),
        (True, False, 0.5),
        (False, True, 0.5),
        (False, False, 0.0),
    ])
    def test_coeficiente_exatidao(self, motor, v_max_por_relatorio, ato, cond, esperado):
        """Matriz de exatidão 2x2: valida o coeficiente para cada combinação de Ato e Condição."""
        nota = motor._calcular_pontuacao_inseguranca(v_max_por_relatorio, ato, cond)
        assert nota == pytest.approx(v_max_por_relatorio * MotorDePontuacao.PESO_FATORES * esperado)

    @pytest.mark.parametrize("status,multiplicador", [
        ("OTIMA", MotorDePontuacao.PESO_DECISAO_OTIMA),
        ("BOA", MotorDePontuacao.PESO_DECISAO_BOA),
        ("INCORRETA", 0.0),
        ("QUALQUER_OUTRA", 0.0),
    ])
    def test_pontuacao_decisao(self, motor, v_max_por_relatorio, status, multiplicador):
        """Mapeamento de decisão: OTIMA, BOA e INCORRETA devem gerar os multiplicadores corretos."""
        nota = motor._calcular_pontuacao_decisao(v_max_por_relatorio, status)
        assert nota == pytest.approx(v_max_por_relatorio * multiplicador)

    @pytest.mark.parametrize("tempo,esperado", [
        (30.0, 1.0),
        (60.0, 1.0),
        (75.0, 1.0 - 0.01 * 15),
        (90.0, 1.0 - 0.01 * 30),
        (91.0, MotorDePontuacao.LIMITE_MINIMO_RETENCAO),
        (120.0, MotorDePontuacao.LIMITE_MINIMO_RETENCAO),
        (999.0, MotorDePontuacao.LIMITE_MINIMO_RETENCAO),
    ])
    def test_fator_tempo(self, motor, tempo, esperado):
        """Decaimento temporal: testa as 3 faixas (ideal, decaimento linear, limite mínimo)."""
        fator = motor._calcular_fator_tempo(tempo)
        assert fator == pytest.approx(esperado)

    def test_fator_tempo_negativo_retorna_ideal(self, motor):
        """Tempo negativo deve retornar 1.0 (tratado como abaixo do ideal)."""
        fator = motor._calcular_fator_tempo(-10.0)
        assert fator == pytest.approx(1.0)

class TestFluxoCompleto:
    """
    Testa o encadeamento: calcular_meta_turno → calcular_pontuacao_relatorio → conferir_condicao_vitoria.
    """

    def test_turno_perfeito_vitoria(self, motor, relatorio_tipico, dto_inspetor_perfeito):
        """Fluxo completo: meta → pontuação → vitória True num turno perfeito."""
        
        v_max = motor.calcular_meta_turno([relatorio_tipico])
        nota = motor.calcular_pontuacao_relatorio(v_max, dto_inspetor_perfeito)
        
        assert nota == pytest.approx(v_max)
        assert motor.conferir_condicao_vitoria(nota, v_max) is True

    def test_turno_negligente_derrota(self, motor, relatorio_tipico, v_max_por_relatorio, dto_inspetor_negligente):
        """Fluxo completo: pontuação zero deve resultar em vitória False."""
        
        nota = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_negligente)
        assert motor.conferir_condicao_vitoria(nota, v_max_por_relatorio) is False


class TestConstantes:
    """
    Garante a integridade das constantes de calibragem do motor.
    """

    def test_pesos_somam_um(self):
        """Os pesos de riscos, fatores e decisão ótima devem somar exatamente 1.0."""
        
        total = (MotorDePontuacao.PESO_RISCOS
                 + MotorDePontuacao.PESO_FATORES
                 + MotorDePontuacao.PESO_DECISAO_OTIMA)
        assert total == pytest.approx(1.0)

    def test_limiar_vitoria_dentro_do_intervalo(self):
        """LIMIAR_VITORIA_TURNO deve estar entre 0 e 1 (percentual)."""
        
        assert 0.0 < MotorDePontuacao.LIMIAR_VITORIA_TURNO < 1.0


class TestVMaxNegativo:
    """
    T7: Testa se v_max negativo é tratado sem quebrar o motor.
    """

    def test_v_max_negativo(self, motor, dto_inspetor_perfeito):
        """v_max=-100 não deve crashar; o resultado propaga o valor negativo."""
        nota = motor.calcular_pontuacao_relatorio(-100, dto_inspetor_perfeito)
        assert isinstance(nota, (int, float))


class TestCondicaoVitoriaExatamenteNoLimiar:
    """
    T8: Testa condição de vitória exatamente no limiar de 60%.
    """

    def test_condicao_vitoria_exatamente_no_limiar(self, motor):
        """600/1000 = 60% → deve retornar True."""
        assert motor.conferir_condicao_vitoria(600.0, 1000.0) is True


class TestCalcularPontuacaoDetalhada:
    """
    Testes do novo metodo calcular_pontuacao_detalhada().
    """

    def test_retorna_dto_com_12_campos(self, motor, v_max_por_relatorio, dto_inspetor_perfeito):
        """O retorno deve ser DiagnosticoPontuacaoDTO com nota_riscos, nota_fatores, etc."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO()
        # Act
        r = motor.calcular_pontuacao_detalhada(v_max_por_relatorio, dto_inspetor_perfeito, f)
        # Assert
        assert r.nota_riscos > 0.0
        assert r.nota_fatores > 0.0
        assert r.nota_decisao > 0.0
        assert r.pontos_bonus_tempo == pytest.approx(0.0)
        assert r.pontuacao_final > 0.0

    def test_bonus_tempo_zero_abaixo_ideal(self, motor, v_max_por_relatorio, dto_inspetor_perfeito):
        """Com t=45s (<=60s), pontos_bonus_tempo deve ser 0.0."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO()
        # Act
        r = motor.calcular_pontuacao_detalhada(v_max_por_relatorio, dto_inspetor_perfeito, f)
        # Assert
        assert r.pontos_bonus_tempo == pytest.approx(0.0)

    def test_bonus_tempo_negativo_acima_ideal(self, motor, v_max_por_relatorio, dto_inspetor_lento):
        """Com t=120s (>90s), pontos_bonus_tempo deve ser < 0."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO()
        # Act
        r = motor.calcular_pontuacao_detalhada(v_max_por_relatorio, dto_inspetor_lento, f)
        # Assert
        assert r.pontos_bonus_tempo < 0.0

    def test_pontuacao_final_consistente_com_metodo_original(self, motor, v_max_por_relatorio, dto_inspetor_perfeito):
        """calcular_pontuacao_detalhada().pontuacao_final == calcular_pontuacao_relatorio()."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO()
        # Act
        original = motor.calcular_pontuacao_relatorio(v_max_por_relatorio, dto_inspetor_perfeito)
        detalhada = motor.calcular_pontuacao_detalhada(v_max_por_relatorio, dto_inspetor_perfeito, f)
        # Assert
        assert detalhada.pontuacao_final == pytest.approx(original)


class TestCalcularScoresPorItem:
    """
    Testes do novo metodo calcular_scores_por_item().
    """

    def test_retorna_dois_dicts(self, motor, v_max_por_relatorio):
        """O retorno deve ser uma tupla de dois dicionarios."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO(riscos_acertados=["FISICO"])
        # Act
        sr, sf = motor.calcular_scores_por_item(v_max_por_relatorio, f)
        # Assert
        assert isinstance(sr, dict)
        assert isinstance(sf, dict)

    def test_risco_acertado_score_positivo(self, motor, v_max_por_relatorio):
        """Riscos em riscos_acertados devem ter score > 0."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO(riscos_acertados=["FISICO"])
        # Act
        sr, _ = motor.calcular_scores_por_item(v_max_por_relatorio, f)
        # Assert
        assert sr.get("FISICO", 0.0) > 0.0

    def test_risco_inventado_score_negativo(self, motor, v_max_por_relatorio):
        """Riscos em riscos_inventados devem ter score < 0."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO(riscos_inventados=["ACIDENTE"])
        # Act
        sr, _ = motor.calcular_scores_por_item(v_max_por_relatorio, f)
        # Assert
        assert sr.get("ACIDENTE", 0.0) < 0.0

    def test_risco_esquecido_score_zero(self, motor, v_max_por_relatorio):
        """Riscos em riscos_esquecidos devem ter score 0.0."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO(riscos_esquecidos=["BIOLOGICO"])
        # Act
        sr, _ = motor.calcular_scores_por_item(v_max_por_relatorio, f)
        # Assert
        assert sr.get("BIOLOGICO", 0.0) == pytest.approx(0.0)

    def test_lista_vazia_nao_crasha(self, motor, v_max_por_relatorio):
        """Feedback com todas as listas vazias nao deve lancar excepcao."""
        # Arrange
        from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
        f = DiagnosticoFeedbackDTO()
        # Act
        sr, sf = motor.calcular_scores_por_item(v_max_por_relatorio, f)
        # Assert
        assert sr == {}
        assert sf == {}
