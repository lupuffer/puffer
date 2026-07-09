from flask import Blueprint

knowledge_bp = Blueprint('knowledge', __name__)

from . import materials, discussions, points, user