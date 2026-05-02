from embodiedmind.world.world_state import WorldState, ObjectState

def test_inside_predicate():
    s=WorldState()
    s.update_object(ObjectState(id="red_block", type="block", color="red", pose=(0.0,0.0,0.08), size=(0.04,0.04,0.04)))
    s.update_object(ObjectState(id="blue_box", type="container", color="blue", pose=(0.0,0.0,0.03), size=(0.12,0.12,0.06)))
    assert s.inside("red_block","blue_box")
