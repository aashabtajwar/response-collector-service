from flask import request 
from flask_restful import Resource

from mysql import connector
import jwt
import pika
import json
from threading import Thread

from extension import logging

db = connector.connect(
    host = "localhost",
    user = "root",
    password = "password",
    database = "atlan_tester"
)
cursor = db.cursor()

def handle_data(form_id, responder_id, response_data):
    # start thead
    # get the form link and the sheet name 
    query = f'''SELECT link, sheet_name FROM forms WHERE id={form_id}'''
    cursor.execute(query)
    form_link, sheet_name = cursor.fetchone()

    # get the questions for this form 
    query = f'''SELECT field_name, id FROM questions WHERE form_id={form_id}'''
    cursor.execute(query)
    field_names = cursor.fetchall()

    
    # LOG -> response data collected
    logging.info('Response data collected')

    # creating empty list 'data'
    # will be used to upload data to sheets in a specific format
    data = []

    # write down all the response data into DB
    for field_name, question_id in field_names:
        data.append(response_data[field_name])
        query = f'''INSERT INTO responses (text, question_id, responder_id) VALUES ('{response_data[field_name]}', {question_id}, {responder_id})'''
        print(query)
        cursor.execute(query)
        db.commit()

    # LOG -> inserted into db
    logging.info('Responses submitted')

    data = [data]

    queue_data = {
        'data': data,
        'link': form_link,
        'sheet_name': sheet_name,
        'form_id': form_id
    }

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='atlan_task')
    channel.basic_publish(exchange='', routing_key='atlan_task', body=json.dumps(queue_data))
    connection.close()

    logging.info('Pushed Data to Queue')



class QueueData(Resource):
    def post(self, form_id):
        response_data = request.get_json()
        
        # USE CASE 2
        if (float(response_data['monthly_savings']) > float(response_data['monthly_income'])):
            return {
                'message': 'Invalid Response. Monthly Savings cannot be greater than Monthly Income'
            }, 400


        token = request.headers.get('Authorization')
        responder_id = jwt.decode(token, 'secret', algorithms="HS256")['id']

        # handle the rest on a different thread
        thread = Thread(target=handle_data, args=[form_id, responder_id, response_data])
        
        thread.start()

        return {
            'message': 'Response Taken. Thank You!'
        }, 201

