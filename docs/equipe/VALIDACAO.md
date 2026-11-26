# Nitidez do Bosque e voo da fagulha · prévia de 26/11

A gravação usa os comandos da App pela História. O piloto parte do começo do Bosque, lança da borda de Véspera, cruza até o poleiro, vence o primeiro morcego e lança de volta. Foram 1.231 quadros a 60 fps com áudio estéreo do mixer do jogo. O tiro para a direita passou de 23 para 15 atualizações até o pouso e consumiu 26 de brilho nas duas versões. O morcego caiu no quadro 1.009 nas duas gravações. [Vídeo da partida](../midia/bosque-em-jogo.mp4) · [Comparar o disparo e o pouso nas duas versões](../midia/fagulha-antes-e-depois.mp4)

A suíte completa passou em 479 testes e 176 subtestes. O lançador do macOS abriu menu e Bosque. As regressões cobrem voo em ambos os sentidos, colisão com paredes, área iluminada durante o voo, contraste da pintura, câmera vertical, som localizado de contato e alcance das duas marcas opcionais de todas as posições horizontais de partida. [Testes da trajetória](../../tests/test_voo_fagulha.py) · [Testes da pintura e do rastro](../../tests/test_arte_fagulha.py)

# Verificação do acabamento visual

O playtest em SDL Cocoa, 960 × 540, saiu do menu, pousou no primeiro
galho, abriu o diário, ativou o clarão e girou o carretel. No Campo de
testes, venceu a Asa Fendida em mudo. Posição, vida, brilho e progresso
coincidiram com os da execução de referência. O vídeo, as capturas e o
JSON ficam em `playtest-visual-integrado` ao lado da cópia de trabalho.

A suíte completa registrou 426 testes e 176 subcasos aprovados.
Reproduziu as mesmas três falhas do exportador já presentes na base.

# Verificação da cópia de usabilidade sobre a S40

As seis regressões em `tests/test_usabilidade_s40.py` cobrem a dica que
expirava sem prática, o primeiro apoio no escuro, a previsão de custo
do clarão, os avisos da Asa Fendida em mudo, a instrução de acesso
vertical e a água após a restauração do Córrego e a recarga.

No Mac ARM, SDL Cocoa abriu a janela de 960 × 540 e inicializou o
mixer. O piloto da App venceu a Asa Fendida em mudo e percorreu a
História pelas quatro raízes até recarregar o pós-jogo. Um save escrito
pela S40 original foi reaberto com os mesmos 78 de brilho e a lição
pendente voltou a aparecer. Foram inspecionados mapa e aviso de
custo em escala de texto de 125%, com alto contraste.

As capturas e o log da suíte estão na pasta `evidencias` ao lado
desta cópia. A suíte completa registrou 425 testes e 176 subcasos
aprovados. As três falhas já presentes na S40 são casos do exportador
que montam um `ENTREGA.json` inválido. Ritmo, leitura na primeira
visita e aprovação de arte e combate dependem de avaliação humana.

A assinatura estrita de replay nesta cópia é
`4ca03da2fc8af30e4a66b0c2f7cabf9d41dd4c67c2e95d0d44ca9c0f144f8bad`.
Replays da assinatura anterior continuam vinculados à S40 original.

# Verificação dos controles S40

[S40.md](S40.md) registra a navegação pela App, as opções em 960×540,
a campanha e a retomada de perfis S39. Barras, alcance mecânico e
custo do clarão seguem iguais. Controle físico e Windows precisam
de uma sessão nos respectivos aparelhos.

# Verificação das revisitas S39

[S39.md](S39.md) mostra o Bosque e o Córrego antes e depois
da água, os postos de Tila e Bento, a descida, a subida e a
migração de saves S38 com e sem resgates.

# Verificação do combate e consumíveis S38

[S38.md](S38.md) reúne a esquiva, a brecha, as trajetórias de veneno,
a diferença entre as armas e o uso dos itens. Há medidas do duelo
nas duas versões e verificação de dois saves do S37.

# Verificação da Câmara da Escuta S37

[S37.md](S37.md) registra a descida, os apoios, a passarela, as pisadas
e a volta após morrer. Inclui a campanha completa e a continuação de
dois saves gravados pela versão S36.

# Verificação da continuidade da História S36

[S36.md](S36.md) reúne o teste de falha de gravação da vitória, a
volta ao marco com brilho zerado, a morte, a troca de dificuldade
e a recarga de um save produzido no S35.

