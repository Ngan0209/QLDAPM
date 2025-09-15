from flask import Blueprint, render_template

cv_bp = Blueprint("cv", __name__, url_prefix="/cv")

@cv_bp.route("/create-cv", methods=["GET"])
def create_cv():
    return render_template("candidate/CV.html")  # file này nằm trong /templates
