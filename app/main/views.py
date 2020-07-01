from flask import render_template,flash, request, url_for, redirect,make_response,abort
from . import main
   
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return 'about'

@main.route('/services')
def services():
    return render_template('services.html')




@main.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method== "POST":
        f=request.files['file']
        bathpath= path.abspath(path.dirname(__file__))  #获取当前文件的绝对路径
        upload_path=path.join(bathpath, 'static','uploads',secure_filename(f.filename))  #文件存放目标位置 
        f.save(upload_path)    #使用cecure_filename放置前端造假 ，注意引用
        return redirect(url_for('main.upload'))   #服务端使用url_for不需要使用.
    return render_template('upload.html')

@main.errorhandler(404)
def page_notfound(err):
    return render_template('404.html')