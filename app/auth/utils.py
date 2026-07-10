from flask import flash


def flash_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
