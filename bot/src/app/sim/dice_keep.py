from collections import Counter


def keep_n_of_face(dice: list[int], face: int, n: int) -> list[bool]:
  keep_indices = set([i for i, d in enumerate(dice) if d == face][:n])
  return [i in keep_indices for i in range(len(dice))]


def keep_pairs_from_faces(dice: list[int], faces: list[int]) -> list[bool]:
  partials = [keep_n_of_face(dice, face, 2) for face in faces]
  return [any(col) for col in zip(*partials)]


def keep_best_single(dice: list[int]) -> list[bool]:
  kept = [False] * len(dice)
  kept[dice.index(max(dice))] = True
  return kept


def keep_upper(dice: list[int], face: int) -> list[bool]:
  return [d == face for d in dice]


def keep_n_of_a_kind(dice: list[int], n: int) -> list[bool]:
  counts = Counter(dice)
  best = max(counts, key=lambda f: (counts[f], f))
  return keep_n_of_face(dice, best, n)


def keep_n_of_a_kind_weighted(dice: list[int], n: int) -> list[bool]:
  counts = Counter(dice)
  best = max(counts, key=lambda f: (min(counts[f], n) * f, counts[f]))
  return keep_n_of_face(dice, best, n)


def keep_top_faces_with_limits(dice: list[int], limits: list[int]) -> list[bool]:
  counts = Counter(dice)
  sorted_faces = sorted(counts.keys(), key=lambda f: (counts[f], f), reverse=True)
  partials = [
    keep_n_of_face(dice, face, limit) for face, limit in zip(sorted_faces, limits)
  ]
  return [any(col) for col in zip(*partials)]


def keep_full_house(dice: list[int]) -> list[bool]:
  return keep_top_faces_with_limits(dice, [3, 2])


def keep_two_pairs(dice: list[int]) -> list[bool]:
  counts = Counter(dice)
  faces = sorted([face for face, count in counts.items() if count >= 2], reverse=True)[
    :2
  ]
  if faces:
    pairs_keep = keep_pairs_from_faces(dice, faces)
    paired = set(faces)
    min_pair = min(faces)
    singles = [
      face
      for face in counts
      if face not in paired and counts[face] == 1 and face > min_pair
    ]
    if singles:
      single_keep = keep_n_of_face(dice, max(singles), 1)
      return [a or b for a, b in zip(pairs_keep, single_keep)]
    return pairs_keep
  return keep_best_single(dice)


def keep_two_pairs_weighted(dice: list[int], min_second_face: int) -> list[bool]:
  counts = Counter(dice)
  pairs = sorted([face for face, count in counts.items() if count >= 2], reverse=True)
  if not pairs:
    return keep_best_single(dice)
  faces = [pairs[0]] + [f for f in pairs[1:2] if f >= min_second_face]
  return keep_pairs_from_faces(dice, faces)


def keep_one_pair(dice: list[int]) -> list[bool]:
  counts = Counter(dice)
  pairs = [face for face, count in counts.items() if count >= 2]
  if pairs:
    best_pair = max(pairs)
    higher = [face for face in counts if face > best_pair and counts[face] == 1]
    if higher:
      pair_keep = keep_n_of_face(dice, best_pair, 2)
      single_keep = keep_n_of_face(dice, max(higher), 1)
      return [a or b for a, b in zip(pair_keep, single_keep)]
    return keep_n_of_face(dice, best_pair, 2)
  return keep_best_single(dice)


def keep_chance(dice: list[int]) -> list[bool]:
  return [d >= 4 for d in dice]


def keep_for_straight(dice: list[int], straights: list[set[int]]) -> list[bool]:
  for run in straights:
    if len(run & set(dice)) >= 4:
      partials = [keep_n_of_face(dice, face, 1) for face in run]
      return [any(col) for col in zip(*partials)]
  return [False] * len(dice)
