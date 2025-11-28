# native modules
import sys
from typing import Dict
# external dependencies
from rich.console import Console
# internal dependencies
from app.cli import constants
from app.domain.MenuFunctions import MenuFunctions
from app.services.login_service import login, get_logged_in_user, reset_logged_in_user
from app.services.user_service import get_all_users, print_all_users, create_user, delete_user
from app.services.portfolio_service import get_all_portfolios, print_all_portfolios, create_portfolio, delete_portfolio, harvest_investment
from app.services.security_service import get_all_securities, print_all_securities, place_buy_order

_console = Console()

_menus: Dict[int, str] = {
    constants.login_menu: "- - - - \nWelcome to Kiwi CLI!\n- - - - \n1. Login\n0. Exit",
    constants.main_menu: "- - - - \nMain Menu\n- - - - \n1. Manage Users\n2. Manage Portfolios\n3. Marketplace\n0. Logout",
    constants.manager_users_menu: "- - - - \nManage Users\n- - - - \n1. View Users\n2. Add User\n3. Delete User\n0. Back to Main Menu",
    constants.manage_portfolios_menu: "- - - - \nManage Portfolios\n- - - - \n1. View Portfolios\n2. Create Portfolio\n3. Delete Portfolio\n4. Harvest Investment\n0. Back to Main Menu",
    constants.marketplace_menu: "- - - - \nMarketplace\n- - - - \n1. View Securities\n2. Place Buy Order\n0. Back to Main Menu",
}

def navigate_to_manage_users_menu() -> int:
    logged_in_user = get_logged_in_user()
    if logged_in_user and logged_in_user.username != "admin":
        raise UnsupportedMenuError("Manager Users Menu is only accessible by admin user.")
    return constants.manager_users_menu

_router: Dict[str, MenuFunctions] = {
    "0.1": MenuFunctions(executor = login, navigator = lambda: constants.main_menu),
    "1.1": MenuFunctions(navigator = navigate_to_manage_users_menu),
    "2.1": MenuFunctions(executor = get_all_users, printer = print_all_users),
    "2.2": MenuFunctions(executor = create_user, printer = lambda msg: _console.print(msg)),
    "2.3": MenuFunctions(executor = delete_user, printer = lambda msg: _console.print(msg)),
    "1.2": MenuFunctions(navigator = lambda: constants.manage_portfolios_menu),
    "3.1": MenuFunctions(executor = get_all_portfolios, printer = print_all_portfolios),
    "3.2": MenuFunctions(executor = create_portfolio, printer = lambda msg: _console.print(msg)),
    "3.3": MenuFunctions(executor = delete_portfolio, printer = lambda msg: _console.print(msg)),
    "3.4": MenuFunctions(executor = harvest_investment, printer = lambda msg: _console.print(msg)),
    "1.3": MenuFunctions(navigator = lambda: constants.marketplace_menu),
    "4.1": MenuFunctions(executor = get_all_securities, printer = print_all_securities),
    "4.2": MenuFunctions(executor = place_buy_order, printer = lambda msg: _console.print(msg))
}

def print_error(error: str):
    _console.print(f"\nError: {error}\n", style = "bold red")

class UnsupportedMenuError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

def handle_user_selection(menu_id: int, user_selection: int):
    if user_selection == 0:
        if menu_id == constants.login_menu:
            sys.exit(0) #terminate the application
        elif menu_id == constants.main_menu:
            reset_logged_in_user()
            print_menu(constants.login_menu) # logout and return to login menu
        else:
            print_menu(constants.main_menu) # return to main menu from sub-menus
    formatted_user_input = f"{str(menu_id)}.{str(user_selection)}"
    menu_functions = _router[formatted_user_input]
    try:
        result = None
        if menu_functions.executor:
            result = menu_functions.executor()
            if result and menu_functions.printer:
                menu_functions.printer(result)
        if menu_functions.navigator and (menu_functions.executor is None or result):
            print_menu(menu_functions.navigator())
        else:
            print_menu(menu_id)
    except UnsupportedMenuError as e:
        print_error(str(e))
        print_menu(menu_id)
    except Exception as e:
        print_error(str(e))
        print_menu(menu_id)

def print_menu(menu_id: int) -> None:
    _console.print(_menus[menu_id])
    try:
        user_selection = int(_console.input(">> ")) 
    except ValueError:
        print_error("Invalid input. Please enter a number.")
        print_menu(menu_id)
        return
    if user_selection == 0:
        handle_user_selection(menu_id, user_selection)
        return
    if f"{menu_id}.{user_selection}" not in _router:
        print_error("Invalid selection. Please try again.")
        print_menu(menu_id)
        return
    handle_user_selection(menu_id, user_selection)