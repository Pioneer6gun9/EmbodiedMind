from embodiedmind.dsl.action_schema import Action

def test_action_schema():
    action = Action(name="grasp", target="red_block")
    assert action.name == "grasp"
