# compdist-servidor-dados

Nesse repositório se encontra o código do Servidor de Dados do projeto "Banco Distribuído com Webservices" da disciplina de Computação de Distribuída. Utilizado em conjunto com o Servidor de Negócios que se encontra [nesse outro repositório](https://github.com/babieste/compdist-servidor-negocios).

## Tokens de Autorização

Cada Servidor de Negócio precisa informar o seu próprio `auth_token` no header `Authorization` ao fazer as requisições para o Servidor de Dados. Abaixo está uma lista que indica qual é o `auth_token` de cada Servidor de Negócio.

|ID do Servidor de Negócio|auth_token|
|-------------------------|----------|
|1                        |`secret#1`|
|2                        |`secret#2`|
|3                        |`secret#3`|

## Endpoints

### `GET /conta/<conta_id>/saldo`

Retorna o saldo atual da conta informada.

Request headers:

```
Authorization: <auth_token>
```

Responses:

1. Sucesso (status code: 200)

```
{
  "conta": 123,                # id da conta
  "saldo": 987654321           # saldo da conta atualmente
}
```

2. Falha por problema de autorização (status code: 403)

Ocorre se o header Authorization não for informado ou for informado com um valor incorreto.

```
{
  "codigo_erro": "NAO_AUTORIZADO"      # código de erro
}
```

3. Falha porque a conta não existe (status code: 404)

Ocorre quando não existe uma conta com o conta_id informado.

```
{
  "codigo_erro": "CONTA_INEXISTENTE"   # código de erro
}
```

4. Falha por causa de lock (status code: 423)

Ocorre quando a operação de alteração de saldo ainda está sendo realizada por algum Servidor de Negócio.

```
{
  "codigo_erro": "CONTA_COM_LOCK",     # código de erro
  "responsavel": 2                     # id do servidor de negócio que lockou a conta
}
```

### `PUT /conta/<conta_id>/saldo/<valor>`

Altera o saldo da conta informada. Esse processo demora x segundos para ocorrer, onde x é igual ao resultado de `<valor>/100`. Durante o processo de alteração do saldo a conta fica em estado de lock.

Request headers:

```
Authorization: <auth_token>
```

Responses:

1. Sucesso (status code: 200)

```
{
  "conta": 123,                # id da conta
  "saldo": 98765               # saldo da conta após a alteração, em centavos
}
```

2. Falha por problema de autorização (status code: 403)

Ocorre se o header Authorization não for informado ou for informado com um valor incorreto.

```
{
  "codigo_erro": "NAO_AUTORIZADO"      # código de erro
}
```

3. Falha porque a conta não existe (status code: 404)

Ocorre quando não existe uma conta com o conta_id informado.

```
{
  "codigo_erro": "CONTA_INEXISTENTE"   # código de erro
}
```

4. Falha por causa de lock (status code: 423)

Ocorre quando a operação de alteração de saldo ainda está sendo realizada por algum Servidor de Negócio.

```
{
  "codigo_erro": "CONTA_COM_LOCK",     # código de erro
  "responsavel": 2                     # id do servidor de negócio que lockou a conta
}
```

### `POST /conta`

Cria uma nova conta de usuário com o saldo inicial informado.

Request body:

```
{
    "saldo": 100
}
```

Responses:

1. Sucesso (status code: 200)
```
{
    "conta": 1,
    "is_locked": false,
    "locked_by": null,
    "saldo": 100,
    "token": "503145c0-0f69-47d0-a95f-e6c14b0c1a09"
}
```
