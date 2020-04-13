from flask import Flask, jsonify, request
from crypto_gateway import get_received
from crypto_gateway import db


app = Flask(__name__)


@app.route('/btc', methods=["POST", "GET"], endpoint="api.btc")
def btc():
    address = request.values.get("address")
    total = get_received(address)
    resp = {
        "confirmed": total[0],
        "unconfirmed": total[1]
    }
    return jsonify(resp)


@app.route('/btc_ipn', methods=["POST", "GET"], endpoint="api.btc_ipn")
def btc_ipn_request():
    address = request.values.get("address")
    url = request.values.get("url")
    max_confirms = request.values.get("max_confirms", 3)
    ldb = db.DataBase()
    if ldb.add_ipn(address, url, type="btc", max_confirms=max_confirms):
        return "success"
    else:
        return "fail"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)
