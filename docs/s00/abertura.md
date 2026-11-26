# Sprint S00 • Base e procedência

Abertura em 06/11/2026. Foram conferidos o executável acadêmico e as permissões que precisam de revisão antes de montar uma demo pública. No quadro, quatro dos sete cartões têm aceite técnico. Os três pareceres humanos seguem abertos.

| Cartão | Resultado desta rodada | Próxima ação |
|---|---|---|
| T00.1 e T00.2 | A suíte original passou em 60 testes na abertura. O executável instalado abriu menu e Bosque a 960 × 540 com dispositivos SDL simulados. A conferência de procedência abrange 14 grupos do pacote. | Usar esta versão para a avaliação de combate. |
| T00.3 | [Ficha de titularidade da equipe](../s00-origens.md#ficha-privada-para-a-equipe--t003) pronta para preenchimento. | A equipe documenta contribuições, permissões por canal, responsável pela publicação e divisão da receita. Registrar apenas o resultado e o identificador da evidência no quadro. |
| T00.4 | [Triagem do material acadêmico e visual](../s00-origens.md). Há uma alternativa independente e um papel revisor para cada um dos oito estudos. O texto educativo e a captura do MVP são cópias identificadas por hash. | Selecionar ou substituir os arquivos antes de uma distribuição pública. |
| T00.5 | Thierry pediu revisão da travessia por baixo, salto duplo, chefes, áudio, manivelas, duração das fases e verticalidade. | Retestar os trechos corrigidos. Os sinais percebidos e as respostas individuais nas duas tentativas não foram descritos. |
| T00.6 | [Busca de títulos no Brasil](nome.md) pronta para avaliação. Foram examinados Miopia, Myopia, Nervura de Lume e O Breu Tem Nervuras. | O titular escolhe um nome provisório ou solicita outra pesquisa. |
| T00.7 | Verificação de procedência por arquivo, conteúdo e canal. Sete testes novos passaram; a suíte completa passou em 67 testes com o runtime do jogo. | Usar a lista de arquivos e os avisos da edição específica ao preparar cada candidata. |

## Como jogar o cartão T00.5

Abra o [executável Linux](../../distribuicao/Miopia/Miopia) e escolha **Campo de testes → Combate no Bosque**. Faça duas tentativas sem consultar as fichas da fauna. A primeira cena é a do morcego. Use **A/D** para se mover, **J** para golpear e **Espaço** para saltar. Para começar de novo, abra a pausa, volte ao Campo de testes e entre outra vez. O ensaio usa uma jornada separada da História.

| Tentativa | O que vi ou ouvi antes do ataque? | O que fiz e o que aconteceu? |
|---|---|---|
| 1 |  |  |
| 2 |  |  |

**Retorno recebido.** Thierry relatou plataformas que barram a subida, falta de salto duplo, chefes fáceis e previsíveis, áudio irritante, manivelas sem resposta e cenários curtos com pouca verticalidade. O parecer de T00.5 é **Revisar**. O [roteiro atualizado](../rodada-de-teste.md) leva aos trechos modificados. O ensaio exclusivo da aranha foi entregue na [rodada S01](../s01-medicao.md).

## Como repetir a verificação de procedência

Execute na raiz do repositório com Python 3.10 ou superior.

```bash
python3 -B -m unittest discover -s tests -p test_procedencia.py -v
python3 tools/ensaiar_procedencia.py docs/s00/manifesto-amostra.json distribuicao/Miopia --canal jogo
```

* O primeiro comando exercita um conjunto sintético em pasta temporária. Uma peça desconhecida impede a exportação. Retirá-la ou regularizá-la permite gerar um ZIP que contém somente os arquivos liberados e os créditos e avisos requeridos. Divergência de hash, arquivo ausente e licença obrigatória excluída bloqueiam o ensaio. Um ZIP anterior permanece íntegro quando uma nova tentativa falha.
* O segundo comando **deve terminar com código 1** e indicar que o README acadêmico está pendente para o canal jogo. O [manifesto](manifesto-amostra.json) identifica por hash dez arquivos da build de referência, que continha 956 arquivos regulares. A amostra é parcial e os dez registros continuam pendentes nos três canais.
* Para um ensaio positivo próprio, prepare uma pasta candidata isolada e um manifesto **fora dela**. Inclua cada arquivo e os caminhos dos avisos exigidos. Para cada liberação, informe a origem, o identificador privado da evidência e o SHA-256 exato. Execute o comando com o canal correspondente (`jogo`, `loja` ou `github`) e, se quiser gerar o ZIP, acrescente `--saida /caminho/externo/ensaio.zip`. O verificador confere decisões registradas; a decisão sobre os direitos pertence aos titulares.

SHA-256 do [pacote acadêmico original usado na avaliação](../../distribuicao/historico/Miopia-S00-f8951a86.tar.gz): `f8951a86979ae3275f002d242a09949f41d6c6c461b6e3d2689a4cffcec2a567`. A pasta principal de distribuição contém a rodada corrigida.
