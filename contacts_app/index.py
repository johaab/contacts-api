from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for, jsonify
)

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    message = "Welcome on my Amazing Contacts API"
    return jsonify({'message': message})


@bp.route('/surprise')
def easter_egg():
    message = "You found an Easter Egg, congrats!"
    return jsonify({'message': message})