# Verificação do Nicho dos Berços S35

[S35.md](S35.md) reúne a abertura da tranca, a ida e volta pelo piso,
os disparos da Cobra, a recompensa única, a luz e a recarga.

# Verificação do Último Chamado S34

[S34.md](S34.md) reúne o contato e a esquiva nas faixas, os quatro
totais de aliados, a morte e a recarga, o mapa e as capturas em mudo.

# Verificação dos trabalhos no Jardim S33

[S33.md](S33.md) reúne o teste das escolhas e seus recibos, os três
postos do Jardim, a travessia de ida e volta, a recarga e a morte.

# Verificação das margens e da ninhada S32

[S32.md](S32.md) documenta a ordem livre das pistas, o reencontro,
a comparação do combate, a evacuação das crias em cada tentativa,
o percurso pela História e as cenas em 960×540.

# Verificação da campanha S31

[S31.md](S31.md) documenta as quatro regiões da História percorridas
do menu até o pós-jogo, os desfechos condicionais, a reprise do sino,
as capturas e a retomada do save.

# Verificação da Galeria das Sementes S30

[S30.md](S30.md) reúne percurso, escolha de ataques, reparo, mapa,
save anterior e evidências a 960×540.

# Verificação do beiral S29

[S29.md](S29.md) registra a leitura das sementes, o percurso com
Espaço, o pavio persistente, a rota principal e as capturas em 960×540.

# Verificação da fauna S28

[S28.md](S28.md) registra o ciclo de caça, o desvio pelo alto, os avisos
corporais e a retomada da rotina depois de morrer ou recarregar.

# Verificação do pedido de Fio S27

[S27.md](S27.md) demonstra o percurso pela App, a ordem alternativa,
o rastreio, a recompensa única e o retorno à passarela após recarga.

# Verificação da comporta S26

[S26.md](S26.md) registra o percurso pelo Estaleiro, a colisão durante a
subida da lâmina, a pausa, a abertura persistente e as três capturas.

# Verificação das patrulhas S25

[S25.md](S25.md) registra a chegada à Vigília, o revezamento dos guardas,
os avisos sob o clarão e a retomada após a morte.

# Verificação do casulo S24

[S24.md](S24.md) registra a chegada ao Poço da Seiva pela História, o
rebote, o uso do pavio, a retomada após morte e as capturas em 960×540.

# Verificação da escuta S23

[S23.md](S23.md) registra a descida e a coleta pela App, a busca por um
pouso, obstáculos, retorno ao marco e as capturas em 960×540.

# Verificação do tutorial S22

[S22.md](S22.md) registra as lições no início da História, a confirmação de
ações pela App, a consulta de controles e as capturas em 960×540.

# Verificação da veneziana S21

[S21.md](S21.md) registra cinco ciclos, a saída com janela fechada, a retomada
após morte, a entrega a Véspera e as capturas da janela aberta e fechada.

# Verificação do atalho do S20

[S20.md](S20.md) registra o percurso aos dois andares, o recarregamento no
marco do poço, o retorno após morte e as capturas em 960×540.

# Verificação do ciclo S15–S19

[S19.md](S19.md) registra os cenários de jogo com E e K, a travessia de volta
no Jardim após carregar, a saturação dos canais de áudio, as armas medidas e
a regressão integrada da campanha. As verificações deste ciclo foram locais,
com perfis descartáveis e sem participação manual de Thierry.

# Verificação da escolha de Tila no S14

[S14.md](S14.md) registra as verificações de narrativa, escolha, save e
recompensa única. Os roteiros humanos abaixo ficam como referência histórica.
Thierry dispensou sua participação e pediu continuidade dos sprints.

# Verificação de repetição dos ensaios S13

Veja [S13.md](S13.md) para os casos de repetição pela pausa e de retorno à
lista após a morte. O roteiro da Vigília abaixo usa os atalhos desta versão.

# Verificação de fluidez do mapa S12

Veja [S12.md](S12.md) para a medição de zoom e arrasto, a comparação pixel a
pixel e o roteiro para verificar o comportamento no notebook de Thierry.

# Verificação da revisão acadêmica S11

