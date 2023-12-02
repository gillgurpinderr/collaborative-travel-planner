from website.__init__ import create_app

app = create_app() # create instance of flask app

if __name__ == '__main__': # check if script executed directly: python main.py
    app.run(debug=True)
    
'''
WanderSync

References for Python files
Google SSO: https://www.youtube.com/watch?v=FKgJEfrhU1E
Flask DB/Auth: https://youtu.be/dam0GPOAvVI
'''