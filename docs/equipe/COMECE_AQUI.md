Para trabalhar no repositório, comece pelo [guia de continuidade da revisão jogável](GUIA_DE_CONTINUIDADE.md). As instruções abaixo documentam a entrega S40 original.

# Miopia para a equipe

Se você recebeu o pacote S40, comece pelo [prompt para GPT ou Claude](PROMPT_EQUIPE.md),
pelo [checklist de implementação](CHECKLIST_EQUIPE.md) e pelo
[guia de pesquisa](PESQUISA_EQUIPE.md). O [plano](PLANO.md) indica os cartões
que podem ser assumidos.

Ferramentas integradas no Q10.0: leia [PROMPT_STUDIO.md](PROMPT_STUDIO.md) e
`.agents/skills/pygame-autonomous-studio-pro/SKILL.md`, junto do pygame-auto-qa.
Há auditoria AST, capturas reais, exploração limitada e executor da suíte com
log/timeout. Comandos e limites em [Q10.0-studio.md](Q10.0-studio.md). Usar por
leitura explícita; copiar a pasta não instala plugin global nem garante sua
exibição imediata no catálogo. A autorização de cada sprint continua no PLANO.

Esta pasta permite continuar o jogo com outra pessoa ou sessão de IA.
O protagonista é Lume, um vaga-lume míope. Luz, orientação, combate e o
retorno do orvalho às bordas da floresta precisam explicar a mesma aventura.
O objetivo de produto é um metroidvania difícil, com ataques legíveis,
exploração vertical contínua e personagens que motivem o jogador a voltar.

1. Leia ESTADO_ATUAL.md para distinguir código existente de proposta.
2. Leia FEEDBACK_2026-11-12.md. As críticas substituem preferências anteriores
   sobre breu absoluto e minimapa sempre visível.
