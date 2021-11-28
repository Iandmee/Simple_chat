from run_server import app
if __name__ == '__main__':
    app.run(host='localhost', port=1337, debug=False, threaded=True)