from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models

# 通过指定的配置文件创建对应配置的app
# create_app 就类似于工厂方法
from info.models import User

app = create_app('development')
manager = Manager(app)
# 将app与db关联
Migrate(app, db)
# 将数据库迁移命令添加到manager中
manager.add_command('db', MigrateCommand)

@manager.command
def dev():
    from livereload import Server
    app.debug = True
    live_server= Server(app.wsgi_app)
    live_server.watch('**/*.*')
    #live_server.serve(open_url_delay=True)
    live_server.serve(open_url=True)   #pip install tornado==4.5.3

@manager.option('-n', '-name', dest='name')
@manager.option('-p', '-password', dest='password')

def createsuperuser(name, password):
    if not all([name, password]):
        print("参数不足")

    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    print("添加成功")


if __name__ == "__main__":
    print(app.url_map)
    manager.run()