Abra [S11.md](S11.md) e compare os temas no Campo de testes. Testes e hashes
estão em qa-S11.json e audio-S11.json. A validação técnica do áudio cobre
transições, carregamento, retomada e loop. A verificação humana cobre
preferência, conforto e audibilidade dos sinais na música.

# Validação e roteiro humano

## R10.5 — Asa Fendida na parte alta da arena

O aviso da primeira fase usava o chão como referência. Na segunda,
a altura só subia quando os pés coincidiam com um patamar. A busca
agora acompanha a altura e o aviso fixa a linha de voo com o patamar
ou a posição de Lume no ar. Na regressão, os quatro apoios podem ser
atingidos nas duas fases. Em um alvo no ar, sair da altura anunciada
evita o contato. A colisão na raiz mantém a janela de 3,8 s, que cai
para 2,1 s depois do primeiro crítico.

- Antes da correção, `./qa.sh tests/test_feedback_chefes.py --tb=short`
  reproduziu uma falha pela App e seis falhas em subcasos.
- Depois, o arquivo passou com 6 testes e 15 subcasos em 0,48 s.
  A seleção com chefes, campanha, morte/retorno, compatibilidade de save
  e replay passou com 30 testes e 20 subcasos em 10,80 s.
- `run_qa.py --repo . --out /tmp/miopia-s10.rc3lGJ/r105-suite --timeout 180`
  passou com 265 testes e 176 subcasos em 87,70 s. A base tinha 262 testes
  e 166 subcasos em 88,61 s. Vídeo e áudio em SDL dummy e perfil temporário.
- No ensaio da Asa Fendida pela App, Lume chegou ao patamar superior por
  eventos reais de teclado. Na primeira fase, com os pés em y=322, a
  guardiã anunciou e percorreu a linha y=291. A vida caiu de 81 para 62.
  Capturas de 960×540 inspecionadas em `work/studio/R10.5/`.

Para revisar jogando, abra **Campo de testes → Asa Fendida**. Suba pelo
patamar da entrada até o patamar seguinte, observe a linha de voo e
mude de altura quando ela avisar. Perto da raiz riscada, atraia a
investida e confira a abertura para J. A leitura, a cadência e a
dificuldade aguardam o parecer de Thierry.

## R10.4 — besouro e abrigo inicial

**Aceite técnico.** O carabídeo anuncia o salto, trava o alvo e acerta Lume
acima se ele permanecer ao alcance. Sólidos bloqueiam o arco e sair da
trajetória evita o dano. Na abertura da História, E junto à cama usa a
reserva quando Lume precisa. E perto de Mimo abre a conversa.

O besouro usava carga, ondas ou o arco curto, que deixavam alvos mais altos
fora de alcance. O salto alto reaproveita o aviso da quinta família e usa
o mesmo arco para validar o espaço e para mover a criatura. Vale para a
IA de patrulha, inclusive o Caruncho, e para o carabídeo do Jardim. A cama
ocupava parte da mesma faixa de Mimo. Seu eixo no Bosque passou de 114
para 70, com Mimo em 163. IDs, campos do save e regras da reserva foram
preservados. A assinatura de replay estrito mudou com os fontes.

### Verificação no Fedora

- Suíte antes da alteração com 256 testes e 166 subcasos em 91,26 s.
- `./qa.sh tests/test_r10_4.py --tb=short` reproduziu seis falhas antes
  da correção. A regressão focada depois da mudança passou com 43 testes
  e 41 subcasos em 19,32 s. Incluiu campanha, combos, geometria de ataque,
  retorno, save antigo, finitude da reserva e replays recém-gravados.
- `./qa.sh --tb=short` passou com 262 testes e 166 subcasos em 91,72 s.
  O SDL dummy emitiu 62 avisos de renderer.
- A App foi aberta pelo menu com eventos pygame, SDL dummy e
  `MIOPIA_DADOS` temporário. Foram inspecionadas capturas de 960×540 em
  `work/studio/R10.4/`. No ensaio de pulo entre paredes, Lume foi
  posicionado na grade real do ramal do Bosque para isolar o ataque.
  Houve aviso no quadro 8 e impacto no quadro 55, com vida de 100 para 81.

Para a revisão humana, comece uma História e confira o aviso de E junto
à cama. Vá à direita e confira a troca para “Ouvir Mimo”. No Campo de
testes, aproxime-se da Sentinela do Taquaral e experimente saltar sobre
ela e sair da mira após o aviso. Clareza do aviso e cadência dependem
de Thierry.

