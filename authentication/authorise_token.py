####################################################################
#  Author: Miguel Pereira
#  This code is licensed under GNU General Public License version 3
#  as published by the Free Software Foundation.
#  (see LICENSE.txt for details)
####################################################################

"""
Utils for authorising user tokens using the Firebase Authentication db.
"""
import flask
from firebase_admin import auth

# auth token.


def auth_token(request: flask.Request) -> bool:
    token = request.headers.get("authorization")
    try:
        auth.verify_id_token(token)
        return True

    except (auth.InvalidIdTokenError, ValueError) as e:
        print(e)
        return False
