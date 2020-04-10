from flask import Flask
from flask_restful import reqparse, abort, Resource, Api, request
from flask_restful.representations import json
import calendar;
import time;

from connection import mydb

dbCursor = mydb.cursor()

app = Flask(__name__)
api = Api(app)


class Account(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('mobileNumber', type=str)
        args = parser.parse_args()
        dbCursor.execute("select * from user where mobileNumber = {}".format(args['mobileNumber']))
        res = dbCursor.fetchall()
        print(res)
        if (len(res) > 0):
            return {'id': res[0][0],
                    'phoneNum': res[0][1],
                    'name': res[0][2],
                    'thumb': res[0][3],
                    'code': 1}
        return {'message': "Account not found with " + args['mobileNumber'], 'code': 0}

    def post(self):
        args = request.get_json()

        if userExist(args['mobileNumber']):
            return {'message': 'User exist', 'code': 0}

        sql = "INSERT INTO user (mobileNumber, name) VALUES (%s, %s)"
        val = (args['mobileNumber'], args['name'])
        dbCursor.execute(sql, val)
        mydb.commit()

        return {'message': 'Account Created', 'code': 1}

    def delete(self):
        args = request.get_json()
        sql = "DELETE FROM user where id = "+ int(args['id'])
        dbCursor.execute(sql)
        mydb.commit()
        return {"message": 'Account deleted', 'code': 1}

    def put(self):
        args = request.get_json()
        print(args)
        sql = 'update user set thumb = "'+ args['thumb'] +'" where mobileNumber = ' + args['mobileNumber']
        dbCursor.execute(sql)
        mydb.commit()
        return {"message": "Image updated", "code": 1}


def userExist(phoneNum):
    sql = "select * from user where mobileNumber = "+phoneNum
    dbCursor.execute(sql)
    res = dbCursor.fetchall()

    if(len(res)>0):
        return True

    return False


class Group(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        args = parser.parse_args()
        dbCursor.execute("select * from groups where id = {}".format(args['id']))
        res = dbCursor.fetchall()
        print(res)
        if (len(res) > 0):
            return {'id': res[0][0],
                    'name': res[0][1],
                    'thumb': res[0][2],
                    'code': 1}
        return {'message': "Group not found", 'code': 0}

    def post(self):
        args = request.get_json()
        print(args)
        sql = "INSERT INTO groups (name) VALUES ('{}')".format(args['name'])

        dbCursor.execute(sql)
        mydb.commit()

        #insert group user
        group_id = dbCursor.lastrowid

        sql = "INSERT INTO group_users (user_id, group_id, position ) VALUES (%s, %s, 'creator')"
        val = (args['user_id'], group_id)

        dbCursor.execute(sql, val)
        mydb.commit()

        return {'message': 'Group Created', 'code': 1}

    def delete(self):
        args = request.get_json()
        sql = "DELETE FROM groups where id = " + int(args['id'])
        dbCursor.execute(sql)
        mydb.commit()
        return {"message": 'Account deleted', 'code': 1}

    def put(self):
        args = request.get_json()
        print(args)
        sql = 'update groups set thumb = "' + args['thumb'] + '" where id = ' + str(args['groupId'])
        dbCursor.execute(sql)
        mydb.commit()
        return {"message": "Image updated", "code": 1}


class Groups(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userId', type=int)
        args = parser.parse_args()
        sql = 'SELECT groups.id, groups.name, groups.thumb from groups inner join group_users where (group_users.user_id = '+ str(args['userId']) +' and group_users.group_id = groups.id)';
        dbCursor.execute(sql)
        groups = dbCursor.fetchall();

        res = []
        for each in groups:
            id = str(each[0])
            sql = 'SELECT user.name, user.thumb, user.id from user inner join group_users where group_users.group_id = ' + id + ' and group_users.user_id = user.id'
            dbCursor.execute(sql)
            members = dbCursor.fetchall()

            sql = 'SELECT cast(sum(amount) as signed) from payments where group_id = ' + id + ' GROUP BY group_id'
            dbCursor.execute(sql)
            groupSpent = dbCursor.fetchall()
            if len(groupSpent) > 0 :
                groupSpent = groupSpent[0]
            else:
                groupSpent = 0

            sql = 'SELECT cast(sum(amount) as signed) from payments where group_id = ' + id +' and user_id = ' + str(args['userId']) + ' GROUP by group_id'
            dbCursor.execute(sql)
            youSpent = dbCursor.fetchall()
            if len(youSpent) > 0 :
                youSpent = youSpent[0]
            else:
                youSpent = 0

            sql = 'SELECT cast(sum(amount) as signed) from owes where user_id = ' + str(args['userId']) + ' and group_id = ' + id + ' GROUP by group_id'
            dbCursor.execute(sql)
            youOwe = dbCursor.fetchall()

            if len(youOwe) > 0 :
                youOwe = youOwe[0]
            else:
                youOwe = 0

            res.append({'groupId': id, 'groupName': each[1], 'groupThumb': each[2], 'members': members, 'groupSpent': groupSpent, 'youSpent': youSpent, 'youOwe': youOwe})

        print(len(res))
        return {'message':  "loaded" if len(res)>0 else 'empty',
                'data': res,
                'code': 1 if len(res)>0 else 0}


class Requests(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userId', type=int)
        args = parser.parse_args()
        sql = 'SELECT r.id, g.id , g.name , g.thumb , u.name from join_requests r inner join groups g on g.id = r.group_id inner join user u on u.id = r.sender_id where r.joiner_id = ' + str(args['userId'])
        dbCursor.execute(sql)
        res = dbCursor.fetchall()

        return {
            "message": 'loaded' if len(res) > 0 else 'empty',
            'data': res,
            'code': 1 if len(res)>0 else 0
        }

    def post(self):
        args = request.get_json()
        print(args)
        sql = 'SELECT * from join_requests where group_id = %s and joiner_id=%s'
        val= [args['groupId'], args['joinerId']]

        dbCursor.execute(sql, val)
        res = dbCursor.fetchall()
        if(len(res)>0):
            return {"message": 'Request already sent', "code": 0}

        sql = 'SELECT * from group_users where group_id = %s and user_id = %s'
        val= [args['groupId'], args['joinerId']]
        dbCursor.execute(sql, val)
        res = dbCursor.fetchall()
        if (len(res) > 0):
            return {"message": 'Already a member', "code": 0}

        sql = 'INSERT into join_requests (group_id, joiner_id, sender_id) values (%s , %s , %s)'

        val = [args['groupId'], args['joinerId'], args['senderId']]
        dbCursor.execute(sql, val)
        mydb.commit()

        return {"message": 'Requested successfully', "code": 1}

    def delete(self):
        args = request.get_json()

        sql = 'DELETE from join_requests where id = ' + str(args['id'])
        dbCursor.execute(sql)
        mydb.commit()
        return {"message": "removed"}

class groupUser(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        args = parser.parse_args()

        sql = "SELECT u.name, u.thumb from group_users gu inner join user u on (gu.user_id = u.id and gu.group_id = " + str(args['id']) + ")"
        dbCursor.execute(sql)
        res = dbCursor.fetchall()

        return {
            "message": res,
            "code": 1
        }

    def post(self):
        args = request.get_json();

        sql = 'INSERT into group_users (user_id, group_id) values (%s , %s)'
        val = [args['userId'], args['groupId']]
        dbCursor.execute(sql, val)
        mydb.commit()

        #remove from join requests
        sql = 'DELETE from join_requests where joiner_id = %s and group_id = %s'
        val = [args['userId'], args['groupId']]
        dbCursor.execute(sql, val)
        mydb.commit()

        response = {"message": "Joined successfully", "code": 1}
        print(response)
        return response

class payment(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('groupId', type=int)
        args = parser.parse_args()

        sql = 'SELECT u.name, u.thumb, p.purpose, p.amount, p.time from payments p inner join user u on (p.user_id = u.id and p.group_id = '+ str(args['groupId']) +') order by time desc  '
        dbCursor.execute(sql)
        res = dbCursor.fetchall()

        return {
            "message": "Found payments" if len(res)>0 else "empty",
            "code": 1 if len(res)>0 else 0,
            "data": res
        }


    def post(self):
        args = request.get_json()
        print(args)
        sql = 'INSERT into payments (user_id, group_id, amount, purpose, time) values (%s, %s, %s, %s, %s)';
        ts = calendar.timegm(time.gmtime())
        val = [args['userId'], args['groupId'], args['amount'], args['purpose'], ts]

        dbCursor.execute(sql, val)
        mydb.commit()

        payment_id = dbCursor.lastrowid
        members = args['members']
        amount = int(args['amount']) // (len(members)+1)

        sql = 'INSERT INTO owes (user_id, payer_id, amount, payment_id, group_id) values'
        for member in members:
            temp = ' ({}, {}, {}, {}, {}),'.format(member, args['userId'], amount, payment_id, args['groupId'])
            sql += temp

        sql = sql[0: -1]
        print(sql)

        dbCursor.execute(sql)
        mydb.commit()

        return {"message" : "Done", "code": 1}

class Search(Resource):
    def get(self):
        cur = mydb.cursor()
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str)
        parser.add_argument('groupId', type=int)
        args = parser.parse_args()

        sql = "SELECT * from user where mobileNumber like '%" + args['key'] + "%'"
        # val = [args['groupId'], args['key']]
        cur.execute(sql)

        res = cur.fetchall()
        cur.close()
        print(res)
        return {
            "message": "results found" if len(res)>0 else "empty",
            "code": 1 if len(res)>0 else 0,
            "data": res
        }

class Owe(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('groupId', type=int)
        parser.add_argument('userId', type=int)
        args = parser.parse_args()

        sql = 'SELECT o.payer_id, u.thumb, u.name, cast(sum(o.amount) as signed) from owes o inner join user u where (o.payer_id = u.id and o.group_id=%s and o.user_id = %s) group by o.payer_id'
        val = [args['groupId'], args['userId']]
        dbCursor.execute(sql, val)

        res = dbCursor.fetchall()

        sql = 'SELECT u.name, u.thumb, p.purpose, p.amount, p.time from payments p inner join user u on (p.user_id = u.id and p.group_id = ' + str(
            args['groupId']) + ') order by time desc  '
        dbCursor.execute(sql)
        res0 = dbCursor.fetchall()

        print(res)

        return [{
            "message": "found owes" if len(res)>0 else "empty",
            "data": res,
            "code": 1 if len(res)>0 else 0
        }, {
            "message": "Found payments" if len(res0)>0 else "empty",
            "code": 1 if len(res0)>0 else 0,
            "data": res0
        }]

api.add_resource(Account, '/user')
api.add_resource(Group, '/group')
api.add_resource(Groups, '/groups')
api.add_resource(Requests, '/requests')
api.add_resource(groupUser, '/groupUser')
api.add_resource(payment, '/payment')
api.add_resource(Search, '/search')
api.add_resource(Owe, '/owe')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
