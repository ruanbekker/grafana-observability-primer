import os
import logging 
from flask import Flask, request, jsonify
from flask.logging import default_handler
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError
from prometheus_flask_exporter import PrometheusMetrics
from time import sleep
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from random import random
from time import strftime

AGENT_HOSTNAME = os.getenv("AGENT_HOSTNAME", "tempo")
AGENT_PORT = int(os.getenv("AGENT_PORT", "4317"))

class SpanFormatter(logging.Formatter):
    def format(self, record):
        trace_id = trace.get_current_span().get_span_context().trace_id
        if trace_id == 0:
            record.trace_id = None
        else:
            record.trace_id = "{trace:032x}".format(trace=trace_id)
        return super().format(record)

resource = Resource(attributes={
    "service.name": "service-api"
})

trace.set_tracer_provider(
    TracerProvider(resource=resource)
)
otlp_exporter = OTLPSpanExporter(endpoint=f"{AGENT_HOSTNAME}:{AGENT_PORT}", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# trace_provider = TracerProvider(
#     resource=Resource.create({"service.name": "my-flask-app"}),
# )
# trace_provider.add_span_processor(
#     SimpleExportSpanProcessor(otlp_exporter)
# )

#logging.basicConfig(level=logging.INFO)
#logging.info("LOGLEVEL=INFO")

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

FlaskInstrumentor().instrument_app(app)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
app.logger.setLevel(logging.INFO)
default_handler.setFormatter(
    SpanFormatter(
        'time="%(asctime)s" service=%(name)s level=%(levelname)s %(message)s trace_id=%(trace_id)s'
    )
)

metrics = PrometheusMetrics(app)
metrics.info("app_info", "grafana observability primer", version="1.0.0")

db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.before_first_request
def create_database():
    db.create_all()
    return 'created'

@app.route("/edge")
def bar():
    random_value = random()  # random number in range [0.0,1.0)
    if random_value < 0.05:
        return "Edge case!", 500
    return "ok"

@app.after_request
def after_request(response):
    app.logger.info(
        'addr="%s" method=%s scheme=%s path="%s" status=%s',
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        response.status_code,
    )
    return response

@app.route("/users", methods=["POST"])
def add_user():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("db-entry"):
        username = request.json['username']
        email = request.json['email']
        try:
            new_user = User(username, email)
            db.session.add(new_user)
            db.session.commit()
            result = user_schema.dump(new_user)
        except IntegrityError:
            db.session.rollback()
            result = {"message": "user {} already exists".format(username)}
    return jsonify(result)

@app.route("/users", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

@app.route("/users/<id>", methods=["GET"])
def user_detail(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@app.route("/users/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    email = request.json['email']
    user.email = email
    user.username = username
    db.session.commit()
    return user_schema.jsonify(user)

@app.route("/users/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
