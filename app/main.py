def main():
	# initialize DB (create tables + seed defaults) before running the app
	from app import database
	try:
		database.init_db()
	except Exception:
		# if DB init fails, continue — services will surface errors as needed
		pass

	# import menu components lazily so importing app.main doesn't start UI
	from app.cli.menu_printer import print_menu
	from app.cli import constants

	print_menu(constants.login_menu)


if __name__ == '__main__':
	main()