# S00 • Triagem de materiais acadêmicos e visuais

**T00.4, conferência de 06/11/2026.** A equipe usa esta lista para separar o piloto privado dos arquivos que podem vir a integrar uma edição pública. O pacote acadêmico já montado continua servindo de referência para o teste do jogo. Para uma demo externa, jogo na loja, material de divulgação ou repositório público, a produção mantém os itens abaixo em quarentena até que o responsável registre uma decisão específica para aquele uso. Quarentena aqui é uma regra de seleção do futuro pacote. Os arquivos instalados continuam nos locais originais.

As quatro pinturas laterais usadas até a revisão `206a09b` foram substituídas na revisão Full HD. A lista histórica abaixo registra o acervo acadêmico daquela época. [Origem dos quatro cenários atuais](arte/PINTURAS_DOS_BIOMAS.md)

## Materiais que chegaram à versão atual

**S35.** A tranca, a parede de colmos, o cofre e a lâmpada do Nicho
dos Berços são desenho procedural de `src/arte_galeria.py`. A Cobra
reusa o desenho procedural e os sons de cobra do jogo, com silhueta
maior e uma segunda trajetória. Registro S35.

**S34.** As faixas de aviso, formas das penas e símbolos dos ninhos
são desenho procedural de `src/arte_arena.py`. Os sons e retratos
da Coruja vêm do acervo local. Registro S34.

**S33.** A meada de Tila, a régua de Bento e os brotos junto de Aru
são desenhos procedurais novos em `src/arte_resgates.py`. As poses de
vaga-lume e os sons são do acervo da equipe. Registro S33.

**S32.** Os entalhes, berços, corda, água, casulos e sinais da ninhada
são desenhos procedurais novos da equipe em `src/corrego_historia.py`
e `src/arte_arena.py`, sem arquivos externos incorporados. As crias
reutilizam as poses de aranha e os efeitos sonoros do acervo local,
sujeitos aos registros já associados a esses arquivos. As fontes
consultadas orientam desenho narrativo e ritmo. Registro S32.

| Identificador | Evidência e uso atual | Alternativa se faltar autorização | Quem revisa e como conferir |
|---|---|---|---|
| A3-TEXTO | O `src/ambiental.py` da entrega A3 e o atual são idênticos, inclusive a cópia no pacote. `src/main.py` consulta `MENSAGENS` ao concluir cada raiz e `src/telas.py` exibe o registro. O uso chega à tela, além do código distribuído. | A equipe de narrativa escreve quatro registros novos a partir de observações ecológicas verificáveis. Como ponto de partida, o jogador pode inferir onde a umidade voltou observando a mudança nas folhas antes de ler a pergunta. Escrever novas perguntas, alternativas e explicações, com autoria registrada. | Roteirista proposto e coautores da base. Fazer uma passagem pelas quatro raízes e pelo diário, verificar alternativas, conclusão e reabertura do save. Comparar os textos efetivamente exibidos com os aprovados. |
| A3-CAPTURA | `capturas/antes.png` corresponde à `capturas/03_partida.png` do MVP. O README aponta para essa captura, e o empacotador acadêmico inclui a pasta de capturas no arquivo distribuído. | Preservar a imagem como registro interno da aula. Criar novas capturas diretamente da build liberada e selecionar arquivos individuais para o pacote, README público e página da loja. | Responsável por distribuição e pessoa que produziu a captura. Conferir manifesto do pacote e links do README público. Estando excluída, a antiga captura deve estar ausente também de GIFs, miniaturas e peças de loja. |
| A3-TEMA | O tema 2 de `TEMAS_A3.pdf` já traz o título e a situação inicial do vaga-lume separado da colônia. O PDF de modelagem identifica o trabalho coletivo. A versão atual usa o nome no título, a situação inicial no roteiro e a instituição nos créditos. | Preservar a função de orientação por luz próxima e escrever de forma independente outra abertura, identidade e texto promocional, se necessário. Redigir o crédito acadêmico com a equipe e pesquisar o título que será divulgado. | Equipe, responsável pela disciplina/instituição quando aplicável e futuro publicador. Anotar a origem do título, da redação e de cada imagem usada. Conferir abertura, créditos, cápsula e trailer por canal. |
| A3-FONTES | `assets/fontes/Nunito-Regular.ttf`, `Nunito-Bold.ttf` e `OFL.txt` são idênticos aos da entrega A3. Há também Liberation Serif com aviso próprio na árvore atual. | Conferir versões e avisos da distribuição pretendida. Se a equipe trocar uma fonte, selecionar outra com termos documentados e testar títulos e diálogos acentuados. | Responsável pelo pacote. Conferir fonte e aviso dentro da instalação limpa. A FreeSans interna do pygame pertence a uma entrada separada da aba **Direitos**. |

