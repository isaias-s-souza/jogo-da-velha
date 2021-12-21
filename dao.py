import sqlite3

class Conexao(object):

    def __init__(self, pathDB):
        self.__pathDB = pathDB
    
    def CriarTabela(self):
        conexao  = sqlite3.connect(self.__pathDB)
        cursor   = conexao.cursor()
        scriptCriacaoTabela = 'CREATE TABLE IF NOT EXISTS "JOGO" (' + \
                            '"ID"	            INTEGER, ' + \
                            '"NUMEROJOGO"	    INTEGER, ' + \
                            '"POSICAOLINHA"	    INTEGER, ' + \
                            '"POSICAOCOLUNA"    INTEGER, ' + \
                            '"VALORPOSICAO"	    TEXT, ' + \
                            '"VENCEDOR"	        TEXT, ' + \
                            'PRIMARY KEY("ID" AUTOINCREMENT));'
        cursor.execute(scriptCriacaoTabela)
        conexao.commit()
        conexao.close()     

    def AtualizaDados(self, comando, dados):
        conexao  = sqlite3.connect(self.__pathDB)
        cursor   = conexao.cursor()
        cursor.executemany(comando, dados)
        conexao.commit()
        conexao.close() 

    def InsereDados(self, comando, dados):
        conexao  = sqlite3.connect(self.__pathDB)
        cursor   = conexao.cursor()
        cursor.executemany(comando, dados)
        conexao.commit()
        conexao.close() 
    
    def SelecionaDados(self, comando, parametros):
        conexao  = sqlite3.connect(self.__pathDB)
        cursor   = conexao.cursor()
        cursor.execute(comando, parametros)
        dados = cursor.fetchall()
        conexao.close() 
        return dados