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
    possibilidadesDeFimDeJogo.append(set([jogo[0][0], jogo[0][1], jogo[0][2]])) #1ª linha
    possibilidadesDeFimDeJogo.append(set([jogo[1][0], jogo[1][1], jogo[1][2]])) #2ª linha
    possibilidadesDeFimDeJogo.append(set([jogo[2][0], jogo[2][1], jogo[2][2]])) #3ª linha
    possibilidadesDeFimDeJogo.append(set([jogo[0][0], jogo[1][0], jogo[2][0]])) #1ª vertical
    possibilidadesDeFimDeJogo.append(set([jogo[0][1], jogo[1][1], jogo[2][1]])) #2ª vertical
    possibilidadesDeFimDeJogo.append(set([jogo[0][2], jogo[1][2], jogo[2][2]])) #3ª vertical
    possibilidadesDeFimDeJogo.append(set([jogo[0][0], jogo[1][1], jogo[2][2]])) #Diagonal principal
    possibilidadesDeFimDeJogo.append(set([jogo[0][2], jogo[1][1], jogo[2][0]])) #Diagonal secundária

    #Verificação de vitória
    for possibilidade in possibilidadesDeFimDeJogo:
        poss = possibilidade
        if (len(possibilidade) == 1) and ('' not in possibilidade): # Tem somente um valor dentro do trio analisado e este valor não é campo vazio
            vencedor = next(iter(possibilidade)) # recupera primeiro item do set

    return vencedor

@app.route('/')
def novo_jogo():
    scriptVerificacao       = 'SELECT IFNULL(MAX(NUMEROJOGO), 1) FROM JOGO WHERE ? = ? '   

    numeroNovoJogo          = conexao.SelecionaDados(scriptVerificacao, [1, 1])
    scriptInsercaoNovoJogo  =   'INSERT INTO JOGO (NUMEROJOGO, POSICAOLINHA, POSICAOCOLUNA, ' + \
                                'VALORPOSICAO, FINALIZADO) VALUES (?, ?, ?, ?, ?); '
    jogoInicial =   [ 
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
    #Guarda informações jogada
    posicaolinha        = str(request.form['jogada'])[:1]
    posicaocoluna       = str(request.form['jogada'])[1:]
    numeroJogo          = request.form['numeroJogo']
    jogadorDaVez        = request.form['vez']

    #Verifica se está tentando jogar em uma posição ja utilizada
    SQL_VERIFICA_JOGADA = "SELECT VALORPOSICAO FROM JOGO " \
                          "WHERE POSICAOLINHA = ? AND POSICAOCOLUNA = ? AND " + \
                          "NUMEROJOGO = ? "
    infosJogo = (posicaolinha, posicaocoluna, numeroJogo)
    infoPosicao = conexao.SelecionaDados(SQL_VERIFICA_JOGADA, infosJogo)
    if infoPosicao[0][0] != '':
        flash("Posição inválida para jogada, alguém ja jogou aqui")
        jogo = Carregajogo(numeroJogo)
        return render_template('/jogo.html', jogo=jogo, vez=jogadorDaVez, numeroJogo=numeroJogo)
    else:    
    # Continua normalmente o jogo
        scriptNovaJogada    =   "UPDATE JOGO SET VALORPOSICAO = ? " + \
                                "WHERE POSICAOLINHA = ? AND POSICAOCOLUNA = ? AND " + \
                                "NUMEROJOGO = ?"
        dadosJogada = [(jogadorDaVez, posicaolinha, posicaocoluna, numeroJogo)]
        conexao.AtualizaDados(scriptNovaJogada, dadosJogada)

    #Verifica se alguém ganhou o jogo
    jogo        = Carregajogo(numeroJogo)
    vencedor    = VerificaJogoERetornaVencedor(jogo)
    if vencedor != '': #Alguém venceu
        return render_template('/vencedor.html', vencedor=vencedor)    

    #define a próxima jogada
    if jogadorDaVez == 'X':
        JogadorProximaVez = 'O'
    elif jogadorDaVez == 'O':
        JogadorProximaVez = 'X'
    return render_template('/jogo.html', jogo=jogo, vez=JogadorProximaVez, numeroJogo=numeroJogo)

if __name__ == '__main__':
    app.run(debug = True)