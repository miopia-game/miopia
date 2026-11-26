# Invariantes verificáveis

Escolha as pertinentes ao cartão; use os limites reais do mundo, não a janela 960×540.

| Domínio | Contrato e evidência |
|---|---|
| Execução | Sem exceção inesperada no percurso executado; registrar transição e traceback |
| Espaço | Posição/velocidade finitas; dentro da região válida; sem atravessar sólido sob velocidades/dt testados |
| Contato | Penetração persistente não explicada vira reprodução; cordas/elevadores e passagens dirigidas têm contrato próprio |
| Recursos | Vida/brilho dentro do domínio e consumo/recuperação conforme regras S08/S09 |
| Input | Soltar tecla, pausa e foco não deixam borda de golpe ou movimento residual indevido |
| Persistência | Carregar não duplica recompensa, resgate, globo ou tocha; saves antigos mantêm conquistas |
| Puzzle | Pré-requisito alcançável; objeto essencial recuperável; saída/retorno após morte e reinício |
| Combate | Um arco não multiplica dano por quadro; aviso, vulnerabilidade e limpeza de projéteis consistentes |
| Entidades | População limitada no cenário estável; crescimento explicado por spawn/cache ou investigado |
| Renderização | Contrato por cena/ROI; legibilidade e personagem conferidos em imagem real, sem limiar global de cores |
| Memória | Aquecimento separado da medição; distinguir Python/RSS/GPU/áudio e memória do harness |
| Entrada normal | Menu, prologue/skip, campanha, pausa, morte e retorno pelo fluxo público |

Testes com fixtures só provam o contrato isolado. A rota principal precisa de teste por comandos reais, sem atribuir flags de chefe/vitória; o Campo de testes é rotulado como preparado. Cenário sem falha observada não comprova ausência de bugs.
