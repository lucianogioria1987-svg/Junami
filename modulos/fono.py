from flask import Blueprint, render_template, session, redirect, url_for

fono_bp = Blueprint('fono_bp', __name__, url_prefix='/fono')

@fono_bp.route('/')
def dashboard():
    if 'usuario_actual' not in session:
        return redirect(url_for('dashboard_loguin_bp.login'))
    return "Dashboard Fonoaudiología en construcción"
