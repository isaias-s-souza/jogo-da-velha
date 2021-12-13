from flask import Flask, render_template, redirect, request
from dao import Conexao

import os
CAMINHO_PROJETO = os.getcwd()

bancodedados = CAMINHO_PROJETO + '\\jogos.db'
conexao = Conexao(bancodedados)
conexao.CriarTabela()

app = Flask(__name__)
app.secret_key = 'JOGODAVELHA'

@app.route('/')
def novo_jogo():
    scriptVerificacao       = 'SELECT IFNULL(MAX(NUMEROJOGO), 1) FROM JOGO WHERE ? = ? '   

    numeroNovoJogo          = conexao.SelecionaDados(scriptVerificacao, [1, 1])
    scriptInsercaoNovoJogo  =   'INSERT INTO JOGO (NUMEROJOGO, POSICAOLINHA, POSICAOCOLUNA, ' + \
                                'VALORPOSICAO, FINALIZADO) VALUES (?, ?, ?, ?, ?); '
    jogoInicial =   [ 
                        (numeroNovoJogo[0][0], 0, 0, '', 0), 
                        (numeroNovoJogo[0][0], 0, 0, '', 0), 
                        (numeroNovoJogo[0][0], 0, 0, '', 0), 
                        (numeroNovoJogo[0][0], 0, 0, '', 0), 
                        (numeroNovoJogo[0][0], 0, 0, '', 0), 
                        (numeroNovoJogo[0][0], 0, 0, '', 0), 
                        (numeroNovoJogo[0][0], 0, 0, '', 0), 
                        (numeroNovoJogo[0][0], 0, 1, '', 0), 
                        (numeroNovoJogo[0][0], 0, 2, '', 0),
                        (numeroNovoJogo[0][0], 1, 0, '', 0), 
                        (numeroNovoJogo[0][0], 1, 1, '', 0), 
                        (numeroNovoJogo[0][0], 1, 2, '', 0),
                        (numeroNovoJogo[0][0], 2, 0, '', 0), 
                        (numeroNovoJogo[0][0], 2, 1, '', 0), 
                        (numeroNovoJogo[0][0], 2, 2, '', 0)
                    ]
    jogo = [
                ('', '', ''),
                ('', '', ''),
                ('', '', '')
            ]

    conexao.InsereDados(scriptInsercaoNovoJogo, jogoInicial)
    return render_template('/jogo.html', jogo = jogo, vez="X", numeroJogo=numeroNovoJogo)

@app.route('/jogar', methods=['POST', ])
def jogar(): 
    print(request)
    posicaolinha        = str(request.form['jogada'])[:1]
    posicaocoluna       = str(request.form['jogada'])[1:]
    jogadorDaVez        = request.form['vez']
    numeroJogo          = request.form['numeroJogo']

    scriptNovaJogada    =   "UPDATE JOGO SET VALORPOSICAO = ? " + \
                            "WHERE POSICAOLINHA = ? AND POSICAOCOLUNA = ? AND " + \
                            "NUMEROJOGO = ?"
    dadosJogada = [(jogadorDaVez, posicaolinha, posicaocoluna, numeroJogo)]
    conexao.AtualizaDados(scriptNovaJogada, dadosJogada)

    if request.form['vez'] == 'X':
        JogadorProximaVez = 'O'
    elif request.form['vez'] == 'O':
        JogadorProximaVez = 'X'

    scriptResgataDados =    'SELECT ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 0 AND POSICAOCOLUNA = 0 AND NUMEROJOGO = ?), ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 0 AND POSICAOCOLUNA = 1 AND NUMEROJOGO = ?), ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 0 AND POSICAOCOLUNA = 2 AND NUMEROJOGO = ?) ' + \
                            'UNION ALL ' + \
                            'SELECT ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 1 AND POSICAOCOLUNA = 0 AND NUMEROJOGO = ?), ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 1 AND POSICAOCOLUNA = 1 AND NUMEROJOGO = ?), ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 1 AND POSICAOCOLUNA = 2 AND NUMEROJOGO = ?) ' + \
                            'UNION ALL ' + \
                            'SELECT ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 2 AND POSICAOCOLUNA = 0 AND NUMEROJOGO = ?), ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 2 AND POSICAOCOLUNA = 1 AND NUMEROJOGO = ?), ' + \
                            '(SELECT VALORPOSICAO FROM JOGO ' + \
                             'WHERE POSICAOLINHA = 2 AND POSICAOCOLUNA = 2 AND NUMEROJOGO = ?) '
    
    parametrosNumerodoJogoAtual = ( numeroJogo, numeroJogo, numeroJogo,
                                    numeroJogo, numeroJogo, numeroJogo,
                                    numeroJogo, numeroJogo, numeroJogo)
    jogo = conexao.SelecionaDados(scriptResgataDados, parametrosNumerodoJogoAtual)

    return render_template('/jogo.html', jogo=jogo, vez=JogadorProximaVez, numeroJogo=numeroJogo)


if __name__ == '__main__':
    app.run(debug = True)