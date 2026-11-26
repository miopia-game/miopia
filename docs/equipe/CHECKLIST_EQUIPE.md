# Miopia S40 — checklist para a equipe

Os itens marcados têm implementação na edição compartilhada. O [histórico](HISTORICO.md) liga cada mudança ao sprint que a introduziu. Para conferir o comportamento em jogo, use **História** e **Campo de testes** na mesma pasta extraída.

## O que existe e como funciona

| Estado | Área | Implementação e verificação |
|---|---|---|
| ✓ | Campanha e desfecho | Quatro travessias ligam as raízes, a volta da água e o Último Chamado. `roteiro.py`, `narrativa.py`, `travessia.py` e `ultimo_chamado.py`. O percurso do prólogo ao pós-jogo é exercitado em `test_s31_historia.py`. |
| ✓ | Verticalidade | Salto duplo, salto entre paredes, planagem enquanto se segura o salto na queda, descida por grades e trilhas com cipós, câmaras e passarelas físicas. `travessia.py`, `corte_vertical.py`, `subsolo.py`, `galeria_taquaral.py`. Ver [S37](S37.md) e o ensaio **O sino soterrado**. |
| ✓ | Tutorial e orientação | Lições automáticas por contexto, confirmação da prática, avisos curtos no canto, objetivo e pista no topo do mapa. `tutorial.py`, `avisos.py`, `orientacao.py`. Ver [S22](S22.md) e iniciar uma História em perfil novo. |
| ✓ | Exploração e mapa | M/Tab abre o diário. Há descoberta por visão, trechos marcados por pisadas na Gruta, ampliação, movimento, marcadores e rastreio de pedidos conhecidos. `descoberta.py`, `cartografia.py`, `mapa_visor.py`, `missoes.py`. |
| ✓ | Luz e recursos | Vida e brilho independentes. Clarão e cortes de luz custam brilho e podem recorrer à vida. Abates devolvem parte dos recursos, e sequências sem dano aumentam o retorno de brilho. Globos e tochas persistem. `travessia.py`, `visao.py`, `luzes_mundo.py`. Ver [S08](S08.md). |
| ✓ | Armas e itens | Corte rápido, pesado, descendente, avanço, combos e versões carregadas. Espinho e Agulha após o pedido de Mimo. Pólen, pavio, bálsamo, seda e melhorias com usos e durações próprias. `combate.py`, `taticas.py`, `ferramentas.py`. Compare **Nicho dos Berços** e **Patrulha em dupla** em [S38](S38.md). |
| ✓ | Encontros e chefes | Perfis de ataque por espécie, seleção contextual, patrulhas com flanco e cobertura, brechas visuais, quatro guardiões e mini-chefes. A Tecelã chama crias. `encontros.py`, `taticas.py`, `chefes.py`, `nicho_taquaral.py`. Ver [S32](S32.md), [S34](S34.md) e [S38](S38.md). |
| ✓ | NPCs e consequências | Pedidos opcionais, três resgates e trabalhos que mudam iluminação, recompensas e atalhos. Restaurações liberam travessias revisitáveis e conversas novas. `resgates.py`, `jardim.py`, `rotas_borda.py`. Ver [S33](S33.md) e [S39](S39.md). |
| ✓ | Save e tentativas | SQLite por perfil. Quedas e morte têm retornos distintos. A volta voluntária conserva os recursos atuais. Inimigos vivos recompõem a tentativa após a morte. Vitória e pós-jogo são gravados juntos. `memoria.py`, `travessia.py`, `main.py`. Ver [S36](S36.md). |
| ✓ | Áudio e arenas | Temas por guardião, ambiências, avisos por ataque e controles de volume. `audio.py`, `assets/sons/`. O Campo de testes tem 30 entradas. Ver [S11](S11.md) e [procedência do áudio](../audio.md). |
| ✓ | Controles e leitura | Quinze ações de teclado remapeáveis, entrada de controle SDL, tamanho do texto, alto contraste e clarões suaves. `controles.py`, `memoria.py`, `ilustracao.py`, `telas.py`. Ver [S40](S40.md). |

## Próximos cartões

- [ ] **S41 · Terreno e animação.** Escolher um bioma, comparar o piso visível com a colisão e corrigir uma emenda comprovada. Depois conferir as poses de preparação, impacto e recuperação de um combate.
- [ ] **S41 · Mixagem.** Medir e ouvir música, floresta e efeitos num encontro. Comparar volume relativo, distância e separação entre presença, preparação e impacto. Deixar uma cena e um trecho de áudio reproduzíveis para a revisão.
- [ ] **S42 · Desempenho em aparelho real.** Medir quadros com janela e áudio no notebook. Reproduzir o clarão, abrir o mapa e trocar de região. Anotar picos por ação e repetir a mesma cena após corrigir a causa.
- [ ] **S43 · Windows offline.** Preparar o executável para uma instalação limpa. Testar abertura, primeira partida e retomada sem Python pré-instalado, em uma máquina Windows.
- [ ] **S43 · Origens e distribuição.** Registrar as licenças do pacote, revisar materiais herdados em `docs/s00-origens.md` com a equipe e definir o conteúdo de eventual repositório público. Preservar o ZIP acadêmico histórico.
- [ ] **Avaliação humana.** Testar um controle físico com o S40. Registrar modelo, sistema, como o rótulo de botão aparece e o comportamento ao reconectar. Em jogo, colher parecer sobre leitura das rotas de primeira visita, dificuldade dos chefes, mixagem e clarão suave.

O [plano](PLANO.md) é a referência para assumir cartões. A [pesquisa complementar](PESQUISA_EQUIPE.md) reúne hipóteses fora dessa fila. Entregue evidência e arquivos do cartão ao integrador, que prepara as distribuições.
