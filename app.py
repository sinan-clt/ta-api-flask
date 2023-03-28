from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/ta_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'dummy' 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)
db = SQLAlchemy(app)


class TA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    native_english_speaker = db.Column(db.Boolean, nullable=False)
    course_instructor = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Boolean, nullable=False)
    class_size = db.Column(db.Integer, nullable=False)
    performance_score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<TA %r>' % self.id


# JWT Authentication
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'admin' or password != 'password':
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200


@app.route('/ta', methods=['GET'])
@jwt_required()
def get_all_ta():
    tas = TA.query.all()
    return jsonify([{'id': ta.id,
                     'native_english_speaker': ta.native_english_speaker,
                     'course_instructor': ta.course_instructor,
                     'course': ta.course,
                     'semester': 'Summer' if ta.semester else 'Regular',
                     'class_size': ta.class_size,
                     'performance_score': ta.performance_score} for ta in tas]), 200


@app.route('/ta', methods=['POST'])
@jwt_required()
def add_ta():
    try:
        ta = TA(native_english_speaker=request.json['native_english_speaker'],
                course_instructor=request.json['course_instructor'],
                course=request.json['course'],
                semester=request.json['semester'],
                class_size=request.json['class_size'],
                performance_score=request.json['performance_score'])
        db.session.add(ta)
        db.session.commit()
    except IntegrityError:
        return jsonify({'message': 'Error: Duplicate ID'}), 400
    return jsonify({'message': 'New TA added successfully'}), 201


@app.route('/ta/<int:id>', methods=['GET'])
@jwt_required()
def get_ta_by_id(id):
    ta = TA.query.get(id)
    if ta:
        return jsonify({'id': ta.id,
                         'native_english_speaker': ta.native_english_speaker,
                         'course_instructor': ta.course_instructor,
                         'course': ta.course,
                         'semester': 'Summer' if ta.semester else 'Regular',
                         'class_size': ta.class_size,
                         'performance_score': ta.performance_score}), 200
    else:
        return jsonify({'message': 'TA not found'}), 404


@app.route('/ta/<int:id>', methods=['PUT'])
@jwt_required()
def update_ta(id):
    ta = TA.query.get(id)
    if ta:
        ta.native_english_speaker = request.json.get('native_english_speaker', ta.native_english_speaker)
        ta.course_instructor = request.json.get('course_instructor', ta.course_instructor)
        ta.course = request.json.get('course', ta.course)
        ta.semester = request.json.get('semester', ta.semester)
        ta.class_size = request.json.get('class_size', ta.class_size)
        ta.performance_score = request.json.get('performance_score', ta.performance_score)
        db.session.commit()
        return jsonify({'message': 'TA updated successfully'}), 200
    else:
        return jsonify({'message': 'TA not found'}), 404


@app.route('/ta/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_ta(id):
    ta = TA.query.get(id)
    if ta:
        db.session.delete(ta)
        db.session.commit()
        return jsonify({'message': 'TA deleted successfully'}), 200
    else:
        return jsonify({'message': 'TA not found'}), 404



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
