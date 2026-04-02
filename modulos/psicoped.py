from flask import Blueprint, render_template, session, redirect, url_for

psicoped_bp = Blueprint('psicoped_bp', __name__, url_prefix='/psicoped')

@psicoped_bp.route('/')
def dashboard():
    if 'usuario_actual' not in session:
        return redirect(url_for('dashboard_loguin_bp.login'))
    return "Dashboard Psicopedagogía en construcción"
