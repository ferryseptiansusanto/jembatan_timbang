# modules/auth.py

current_userid = None
current_username = None
current_user_level = None

def set_user(id, username, level):
    global current_userid, current_username, current_user_level
    current_userid = id
    current_username = username
    current_user_level = level
def get_userid():
    return current_userid
def get_username():
    return current_username

def get_level():
    return current_user_level

def is_admin():
    return current_user_level and current_user_level.lower() == "administrator"

def is_superadmin():
    return current_user_level and current_user_level.lower() == "superadmin"

def can_delete_user(target_level):
    # Misal hanya admin boleh hapus 'user', tapi tidak boleh hapus sesama admin atau superadmin
    if is_superadmin():
        return True
    if is_admin() and target_level.lower() == "user":
        return True
    return False