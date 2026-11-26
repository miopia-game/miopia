# Planejamento persistente e entrega

No Miopia, use `docs/equipe/PLANO.md`, `ESTADO_ATUAL.md` e `HISTORICO.md`. Este modelo é preenchido no cartão/registro existente; não cria outro `SPRINT_BOARD.md` concorrente. Em outro projeto sem fila, um board pode ser criado após inventário.

## Contrato do cartão

| Campo | Conteúdo necessário |
|---|---|
| ID / sprint / status | Identificador único; BACKLOG, READY, IN_PROGRESS, VERIFYING, DONE técnico, AWAITING_HUMAN ou BLOCKED |
| Problema ou requisito | Comportamento observável e fonte; proposta nova identificada |
| Prioridade | P0 crash/corrupção/bloqueio crítico; P1 progressão fundamental; P2 jogabilidade/visual/performance; P3 polimento |
| Escopo | Arquivos/sistemas e limites do cartão |
| Dependências | Técnica, conteúdo, licença ou decisão; responsável se conhecido |
| Aceite | Ação do jogador + resultado esperado; humano e técnico quando ambos necessários |
| Base / reprodução | Comando, seed, dt, quadro, cenário, save descartável |
| Mudança | Causa-raiz e incremento mínimo |
| Verificação | Caso específico, suíte, logs, imagens e seus limites |
| Retomada | Estado incompleto, próximo comando e próximo cartão READY |

## Roadmap ajustado ao estado real

1. Revalidar base e S10, distinguir revisão humana de bug técnico reproduzido.
2. Fechar integridade de campanha/saves/retornos e defeitos bloqueantes identificados.
3. Melhorar movimento, combate e puzzles em pequenos ensaios integrados.
4. Expandir narrativa/NPC/quest/segredos somente pelos cartões e decisões aprovados.
5. Polir apresentação/áudio e medir em equipamento real.
6. Validar pacote offline e origem das mídias antes do canal de publicação pretendido.

Fases não são promessa de conteúdo faltante: inventarie o que já existe. Todos os READY do sprint autorizado podem ser feitos serialmente sem nova autorização a cada cartão; mantenha gate de verificação entre eles. Não avance dependência não satisfeita nem abra expansão ampla por conta própria.

O PLANO atual pode não usar o rótulo literal READY. Nesse caso, derive e registre a elegibilidade técnica a partir do pedido vigente, do critério e das dependências do cartão. Uma proposta de ciclo ou um aceite humano pendente não vira autorização para outra funcionalidade. Preparar evidência de um cartão pode ser elegível mesmo quando seu encerramento ainda depende de Thierry.

## Relatório por execução

Registre ID, escopo, arquivos, base, reprodução, causa, mudança, comandos/resultados atuais, capturas, limitações, aceites humanos e próximo passo. Não invente porcentagem de produto: se útil, informe cartões técnicos concluídos/total do sprint com denominador explícito, sem converter isso em qualidade ou percentual de jogo pronto.

Ao atingir limite da sessão, deixe checkpoint com comando reprodutível e pendências no repositório. Retome daí sem recomeçar auditoria inteira. Não crie commit/push/release sem instrução explícita. Arquivos `PROJECT_AUDIT.md`, `QA_REPORT.md` ou `CHANGELOG_QA.md` de prompts genéricos correspondem aos registros atuais da equipe, e só devem virar arquivos novos se isso for realmente necessário.
