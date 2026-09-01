# Tier badges — generation prompts (player report #684, D 2026-09-02)
# "the current tier icons on items e.g. X looks awful, in needs to be generated as an image for
#  each roman numeral tier. a square little badge dark-fantasy icon in the same style of all the
#  other game icons"
# Style anchor: the approved menu-tile and currency icon sets — burnished gold-bronze metalwork,
# deep crimson enamel, gothic filigree, painterly, rim-lit, single centred object, flat black.
# Model: gpt-image-2-2026-04-21, POST /images/generations, 1024x1024, one image per tier.
# Raws to _parking/ui/tier-badges/ for D's approval; remove.bg crops after approval; 64px
# derivatives in the game (the plaque paints at ~17-24px). NO FLOOR.
# One prompt template, the numeral swapped per tier (I, II, III, IV, V, VI, VII, VIII, IX, X):

Ornate dark-fantasy game badge icon: a small square plaque of burnished gold-bronze with a
raised gothic filigree frame and small ornamental corners, a deep crimson enamel field, and the
roman numeral "{N}" embossed large in bright polished gold at the exact centre, crisp and
legible, painterly, dramatic rim light from the upper left, single centred square badge filling
80% of frame, flat pure black background, no floor, no ground shadow, no text other than the
numeral, no border outside the badge.
