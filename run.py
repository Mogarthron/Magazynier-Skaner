import sys
from app import app


if __name__ == "__main__":
    if len(sys.argv) == 1:
        app.run(debug=True, host="0.0.0.0", port=5000)#, ssl_context=('localhost.pem', 'localhost-key.pem'))
    else:
        app.run(debug=True, host=sys.argv[1], port=sys.argv[2])