## R10.2 — combate na Clareira da Vigília

**Estado em 16/11/2026.** Preparação técnica concluída. O aceite precisa
de duas tentativas de Thierry antes de decidir valores de J/L/Ctrl e retorno
de brilho. R10.1, R10.3, C05 e A02 mantêm seus próprios pareceres.

### Roteiro para Thierry

1. Em **Ajustes**, use dificuldade **Normal** e mantenha música e efeitos
   iguais nas duas tentativas. Abra **Campo de testes → Clareira da Vigília**.
   **D + Espaço** no começo atravessa a abertura do piso.
2. Na primeira tentativa, alterne **J** e **L**. Na segunda, volte à mesma
   cena e combine os golpes com **Ctrl**. Use movimento e esquiva nas duas.
   Para comparar o custo desses golpes, deixe K e o bálsamo de fora.
3. A partir da entrada, cronometre até derrotar os três guardas ou até a
   primeira morte. Registre os guardas vencidos se encerrar antes. Anote
   o primeiro aviso visual ou sonoro que percebeu e a reação que tentou.
   Se for mais fácil, grave a tela para conferir quedas e recuperações das barras.
4. Entre as tentativas, use **Repetir o ensaio** na tela de morte. Com Lume
   vivo, pressione **Esc → Repetir o ensaio** e confirme. **R** na pausa abre
   a mesma confirmação. A nova tentativa repõe os guardas e os recursos.
5. Registre dano recebido e vida usada pelas habilidades em campos distintos.
   Para o brilho, some as quedas causadas pelos golpes e anote as recuperações
   quando identificáveis. O saldo final também é útil. Marque como estimado
   qualquer valor de que tenha apenas uma leitura aproximada.

| Tentativa | Primeiro aviso (visual/sonoro, origem e reação) | Tempo e resultado | Dano dos guardas | Brilho gasto/recuperado/final | Vida usada por falta de brilho |
|---|---|---|---|---|---|
| J/L | Pendente | Pendente | Pendente | Pendente | Pendente |
| Ctrl+J/L | Pendente | Pendente | Pendente | Pendente | Pendente |

### Evidência técnica no Fedora

As duas sequências automatizadas entraram pelo menu real, dificuldade Normal,
por eventos pygame. A entrada segurou D por 34 quadros e Espaço pelos primeiros
24. A partir do quadro 34, alternou J/L a cada 21 quadros com passo solicitado de
1/60 s. A segunda sequência acrescentou Ctrl a cada toque. O limite foi 480
quadros, com parada antecipada em morte ou vitória sobre os três guardas.
A primeira emissão foi `aviso_morcego_1` aos 0,133 s do relógio da App nas duas
sequências. A captura mostra Lume, o morcego e a mira no quadro da emissão.

| Entradas | Tempo da App (tempo da Jornada) | Resultado | Dano dos guardas | Brilho gasto | Brilho recuperado por acerto/abate | Vida usada por falta de brilho |
|---|---|---|---:|---:|---:|---:|
| J/L | 8,000 s (7,667 s) | Limite, 5 de vida e nenhum guarda abatido | 95 | 0 | 0 / 0 | 0 |
| Ctrl+J/L | 6,233 s (5,933 s) | Morte com um guarda abatido | 74,4 | 101,4 | 1,8375 / 8 | 28,6 |

O gasto é acumulado e pode superar a barra inicial quando há recuperação no
percurso. Os tempos são da simulação e incluem as diferenças causadas pelas
pausas de impacto. São percursos curtos de entradas fixas. A percepção dos
avisos e a decisão de balanceamento seguem pendentes de teste humano.

Comandos executados com CPython 3.14.10, pygame-ce 2.5.8 e, para a suíte,
pytest 9.2.0 instalado em ambiente temporário. Todos os ensaios usaram SDL
dummy, perfil temporário e, na sonda da Vigília, SQLite em memória.

