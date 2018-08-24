#coding=utf-8
from flask import Flask,render_template,request,make_response
import zabbix,os,chukou,json

from flask import send_file, send_from_directory


app=Flask(__name__)


@app.route('/Flask',methods=['POST'])
def Flask():
    if  request.method == 'POST':
        start=request.form['starttime']
        end=request.form['endtime']
        form=request.form['data3']
        start1=start.encode('utf-8')
        end1=end.encode('utf-8')
        if form == 'gg':
            result=zabbix.test(start1,end1)
        else:
            result=chukou.test(start1,end1)

        result=json.dumps(result).decode("unicode-escape")
        return result
        #return render_template('submit.html',file1=ggfilename,jinjia1=info1,file2=ckfilename,jinjia2=info2)

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):

        directory = '/usr/local/nginx/flask/file'
        response = make_response(send_from_directory(directory, filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        return response

@app.route('/')
def index():
    return render_template('index.html')



if __name__=="__main__":
    #app.run(host="0.0.0.0",port=5000,debug=True)
    app.run(host="0.0.0.0",port=5000)
