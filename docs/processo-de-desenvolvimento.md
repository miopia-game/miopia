# Produção de Miopia

O primeiro marco é um duelo completo no Bosque. Lume encontra uma aranha, distingue o salto do fio, morre, volta pelo marco e tenta outra resposta. Essa sala serve para decidir como produzir o restante dos inimigos. O segundo marco é uma viagem pela figueira que muda a vida de um morador e dá ao jogador motivo para voltar.

[Quadro de produção](../outputs/01a1b1f9-1c16-78f1-8fae-2455f783cba0/Plano%20de%20produ%C3%A7%C3%A3o%20-%20Miopia.xlsx) · [Atlas de design e simuladores](../outputs/01a1b1f9-1c16-78f1-8fae-2455f783cba0/Atlas%20de%20desenvolvimento%20-%20Miopia.xlsx)

## Ritmo combinado para o planejamento

Use uma semana como janela inicial e seis horas de trabalho ativo como hipótese de capacidade, até medir a disponibilidade da equipe. Reserve uma hora para integração, teste e retorno. A aba **Sprints** calcula a folga com a capacidade escolhida. Se o trabalho exceder a janela, selecione menos cartões ou divida a etapa em duas semanas. Aguardar documentos ou a Valve consome tempo de calendário em separado.

1. Na abertura, escolha um incremento que Thierry consegue experimentar e uma pergunta que o teste deve responder. Filtre **Tarefas** pelo sprint e pelo fluxo **Pronta**. Trabalhe em um cartão por vez.
2. Antes de editar, reproduza o comportamento atual. Anote versão, entrada pelo menu, controles, semente quando houver e resultado observado. A ficha técnica precisa ter local, limite da mudança, dependências e critério de aceite.
3. Implemente a menor mudança que o jogador consegue distinguir. Reaproveite os sistemas existentes. Quando uma proposta exigir animação, IA e uma sala nova ao mesmo tempo, separe-as em cartões. Teste primeiro num ensaio que preserve o save da História.
4. Rode o teste específico, a suíte de regressão e uma passagem pela entrada normal do jogo. Mudou arte ou som? Compare na escala de jogo, em movimento e no escuro, com a origem do material anexada. Mudou save? Teste migração repetida, morte/retorno e reabertura.
5. Em **Tarefas**, registre evidência reproduzível e marque **Em revisão**. Nos cartões humanos, Thierry ou o responsável indicado preenche o parecer. Use **Concluir** apenas com evidência e aprovações aplicáveis. A coluna **Fluxo** mostra se o aceite realmente fechou.
6. Se a avaliação falhar, registre local, ação, esperado e observado. Reabra só a mudança responsável e mantenha um pacote conhecido para comparação. Uma nova rodada começa com o primeiro problema ainda reproduzível.

**Decisões de escopo.** Cada ID do atlas aparece uma vez em **Escopo**. Os itens do núcleo apontam para um cartão. Candidatas e ideias para depois apontam para um lote opcional em **Lotes**. Antes de puxar um lote, escolha um único item, use o aceite do atlas e crie seu cartão. Se uma pessoa só estiver disponível aos fins de semana, a capacidade muda na aba **Começar**. A aprovação é registrada depois de jogar.

## Primeira rodada

O S00 já tem uma [ata de execução e roteiro dos testes](s00/abertura.md). A [triagem de materiais](s00-origens.md) inclui a ficha privada de titularidade e o [levantamento de nomes](s00/nome.md) está pronto para avaliação da equipe.

| Quem | Cartão | Próxima ação |
|---|---|---|
| Thierry | T00.5 | Parecer de revisão registrado no S00. Retestar as correções pelo Estaleiro e pelos ensaios de chefes. Para a avaliação nova, o S01 oferece um duelo exclusivo de aranha. |
| Equipe | T00.3 | Identifique quem criou cada contribuição herdada e quem pode autorizar sua venda e divulgação. Guarde termos, comprovantes e divisão de receitas fora do repositório. |
| Engenharia | T01.2 | Galeria da Seda entregue no S01. O menu abre o ensaio de uma aranha, com abrigo e duas formas de aproximação. |

## S01 • Medir a aranha

As comparações do sprint estão na [ficha de produção da Galeria da Seda](s01-medicao.md). O [roteiro jogável](rodada-de-teste.md) explica como repetir a semente, assistir à tentativa no jogo e localizar o JSON no perfil do jogador. A aranha usa a decisão atual da campanha. O S02 pode comparar seu novo seletor com essa referência usando os mesmos comandos e condições iniciais. Uma mudança nas regras pede gravar a sequência na nova versão a partir dos mesmos comandos, pois o verificador estrito identifica a versão que produziu cada arquivo.