- `python -B .agents/skills/pygame-autonomous-studio-pro/scripts/run_qa.py --repo . --out /tmp/miopia-s10.rc3lGJ/suite --timeout 180` passou com 256 testes e 166 subcasos em 89,47 s, com 60 avisos de renderer do SDL dummy.
- `./qa.sh tests/test_s08.py tests/test_s10.py tests/test_campanha.py` passou com 45 testes em 11,78 s, com 24 avisos do mesmo renderer. Inclui campanha, migração de save, morte/retorno, combos, coordenação da patrulha e mapa/avisos S10.
- `python -B -m unittest discover -s .agents/skills/pygame-autonomous-studio-pro/tests -v` passou com 9 testes. O auditor AST da Pro retornou zero candidatos nas heurísticas verificadas.
- `./Miopia --smoke` abriu menu e Bosque com o runtime incluído. O capturador Pro gerou menu e Vigília, e a medição abaixo gerou os quadros de aviso e desfecho inspecionados em 960×540.
- `PYTHONPATH=. python -B work/studio/R10.2/medir_vigilia.py` reproduziu os resultados e conferiu a reabertura com Lume e guardas restaurados. O roteiro automatizado usa o menu, teclado virtual e os métodos reais do jogo.

Script, resumos, eventos por quadro, capturas e log do executor ficam
localmente em `work/studio/R10.2/`. Os arquivos desta preparação de cartão
são PLANO.md, ESTADO_ATUAL.md, HISTORICO.md e VALIDACAO.md. A verificação
compara `src/`, mídia, runtime, skills, testes e ZIP com a extração original.

## Entrega S10

256 testes/166 subcasos na fonte, incluindo 16 testes novos de avisos/mapa/
grade. Nove testes dos helpers e M nos 26 ensaios. Extração/runtime e hashes
registrados no ENTREGA.json da entrega; os resultados locais estão em
qa-S10.json. Somente perfis temporários e SDL dummy.

1. Campo de testes → Clareira da Vigília: leia a quinta linha, que explica
   acender a clareira. O painel deve caber no canto e evitar Lume.
2. Espere o aviso desaparecer e abra M: cabeçalho identifica o ensaio e a
   pista continua completa. Na História, M continua com sua missão normal.
3. Compare o tutorial antes da primeira grade e S+Espaço para descer. Suba
   pelos galhos; câmera e física não foram rebalanceadas.

Capturas s10_*.png inspecionadas em 960×540. Qualidade da leitura, tempo e
conforto da câmera continuam para avaliação de Thierry. Sem novo aceite de
combate, arte, música ou direitos. Replays S09 não foram invalidados.

## Integração de ferramentas Q10.0

Base atual confirmada: 238 testes. Após integrar a Pro e acrescentar regressões
dos exportadores: 240 testes e 166 subcasos passaram pelo executor novo.
Os 9 testes dos helpers também passaram separadamente. Detalhes e comandos
em Q10.0-studio.md e STUDIO_VALIDACAO.json. A build jogável S09 permanece
inalterada, com seu relatório histórico de 238 testes. Pacotes não foram
regerados neste cartão. Avaliações humanas continuam pendentes.

## Entrega atual S09

238 testes e 166 subcasos na fonte; 26 ensaios mantidos. Relatório em S09.md
e qa-S09.json. `./qa.sh` roda toda a suíte com perfil descartável e SDL dummy,
incluindo `tests/auto_qa`. Instale requirements-dev.txt para desenvolver.
Não escrever no perfil pessoal. Infinito retirado; saves de História antigos
e recordes legados preservados. Replays estritos precisam ser novos (S09).
O resultado da extração com runtime e hashes consta de ENTREGA.json da equipe.

Roteiro de revisão S09:

1. Nova História: tutorial durante a partida, no canto; sem objetivo em faixa
   inferior. Aproxime Lume do canto direito: o cartão deve mudar para a esquerda.
2. M abre mapa: missão centralizada no alto; terreno conhecido abaixo. Feche
   com M e confirme que a partida não ganha uma instrução contínua.
3. Raízes do Bosque/Córrego: aproxime da grade. Folhas e sinais apontam para
   baixo e a câmera mostra mais espaço inferior. Desça e retorne pelos galhos.
   A sala distante não deve aparecer no mapa só por mudar a câmera.
4. Continue um save anterior, morra e retorne. Mobs vivos voltam inteiros;
   derrotados continuam derrotados. A História termina sem iniciar outra volta.

Capturas s09_*.png inspecionadas em 960×540. Bots: 3.000 quadros estáveis,
3 × 1.100 de controles simultâneos, colisão de um pixel, dt até 0,15 s,
cinco ciclos de morte/reinício/troca de bioma. Não medem sensação, dificuldade,
audição ou FPS real. Nenhum desses aceites humanos foi marcado como aprovado.


