# Miopia — entrada para agentes de programação

Leia `docs/equipe/COMECE_AQUI.md`, `docs/equipe/ESTADO_ATUAL.md`,
`docs/equipe/PLANO.md` e `docs/equipe/VALIDACAO.md` antes de editar.
O feedback mais recente está em `docs/equipe/FEEDBACK_2026-11-12.md`.
Esses documentos atualizam os relatórios históricos S00–S02 e as planilhas.
Para os próximos cartões, leia também `.agents/skills/pygame-autonomous-studio-pro/SKILL.md`,
a rotina irmã `pygame-auto-qa` e `docs/equipe/PROMPT_STUDIO.md`. O escopo e os
aceites continuam no PLANO; os helpers não encerram revisão humana.

Trabalhe em um cartão pequeno de cada vez. Registre o ID, arquivos afetados,
critério de aceite, resultado dos testes e o que depende de Thierry.
Não marque avaliação humana como aprovada sem o parecer dele.
Não transforme referências a Hollow Knight/Cuphead/Sekiro em cópia de mídia,
personagens ou composição. Registre a origem/licença de cada recurso novo.
Os materiais herdados ainda têm pendências comerciais em `docs/s00-origens.md`.

Código em `src/` é a fonte oficial. `distribuicao/` e `colaboracao/` são entregas.
Não edite cópias geradas. Não escreva no perfil real do jogador durante testes.
Use `MIOPIA_DADOS` em uma pasta temporária e SDL dummy para automação.
Dependência de execução: `pygame-ce==2.5.8`. NumPy só é necessário para
regenerar o áudio antigo; o jogo e o gerador de temas novos não exigem NumPy.

Antes de entregar, rode o teste específico e a regressão pertinente, confira
entrada normal pela App, save antigo, morte/retorno e aparência na resolução
960×540 quando afetados. Mudanças nas regras invalidam replays estritos antigos.
Guarde a versão anterior ao atualizar um pacote. Não declare qualidade da
experiência comprovada apenas porque os testes passaram.

Se várias pessoas trabalharem simultaneamente, atribuam arquivos distintos e
combinem os contratos antes das edições. Façam branches `codex/ID-assunto` ou
`claude/ID-assunto`. Só o integrador atualiza a distribuição.
