from flask import Flask
from flask_restful import reqparse, abort, Resource, Api, request
from flask_restful.representations import json

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
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        args = parser.parse_args()
        sql = "DELETE FROM user where id = "+ int(args['id'])
        dbCursor.execute(sql)
        mydb.commit()
        return {"message": 'Account deleted', 'code': 1}


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
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('user_id', type=int)
        parser.add_argument('position', type=str)
        args = parser.parse_args()

        sql = "INSERT INTO groups (name) VALUES ('{}')".format(args['name'])

        dbCursor.execute(sql)
        mydb.commit()

        #insert group user
        group_id = dbCursor.lastrowid

        sql = "INSERT INTO group_users (user_id, group_id, position ) VALUES (%s, %s, 'creator')"
        val = (args['user_id'], group_id)

        dbCursor.execute(sql, val)

        return {'message': 'Group Created', 'code': 1}

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        args = parser.parse_args()
        sql = "DELETE FROM groups where id = " + int(args['id'])
        dbCursor.execute(sql)
        mydb.commit()
        return {"message": 'Account deleted', 'code': 1}



api.add_resource(Account, '/user')
api.add_resource(Group, '/group')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
