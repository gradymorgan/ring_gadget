import animator
from flask import Flask

app = Flask(__name__)


script = None
def startAnimation():
	global script
	script = animator.TwinkleScript()
	animator.Animator(script).run()


@app.route("/hue/<hue>")
def setHue(hue):
	script.update( float(hue) )
	return str(hue)

@app.route("/brightness/<brightness>")
def setBrightness(brightness):
	script.setBrightness( float(brightness) )
	return str(brightness)

# @app.route("/hue")
# def getHue():
# 	return current_hue


startAnimation()

if __name__ == "__main__":
	app.run()
