# Arquitetura e sensação de jogo

O Miopia já expõe `App.evento`, `App.atualizar(dt,presso=...)`, `App.desenhar` e `Jornada.update(dt,cmd)`. Seu loop não precisa ser reescrito para habilitar QA. Em outro projeto, só isole um loop que realmente execute no import e bloqueie o harness; preserve a entrada normal e o guard `if __name__ == '__main__'`.

## Física e tempo

Preserve a representação atual de posição subpixel (`FRect`, floats escalares ou Vector2 são opções). `pygame.Rect` inteiro pode truncar deltas pequenos; prove a assimetria com movimento repetido antes de trocar a representação. Não imponha Vector2 a toda entidade.

A Jornada já limita dt e subdivide a física; estude esse contrato antes de modificar o tratamento de lag. Clampar indiscriminadamente em 0,05 pode descartar tempo e mudar recursos/ataques. Compare normal, baixa taxa de quadros e pico pelo método público. Resolução por eixos é uma técnica possível, não substituição obrigatória de colisões que já funcionam. Examine quinas, teto, descida seletiva, corda/elevador, parede fina e queda terminal.

## Entrada e estados

Eventos sintéticos não atualizam `pygame.key.get_pressed`. Mantenha teclado virtual e passe `presso` à App. Bordas de ataque/interação devem ser consumidas uma vez, mesmo com substeps. Pausa, perda de foco, conversa, morte e retorno devem limpar comandos/timers conforme o contrato. Reutilize estados existentes; não imponha uma nova FSM com enter/exit se a App já cobre as transições.

## Cache e ciclo de vida

Assets normais devem carregar de arquivos reais. Inspecione caches antes de acusar chamadas indiretas de I/O por frame. Partículas, vestígios, projéteis e áudio precisam de fim de vida/limites; `.kill()` só se aplica a SpriteGroups, listas comuns exigem remoção correspondente. Não exigir contagem constante enquanto há spawns legítimos.

## Game feel

Audite o que já existe: tolerância de borda, fila de entrada, pulo variável, pausa de impacto, recuo, invulnerabilidade, antecipação de câmera e feedback sonoro. Compare cada ajuste em ensaio isolado e no percurso normal. Os 0,10 s de coyote, 0,12 s de buffer ou redução de velocidade por 0,5 do anexo são hipóteses de design; não valores impostos. Hitstop, shake e partículas devem preservar leitura, controle, performance e opção de reduzir efeitos quando aplicável. Não adicionar todos de novo apenas porque aparecem numa checklist.

## Distribuição

Mantenha runtime pygame-ce separado de ferramentas dev. Nenhum download obrigatório no primeiro clique do pacote offline. Salve fora da instalação, preserve migrações e confira a extração limpa. Não prometa Windows/macOS sem build e execução nesses sistemas. Preserve pacote anterior e avisos de runtime; gere cópias pelo fluxo do integrador, nunca editando o pacote extraído como fonte.
