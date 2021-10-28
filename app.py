import time
from flask import Flask, request, abort
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[
                        logging.FileHandler('logs/record.log', mode='w'),
                        logging.StreamHandler()
                    ])

db = {
    'contas': [
        {'id': 1, 'saldo': 150, 'is_locked': False, 'locked_by': None},
        {'id': 2, 'saldo': 0, 'is_locked': False, 'locked_by': None},
        {'id': 3, 'saldo': 4800000, 'is_locked': False, 'locked_by': None},
        {'id': 4, 'saldo': 100, 'is_locked': True, 'locked_by': 3},
    ]
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

    valor = int(valor)

    conta['is_locked'] = True
    conta['locked_by'] = serv_negocio_id

    app.logger.debug('Realizando operação de alteração de saldo da conta {}'.format(
        {'conta': conta['id']}))

    # Simulando uma operação demorada
    time.sleep(valor//100)

    conta['is_locked'] = False
    conta['locked_by'] = None

    conta['saldo'] = valor

    app.logger.debug('Saldo da conta atualizado {}'.format(
        {'conta': conta['id'], 'saldo': conta['saldo']}))

    return {
        'conta': conta['id'],
        'saldo': conta['saldo'],
    }, 200