## Histórico da entrega S08

213 testes da fonte, incluindo 28 novos em test_s08; 26 ensaios abertos e
desenhados pela App. A extração final passa novamente pela suíte, launcher e
replay estrito S08. ENTREGA.json registra o resultado efetivo/hash do pacote.
Todos os perfis de teste são temporários; o perfil real não é escrito.

Testes antigos que esperavam dreno passivo, dano na barra de luz, ausência de
L/Ctrl ou oclusão por paredes foram atualizados pelos pedidos explícitos desta
rodada. Asserções de morte continuam usando vida, inclusive queda, sacrifício,
Game Over e retorno ao checkpoint. O piloto da campanha passa a usar bálsamos
pela vida e as reservas finitas dos abrigos de cada bioma; não recebe cura falsa.

Roteiro curto:

1. Nova História: ande, salte, atravesse o primeiro trecho. Dicas devem aparecer
   durante a partida; não há botão obrigatório para abrir tutorial. Veja se o
   aviso chega antes do obstáculo e se dá tempo de ler. Itens novos têm dicas.
2. K alcança 520 px e passa por paredes/plataformas. Sem K/Ctrl, brilho deve
   permanecer estável. Zere brilho: halo apaga, Lume vive. K agora usa vida;
   usar a última vida mata e a tela explica o sacrifício.
3. Campo de testes → Combos da colônia: J/J/J, J/L/J, K/L e Ctrl+J/L. Compare
   animação, alcance, custo e um acerto por alvo/arco. Acertos devolvem brilho;
   sequência cresce até 8×, dano/queda zera. Abates comuns +3 vida/+8 brilho.
4. Clareira da Vigília: três guardas, flancos e cobertura. Observe avisos
   escalonados. Depois de vencer, E no núcleo e E na tocha. Q/F usa o globo
   em outro local. A região da tocha fica nítida; K nela não cega os mobs.
5. Globos e tochas abre o resultado do mini-chefe no berçário inferior. Coloque
   um globo, morra, volte e confira a luz. Na História, saia/carregue e confira
   novamente. A reserva não depende de inimigos continuarem derrotados.
6. Raízes do Córrego: compare as novas faces verticais com s08_corrego.png e
   s08_corrego_clarao.png. A luz não deve mais recortar as paredes em blocos.
7. M: +/− ou roda amplia; arrasto/WASD move; C centraliza; direito marca/remove;
   V muda tipo. A navegação não revela terreno. Confira a consulta do Corte
   quando Lume está na superfície. Marcações persistem e ensaios não gravam
   na campanha. Vitória/Jardim concluídos aparecem com objetivos coerentes.
8. Machuque/desloque um mob e morra: vivo deve voltar inteiro ao ponto inicial;
   derrotado permanece derrotado. Repita perdendo a última fagulha.

Capturas conferidas em 960×540: s08_tutorial, s08_corrego, s08_corrego_clarao,
s08_mapa, s08_mapa_geral, s08_clareira, s08_globo e s08_golpe_luz (capturas/).
Não se presume aprovação humana de dificuldade, arte, didática ou músicas.

Desempenho local, sem testes simultâneos: desempenho-S08-cenas.json e
desempenho-S08-mapa.json. Jardim: simulação mediana 0,549 ms, desenho 2,473 ms;
clareira: 0,489/2,851 ms. Mesmo mapa parcial: redesenho mediano 18,304 ms;
cache 0,077 ms. No mapa completo, cache mediano 0,506 ms. SDL dummy não mede
FPS real nem latência do monitor/áudio; comparar no notebook antes de aprovar.

## Histórico da entrega S07

185 testes na suíte completa da fonte, incluindo os 14 novos de test_s07;
23 ensaios abertos e desenhados pela App com perfil temporário. As alterações
posteriores de apresentação/fixtures também passam pela verificação específica
e pela suíte completa dentro do pacote final. ENTREGA.json registra o resultado
efetivo, hash e quantidade de testes da instalação conferida.

Capturas de 960×540: capturas/s07_resgate.png, s07_jardim.png,
s07_ultimo_chamado.png, s07_retorno.png e s07_final.png. Conferidas visualmente:
escolhas e textos cabem na janela e os dois botões finais continuam acessíveis.
Perfil real não é usado. Replays estritos anteriores são incompatíveis com as
regras S07; um replay novo deve ser gravado e verificado pela CLI da extração.