Os hashes SHA-256 completos das duas cópias diretas são `595445061b303e7c1c4bf1282062b808e140c7f412e64e351ba1ec9385d3bf4b` (módulo educativo) e `640a2fafd221fb30ca77e2531c624669bcfc2a9ec2f57aaf755c920a2e51a3c4` (captura). Para reproduzir a comparação a partir da raiz do projeto, estando as pastas locais nos endereços originais:

```sh
sha256sum src/ambiental.py "$HOME/Downloads/jogo/A3_Jogo_Miopia/src/ambiental.py"
sha256sum capturas/antes.png "$HOME/Downloads/jogo/A3_Jogo_Miopia/capturas/03_partida.png"
```

## Oito estudos visuais a revisar

Os estudos ficam originalmente em `~/Downloads/prompt/PACOTE_MIOPIA_PROMPT_E_CONCEITOS/`. O caderno de direção de arte registra seu uso no desenvolvimento visual. Na tabela, o prefixo do hash identifica a entrada conferida. A coluna de usos aponta famílias expostas à influência do estudo e que pedem comparação humana. Ela não atribui a criação de uma saída específica a uma única imagem.

| Estudo e SHA-256 abreviado | Função observável no design | Onde revisar no projeto | Caminho independente de substituição | Revisão proposta |
|---|---|---|---|---|
| REF01 • `lume_conceito.png` • `5ecc95d169a8` | Ler o corpo pequeno, as asas e a lanterna de Lume. | `assets/arte/lume_0.png` a `lume_11.png`, capa e capturas com o jogador. | Desenhar três novas silhuetas de perfil a partir dos pivôs de movimento do jogo. Em 44 px, testar uma lanterna lateral e um contorno de asa que diferencie queda de planeio. Guardar rascunhos e decisões. | Arte de personagem + animação. |
| REF02 • `coruja_conceito.png` • `c35a22287b26` | Tornar legível uma guardiã que se orienta por som. | `assets/arte/chefe_3_*.png`, `npc_coruja.png`, `assets/chefes/coruja.png` e imagens de divulgação da luta. | Começar pelo movimento necessário: repouso, cabeça girando em direção ao sino, recuperação após o impacto. Compor novas proporções e perfil de penas a partir de esboços próprios ou observação autorizada. | Arte de criatura + design de combate. |
| REF03 • `gruta_figueira_conceito.png` • `290a527e18e1` | Comunicar profundidade da gruta e mudança de altitude junto à figueira. | Fundo da Gruta (`assets/arte/fundo_3.jpg`), mural do Corte (`corte_da_figueira.jpg`) e capturas da cisterna. | Partir da altura real da câmera e dos patamares medidos. Compor uma fissura lateral e um espelho d'água em cotas próprias, com manchas de valor desenhadas da base para o topo. | Arte de ambiente + design de nível. |
| REF04 • `npcs_nira_casca_eco_conceito.png` • `4aac54044d15` | Distinguir Nira, Casca e Eco em conversa e à distância. | `assets/arte/npc_nira.png`, `npc_casca.png`, `npc_eco.png` e capturas de diálogo. | Desenhar cada um executando seu trabalho: Nira mede um galho, Casca inspeciona uma marca de cheia, Eco localiza o interlocutor. Escolher três novas relações entre tronco, membros e objeto útil, verificadas em miniatura. | Arte de personagem + narrativa. |
| REF05 • `bosque_lateral_conceito.png` • `fba5acd7722b` | Contrastar um túnel baixo com um caminho elevado, mantendo a leitura do apoio. | `fundo_0.jpg`, `beiral_0.png`, objetos de corda/porta e sala do Bosque em `src/fases.py`. | Construir em cinza um tronco que se apoia em forquilha, com uma grade no alto e o retorno por baixo. Desenhar só depois de medir o deslize e o contato do pé no colisor. | Design de nível + arte de ambiente. |
| REF06 • `corrego_lateral_conceito.png` • `7739000d0f7a` | Mostrar que drenar a água altera a travessia entre margens. | `fundo_1.jpg`, `beiral_1.png`, válvula, ponte e localização das teias no Córrego. | Projetar a partir de duas marcas de nível d'água e de um remanso próprio, colocando a válvula onde é possível observar as duas margens. Pintar junções de rocha e madeira a partir desse protótipo. | Design de nível + arte de ambiente. |
| REF07 • `taquaral_arena_conceito.png` • `d0bead129a46` | Dar altura útil aos colmos e tornar o objeto de arena alcançável. | `fundo_2.jpg`, `beiral_2.png`, `obj_bambu.png`, `obj_barril.png` e arena do Taquaral. | Marcar uma área de esquiva e duas zonas de pouso. Desenhar touceiras a partir das medidas de salto e dar ao recipiente de seiva uma silhueta nova. Ensaiar ambos os lados antes de pintar. | Design de combate + arte de ambiente. |
| REF08 • `gruta_arena_conceito.png` • `2c451397a787` | Associar o som do sino a uma superfície de impacto e a uma saída segura. | `obj_sino.png`, `obj_corda.png`, arena da Coruja em `src/chefes.py` e capturas da Gruta. | Construir outra disposição em cinza a partir do tempo de aviso da Coruja. Posicionar o sino numa altura alcançável e expor a superfície de impacto do lado oposto. Criar objetos e fundo após testar a fuga nos dois sentidos. | Design de combate + áudio + arte de ambiente. |

