from flask import Blueprint, render_template, session, redirect, url_for

teo_bp = Blueprint('teo_bp', __name__, url_prefix='/teo')

@teo_bp.route('/')
def dashboard():
    if 'usuario_actual' not in session:
        return redirect(url_for('dashboard_loguin_bp.login'))
    return "Dashboard TEO en construcción"