3. Siga a ordem dos [próximos sprints no PLANO](PLANO.md#próximos-sprints-a-partir-do-s36) e confira VALIDACAO.md.
4. Combine quem edita cada arquivo. Uma pessoa integra e gera a entrega.
5. Registre cada mudança em HISTORICO.md e atualize o estado do cartão.

O [S40](S40.md) guarda o remapeamento e as preferências de leitura e clarão.
Controles reconhecidos pelo SDL navegam nos menus e na partida.
O [S39](S39.md) liga a restauração da água a travessias no Bosque
e no Córrego. Tila e Bento abrem atalhos ao trabalhar na trilha.
O [S38](S38.md) diferencia os cortes na Cobra dos Berços, os papéis
das patrulhas e o uso de consumíveis. O Nicho e a Patrulha em dupla
permitem alternar as armas com V.
O [S37](S37.md) dá à Câmara da Escuta uma descida em duas grades,
uma escadaria de pedra e uma passarela de retorno. O mapa da Gruta
marca onde Lume pisou em âmbar.
O [S36](S36.md) preserva o save na vitória e os recursos na volta
voluntária. Esc → Ajustes permite escolher a dificuldade da História
para aplicar no próximo marco.
O [S35](S35.md) abre o Nicho dos Berços após a veneziana do Taquaral.
A Cobra dos Berços protege o depósito e sua luz permanente.
O [S34](S34.md) dá avisos e respostas distintos aos rasantes e às
quedas de penas do Último Chamado. Cada resgate alarga a resposta.
O [S33](S33.md) coloca Tila, Bento e Aru na ponte, na calha e na nascente
do Jardim. As escolhas mostram os itens e os trechos iluminados.
O [S32](S32.md) conta o desvio do Córrego pelas marcas do canal e dos
berços. Casca e Fio se reencontram quando a água volta. Os quatro
guardiões foram recalibrados e a Tecelã chama reforços.
O [S31](S31.md) revê a história da abertura ao pós-jogo. O diário
resume cada travessia, o sino prepara a Coruja e o desfecho acompanha
os resgates e a estufa.
O [S30](S30.md) abre a Galeria das Sementes sob o Taquaral, com patrulha,
pedido de Risca e retorno pela chaminé após o reparo.
O [S29](S29.md) abre um desvio vertical no Taquaral. Sementes indicam a
subida, a deriva lateral e a passagem sob a aba. O Campo de testes
permite começar no pé dos colmos.
O [S28](S28.md) acrescenta a caça na Ponte das Lanternas, a isca de luz
e posturas próprias para a cobra e a vespa.
O [S27](S27.md) liga as duas margens pelo pedido de Fio e pela
passarela que ela repara após a entrega.
O [S26](S26.md) dá movimento à comporta do Viveiro e mostra a água
seguindo para a cisterna.
O [S25](S25.md) alterna os ataques das patrulhas no escuro e ajusta a
chegada no ensaio da Vigília.
No [S24](S24.md), Lume pode rebater num casulo do Poço da Seiva e alcançar
um nicho que guarda um Pavio de pólen.
No [S23](S23.md), a aranha das Raízes do Córrego investiga pousos.
O [S22](S22.md) trouxe lições práticas à História e os controles ao diário.
O [S21](S21.md) pôs uma veneziana e uma pista para Véspera no Arquivo da
Casca. O [S20](S20.md) ligou o Poço da Seiva e o Arquivo por um atalho
opcional. O ciclo [S15–S19](S19.md) trouxe orientação na Coruja e no Jardim,
avisos reservados e Agulha na História. A escolha de Tila ficou mais clara no
[S14](S14.md). No [S13](S13.md), **Repetir o ensaio** na pausa do Campo
de testes passou a iniciar a cena do zero. O [S12](S12.md) trouxe
redesenho mais leve para mapas pouco descobertos. A edição acadêmica [S11](S11.md) recebe 14
trilhas e a revisão de Tiago. Use Campo de testes para acessar as arenas e
comparar os temas. O plano de Steam foi arquivado a pedido de Thierry.

A base local anterior é o S10. Leia S10.md: pistas atuais inteiras no painel
e reconsulta da orientação do ensaio por M, com cabeçalho próprio. As duas
rotinas locais de desenvolvimento acompanham as novas entregas. R10.1 está
tecnicamente corrigido e continua aguardando seu parecer humano.

A base anterior é o S09. Leia S09.md: Infinito removido, objetivo no alto
do mapa, avisos breves que evitam Lume e descidas sinalizadas com câmera que
abre espaço abaixo. `./qa.sh` roda os testes com perfil temporário; instale
requirements-dev.txt para desenvolver. A rotina em
`.agents/skills/pygame-auto-qa/SKILL.md` acompanha a entrega para Codex/Claude.
As mudanças visuais/didáticas aguardam avaliação de Thierry.

A base anterior é o S08. Leia S08.md: vida/brilho separados, brilho estável,
luz atravessando terreno, K de 520 px, combos J/L/K e Ctrl, globos/tochas,
patrulhas, tutorial contextual e mapa navegável. Thierry decidiu as duas barras;
não reabrir a decisão do C06 como se ainda faltasse autorização. C05/armas e
A02/músicas continuam em revisão humana. S07.md descreve resgates, Jardim,
último chamado e pós-jogo. S06.md descreve
o Bosque, Caruncho, cipó e provisões/save. S05.md descreve arenas e armas.
Leia S04.md e combos-S04.json para visão,
missões, ferramentas e repertório de combate. Desempenho local está em
desempenho-S04.json até desempenho-S08-cenas.json e desempenho-S08-mapa.json; execute
tools/medir_desempenho.py para medir novamente.

## Como abrir

Na pasta de equipe exportada, o executável `Miopia` fica na raiz e inclui
runtime para Linux x86_64. Extraia a pasta inteira. A versão Windows precisa
ser executada a partir do código com Python e pygame-ce; não há executável
Windows pronto. O código foi testado em Linux.

Para desenvolver com Python instalado:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m src.main
```

No Windows use `.venv\Scripts\python.exe` nos comandos equivalentes.
Não envie sua `.venv`. O pacote já contém assets, código, testes, fontes,
avisos e documentação. Os dados do jogador ficam fora da instalação.

## Organização

| Local | Responsabilidade |
|---|---|
| src/travessia.py, combate.py | Física, entrada, recursos e inimigos comuns |
| src/chefes.py, arte_arena.py | Regras, estados e desenho das arenas |
| src/casco.py, coruja.py, oficina_armas.py | Fases móveis e protótipo isolado de armas do S05 |
| src/fases.py, corte_vertical.py, subsolo.py | Topologia e mecanismos |
| src/raizes_bosque.py, arte_raizes.py, recursos.py | Região contínua do Bosque, mini-chefe e provisões finitas |
| src/resgates.py, jardim.py, ultimo_chamado.py | Sobreviventes, estufa contínua e clímax com sinais de luz |
| src/arte_resgates.py, arte_jardim.py, escuta.py | Desenho original e sala de comparação dos avisos |
| src/avisos.py, sinalizacao.py | Dicas que evitam Lume, abertura de câmera e sinais de descida |
| src/luzes_mundo.py, encontros.py, tutorial.py | Globos/tochas persistentes, patrulhas e ensino durante a partida |
| src/mapa_visor.py, marcas_mapa.py | Zoom, movimento, cache e anotações do jogador |
| src/taticas.py, ferramentas.py, missoes.py | Combos, consumíveis e painel de pedidos |
| src/visao.py, paisagem.py, arte_corte.py | Nitidez, clarão e renderização |
| src/descoberta.py, cartografia.py, orientacao.py | Exploração e objetivos |
| src/narrativa.py, roteiro.py, ambiental.py | Pedidos, diálogos e caderno |
| src/main.py, controles.py, telas.py, audio.py | App, entrada, interface e mistura de áudio |
| tests/ | Regressões físicas, campanha, interface e replay |
| docs/equipe/ | Estado e trabalho atual |
| outputs/ | Atlas e quadro XLSX históricos, úteis como referências |

## Prompt de retomada

> Leia AGENTS.md e docs/equipe. Execute somente o cartão [ID] livre do plano.
> Antes de editar, reproduza seu problema. Preserve o feedback atual e os saves.
> Entregue código, teste apropriado, instrução curta para jogar e registro do
> que ainda precisa de avaliação humana. Atualize ESTADO_ATUAL e HISTORICO.
> Não publique nem marque permissões comerciais pendentes como resolvidas.

O Codex desta sessão não recebe um indicador confiável de percentual da cota
da conta. Thierry acompanha o painel e pede uma nova exportação ao chegar
ao limite desejado. `tools/preparar_equipe.py` gera um snapshot atualizado
sob demanda; arquivos de exportação anteriores são preservados.
Use `--sem-a3` para manter o atlas e a documentação do jogo na cópia de
desenvolvimento, com as entregas acadêmicas na pasta original.
