# Main-menu buttons — generation prompt template (player report #688, D 2026-09-02)
# "need to generate buttons with stylized text for the main menu"
# Target: the menu's 4-column grid tiles (~425x196 px) - a wide plate with the label baked in.
# Style anchor: the approved tier badges / currency icons / menu-tile icon set.
# Model: gpt-image-2-2026-04-21, POST /images/generations, 1536x1024, one image per label.
# Raws to _parking/ui/menu-buttons/ for D's approval; crops to the plate + 850x390 webp
# derivatives (2x the 425x196 box) after approval. NO FLOOR. The 14 labels, as the menu prints them:
# GAME, FLOOR MAP, INVENTORY, SOUL BAG, EQUIPMENT, BREEDING, CRAFTING, CODEX, ADVENTURE LOG,
# PVP ARENA, GAME SETTINGS, PREMIUM SHOP, REPORT A BUG, JOIN THE DISCORD CHAT.

Ornate dark-fantasy game menu button: a wide rectangular plate of burnished gold-bronze with a
raised gothic filigree frame and small ornamental corners, a deep crimson enamel field, and the
words "{LABEL}" embossed large in bright polished gold capitals, centred on the plate, crisp and
perfectly legible, no other text anywhere, painterly, dramatic rim light from the upper left, one
centred plate filling 85% of the frame width and about half of its height, flat pure black
background, no floor, no ground shadow, no border outside the plate.

# ---- SECOND BATCH (D 2026-09-02: "they all need to be the same size. They also need an icon
# representing what they are about, and they need to visually represent what they are about").
# Method: the house S1/S3 pattern - ONE master plate is generated blank (/images/generations), then
# every button is an /images/edits derivative off that master, so geometry and frame are identical
# by construction; each edit adds the button's icon on the left third, the label to its right, and
# a faint engraved motif in the enamel behind the text.

MASTER: Ornate dark-fantasy game menu button plate, blank: a wide rectangular plate of burnished
gold-bronze with a raised gothic filigree frame and small ornamental corners, a deep crimson enamel
field, no text, no icon, the plate filling the frame edge to edge horizontally with a thin even
black margin, centred vertically and about 45% of the frame height, painterly, dramatic rim light
from the upper left, flat pure black background, no floor, no ground shadow.

EDIT (per button): Keep this exact plate, frame, size and position unchanged. Add on the left third
of the crimson field a large embossed polished-gold icon of {ICON}, and to its right the words
"{LABEL}" embossed in bright polished gold capitals, crisp and perfectly legible, centred in the
remaining field; engrave a faint {MOTIF} into the crimson enamel behind the text. No other text.
Same painterly style, same lighting, flat pure black background outside the plate.

| label | icon | motif |
| GAME | a stone tower under a crescent moon | tower silhouette lines |
| FLOOR MAP | an unrolled parchment map with a compass rose | map contour lines |
| INVENTORY | an open treasure chest | chest straps and rivets |
| SOUL BAG | a drawstring pouch leaking a glowing violet soul-wisp | drifting wisps |
| EQUIPMENT | a horned helm over a crossed sword and shield | armour plate seams |
| BREEDING | a large egg in a nest of thorns | thorn vines |
| CRAFTING | an anvil and hammer | flying sparks |
| CODEX | an open tome with a glowing page | lines of script |
| ADVENTURE LOG | a quill over a bound journal | ink strokes |
| PVP ARENA | two crossed blades over a laurel wreath | colosseum arches |
| GAME SETTINGS | three interlocking gears | gear teeth |
| PREMIUM SHOP | a merchant's scale with stacked coins | scattered coins |
| REPORT A BUG | a beetle pinned to a parchment | parchment creases |
| JOIN THE DISCORD CHAT | a heraldic speech-scroll with two crossed horns | speech lines |