Medição local: desempenho-S07.json, 180 quadros/cena após 20 de aquecimento,
SDL dummy, sem testes simultâneos. No Jardim, mediana da simulação 1,529 ms e
desenho 10,226 ms; p95 do desenho 17,012 ms. No retorno, desenho mediano
11,234 ms e máximo 24,189 ms. Não equivalem a FPS real, tempo total de quadro
ou garantia para o notebook; o monitor, áudio e outros processos não estão
cobertos. Criaturas novas distantes dormem; projéteis ativos continuam.

Roteiro humano S07:

1. Resgate no berçário: E conversa; escolha trilha ou mantimento. Esc deve
   adiar, sem escolher. Na História, volte ao Bosque e confira a consequência.
2. Jardim do Último Sinal: suba à copa pelo apoio antes da raiz alta, pegue
   orvalho e mova o contrapeso a leste. Afaste o vigia das sementes. S+Espaço
   na grade da estufa desce às calhas; no vão baixo, agache/deslize à esquerda.
   Solte o tampão, desça e plante. Anote tempo, primeira confusão e retornos.
   Lente e carta são opcionais; os cipós do fundo retornam mesmo sem concluir.
3. Último chamado: recolha uma gota com E e use K junto ao ninho marcado.
   Atravesse a arena para o próximo; pule o rasante. Diga se ouviu e entendeu
   a troca de fase. A sequência pode ser terminada sem resgatados.
4. Floresta reacesa: compare as luzes das trilhas e o mapa por visão; observe
   se perdeu definição demais ou se algo foi revelado sem ver.
5. Escuta dos ataques: J troca família, K espécie, E reproduz. Depois compare
   com Patrulha em dupla. Anote nomes que se confundem, irritação e volume.

Na campanha, restaurar raiz não deve abrir pergunta. C abre o caderno por
escolha e as setas revisitam raízes anteriores. Depois da vitória, escolha
Explorar a floresta, saia e continue o save. Resgates, trabalhos, recompensas
e Jardim devem persistir. Ainda não estão aprovados o tempo de 10–15 min,
ritmo/justiça da Coruja, direção de arte, música ou clareza geral da história.

## Executar sem tocar no perfil real

Na raiz com pygame-ce instalado:

```sh
MIOPIA_DADOS=/tmp/miopia-teste-equipe SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -B -m unittest discover -s tests -v
```

Use uma pasta temporária nova por sessão e não publique dados do jogador.
Para testar normalmente, execute `python -m src.main` ou o launcher Linux.

## Regressores essenciais

- `test_s03_feedback`: M/F10/R, descoberta e save antigo, queda com custo e
  morte por energia insuficiente, pavio/resina, dano por arco/crítico, avanço.
- `test_campanha`: quatro biomas por comandos normais, incluindo arenas.
- `test_narrativa`: pedidos, entregas, presentes e persistência.
- `test_s02_aranha` e `test_s01_replay`: regras locais determinísticas e replay.
- `test_feedback_mapa_luz`: renderização da superfície e câmera subterrânea.
- `test_corte_vertical` e `test_feedback_s02`: ida, recompensa e volta física.

Testes antigos que exigiam preto absoluto, M para mute, morte imediata por
qualquer queda e ausência de dano comum nos chefes foram atualizados devido
às novas decisões explícitas do jogador. Os novos testes mantêm a morte por
energia esgotada e a vantagem do crítico. Não remover testes para esconder
regressões. Resultados do pacote ficam em `ENTREGA.json` da exportação.

## Sessão humana curta

1. Abra nova História ou continue um save antigo. M abre mapa e M fecha.
   Vá e volte. Só as células percorridas devem aparecer; o terreno distante
   e o marcador exato de um item não descoberto devem continuar ocultos.
2. Compare floresta borrada com a nitidez perto de Lume. K deve esclarecer a
   região de 340 px (ajuste S04). Use pavio antes de K para comparar duração e resina para custo.
3. Converse com Nira ou Casca. Em M, R acompanha o pedido. Recompensa não
   pode duplicar após salvar e carregar. Volte ao rastreio principal.
4. Caia com luz cheia. Volte à borda com menos luz. Caia com 20: deve haver
   morte/retorno ao marco. Tente encontrar uma borda que registre posição ruim.
