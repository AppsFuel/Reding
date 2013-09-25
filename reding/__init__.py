
if __name__ == '__main__':
    from reding.app import app
    from reding.settings import DAEMON_CONFIG
    #app.run(debug=True, port=5001); import sys; sys.exit()
    from cherrypy import wsgiserver
    w = wsgiserver.WSGIPathInfoDispatcher({'/': app.wsgi_app})
    server = wsgiserver.CherryPyWSGIServer(
        bind_addr=(
            DAEMON_CONFIG['host'],
            DAEMON_CONFIG['port']
        ),
        wsgi_app=w,
    )

    try:
        server.start()
    except KeyboardInterrupt:
        print('Shutting down Reding...')
    finally:
        server.stop()
        print('Done.')
