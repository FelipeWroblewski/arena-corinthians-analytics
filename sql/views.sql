--------------------------------------------------------------------------
--VW_DESEMPENHO_GERAL
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_desempenho_geral AS 
SELECT 
	COUNT(*) AS JOGOS,
	COUNT(*) FILTER (WHERE jg.resultado = 'V') AS VITORIAS,
	COUNT(*) FILTER (WHERE jg.resultado = 'E') AS EMPATES,
	COUNT(*) FILTER (WHERE jg.resultado = 'D') AS DERROTAS,
	ROUND(
        (
            (
                COUNT(*) FILTER (WHERE jg.resultado = 'V')
                + (COUNT(*) FILTER (WHERE jg.resultado = 'E') * 0.5)
            ) * 100.0
        ) / COUNT(*),
        2
    ) AS aproveitamento
FROM dim_jogos jg;

	
--------------------------------------------------------------------------
--VW_RESULTADOS_POR_ANO
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_resultados_por_ano AS 
SELECT
	jg.ano AS ANO,
	COUNT(*) FILTER (WHERE jg.resultado = 'V') AS VITORIAS,
	COUNT(*) FILTER (WHERE jg.resultado = 'E') AS EMPATES,
	COUNT(*) FILTER (WHERE jg.resultado = 'D') AS DERROTAS
FROM dim_jogos jg
GROUP BY
	jg.ano
ORDER BY jg.ano DESC;


--------------------------------------------------------------------------
--VW_JOGOS_POR_CAMPEONATO
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_jogos_por_campeonato AS 
SELECT 
	jg.campeonato,
	COUNT(*)
FROM dim_jogos jg
GROUP BY jg.campeonato
ORDER BY jg.campeonato ASC;


--------------------------------------------------------------------------
--VW_PUBLICO_MEDIO_POR_ANO
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_publico_medio_por_ano AS 
SELECT
	jg.ano AS ANO,
	ROUND(AVG(jg.publico_pagante), 2) AS PUBLICO_PAGANTE,
	ROUND(AVG(REPLACE(REPLACE(jg.renda, '.', ''), ',', '.')::NUMERIC), 2) AS RENDA
FROM dim_jogos jg
GROUP BY jg.ano
ORDER BY jg.ano DESC;


--------------------------------------------------------------------------
--VW_ARTILHARIA
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_artilharia AS 
SELECT
	gol.jogador AS JOGADOR,
	COUNT(gol.gol_id) AS QTD_GOL
FROM fato_gols gol
GROUP BY 
	gol.jogador
ORDER BY QTD_GOL DESC
LIMIT 8;


--------------------------------------------------------------------------
--VW_ESTILOS_GOL
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_estilos_gol AS 
SELECT  
	gol.estilo,
	COUNT(*) QTD_GOL
FROM fato_gols gol
GROUP BY
	gol.estilo
ORDER BY qtd_gol DESC
LIMIT 5;


--------------------------------------------------------------------------
--VW_TEMPOS_JOGO
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_tempos_jogo AS 
SELECT
	gol.tempo AS TEMPO,
	COUNT(*) AS QTD_GOL
FROM fato_gols gol
GROUP BY
	gol.tempo
ORDER BY gol.tempo ASC;


--------------------------------------------------------------------------
--VW_SETORES
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_setores AS 
SELECT
	gol.setor AS TEMPO,
	COUNT(*) AS QTD_GOL
FROM fato_gols gol
GROUP BY
	gol.setor
ORDER BY gol.setor ASC;


--------------------------------------------------------------------------
--VW_DUPLAS
--------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_duplas AS 
SELECT
	gol.jogador,
	gol.assistencia,
	count(*) AS qtd_gol
FROM fato_gols gol
WHERE gol.assistencia NOT IN ('(Pênalti)', 'X', '(Falta)')
GROUP BY 
	gol.jogador,
	gol.assistencia
ORDER BY qtd_gol DESC
LIMIT 6;