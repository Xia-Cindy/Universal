INSERT INTO users (id, display_name)
VALUES ('local-user', 'Cindy')
ON CONFLICT (id) DO NOTHING;

INSERT INTO planets (name, display_name, status, description, primary_action)
VALUES
    ('study', 'Study Planet', 'active', 'A calm AI learning workspace focused on next action.', 'Enter Study Planet'),
    ('work', 'Work Planet', 'coming_later', 'Future professional workspace placeholder.', 'Coming Later'),
    ('novel', 'Novel Planet', 'coming_later', 'Future creative writing workspace placeholder.', 'Coming Later'),
    ('life', 'Life Planet', 'coming_later', 'Future personal life rhythm workspace placeholder.', 'Coming Later'),
    ('creator', 'Creator Planet', 'coming_later', 'Future creator workspace placeholder.', 'Coming Later')
ON CONFLICT (name) DO NOTHING;

INSERT INTO planet_memberships (user_id, planet_name)
VALUES ('local-user', 'study')
ON CONFLICT (user_id, planet_name) DO NOTHING;

