#!/usr/bin/env python
from app import app, db, auth
from app.models import Goal, User, Feedback
from flask import abort, request, jsonify, g, url_for


@app.route('/api/sync', methods=['Post'])
def sync():
    upload_goals = request.get_json()
    goals = upload_goals.get('goals')
    for goal in goals:
        title = goal.get('title')
        timestamp = goal.get('timestamp')
        level = goal.get('level')
        parent = goal.get('parent')
        start = goal.get('start')
        over = goal.get('over')
        items = goal.get('items')
        username = goal.get('username')
        user_name = username
        mGoal = Goal(level, parent, title, start, over, timestamp, 9, items, username)
        existGoal = Goal.query.filter_by(title=title, username=username).first()

        if goal.get('status') == 1:
            if existGoal is not None:
                db.session.delete(existGoal)  # 增
            db.session.add(mGoal)  # 增
        elif goal.get('status') == 2:
            if existGoal is not None:
                db.session.delete(existGoal)  # 删除
        elif goal.get('status') == 3:
            if existGoal is not None:
                if existGoal.timestamp < timestamp:
                    db.session.delete(existGoal)
                    db.session.add(mGoal)  # 改
    db.session.commit()
    goals_in_db = Goal.query.filter_by(username=upload_goals.get('username')).all()
    contList = []
    for goal in goals_in_db:
        contList.append(goal.serialize())
    return formattingData(200, "success", contList)


def formattingData(code, msg, data):
    return jsonify(
        {
            "code": code,
            "msg": msg,
            "data": data
        }
    )


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return formattingData(400, "信息缺失", {})
    if User.query.filter_by(username=username).first() is not None:
        return formattingData(400, '用户名被注册', {})
        # abort(404)  # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return formattingData(200, "Success",
                          {"username": user.username, "Location": url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        return formattingData(400, '查询不到', {})
    return formattingData(200, 'Success', {'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return formattingData(200, "Success", {"username": g.user.username})


@app.route('/api/feedback', methods=['POST'])
def feedback():
    username = request.json.get('username')
    note = request.json.get('note')
    date = request.json.get('date')
    email = request.json.get('email')
    feedback = Feedback(username, note, date, email)
    db.session.add(feedback)
    db.session.commit()
    return formattingData(200, "Success", {})
