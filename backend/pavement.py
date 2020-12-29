# -*- coding: utf-8 -*-

import os
import subprocess
import platform

from paver.easy import (BuildFailure, call_task, cmdopts, info, needs, options,
						path, sh, task)

@task
def start_chrome_devtool():
	"""
	Start Chrome Devtool process.
	"""
	system = platform.system()
	cmd_list = [
		'--headless',
		'--disable-gpu',
		'--remote-debugging-port=9222',
		'--run-all-compositor-stages-before-draw',
		# '--virtual-time-budget=10000',
	] 
	if system == 'Linux':
		app_path = 'google-chrome'
		# app_path = 'chromium-browser' # produces smaller pdf size
	elif system == 'Darwin':
		app_path = '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'
		# app_path = '/Applications/Chromium.app/Contents/MacOS/Chromium'
		cmd_list += [
			'--disk-cache-dir=/tmp',
			'--user-data-dir=/tmp',
			'--crash-dumps-dir=/tmp',
		]
	elif system == 'Windows':
		app_path = "start chrome"
	cmd_list = [app_path] + cmd_list
	cmd_str = ' '.join(cmd_list)
	print(cmd_str)
	p = subprocess.Popen(cmd_str, shell=True)

@task
def stop_chrome_devtool():
	"""
	Stop Chrome Devtool process.
	"""
	system = platform.system():
	if system == 'Windows':
		sh('''for /f "tokens=5" %a in ('netstat -aon ^| find "9222"') do taskkill /f /pid %a''')
	else:
		sh('lsof -n -i:9222 | grep LISTEN | awk \'{ print $2 }\' | xargs kill')
