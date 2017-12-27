import animator
from flask import Flask

app = Flask(__name__)


script = None
def startAnimation():
	global script
	script = animator.TwinkleScript()
	Animator(script)


@app.route("/hue/<hue>")
def setHue(hue):
	script.update( float(hue) )
	return hue

# @app.route("/hue")
# def getHue():
# 	return current_hue


startAnimation()

if __name__ == "__main__":
	app.run()
