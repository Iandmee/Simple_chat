from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super_s3cr3t"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///C:\\Users\\milae\\PycharmProjects\\pythonProject2\\server\\test.db"
db = SQLAlchemy(app)
login_length = 40
chat_name_length = login_length
password_length = 100
chat_id_length = 32
hash_salt = "secret_s2lt"
from chat import utils, routes, models  # noqa

db.create_all()
