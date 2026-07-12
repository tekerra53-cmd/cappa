from app import create_app

app = create_app()
with app.test_request_context('/'):
    print('app ok')
