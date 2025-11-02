# Status de Publicação no GitHub

Até o momento, o código deste projeto está versionado localmente e as alterações mais recentes ainda não foram publicadas em um repositório remoto do GitHub. O histórico local contém a implementação das funcionalidades descritas nas últimas interações (modo guardião, mapeamento de ativos urbanos, gamificação comunitária etc.).

## Como publicar no GitHub

1. Configure um repositório remoto no GitHub (crie o repositório via interface web ou CLI e copie a URL HTTPS ou SSH).
2. Adicione o repositório remoto ao projeto:
   ```bash
   git remote add origin <URL_DO_REPOSITORIO>
   ```
3. Verifique se os commits locais estão atualizados:
   ```bash
   git status
   git log --oneline
   ```
4. Envie o histórico local para o GitHub:
   ```bash
   git push -u origin <nome-da-branch>
   ```
5. Crie um Pull Request a partir da interface do GitHub, descrevendo as alterações aplicadas.

> **Observação:** caso já exista um remoto configurado, basta executar o `git push` com as credenciais apropriadas para publicar as mudanças vigentes.
