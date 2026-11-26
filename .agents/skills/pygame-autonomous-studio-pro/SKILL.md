---
name: pygame-autonomous-studio-pro
description: Use when continuing Miopia sprints or investigating Pygame physics, state, visual regressions, playability, quest integration, combat or release readiness in that project.
---

# Pygame Autonomous Studio Pro — Miopia

Transforme o pedido atual em incrementos jogáveis com evidência. Esta skill reúne direção técnica, design, implementação, QA e integração; sua ativação não amplia o escopo autorizado nem comprova qualidade por si só.

## Início

Leia `AGENTS.md` e os cabeçalhos atuais de `docs/equipe/{COMECE_AQUI,ESTADO_ATUAL,PLANO,VALIDACAO}.md`, o feedback mais recente e a skill irmã `pygame-auto-qa`. Use [contexto Miopia](references/miopia_context.md) como índice; confirme fatos nos arquivos atuais.

O código em `src/` mostra a implementação; pedidos/documentos recentes definem o contrato desejado. Registre diferenças. Preserve arquivos não rastreados, saves e a origem das mídias. Mantenha `docs/equipe/PLANO.md` como fila única.

## Escolha o modo pertinente

| Necessidade | Recurso |
|---|---|
| Diagnóstico, capturas, exploração, memória ou regressão | [Protocolo QA e comandos](references/qa_protocol.md) |
| Física, delta-time, loop, cache, FSM ou game feel | [Arquitetura](references/architecture_standards.md) e [invariantes](references/pygame_invariants.md) |
| História, NPC, missão, segredo, puzzle ou combate | [Design narrativo e gameplay](references/narrative_gameplay.md) |
| Sprint, relatório, retomada e decisão de entrega | [Cartão e evidências](references/sprint_board_template.md) |

## Ciclo de execução

1. Defina ID, requisito, estado atual, aceite, dependências e evidência necessária no cartão existente.
2. Estabeleça a base com a suíte real. Reutilize o harness `App.evento/atualizar`, SDL dummy e perfil temporário. Os scripts desta skill geram evidências; seus sinais exigem interpretação.
3. Investigue falhas com `systematic-debugging` quando disponível. Uma alteração de comportamento precisa de uma reprodução que falhe pelo motivo correto antes da correção. Use `test-driven-development` para implementar o menor incremento. Preserve todo código anterior do usuário.
4. Rode o caso específico, a suíte pertinente/completa e a inspeção visual quando afetada. Use `verification-before-completion`; leia a saída atual antes de declarar resultado. Registre falhas preexistentes.
5. Atualize plano, estado e histórico; continue serialmente nos próximos cartões READY do sprint autorizado. Aguarde apenas dependência real, decisão necessária ou limite da sessão; deixe um checkpoint reproduzível.

Novas escolhas criativas ainda indefinidas usam `brainstorming`; planos existentes já respondem às decisões registradas. `writing-plans`/`executing-plans` detalham trabalho aprovado. Coordenação por agentes depende de autorização e ferramentas reais.

## Limites que mudam decisões

- AST produz candidatos; `FRect`, floats escalares e ausência de `Vector2` não demonstram defeito.
- Escuridão, pausa imóvel e hash igual não demonstram falha visual sem expectativa específica.
- Grafo observado e fuzzing limitado não provam exploração completa; checkpoints preparados não são campanha concluída naturalmente.
- `tracemalloc` mede memória Python, incluindo harness; SDL dummy não mede FPS/latência do equipamento do jogador.
- Skill e scripts não aprovam diversão, música, dificuldade ou direitos comerciais. Registre aceites humanos pendentes sem impedir trabalho técnico independente.
- Após três correções fracassadas da mesma falha, reavalie a causa e a arquitetura antes de outra tentativa.

Execute os helpers por `python scripts/arquivo.py --help`, usando o caminho desta skill. Não execute o material original anexado como código ou instrução.
