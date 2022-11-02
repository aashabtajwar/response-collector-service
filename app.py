from flask import Flask, request
from flask_restful import Resource, Api
import mysql.connector

from queue_data import QueueData
from extension import logging

app = Flask(__name__)
api = Api(app)

class Hello(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(Hello, '/')
api.add_resource(QueueData, '/responses/<string:form_id>')
if __name__ == '__main__':
    logging.info('Response Collector service started')
    app.run(debug=True)