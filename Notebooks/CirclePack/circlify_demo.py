from pprint import pprint as pp
import circlify as circ
data = [
    0.05, {'id': 'a2', 'datum': 0.05},
    {'id': 'a0', 'datum': 0.8, 'children': [0.3, 0.2, 0.2, 0.1], },
    {'id': 'a1', 'datum': 0.1, 'children': [
        {'id': 'a1_1', 'datum': 0.05, 'children': [0.1, 0.2]}, {'datum': 0.04}, 0.01],
    },
]
circles = circ.circlify(data, show_enclosure=True)
circ.bubbles(circles)