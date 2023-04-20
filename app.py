from flask import Flask


from viwes import viwes

app = Flask(__name__)
app.register_blueprint(viwes, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)

    1