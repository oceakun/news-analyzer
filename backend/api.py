from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from query_processing import retrieve_similar_content 
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app,resources={r"/api/*": {"origins": "*"}})
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:m1n1g3r1t@localhost/postgres'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS']=False

db = SQLAlchemy(app)
app.app_context().push()

class NewsHeadline(db.Model):
    __tablename__ = 'news_headlines'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    article = db.Column(db.Text, nullable=True)
    def __repr__(self):
        return f"<NewsHeadline title={self.title}>"

with app.app_context():
    db.create_all()
class NewsHeadlines(Resource):
    def get(self):
        news_headlines = NewsHeadline.query.all()
        headlines_data = [
            {
                'title': headline.title,
                'url': headline.url,
                'category': headline.category,
                'article': headline.article
            } for headline in news_headlines
        ]
        return {'news_headlines': headlines_data}


class AnswerQuery(Resource):
    def post(self):
        data = request.get_json()
        query = data.get('query', '')
        if not query:
            return {'response': "No query provided"}, 400
        print("query : ", query)
        similar_content = retrieve_similar_content(query)
        response_data = [
            {'title': content[0], 'url': content[1], 'category': content[2], 'article': content[3]}
            for content in similar_content
        ]  
        return {'response': "Here's similar content", 'data': response_data}


api.add_resource(NewsHeadlines, '/api/news_headlines')
api.add_resource(AnswerQuery, '/api/answer_query')

if __name__ == '__main__':
    app.run(debug=True)