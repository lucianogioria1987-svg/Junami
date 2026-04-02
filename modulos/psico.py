from flask import Blueprint, render_template, session, redirect, url_for

psico_bp = Blueprint('psico_bp', __name__, url_prefix='/psico')

@psico_bp.route('/')
def dashboard():
    if 'usuario_actual' not in session:
        return redirect(url_for('dashboard_loguin_bp.login'))
    return "Dashboard Psicología en construcción"
