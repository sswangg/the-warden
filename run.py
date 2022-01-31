from subprocess import call

call(["cd", "/home/pi/Warden"])
call(["screen", "-S", "warden", "-d", "-m", "bash", "-c", "source bin/activate; cd The-Warden; python main.py"])
