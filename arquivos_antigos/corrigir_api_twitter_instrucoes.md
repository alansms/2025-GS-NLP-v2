# Instruções para Corrigir a API do Twitter

Para corrigir o problema da API do Twitter e permitir que as configurações sejam salvas:

1. Certifique-se de que os arquivos `config_manager.py` e `patch_api_twitter.py` foram criados
2. Adicione a seguinte linha ao início do arquivo `app.py`, logo após as importações:
   ```python
   from config_manager import salvar_config_twitter, carregar_config_twitter
   ```

3. Para uma solução rápida, você pode adicionar a seguinte linha no seu arquivo `app.py` dentro da função `construir_interface`, logo após a definição da barra lateral:
   ```python
   # Adicionar patch para API do Twitter
   import patch_api_twitter
   ```

4. Reinicie a aplicação para ver as mudanças

## Como obter o Bearer Token do Twitter

1. Acesse o portal de desenvolvedores do Twitter: https://developer.twitter.com/
2. Faça login e acesse seu projeto (ou crie um novo)
3. No menu do projeto, acesse "Keys and tokens"
4. Você encontrará o Bearer Token na seção "Authentication Tokens"
5. Copie o Bearer Token e cole no campo correspondente da interface

Observação: O Bearer Token é essencial para usar a API v2 do Twitter, que é a versão atual da API.
