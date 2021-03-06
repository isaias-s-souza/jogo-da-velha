from flask import Flask, render_template, redirect, request, flash
from dao import Conexao

import os
CAMINHO_PROJETO = os.getcwd()

bancodedados = CAMINHO_PROJETO + '\\jogos.db'
conexao = Conexao(bancodedados)
conexao.CriarTabela()

app = Flask(__name__)
app.secret_key = 'JOGODAVELHA'

def Carregajogo(numeroJogo):
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
    
    parametrosNumerodoJogoAtual = (numeroJogo * 9)
    return conexao.SelecionaDados(scriptResgataDados, parametrosNumerodoJogoAtual)

def VerificaJogoERetornaVencedor(jogo):
    vencedor = ''
    
    possibilidadesDeFimDeJogo = list()
    #todas possibilidades de fim de jogo
    possibilidadesDeFimDeJogo.append(set([jogo[0][0], jogo[0][1], jogo[0][2]])) #1?? linha
    possibilidadesDeFimDeJogo.append(set([jogo[1][0], jogo[1][1], jogo[1][2]])) #2?? linha
    possibilidadesDeFimDeJogo.append(set([jogo[2][0], jogo[2][1], jogo[2][2]])) #3?? linha
    possibilidadesDeFimDeJogo.append(set([jogo[0][0], jogo[1][0], jogo[2][0]])) #1?? vertical
    possibilidadesDeFimDeJogo.append(set([jogo[0][1], jogo[1][1], jogo[2][1]])) #2?? vertical
    possibilidadesDeFimDeJogo.append(set([jogo[0][2], jogo[1][2], jogo[2][2]])) #3?? vertical
    possibilidadesDeFimDeJogo.append(set([jogo[0][0], jogo[1][1], jogo[2][2]])) #Diagonal principal
    possibilidadesDeFimDeJogo.append(set([jogo[0][2], jogo[1][1], jogo[2][0]])) #Diagonal secund??ria

    #Verifica????o de vit??ria
    acabouOJogo = True
    for possibilidade in possibilidadesDeFimDeJogo:
        if '' in possibilidade:
            acabouOJogo = False

        if (len(possibilidade) == 1) and ('' not in possibilidade): # Tem somente um valor dentro do trio analisado e este valor n??o ?? campo vazio
            vencedor = next(iter(possibilidade)) # recupera primeiro item do set

    #Empatou / Deu velha
    if vencedor == '' and acabouOJogo == True:
        vencedor = 'velha'

    return vencedor

@app.route('/')
def inicio():
    return render_template('menu.html')

@app.route('/novo_jogo')
def novo_jogo():
    scriptVerificacao       = 'SELECT IFNULL(MAX(NUMEROJOGO), 0) + 1 FROM JOGO WHERE ? = ? '   

    numeroNovoJogo          = conexao.SelecionaDados(scriptVerificacao, [1, 1])
    scriptInsercaoNovoJogo  = 'INSERT INTO JOGO (NUMEROJOGO, POSICAOLINHA, POSICAOCOLUNA, ' + \
                              'VALORPOSICAO, VENCEDOR) VALUES (?, ?, ?, ?, ?); '
    jogoInicial =   [ 
                        (numeroNovoJogo[0][0], 0, 0, '', ''), 
                        (numeroNovoJogo[0][0], 0, 1, '', ''), 
                        (numeroNovoJogo[0][0], 0, 2, '', ''), 
                        (numeroNovoJogo[0][0], 1, 0, '', ''), 
                        (numeroNovoJogo[0][0], 1, 1, '', ''), 
                        (numeroNovoJogo[0][0], 1, 2, '', ''), 
                        (numeroNovoJogo[0][0], 2, 0, '', ''), 
                        (numeroNovoJogo[0][0], 2, 1, '', ''), 
                        (numeroNovoJogo[0][0], 2, 2, '', '')
                    ]
    jogo = [
                ('', '', ''),
                ('', '', ''),
                ('', '', '')
            ]

    conexao.InsereDados(scriptInsercaoNovoJogo, jogoInicial)
    return render_template('/jogo.html', jogo=jogo, vez="X", numeroJogo=numeroNovoJogo)

@app.route('/jogar', methods=['POST', ])
def jogar(): 
    #Guarda informa????es jogada
    posicaolinha        = str(request.form['jogada'])[:1]
    posicaocoluna       = str(request.form['jogada'])[1:]
    numeroJogo          = request.form['numeroJogo']
    jogadorDaVez        = request.form['vez']

    #Verifica se est?? tentando jogar em uma posi????o ja utilizada
    SQL_VERIFICA_JOGADA = "SELECT VALORPOSICAO FROM JOGO " \
                          "WHERE POSICAOLINHA = ? AND POSICAOCOLUNA = ? AND " + \
                          "NUMEROJOGO = ? "
    infosJogo = (posicaolinha, posicaocoluna, numeroJogo)
    infoPosicao = conexao.SelecionaDados(SQL_VERIFICA_JOGADA, infosJogo)
    if infoPosicao[0][0] != '':
        flash("Posi????o inv??lida para jogada, algu??m ja jogou aqui")
        jogo = Carregajogo(numeroJogo)
        return render_template('/jogo.html', jogo=jogo, vez=jogadorDaVez, numeroJogo=numeroJogo)
    else:    
    # Continua normalmente o jogo
        scriptNovaJogada    =   "UPDATE JOGO SET VALORPOSICAO = ? " + \
                                "WHERE POSICAOLINHA = ? AND POSICAOCOLUNA = ? AND " + \
                                "NUMEROJOGO = ?"
        dadosJogada = [(jogadorDaVez, posicaolinha, posicaocoluna, numeroJogo)]
        conexao.AtualizaDados(scriptNovaJogada, dadosJogada)

    #Verifica se algu??m ganhou o jogo
    jogo        = Carregajogo(numeroJogo)
    vencedor    = VerificaJogoERetornaVencedor(jogo)
    if vencedor != '': #Algu??m venceu
        scriptFinalizacaoJogo = "UPDATE JOGO SET VENCEDOR = ? " + \
                                "WHERE NUMEROJOGO = ?"
        dadosJogoFinalizado = [(vencedor, numeroJogo)]
        conexao.AtualizaDados(scriptFinalizacaoJogo, dadosJogoFinalizado)

        return render_template('/vencedor.html', vencedor=vencedor)    

    #define a pr??xima jogada
    if jogadorDaVez == 'X':
        JogadorProximaVez = 'O'
    elif jogadorDaVez == 'O':
        JogadorProximaVez = 'X'
    return render_template('/jogo.html', jogo=jogo, vez=JogadorProximaVez, numeroJogo=numeroJogo)

@app.route('/resultados')
def resultados():
    scriptResultadoJogosAnteriores =    "SELECT NUMEROJOGO, VENCEDOR, SUM(IIF(VALORPOSICAO <> '', 1, 0)) " + \
                                        "FROM JOGO " + \
                                        "WHERE ? = ? " + \
                                        "GROUP BY NUMEROJOGO, VENCEDOR " 
                                         
    resultados_anteriores = conexao.SelecionaDados(scriptResultadoJogosAnteriores, [1, 1])
    return render_template('/resultados.html', resultadosJogosAnteriores=resultados_anteriores)

if __name__ == '__main__':
    app.run(debug = True)