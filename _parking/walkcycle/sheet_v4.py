import os,sys,json,base64,subprocess,pathlib
KEY=os.environ['OAI']; D=pathlib.Path('sheet'); D.mkdir(exist_ok=True)
POSE='muy_grid_6x2.png'; CHAR='assassin1.png'      # v1's reference — the one that read closest
PROMPT=("Draw ONE image that is a 12-cell sprite sheet: 6 columns by 2 rows, 12 equal cells, "
 "read left to right then top to bottom.\n\n"
 "IMAGE 1 IS THE POSE REFERENCE ONLY. It is a 6x2 grid of 12 photographic frames of a walk cycle "
 "in the SAME layout and the SAME reading order as the sheet you are drawing. Cell N of your sheet "
 "must match cell N of IMAGE 1 EXACTLY in body mechanics: stride phase, the bend of each knee and "
 "each elbow, which foot is flat / on its heel / on its toe / clear of the ground, weight "
 "distribution, hip height, torso lean and head angle. The twelve cells are TWELVE DIFFERENT POSES "
 "- do not repeat a pose, do not average them, do not draw twelve variations of one stance. "
 "Take NOTHING else from IMAGE 1: not the person, not the nudity, not the lighting, not the grid "
 "background, not the photographic look, not the frame numbers.\n\n"
 "IMAGE 2 IS THE CHARACTER AND ART STYLE REFERENCE. Everything about WHO this is comes from it: "
 "face, hair, hood and cloak, costume, palette, silhouette, and its painterly semi-realistic "
 "dark-fantasy rendering. The character is FULLY CLOTHED in their own costume in every cell.\n\n"
 "HER HANDS ARE EMPTY - no daggers, no blades, nothing held. Ignore the weapons in IMAGE 2.\n\n"
 "POSTURE IS UPRIGHT: spine vertical, shoulders back, head level and facing forward. She walks "
 "tall. No forward hunch, no stoop, no crouch, no leaning into the stride.\n\n"
 "THE CLOAK IS ONE UNCHANGING GARMENT: same length, same ragged hem, same collar, same shoulder "
 "line in all twelve cells. Only its sway changes with the stride.\n\n"
 "IN EVERY CELL: complete side profile facing RIGHT, walking to the right, full body head to feet, "
 "identical character, identical costume, identical colours, identical camera distance, identical "
 "scale, identical eye level, feet on the same invisible ground line at the bottom of the cell. "
 "Fully transparent background, nothing behind the character, no floor, no cast shadow, no motion "
 "blur, no speed lines, no text, no numbers, no visible cell borders or gutters.")
cmd=['curl','-s','--noproxy','*','https://api.openai.com/v1/images/edits',
 '-H','Authorization: Bearer '+KEY,'-F','model=gpt-image-2.5-sunburst-2026-09-08',
 '-F','size=2304x1536','-F','quality=xhigh','-F','background=transparent',
 '-F','output_format=png','-F','prompt='+PROMPT,'-F','image[]=@'+POSE,'-F','image[]=@'+CHAR]
j=json.loads(subprocess.run(cmd,capture_output=True,text=True).stdout)
if 'error' in j: sys.exit('ERR '+j['error'].get('message','')[:160])
(D/'assassin_25_v4.png').write_bytes(base64.b64decode(j['data'][0]['b64_json']))
print('ok', j.get('usage'))
