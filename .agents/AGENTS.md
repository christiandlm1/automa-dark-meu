# Diretriz Permanente do Projeto — AUTOMA

## Identidade do Produto
O AUTOMA não é um editor de vídeo profissional.
O AUTOMA é uma ferramenta especializada em processamento em lote de vídeos curtos (Reels, Shorts e TikTok).
Todo o desenvolvimento futuro deverá respeitar esta identidade.
O objetivo do software é simples: Importar centenas de vídeos, aplicar automaticamente um mesmo Template, utilizar um Perfil de Exportação e gerar todos os vídeos finais com o mínimo possível de intervenção do usuário.

## Regra de Desenvolvimento
Antes de implementar qualquer funcionalidade, validar a seguinte pergunta:
*Esta funcionalidade reduz o tempo necessário para processar centenas de vídeos?*
Se a resposta for SIM, ela faz parte do AUTOMA. Se a resposta for NÃO, ela não deve ser implementada.

### O que o AUTOMA deve ser
* Biblioteca para importar vídeos em massa.
* Templates reutilizáveis.
* Perfis de exportação reutilizáveis.
* Legendas automáticas.
* Aplicação de fundo.
* Processamento paralelo em lote.
* Exportação automática.
* Histórico dos lotes processados.

### O que o AUTOMA não deve ser
Não transformar o projeto em um editor de vídeo profissional. Não adicionar:
* Timeline.
* Canvas.
* Drag-and-drop de edição.
* Node Editor visual.
* Keyframes.
* Máscaras complexas.
* Correção de cor profissional.
* Ferramentas de edição manual quadro a quadro.
* Funcionalidades que desviem do foco de automação em lote.

## Diretrizes de Arquitetura
Manter a arquitetura modular construída até o momento.
* O Engine executa o processamento.
* Os Plugins encapsulam tecnologias específicas.
* Os Providers abstraem implementações futuras.
* Os Managers coordenam o fluxo.
* Os Templates armazenam apenas configurações visuais.
* Os Perfis de Exportação armazenam apenas configurações técnicas.
* O processamento continua baseado em pipeline_config (JSON).

Nenhum módulo futuro deve quebrar essa separação de responsabilidades.
A experiência deve continuar sendo:
**Importar vídeos → Escolher Template → Escolher Perfil de Exportação → Processar → Exportar.**

## Diretriz Permanente para Trabalho com Sub-Agentes
A partir do Módulo 07, utilizar obrigatoriamente três sub-agentes com responsabilidades fixas:

### Agente 01 — Implementação
Responsável por escrever todo o código do módulo atual.
Responsabilidades: Backend, Frontend, Banco de dados, APIs, Engine, Testes, Walkthrough.
Este agente é o único autorizado a modificar o código.

### Agente 02 — Arquitetura do Próximo Módulo
Enquanto o Agente 01 implementa o módulo atual, o Agente 02 não deve escrever código.
Seu trabalho é preparar o próximo módulo. Ele deve produzir: Plano de Implementação, Estrutura de pastas, Dependências, Alterações necessárias, Compatibilidade com módulos anteriores, Estratégia de integração.
Ao término do módulo atual, o próximo plano já estará pronto para implementação.

### Agente 03 — Auditoria Técnica
Enquanto os outros trabalham, este agente analisa continuamente o projeto.
Ele deve verificar: arquitetura, duplicação de código, compatibilidade, performance, organização, riscos futuros, simplificações possíveis.
Caso encontre melhorias, deve registrá-las como recomendações para o próximo módulo, sem modificar o escopo do produto.

### Planejamento e Fluxo dos Últimos Módulos
* **Módulo 07 — Biblioteca de Assets:** Centralizar recursos reutilizáveis (Fundos, Logos, Fontes, Músicas). Importação em lote.
* **Módulo 08 — Otimização do Processamento:** Melhorar desempenho (Scheduler, Workers, CPU/GPU, Cache, Recuperação de jobs).
* **Módulo 09 — Empacotamento e Distribuição:** Build para Windows, Instalador, Estrutura de configuração, Logs, Testes Finais.

Com essa organização, o desenvolvimento permanece sequencial, mas os três agentes trabalham continuamente. Todo novo recurso deve responder à pergunta: "Isso acelera o processamento em massa de vídeos curtos?". Se não, não implementar.