**Linha de base de 06/11/2026.** Rodei os testes do código da raiz com o CPython e o pygame-ce da distribuição Linux, armazenando os dados em diretório temporário e simulando os dispositivos SDL. Resultado: 60 de 60 passaram. No seletor atual da aranha, 20 chamadas a 103 px retornaram salto e 20 chamadas a 104 px retornaram fio. A medição isola a escolha do ataque. A leitura das patas e a sensação de dificuldade dependem de jogar o encontro. SHA-256 do pacote Linux de referência: `f8951a86979ae3275f002d242a09949f41d6c6c461b6e3d2689a4cffcec2a567`.

Para repetir a suíte em um ambiente de desenvolvimento com pygame-ce instalado, use `python -m unittest discover -s tests -v`. Os botões de atalho e o roteiro anterior estão na [rodada de teste](rodada-de-teste.md).

## S02 e feedback da campanha

O **S02** está implementado no [relatório da aranha](s02-aranha.md). A mesma entrega trata o feedback de continuidade, mapa, escuridão, planagem e exploração no [roteiro das correções](s02-feedback.md). Os testes técnicos e a distribuição são conferidos antes de entregar. O aceite de dificuldade, orientação e verticalidade continua com Thierry. As próximas tarefas devem partir desse parecer, preservando saves e as rotas já verificadas.

## Como pedir um cartão à IA

> Execute somente o cartão [ID], na versão [identificador]. Leia o aceite da linha, o comportamento já aprovado e os testes do sistema afetado. Reproduza o ponto de partida pelo menu ou por uma entrada equivalente. Informe quais arquivos precisou alterar e por quê. Se aparecer outra necessidade, registre um cartão separado. Entregue o teste específico, a regressão, o caminho exato para eu jogar e a evidência do que ainda falta validar. Deixe meu parecer em aberto. Use apenas materiais com autorização documentada para o canal pretendido.

## Da faculdade para uma edição comercial

O inventário de **Direitos** tem decisões separadas para jogo, loja e GitHub. No repositório registre apenas um identificador da prova e o resultado da revisão. Mantenha acordos, dados bancários, informações fiscais e comprovantes em arquivo privado da equipe. Para material novo, registre arquivo e versão, autor/titular, URL ou origem da produção, licença aplicável, alterações, crédito exigido e canais autorizados.

* **Equipe e origem acadêmica.** O README credita seis integrantes. O enunciado já apresenta o nome e a premissa, e o jogo preserva material da entrega anterior. Identifiquem as contribuições efetivamente usadas, revisem as condições da A3 e formalizem titular, venda, promoção, GitHub e divisão de receitas. Se faltar respaldo, substituam a expressão específica ou retirem o material. As regras de software e de direitos autorais precisam ser consideradas conforme a contribuição e os vínculos da equipe. [Lei do Software](https://www2.camara.leg.br/legin/fed/lei/1998/lei-9609-19-fevereiro-1998-364738-normaatualizada-pl.html) · [Lei de Direitos Autorais](https://www2.camara.leg.br/legin/fed/lei/1998/lei-9610-19-fevereiro-1998-365399-normaatualizada-pl.html) · [Documentos institucionais USJT](https://www.usjt.br/sobre/documentos-institucionais/)
* **Arte e áudio.** Usem os jogos estudados para discutir decisões de design. Produzam seus próprios layouts, silhuetas, nomes, melodias e capturas. Apurem a origem dos oito estudos visuais, guardem os registros da arte gerada e preencham o questionário da Steam para o conteúdo presente na versão enviada. Os sons sintetizados puderam ser reproduzidos a partir do gerador local. [Questionário de conteúdo](https://partner.steamgames.com/doc/gettingstarted/contentsurvey)
* **Instalador e divulgação.** Revisem individualmente dependências, mídias internas e avisos, inclusive a FreeSans dentro do pygame. O pacote da apresentação leva documentos e capturas acadêmicas. Montem o pacote comercial a partir de uma lista autorizada. Pesquisem nome e identidade antes de investir na cápsula da loja. [Busca de marcas do INPI](https://www.gov.br/inpi/pt-br/servicos/marcas) · [Publicação e licenças no GitHub](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
* **Decisão de venda.** Experimentem o preço proposto na aba **Venda na Steam**. Informem custos e recebimento efetivo por venda com base nas condições da conta. Validem preço regional, termos e prazos antes de gastar. Só o titular autorizado paga taxas, envia a build e escolhe publicar. [Preços](https://partner.steamgames.com/doc/store/pricing) · [Steam Direct](https://partner.steamgames.com/doc/gettingstarted/appfee) · [Entrada no programa](https://partner.steamgames.com/doc/gettingstarted/onboarding)