5. Campo de testes → Asa Fendida/Tecelã: compare dano comum e fraqueza.
   Cada arco deve acertar uma vez; o crítico deve retirar uma parte grande da
   barra. Avalie velocidade e se os avisos continuam justos.
6. Direção + Shift + J no mesmo toque deve executar avanço custando 8 de luz.
   Compare com J/J/J e S+J no ar. Não é uma segunda barra de recurso.
7. Ouça um aviso de cada chefe, sua música e o retorno ao ambiente depois
   da vitória. Julgue volumes em fone e caixas. Audição humana está pendente.

Registre trecho, controle, esperado, observado e aprovar/ajustar. Teste técnico
nunca substitui a avaliação de dificuldade, narrativa, música ou composição.


## Rodada S04

- test_s04_missoes percorre a marca no túnel, a encomenda física e seleção na App.
- test_s04_ferramentas verifica carapaça, pólen, gasto e fraqueza à luz.
- test_s04_visao_taticas verifica teto oculto, ausência de silhueta fora da luz,
  migração, vinte sequências, alvo comprometido, colisão de flancos e cinco famílias.
- Campanha e Infinito continuam exercitados por comandos normais.

Para jogar: Campo de testes → Patrulha em dupla. Q/F escolhe/usa ferramenta.
Na História, Mimo pede o pacote na varanda acima de Nira. Depois de recolher,
volte ao abrigo. No mapa, direita abre pedidos; cima/baixo escolhe e Enter segue.
No Córrego, examine a marca de Casca antes do túnel. Para avaliar a cobra,
ela aparece após a comporta, na margem das raízes inferiores.
O Duelo da aranha mantém o comportamento de referência e seu replay.

Pedir parecer sobre: legibilidade do foco, descoberta sem andares indevidos,
combos, combate em dupla, utilidade das ferramentas, aparência/silvo da cobra
e engasgos no equipamento real. O S04 não fecha automaticamente esses aceites.

## Rodada S05

Suíte atual: 161 testes, incluindo a campanha completa e o Infinito.
test_s05_guardioes cobre mira comprometida, passagem de lado, salto contra
apoios, fuga da queda, ondas, fase II, famílias da Coruja, expiração, crítico
único e recomposição após morte/save. test_s05_comandos cobre fila sem pular
animação, interrupção por dano, armas, custo e menu com rolagem/clique.

Campo de testes → Casco Oco, A Coruja e Oficina dos Espinhos abre os novos
ensaios. Na oficina, V troca arma somente fora do golpe. E no abrigo restaura
luz e alvos. Testes confirmam que a campanha não recebe a arma experimental.
Os 16 ensaios também são abertos e desenhados pela App.

Avaliação humana pendente: ritmo/justiça, aviso sonoro distinguível, prazer de
usar a seiva sob pressão, clareza do sino/crítico, preferência entre armas e
desempenho no notebook real. B06/C06 não estão concluídos.

## Rodada S06

Suíte atual: 171 testes. test_s06_raizes percorre as três salas por controles,
coleta o pino, abre a porta, vence o Caruncho, pega âmbar, estende o cipó,
sobe fisicamente e entrega a Mimo. Também confere volta sem vitória, salto
insuficiente no poço, descoberta bloqueada, save seguro e recomposição.
test_s06_recursos confere marco sem cura, abrigo finito, banco de excedentes,
save sem recarga gratuita, migração, mecanismos antigos e autosave por dano.

Teste humano: Campo de testes → Raízes do Bosque. E lê a placa; S + Espaço
na grade à direita desce. No galho alto da galeria há o pino; siga as duas
setas no chão. A porta fica à esquerda do fundo do poço. O cipó sempre volta
à galeria e, após soltar o nó do viveiro, chega à superfície. O Caruncho tem
ensaio próprio, com entrada pelo poço. São 18 ensaios, sem escrever na campanha.

Na História, compare a falta de cura dos marcos e a reserva única do abrigo.
A bolsa tem dois bálsamos; excedentes ficam no abrigo e não somem dos saves
antigos. Depois de entregar o âmbar a Mimo, a bolsa comporta três. Salvar e
carregar deve preservar energia; morte ainda restaura a luz no marco.

Ainda precisam de parecer: verticalidade/naturalidade, clareza de pistas e
retorno, ritmo do combate opcional, valor da ampola, escassez de provisões,
composição visual e desempenho no notebook. Medições locais não aprovam FPS.
