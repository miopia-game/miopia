# História, NPCs, missões, segredos, puzzles e combate

Use `docs/continuidade.md`, cabeçalhos atuais da equipe e os módulos existentes como base. Este arquivo oferece critérios e fichas; nenhum exemplo de campo vazio é conteúdo canônico.

## Continuidade e quest principal

Conserve protagonista, conflito, quatro biomas, consequências do orvalho e papel trágico da Coruja. A miopia liga percepção e mundo; as ações de restaurar, escutar e reencontrar devem carregar a narrativa. Antes de escrever, mapeie fato conhecido, fonte, quem sabe e quando o jogador pode descobrir. Relatos podem discordar; as regras físicas e a progressão precisam ser consistentes. Dois finais e pós-jogo devem respeitar a implementação atual; não restaurar uma versão histórica por acidente.

Faça um grafo da rota: pré-condição → pista → ação → mecanismo/objeto → consequência → passagem → retorno. A campanha deve contar sua história sem exigir todas as conversas, segredos ou perguntas educativas. O conteúdo ambiental do projeto tem pendências de procedência; reescrita, se autorizada, precisa de autoria e referências verificáveis.

## Ficha de NPC e pedido

Registre ID existente/novo; personagem, motivo e voz; fato que conhece; relação com outra pessoa; ação visível; estados inicial/aceito/em progresso/concluído/retorno; gatilhos; falas curtas; consequência no mundo; recompensa e recibo único; save/migração; saída se ignorado. Reuse Nira, Véspera, Mimo, Casca, Fio, Eco, Risca, Pingo, Brasa, Nó e resgates conforme o código, sem redistribuir seus papéis por conveniência.

Teste aceitar → sair → morrer → retornar → salvar → carregar → concluir → interagir de novo, incluindo entrega fora de ordem e inventário cheio quando aplicável. Registros/objetivos só revelam pistas descobertas. Uma missão secundária precisa de motivo e consequência, não apenas coleta repetida. NPCs funcionam offline com condições/flags; novos serviços de IA em runtime exigem decisão de produto.

## Puzzles e segredos

Ensine o verbo numa área segura, teste a regra e só depois combine com outra. Para válvulas, água, cordas, contrapesos, grades e raízes, alinhe pista, affordance, colisão, resposta sonora/visual e resultado. Objetos críticos reaparecem ou permanecem recuperáveis; save/restart não deixam o jogador sem solução. Evite pista de um único pixel ou exclusivamente sonora/colorida.

Segredos são opcionais, com indícios recuperáveis e retorno físico. Estime o valor da recompensa em relação ao risco e à economia atual. Não bloqueie a quest principal com um segredo sem explicação. Um bot não visitar uma sala não prova que ela seja inalcançável; confronte grafo, pré-requisitos e piloto dirigido.

## Combate e inimigos

Modele percepção → preparação → ataque comprometido → recuperação → reposicionamento. Dê a cada tipo função, aviso, duas respostas possíveis e limite de ataques simultâneos conforme a cena. Mais PV, velocidade ou stun não substituem decisões interessantes. Meça janela de aviso, resposta, tempo para derrotar, dano recebido, brilho gasto/recuperado e punição possível, sem definir números universais.

Preserve as soluções ambientais distintas dos guardiões e os módulos atuais. A ficha de encontro deve registrar motivo narrativo, arena/alturas, pré-requisito, ataques/avisos, estados/fases, vulnerabilidade, progresso, feedback, checkpoint, recuperação de objetos, reset e saída. Coruja é acalmada. A barra vazia por flag de teste não é vitória jogada. Prototipe arma nova em ensaio antes de alterar campanha e economia; C05 continua dependente de avaliação.

## Avaliação da experiência

Capture texto, HUD e ação em 960×540, revise áudio causal sem encobrir avisos e procure pausas/exposição longa que tirem controle sem motivo. IA pode avaliar consistência e formular hipóteses de clareza; aprovação de ritmo, arte, música e dificuldade permanece com o jogador. Reúna a evidência para reduzir o tempo que Thierry precisa dedicar, sem atribuir a ele um parecer não recebido.
