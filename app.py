import time
import uuid
from flask import Flask, request, abort
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[
                        logging.FileHandler('logs/record.log', mode='w'),
                        logging.StreamHandler()
                    ])

db = {
    'contas': []
}

tokens = [
    {'serv_negocio_id': 1, 'auth_token': 'secret#1'},
    {'serv_negocio_id': 2, 'auth_token': 'secret#2'},
    {'serv_negocio_id': 3, 'auth_token': 'secret#3'},
]

COD_ERR_NAO_AUTORIZADO = 'NAO_AUTORIZADO'
COD_ERR_CONTA_INEXISTENTE = 'CONTA_INEXISTENTE'
COD_ERR_CONTA_COM_LOCK = 'CONTA_COM_LOCK'


def authorize(request):
    provided_auth_token = request.headers.get('Authorization')
    serv_negocio_id = next(
        (
            token['serv_negocio_id']
            for token in tokens
            if token['auth_token'] == provided_auth_token
        ),
        None
    )
    if serv_negocio_id == None:
        abort(app.make_response(({
            'codigo_erro': COD_ERR_NAO_AUTORIZADO,
        }, 403)))
    return serv_negocio_id


def raise_conta_inexistente():
    abort(app.make_response(({
        'codigo_erro': COD_ERR_CONTA_INEXISTENTE,
    }, 404)))


def raise_locked(responsavel):
    abort(app.make_response(({
        'codigo_erro': COD_ERR_CONTA_COM_LOCK,
        'responsavel': responsavel,
    }, 423)))


@app.get('/')
def get_home():
    return 'API do servidor de dados'


@app.get('/conta/<conta_id>/saldo')
def get_saldo(conta_id):
    authorize(request)
    conta = next(
        (
            conta
            for conta in db['contas']
            if conta['id'] == int(conta_id)
        ),
        None
    )

    if conta == None:
        raise_conta_inexistente()
    if conta['is_locked']:
        raise_locked(conta['locked_by'])

    app.logger.debug('Retornando o saldo atual da conta {}'.format(
        {'conta': conta['id'], 'saldo': conta['saldo']}))

    return {
        'conta': conta['id'],
        'saldo': conta['saldo'],
    }, 200


@app.put('/conta/<conta_id>/saldo/<valor>')
def set_saldo(conta_id, valor):
    serv_negocio_id = authorize(request)
    conta = next(
        (
            conta
            for conta in db['contas']
            if conta['id'] == int(conta_id)
        ),
        None
    )

    if conta == None:
        raise_conta_inexistente()
    if conta['is_locked']:
        raise_locked(conta['locked_by'])

    conta['is_locked'] = True
    conta['locked_by'] = serv_negocio_id

    app.logger.debug('Realizando operação de alteração de saldo da conta {}'.format(
        {'conta': conta['id']}))

    # Simulando uma operação demorada
    time.sleep(5)

    conta['is_locked'] = False
    conta['locked_by'] = None

    conta['saldo'] = int(valor)

    app.logger.debug('Saldo da conta atualizado {}'.format(
        {'conta': conta['id'], 'saldo': conta['saldo']}))

    return {
        'conta': conta['id'],
        'saldo': conta['saldo'],
    }, 200


@app.post('/conta')
def post_conta():
    body = request.get_json()
    saldo_inicial_desejado = int(body['saldo'])
    if len(db['contas']) == 0:
        id = 1
    else:
        ultimo_id = max(db['contas'], key=lambda conta: conta['id'])['id']
        id = ultimo_id + 1
    nova_conta = {
        'id': id,
        'saldo': saldo_inicial_desejado,
        'is_locked': False,
        'locked_by': None,
        'token': str(uuid.uuid4())
    }
    db['contas'].append(nova_conta)
    return {
        'conta': nova_conta['id'],
        'saldo': nova_conta['saldo'],
        'is_locked': nova_conta['is_locked'],
        'locked_by': nova_conta['locked_by'],
        'token': nova_conta['token']
    }, 200


@app.get('/conta/<conta_id>')
def get_conta(conta_id):
    conta = next(
        (
            conta
            for conta in db['contas']
            if conta['id'] == int(conta_id)
        ),
        None
    )
    if conta == None:
        raise_conta_inexistente()
    if conta['is_locked']:
        raise_locked(conta['locked_by'])
    return {
        'conta': conta['id'],
        'saldo': conta['saldo'],
        'is_locked': conta['is_locked'],
        'locked_by': conta['locked_by'],
        'token': conta['token']
    }, 200


@app.get('/conta')
def get_contas():
    return {
        'contas': [{
            'conta': conta['id'],
            'saldo': conta['saldo'],
            'is_locked': conta['is_locked'],
            'locked_by': conta['locked_by'],
            'token': conta['token']
        } for conta in db['contas']]
    }, 200
