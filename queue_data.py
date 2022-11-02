from flask import request 
from flask_restful import Resource

from mysql import connector
import jwt
import pika

db = connector.connect(
    host = "localhost",
    user = "root",
    password = "password",
    database = "atlan_tester"
)
cursor = db.cursor()

class QueueData(Resource):
    def post(self, form_id):
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, 'secret', algorithms="HS256")['id']

        # get the form link and the sheet name 
        query = f'''SELECT link, sheet_name FROM forms WHERE id={form_id}'''
        cursor.execute(query)
        form_link, sheet_name = cursor.fetchone()

        # get the questions for this form 
        query = f'''SELECT field_name, id FROM questions WHERE form_id={form_id}'''
        cursor.execute(query)
        field_names = cursor.fetchall()

        response_data = request.get_json()

        # creating empty list 'data'
        # will be used to upload data to sheets in a specific format
        data = []

        # write down all the response data into DB
        for field_name, question_id in field_names:
            data.append(response_data[field_name])
            query = f'''INSERT INTO responses (text, question_id, user_id) VALUES ('{response_data[field_name]}', {question_id}, {user_id})'''
            print(query)
            cursor.execute(query)
            db.commit()
        
        data = [data]
        return {
            'message': data
        }

        # queue data to rabbitmq