**Resultado da triagem.** Comparei cada estudo com os 956 arquivos regulares de `distribuicao/Miopia-Linux-x86_64.tar.gz` pelo conteúdo. O total de cópias binárias exatas foi zero. Os hashes ajudam a identificar os arquivos comparados. A direção de arte deve examinar separadamente silhueta, composição, traço e usos promocionais, mesmo que a imagem final tenha sido gerada, recortada ou repintada. Os oito originais permanecem de referência privada. Cada saída candidata ao jogo, à página e ao GitHub precisa de procedência própria ou de uma alternativa produzida independentemente.

## Ficha privada para a equipe • T00.3

O produtor reúne os seis colaboradores creditados e identifica quem efetivamente contribuiu para cada item. Se uma pessoa entregou material criado por terceiro, registrar a cadeia até o titular. Para cada papel indicado acima, anotar em privado o nome de quem produzirá, de quem revisará e de quem poderá decidir.

| Campo da ficha privada | O que preencher antes de liberar o arquivo |
|---|---|
| Contribuição e origem | ID estável, arquivo/versão/hash, descrição, autor(es), titular declarado, documentos ou arquivos de criação, participantes e eventuais vínculos acadêmicos aplicáveis. |
| Usos por canal | Registrar separadamente edição e venda do jogo, demo pública, imagens/trailer da loja e divulgação/reutilização do código ou assets no GitHub. Anotar crédito, condições, prazo, território e alterações permitidas conforme o caso. |
| Materiais de IA e referências | Para os oito estudos e saídas correspondentes, registrar origem de cada insumo, ferramenta, data, condições aplicáveis, esboços, intervenções humanas e hash final. Se substituir, registrar o novo processo. |
| Publicação e receita | Identificar quem pode assinar e operar a conta Steamworks. Acordar o que será dividido, quais despesas entram, percentuais, frequência dos relatórios e pessoa responsável por prestar contas. |
| Pendências e retorno | Registrar a decisão por canal, quem a deu, data e evidência. Se houver dúvida, marcar pendência, responsável, alternativa e próxima revisão. Se uma substituição for escolhida, conferir também capturas, textos de loja e arquivos da instalação. |

Na aba **Direitos**, levar somente o ID da evidência e o resultado que a equipe realmente confirmou. Contratos, assinaturas, dados bancários, documentos pessoais e tratativas comerciais ficam no arquivo privado. Esta triagem fornece a evidência técnica para **T00.4**. A decisão humana de **T00.3** fica em aberto.

## Beiral do Taquaral, S29

As sementes são formas desenhadas em tempo real no código de Miopia,
sem arquivo de arte de terceiros. A aba reutiliza `assets/arte/beiral_2.png`
(REF07); o prêmio usa `assets/arte/item_pavio.png` e o efeito de coleta
do acervo atual. Nenhuma licença externa foi incorporada nesta rodada.

## Galeria das Sementes, S30

Os colmos, a placa, a cavilha, os berços, a veneziana e os efeitos de
vento usam desenho do projeto em código. Chão, raízes de fundo e
criaturas usam os materiais presentes na edição S29. A vespa reaproveita
seus dois quadros e recebe postura procedural ao pousar. Os sons de
ferrão, aranha, roda, madeira e coleta vêm do acervo do Miopia.

## História das quatro raízes, S31

Prólogo, transições, falas e resumo da viagem foram escritos para o
Miopia. A linha do sino e a marca são desenhadas em código. Os fundos,
o ícone e o áudio do sino foram reutilizados do acervo instalado.
