from back_end import create_app
from flask_cors import CORS, cross_origin


app=create_app()

cors = CORS(app, resources={
    r"/*": {
        "origins": "http://localhost:5173",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_SUPPORTS_CREDENTIALS'] = True

if __name__ == "__main__":
    app.run(debug=True)


# Modification:
# sa user ang attributes nalang ay username, password & password confirmation
# note -> feedback

# Dagdag:
# Leaderboards (LIVE)

#ang magagamit ay:
# all about user

#pag aaralan:
#TOKEN