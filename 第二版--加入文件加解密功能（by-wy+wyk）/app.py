from flask import Flask, render_template
from flask_cors import CORS
from models import db, User
from auth import auth_bp
from file_handler import file_bp

app = Flask(__name__)
CORS(app)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(file_bp)


# 首页：登录页
@app.route('/')
def index():
    return render_template('index.html')


# 登录后主页面
@app.route('/main')
def main_page():
    return render_template('main.html')


@app.route('/audit')
def audit_page():
    return render_template('audit.html')


# 初始化数据库并添加测试用户
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            # 关键修改：添加 role='admin'
            admin = User(username='admin', role='admin')
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)