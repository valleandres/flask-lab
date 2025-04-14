from flask import Blueprint, render_template_string, request, redirect
from .forms import NameForm
from .models import db, User

main = Blueprint('main', __name__)

TEMPLATE = '''
<form method="POST">
  {{ form.csrf_token }}
  {{ form.name.label }} {{ form.name(size=20) }}
  {{ form.submit() }}
</form>
'''

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User(name=form.name.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template_string(TEMPLATE, form=form)