# O som da mata

A trilha atual está listada em [S11](equipe/S11.md), com 14 faixas em Ogg.
As anotações sobre WAV são das versões anteriores.

## S07 — avisos e motivos provisórios

tools/gerar_audio_s07.py sintetiza 30 avisos (`aviso_ESPECIE_0` até `_4`)
para morcego, aranha, sombra, vespa, carabídeo e cobra. A cadência corresponde
à família do golpe em src/taticas.py; registro e timbre mudam por espécie.
São cinco famílias e vinte sequências por espécie, não vinte animações novas.
Presença ocupa canais 10–11; avisos espaciais ocupam 12–15 e reduzem a música
brevemente. Fones ajudam a perceber lado/distância; distinção requer audição.

Campo de testes → Escuta dos ataques: J troca família, K troca espécie,
E reproduz à direita. Não grava no save. Sinais novos: coruja_eco,
chamado_final, harmonia e resgate. Temas novos: trilha_jardim,
trilha_retorno e trilha_chefe_final. A App muda o tema por região/desfecho;
o final da Coruja ganha tema mais rápido. Os anteriores foram preservados.

Novos arquivos são PCM mono 16 bits, 22.050 Hz, com panorama calculado na
execução. Gerador usa apenas biblioteca padrão, osciladores, envelopes e
ruído com semente fixa, sem samples ou downloads. Inventário/hash em
docs/equipe/audio-S07.json. Não há aprovação de composição ou mixagem:
A02 permanece parcial até parecer humano; não se infere qualidade por hash.

## Atualização de 12/11/2026

As arenas agora têm quatro temas instrumentais diferentes, gerados por
`tools/gerar_trilhas_chefes.py`. São sínteses locais em 22.050 Hz, com motivos,
baixo e percussão próprios, sem samples externos. Arquivos
`trilha_chefe_0.wav` a `trilha_chefe_3.wav`. A App entra no tema ao detectar o
chefe ativo e retorna à ambiência do bioma depois da vitória. Os avisos usam
rasgo, seda, casco e presságio com canais espaciais. A leitura da altura da
Asa mantém dois avisos distintos. A qualidade musical e os volumes aguardam
audição humana; não há alegação de trilha final aprovada.

O texto abaixo descreve a ambiência herdada, que continua nas explorações.

Nesta rodada o menu e as fases usam uma paisagem sonora sem melodia. O Bosque tem folhas e gotas espaçadas, o Córrego tem água contínua, o Taquaral estala e a Gruta alterna eco e silêncio. A tela de morte deixa a ressonância cair. O controle **Ambiência** ajusta essa camada. **Efeitos** controla passos, golpes, mecanismos, avisos e batimentos.

## Como localizar um inimigo

Dois passos suaves de folha se alternam, e o pulo usa um ataque sonoro menos agudo. A baixa energia toca um par de batimentos a cada seis segundos. Sons de presença usam uma faixa de mixagem separada dos avisos de ataque; somente um aviso reduz a ambiência, com transição gradual. O aviso de chefe usa uma única voz, com posição quando a fonte está ao alcance. Todos os 56 WAVs desta edição são sintetizados pelo gerador local.

Cada espécie tem uma assinatura antes de atacar: batidas curtas de asas do morcego, toques espaçados da aranha, sopro da sombra, zumbido da vespa e estalo grave do carabídeo. O mixer posiciona o aviso à esquerda ou à direita de Lume e atenua seu volume com a distância. O aviso também abaixa a ambiência por um instante. Os sinais de mira e vulnerabilidade continuam visíveis para quem joga com o som desligado.

## Arquivos e procedência

| Arquivos em assets/sons | Função |
|---|---|
| trilha_menu, trilha_historia, trilha_bosque, trilha_corrego, trilha_taquaral, trilha_gruta, trilha_derrota, trilha_vitoria, trilha_creditos | Nove paisagens locais de vento, pingos, folhas, bambu e ressonância. Os nomes de arquivo são os mesmos esperados pelo mixer. |
| asa_perto, patas_perto, sopro_perto, zurro_perto, casco_perto | Presença das cinco espécies. |
| rasgo, fio_disparo, ferrao, casco_avanco, pressagio | Início de ataques, projéteis e investidas. |
| rebote, bloqueio, abatido, morte | Contato, defesa, fim de encontro e perda de fagulha. |
| camada_combate, camada_pulso, camada_vida | Rumor de perigo, batimento de pouca energia e insetos da raiz restaurada. |

Todos os arquivos são WAV PCM mono, 44,1 kHz. A posição estéreo dos avisos é calculada em tempo real. Os sons desta versão foram sintetizados para Miopia, sem gravações nem samples de terceiros. Podem acompanhar o projeto da faculdade e seu repositório. O código de produção é `tools/gerar_audio.py` e requer NumPy apenas para gerar os arquivos. O jogo lê os WAVs locais e segue jogável sem dispositivo de áudio.


## S04

Silvos próprios da cobra em silvo_perto.wav e silvo_ataque.wav, gerados por
tools/gerar_som_cobra.py com ruído filtrado/envelopes. Sem samples externos.
Presença e aviso ocupam canais diferentes; posições continuam em estéreo.

## S05

tools/gerar_avisos_s05.py produz seis WAVs mono PCM 16 bits, 22,05 kHz:
casco_salto (tom ascendente), casco_chifre (raspado descendente), coruja_garra
(queda tonal), coruja_penas (três pulsos), casco_muda e coruja_muda (transições).
Osciladores, ruído de semente fixa e envelopes; sem samples, gravações,
melodias copiadas ou downloads. Os avisos usam os canais espaciais reservados;
as transições têm canal próprio. Audição humana ainda pendente.
