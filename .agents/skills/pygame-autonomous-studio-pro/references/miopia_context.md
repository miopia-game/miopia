# Contexto confirmado e localização do código

Referência lida em 13/11/2026: S09, Python 3.14.10 no ambiente disponível, pygame-ce 2.5.8 e pytest 9.2.0. Confirme novamente em outra cópia. O S09 reporta historicamente 238 testes e 26 ensaios. A branch local estava sem commits, com arquivos não rastreados; todos pertencem ao usuário.

## Fontes

`AGENTS.md` aponta para `docs/equipe/COMECE_AQUI.md`, `ESTADO_ATUAL.md`, `PLANO.md`, `VALIDACAO.md` e `FEEDBACK_2026-11-12.md`. Os cabeçalhos recentes e `S09.md` substituem seções históricas. `docs/continuidade.md`, `mapas.md` e `guardioes.md` contêm história e fichas anteriores; leia seus avisos de atualização. Atlas/XLSX e relatórios S00–S02 são referências históricas.

| Código | Responsabilidade |
|---|---|
| `src/main.py`, `telas.py` | App, eventos, entrada normal, telas, pausa e diário |
| `travessia.py`, `combate.py`, `taticas.py` | Jornada, movimento, recursos, golpes e inimigos comuns |
| `fases.py`, `corte_vertical.py`, `subsolo.py`, `raizes_bosque.py`, `jardim.py` | Geografia e progressão |
| `chefes.py`, `casco.py`, `coruja.py`, `ultimo_chamado.py` | Encontros e clímax |
| `narrativa.py`, `roteiro.py`, `missoes.py`, `resgates.py`, `ambiental.py` | Continuidade, diálogos, pedidos e registros |
| `memoria.py`, `recursos.py`, `luzes_mundo.py` | Save, provisões e luz persistente |
| `visao.py`, `paisagem.py`, `avisos.py`, `sinalizacao.py`, `tutorial.py`, `mapa_visor.py` | Percepção e interface |

## Contratos atuais

Miopia já é lateral. Quatro biomas: Bosque das Samambaias, Córrego Fundo, Taquaral e Gruta da Figueira. Guardiões: Asa Fendida, Tecelã do Vão, Casco Oco e Coruja; Caruncho é mini-chefe no Bosque. O Infinito foi retirado no S09. Não restaurar requisitos históricos.

Vida/brilho separados; brilho estável, zero brilho apaga halo sem matar. K/Ctrl gastam brilho e completam custo com vida. K tem alcance de 520 px e luz atravessa terreno. Marcos não curam; abrigos têm reservas finitas. Objetivo no topo do mapa M/Tab; dicas breves evitam Lume. Navegar no mapa não revela terreno novo. Globos/tochas, recompensas e derrotas relevantes persistem conforme o save.

Lume é um vaga-lume míope; Breu, Figueira, orvalho e Coruja estão na continuidade atual. O retorno da água/luz às bordas dá consequência à aventura. Use os personagens existentes e verifique suas falas/flags antes de escrever novos fatos. Coruja é acalmada e permanece viva.

## Próxima fila documentada

R10.1: revisar dicas/primeira descida, depende do primeiro ponto não percebido relatado por Thierry. R10.2: combate na Vigília, sem encerrar C05 por automação. R10.3: câmera/globos e conforto. N10.1: uma conversa e consequência, após R10.1. A02 requer escuta/parecer; D01 envolve 14 grupos de origem/licença. Faça evidência técnica enquanto o aceite humano permanece pendente.

Pacote verificado historicamente: Linux x86_64. Windows tem atalho de desenvolvimento, sem executável offline confirmado. Código oficial em `src/`; só o integrador gera distribuição. `docs/s00-origens.md` mantém pendências para publicação externa/comercial.
