import pytest
from game import inventory_grid as mod

CASES = [
    ("cell_two", "m.cell_coord(65, 33, 32) == (2, 1)"),
    ("cell_zero", "m.cell_coord(10, 10, 32) == (0, 0)"),
    ("rotate_swap", "m.rotate_size(2, 3, True) == (3, 2)"),
    ("rotate_same", "m.rotate_size(2, 3, False) == (2, 3)"),
    ("stack_potion", "m.stack_limit('potion', 99) == 99"),
    ("can_empty", "m.can_place([[0, 0], [0, 0]], 0, 0, 1, 1) is True"),
    ("can_blocked", "m.can_place([[1, 0], [0, 0]], 0, 0, 1, 1) is False"),
    ("migrate_add", "m.migrate((1, 1), (2, 0)) == (3, 1)"),
    ("split_pair", "m.split_count(5, 2) == (2, 3)"),
    ("split_zero", "m.split_count(3, 0) == (0, 3)"),
    ("sort_lower", "m.sort_key('Sword') == 'sword'"),
    ("find_first", "m.find_slot([[0, 0], [0, 0]], 1, 1) == (0, 0)"),
    ("release_true", "m.release_slot([[1, 0]], 0, 0) is True"),
    ("release_false", "m.release_slot([[0, 0]], 0, 0) is False"),
    ("reconcile_local", "m.reconcile('local', 'remote') == 'local'")
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
