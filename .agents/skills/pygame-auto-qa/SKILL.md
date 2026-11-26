---
name: pygame-auto-qa
description: Executa QA headless de Miopia ou jogos Pygame ao investigar física, controles, estados, entidades e regressões de gameplay, com pytest e eventos SDL reais.
---

# QA headless de Pygame

Leia AGENTS.md e os contratos atuais em docs/equipe antes de editar. No Miopia,
rode `./qa.sh tests/auto_qa -v --tb=short` para os bots e `./qa.sh` para a
regressão. Dependências de desenvolvimento: requirements-dev.txt. O jogo
normal continua usando apenas requirements.txt.

Defina SDL_VIDEODRIVER=dummy e SDL_AUDIODRIVER=dummy antes de importar pygame.
Sempre use MIOPIA_DADOS temporário ou App(temporaria=True). Não use perfil real.
Não modifique distribuições geradas: fontes oficiais estão em src/.

- Use App.evento/atualizar e a fila pygame.event.post/get, sem clock.tick ou
  espera de tempo real. Eventos sintéticos não mudam key.get_pressed: mantenha
  um teclado virtual KEYDOWN/KEYUP e passe-o a App.atualizar(presso=...).
- Cubra estabilidade prolongada (3.000 quadros), controles simultâneos com
  semente reproduzível (1.000+ quadros), colisões rápidas e dt até 0,15,
  morte/reinício/troca de região e limpeza de projéteis/entidades.
- Meça os limites reais do mundo, não apenas os 960×540 da janela. Cordas e
  elevadores têm travessia dirigida: diferencie esse contrato de penetração.
  O passo público Jornada.update subdivide a física; teste picos por ele.
- Injete entrada pelo fluxo real. Fixtures podem preparar um checkpoint ou
  geometria para isolar um contrato; não substitua combate/vitória por flags
  quando o próprio percurso for o comportamento avaliado.
- Carregue recursos reais. Não silencie falha de asset ou substitua por mock
  para deixar o teste passar. Mocks cabem apenas em um teste específico de
  recuperação de uma falha intencional, identificado como tal.

Registre a semente, quadro, estado, posição e entrada ao falhar. Reproduza a
causa, corrija o jogo e rode a regressão afetada. Não enfraqueça uma asserção
para acomodar defeito; atualize contrato somente quando o usuário mudar a regra.
Se persistir bloqueio de ambiente, relate a evidência em vez de prometer verde.

Finalize com bugs encontrados, causa e correção, arquivo/linha, comandos e
resultado efetivo. Use o tempo medido: não prometa 0,5 s nem todos os bugs
eliminados. Renderize e inspecione capturas para mudanças visuais. Testes
headless não aprovam sensação de combate, didática, música ou arte pelo jogador.
