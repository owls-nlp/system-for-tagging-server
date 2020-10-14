# Серверная часть системы

Пример запуска сервера:

if __name__ == '__main__':

    app.secret_key = 'cwq$tdf-er56m(bi1@-7t74@1i*r-4j4@m@w#isv1ud9r(b4('
    
    http_server = WSGIServer(('0.0.0.0', 5000), app, keyfile='key.pem', certfile='cert.pem')

    http_server.serve_forever()
