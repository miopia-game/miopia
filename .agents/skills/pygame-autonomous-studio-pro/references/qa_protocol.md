# QA autônomo: auditoria, visão, exploração e telemetria

Reutilize `.agents/skills/pygame-auto-qa/SKILL.md`, `tests/conftest.py`, `tests/auto_qa/test_gameplay_fuzz.py` e `qa.sh`. Os helpers adicionais não substituem a suíte. Eles não instalam pacotes nem modificam `src/`.

Nos exemplos, execute da raiz do Miopia com o Python de desenvolvimento que já tem pygame-ce. No Linux pode usar `.venv/bin/python`; no Windows `.venv\Scripts\python.exe`. Ajuste `python` ao ambiente real. `--repo .` é a raiz do jogo e `--out work/...` identifica a pasta de evidências.

## 1. Auditoria AST

```sh
python .agents/skills/pygame-autonomous-studio-pro/scripts/invariant_auditor.py . --out work/studio/ast.json
```

Qualifica imports/aliases de pygame/time e procura carregamento de imagens/fontes/sons ou sleep em callbacks/loops. Usa `src/` quando existir e exclui runtime/distribuições/testes. Achados são candidatos para inspecionar cache e frequência real; nenhum patch é aplicado. O scanner não prova correção de `dt`, física, vazamento, call graph completo ou posição subpixel. Não tratar toda chamada chamada `load` como Pygame.

## 2. Base e regressão com limite de execução

```sh
python .agents/skills/pygame-autonomous-studio-pro/scripts/run_qa.py --repo . --out work/studio/base --timeout 180
python .agents/skills/pygame-autonomous-studio-pro/scripts/run_qa.py --repo . --out work/studio/bots --timeout 180 -- tests/auto_qa -v --tb=short
```

O executor usa o Python da `.venv` se presente, roda pytest real, cria e remove `MIOPIA_DADOS` temporário, configura SDL dummy, desativa plugins externos e cache/bytecode. Salva log, comando, código de saída, duração e timeout. Não converta timeout em aprovação. O comando original `./qa.sh` também continua válido. Execute caso específico durante o ciclo e suíte completa ao encerrar mudança em código; não repita a bateria sem mudança ou dúvida concreta.

## 3. Capturas reais de menu e dos ensaios

```sh
python .agents/skills/pygame-autonomous-studio-pro/scripts/miopia_probe.py --repo . --out work/studio/capturas --mode captures
```

Captura menu e todos os ensaios disponíveis pela App, usando assets reais e `pygame.image.save`, sem Pillow. `--scene 'Raízes do Bosque'` limita um ensaio. Entrada preparada é rotulada; capturar a cena não equivale a completá-la. Inspecione as imagens, inclusive HUD, personagem, dicas e plataformas; métricas de cor/hash não substituem essa leitura.

## 4. Exploração por estados observados

```sh
python .agents/skills/pygame-autonomous-studio-pro/scripts/miopia_probe.py --repo . --out work/studio/exploracao --mode explore --scene 'Clareira da Vigília' --frames 10000 --seed 9101 --extreme
```

O bot mantém teclado virtual KEYDOWN/KEYUP pela fila real, usa macros de ações, favorece ações menos tentadas por estado e registra células/flags/transições em grafo. Registra cada quadro e entrada em `trace.jsonl`; estado do ator, recursos, inimigos/projéteis, memória Python e tempo de update em JSON; capturas periódicas e falha. Usa banco em memória e perfil descartável. Não atribui vitória nem teletransporta durante a exploração; a entrada da cena é um fixture explícito.

Use seeds 9101/9102/9103 para comparação e o piloto conhecido em `tests/test_campanha.py` para provar a rota principal. Não há promessa de solver completo: o bot não enumera todos os estados possíveis, não calcula uma porcentagem de mapa coberto e não prova que uma zona não observada seja inacessível. Transições de mapa e flags distinguem estados além de coordenadas.

`--extreme` inclui pedido de dt=0,001; também há 1/120, 1/60, 0,05 e 0,15. São inputs diagnósticos: a Jornada já limita/subdivide o tempo. O log preserva o dt pedido sem alegar que todo ele virou tempo físico. Amplie uma macro ou política somente para um comportamento real identificado.

## 5. Validação visual por contrato

```sh
python .agents/skills/pygame-autonomous-studio-pro/scripts/visual_probe.py work/studio/capturas/menu.png
```

`analyze_surface` mede uma Surface/ROI. `compare_surfaces` mede mudança de pixels. `assert_visual_progression(before.copy(), after)` exige mudança somente quando esse é o contrato; cópia independente evita comparar a mesma Surface mutada. Na CLI, `--before imagem.png --expect-change` aplica essa condição. Tela escura/monocromática ou estática é evidência contextual, não crash automático; pausa, fades e breu são casos legítimos. Para jogador/HUD, identifique a região esperada e confronte estado, desenho e imagem. Um hash diferente pode ser só partícula; não prova atualização de gameplay.

## 6. Estabilidade e diagnóstico

Use a bateria existente para 3.000 quadros estáveis após aquecimento, três sementes de 1.100 quadros, colisões de um pixel e cinco ciclos menu/pausa/morte/reinício. Um sprint maior pode justificar 10.000 quadros e dez ciclos; registre orçamento e cenário, sem inventar duração de execução.

`tracemalloc` mede alocações Python; grafo/logs do explorador também retêm memória. Compare crescimento de entidades/partículas/projéteis com um cenário de população limitada e assets aquecidos; cache novo e mudança de sala não provam vazamento. Os tempos do SDL dummy não são FPS ou latência reais do notebook. Use `tools/medir_desempenho.py` e testes em equipamento real para esse aceite.

Ao falhar: preservar seed/quadro/eventos/estado/traceback/captura, reproduzir a menor sequência, separar bug de harness/ambiente, corrigir a causa em `src/`, reexecutar caso e regressão. Não mascarar asset ausente com mocks. Fallback só é teste de recuperação intencional, identificado; não valida a entrega normal.
