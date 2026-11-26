# Produzir e verificar o pacote

S09 usa CPython 3.14.10 e pygame-ce 2.5.8. O runtime foi reconstruído para
preservar módulos da biblioteca padrão que o Fedora distribui somente em
bytecode, incluindo CP437 para arquivos ZIP. Caches com fonte correspondente
e pastas __pycache__ são descartados; bytecode sem fonte é parte do runtime.
A exportação limita datas anteriores a 1980 somente nos metadados do ZIP.
O jogo continua offline e pytest é dependência externa de desenvolvimento.
Os procedimentos/versões anteriores abaixo ficam como histórico.

O alvo de distribuição desta entrega é Fedora Linux 44, desktop x86_64. Na entrega local, abra **distribuicao/Miopia/Miopia**. Para levar a outro computador Fedora, extraia `distribuicao/Miopia-Linux-x86_64.tar.gz` e abra o executável **Miopia** dentro da pasta extraída. Mantenha os arquivos juntos. O menu, os sons, as ilustrações, o interpretador e o módulo pygame-ce acompanham o arquivo.

O executável lê a própria localização, inclusive quando há espaços ou acentos no nome das pastas. Ele inicia o Python local, com biblioteca padrão, pygame-ce e SDL. As bibliotecas do sistema de desktop do Fedora fornecem o ambiente gráfico e os dispositivos de som. Para mover a instalação, mova a pasta inteira. Os dados do jogador são gravados à parte em `$XDG_DATA_HOME/miopia` ou em `~/.local/share/miopia`.

## Pasta de desenvolvimento

- Linux: abra `rodar.sh`.
- Windows: abra `rodar.bat`. Esse atalho é fornecido para desenvolvimento. A distribuição executável desta entrega foi construída no Linux.

Os atalhos procuram CPython 3.10 a 3.14, criam `.venv` local e verificam versão e módulos de pygame-ce em cada abertura. Quando a importação falha, reinstalam o pygame-ce com o pip do ambiente. Uma instalação protegida ou sem acesso à rede pode exigir o pacote de apresentação. Se o executável antigo da venv estiver danificado, o lançador preserva a pasta com o nome `.venv-incompleta-…` antes de criar outra. Para gerar a arte e o áudio, consulte os pré-requisitos dos respectivos scripts em `tools`.

## Reconstrução no Fedora 44 x86_64

Use o Python da venv que contém pygame-ce 2.5.8 e as ferramentas `as` e `ld` de binutils. Execute `.venv/bin/python tools/empacotar_linux.py`. O script gera o executável nativo, copia o runtime e os avisos, inclui a árvore atual de `assets` e `src` e grava o arquivo em `distribuicao`. A substituição do arquivo final só ocorre após a conclusão da compactação.

A preparação desta versão usa o CPython 3.14.8 e a wheel x86_64 manylinux do pygame-ce 2.5.8. Os avisos completos de CPython, SDL e dependências seguem em `avisos-runtime` na distribuição, com um índice de fontes. A wheel Linux inclui bibliotecas dinâmicas de fontes, imagens e som. O ponto de entrada ELF foi construído de `tools/inicio-linux.S`.

## Ensaios do lançador

Em uma pasta temporária, o inicializador nativo carregou pygame-ce, SQLite, as fontes de biblioteca padrão e o mixer 44,1 kHz usando o Python de dentro do pacote. O diretório de trabalho era diferente, o caminho continha espaços, o PATH não continha executáveis e um filtro seccomp recusava a criação de sockets IPv4 e IPv6. A consulta a `sys.path` mostrou apenas caminhos sob o diretório extraído.

Foram exercitados três estados do atalho Linux, com uma wheel de teste local montada a partir da instalação fornecida no projeto: ambiente vazio (instalou), já pronto (reutilizou), e incompleto, com uma extensão removida (reinstalou e iniciou). Foi possível testar a instalação sem acesso ao índice externo. O atalho Windows requer uma rodada de validação em Windows.

O teste de integração abre o binário real duas vezes a partir de uma cópia extraída em outro diretório, com a instalação em modo de leitura, sem Python no PATH e com sockets de internet bloqueados. O smoke desenha o menu e 15 quadros do Bosque em 960 × 540. Uma partida com o armazenamento normal grava preferências, marco e recorde fora do pacote. A segunda abertura os recupera. Nesses ensaios os dispositivos SDL de vídeo e áudio foram simulados; a tela física e a saída de som da máquina da apresentação ainda precisam de uma conferência presencial.

## Segunda rodada

A validação do pacote também abre os seis trechos do Campo de testes, compara o salvamento da História antes e depois, relê o brilho escolhido e recupera o marco intermediário e o item de bolsa em outro processo. O executável continua no mesmo local. Feche a janela de uma sessão anterior e abra o executável novamente para carregar a revisão.

## Corte vertical e compatibilidade

O Campo de testes inclui a entrada do Corte da Figueira. No modo História, o diário abre o mapa do corte pelo Tab quando Lume está dentro da região. A campanha usa o formato de salvamento 3 e lê os formatos 1 e 2. O local do save do jogador continua fora da pasta extraída.

O ensaio desta distribuição usa um perfil SQLite temporário para retomar um save no formato 2, percorrer o corte até o marco do Poço e guardar as descobertas. Uma nova execução recupera o marco da camada, a cartografia e o item na bolsa. Os trechos do Campo de testes são verificados com comparação do save antes e depois de cada visita.
