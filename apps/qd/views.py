# 导入qd蓝图对象
from . import qd
from flask import render_template, redirect, url_for, flash, session,jsonify
import time
from apps.decorator import login_validate
from flask.views import MethodView
from apps.qd.forms import QdForm
from apps.models import Qd, db, User


# 显示今日时间
def create_time():
    create_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    return create_time


# 登录验证
# @qd.route("/qdhome/",endpoint="qd_home")
# @login_validate
# def qd_home():
#     return render_template("qd/qd_home.html",create_time=create_time())

class QdView(MethodView):
    decorators = [login_validate]

    def get(self):
        if session['role'] == 0:
            return render_template("qd/manager_qd_home.html")
        else:
            # 查找并显示签到表里的签到历史数据
            qds = Qd.query.filter_by(uid=session.get("uid")).order_by(Qd.create_time.desc()).all()
            today_qd = None
            # 先看是否有签到历史数据 如果有
            if len(qds) > 0:
                # 如果签到历史的第一条数据是今天的（如果已经签过到）
                if qds[0].create_time == create_time():
                    today_qd = qds[0]
                # 如果今天还没签到
                else:
                    today_qd = None
            else:
                today_qd = None
            return render_template("qd/qd_home.html", create_time=create_time(), qds=qds, today_qd=today_qd)

    def post(self):
        form = QdForm()
        # 如果验证通过 提交签到数据
        if form.validate_on_submit():
            uid = session.get("uid")
            qd = Qd(uid=uid, stage=form.data.get("stage"), progress=form.data.get("progress"),
                    code_num=form.data.get("code_num"), bug_num=form.data.get("bug_num"),
                    create_time=form.data.get("create_time"), remark=form.data.get("remark"))
            db.session.add(qd)
            db.session.commit()
            return redirect(url_for("qd.qd"))
        else:
            flash("请将签到信息填写完整！")
            return redirect(url_for("qd.qd"))


@qd.route("/search_qd/", methods=["POST"])
def search_qd():
    # 查讯所有的签到数据
    qd = Qd.query.join(User).join(User.clazzs).all()
    qds = []
    for q in qd:
        # 班级名
        cname=q.user.clazzs[0].name if len(q.user.clazzs)>0 else "None"
        #班级id
        cid=q.user.clazzs[0].id
        #昵称
        uname=q.user.nick_name
        uid=q.uid
        qds.append({
            "id":q.id,
            "uid":uid,
            "uname":uname,
            "cid":cid,
            "cname":cname,
            "stage":q.stage,
            "progress":q.progress,
            "code_num":q.code_num,
            "bug_num":q.bug_num,
            "create_time":q.create_time,
            "remark":q.remark
        })
    return jsonify({"qd":qds})

qd.add_url_rule('/qd/', view_func=QdView.as_view('qd'))
