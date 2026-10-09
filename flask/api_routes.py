from flask import request,Blueprint

api_bp = Blueprint("api", __name__)

@api_bp.route("/")
def blueprint_root():
    print(request.method)
    if request.method=='GET':
        return "Hello From Flask Blueprint"
    else:
        return "Invalid Request"

@api_bp.route("/home")
def blueprint_root_home():
    print(request.method)
    if request.method=='GET':
        return "Hello From Flask Blueprint Home"
    else:
        return "Invalid Request"