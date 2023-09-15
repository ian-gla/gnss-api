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
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials

# auth token.


def auth_token(request: flask.Request) -> bool:
    token = request.headers.get("authorization")
    try:
        decoded_token = auth.verify_id_token(token)
        return True

    except (auth.InvalidIdTokenError, ValueError) as e:
        print(e)
        return False
