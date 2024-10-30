from views import app
from controller.app_controller import app_controller

def main():
    app.App(650, 700, app_controller)

if __name__ == '__main__':
    main()