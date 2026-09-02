import sys
import os
import json
sys.path.append(os.path.dirname(__file__))
from models.thesis_group import ThesisGroupModel
from controllers.auth_controller import AuthController

# create a test student
res = AuthController.handle_signup({
    'name': 'Test Student',
    'email': 'test_student_thesis@univ.edu',
    'password': 'password123',
    'role': 'Student',
})
if not res.get('success'):
    res = AuthController.handle_login({
        'email': 'test_student_thesis@univ.edu',
        'password': 'password123'
    })
user_id = res['user']['user_id']
print("User ID:", user_id)

# create a group
group_id = ThesisGroupModel.create_group(user_id, "Test Group", "AI", "Desc")
print("Group ID:", group_id)

# get groups
groups = ThesisGroupModel.get_all_groups()
for g in groups:
    if g['group_id'] == group_id:
        print("Group created!")
        print("Members:", g['members'])

# try to join
res = ThesisGroupModel.join_group(group_id, user_id)
print("Join result:", res)
